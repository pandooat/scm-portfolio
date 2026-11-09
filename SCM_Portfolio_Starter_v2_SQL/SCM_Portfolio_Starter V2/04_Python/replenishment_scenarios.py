"""Beginner-friendly forecast backtest and replenishment scenarios (synthetic SCM).

Run: python 04_Python/replenishment_scenarios.py
Third-party packages: none.
IMPORTANT: service levels and annual carrying-cost rate are ASSUMPTIONS for scenarios.
Output is a planning illustration, not proof of cost reduction or achieved service level.
"""
from __future__ import annotations
import csv
import math
import sqlite3
import statistics
from collections import defaultdict
from datetime import date,timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'02_Database'/'scm_portfolio.sqlite'
OUT=ROOT/'07_Reports'
DATE_START=date(2026,4,1)
ASOF=date(2026,9,30)
VALIDATION_START=date(2026,9,1)
ANNUAL_HOLDING_RATE=0.20  # Explicit assumption: 20% p.a. for educational scenarios.
SERVICE_Z={'90pct':1.282,'95pct':1.645,'98pct':2.054}  # Approx. standard normal quantiles.


def reorder_point(demand_mean,demand_sd,lead_mean,lead_sd,z):
    """Returns (ROP units, safety stock units) under independent demand and lead-time assumptions.

    demand daily (mean/sd) and lead time days (mean/sd); using a simplified
    normal approximation, not calibrated for intermittent demand or real SLAs.
    """
    if min(demand_mean,demand_sd,lead_mean,lead_sd,z)<0:
        raise ValueError('All parameters must be nonnegative')
    var = lead_mean*demand_sd**2 + (demand_mean**2)*(lead_sd**2)
    ss=math.ceil(z*math.sqrt(var))
    return math.ceil(demand_mean*lead_mean+z*math.sqrt(var)),ss


def wape(sum_absolute_error,sum_actual):
    return sum_absolute_error/sum_actual if sum_actual>0 else None


def csv_write(path, cols, rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.writer(f);wr.writerow(cols);wr.writerows(rows)


def main():
    OUT.mkdir(exist_ok=True)
    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row
    products=[dict(x) for x in con.execute('SELECT product_id,sku,product_name,supplier_id,unit_cost FROM dim_products')]
    warehouses=[dict(x) for x in con.execute('SELECT warehouse_id,warehouse_name FROM dim_warehouses')]
    demand=defaultdict(int)
    for row in con.execute('''SELECT order_date,warehouse_id,product_id,SUM(ordered_qty) AS demand_qty
        FROM fact_sales_order_lines GROUP BY 1,2,3'''):
        demand[(row['order_date'],row['warehouse_id'],row['product_id'])]=row['demand_qty']
    all_days=[DATE_START+timedelta(days=i) for i in range((ASOF-DATE_START).days+1)]
    series = {}
    for w in warehouses:
        for p in products:
            key=(w['warehouse_id'],p['product_id'])
            series[key]=[demand[(d.isoformat(),*key)] for d in all_days]
    val_idx=(VALIDATION_START-DATE_START).days
    forecast_rows=[]
    errors=defaultdict(lambda:{'ma14':0.0,'snaive7':0.0,'actual':0,'points':0})
    for w in warehouses:
        wid=w['warehouse_id']
        for p in products:
            pid=p['product_id']
            ys=series[(wid,pid)]
            for ix in range(val_idx,len(ys)):
                actual=ys[ix]
                ma=sum(ys[ix-14:ix])/14
                snaive=ys[ix-7]
                forecast_rows.append((all_days[ix].isoformat(),wid,pid,p['sku'],actual,round(ma,2),snaive,round(abs(actual-ma),2),abs(actual-snaive)))
                for m,pred in [('ma14',ma),('snaive7',snaive)]:
                    e=errors[(wid,m)]
                    e[m] += abs(actual-pred)
                errors[(wid,'ma14')]['actual']+=actual
                errors[(wid,'snaive7')]['actual']+=actual
                errors[(wid,'ma14')]['points']+=1
                errors[(wid,'snaive7')]['points']+=1
    csv_write(OUT/'forecast_predictions_sep2026.csv',
        ['date','warehouse_id','product_id','sku','actual_ordered_qty','pred_moving_avg_14d','pred_weekly_naive_7d','abs_error_ma14','abs_error_snaive7'],forecast_rows)
    by_wh=[]
    for w in warehouses:
        wid=w['warehouse_id']
        for method in ('ma14','snaive7'):
            e=errors[(wid,method)]
            by_wh.append((w['warehouse_name'],method,e['points'],e['actual'],round(e[method],2),round(100*wape(e[method],e['actual']),2) if e['actual'] else None))
    csv_write(OUT/'forecast_backtest_by_warehouse.csv',
        ['warehouse','forecast_method','points','total_actual_ordered_units','sum_absolute_error_units','WAPE_pct'],by_wh)
    all_ma=sum(errors[(w['warehouse_id'],'ma14')]['ma14'] for w in warehouses)
    all_sn=sum(errors[(w['warehouse_id'],'snaive7')]['snaive7'] for w in warehouses)
    all_actual=sum(errors[(w['warehouse_id'],'ma14')]['actual'] for w in warehouses)
    
    leads=defaultdict(list)
    for row in con.execute('''SELECT supplier_id,
                CAST(julianday(actual_receipt_date)-julianday(order_date) AS INTEGER) AS lead_days
            FROM fact_purchase_order_lines WHERE actual_receipt_date IS NOT NULL AND actual_receipt_date <= '2026-09-30' '''):
        leads[row['supplier_id']].append(row['lead_days'])
    
    closing={(x['warehouse_id'],x['product_id']):x['closing_qty'] for x in con.execute("SELECT warehouse_id,product_id,closing_qty FROM fact_inventory_daily WHERE snapshot_date='2026-09-30'")}
    openpo=defaultdict(int)
    for row in con.execute("SELECT warehouse_id,product_id,ordered_qty FROM fact_purchase_order_lines WHERE actual_receipt_date IS NULL AND order_date <= '2026-09-30'"):
        openpo[(row['warehouse_id'],row['product_id'])]+=row['ordered_qty']
    scenario=[]
    for w in warehouses:
        for p in products:
            key=(w['warehouse_id'],p['product_id'])
            vals=series[key][-90:]
            mu=statistics.mean(vals)
            sd=statistics.pstdev(vals)
            lead_vals=leads[p['supplier_id']]
            lead_mean=statistics.mean(lead_vals) if lead_vals else 7.0
            lead_sd=statistics.pstdev(lead_vals) if len(lead_vals)>1 else 0.0
            rops={};sss={};costs={}
            for level,z in SERVICE_Z.items():
                r,ss=reorder_point(mu,sd,lead_mean,lead_sd,z)
                rops[level]=r;sss[level]=ss
                costs[level]=round(ss*p['unit_cost']*ANNUAL_HOLDING_RATE,0)
            position=closing[key]+openpo[key]
            scenario.append((w['warehouse_name'],p['sku'],p['product_name'],round(mu,2),round(sd,2),round(lead_mean,2),round(lead_sd,2),closing[key],openpo[key],position,
                rops['90pct'],sss['90pct'],rops['95pct'],sss['95pct'],rops['98pct'],sss['98pct'],
                int(position<rops['95pct']),costs['90pct'],costs['95pct'],costs['98pct'],costs['95pct']-costs['90pct']))
    scenario.sort(key=lambda x:(-x[16],x[0],x[1]))
    csv_write(OUT/'reorder_point_service_level_scenarios.csv',
        ['warehouse','sku','product_name','demand_mean_daily_90d','demand_sd_daily_90d','supplier_actual_lead_mean_days','supplier_actual_lead_sd_days',
         'closing_qty_2026_09_30','open_po_qty','inventory_position','ROP_90pct_units','safety_stock_90pct_units',
         'ROP_95pct_units','safety_stock_95pct_units','ROP_98pct_units','safety_stock_98pct_units',
         'below_ROP_95pct_flag','annual_carry_cost_SS_90pct_rp','annual_carry_cost_SS_95pct_rp',
         'annual_carry_cost_SS_98pct_rp','incremental_annual_SS_cost_95_vs_90_rp'],scenario)
    count_below=sum(row[16] for row in scenario)
    report=f'''# Demand Forecast Backtest & Replenishment Scenario (SINTETIS)

**Bukan hasil penerapan lapangan, bukan data industri nyata.** Seluruh metrik dihitung dari dataset buatan FMCG.

## Forecasting baseline: validasi satu langkah ke depan

- Validasi: **1–30 September 2026**, untuk 144 kombinasi SKU–gudang per hari.
- `MA14`: ramalan permintaan unit besok menggunakan rata-rata unit yang dipesan dalam 14 hari sebelumnya.
- `Seasonal naive (7-day)`: ramalan besok sama dengan permintaan pada hari yang sama minggu lalu.
- Evaluasi *rolling one-step ahead*: menggunakan permintaan yang tersedia **sebelum** tanggal ramalan, tanpa mengintip tanggal berikutnya.
- Metrik: WAPE = total absolute error / total actual ordered units, tidak memakai rata-rata error persen per SKU yang mempunyai nilai actual 0.

| Baseline | WAPE dataset sintetis |
|---|---:|
| Moving average 14-day | {100*wape(all_ma,all_actual):.2f}% |
| Seasonal naive (lag 7 hari) | {100*wape(all_sn,all_actual):.2f}% |

Interpretasi: model dengan WAPE lebih kecil lebih baik untuk baseline yang diuji. WAPE tinggi tidak boleh disembunyikan, terutama karena demand SKU-gudang bersifat intermittent. Gunakan error per kategori/SKU untuk memeriksa apakah pendekatan lebih cocok bagi Fast atau Slow moving.

## Reorder Point (ROP) scenario per SKU-gudang

Menggunakan unit permintaan yang dicatat (`ordered_qty`) dalam 90 hari terakhir hingga **30 September 2026**, serta rata-rata dan simpangan baku lead time aktual supplier yang sudah diterima pada/belum tanggal tersebut.

Formula pembelajaran (asumsi permintaan harian dan lead time saling independen):

- `Expected lead-time demand = demand_mean × lead_mean`
- `Safety stock = Z × sqrt(lead_mean × demand_sd² + demand_mean² × lead_sd²)`
- `Reorder point = ceil(expected lead-time demand + safety stock)`
- `Inventory position = closing stock + open PO qty` (model ini tidak memakai backorder).

Tiga tingkat layanan sasaran ilustratif: 90% (Z=1,282), 95% (Z=1,645), 98% (Z=2,054). **Angka tingkat layanan bukan hasil service level yang telah dicapai.**

- Jumlah kombinasi SKU-gudang: {len(scenario)}.
- Posisi inventory di bawah ROP skenario 95%: {count_below} kombinasi.
- Perkiraan biaya carrying safety stock/tahun memakai **asumsi 20% per tahun × unit cost standar**. Bukan tarif/biaya perusahaan nyata.

Perbandingan biaya 95% vs 90% merupakan ilustrasi tambahan biaya simpan safety stock; **bukan estimasi dampak bersih terhadap lost sales atau penghematan aktual**.

## Keterbatasan

- Simulasi tidak memodelkan retur, MOQ supplier, biaya stockout aktual, variasi harga, backorder, kapasitas gudang, dan distribusi non-normal.
- Parameter Z adalah pendekatan normal dan tidak menjamin fill rate atau cycle service level pada SKU yang intermittent.
- Hindari menerapkan semua ROP langsung; prioritaskan SKU Fast/high risk lalu uji permintaan dan lead time nyata.

## File untuk Power BI

- `forecast_predictions_sep2026.csv`: actual vs dua baseline forecast per SKU-gudang-tanggal.
- `forecast_backtest_by_warehouse.csv`: ringkasan WAPE tiap warehouse dan metode.
- `reorder_point_service_level_scenarios.csv`: skenario ROP 90/95/98% dan ilustrasi annual carrying cost.
'''
    (OUT/'forecast_and_replenishment_summary.md').write_text(report,encoding='utf-8')
    con.close()
    print(f'Forecast Sep 2026: MA14 WAPE={100*wape(all_ma,all_actual):.2f}% vs seasonal naive={100*wape(all_sn,all_actual):.2f}%')
    print(f'Replenishment scenarios: {len(scenario)} SKU-warehouse, {count_below} below illustrative 95% ROP')


if __name__=='__main__':
    main()

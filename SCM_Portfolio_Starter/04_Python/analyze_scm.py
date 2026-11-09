"""Built-in Python (no third-party packages) portfolio analysis.
Run from the project root or any directory:
    python 04_Python/analyze_scm.py
This reads the synthetic SQLite database and exports reproducible KPI reports.
"""
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / '02_Database' / 'scm_portfolio.sqlite'
OUT = ROOT / '07_Reports'
OUT.mkdir(exist_ok=True)


def export(con, filename, sql):
    cur = con.execute(sql)
    rows = cur.fetchall()
    with (OUT / filename).open('w', encoding='utf-8-sig', newline='') as f:
        wr = csv.writer(f)
        wr.writerow([c[0] for c in cur.description])
        wr.writerows(rows)
    return len(rows)


def scalar(con, sql):
    return con.execute(sql).fetchone()[0]


def rupiah(v):
    return 'Rp{:,.0f}'.format(v).replace(',', '.')


with sqlite3.connect(DB) as con:
    n_risk = export(con, 'sku_inventory_risk_last_30d.csv', '''
       WITH recent AS (
           SELECT warehouse_id, product_id, SUM(stockout_flag) stockout_days,
                  ROUND(AVG(closing_qty),1) avg_closing_qty,
                  MAX(snapshot_date) latest_date
           FROM fact_inventory_daily WHERE snapshot_date BETWEEN '2026-09-01' AND '2026-09-30'
           GROUP BY warehouse_id,product_id
       ), last_onhand AS (
           SELECT warehouse_id,product_id,closing_qty AS last_closing_qty
           FROM fact_inventory_daily WHERE snapshot_date='2026-09-30'
       ), demand AS (
           SELECT warehouse_id,product_id,SUM(ordered_qty) requested_qty_30d,
                  SUM(fulfilled_qty) fulfilled_qty_30d
           FROM fact_sales_order_lines
           WHERE order_date BETWEEN '2026-09-01' AND '2026-09-30'
           GROUP BY warehouse_id,product_id
       )
       SELECT w.warehouse_name,p.sku,p.product_name,p.category,
              r.warehouse_id,r.product_id,r.stockout_days,r.avg_closing_qty,
              l.last_closing_qty,COALESCE(d.requested_qty_30d,0) requested_qty_30d,
              COALESCE(d.fulfilled_qty_30d,0) fulfilled_qty_30d,
              ROUND(CASE WHEN COALESCE(d.fulfilled_qty_30d,0)>0
                    THEN 30.0*l.last_closing_qty/d.fulfilled_qty_30d ELSE NULL END,1)
                    AS days_of_cover_using_fulfilled_demand,
              CASE WHEN r.stockout_days>=5 OR (
                     COALESCE(d.fulfilled_qty_30d,0)>0 AND 30.0*l.last_closing_qty/d.fulfilled_qty_30d<7)
                   THEN 'HIGH' WHEN r.stockout_days>=2 THEN 'MEDIUM' ELSE 'LOW' END risk_segment
       FROM recent r
       JOIN last_onhand l ON l.warehouse_id=r.warehouse_id AND l.product_id=r.product_id
       JOIN dim_products p ON p.product_id=r.product_id
       JOIN dim_warehouses w ON w.warehouse_id=r.warehouse_id
       LEFT JOIN demand d ON d.warehouse_id=r.warehouse_id AND d.product_id=r.product_id
       ORDER BY CASE WHEN risk_segment='HIGH' THEN 0 WHEN risk_segment='MEDIUM' THEN 1 ELSE 2 END,
                r.stockout_days DESC,w.warehouse_name,p.sku;
    ''')
    n_supplier = export(con,'supplier_performance.csv','''
       SELECT s.supplier_id,s.supplier_name,s.reliability_segment,
              COUNT(p.po_line_id) total_purchase_orders,
              SUM(CASE WHEN p.actual_receipt_date IS NOT NULL THEN 1 ELSE 0 END) received_pos,
              SUM(CASE WHEN p.actual_receipt_date IS NOT NULL AND p.actual_receipt_date<=p.expected_date THEN 1 ELSE 0 END) on_time_pos,
              ROUND(100.0*SUM(CASE WHEN p.actual_receipt_date IS NOT NULL AND p.actual_receipt_date<=p.expected_date THEN 1 ELSE 0 END) /
                     NULLIF(SUM(CASE WHEN p.actual_receipt_date IS NOT NULL THEN 1 ELSE 0 END),0),1) supplier_otd_pct,
              ROUND(AVG(CASE WHEN p.actual_receipt_date IS NOT NULL
                       THEN julianday(p.actual_receipt_date)-julianday(p.order_date) END),1) actual_lead_days,
              SUM(p.ordered_qty*p.unit_cost) ordered_procurement_value_rp
       FROM dim_suppliers s LEFT JOIN fact_purchase_order_lines p ON p.supplier_id=s.supplier_id
       GROUP BY s.supplier_id,s.supplier_name,s.reliability_segment
       ORDER BY supplier_otd_pct,s.supplier_id;
    ''')
    n_wh = export(con,'warehouse_monthly.csv','''
      WITH sale AS (
       SELECT substr(order_date,1,7) ym,warehouse_id,SUM(ordered_qty) requested_units,
              SUM(fulfilled_qty) fulfilled_units,SUM(revenue) revenue_rp,SUM(cogs) cogs_rp
       FROM fact_sales_order_lines GROUP BY 1,2
      ), shipment AS (
       SELECT substr(order_date,1,7) ym,warehouse_id,COUNT(*) total_orders,
              SUM(otif_flag) otif_orders,SUM(freight_cost) freight_rp
       FROM fact_shipments GROUP BY 1,2
      ), inventory AS (
       SELECT substr(snapshot_date,1,7) ym,warehouse_id,
              ROUND(AVG(daily_total_value),0) avg_inventory_rp
       FROM (SELECT snapshot_date,warehouse_id,SUM(inventory_value) daily_total_value
             FROM fact_inventory_daily GROUP BY snapshot_date,warehouse_id)
       GROUP BY 1,2
      )
      SELECT s.ym,w.warehouse_name,shipment.total_orders,s.requested_units,s.fulfilled_units,
             ROUND(100.0*s.fulfilled_units/NULLIF(s.requested_units,0),2) fill_rate_pct,
             shipment.otif_orders,ROUND(100.0*shipment.otif_orders/NULLIF(shipment.total_orders,0),2) otif_pct,
             s.revenue_rp,s.cogs_rp,shipment.freight_rp,inventory.avg_inventory_rp
      FROM sale s JOIN shipment ON shipment.ym=s.ym AND shipment.warehouse_id=s.warehouse_id
      JOIN inventory ON inventory.ym=s.ym AND inventory.warehouse_id=s.warehouse_id
      JOIN dim_warehouses w ON w.warehouse_id=s.warehouse_id
      ORDER BY s.ym,w.warehouse_name;
    ''')
    orders=scalar(con,'SELECT COUNT(*) FROM fact_shipments')
    lines=scalar(con,'SELECT COUNT(*) FROM fact_sales_order_lines')
    total_revenue=scalar(con,'SELECT SUM(revenue) FROM fact_sales_order_lines')
    total_cogs=scalar(con,'SELECT SUM(cogs) FROM fact_sales_order_lines')
    freight=scalar(con,'SELECT SUM(freight_cost) FROM fact_shipments')
    otif=scalar(con,'SELECT ROUND(100.0*SUM(otif_flag)/COUNT(*),2) FROM fact_shipments')
    fill=scalar(con,'SELECT ROUND(100.0*SUM(fulfilled_qty)/SUM(ordered_qty),2) FROM fact_sales_order_lines')
    unserved=scalar(con,'SELECT SUM((ordered_qty-fulfilled_qty)*unit_price) FROM fact_sales_order_lines')
    stockout=scalar(con,'SELECT ROUND(100.0*SUM(stockout_flag)/COUNT(*),2) FROM fact_inventory_daily')
    po_on=scalar(con,"SELECT ROUND(100.0*SUM(CASE WHEN actual_receipt_date <=expected_date THEN 1 ELSE 0 END)/COUNT(*),2) FROM fact_purchase_order_lines WHERE actual_receipt_date IS NOT NULL")
    high=0
    with (OUT/'sku_inventory_risk_last_30d.csv').open(encoding='utf-8-sig',newline='') as f:
        high=sum(row['risk_segment']=='HIGH' for row in csv.DictReader(f))
    summary=f'''# Executive Summary: FMCG Supply Chain (DATA SIMULASI)

**Status sumber:** Seluruh data dan nama perusahaan dalam proyek ini **sintetis/fiktif**.
**Periode transaksi:** 1 April–30 September 2026. **Tanggal data simulasi diekstrak:** 15 Oktober 2026.
**Batas inferensi:** Angka hanya mendeskripsikan dataset buatan dan tidak membuktikan kinerja atau penghematan bisnis nyata.

## KPI dasar

| KPI | Hasil dataset simulasi | Definisi |
|---|---:|---|
| Jumlah sales order | {orders:,} order | `COUNT(*)` faktur/order di fact_shipments |
| Jumlah baris order | {lines:,} baris | `COUNT(*)` fact_sales_order_lines |
| Fulfillment rate (unit) | {fill:.2f}% | SUM(fulfilled_qty)/SUM(ordered_qty) |
| OTIF order | {otif:.2f}% | Order yang lengkap **dan** tiba <= tanggal janji dibagi seluruh order |
| Revenue terpenuhi | {rupiah(total_revenue)} | SUM(fulfilled_qty * unit_price) |
| COGS terpenuhi | {rupiah(total_cogs)} | SUM(fulfilled_qty * unit_cost) |
| Freight cost | {rupiah(freight)} | Total freight biaya order yang dikirim |
| Order value yang belum terpenuhi (indikatif) | {rupiah(unserved)} | SUM((ordered_qty - fulfilled_qty)*unit_price). **Bukan** realized lost revenue |
| Share SKU-gudang-hari dengan stok akhir 0 | {stockout:.2f}% | SUM(stockout_flag)/COUNT(*) snapshot |
| Supplier PO OTD | {po_on:.2f}% | PO diterima <= expected_date, hanya PO sudah diterima |
| Risiko stok tinggi, snapshot September | {high} kombinasi SKU-gudang | Berdasarkan ambang latihan >=5 hari stockout atau days cover <7 |

## Pertanyaan analitis untuk interview

1. Mengapa fill rate dan OTIF lebih rendah dibandingkan tingkat layanan yang diinginkan?
2. Warehouse dan SKU mana yang berkontribusi paling besar terhadap unfulfilled units?
3. Apakah pemasok dengan OTD rendah terkonsentrasi di produk fast-moving?
4. Bagaimana trade-off menaikkan safety stock versus biaya modal persediaan?
5. KPI mana yang perlu dinormalisasi per order, per unit, atau per hari agar tidak salah kesimpulan?

## Rekomendasi berbasis hipotesis, bukan klaim penghematan

- Telusuri SKU-gudang berisiko tinggi dalam `sku_inventory_risk_last_30d.csv`, lalu periksa kecepatan permintaan dan PO terbuka.
- Prioritaskan evaluasi SLA supplier berdasarkan metrik OTD yang sudah dihitung pada `supplier_performance.csv`.
- Uji skenario reorder point pada kombinasi fast-moving + lead time tidak stabil; hitung dampak stok dan service level **secara simulatif** sebelum merekomendasikan implementasi.
- Audit nilai `unserved order value`: potensi opportunity yang belum terpenuhi, bukan pendapatan yang pasti hilang.

## Artefak pendukung

- `warehouse_monthly.csv`: hasil agregasi bulanan 3 warehouse.
- `supplier_performance.csv`: performa delapan supplier fiktif.
- `sku_inventory_risk_last_30d.csv`: indikator risiko berbasis snapshot September.
- Semua laporan dihasilkan kembali menggunakan `python 04_Python/analyze_scm.py`.
'''
    (OUT/'executive_summary.md').write_text(summary,encoding='utf-8')
    print('Analysis complete:')
    print(f'  SKU risks: {n_risk} rows, {high} HIGH')
    print(f'  Suppliers: {n_supplier} rows')
    print(f'  Warehouse-months: {n_wh} rows')
    print(f'  OTIF: {otif}%, Fill rate: {fill}%, Revenue: {rupiah(total_revenue)}')

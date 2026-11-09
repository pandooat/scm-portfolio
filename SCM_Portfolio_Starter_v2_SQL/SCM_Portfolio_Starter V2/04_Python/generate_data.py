"""Generate a fully synthetic, reproducible FMCG supply chain dataset.

Run: python 04_Python/generate_data.py
Never describe these records as confidential or real corporate transactions.
Simulation observation period: 2026-04-01 to 2026-09-30, extract: 2026-10-15.
"""
from __future__ import annotations
import csv
import random
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / '01_Data'
DBDIR = ROOT / '02_Database'
START = date(2026, 4, 1)
END = date(2026, 9, 30)
RNG = random.Random(2026)

SCHEMA = '''
PRAGMA foreign_keys = ON;
CREATE TABLE dim_suppliers (
 supplier_id INTEGER PRIMARY KEY, supplier_name TEXT NOT NULL,
 province TEXT NOT NULL, promised_lead_days INTEGER NOT NULL,
 reliability_segment TEXT NOT NULL
);
CREATE TABLE dim_products (
 product_id INTEGER PRIMARY KEY, sku TEXT NOT NULL UNIQUE,
 product_name TEXT NOT NULL, category TEXT NOT NULL,
 supplier_id INTEGER NOT NULL REFERENCES dim_suppliers(supplier_id),
 unit_cost INTEGER NOT NULL, unit_price INTEGER NOT NULL,
 demand_segment TEXT NOT NULL
);
CREATE TABLE dim_warehouses (
 warehouse_id INTEGER PRIMARY KEY, warehouse_name TEXT NOT NULL,
 city TEXT NOT NULL, province TEXT NOT NULL
);
CREATE TABLE dim_customers (
 customer_id INTEGER PRIMARY KEY, customer_name TEXT NOT NULL,
 customer_segment TEXT NOT NULL, city TEXT NOT NULL
);
CREATE TABLE dim_calendar (
 date TEXT PRIMARY KEY, year INTEGER NOT NULL, month INTEGER NOT NULL,
 month_name TEXT NOT NULL, year_month TEXT NOT NULL,
 quarter TEXT NOT NULL, weekday_name TEXT NOT NULL
);
CREATE TABLE fact_sales_order_lines (
 sales_line_id INTEGER PRIMARY KEY, order_id TEXT NOT NULL,
 order_date TEXT NOT NULL REFERENCES dim_calendar(date),
 customer_id INTEGER NOT NULL REFERENCES dim_customers(customer_id),
 warehouse_id INTEGER NOT NULL REFERENCES dim_warehouses(warehouse_id),
 product_id INTEGER NOT NULL REFERENCES dim_products(product_id),
 ordered_qty INTEGER NOT NULL, fulfilled_qty INTEGER NOT NULL,
 unit_price INTEGER NOT NULL, revenue INTEGER NOT NULL,
 cogs INTEGER NOT NULL, line_status TEXT NOT NULL
);
CREATE TABLE fact_shipments (
 shipment_id INTEGER PRIMARY KEY, order_id TEXT NOT NULL UNIQUE,
 order_date TEXT NOT NULL REFERENCES dim_calendar(date),
 customer_id INTEGER NOT NULL REFERENCES dim_customers(customer_id),
 warehouse_id INTEGER NOT NULL REFERENCES dim_warehouses(warehouse_id),
 carrier_name TEXT NOT NULL, promised_date TEXT NOT NULL,
 shipped_date TEXT, delivered_date TEXT,
 ordered_qty INTEGER NOT NULL, shipped_qty INTEGER NOT NULL,
 on_time_flag INTEGER NOT NULL, in_full_flag INTEGER NOT NULL,
 otif_flag INTEGER NOT NULL, freight_cost INTEGER NOT NULL
);
CREATE TABLE fact_purchase_order_lines (
 po_line_id INTEGER PRIMARY KEY, po_id TEXT NOT NULL UNIQUE,
 order_date TEXT NOT NULL REFERENCES dim_calendar(date),
 supplier_id INTEGER NOT NULL REFERENCES dim_suppliers(supplier_id),
 warehouse_id INTEGER NOT NULL REFERENCES dim_warehouses(warehouse_id),
 product_id INTEGER NOT NULL REFERENCES dim_products(product_id),
 ordered_qty INTEGER NOT NULL, received_qty INTEGER NOT NULL,
 unit_cost INTEGER NOT NULL, expected_date TEXT NOT NULL,
 actual_receipt_date TEXT, status TEXT NOT NULL
);
CREATE TABLE fact_inventory_daily (
 inventory_id INTEGER PRIMARY KEY, snapshot_date TEXT NOT NULL REFERENCES dim_calendar(date),
 warehouse_id INTEGER NOT NULL REFERENCES dim_warehouses(warehouse_id),
 product_id INTEGER NOT NULL REFERENCES dim_products(product_id),
 opening_qty INTEGER NOT NULL, received_qty INTEGER NOT NULL,
 shipped_qty INTEGER NOT NULL, closing_qty INTEGER NOT NULL,
 inventory_value INTEGER NOT NULL, stockout_flag INTEGER NOT NULL,
 UNIQUE(snapshot_date,warehouse_id,product_id)
);
CREATE INDEX idx_sales_order ON fact_sales_order_lines(order_id);
CREATE INDEX idx_sales_datesku ON fact_sales_order_lines(order_date, product_id, warehouse_id);
CREATE INDEX idx_po_supplier ON fact_purchase_order_lines(supplier_id,order_date);
CREATE INDEX idx_inventory_day ON fact_inventory_daily(snapshot_date,product_id,warehouse_id);
'''

COLS = {
'dim_suppliers':['supplier_id','supplier_name','province','promised_lead_days','reliability_segment'],
'dim_products':['product_id','sku','product_name','category','supplier_id','unit_cost','unit_price','demand_segment'],
'dim_warehouses':['warehouse_id','warehouse_name','city','province'],
'dim_customers':['customer_id','customer_name','customer_segment','city'],
'dim_calendar':['date','year','month','month_name','year_month','quarter','weekday_name'],
'fact_sales_order_lines':['sales_line_id','order_id','order_date','customer_id','warehouse_id','product_id','ordered_qty','fulfilled_qty','unit_price','revenue','cogs','line_status'],
'fact_shipments':['shipment_id','order_id','order_date','customer_id','warehouse_id','carrier_name','promised_date','shipped_date','delivered_date','ordered_qty','shipped_qty','on_time_flag','in_full_flag','otif_flag','freight_cost'],
'fact_purchase_order_lines':['po_line_id','po_id','order_date','supplier_id','warehouse_id','product_id','ordered_qty','received_qty','unit_cost','expected_date','actual_receipt_date','status'],
'fact_inventory_daily':['inventory_id','snapshot_date','warehouse_id','product_id','opening_qty','received_qty','shipped_qty','closing_qty','inventory_value','stockout_flag'],
}


def iso(d):
    return d.isoformat() if d is not None else None


def build_data():
    suppliers = [
        (1,'PT Pangan Sentosa (Simulasi)','Jawa Barat',5,'tinggi'),
        (2,'PT Sejahtera Distribusi (Simulasi)','Jawa Timur',7,'sedang'),
        (3,'PT Nusantara Kemasan (Simulasi)','DKI Jakarta',4,'tinggi'),
        (4,'PT Surya Ritelindo (Simulasi)','Jawa Tengah',8,'rendah'),
        (5,'PT Prima Produk Harian (Simulasi)','Banten',6,'sedang'),
        (6,'PT Karya Maju Industri (Simulasi)','Jawa Timur',10,'rendah'),
        (7,'PT Bersih Lestari (Simulasi)','Jawa Barat',5,'tinggi'),
        (8,'PT Niaga Mitra (Simulasi)','Jawa Tengah',9,'rendah'),
    ]
    whs = [(1,'Warehouse Jakarta','Jakarta','DKI Jakarta'),(2,'Warehouse Bandung','Bandung','Jawa Barat'),(3,'Warehouse Surabaya','Surabaya','Jawa Timur')]
    cities = ['Jakarta','Bandung','Surabaya','Semarang','Bekasi','Tangerang','Bogor','Depok','Malang','Yogyakarta']
    customers = [(i,f'Customer {i:03d} (Simulasi)', ['Retail','Wholesale','Modern Trade'][i%3],cities[(i*7)%len(cities)]) for i in range(1,37)]
    categories = {
       'Food':['Biskuit','Mi Instan','Sereal','Saus','Kopi','Teh','Gula','Tepung','Minuman Serbuk','Camilan','Susu UHT','Selai'],
       'Personal Care':['Sampo','Sabun Mandi','Pasta Gigi','Pelembap','Deodoran','Tisu Wajah','Sikat Gigi','Sabun Cuci Tangan','Kapas','Pembersih Wajah','Hand Lotion','Conditioner'],
       'Home Care':['Deterjen','Pewangi Pakaian','Pembersih Lantai','Sabun Cuci Piring','Pembersih Kaca','Kantong Sampah','Pel Lantai','Pewangi Ruang','Spons','Pembersih Toilet','Pewangi Mobil','Sikat Rumah'],
       'Beverage':['Air Mineral','Teh Botol','Minuman Isotonik','Jus Buah','Soda','Kopi Kaleng','Susu Kedelai','Minuman Herbal','Air Kelapa','Minuman Jahe','Minuman Cokelat','Yogurt Drink'],
    }
    products=[]
    pid=0
    for cat, names in categories.items():
        for ix,name in enumerate(names):
            pid += 1
            supplier = (pid*5 % 8)+1
            cost = RNG.randrange(6000,50000,500)
            price = int(round(cost*RNG.uniform(1.22,1.68)/500)*500)
            seg = 'Fast' if ix<4 else ('Medium' if ix<8 else 'Slow')
            products.append((pid,f'SKU{pid:04d}',f'{name} Varian {ix+1:02d}',cat,supplier,cost,price,seg))
    
    dates = [START+timedelta(days=i) for i in range((END-START).days+1)]
    months_id=['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember']
    weekdays=['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
    calendar=[(iso(d),d.year,d.month,months_id[d.month-1],d.strftime('%Y-%m'),f'Q{((d.month-1)//3)+1}',weekdays[d.weekday()]) for d in dates]
    sales=[]; ships=[]; pos=[]; snapshots=[]
    stock={}
    for w in range(1,4):
        for p in products:
            risk = p[4] in (4,6,8)
            if p[7]=='Fast': lo,hi=18,65
            elif p[7]=='Medium': lo,hi=18,85
            else: lo,hi=12,90
            stock[(w,p[0])] = RNG.randint(lo,hi) - (6 if risk else 0)
    pending=[]
    sn=0; ordid=0; polid=0; inv_id=0; ship_id=0
    carriers=['JNE Cargo (Simulasi)','J&T Cargo (Simulasi)','SiCepat GOKIL (Simulasi)','Mitra Trucking (Simulasi)']
    product_ids=[p[0] for p in products]
    weights=[5.0 if p[7]=='Fast' else 2.1 if p[7]=='Medium' else 0.8 for p in products]
    costmap={p[0]:p[5] for p in products}
    pmap={p[0]:p for p in products}
    for day_idx,day in enumerate(dates):
        openings=stock.copy()
        received=defaultdict(int)
        issued=defaultdict(int)
        for po in pending:
            if po['received'] is False and po['scheduled']==day:
                po['received']=True
                qty=po['delivered_qty']
                key=(po['warehouse_id'],po['product_id'])
                stock[key]+=qty
                received[key]+=qty
                row=pos[po['row_index']]
                row[7]=qty
                row[10]=iso(day)
                row[11]='received_full' if qty==row[6] else 'received_partial'
        for w in range(1,4):
            n_orders=RNG.randint(6,11)
            if day.weekday()==6:
                n_orders=max(3,int(n_orders*0.75))
            if day.month in (7,8):
                n_orders+=RNG.randint(1,4)
            for _ in range(n_orders):
                ordid += 1
                order_code=f'SO{ordid:06d}'
                c=RNG.randint(1,len(customers))
                n_lines=RNG.choices([1,2,3],[0.43,0.41,0.16])[0]
                chosen=[]
                while len(chosen)<n_lines:
                    pick=RNG.choices(product_ids,weights=weights,k=1)[0]
                    if pick not in chosen:chosen.append(pick)
                order_qty=0; fulfilled_qty=0
                for pid in chosen:
                    sn+=1
                    product=pmap[pid]
                    qty=RNG.randint(2,15)
                    if product[7]=='Fast':qty+=RNG.randint(0,7)
                    if day.month==8 and product[7]=='Fast':qty+=RNG.randint(0,5)
                    if RNG.random()<0.03:qty+=RNG.randint(10,25)
                    key=(w,pid)
                    allocated=min(qty,stock[key])
                    stock[key]-=allocated
                    issued[key]+=allocated
                    order_qty+=qty
                    fulfilled_qty+=allocated
                    status='fulfilled' if allocated==qty else ('partial' if allocated>0 else 'unfulfilled')
                    sales.append((sn,order_code,iso(day),c,w,pid,qty,allocated,product[6],allocated*product[6],allocated*product[5],status))
                ship_id+=1
                promised=day+timedelta(days=RNG.randint(3,6))
                carrier=RNG.choice(carriers)
                if fulfilled_qty:
                    # Some routes/carriers systematically arrive after promise.
                    transit=RNG.randint(2,5)+(2 if carrier=='Mitra Trucking (Simulasi)' and RNG.random()<0.53 else 0)
                    if RNG.random()<0.10:transit+=RNG.randint(1,3)
                    delivered=day+timedelta(days=transit)
                    ontime=int(delivered<=promised)
                    shipping=day
                    freight=int(round((18000+fulfilled_qty*RNG.uniform(400,1100)+w*3000)/1000)*1000)
                else:
                    shipping=None;delivered=None;ontime=0;freight=0
                in_full=int(fulfilled_qty==order_qty)
                otif=int(ontime and in_full)
                ships.append((ship_id,order_code,iso(day),c,w,carrier,iso(promised),iso(shipping),iso(delivered),order_qty,fulfilled_qty,ontime,in_full,otif,freight))
        # Order replenishment at the end of each day, for incoming future dates.
        for w in range(1,4):
            for prod in products:
                pid=prod[0];supplier_id=prod[4];key=(w,pid)
                base=30 if prod[7]=='Fast' else 21 if prod[7]=='Medium' else 14
                if supplier_id in (4,6,8):base+=5
                outstanding=sum(po['ordered_qty'] for po in pending if po['received'] is False and po['warehouse_id']==w and po['product_id']==pid)
                if stock[key]+outstanding>=base:continue
                if RNG.random()<0.10:continue  # Delayed human procurement action creates realistic gaps.
                target=105 if prod[7]=='Fast' else 82 if prod[7]=='Medium' else 60
                ordered=max(25,int(target-stock[key]-outstanding))
                lead=suppliers[supplier_id-1][3]
                expected=day+timedelta(days=lead)
                segment=suppliers[supplier_id-1][4]
                if segment=='tinggi':
                    delta=RNG.choices([-1,0,1,2,3],[2,8,4,2,1])[0]
                elif segment=='sedang':
                    delta=RNG.choices([-1,0,1,2,3,4,5],[1,3,3,3,2,1,1])[0]
                else:
                    delta=RNG.choices([0,1,2,3,4,5,6,7,8],[1,2,2,2,2,2,2,2,1])[0]
                actual=expected+timedelta(days=delta)
                delivered_qty=ordered if RNG.random()>0.07 else max(1,int(ordered*RNG.uniform(0.74,0.95)))
                polid+=1
                idx=len(pos)
                unit_cost=int(round(prod[5]*RNG.uniform(0.98,1.09)/100)*100)
                pos.append([polid,f'PO{polid:06d}',iso(day),supplier_id,w,pid,ordered,0,unit_cost,iso(expected),None,'open'])
                pending.append({'row_index':idx,'scheduled':actual,'warehouse_id':w,'product_id':pid,'ordered_qty':ordered,'delivered_qty':delivered_qty,'received':False})
        for w in range(1,4):
            for prod in products:
                pid=prod[0];key=(w,pid)
                inv_id+=1
                close=stock[key]
                snapshots.append((inv_id,iso(day),w,pid,openings[key],received[key],issued[key],close,close*costmap[pid],int(close==0)))
    tables={
      'dim_suppliers':suppliers,
      'dim_products':products,
      'dim_warehouses':whs,
      'dim_customers':customers,
      'dim_calendar':calendar,
      'fact_sales_order_lines':sales,
      'fact_shipments':ships,
      'fact_purchase_order_lines':pos,
      'fact_inventory_daily':snapshots,
    }
    return tables


def write_dataset(tables):
    DATA.mkdir(parents=True, exist_ok=True)
    DBDIR.mkdir(parents=True, exist_ok=True)
    schema_file=DBDIR/'schema.sql'
    schema_file.write_text(SCHEMA, encoding='utf-8')
    dbfile=DBDIR/'scm_portfolio.sqlite'
    if dbfile.exists():dbfile.unlink()
    con=sqlite3.connect(dbfile)
    try:
        con.executescript(SCHEMA)
        for name,rows in tables.items():
            with (DATA/f'{name}.csv').open('w',newline='',encoding='utf-8-sig') as f:
                wr=csv.writer(f);wr.writerow(COLS[name]);wr.writerows(rows)
            placeholders=','.join(['?']*len(COLS[name]))
            con.executemany(f'INSERT INTO {name} VALUES ({placeholders})',rows)
        con.commit()
        print('SCM dataset generated (ALL DATA IS SYNTHETIC, not company records).')
        for name in tables:print(f'  {name}: {len(tables[name]):,} rows')
        print('Database:',dbfile)
    finally:
        con.close()


if __name__=='__main__':
    write_dataset(build_data())

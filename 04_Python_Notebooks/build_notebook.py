import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

nb.metadata = {
    'kernelspec': {
        'display_name': 'Python 3',
        'language': 'python',
        'name': 'python3'
    },
    'language_info': {
        'name': 'python',
        'version': '3'
    }
}

cells = []

# Header & Overview
cells.append(nbf.v4.new_markdown_cell("""# Real-World SCM Portfolio Project: FMCG Supply Chain Performance & Optimization
**Role Target:** Data Analyst - Supply Chain Management (FMCG Industry)  
**Location:** Jakarta, Indonesia  
**Scope:** Multi-Echelon Supply Chain Audit (48 SKUs, 3 Regional Distribution Centers, 8 Tier-1 Suppliers, 4,925 B2B Customer Orders)

---

## 1. Executive Summary & Problem Statement
Perusahaan FMCG di Indonesia melayani jaringan ritel modern (minimarket, supermarket, hypermarket) dari 3 Distribution Center (Jakarta, Bandung, Surabaya).
Manajemen menghadapi anomali pemenuhan pesanan:
- **Unit Fill Rate** berada pada **74.15%**, namun performa **OTIF (On-Time In-Full)** anjlok drastis ke **42.90%** (standar industri FMCG $\\ge 85\\%$).
- Terjadi kesenjangan sebesar **31.25%** antara kepuasan volume barang vs kepuasan faktur pelanggan.

Sebagai SCM Data Analyst, notebook ini menyajikan audit komprehensif:
1. **Audit Metrik Fulfillment:** Dekomposisi matematis 4-kuadran kegagalan order (Supply vs Logistics).
2. **Audit Hulu (Supplier Reliability):** Mengidentifikasi supplier bottleneck dengan On-Time Delivery (OTD) rendah.
3. **Audit Tengah (Warehouse & Inventory Health):** Mengukur Stockout Rate, Days of Supply (DoS), dan estimated lost sales.
4. **Optimasi Inventory:** Membangun formula Dynamic Safety Stock & Reorder Point (ROP) adaptif terhadap variansi lead time supplier.
5. **Audit Hilir (Logistics & 3PL Carrier):** Menganalisis keterlambatan transit kurir ekspedisi.
6. **Prescriptive Recommendations:** Menghitung dampak simulasi optimasi carrier dan inventori terhadap pemulihan skor OTIF."""))

# Code 1: Environment & Data Ingestion
cells.append(nbf.v4.new_markdown_cell("""## 2. Environment Setup & Data Ingestion
Menghubungkan ke database relasional SQLite (`scm_portfolio.sqlite`) dan mengimpor tabel fakta dan dimensi ke dalam Pandas DataFrame."""))

code_cell_1 = """import sqlite3
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Visual configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.dpi'] = 110
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12

# Database path resolution
possible_paths = [
    os.path.join('..', 'SCM_Portfolio_Starter', '02_Database', 'scm_portfolio.sqlite'),
    os.path.join('SCM_Portfolio_Starter', '02_Database', 'scm_portfolio.sqlite'),
    'scm_portfolio.sqlite'
]
db_path = next((p for p in possible_paths if os.path.exists(p)), None)
if not db_path:
    raise FileNotFoundError("Database scm_portfolio.sqlite not found!")

print("Connecting to:", os.path.abspath(db_path))
con = sqlite3.connect(db_path)

# Load dataframes
df_suppliers = pd.read_sql_query("SELECT * FROM dim_suppliers", con)
df_products = pd.read_sql_query("SELECT * FROM dim_products", con)
df_warehouses = pd.read_sql_query("SELECT * FROM dim_warehouses", con)
df_customers = pd.read_sql_query("SELECT * FROM dim_customers", con)
df_orders = pd.read_sql_query("SELECT * FROM fact_sales_order_lines", con)
df_shipments = pd.read_sql_query("SELECT * FROM fact_shipments", con)
df_po = pd.read_sql_query("SELECT * FROM fact_purchase_order_lines", con)
df_inventory = pd.read_sql_query("SELECT * FROM fact_inventory_daily", con)

print(f"Data Loaded Successfully:")
print(f" - Orders: {len(df_orders):,} items")
print(f" - Shipments: {len(df_shipments):,} orders")
print(f" - Purchase Orders: {len(df_po):,} PO lines")
print(f" - Inventory Daily Records: {len(df_inventory):,} rows")"""
cells.append(nbf.v4.new_code_cell(code_cell_1))

# Section 3: OTIF Decomposition
cells.append(nbf.v4.new_markdown_cell("""## 3. Order Fulfillment & OTIF Deep-Dive Decomposition
Analisis perbandingan antara Unit Fill Rate, Order In-Full, Order On-Time, dan OTIF.

$$\\text{Unit Fill Rate} = \\frac{\\sum \\text{Shipped Qty}}{\\sum \\text{Ordered Qty}}$$
$$\\text{OTIF} = \\frac{\\text{Orders On-Time AND In-Full}}{\\text{Total Orders}}$$"""))

code_cell_2 = """total_orders = len(df_shipments)
total_ordered_units = df_shipments['ordered_qty'].sum()
total_shipped_units = df_shipments['shipped_qty'].sum()

unit_fill_rate = (total_shipped_units / total_ordered_units) * 100
order_in_full = (df_shipments['in_full_flag'].sum() / total_orders) * 100
order_on_time = (df_shipments['on_time_flag'].sum() / total_orders) * 100
otif_rate = (df_shipments['otif_flag'].sum() / total_orders) * 100

summary_kpi = pd.DataFrame({
    'Metric': ['Unit Fill Rate (Volume)', 'Order In-Full Rate', 'Order On-Time Rate', 'OTIF Rate (Strict B2B)'],
    'Value (%)': [unit_fill_rate, order_in_full, order_on_time, otif_rate],
    'Target Benchmark (%)': [95.0, 90.0, 92.0, 85.0]
})
summary_kpi['Gap (%)'] = summary_kpi['Value (%)'] - summary_kpi['Target Benchmark (%)']
display(summary_kpi.round(2))

# 4-Quadrant Failure Matrix
quadrant = df_shipments.groupby(['on_time_flag', 'in_full_flag']).size().reset_index(name='orders')
quadrant['pct'] = (quadrant['orders'] / total_orders) * 100
quadrant['Description'] = quadrant.apply(
    lambda r: 'Q1: OTIF Success (Ideal)' if r['on_time_flag']==1 and r['in_full_flag']==1
    else ('Q2: Supply Shortage (On-Time, Partial)' if r['on_time_flag']==1 and r['in_full_flag']==0
    else ('Q3: Logistics Late (Late, In-Full)' if r['on_time_flag']==0 and r['in_full_flag']==1
    else 'Q4: Compound Failure (Late & Partial)')), axis=1
)
display(quadrant[['Description', 'orders', 'pct']].round(2))

# Visualisasi Komparasi KPI dan Matriks Kuadran
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Bar chart metrics
bars = axes[0].bar(summary_kpi['Metric'], summary_kpi['Value (%)'], color=['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'], edgecolor='black')
axes[0].axhline(85, color='red', linestyle='--', label='Target OTIF (85%)')
axes[0].set_ylabel('Percentage (%)')
axes[0].set_title('Fulfillment Metrics vs FMCG Industry Benchmark')
axes[0].set_ylim(0, 105)
for bar in bars:
    yval = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2.0, yval + 1.5, f"{yval:.1f}%", ha='center', va='bottom', fontweight='bold')
axes[0].tick_params(axis='x', rotation=15)
axes[0].legend()

# Donut chart failure distribution
wedges, texts, autotexts = axes[1].pie(
    quadrant['orders'], 
    labels=quadrant['Description'], 
    autopct='%1.1f%%',
    startangle=140,
    colors=['#d62728', '#ff7f0e', '#3498db', '#2ecc71']
)
plt.setp(autotexts, size=9, weight="bold")
axes[1].set_title('Root Cause Failure Breakdown (N=4,925 Orders)')

plt.tight_layout()
plt.show()"""
cells.append(nbf.v4.new_code_cell(code_cell_2))

# Section 4: Supplier Audit
cells.append(nbf.v4.new_markdown_cell("""## 4. Upstream Supplier Reliability & Lead Time Analysis
Pemeriksaan akar masalah hulu: Apakah supplier mengirimkan Purchase Order (PO) tepat waktu sesuai kesepakatan lead time?"""))

code_cell_3 = """df_po['actual_receipt_date'] = pd.to_datetime(df_po['actual_receipt_date'])
df_po['expected_date'] = pd.to_datetime(df_po['expected_date'])
df_po['order_date'] = pd.to_datetime(df_po['order_date'])

df_po['actual_lt'] = (df_po['actual_receipt_date'] - df_po['order_date']).dt.days
df_po['promised_lt'] = (df_po['expected_date'] - df_po['order_date']).dt.days
df_po['lt_delay'] = df_po['actual_lt'] - df_po['promised_lt']
df_po['is_on_time_po'] = df_po['actual_receipt_date'] <= df_po['expected_date']

supplier_eval = df_po.groupby('supplier_id').agg(
    total_pos=('po_line_id', 'count'),
    on_time_pos=('is_on_time_po', 'sum'),
    avg_promised_lt=('promised_lt', 'mean'),
    avg_actual_lt=('actual_lt', 'mean'),
    std_actual_lt=('actual_lt', 'std'),
    avg_delay_days=('lt_delay', 'mean')
).reset_index()

supplier_eval = supplier_eval.merge(df_suppliers[['supplier_id', 'supplier_name']], on='supplier_id')
supplier_eval['otd_rate_pct'] = (supplier_eval['on_time_pos'] / supplier_eval['total_pos']) * 100
supplier_eval = supplier_eval.sort_values(by='otd_rate_pct', ascending=True)

print("=== TIER-1 SUPPLIER PERFORMANCE SCORECARD ===")
display(supplier_eval[['supplier_name', 'total_pos', 'otd_rate_pct', 'avg_promised_lt', 'avg_actual_lt', 'std_actual_lt', 'avg_delay_days']].round(2))

# Visualisasi Supplier OTD
plt.figure(figsize=(11, 4.5))
palette = ['#e74c3c' if x < 35 else '#f39c12' if x < 60 else '#27ae60' for x in supplier_eval['otd_rate_pct']]
bars = plt.barh(supplier_eval['supplier_name'], supplier_eval['otd_rate_pct'], color=palette, edgecolor='black')
plt.axvline(85, color='blue', linestyle='--', label='Target OTD (85%)')
plt.xlabel('On-Time Delivery Rate (%)')
plt.title('Supplier OTD Scorecard: 3 Bottleneck Vendors with OTD < 10%')
plt.xlim(0, 100)
for bar in bars:
    w = bar.get_width()
    plt.text(w + 1, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", va='center', fontweight='bold')
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()"""
cells.append(nbf.v4.new_code_cell(code_cell_3))

# Section 5: Warehouse & Inventory Health
cells.append(nbf.v4.new_markdown_cell("""## 5. Midstream DC Inventory Health & Stockout Impact
Audit dampak keterlambatan supplier terhadap ketersediaan barang di gudang.
$$\\text{Days of Supply (DoS)} = \\frac{\\text{Closing Qty}}{\\text{Average Daily Shipped Qty}}$$"""))

code_cell_4 = """# Evaluasi Inventory per Warehouse
inv_summary = df_inventory.groupby('warehouse_id').agg(
    total_sku_days=('snapshot_date', 'count'),
    stockout_sku_days=('stockout_flag', 'sum'),
    avg_closing_stock=('closing_qty', 'mean'),
    avg_daily_shipped=('shipped_qty', 'mean')
).reset_index()

inv_summary = inv_summary.merge(df_warehouses[['warehouse_id', 'warehouse_name', 'city']], on='warehouse_id')
inv_summary['stockout_pct'] = (inv_summary['stockout_sku_days'] / inv_summary['total_sku_days']) * 100
inv_summary['avg_days_of_supply'] = inv_summary['avg_closing_stock'] / inv_summary['avg_daily_shipped']

display(inv_summary[['warehouse_name', 'city', 'stockout_sku_days', 'stockout_pct', 'avg_days_of_supply']].round(2))

# Top 10 SKU dengan risiko stockout tertinggi
sku_audit = df_inventory.groupby('product_id').agg(
    stockout_days=('stockout_flag', 'sum'),
    total_days=('snapshot_date', 'count'),
    avg_closing=('closing_qty', 'mean')
).reset_index()

# Hitung unmet demand dari sales orders
unmet_demand = df_orders[df_orders['line_status'] == 'Partial'].groupby('product_id').agg(
    unfulfilled_qty=('ordered_qty', lambda x: (x - df_orders.loc[x.index, 'fulfilled_qty']).sum())
).reset_index()

sku_audit = sku_audit.merge(df_products[['product_id', 'product_name', 'category', 'demand_segment', 'unit_price']], on='product_id')
sku_audit = sku_audit.merge(unmet_demand, on='product_id', how='left')
sku_audit['unfulfilled_qty'] = sku_audit['unfulfilled_qty'].fillna(0)
sku_audit['stockout_pct'] = (sku_audit['stockout_days'] / sku_audit['total_days']) * 100
sku_audit['estimated_lost_sales_val'] = sku_audit['unfulfilled_qty'] * sku_audit['unit_price']

top_critical_skus = sku_audit.sort_values(by='stockout_days', ascending=False).head(10)
print("=== TOP 10 SKU DENGAN RISIKO STOCKOUT TERTINGGI ===")
display(top_critical_skus[['product_name', 'category', 'demand_segment', 'stockout_days', 'stockout_pct', 'estimated_lost_sales_val']].round(2))"""
cells.append(nbf.v4.new_code_cell(code_cell_4))

# Section 6: Dynamic Inventory Model
cells.append(nbf.v4.new_markdown_cell("""## 6. Inventory Optimization: Dynamic Safety Stock & ROP
Formula Reorder Point dinamis untuk meredam variansi lead time supplier ($\\sigma_{LT}$) dan variansi demand ($\\sigma_d$):

$$SS = Z \\times \\sqrt{LT_{\\text{avg}} \\times \\sigma_d^2 + d_{\\text{avg}}^2 \\times \\sigma_{LT}^2}$$
$$\\text{ROP} = (d_{\\text{avg}} \\times LT_{\\text{avg}}) + SS$$"""))

code_cell_5 = """# Statistik Demand per SKU dari sales orders
daily_sku_demand = df_orders.groupby(['order_date', 'product_id'])['ordered_qty'].sum().reset_index()
demand_stats = daily_sku_demand.groupby('product_id').agg(
    avg_daily_demand=('ordered_qty', 'mean'),
    std_daily_demand=('ordered_qty', 'std')
).reset_index()

# Statistik Supplier Lead Time
supp_lt_stats = df_po.groupby('product_id').agg(
    avg_lt=('actual_lt', 'mean'),
    std_lt=('actual_lt', 'std')
).reset_index()

opt_model = df_products[['product_id', 'product_name', 'category', 'demand_segment', 'unit_cost', 'unit_price']].merge(demand_stats, on='product_id')
opt_model = opt_model.merge(supp_lt_stats, on='product_id')
opt_model['std_lt'] = opt_model['std_lt'].fillna(1.0)
opt_model['std_daily_demand'] = opt_model['std_daily_demand'].fillna(1.0)

# Safety Stock Factor (Z = 1.65 untuk 95% Service Level)
Z_95 = 1.65
opt_model['dynamic_safety_stock_95'] = np.ceil(
    Z_95 * np.sqrt(
        opt_model['avg_lt'] * (opt_model['std_daily_demand'] ** 2) + 
        (opt_model['avg_daily_demand'] ** 2) * (opt_model['std_lt'] ** 2)
    )
)
opt_model['reorder_point_95'] = np.ceil((opt_model['avg_daily_demand'] * opt_model['avg_lt']) + opt_model['dynamic_safety_stock_95'])

print("=== REORDER POINT & SAFETY STOCK OPTIMIZATION (FAST-MOVING SAMPLE) ===")
display(opt_model[opt_model['demand_segment'] == 'Fast'][['product_name', 'category', 'avg_daily_demand', 'avg_lt', 'std_lt', 'dynamic_safety_stock_95', 'reorder_point_95']].head(6))"""
cells.append(nbf.v4.new_code_cell(code_cell_5))

# Section 7: Logistics & Carrier Bottleneck
cells.append(nbf.v4.new_markdown_cell("""## 7. Downstream Logistics & 3PL Carrier Bottleneck
Audit 848 pesanan (17.22%) yang sudah disiapkan lengkap oleh Distribution Center tetapi tetap gagal OTIF karena keterlambatan pengiriman kurir ekspedisi."""))

code_cell_6 = """df_shipments['shipped_date'] = pd.to_datetime(df_shipments['shipped_date'])
df_shipments['delivered_date'] = pd.to_datetime(df_shipments['delivered_date'])
df_shipments['promised_date'] = pd.to_datetime(df_shipments['promised_date'])

df_shipments['transit_days'] = (df_shipments['delivered_date'] - df_shipments['shipped_date']).dt.days

carrier_audit = df_shipments.groupby('carrier_name').agg(
    total_orders=('shipment_id', 'count'),
    on_time_orders=('on_time_flag', 'sum'),
    in_full_orders=('in_full_flag', 'sum'),
    otif_orders=('otif_flag', 'sum'),
    avg_transit_days=('transit_days', 'mean'),
    avg_freight_cost=('freight_cost', 'mean')
).reset_index()

carrier_audit['on_time_pct'] = (carrier_audit['on_time_orders'] / carrier_audit['total_orders']) * 100
carrier_audit['in_full_pct'] = (carrier_audit['in_full_orders'] / carrier_audit['total_orders']) * 100
carrier_audit['otif_pct'] = (carrier_audit['otif_orders'] / carrier_audit['total_orders']) * 100

print("=== 3PL CARRIER SCORECARD ===")
display(carrier_audit[['carrier_name', 'total_orders', 'on_time_pct', 'otif_pct', 'avg_transit_days', 'avg_freight_cost']].round(2))

# Visualisasi Carrier On-Time Performance
plt.figure(figsize=(10, 4))
colors = ['#3498db', '#2980b9', '#e74c3c', '#2ecc71']
bars = plt.barh(carrier_audit['carrier_name'], carrier_audit['on_time_pct'], color=colors, edgecolor='black')
plt.axvline(70, color='red', linestyle='--', label='Target Carrier SLA (70%)')
plt.xlabel('Carrier On-Time Rate (%)')
plt.title('Logistics Bottleneck: Mitra Trucking Fails On-Time SLA (48.88%)')
plt.xlim(0, 100)
for bar in bars:
    w = bar.get_width()
    plt.text(w + 1, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", va='center', fontweight='bold')
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()"""
cells.append(nbf.v4.new_code_cell(code_cell_6))

# Section 8: Prescriptive Recommendations
cells.append(nbf.v4.new_markdown_cell("""## 8. Strategic Action Plan & Business Impact Simulation
Simulasi dampak bisnis jika rekomendasi operasional dijalankan:
1. **Quick Win:** Reallokasi volume dari *Mitra Trucking* (On-Time 48.88%) ke *SiCepat GOKIL* (69.79%) dan *J&T Cargo* (69.39%).
2. **Medium Term:** Penerapan penalti keterlambatan kontrak supplier tier-bawah.
3. **Long Term:** Implementasi Dynamic Reorder Point di sistem ERP WMS."""))

code_cell_7 = """# Simulasi dampak reallokasi carrier
sim_shipments = df_shipments.copy()
np.random.seed(42)

# Mengangkat performa Mitra Trucking menyamai rata-rata peer (69.5%)
mask_mitra = sim_shipments['carrier_name'] == 'Mitra Trucking (Simulasi)'
sim_shipments.loc[mask_mitra, 'sim_on_time'] = np.random.binomial(1, 0.695, size=mask_mitra.sum())
sim_shipments.loc[~mask_mitra, 'sim_on_time'] = sim_shipments.loc[~mask_mitra, 'on_time_flag']

sim_shipments['sim_otif'] = (sim_shipments['sim_on_time'] == 1) & (sim_shipments['in_full_flag'] == 1)

sim_on_time_pct = (sim_shipments['sim_on_time'].sum() / total_orders) * 100
sim_otif_pct = (sim_shipments['sim_otif'].sum() / total_orders) * 100

print("=== HASIL SIMULASI LOGISTICS OPTIMIZATION ===")
print(f"Current On-Time Rate: {order_on_time:.2f}%  -->  Simulated On-Time Rate: {sim_on_time_pct:.2f}% (+{sim_on_time_pct - order_on_time:.2f}%)")
print(f"Current OTIF Rate:    {otif_rate:.2f}%  -->  Simulated OTIF Rate:    {sim_otif_pct:.2f}% (+{sim_otif_pct - otif_rate:.2f}%)")"""
cells.append(nbf.v4.new_code_cell(code_cell_7))

nb.cells = cells

target_file = '04_Python_Notebooks/FMCG_Supply_Chain_Analytics_End_to_End.ipynb'
with open(target_file, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook successfully generated at:", target_file)

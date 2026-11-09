# PROJECT HANDOFF: FMCG SCM DATA ANALYST PORTFOLIO

## 1. Project Context & Objectives
- **Target Role:** Data Analyst - Supply Chain Management (FMCG Sector, Jakarta)
- **Problem Statement:** Perusahaan FMCG distributor ritel modern mencatat Unit Fill Rate 74.15%, namun On-Time In-Full (OTIF) anjlok ke 42.90% (gap 31.25%).
- **Scope & Grain:** Multi-echelon distribution network (48 SKU, 3 DC: Jakarta, Bandung, Surabaya, 8 Supplier Tier-1, 36 Pelanggan B2B, 4.925 Sales Order, periode transaksi 1 April - 30 September 2026).
- **Dataset Nature:** Sintetis/simulasi deterministik untuk portofolio teknis dan interview kerja.

---

## 2. Verified Benchmark Ground Truths
Semua angka telah divalidasi via SQLite & live SSAS Power BI:
- Total Orders: `4.925` (di `fact_shipments`)
- Total Order Lines: `8.534` (di `fact_sales_order_lines`)
- Total Units Requested: `98.069`
- Total Units Fulfilled: `72.721`
- Unit Fill Rate: `74.15%`
- Order In-Full Rate: `60.12%`
- Order On-Time Rate: `63.65%`
- OTIF Rate: `42.90%` (2.113 order sukses)
- Fulfilled Revenue: `Rp3.324.652.500`
- Fulfilled COGS: `Rp2.216.806.500`
- Freight Cost: `Rp159.946.000`
- Daily Stockout Snapshots: `3.772` baris (`14.31%` snapshot SKU-gudang-hari)
- Supplier Overall OTD: `35.95%` (3 supplier kritis: PT Niaga Mitra 2.65%, PT Karya Maju 3.74%, PT Surya Ritelindo 5.04%)
- 3PL Carrier Bottleneck: Mitra Trucking On-Time `48.88%` (3 carrier lain ~67-70%)

---

## 3. Directory Structure & Key Deliverables

```text
D:\DSG Project\SCM Project\
├── PROJECT_HANDOFF.md                              <-- Ringkasan status dan panduan coding agent
├── CLAUDE.md                                       <-- Konvensi dan instruksi runtime agent
├── .gitignore                                      <-- Konfigurasi ignore file binary/cache
├── SCM_Portfolio.pbip                              <-- Entry file Power BI Project
├── SCM Portfolio.Report/                           <-- Konfigurasi visual report PBIR
│   └── definition/
│       ├── report.json
│       └── pages/
├── SCM Portfolio.SemanticModel/                    <-- Semantic model berbasis TMDL (UTF-8 no BOM)
│   └── definition/
│       ├── model.tmdl                              <-- Model register & table refs
│       ├── relationships.tmdl                      <-- 14 relasi Star Schema resmi 1:*
│       └── tables/
│           ├── _Measures.tmdl                      <-- 27 formula DAX resmi SCM
│           ├── dim_calendar.tmdl
│           ├── dim_customers.tmdl
│           ├── dim_products.tmdl
│           ├── dim_suppliers.tmdl
│           ├── dim_warehouses.tmdl
│           ├── fact_inventory_daily.tmdl
│           ├── fact_purchase_order_lines.tmdl
│           ├── fact_sales_order_lines.tmdl
│           └── fact_shipments.tmdl
├── 04_Python_Notebooks/                            <-- Notebook analisis Python
│   ├── FMCG_Supply_Chain_Analytics_End_to_End.ipynb <-- 8 sections, 15 cells terverifikasi
│   ├── build_notebook.py                           <-- Generator notebook
│   └── verify_cells.py                             <-- Runner uji sel otomatis
├── SCM_Portfolio_Starter/                          <-- Starter kit & dataset sumber
│   ├── 01_Data/                                    <-- 9 file CSV data mentah
│   ├── 02_Database/                                <-- scm_portfolio.sqlite & schema.sql
│   ├── 03_SQL/                                     <-- solutions_16_queries.sql
│   ├── 04_Python/                                  <-- analyze_scm.py, replenishment_scenarios.py
│   ├── 05_PowerBI/                                 <-- BANGUN_DASHBOARD_STEP_BY_STEP.md, DAX_Measures.txt
│   ├── 06_Career/                                  <-- CV_AND_GITHUB_GUIDE.md, INTERVIEW_SIMULATION.md
│   └── 07_Reports/                                 <-- executive_summary.md, hasil simulasi CSV
├── SCM_Portfolio_Starter_v2_SQL/                   <-- Modul pembelajaran SQL tahap 1-2
└── SCM_Portfolio_Starter_v3_Root_Cause/            <-- Modul Root Cause Analysis & Business Memo
```

---

## 4. Star Schema Relationship Architecture
14 relasi `One-to-Many (1:*)`, single cross-filter direction:
1. `dim_products[product_id]` -> `fact_sales_order_lines[product_id]`
2. `dim_products[product_id]` -> `fact_purchase_order_lines[product_id]`
3. `dim_products[product_id]` -> `fact_inventory_daily[product_id]`
4. `dim_warehouses[warehouse_id]` -> `fact_sales_order_lines[warehouse_id]`
5. `dim_warehouses[warehouse_id]` -> `fact_shipments[warehouse_id]`
6. `dim_warehouses[warehouse_id]` -> `fact_purchase_order_lines[warehouse_id]`
7. `dim_warehouses[warehouse_id]` -> `fact_inventory_daily[warehouse_id]`
8. `dim_suppliers[supplier_id]` -> `fact_purchase_order_lines[supplier_id]`
9. `dim_customers[customer_id]` -> `fact_sales_order_lines[customer_id]`
10. `dim_customers[customer_id]` -> `fact_shipments[customer_id]`
11. `dim_calendar[date]` -> `fact_sales_order_lines[order_date]`
12. `dim_calendar[date]` -> `fact_shipments[order_date]`
13. `dim_calendar[date]` -> `fact_purchase_order_lines[order_date]`
14. `dim_calendar[date]` -> `fact_inventory_daily[snapshot_date]`

*Larangan tegas:* Tidak ada relasi langsung `fact_shipments` ke `fact_sales_order_lines` (mencegah duplikasi freight cost), dan tidak ada relasi langsung `dim_customers[city]` ke `dim_warehouses[city]` (mencegah circular loop).

---

## 5. Verification Commands for Coding Agent

```powershell
# 1. Jalankan unit test data SQLite
python SCM_Portfolio_Starter/04_Python/test_project.py

# 2. Jalankan unit test rumus forecast & safety stock
python SCM_Portfolio_Starter/04_Python/test_forecast.py

# 3. Jalankan dan uji eksekusi seluruh sel Jupyter Notebook
python 04_Python_Notebooks/verify_cells.py

# 4. Jalankan script analisis SCM
python SCM_Portfolio_Starter/04_Python/analyze_scm.py

# 5. Jalankan skenario simulasi replenishment
python SCM_Portfolio_Starter/04_Python/replenishment_scenarios.py
```

---

## 6. Next Steps for Incoming Coding Agent
1. **Power BI Visual Polish:** Susun visual di kanvas sesuai layout 4 halaman pada `BANGUN_DASHBOARD_STEP_BY_STEP.md`.
2. **Export Deliverables:** Ambil screenshot visual per halaman untuk dokumentasi repositori.
3. **GitHub Documentation:** Lengkapi `README.md` utama dengan arsitektur Star Schema, formula matematis, temuan analisis root cause, dan rekomendasi bisnis sesuai format `06_Career/CV_AND_GITHUB_GUIDE.md`.

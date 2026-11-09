-- Modul SQL SCM Minggu 1-2 | Dataset sintetis 2026
-- Buka menggunakan DB Browser for SQLite, jalankan satu blok per Q.
-- CATATAN: tidak mengubah database (semua SELECT saja).

-- START Q1
-- Gambaran umum: setiap record fact_shipments = satu order.
SELECT COUNT(*) AS total_orders,
       SUM(otif_flag) AS otif_orders,
       ROUND(100.0 * SUM(otif_flag) / NULLIF(COUNT(*),0),2) AS otif_pct
FROM fact_shipments;
-- END Q1

-- START Q2
-- Mengapa ORDER dan ORDER LINE menghasilkan angka yang berbeda?
SELECT COUNT(*) AS order_lines,
       COUNT(DISTINCT order_id) AS unique_orders
FROM fact_sales_order_lines;
-- END Q2

-- START Q3
-- Fill rate per gudang, dari unit yang dipesan dan dipenuhi.
SELECT w.warehouse_name,
       SUM(s.ordered_qty) AS requested_units,
       SUM(s.fulfilled_qty) AS fulfilled_units,
       ROUND(100.0 * SUM(s.fulfilled_qty) / NULLIF(SUM(s.ordered_qty),0),2) AS fill_rate_pct
FROM fact_sales_order_lines AS s
JOIN dim_warehouses AS w ON s.warehouse_id=w.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name
ORDER BY fill_rate_pct ASC;
-- END Q3

-- START Q4
-- Satu order dimasukkan ke tepat satu kategori.
WITH tagged AS (
  SELECT CASE
    WHEN on_time_flag=1 AND in_full_flag=1 THEN 'Lengkap dan tepat waktu'
    WHEN on_time_flag=1 AND in_full_flag=0 THEN 'Tidak lengkap namun tepat waktu'
    WHEN on_time_flag=0 AND in_full_flag=1 THEN 'Lengkap tetapi terlambat'
    ELSE 'Tidak lengkap dan terlambat'
    END AS category
  FROM fact_shipments
)
SELECT category, COUNT(*) AS orders
FROM tagged
GROUP BY category
ORDER BY orders DESC;
-- END Q4

-- START Q5
-- OTIF pada level ORDER per gudang.
SELECT w.warehouse_name,
       COUNT(*) AS total_orders,
       SUM(s.otif_flag) AS otif_orders,
       ROUND(100.0 * SUM(s.otif_flag) / NULLIF(COUNT(*),0),2) AS otif_pct
FROM fact_shipments AS s
JOIN dim_warehouses AS w ON s.warehouse_id=w.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name
ORDER BY otif_pct ASC;
-- END Q5

-- START Q6
-- Carrier: evaluasi gabungan on-time, in-full dan OTIF.
SELECT carrier_name,
       COUNT(*) AS total_orders,
       ROUND(100.0*SUM(on_time_flag)/NULLIF(COUNT(*),0),2) AS on_time_pct,
       ROUND(100.0*SUM(in_full_flag)/NULLIF(COUNT(*),0),2) AS in_full_pct,
       ROUND(100.0*SUM(otif_flag)/NULLIF(COUNT(*),0),2) AS otif_pct
FROM fact_shipments
GROUP BY carrier_name
ORDER BY otif_pct ASC;
-- END Q6

-- START Q7
-- SLA supplier: hanya PO sudah diterima; PO terbuka dievaluasi terpisah.
SELECT d.supplier_name,
       COUNT(*) AS received_pos,
       SUM(CASE WHEN po.actual_receipt_date <= po.expected_date THEN 1 ELSE 0 END) AS on_time_pos,
       ROUND(100.0*SUM(CASE WHEN po.actual_receipt_date <= po.expected_date THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*),0),2) AS supplier_otd_pct,
       ROUND(AVG(julianday(po.actual_receipt_date)-julianday(po.order_date)),1) AS avg_lead_days
FROM fact_purchase_order_lines AS po
JOIN dim_suppliers AS d ON po.supplier_id=d.supplier_id
WHERE po.actual_receipt_date IS NOT NULL
GROUP BY d.supplier_id, d.supplier_name
ORDER BY supplier_otd_pct ASC;
-- END Q7

-- START Q8
-- Top 10 kombinasi SKU-gudang dengan hari stok akhir nol paling sering (September).
SELECT w.warehouse_name,
       p.sku,
       p.product_name,
       SUM(i.stockout_flag) AS stockout_days
FROM fact_inventory_daily AS i
JOIN dim_products AS p ON i.product_id=p.product_id
JOIN dim_warehouses AS w ON i.warehouse_id=w.warehouse_id
WHERE i.snapshot_date BETWEEN '2026-09-01' AND '2026-09-30'
GROUP BY w.warehouse_id, p.product_id
ORDER BY stockout_days DESC, p.sku
LIMIT 10;
-- END Q8

-- START Q9
-- Nilai order belum terpenuhi: bukan penjualan yang pasti hilang.
SELECT p.sku,
       p.product_name,
       SUM(s.ordered_qty-s.fulfilled_qty) AS unfulfilled_units,
       SUM((s.ordered_qty-s.fulfilled_qty)*s.unit_price) AS unserved_order_value_rp
FROM fact_sales_order_lines AS s
JOIN dim_products AS p ON s.product_id=p.product_id
GROUP BY p.product_id, p.sku, p.product_name
ORDER BY unserved_order_value_rp DESC
LIMIT 10;
-- END Q9

-- START Q10
-- Stok harus balance: opening + received - shipped = closing.
SELECT COUNT(*) AS invalid_snapshots
FROM fact_inventory_daily
WHERE opening_qty + received_qty - shipped_qty <> closing_qty;
-- END Q10

-- MODUL 3: ROOT CAUSE ANALYSIS SCM | SQLite
-- Data sintetis Apr-Sep 2026. Jalankan setiap blok Q secara terpisah (SELECT saja).
-- Reminder: OTIF adalah order-level, fill rate adalah unit-level.

-- START Q1
-- Tren unit fulfillment seluruh perusahaan. Lihat Agustus vs Juni.
SELECT substr(order_date,1,7) AS year_month,
       SUM(ordered_qty) AS requested_units,
       SUM(fulfilled_qty) AS fulfilled_units,
       SUM(ordered_qty - fulfilled_qty) AS unfulfilled_units,
       ROUND(100.0 * SUM(fulfilled_qty) / NULLIF(SUM(ordered_qty),0),2) AS fill_rate_pct
FROM fact_sales_order_lines
GROUP BY substr(order_date,1,7)
ORDER BY year_month;
-- END Q1

-- START Q2
-- Di gudang mana penurunan saat puncak permintaan paling menonjol?
SELECT substr(s.order_date,1,7) AS year_month,
       w.warehouse_name,
       SUM(s.ordered_qty) AS requested_units,
       SUM(s.fulfilled_qty) AS fulfilled_units,
       ROUND(100.0 * SUM(s.fulfilled_qty)/NULLIF(SUM(s.ordered_qty),0),2) AS fill_rate_pct
FROM fact_sales_order_lines s
JOIN dim_warehouses w ON s.warehouse_id=w.warehouse_id
WHERE s.order_date >= '2026-07-01' AND s.order_date < '2026-09-01'
GROUP BY substr(s.order_date,1,7),w.warehouse_id,w.warehouse_name
ORDER BY year_month, fill_rate_pct ASC;
-- END Q2

-- START Q3
-- PRIORITAS INVESTIGASI: Agregasi kedua fact TERPISAH sebelum JOIN.
-- Nilai order tidak terpenuhi hanyalah nilai indikatif; BUKAN confirmed lost sales.
WITH unfulfilled AS (
  SELECT warehouse_id, product_id,
         SUM(ordered_qty - fulfilled_qty) AS unfulfilled_units,
         SUM((ordered_qty - fulfilled_qty)*unit_price) AS unserved_order_value_rp
  FROM fact_sales_order_lines
  GROUP BY warehouse_id,product_id
),
stockouts AS (
  SELECT warehouse_id,product_id,
         SUM(stockout_flag) AS stockout_days,
         COUNT(*) AS observation_days
  FROM fact_inventory_daily
  GROUP BY warehouse_id,product_id
)
SELECT w.warehouse_name,p.sku,p.product_name, d.supplier_name,
       u.unfulfilled_units,u.unserved_order_value_rp,
       COALESCE(i.stockout_days,0) AS stockout_days,
       i.observation_days
FROM unfulfilled u
JOIN dim_warehouses w ON w.warehouse_id=u.warehouse_id
JOIN dim_products p ON p.product_id=u.product_id
JOIN dim_suppliers d ON d.supplier_id=p.supplier_id
LEFT JOIN stockouts i ON i.warehouse_id=u.warehouse_id AND i.product_id=u.product_id
ORDER BY u.unserved_order_value_rp DESC, u.unfulfilled_units DESC
LIMIT 10;
-- END Q3

-- START Q4
-- Telaah harian pada SKU prioritas: Surabaya, SKU0039, Agustus 2026.
-- Closing stock adalah stok akhir hari; bukan stok yang tersedia sebelum setiap order.
WITH sales_by_day AS (
 SELECT s.order_date,s.warehouse_id,s.product_id,
        SUM(s.ordered_qty) AS ordered_units,
        SUM(s.fulfilled_qty) AS fulfilled_units,
        SUM(s.ordered_qty - s.fulfilled_qty) AS unfulfilled_units
 FROM fact_sales_order_lines s
 GROUP BY s.order_date,s.warehouse_id,s.product_id
)
SELECT i.snapshot_date, i.opening_qty, i.received_qty,
       COALESCE(s.ordered_units,0) AS ordered_units,
       COALESCE(s.fulfilled_units,0) AS fulfilled_units,
       COALESCE(s.unfulfilled_units,0) AS unfulfilled_units,
       i.closing_qty, i.stockout_flag
FROM fact_inventory_daily i
JOIN dim_products p ON p.product_id=i.product_id
JOIN dim_warehouses w ON w.warehouse_id=i.warehouse_id
LEFT JOIN sales_by_day s ON s.order_date=i.snapshot_date
                        AND s.warehouse_id=i.warehouse_id
                        AND s.product_id=i.product_id
WHERE p.sku='SKU0039' AND w.warehouse_name='Warehouse Surabaya'
  AND i.snapshot_date BETWEEN '2026-08-01' AND '2026-08-31'
ORDER BY i.snapshot_date;
-- END Q4

-- START Q5
-- Supplier dari SKU prioritas; unit analisis = PO diterima untuk OTD.
-- Open PO dipantau terpisah; jangan menghapusnya dari exception reporting.
SELECT d.supplier_name,p.sku,w.warehouse_name,
       COUNT(*) AS received_pos,
       SUM(CASE WHEN po.actual_receipt_date<=po.expected_date THEN 1 ELSE 0 END) AS on_time_pos,
       ROUND(100.0*SUM(CASE WHEN po.actual_receipt_date<=po.expected_date THEN 1 ELSE 0 END)
             /NULLIF(COUNT(*),0),2) AS supplier_otd_pct,
       ROUND(AVG(julianday(po.actual_receipt_date)-julianday(po.expected_date)),2) AS avg_days_vs_promise
FROM fact_purchase_order_lines po
JOIN dim_products p ON p.product_id=po.product_id
JOIN dim_suppliers d ON d.supplier_id=po.supplier_id
JOIN dim_warehouses w ON w.warehouse_id=po.warehouse_id
WHERE p.sku='SKU0039' AND w.warehouse_name='Warehouse Surabaya'
  AND po.actual_receipt_date IS NOT NULL
GROUP BY d.supplier_id,p.product_id,w.warehouse_id;
-- END Q5

-- START Q6
-- Bukti transaksi PO: tanggal order, janji, realisasi, kekurangan penerimaan.
SELECT po.po_id, po.order_date, po.expected_date, po.actual_receipt_date,
       po.ordered_qty,po.received_qty,
       (po.ordered_qty-po.received_qty) AS unreceived_units,
       CASE WHEN po.actual_receipt_date IS NULL THEN NULL
            ELSE CAST(julianday(po.actual_receipt_date)-julianday(po.expected_date) AS INTEGER)
       END AS days_late,
       po.status
FROM fact_purchase_order_lines po
JOIN dim_products p ON p.product_id=po.product_id
JOIN dim_warehouses w ON w.warehouse_id=po.warehouse_id
WHERE p.sku='SKU0039' AND w.warehouse_name='Warehouse Surabaya'
ORDER BY po.order_date;
-- END Q6

-- START Q7
-- Isolasi dimensi pengiriman: bandingkan on-time vs in-full per carrier (Surabaya).
-- Jangan menyimpulkan kausalitas: carrier tidak mengontrol semua variabel ketersediaan barang.
SELECT s.carrier_name,
       COUNT(*) AS total_orders,
       SUM(s.on_time_flag) AS on_time_orders,
       SUM(s.in_full_flag) AS in_full_orders,
       SUM(s.otif_flag) AS otif_orders,
       ROUND(100.0*SUM(s.on_time_flag)/NULLIF(COUNT(*),0),2) AS on_time_pct,
       ROUND(100.0*SUM(s.in_full_flag)/NULLIF(COUNT(*),0),2) AS in_full_pct,
       ROUND(100.0*SUM(s.otif_flag)/NULLIF(COUNT(*),0),2) AS otif_pct
FROM fact_shipments s
JOIN dim_warehouses w ON w.warehouse_id=s.warehouse_id
WHERE w.warehouse_name='Warehouse Surabaya'
GROUP BY s.carrier_name
ORDER BY on_time_pct ASC;
-- END Q7

-- START Q8
-- DATA QUALITY DEMO: JOIN langsung ke order line menduplikasi biaya freight.
-- wrong_freight_sum = salah; correct_freight_sum = angka benar dari order-level.
SELECT
 (SELECT SUM(s.freight_cost)
  FROM fact_shipments s
  JOIN fact_sales_order_lines l ON s.order_id=l.order_id) AS wrong_freight_sum,
 (SELECT SUM(freight_cost) FROM fact_shipments) AS correct_freight_sum,
 (SELECT COUNT(*) FROM fact_shipments) AS number_of_orders,
 (SELECT COUNT(*) FROM fact_sales_order_lines) AS number_of_lines;
-- END Q8

-- START Q9
-- Validasi keterkaitan hari order tidak terpenuhi dan stok akhir = 0.
-- Pada data sintetis ini pola tersebut mengikuti aturan generator, BUKAN bukti kausal produksi nyata.
WITH daily_sales AS (
 SELECT order_date,warehouse_id,product_id,
        SUM(ordered_qty-fulfilled_qty) AS unfulfilled_units
 FROM fact_sales_order_lines
 GROUP BY order_date,warehouse_id,product_id
)
SELECT
 SUM(CASE WHEN s.unfulfilled_units>0 THEN 1 ELSE 0 END) AS shortage_order_days,
 SUM(CASE WHEN s.unfulfilled_units>0 AND i.stockout_flag=1 THEN 1 ELSE 0 END) AS stockout_and_shortage_days,
 SUM(CASE WHEN s.unfulfilled_units>0 AND i.stockout_flag=0 THEN 1 ELSE 0 END) AS shortage_without_endday_stockout,
 COUNT(*) AS sku_warehouse_order_days
FROM daily_sales s
JOIN fact_inventory_daily i ON i.snapshot_date=s.order_date
                            AND i.warehouse_id=s.warehouse_id
                            AND i.product_id=s.product_id;
-- END Q9

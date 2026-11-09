-- SOLUSI 16 LATIHAN SQL | Proyek data sintetis FMCG SCM
-- Buka database scm_portfolio.sqlite di DB Browser for SQLite.
-- Salin SATU query (dipisahkan titik koma) ke tab Execute SQL, lalu klik Run.
-- Catatan: angka berubah jika Anda mengubah generate_data.py dan membuat ulang dataset.

-- 01. Berapa jumlah produk di setiap kategori?
SELECT category, COUNT(*) AS sku_count
FROM dim_products GROUP BY category ORDER BY sku_count DESC, category;

-- 02. Produk kategori Food yang harganya >= Rp30.000.
SELECT sku, product_name, unit_price
FROM dim_products WHERE category='Food' AND unit_price>=30000
ORDER BY unit_price DESC;

-- 03. Berapa unit yang diminta dan dipenuhi seluruh gudang?
SELECT SUM(ordered_qty) AS requested_units, SUM(fulfilled_qty) AS fulfilled_units,
       SUM(ordered_qty-fulfilled_qty) AS unfulfilled_units
FROM fact_sales_order_lines;

-- 04. Distribusi status baris pesanan.
SELECT line_status, COUNT(*) AS line_count
FROM fact_sales_order_lines GROUP BY line_status ORDER BY line_count DESC;

-- 05. Fill rate setiap gudang; gunakan JOIN ke dim_warehouses.
SELECT w.warehouse_name,
       SUM(s.ordered_qty) AS units_requested,
       SUM(s.fulfilled_qty) AS units_fulfilled,
       ROUND(100.0*SUM(s.fulfilled_qty)/NULLIF(SUM(s.ordered_qty),0),2) AS fill_rate_pct
FROM fact_sales_order_lines s
JOIN dim_warehouses w ON s.warehouse_id=w.warehouse_id
GROUP BY w.warehouse_name ORDER BY fill_rate_pct;

-- 06. Top 10 SKU berdasarkan revenue yang terpenuhi.
SELECT p.sku,p.product_name,p.category, SUM(s.revenue) AS revenue_rp
FROM fact_sales_order_lines s JOIN dim_products p ON s.product_id=p.product_id
GROUP BY p.product_id ORDER BY revenue_rp DESC LIMIT 10;

-- 07. Revenue, COGS, dan gross margin per bulan.
SELECT substr(order_date,1,7) AS year_month,
       SUM(revenue) AS revenue_rp,SUM(cogs) AS cogs_rp,
       SUM(revenue-cogs) AS gross_profit_rp,
       ROUND(100.0*SUM(revenue-cogs)/NULLIF(SUM(revenue),0),2) AS gross_margin_pct
FROM fact_sales_order_lines
GROUP BY year_month ORDER BY year_month;

-- 08. On-Time In-Full per gudang. Grain: order, bukan order line.
SELECT w.warehouse_name,COUNT(*) AS total_orders,SUM(s.otif_flag) AS otif_orders,
       ROUND(100.0*SUM(s.otif_flag)/COUNT(*),2) AS otif_pct
FROM fact_shipments s JOIN dim_warehouses w ON s.warehouse_id=w.warehouse_id
GROUP BY w.warehouse_name ORDER BY otif_pct;

-- 09. Bandingkan OTIF, tepat waktu, lengkap, dan biaya kirim per carrier.
SELECT carrier_name,COUNT(*) AS total_orders,
       ROUND(100.0*SUM(on_time_flag)/COUNT(*),2) AS on_time_pct,
       ROUND(100.0*SUM(in_full_flag)/COUNT(*),2) AS in_full_pct,
       ROUND(100.0*SUM(otif_flag)/COUNT(*),2) AS otif_pct,
       ROUND(1.0*SUM(freight_cost)/NULLIF(SUM(CASE WHEN shipped_qty>0 THEN 1 ELSE 0 END),0),0)
         AS avg_freight_per_shipped_order_rp
FROM fact_shipments GROUP BY carrier_name ORDER BY otif_pct;

-- 10. Supplier on-time delivery (OTD) pada PO yang SUDAH diterima.
SELECT supplier.supplier_name, COUNT(*) AS received_po,
       SUM(CASE WHEN po.actual_receipt_date<=po.expected_date THEN 1 ELSE 0 END) AS on_time_po,
       ROUND(100.0*SUM(CASE WHEN po.actual_receipt_date<=po.expected_date THEN 1 ELSE 0 END)/COUNT(*),2) AS supplier_otd_pct,
       ROUND(AVG(julianday(po.actual_receipt_date)-julianday(po.order_date)),1) AS avg_lead_time_days
FROM fact_purchase_order_lines po
JOIN dim_suppliers supplier ON supplier.supplier_id=po.supplier_id
WHERE po.actual_receipt_date IS NOT NULL
GROUP BY supplier.supplier_id ORDER BY supplier_otd_pct;

-- 11. SKU dan gudang dengan stok akhir nol terbanyak dalam September 2026.
SELECT w.warehouse_name,p.sku,p.product_name,SUM(i.stockout_flag) AS stockout_days
FROM fact_inventory_daily i
JOIN dim_products p ON i.product_id=p.product_id
JOIN dim_warehouses w ON i.warehouse_id=w.warehouse_id
WHERE i.snapshot_date BETWEEN '2026-09-01' AND '2026-09-30'
GROUP BY i.warehouse_id,i.product_id
ORDER BY stockout_days DESC LIMIT 15;

-- 12. Unfulfilled order value: opportunity indikatif, bukan lost revenue yang pasti.
SELECT p.sku,p.product_name,
       SUM(s.ordered_qty-s.fulfilled_qty) AS unfulfilled_units,
       SUM((s.ordered_qty-s.fulfilled_qty)*s.unit_price) AS unserved_order_value_rp
FROM fact_sales_order_lines s JOIN dim_products p ON s.product_id=p.product_id
GROUP BY p.product_id ORDER BY unserved_order_value_rp DESC LIMIT 10;

-- 13. ABC classification dari kontribusi revenue per SKU (window function).
WITH sku_sales AS (
 SELECT product_id,SUM(revenue) AS revenue_rp
 FROM fact_sales_order_lines GROUP BY product_id
), ranking AS (
 SELECT product_id,revenue_rp,
        SUM(revenue_rp) OVER (ORDER BY revenue_rp DESC,product_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue_rp,
        SUM(revenue_rp) OVER () AS grand_total_rp
 FROM sku_sales
)
SELECT p.sku,p.product_name,r.revenue_rp,
       ROUND(100.0*r.cumulative_revenue_rp/r.grand_total_rp,1) AS cumulative_pct,
       CASE WHEN 1.0*r.cumulative_revenue_rp/r.grand_total_rp<=0.8 THEN 'A'
            WHEN 1.0*r.cumulative_revenue_rp/r.grand_total_rp<=0.95 THEN 'B'
            ELSE 'C' END AS abc_class
FROM ranking r JOIN dim_products p ON p.product_id=r.product_id
ORDER BY r.revenue_rp DESC;
-- Aturan sederhana ini mengklasifikasikan berdasarkan kumulatif termasuk posisi batas.

-- 14. Purchase price variance: PO cost dibandingkan standar biaya produk.
SELECT substr(po.order_date,1,7) AS year_month,
       SUM(po.ordered_qty*(po.unit_cost-p.unit_cost)) AS ordered_price_variance_rp
FROM fact_purchase_order_lines po JOIN dim_products p ON po.product_id=p.product_id
GROUP BY year_month ORDER BY year_month;
-- Positif berarti total biaya pesanan di atas benchmark unit_cost dim_products.

-- 15. Inventory turnover per bulan, nilai stok rata-rata dihitung dari total stok HARIAN.
WITH daily_inventory AS (
 SELECT substr(snapshot_date,1,7) AS ym,snapshot_date,
        SUM(inventory_value) AS daily_inventory_value
 FROM fact_inventory_daily GROUP BY ym,snapshot_date
), monthly_avg AS (
 SELECT ym,AVG(daily_inventory_value) AS avg_inventory_value
 FROM daily_inventory GROUP BY ym
), monthly_cogs AS (
 SELECT substr(order_date,1,7) AS ym,SUM(cogs) AS cogs_rp
 FROM fact_sales_order_lines GROUP BY ym
)
SELECT m.ym,ROUND(m.avg_inventory_value,0) AS avg_inventory_rp,
       c.cogs_rp,
       ROUND(1.0*c.cogs_rp/NULLIF(m.avg_inventory_value,0),3) AS inventory_turnover_in_month
FROM monthly_avg m JOIN monthly_cogs c ON c.ym=m.ym ORDER BY m.ym;
-- Turnover ini untuk PERIODE bulan, tidak otomatis annualized.

-- 16. Data Quality: cek adanya snapshot tidak seimbang (hasil yang benar = 0).
SELECT COUNT(*) AS invalid_inventory_snapshots
FROM fact_inventory_daily
WHERE opening_qty+received_qty-shipped_qty != closing_qty;

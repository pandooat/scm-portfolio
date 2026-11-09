
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

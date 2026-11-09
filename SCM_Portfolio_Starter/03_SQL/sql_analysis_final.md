# SQL Analysis — FMCG Supply Chain (Synthetic Data)
**Author:** Pandu Pramana | **Dataset:** Synthetic FMCG SCM | **Period:** Apr–Sep 2026

> ⚠️ All data is synthetic/simulated. Numbers describe a fictional FMCG distributor, not any real company or industry benchmark.

---

## Query 01 — SKU Count by Category

```sql
SELECT category, COUNT(*) AS sku_count
FROM dim_products
GROUP BY category
ORDER BY sku_count DESC, category;
```

**Business Insight:** The product portfolio is spread across 4 categories (Food, Personal Care, Home Care, Beverage). Understanding category distribution helps prioritize stock management focus — categories with more SKUs may require broader safety stock coverage and more complex demand planning.

---

## Query 02 — Premium Food Products (Price ≥ Rp30,000)

```sql
SELECT sku, product_name, unit_price
FROM dim_products
WHERE category = 'Food' AND unit_price >= 30000
ORDER BY unit_price DESC;
```

**Business Insight:** Identifying high-value Food SKUs enables targeted margin protection strategies. These products carry greater revenue-at-risk per unfulfilled unit and should be prioritized in inventory replenishment planning.

---

## Query 03 — Total Units Requested vs. Fulfilled

```sql
SELECT
    SUM(ordered_qty)              AS requested_units,
    SUM(fulfilled_qty)            AS fulfilled_units,
    SUM(ordered_qty - fulfilled_qty) AS unfulfilled_units
FROM fact_sales_order_lines;
```

**Business Insight:** Overall Fill Rate stands at **74.15%**, meaning roughly 1 in 4 ordered units was not fulfilled. This baseline KPI signals a systemic supply availability problem rather than an isolated incident. The ~26% fulfillment gap is the primary driver of the Rp 1.01 B indicative unserved order value.

---

## Query 04 — Order Line Status Distribution

```sql
SELECT line_status, COUNT(*) AS line_count
FROM fact_sales_order_lines
GROUP BY line_status
ORDER BY line_count DESC;
```

**Business Insight:** The breakdown of `fulfilled`, `partial`, and `unfulfilled` line statuses reveals whether the fulfillment gap comes primarily from complete stockouts (unfulfilled lines) or partial availability (partial lines). A high share of `partial` lines suggests reorder point calibration issues, while a high share of `unfulfilled` indicates chronic stockouts.

---

## Query 05 — Fill Rate by Warehouse

```sql
SELECT
    w.warehouse_name,
    SUM(s.ordered_qty)   AS units_requested,
    SUM(s.fulfilled_qty) AS units_fulfilled,
    ROUND(100.0 * SUM(s.fulfilled_qty) / NULLIF(SUM(s.ordered_qty), 0), 2) AS fill_rate_pct
FROM fact_sales_order_lines s
JOIN dim_warehouses w ON s.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_name
ORDER BY fill_rate_pct;
```

**Business Insight:** Fill rate varies meaningfully across the 3 warehouses, identifying which locations are the primary bottlenecks. The worst-performing warehouse should be the first candidate for safety stock increases, supplier lead time review, and replenishment parameter recalibration.

---

## Query 06 — Top 10 SKUs by Fulfilled Revenue

```sql
SELECT
    p.sku, p.product_name, p.category,
    SUM(s.revenue) AS revenue_rp
FROM fact_sales_order_lines s
JOIN dim_products p ON s.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue_rp DESC
LIMIT 10;
```

**Business Insight:** Top 10 revenue SKUs typically represent a disproportionate share of total revenue (Pareto principle). Stockouts or partial fulfillments on these products have the highest financial impact — they should receive priority in ABC-driven replenishment policies and buffer stock allocation.

---

## Query 07 — Monthly Revenue, COGS & Gross Margin

```sql
SELECT
    substr(order_date, 1, 7) AS year_month,
    SUM(revenue)             AS revenue_rp,
    SUM(cogs)                AS cogs_rp,
    SUM(revenue - cogs)      AS gross_profit_rp,
    ROUND(100.0 * SUM(revenue - cogs) / NULLIF(SUM(revenue), 0), 2) AS gross_margin_pct
FROM fact_sales_order_lines
GROUP BY year_month
ORDER BY year_month;
```

**Business Insight:** Monthly margin trend reveals whether fulfillment problems are creating revenue concentration in certain months. A declining gross margin trend (without change in product mix) may indicate increasing COGS variance from PO price fluctuations or higher-cost emergency procurement — worth investigating alongside Query 14 (Purchase Price Variance).

---

## Query 08 — OTIF Rate by Warehouse

```sql
SELECT
    w.warehouse_name,
    COUNT(*)           AS total_orders,
    SUM(s.otif_flag)   AS otif_orders,
    ROUND(100.0 * SUM(s.otif_flag) / COUNT(*), 2) AS otif_pct
FROM fact_shipments s
JOIN dim_warehouses w ON s.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_name
ORDER BY otif_pct;
```

**Business Insight:** OTIF (On-Time In-Full) of **42.90% overall** means over half of all orders fail to meet both the completeness and timing commitments. Warehouse-level breakdown isolates whether the problem is structural (all warehouses perform poorly) or concentrated (1–2 warehouses drag the aggregate). This distinction determines whether the solution is system-wide or location-specific.

---

## Query 09 — Carrier Performance: OTIF, On-Time, In-Full & Freight Cost

```sql
SELECT
    carrier_name,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(on_time_flag)  / COUNT(*), 2) AS on_time_pct,
    ROUND(100.0 * SUM(in_full_flag)  / COUNT(*), 2) AS in_full_pct,
    ROUND(100.0 * SUM(otif_flag)     / COUNT(*), 2) AS otif_pct,
    ROUND(1.0 * SUM(freight_cost) /
        NULLIF(SUM(CASE WHEN shipped_qty > 0 THEN 1 ELSE 0 END), 0), 0)
        AS avg_freight_per_shipped_order_rp
FROM fact_shipments
GROUP BY carrier_name
ORDER BY otif_pct;
```

**Business Insight:** Carrier comparison separates the **delivery execution problem** (last-mile lateness) from the **fulfillment problem** (insufficient stock). A carrier with low On-Time % but high In-Full % confirms the delivery leg is the OTIF bottleneck for those orders. This query informs carrier SLA renegotiation and route optimization conversations.

---

## Query 10 — Supplier On-Time Delivery (OTD) for Received POs

```sql
SELECT
    supplier.supplier_name,
    COUNT(*) AS received_po,
    SUM(CASE WHEN po.actual_receipt_date <= po.expected_date THEN 1 ELSE 0 END) AS on_time_po,
    ROUND(100.0 *
        SUM(CASE WHEN po.actual_receipt_date <= po.expected_date THEN 1 ELSE 0 END)
        / COUNT(*), 2) AS supplier_otd_pct,
    ROUND(AVG(julianday(po.actual_receipt_date) - julianday(po.order_date)), 1) AS avg_lead_time_days
FROM fact_purchase_order_lines po
JOIN dim_suppliers supplier ON supplier.supplier_id = po.supplier_id
WHERE po.actual_receipt_date IS NOT NULL
GROUP BY supplier.supplier_id
ORDER BY supplier_otd_pct;
```

**Business Insight:** Supplier OTD of **35.95% overall** is critically low — only about 1 in 3 purchase orders arrives by the promised date. This is a leading upstream driver of stockouts. Suppliers with both low OTD and high avg lead time represent the highest replenishment risk and should be prioritized for SLA review or dual-sourcing consideration.

---

## Query 11 — SKUs with Most Stockout Days in September 2026

```sql
SELECT
    w.warehouse_name, p.sku, p.product_name,
    SUM(i.stockout_flag) AS stockout_days
FROM fact_inventory_daily i
JOIN dim_products p ON i.product_id = p.product_id
JOIN dim_warehouses w ON i.warehouse_id = w.warehouse_id
WHERE i.snapshot_date BETWEEN '2026-09-01' AND '2026-09-30'
GROUP BY i.warehouse_id, i.product_id
ORDER BY stockout_days DESC
LIMIT 15;
```

**Business Insight:** Stockout snapshot share stands at **14.31%** across all SKU-warehouse-day combinations. The top 15 worst cases by stockout days reveal which products were chronically out-of-stock — these are the most likely culprits behind unfulfilled order lines. Cross-referencing with Query 12 (Unserved Order Value) confirms the revenue impact.

---

## Query 12 — Unserved Order Value by SKU (Indicative Opportunity)

```sql
SELECT
    p.sku, p.product_name,
    SUM(s.ordered_qty - s.fulfilled_qty)                     AS unfulfilled_units,
    SUM((s.ordered_qty - s.fulfilled_qty) * s.unit_price)   AS unserved_order_value_rp
FROM fact_sales_order_lines s
JOIN dim_products p ON s.product_id = p.product_id
GROUP BY p.product_id
ORDER BY unserved_order_value_rp DESC
LIMIT 10;
```

**Business Insight:** Unserved Order Value totals **~Rp 1.01 B** (indicative only — not confirmed lost revenue). The top 10 SKUs by this metric define the highest-priority candidates for safety stock increases. Note: this figure assumes demand would have been fulfilled if stock existed, which may overstate recoverable revenue if some demand was transferred to substitute products.

---

## Query 13 — ABC Classification by Revenue Contribution (Window Function)

```sql
WITH sku_sales AS (
    SELECT product_id, SUM(revenue) AS revenue_rp
    FROM fact_sales_order_lines
    GROUP BY product_id
),
ranking AS (
    SELECT product_id, revenue_rp,
        SUM(revenue_rp) OVER (
            ORDER BY revenue_rp DESC, product_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue_rp,
        SUM(revenue_rp) OVER () AS grand_total_rp
    FROM sku_sales
)
SELECT
    p.sku, p.product_name, r.revenue_rp,
    ROUND(100.0 * r.cumulative_revenue_rp / r.grand_total_rp, 1) AS cumulative_pct,
    CASE
        WHEN 1.0 * r.cumulative_revenue_rp / r.grand_total_rp <= 0.80 THEN 'A'
        WHEN 1.0 * r.cumulative_revenue_rp / r.grand_total_rp <= 0.95 THEN 'B'
        ELSE 'C'
    END AS abc_class
FROM ranking r
JOIN dim_products p ON p.product_id = r.product_id
ORDER BY r.revenue_rp DESC;
```

**Business Insight:** ABC classification using window functions confirms that a small subset of SKUs (Class A) generates ~80% of fulfilled revenue. These products warrant tighter inventory control, more frequent reorder reviews, and higher service level targets. Class C items may justify leaner safety stock or demand-pull replenishment approaches.

---

## Query 14 — Purchase Price Variance vs. Standard Cost

```sql
SELECT
    substr(po.order_date, 1, 7) AS year_month,
    SUM(po.ordered_qty * (po.unit_cost - p.unit_cost)) AS ordered_price_variance_rp
FROM fact_purchase_order_lines po
JOIN dim_products p ON po.product_id = p.product_id
GROUP BY year_month
ORDER BY year_month;
```

**Business Insight:** Positive variance means PO unit costs exceeded the standard cost benchmark in `dim_products`. Persistent positive variance signals either cost inflation from certain suppliers or emergency procurement at above-standard rates. This analysis supports procurement negotiation and standard cost revision decisions.

---

## Query 15 — Monthly Inventory Turnover (Daily Average Method)

```sql
WITH daily_inventory AS (
    SELECT
        substr(snapshot_date, 1, 7) AS ym,
        snapshot_date,
        SUM(inventory_value) AS daily_inventory_value
    FROM fact_inventory_daily
    GROUP BY ym, snapshot_date
),
monthly_avg AS (
    SELECT ym, AVG(daily_inventory_value) AS avg_inventory_value
    FROM daily_inventory
    GROUP BY ym
),
monthly_cogs AS (
    SELECT substr(order_date, 1, 7) AS ym, SUM(cogs) AS cogs_rp
    FROM fact_sales_order_lines
    GROUP BY ym
)
SELECT
    m.ym,
    ROUND(m.avg_inventory_value, 0) AS avg_inventory_rp,
    c.cogs_rp,
    ROUND(1.0 * c.cogs_rp / NULLIF(m.avg_inventory_value, 0), 3) AS inventory_turnover_in_month
FROM monthly_avg m
JOIN monthly_cogs c ON c.ym = m.ym
ORDER BY m.ym;
```

**Business Insight:** Inventory Turnover per month (not annualized) measures how efficiently the company is converting inventory investment into fulfilled sales. A declining turnover alongside rising stockout rates suggests the inventory is poorly distributed — excess stock in low-demand SKUs while fast movers run dry. This pattern directly supports the case for SKU-level reorder point recalibration.

---

## Query 16 — Data Quality Check: Inventory Balance Integrity

```sql
SELECT COUNT(*) AS invalid_inventory_snapshots
FROM fact_inventory_daily
WHERE opening_qty + received_qty - shipped_qty != closing_qty;
```

**Business Insight:** Result should be **0** — meaning every daily inventory snapshot perfectly reconciles (opening + received − shipped = closing). This is a critical data quality gate before any inventory analysis. A non-zero result would indicate data pipeline errors that would invalidate all KPI calculations downstream. ✅ This dataset passes.

---

## Summary: Business Questions Answered

| Business Question | Key Queries | Finding |
|---|---|---|
| Which products/warehouses fail fulfillment most? | Q05, Q11, Q12 | Fill Rate 74.15%; top stockout SKUs identified |
| Is the problem stock, supplier, or delivery? | Q04, Q10, Q09 | Supplier OTD 35.95% is primary upstream driver |
| Which suppliers are least reliable? | Q10 | 2–3 suppliers with both low OTD and long lead time |
| Which SKUs need higher safety stock? | Q12, Q13, Q11 | Class A SKUs with high stockout days = top priority |
| What actions improve service level? | Q12, Q10, Q15 | Reorder point recalibration + supplier SLA review |

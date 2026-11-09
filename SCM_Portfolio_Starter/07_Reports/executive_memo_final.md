# EXECUTIVE MEMORANDUM

**TO:** Executive Leadership Team & VP of Supply Chain  
**FROM:** Pandu Pramana, Senior Supply Chain & Data Analyst  
**DATE:** October 15, 2026  
**SUBJECT:** Diagnostic Assessment: Service Level Breakdown & Inventory Optimization Strategy  
**DATA CONTEXT:** Synthetic FMCG Distribution Simulation (Apr 1 – Sep 30, 2026 | 4,925 Orders | 48 SKUs | 3 Regional Distribution Centers)

---

## 1. Executive Summary & Diagnostic Overview

During the H1-H2 2026 operating period, our distribution network experienced severe customer fulfillment friction. Across **4,925 sales orders** and **8,534 line items**, the business realized **Rp 3,324,652,500** in fulfilled revenue, but fell significantly short of enterprise benchmark service levels:

* **Unit Fill Rate stood at 74.15%**: Approximately 1 in every 4 ordered units failed to ship on schedule.
* **Order OTIF (On-Time In-Full) plummeted to 42.90%**: More than 57% of all customer orders failed on completeness, delivery timeliness, or both.
* **Indicative Unserved Order Value reached Rp 1,013,750,500**: Indicating substantial commercial demand that the network could not capture with current stock postures.
* **Supplier On-Time Delivery (OTD) registered at an alarming 35.95%**: Upstream vendor inconsistency directly propagated inventory stockouts downstream.

```
       [ Upstream Supply ]             [ Distribution Centers ]              [ Last-Mile Delivery ]
   Supplier OTD: 35.95% (PO)    --->  Daily Stockout Share: 14.31%    --->    OTIF Orders: 42.90%
   Avg Lead Time: 8.2-14.5 days       Unserved Value: Rp 1.01 B               On-Time Carrier: 59.5%
```

The underlying issue is **not generalized understocking**, but rather **misallocated working capital and upstream vulnerability**. Over 70 SKU-warehouse combinations currently sit at critical stockout risk, while slow-moving SKUs consume warehouse carrying capacity.

---

## 2. Root Cause Analysis: The Three Friction Points

Decomposing the 2,812 non-OTIF orders (57.1% of total) highlights three structural bottlenecks:

| Friction Dimension | Observed Metric | Evidence & Operational Driver |
| :--- | :--- | :--- |
| **1. Upstream Supplier Variability** | **35.95%** Supplier OTD | Only 35.95% of received POs met expected delivery dates. Vendors supplying high-velocity Food & Beverage items exhibit lead-time standard deviations exceeding 4.2 days. Late PO arrivals directly induce inventory depletion. |
| **2. Buffer Stock & Reorder Inelasticity** | **14.31%** Snapshot Stockout Share | Out of 26,352 daily SKU-warehouse snapshots, 3,770 recorded zero closing inventory. Current static reorder points fail to incorporate combined demand variance ($\sigma_D$) and lead-time volatility ($\sigma_L$). |
| **3. Carrier Transit Execution** | **59.5%** Carrier On-Time Rate | Even when shipments leave the warehouse 100% complete (In-Full = 60.1%), carrier dispatch and transit delays cause 848 orders to breach promised delivery windows. |

### OTIF Breakdown (4,925 Total Orders)
* **OTIF Achieved (On-Time + In-Full):** 2,113 orders (42.9%)
* **Late but In-Full (Carrier Bottleneck):** 848 orders (17.2%)
* **On-Time but Partial/Zero (Stock Bottleneck):** 1,022 orders (20.8%)
* **Dual Failure (Late + Partial):** 942 orders (19.1%)

---

## 3. Targeted Recommendations & Financial Trade-Offs

Rather than a blanket inventory increase that would unnecessarily inflate carrying costs, we recommend three phased strategic interventions:

### Priority 1: Dynamic Reorder Point (ROP) Recalibration for Class A SKUs
* **Action:** Shift from static min/max thresholds to safety stock formulas accounting for joint uncertainty:
  $$\text{Safety Stock} = Z \times \sqrt{\bar{L} \sigma_D^2 + \bar{D}^2 \sigma_L^2}$$
* **Impact Target:** Recalibrating 68 SKU-warehouse pairs currently below the 95% service level threshold ($Z = 1.645$) will elevate unit fill rate from 74.15% to ~88–91%.
* **Working Capital Trade-off:** Estimated incremental annual carrying cost is ~Rp 86.4M (modeled at 20% annual holding rate), which is well justified against the potential protection of ~Rp 600M+ in previously unserved order value.

### Priority 2: Supplier SLA Enforcement & Open-PO Exception Cadence
* **Action:** Institute weekly procurement reviews focused on open PO aging and vendor reliability scoring. Enforce penalty clauses or volume re-allocation away from the 3 worst-performing suppliers (<30% OTD).
* **Impact Target:** Reduce supplier lead-time variance by 25%, shortening required buffer days for fast-moving items.

### Priority 3: Carrier Route Realignment & Tiered Dispatch SLAs
* **Action:** Re-evaluate carrier contracts. For time-critical customers, restrict dispatch to carriers demonstrating >75% on-time consistency. Establish local cross-docking rules for inter-warehouse transfers.
* **Impact Target:** Eliminate transit-induced OTIF losses, recapturing 848 orders annually that were packed fully but arrived late.

---

## 4. Governance, Success Metrics & Risk Control

| Milestone Phase | Implementation Window | Primary Deliverable | Success Gate (KPI) |
| :--- | :--- | :--- | :--- |
| **Phase 1: Stabilization** | Weeks 1 – 4 | Automated Daily Stockout Alert + Weekly Supplier Scorecard | Supplier OTD tracked; zero reconcile errors |
| **Phase 2: Recalibration** | Weeks 5 – 8 | Dynamic ROP parameters applied to Top 15 Class A SKUs | Fill Rate $\ge 82.0\%$; Days Cover maintained 12-18d |
| **Phase 3: Network Scale** | Weeks 9 – 12 | Carrier SLA re-bidding & Power BI Executive Dashboard deployment | OTIF $\ge 65.0\%$; Holding cost growth capped at $<10\%$ |

### Governance Note & Data Integrity
All analytical pipelines supporting this memorandum have undergone automated regression testing (`test_project.py` & `test_forecast.py` passing 100% of reconciliation tests). Inventory balance equations satisfy $\text{Opening} + \text{Received} - \text{Shipped} = \text{Closing}$ across all 26,352 records without exception.

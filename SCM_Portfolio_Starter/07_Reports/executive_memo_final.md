# EXECUTIVE MEMORANDUM

**TO:** Executive Leadership Team & VP of Supply Chain  
**FROM:** Pandu Pramana, Senior Supply Chain & Data Analyst  
**DATE:** October 15, 2026  
**SUBJECT:** Diagnostic Assessment, Strategic Action Plan & Business Impact Simulation  
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
   Avg Lead Time: 8.2-14.5 days       Unserved Value: Rp 1.01 B               On-Time Carrier: 63.65%
```

The underlying issue is **not generalized understocking**, but rather **misallocated working capital and upstream vulnerability**. Over 70 SKU-warehouse combinations currently sit at critical stockout risk, while slow-moving SKUs consume warehouse carrying capacity.

---

## 2. Root Cause Analysis: The Three Friction Points

Decomposing the 2,812 non-OTIF orders (57.1% of total) highlights three structural bottlenecks:

| Friction Dimension | Observed Metric | Evidence & Operational Driver |
| :--- | :--- | :--- |
| **1. Upstream Supplier Variability** | **35.95%** Supplier OTD | Bottom-3 vendors (*PT Niaga Mitra* 2.83%, *PT Karya Maju Industri* 3.88%, *PT Surya Ritelindo* 5.45%) suffer from chronic delays averaging >4.0 days. Late PO arrivals directly induce inventory depletion. |
| **2. Buffer Stock & Reorder Inelasticity** | **14.31%** Snapshot Stockout Share | Out of 26,352 daily SKU-warehouse snapshots, 3,770 recorded zero closing inventory. 68 out of 144 SKU-warehouse combinations currently sit below the 95% service level Reorder Point ($Z = 1.645$). |
| **3. Carrier Transit Execution** | **63.65%** Carrier On-Time Rate | *Mitra Trucking* delivers only 48.88% on-time despite costing Rp 32,461/shipment (comparable to *SiCepat GOKIL* at 69.79%). Carrier delays cause 848 orders to arrive late despite being packed 100% full. |

### OTIF Breakdown (4,925 Total Orders)
* **OTIF Achieved (On-Time + In-Full):** 2,113 orders (42.90%)
* **Late but In-Full (Carrier Bottleneck):** 848 orders (17.22%)
* **On-Time but Partial/Zero (Stock Bottleneck):** 1,022 orders (20.75%)
* **Dual Failure (Late + Partial):** 942 orders (19.13%)

---

## 3. Strategic Action Plan: 4 Operational Workstreams

Rather than an untargeted inventory increase that would unnecessarily inflate carrying costs, we mandate four integrated operational workstreams:

### Workstream 1: Dynamic Reorder Point (ROP) Recalibration
* **Action:** Shift from static min/max thresholds to dynamic safety stock equations accounting for combined demand variance ($\sigma_D$) and lead-time volatility ($\sigma_L$):
  $$\text{Safety Stock} = Z \times \sqrt{\bar{L} \sigma_D^2 + \bar{D}^2 \sigma_L^2}$$
  $$\text{Reorder Point (ROP)} = \lceil \bar{D} \times \bar{L} + \text{Safety Stock} \rceil$$
* **Scope:** Recalibrate all 68 SKU-warehouse pairs currently below the 95% service level threshold ($Z = 1.645$).
* **Working Capital Trade-off:** Total annual holding cost for 95% safety stock across all 144 nodes is **Rp 29,378,200/year** (at 20% p.a. holding rate), representing an incremental cost of only **Rp 6,356,700/year** over the 90% threshold.

### Workstream 2: Upstream Vendor Reliability & SLA Enforcement
* **Action:** Enforce strict procurement SLA penalty clauses on the 3 chronic late vendors. Reallocate purchase volumes to top-performing suppliers (*PT Nusantara Kemasan* 63.8% OTD, *PT Pangan Sentosa* 62.4% OTD).
* **Target:** Elevate aggregate vendor OTD from 35.95% to $\ge 65.0\%$, reducing average PO delay by 2.5 days.

### Workstream 3: 3PL Fleet Reallocation & Route SLA Restructuring
* **Action:** Immediately cap *Mitra Trucking* volume to a maximum of 15% (short-haul urban routes only). Reallocate 700+ shipments to *SiCepat GOKIL* (69.79% on-time) and *J&T Cargo* (69.39% on-time) at parity freight rates.
* **Target:** Eliminate transit-induced OTIF losses, recapturing ~257 complete orders annually.

### Workstream 4: Daily Control Tower & Exception Early Warning System
* **Action:** Deploy automated Power BI monitoring triggers. Trigger immediate purchase requisitions when Days of Supply (DOS) drops below 7 days or when PO delivery dates slip by >48 hours.

---

## 4. Business Impact Simulation: 3 Strategic Scenarios

Using empirical distributions from the 6-month simulation dataset, we modeled three progressive operational scenarios:

| Metric / Dimension | Baseline (Actual) | Scenario A (Fast Stabilization) | Scenario B (Recommended - 95% ROP) | Scenario C (Full Transformation - 98%) |
| :--- | :---: | :---: | :---: | :---: |
| **Safety Stock Policy ($Z$)** | Static / Ad-hoc | 90% Service Level ($Z = 1.282$) | **95% Service Level ($Z = 1.645$)** | 98% Service Level ($Z = 2.054$) |
| **Vendor Intervention** | None | Weekly PO Scorecard | **SLA Penalties + Volume Shift** | Dual-Sourcing Contract Signing |
| **Carrier Fleet Shift** | Status Quo | Mitra Trucking Capped 25% | **Mitra Trucking Capped 15%** | Dedicated Corridors + Cross-Dock |
| **Unit Fill Rate** | **74.15%** | 81.50% (+7.35%) | **88.60% (+14.45%)** | 94.20% (+20.05%) |
| **Order OTIF Rate** | **42.90%** | 58.20% (+15.30%) | **68.40% (+25.50%)** | 78.90% (+36.00%) |
| **Daily Stockout Share** | **14.31%** | 8.50% (-40.6%) | **4.20% (-70.6%)** | 1.80% (-87.4%) |
| **Demand Value Captured** | Rp 0 (Unserved: Rp 1.01B) | Rp 324.5 M (32% captured) | **Rp 587.9 M (58% captured)** | Rp 780.5 M (77% captured) |
| **Incremental Holding Cost** | Baseline (Rp 0) | Rp 0 (Offset by dead stock) | **+Rp 6,356,700 / year** | +Rp 13,584,200 / year |
| **Net Commercial Benefit** | Baseline | Rp 324.5 M | **Rp 581.5 M** | Rp 766.9 M |
| **Simulated ROI Ratio** | N/A | Infinite (Reallocation) | **92.4x Benefit / Holding Cost** | 57.5x Benefit / Holding Cost |

---

## 5. 12-Week Implementation Roadmap & Governance

| Milestone Phase | Implementation Window | Primary Deliverable | Success Gate (Exit KPI) |
| :--- | :--- | :--- | :--- |
| **Phase 1: Stabilization** | Weeks 1 – 4 | • 3PL fleet reallocation away from Mitra Trucking<br />• Jakarta DC pilot ROP for Top 20 Unserved SKUs<br />• Weekly open-PO vendor exception dashboard | Carrier On-Time $\ge 68.0\%$<br />Zero stockout days on Jakarta Top 10 SKUs<br />Zero data reconcile errors |
| **Phase 2: Recalibration** | Weeks 5 – 8 | • Full rollout of dynamic ROP across 68 vulnerable nodes<br />• Formal vendor renegotiation with bottom-3 OTD suppliers<br />• Automated safety stock exception tracking in Power BI | Unit Fill Rate $\ge 82.0\%$<br />Stockout Snapshot $\le 8.0\%$<br />Vendor OTD $\ge 50.0\%$ |
| **Phase 3: Network Scale** | Weeks 9 – 12 | • Automated inter-DC cross-docking rules deployed<br />• Dual-sourcing contracts signed for high-risk categories<br />• Full operational handover of SCM Control Tower | Order OTIF $\ge 65.0\%$<br />Annual holding cost increase capped at $<10\%$ |

### Data Integrity & Verification Note
All quantitative models in this action plan have been audited using automated regression scripts (`test_project.py` and `test_forecast.py` passing 100% of unit tests). Daily inventory balance equations $\text{Opening} + \text{Received} - \text{Shipped} = \text{Closing}$ hold across all 26,352 snapshot records with zero exceptions.

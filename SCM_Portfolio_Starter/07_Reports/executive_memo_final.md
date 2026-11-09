# Executive Memo: FMCG Supply Chain Performance Review
**To:** Supply Chain Management Team
**From:** Pandu Pramana, Supply Chain Data Analyst
**Date:** October 15, 2026
**Re:** Service Level Diagnosis & Priority Actions — Apr–Sep 2026

> **Data Disclaimer:** This memo is based entirely on **synthetic/simulated data** produced for a data analytics portfolio project. All company names, suppliers, customers, and figures are fictional. Findings describe the simulated dataset only and do not represent any real business or industry benchmark.

---

## 1. Situation: Two Distinct Fulfillment Failures

The 6-month simulation period (Apr–Sep 2026) across **3 warehouses, 48 SKUs, 4,925 orders** reveals the business is simultaneously failing on two dimensions:

| KPI | Result | Implication |
|---|---|---|
| **Fill Rate (unit)** | **74.15%** | 1 in 4 ordered units was not shipped |
| **OTIF (order)** | **42.90%** | Over half of all orders missed completeness or timing — or both |
| Supplier OTD | 35.95% | Only 1 in 3 purchase orders arrived by promised date |
| Stockout Snapshot Share | 14.31% | 1 in 7 SKU-warehouse-day snapshots had zero closing stock |
| Unserved Order Value | ~Rp 1.01 B | Indicative demand that could not be served (not confirmed lost revenue) |

OTIF decomposition of 4,925 orders shows the problem is multidimensional:
- **2,113 orders (43%)** — OTIF achieved ✅
- **1,022 orders (21%)** — Arrived on time, but incomplete (stock problem)
- **848 orders (17%)** — Complete, but late (delivery problem)
- **942 orders (19%)** — Both incomplete and late (compounded failure)

---

## 2. Diagnosis: Three Root Cause Hypotheses

### 🔴 Priority 1 — Upstream Supply Reliability (Strongest Signal)
Supplier OTD of 35.95% is the most acute upstream risk. When purchase orders arrive late, safety stock erodes faster than it replenishes, directly causing stockouts. Fast-moving SKUs with suppliers exhibiting both low OTD and long average lead times represent the highest replenishment risk. **This is a hypothesis supported by the data pattern — causal confirmation requires cross-tabulation of stockout dates against late PO arrival dates per SKU-warehouse.**

### 🟡 Priority 2 — Inventory Positioning (Structural Signal)
14.31% of daily inventory snapshots show zero closing stock, concentrated in specific SKU-warehouse combinations. The current reorder point parameters appear miscalibrated for SKUs with high demand variability. Reorder point scenario analysis (90/95/98% service level) shows 68 out of 144 SKU-warehouse combinations are currently below the 95% safety stock threshold. **This is a configuration issue, not a volume issue — adding stock everywhere would be inefficient.**

### 🟠 Priority 3 — Last-Mile Delivery Execution (Secondary Signal)
848 orders (17%) were complete but delivered late. Carrier performance analysis reveals meaningful variation in on-time delivery rates across providers. Some carriers show low on-time rates despite not being responsible for the fulfillment gap. **Further analysis required to determine if late delivery is driven by route, region, or carrier-specific factors.**

---

## 3. Priority Actions (Hypothesis-Based — Require Validation Before Implementation)

| # | Action | Metric to Track | Risk |
|---|---|---|---|
| **1** | Build a weekly PO exception dashboard — flag open POs past expected date per supplier. Begin SLA discussion with bottom-2 OTD suppliers. | Supplier OTD %, avg lead time days | Supplier relationship risk; sample size per supplier may be small |
| **2** | Recalibrate reorder points for top-20 SKUs by Unserved Order Value using 95% service level target. Test on pilot warehouse before rollout. | Fill Rate %, Stockout Snapshot % | Carrying cost increase ~20% p.a. per additional safety stock unit |
| **3** | Conduct a carrier performance review: compare on-time %, freight cost per shipped order, and volume to identify renegotiation or reallocation opportunities. | On-Time %, Avg Freight per Order | Contract terms may limit short-term flexibility |

---

## 4. Measurement Framework (If Actions Are Implemented)

Success metrics should be compared to this baseline using equivalent time periods and controlled for SKU mix changes:
- Fill Rate: target ≥ 85% (from 74.15%)
- OTIF: target ≥ 60% (from 42.90%)
- Supplier OTD: target ≥ 70% (from 35.95%)
- Stockout Snapshot Share: target ≤ 8% (from 14.31%)

**Important:** Revenue impact estimates should not be derived directly from Unserved Order Value (Rp 1.01 B) without accounting for demand substitution, lost vs. deferred orders, and potential mix effects.

---

*All figures are recalculated from `analyze_scm.py` using the synthetic FMCG dataset. This memo is a portfolio demonstration artifact — not an operational business document.*

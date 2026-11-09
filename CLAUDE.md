# CLAUDE.md - SCM FMCG Data Analyst Portfolio Guide

## Project Summary
FMCG Supply Chain Management Analytics & Optimization project designed for Data Analyst recruitment standards.
Simulated multi-echelon network: 48 SKUs, 3 DCs, 8 Suppliers, 36 Customers, 4,925 Orders.
Investigates 31.25% gap between Unit Fill Rate (74.15%) and OTIF (42.90%).

## Key Ground Truth Numbers (Do Not Hallucinate Alternate Values)
- Total Orders: 4,925 | Total Lines: 8,534
- Requested Units: 98,069 | Fulfilled Units: 72,721
- Unit Fill Rate: 74.15% | In-Full Orders: 60.12% | On-Time Orders: 63.65% | OTIF Rate: 42.90%
- Revenue Fulfilled: Rp3,324,652,500 | COGS: Rp2,216,806,500 | Freight: Rp159,946,000
- Daily Stockout Rate: 14.31% (3,772 snapshot rows)
- Supplier OTD: 35.95% (Lowest: PT Niaga Mitra 2.65%, PT Karya Maju 3.74%, PT Surya Ritelindo 5.04%)
- Carrier On-Time: Mitra Trucking 48.88% vs Peers ~69%

## Core Stack & Rules
- **Power BI / PBIP:** Format PBIP (`.pbip` + TMDL). All TMDL files (`.tmdl`) MUST be saved in UTF-8 WITHOUT BOM. Power BI throws `Detected BOM: 'UTF-8'` if saved with BOM.
- **Relational Schema:** Star Schema only. 14 relationships, all `1:*`, single direction. Never connect fact-to-fact (`fact_shipments` <-> `fact_sales_order_lines`).
- **Python:** Python 3.10+ using standard libraries + pandas/numpy/matplotlib/seaborn. Keep tests green before committing.
- **SQLite:** Database at `SCM_Portfolio_Starter/02_Database/scm_portfolio.sqlite`.

## Standard Commands
- Run project tests: `python SCM_Portfolio_Starter/04_Python/test_project.py`
- Run forecast math tests: `python SCM_Portfolio_Starter/04_Python/test_forecast.py`
- Verify notebook execution: `python 04_Python_Notebooks/verify_cells.py`
- Re-generate SCM analysis summaries: `python SCM_Portfolio_Starter/04_Python/analyze_scm.py`
- Re-run replenishment scenarios: `python SCM_Portfolio_Starter/04_Python/replenishment_scenarios.py`

<!-- antislop:start -->
## antislop
For UI, copy, people, mobile layout, or code comments work, read these installed skill files directly (use these paths even if a same-named global skill exists):
- Core filter, always on: `antislop`: `.agents/skills/antislop/SKILL.md`
- UI / visual: `antislop-ui`: `.agents/skills/antislop-ui/SKILL.md`
- Copy & text: `antislop-copywriting`: `.agents/skills/antislop-copywriting/SKILL.md`
- People: `antislop-human`: `.agents/skills/antislop-human/SKILL.md`
- Mobile / responsive: `antislop-layoutmobile`: `.agents/skills/antislop-layoutmobile/SKILL.md`
- Code comments: `antislop-code`: `.agents/skills/antislop-code/SKILL.md`
<!-- antislop:end -->


# Pittsburgh Artificial Intelligence Investment Ecosystem – Technical Documentation

_Block Center for Technology & Society, Carnegie Mellon University_

**Principal Investigators**: Pablo Zavala · Liufei Chen  
**Release**: v2.0  (July 2025)

---

## 1 Project Purpose
This repository provides a reproducible, data-driven assessment of venture-backed artificial-intelligence companies headquartered in Pittsburgh (and peer regions).  The codebase ingests Crunchbase-derived datasets, rigorously cleans and enriches them, and outputs an interactive, publication-ready HTML report suitable for academic and policy analysis.

**Public scope.** The findings published in this repository cover the Pittsburgh metropolitan area only: **133 active AI firms and USD 6.3 B cumulative funding** (July 2025 snapshot), computed by the committed pipeline from Crunchbase-derived datasets.  In compliance with Crunchbase's Terms of Service, the raw exports are **not redistributed** in this repository (see Section 4); the committed HTML report is the pipeline's verbatim output.  Peer-region data supported the report's peer-city benchmarking section only; no aggregate findings beyond Pittsburgh are published here.

## 2 Repository Structure
| Path | Description |
|------|-------------|
| `comprehensive_pittsburgh_analysis.py` | Core ETL and metric-calculation engine (Pandas + NumPy). |
| `unified_pittsburgh_report.py` | Orchestrates visual analytics (Plotly + Folium) and compiles the single HTML deliverable. |
| `Companies-With-Address - Sheet1.csv`, `*.geojson` | Included geo files (hand-geocoded company points; county ZIP polygons).  Raw Crunchbase exports are excluded -- see Section 4. |
| `Pittsburgh_AI_Preliminary_Report.html` | Most recent build of the interactive report (open in any modern browser). |

## 3 Quick-start (local execution)
1. Create/activate a Python 3.10+ environment.
2. Install requirements:
```bash
pip install -r requirements.txt
```
3. Run the pipeline:
```bash
python - <<'PY'
from comprehensive_pittsburgh_analysis import run_comprehensive_analysis
from unified_pittsburgh_report import UnifiedPittsburghReport
an = run_comprehensive_analysis()
UnifiedPittsburghReport(an).generate_unified_report()
PY
```
The script regenerates `Pittsburgh_AI_Preliminary_Report.html` in the project root.

> **Note.** Re-running the pipeline end-to-end requires the five raw Crunchbase export files listed in Section 4, which are not redistributed here.  The committed `Pittsburgh_AI_Preliminary_Report.html` is the pipeline's verbatim output; the raw July-2025 snapshot is available on request to the authors for academic verification.

## 4 Data Inventory and Availability
| File | Rows | Key variables | Availability |
|------|------|---------------|--------------|
| `all-minus-austin-companies-7-18-2025.csv` | 1 324 | funding $, industry tags, HQ location, founding dates. | excluded -- Crunchbase license |
| `austin-companies-7-18-2025.csv` | 635 | peer-city company universe. | excluded -- Crunchbase license |
| `Companies-With-Address - Sheet1.csv` | 69 | point geocodes (lat/lon). | included |
| `funding_transactions_full.csv` | 5 564 | round-level amounts, dates, participant counts. | excluded -- Crunchbase license |
| `investor_profiles_unique (1).csv` | 5 633 | investor meta-data (location, stage focus). | excluded -- Crunchbase license |
| `pittsburgh-schools-7-23-2025.csv` | 68 | university descriptors (alumni, founders). | excluded -- Crunchbase license |
| `Allegheny_County_Zip_Code_Boundaries.geojson` | 110 polygons | ZIP polygons for choropleths. | included (public county GIS) |

**Source: Crunchbase (crunchbase.com), July 2025 snapshot.**  Raw exports are not redistributed in compliance with Crunchbase's Terms of Service; they are available on request to the authors for academic verification.  All processing runs locally; the pipeline makes no external API calls.

## 5 Analytical Pipeline (summary)
1. **Entity normalisation** – deduplicate organisations, coerce monetary strings to floats, harmonise ZIP-codes.
2. **Industry classification** – multi-label keyword matching; proportional funding weighting across eight macro-sectors.
3. **Metric derivation** – company age, funding velocity, innovation score, employment estimates, unicorn flag, etc.
4. **Network extraction** – explode `Top 5 Investors` strings, construct investor–company bipartite graph; compute portfolio statistics.
5. **Visual synthesis** – Plotly dashboards (industry, funding stages, investor performance, peer-city benchmarking) and Folium geospatial layers (choropleths, marker clusters, university overlay).

## 6 Key Findings (2025-07 snapshot)
• 133 active AI firms headquartered in Pittsburgh, USD 6.3 B cumulative funding.  
• Sectoral funding leadership: Autonomous Systems (38 %), Core AI/ML (34 %), Healthcare AI (7 %).  
• Median time-to-first funding: 2.4 years; median employee count: 18.  
• Investor landscape dominated by a small set of specialised funds; portfolio success-rate median = 66 %.  
• Zip-code level clustering around 15213 (CMU/Pitt) exhibiting > USD 2 B raised.

Full methodological notes appear in the generated report.

## 7 Reproducibility & Contribution
The codebase is modular and annotation-rich.  Researchers wishing to extend the study (e.g., additional peer regions, longitudinal updates) should fork the repo and observe the following guidelines:
1. Submit pull-requests with atomic commits and descriptive messages.  
2. Adhere to PEP-8 and maintain type consistency (use `mypy` stubs where practical).  
3. Update unit tests (`pytest`) if you alter core computation functions.  
4. Document new variables/datasets in this README.

For questions, contact **pzavalar@andrew.cmu.edu** or **liufeic@cmu.edu**.

---
© 2025 Carnegie Mellon University – Released for non-commercial research use. 

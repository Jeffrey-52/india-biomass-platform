# India Biomass Intelligence Platform (IBIP)

An open, learning-first project that turns India's crop-residue data into **energy
intelligence** — from official government tables to techno-economics, GIS and
(next) Life Cycle Assessment. It is the analytical engine behind a wider goal: a
**data-backed proposal for a hybrid renewable energy system for India**.

**Live demo:** **https://india-biomass-platform.vercel.app**

The whole thing is a single, dependency-free `index.html` fed by a small Python
data pipeline. No framework, no build step, no server.

---

## Current status

- ✅ Interactive biomass estimator (state × crop × collection efficiency)
- ✅ Interactive India choropleth map **with click-to-drill-into-districts**
- ✅ CHP sizing & techno-economics (plant size → feedstock, cost, LCOE)
- ✅ **Real government data** — DES *Area, Production & Yield* 2022-23, district-level
- ✅ Reproducible data pipeline (official file → clean `data.json` / `districts.json`)
- ✅ Live public site (auto-deploys from GitHub via Vercel)
- ✅ **Existing bio-power capacity by state + "opportunity" view** (MNRE, 31 Mar 2026)
- ✅ **Open-data downloads** + an About / method + sources page
- ✅ LCA module 1: crop residue burnt in the field vs used in a biomass power plant (kg CO2e per tonne, GWP100; sourced factors in the page footnote)
- 🔄 LCA module 2: biomass power vs the Indian grid per kWh — *next*
- ⬜ Hybrid renewable energy system proposal for India (career deliverable)
- ⬜ Natural-language query assistant

*Built and released in layers — each stage is usable on its own.*

---

## What the site shows

- **The gap** — why India's ~500 Mt/yr of crop residue is hard to count and largely burned.
- **A live estimator** — pick a state and crop, set a collection efficiency, and see recoverable
  biomass, energy content, equivalent power capacity, and homes powered. Runs entirely client-side.
- **An interactive choropleth map** — recoverable residue by state; **click a state to enlarge it
  into its districts**, each coloured by biomass with a per-district crop breakdown.
- **A CHP techno-economics panel** — choose a plant size and see the feedstock it needs, how much
  the state can supply, how many plants the surplus supports, indicative capex and LCOE.

- **Supply vs existing plants** &mdash; each state's recoverable residue next to its installed
  bio-power capacity, flagging where there's lots of surplus but few plants (the opportunity).
- **Open data** &mdash; download every dataset (JSON/CSV) to study or build on.

### The estimator formula

```
recoverable biomass = production × residue-to-product ratio × surplus factor × collection efficiency
```

**Production** is now **real 2022-23 government data** (DES, district-level, aggregated to state).
**Residue ratios / surplus / heating values** are sourced estimates from the National Biomass
Atlas — see [`SOURCES.md`](SOURCES.md) for full provenance and honest caveats.

---

## Data pipeline

```
Official DES 2022-23 export (.xls)        National Biomass Atlas ratios (data/raw/crops.csv)
                 |                                          |
   pipeline/adapt_gov_data.py  →  data/raw/production.csv   |
                 |                                          |
   pipeline/build_data.py       →  data.json  ←─────────────┘
   pipeline/build_districts.py  →  districts.json
                 |
            index.html (estimator · map + district drill-down · CHP)
```

Update the data by editing a CSV and rerunning a script — no code changes. Every build is
validated (bad rows fail loudly). The ~14 MB raw government file stays out of the repo
(see `.gitignore`); download it from DES to regenerate.

---

## Where this is going

The platform is the evidence base for a **hybrid renewable energy system design study for a
representative Indian region** — combining feedstock assessment (done), unused-land mapping,
biomass-plus-solar sizing, logistics, techno-economics and a transparent LCA, grounded in
published literature and official energy-demand data. Scoped deliberately to a defensible case,
with the method framed as India-applicable.

---

## Tech

Plain HTML, CSS and vanilla JavaScript for the site; Python + pandas for the pipeline.
No framework, no build step — trivial to host anywhere static.

Type: Fraunces (display) · Public Sans (body) · IBM Plex Mono (data).

## Run locally

```bash
python -m http.server 8000   # then open http://localhost:8000
# regenerate data (needs the DES .xls in the repo root):
pip install pandas
python3 pipeline/adapt_gov_data.py && python3 pipeline/build_data.py && python3 pipeline/build_districts.py
```

---

## Roadmap

| Phase | Focus | Status |
|------:|-------|:------:|
| 1 | Python fundamentals (pandas pipeline) | ✅ |
| 2 | Government data acquisition (DES APY 2022-23) | ✅ |
| 3 | Cleaning & validation pipeline | ✅ |
| 4 | Database | — *(not needed at this scale)* |
| 5 | Biomass estimation | ✅ |
| 6 | GIS mapping + district drill-down | ✅ |
| 7 | Techno-economic analysis (CHP) | ✅ |
| 8 | Life cycle assessment | 🔄 |
| 9 | Hybrid-system proposal + AI assistant | ⬜ |

---

## Author

Jeffrey Saju Mancheril — MSc Biomass Technology.
Built as a portfolio project spanning data engineering, GIS, techno-economics and LCA.

_Production figures are official DES 2022-23; residue ratios are sourced estimates. See SOURCES.md._

# Data sources & authenticity

The site's numbers come in two kinds: **crop production** (how much of each crop
a state grows) and **residue parameters** (how much residue that crop leaves and
how much is realistically collectable). This note records the sources for each.

## 1. Crop production (state × crop, Mt/year) — REAL, 2022-23

Production is now **official government data**, not indicative.

- **Source:** Directorate of Economics & Statistics (DES), Department of
  Agriculture & Farmers Welfare — the "Area, Production & Yield" (APY) report,
  **2022-23**, at district level. Portal: https://data.desagri.gov.in/website/crops-apy-report-web
  (also the DES APY report at https://aps.dac.gov.in/APY/Public_Report1.aspx).
- **How it's processed:** `pipeline/adapt_gov_data.py` reads the official export
  (`horizontal_crop_vertical_year_report.xls`, a district-level APY table),
  sums **Production** across every district and season for each of our 17 states
  and 11 crops, and writes `data/raw/production.csv` in million tonnes.
- **Unit handling:**
  - Most crops are reported in tonnes.
  - **Cotton** is reported in **bales**; converted at **1 bale = 170 kg** (the
    Indian standard) to tonnes of lint.
  - **Millets** = Bajra + Jowar + Ragi + Small millets (combined, matching the
    site's single "Millets" category).

**Authenticity: high — first-party government data.** Spot-checked against known
figures and they match: Punjab rice 13.75 Mt, Uttar Pradesh wheat 38.07 Mt,
Uttar Pradesh sugarcane 239.4 Mt, Maharashtra cotton 1.46 Mt lint.

**Important caveat (documented, not a defect):** DES compiles state/district
figures separately from its national production *estimates*, and the two do not
reconcile — the sum of state figures can run above the all-India headline (e.g.
summing states gives ~155 Mt rice vs the ~136 Mt national estimate). So the
per-state values here are accurate official state figures, but their national
sum should not be read as the DES all-India total.

## 2. Residue parameters (RPR, surplus factor, heating value) — indicative, sourced

`data/raw/crops.csv` (residue-to-product ratio, surplus fraction, heating value)
is unchanged and still based on published estimates:

- **National Biomass Atlas of India** — Sardar Swaran Singh National Institute
  of Bio-Energy (SSS-NIBE) for MNRE: https://nibe.res.in/english/biomass-atlas.php
- MNRE biomass assessment (~750 Mt/yr total residue, ~230 Mt/yr surplus).

**Authenticity: medium-high, inherently variable.** Residue-to-product ratios
for the same crop range widely across studies (~0.42 to 3.96), so these remain
*sourced estimates with a citation*, not exact constants.

## Regenerating the data

1. Download the DES APY district export for the target year and save it as
   `horizontal_crop_vertical_year_report.xls` in the project root. (This raw
   file is ~14 MB and is **not** committed to the repo — download it from DES.)
2. `python3 pipeline/adapt_gov_data.py`   → rebuilds `data/raw/production.csv`
3. `python3 pipeline/build_data.py`        → rebuilds `data.json`
4. Commit `production.csv` + `data.json` and push; the live site updates.

## Known limitation

The choropleth map's per-state shading and hover totals are baked into the HTML
from the earlier indicative dataset, so they don't yet reflect these 2022-23
figures. The **estimator and CHP module do** (they read `data.json`). Refreshing
the map's static totals is a separate follow-up.

_Last reviewed: 2026-07-10._

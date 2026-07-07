# Data sources & authenticity

This project's numbers come in two kinds: **crop production** (how much of each
crop a state grows) and **residue parameters** (how much residue that crop
leaves, and how much is realistically collectable). This note records the
authoritative sources for each, how trustworthy they are, and how the current
figures compare — so the indicative seed data can be replaced with confidence.

## Status of the current figures

The numbers shipped in `data/raw/*.csv` today are **indicative** — round,
plausible values used to build and demonstrate the tool. They are **not** yet
sourced line-by-line from government tables. Replacing them is the point of the
pipeline: edit the CSVs, rerun `pipeline/build_data.py`, done.

## 1. Crop production (state × crop, Mt/year)

**Primary, authoritative source — use this.**

- **Agricultural Statistics at a Glance 2024** — Directorate of Economics &
  Statistics (DES), Department of Agriculture & Farmers Welfare, Government of
  India. State-wise area, production and yield for all major crops. This is the
  official record and the right source for the `production.csv` numbers.
  https://desagri.gov.in/  (publication PDF and the "Area, Production & Yield"
  report builder at https://data.desagri.gov.in/website/crops-apy-report-web)
- **UPAg portal** (Unified Portal for Agricultural Statistics),
  https://upag.gov.in — the government's newer live dashboard for the same APY
  data; good for pulling a clean per-state CSV.
- **PIB "Final estimates of production of major crops"** press releases — the
  headline national totals each year, useful as a sanity check.

Authenticity: **high.** These are first-party government statistics. Prefer the
"Final/4th Advance Estimates" for a given year over earlier advance estimates,
and always record which crop-year (e.g. 2022–23) a figure belongs to.

## 2. Residue parameters (RPR, surplus factor, heating value)

**Primary, authoritative source — use this.**

- **National Biomass Atlas of India** — Sardar Swaran Singh National Institute
  of Bio-Energy (SSS-NIBE) for MNRE. Gives state-wise and crop-wise **total and
  surplus** biomass availability, i.e. exactly the residue-to-product ratios and
  surplus (availability) factors this tool uses.
  https://nibe.res.in/english/biomass-atlas.php
- **MNRE biomass assessment**: total crop residue ≈ 750 Mt/yr, of which
  ≈ 230 Mt/yr is **surplus** (available for energy) — the basis for the site's
  "~500 Mt generated / ~140 Mt surplus" framing.

Supporting / cross-check (peer-reviewed, secondary):

- Crop residue potential assessments in *Biomass and Bioenergy* / *Science of
  the Total Environment* and CSE's "Agro-residue for power" report.

Authenticity: **medium-high, but inherently variable.** RPR is not a fixed
constant — published values for the same crop range widely (roughly **0.42 to
3.96**) because residue depends on variety, weather, soil and practice. So treat
RPR and surplus as *sourced estimates with a citation and a range*, not exact
truths. Always note which source and year each value came from.

## 3. Cross-check: indicative vs. real (illustrative)

A few 2022–23 official rice figures next to the site's current indicative ones,
to show the gap the pipeline is meant to close:

| State          | Site (indicative) | Official 2022–23 (DES) |
|----------------|------------------:|-----------------------:|
| Uttar Pradesh  | 15.5 Mt           | ~20.8 Mt               |
| Telangana      | 11.0 Mt           | ~17.5 Mt               |

The indicative numbers are in the right ballpark but run low against recent
actuals — expected, since production has grown. This is precisely why the data
belongs in editable CSVs rather than baked into code.

## How to replace the seed data with real numbers

1. Download the relevant table from Agricultural Statistics at a Glance / UPAg
   (production) and the National Biomass Atlas (RPR + surplus).
2. Edit `data/raw/production.csv` and `data/raw/crops.csv` — same columns.
3. Add a `year` and a `source` note to your commit message (and, later, we can
   add explicit source columns to the CSVs).
4. Run `python3 pipeline/build_data.py`. Validation will flag any bad rows.
5. Commit and push — the live site updates automatically.

_Last reviewed: 2026-07-07._

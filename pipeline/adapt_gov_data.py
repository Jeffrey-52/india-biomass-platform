#!/usr/bin/env python3
"""
IBIP data pipeline — Stage 0 (ingestion): official DES file -> production.csv
=============================================================================

Takes the government's district-level "Area, Production & Yield" export
(Directorate of Economics & Statistics, 2022-23) and turns it into the clean
data/raw/production.csv the rest of the pipeline expects.

What it does:
  * reads the DES .xls (which is really an HTML table),
  * for each of our 17 states and 11 crops, SUMS the Production (Tonnes)
    across all districts and all seasons,
  * converts tonnes -> million tonnes,
  * writes data/raw/production.csv (state, crop, production_mt_per_year).

Crop-name mapping (our name -> official column[s]):
  Cotton  -> "Cotton(lint)"   (official cotton is lint tonnes)
  Millets -> Bajra + Jowar + Ragi + Small millets  (combined millet group)
  Mustard -> "Rapeseed &Mustard";  Pigeonpea -> "Arhar/Tur";  Soybean -> "Soyabean"

Run:  python3 pipeline/adapt_gov_data.py
Then: python3 pipeline/build_data.py     (rebuilds data.json)
"""
import re, sys, csv, warnings
from pathlib import Path
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
GOV  = ROOT / "horizontal_crop_vertical_year_report.xls"
OUT  = ROOT / "data" / "raw" / "production.csv"

# our 17 states, in display order (kept stable for the map + dropdown)
STATES = ["Punjab","Haryana","Uttar Pradesh","Madhya Pradesh","Maharashtra",
          "West Bengal","Andhra Pradesh","Telangana","Bihar","Rajasthan",
          "Gujarat","Karnataka","Tamil Nadu","Odisha","Chhattisgarh","Assam","Kerala"]

# our crop -> official column name(s) to sum
CROP_MAP = {
    "Rice":["Rice"], "Wheat":["Wheat"], "Sugarcane":["Sugarcane"], "Maize":["Maize"],
    "Cotton":["Cotton(lint)"], "Groundnut":["Groundnut"],
    "Millets":["Bajra","Jowar","Ragi","Small millets"],
    "Soybean":["Soyabean"], "Mustard":["Rapeseed &Mustard"],
    "Barley":["Barley"], "Pigeonpea":["Arhar/Tur"],
}
# crop display order (matches crops.csv)
CROP_ORDER = ["Rice","Wheat","Sugarcane","Maize","Cotton","Groundnut","Millets",
              "Soybean","Mustard","Barley","Pigeonpea"]
INCLUDE_MIN_MT = 0.01   # skip trivially tiny (<10,000 t) state-crop entries

def main():
    if not GOV.exists():
        sys.exit("  missing official file: " + str(GOV))
    df = pd.read_html(GOV)[0]
    cols = df.columns
    scol = ('State','State','State')
    df[scol] = df[scol].map(lambda x: re.sub(r'^\d+\.\s*','',str(x)).strip())

    # index official production columns by crop-name.
    # Most crops report Production (Tonnes); cotton reports Production (Bales)
    # where 1 Indian cotton bale = 170 kg = 0.17 tonnes.
    BALE_T = 0.17
    prod_cols = {}   # crop -> list of (column, tonnes_factor)
    for c in cols:
        if not isinstance(c, tuple):
            continue
        if c[2] == 'Production (Tonnes)':
            prod_cols.setdefault(c[0], []).append((c, 1.0))
        elif c[2] == 'Production (Bales)':
            prod_cols.setdefault(c[0], []).append((c, BALE_T))

    rows, report = [], []
    for state in STATES:
        sub = df[df[scol].str.lower() == state.lower()]
        if sub.empty:
            report.append(f"  !! state not found in file: {state}")
            continue
        for crop in CROP_ORDER:
            tot_t = 0.0
            for gov_name in CROP_MAP[crop]:
                for c, factor in prod_cols.get(gov_name, []):
                    tot_t += pd.to_numeric(sub[c], errors='coerce').fillna(0).sum() * factor
            mt = tot_t / 1e6
            if mt >= INCLUDE_MIN_MT:
                rows.append((state, crop, round(mt, 3)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["state","crop","production_mt_per_year"])
        w.writerows(rows)

    print("  INGEST OK  -> " + str(OUT.relative_to(ROOT)))
    print(f"  {len(rows)} state-crop rows across {len(STATES)} states (2022-23, DES)")
    for line in report: print(line)

if __name__ == "__main__":
    main()


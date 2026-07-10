#!/usr/bin/env python3
"""
IBIP data pipeline — district drill-down: DES district file -> districts.json
=============================================================================

Reads the same official DES district export used for production, plus the
residue parameters in data/raw/crops.csv, and computes per-DISTRICT recoverable
biomass, energy, and the top crop. Output feeds the map's state -> districts
drill-down in index.html.

recoverable (Mt) = production (Mt) x rpr x surplus x COLLECTION
energy (PJ)      = recoverable (Mt) x lower-heating-value (MJ/kg)
(same formula the estimator uses.)

Run:  python3 pipeline/build_districts.py   (needs the DES .xls in the repo root)
"""
import re, sys, json, csv, warnings
from pathlib import Path
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
GOV  = ROOT / "horizontal_crop_vertical_year_report.xls"
CROPS= ROOT / "data" / "raw" / "crops.csv"
OUT  = ROOT / "districts.json"
COLLECTION = 0.55   # same collection efficiency the map uses

STATES = ["Punjab","Haryana","Uttar Pradesh","Madhya Pradesh","Maharashtra",
          "West Bengal","Andhra Pradesh","Telangana","Bihar","Rajasthan",
          "Gujarat","Karnataka","Tamil Nadu","Odisha","Chhattisgarh","Assam","Kerala"]
CROP_MAP = {
    "Rice":["Rice"], "Wheat":["Wheat"], "Sugarcane":["Sugarcane"], "Maize":["Maize"],
    "Cotton":["Cotton(lint)"], "Groundnut":["Groundnut"],
    "Millets":["Bajra","Jowar","Ragi","Small millets"],
    "Soybean":["Soyabean"], "Mustard":["Rapeseed &Mustard"],
    "Barley":["Barley"], "Pigeonpea":["Arhar/Tur"],
}
BALE_T = 0.17

def main():
    if not GOV.exists():
        sys.exit("  missing official file: " + str(GOV))
    # residue params
    cp = {}
    for r in csv.DictReader(open(CROPS)):
        cp[r["crop"]] = (float(r["rpr"]), float(r["surplus"]), float(r["lhv_mj_per_kg"]))

    df = pd.read_html(GOV)[0]
    cols = df.columns
    scol, dcol = ('State','State','State'), ('District','District','District')
    clean = lambda x: re.sub(r'^\d+\.\s*','',str(x)).strip()
    df['state_clean'] = df[scol].map(clean)

    # production columns per official crop name, with tonnes factor (cotton=bales)
    pcols = {}
    for c in cols:
        if not isinstance(c, tuple): continue
        if c[2] == 'Production (Tonnes)': pcols.setdefault(c[0], []).append((c, 1.0))
        elif c[2] == 'Production (Bales)': pcols.setdefault(c[0], []).append((c, BALE_T))

    out = {"collection": COLLECTION, "generated": str(pd.Timestamp.today().date()),
           "source": "DES APY 2022-23 (district)", "states": {}}

    for state in STATES:
        sub = df[df['state_clean'] == state]
        districts = []
        for _, row in sub.iterrows():
            dname = clean(row[dcol])
            crop_rec = {}
            for our, gov_names in CROP_MAP.items():
                if our not in cp: continue
                rpr, surplus, lhv = cp[our]
                t = 0.0
                for g in gov_names:
                    for c, f in pcols.get(g, []):
                        v = row[c]
                        if isinstance(v, pd.Series):      # duplicate column labels
                            v = pd.to_numeric(v, errors='coerce').fillna(0).sum()
                        else:
                            v = pd.to_numeric(v, errors='coerce')
                            v = 0 if pd.isna(v) else v
                        t += float(v) * f
                mt = t / 1e6
                rec = mt * rpr * surplus * COLLECTION
                if rec > 0:
                    crop_rec[our] = round(rec, 4)
            if not crop_rec:
                continue
            total_rec = round(sum(crop_rec.values()), 4)
            energy = round(sum(crop_rec[c] * cp[c][2] for c in crop_rec), 2)  # PJ
            top = max(crop_rec, key=crop_rec.get)
            crops_sorted = [[c, float(v)] for c,v in sorted(crop_rec.items(), key=lambda kv: -kv[1])[:5]]
            districts.append({"name": dname, "rec": total_rec, "energy": energy,
                              "top": top, "crops": crops_sorted})
        districts.sort(key=lambda d: -d["rec"])
        out["states"][state] = {
            "total_rec": round(sum(d["rec"] for d in districts), 3),
            "n": len(districts),
            "districts": districts,
        }

    OUT.write_text(json.dumps(out, ensure_ascii=False) + "\n", encoding="utf-8")
    tot = sum(v["n"] for v in out["states"].values())
    print("  DISTRICTS OK -> districts.json")
    print(f"  {tot} districts across {len(STATES)} states, at {int(COLLECTION*100)}% collection")

if __name__ == "__main__":
    main()


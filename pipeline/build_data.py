#!/usr/bin/env python3
"""
IBIP data pipeline — Stage 1: CSV  ->  data.json
=================================================

WHAT THIS DOES
--------------
Reads two human-editable CSV files in data/raw/ and turns them into a single
data.json that the website (index.html) loads at runtime. Nothing about the
website's maths changes — we are just moving the numbers OUT of the HTML and
INTO data files, so that updating the data no longer means editing code.

    data/raw/crops.csv        residue parameters, one row per crop
    data/raw/production.csv   production in Mt/year, one row per state+crop
                |
                |   (this script: read -> validate -> assemble)
                v
    data.json                 what the browser fetches

WHY A PIPELINE (and not just editing the HTML)?
    * The data has one home. Swap in real government numbers by editing a CSV.
    * Every build is validated, so a typo (a negative number, or a crop in
      production.csv that isn't defined in crops.csv) is caught here, loudly,
      instead of silently breaking the site.
    * This is the seam where real government CSVs will plug in later — same
      schema, same validation, same output.

HOW TO RUN
    python3 pipeline/build_data.py
    (run from the repo root; it writes data.json next to index.html)

Requires: pandas   ->   pip install pandas
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

# --- paths -----------------------------------------------------------------
# Repo root is the parent of the folder this script lives in (pipeline/).
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data.json"

# --- physical / modelling constants ---------------------------------------
# These match the constants currently in index.html. Keeping them here means
# the site and the pipeline can never drift apart.
CONSTANTS = {
    "elec_eff": 0.30,   # biomass-to-power conversion efficiency
    "hours": 7000,      # effective operating hours per year
    "home_kwh": 1000,   # indicative Indian household kWh per year
}

# Sanity bounds. Anything outside these is almost certainly a typo, so we stop
# the build and say exactly which row is wrong.
BOUNDS = {
    "rpr": (0.1, 5.0),                       # residue-to-product ratio
    "surplus": (0.0, 1.0),                   # available fraction (0..1)
    "lhv_mj_per_kg": (5.0, 25.0),            # lower heating value, MJ/kg
    "production_mt_per_year": (0.0, 500.0),  # Mt/year
}


def fail(message):
    """Print a clear error and stop. A pipeline should fail loudly, not quietly."""
    print("\n  BUILD FAILED\n  -> " + message + "\n", file=sys.stderr)
    sys.exit(1)


def load_crops():
    """Read crops.csv and check each residue parameter is present and sane."""
    path = RAW / "crops.csv"
    if not path.exists():
        fail("missing file: " + str(path))
    df = pd.read_csv(path)

    required = {"crop", "rpr", "surplus", "lhv_mj_per_kg", "residue_type"}
    missing = required - set(df.columns)
    if missing:
        fail("crops.csv is missing column(s): " + str(sorted(missing)))

    if df["crop"].duplicated().any():
        dupes = df.loc[df["crop"].duplicated(), "crop"].tolist()
        fail("crops.csv has duplicate crop(s): " + str(dupes))

    for col in ("rpr", "surplus", "lhv_mj_per_kg"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            bad = df.loc[df[col].isna(), "crop"].tolist()
            fail("crops.csv column '" + col + "' has non-numeric values for: " + str(bad))
        lo, hi = BOUNDS[col]
        out = df[(df[col] < lo) | (df[col] > hi)]
        if not out.empty:
            fail("crops.csv column '" + col + "' out of range "
                 + str(lo) + ".." + str(hi) + " for: " + str(out["crop"].tolist()))
    return df


def load_production(valid_crops):
    """Read production.csv and check every crop is one we have parameters for."""
    path = RAW / "production.csv"
    if not path.exists():
        fail("missing file: " + str(path))
    df = pd.read_csv(path)

    required = {"state", "crop", "production_mt_per_year"}
    missing = required - set(df.columns)
    if missing:
        fail("production.csv is missing column(s): " + str(sorted(missing)))

    col = "production_mt_per_year"
    df[col] = pd.to_numeric(df[col], errors="coerce")
    if df[col].isna().any():
        bad = df.loc[df[col].isna(), ["state", "crop"]].values.tolist()
        fail("production.csv has non-numeric production for: " + str(bad))
    lo, hi = BOUNDS[col]
    out = df[(df[col] < lo) | (df[col] > hi)]
    if not out.empty:
        rows = out[["state", "crop", col]].values.tolist()
        fail("production.csv value out of range " + str(lo) + ".." + str(hi) + ": " + str(rows))

    # Referential integrity: a crop grown in a state must exist in crops.csv,
    # otherwise the site would read residue parameters that don't exist.
    unknown = set(df["crop"]) - valid_crops
    if unknown:
        fail("production.csv references crop(s) not defined in crops.csv: " + str(sorted(unknown)))

    if df.duplicated(subset=["state", "crop"]).any():
        d = df[df.duplicated(subset=["state", "crop"], keep=False)]
        fail("production.csv has duplicate state+crop rows:\n" + str(d))
    return df


def build():
    """Assemble the validated CSVs into the JSON shape the website expects."""
    crops_df = load_crops()
    valid_crops = set(crops_df["crop"])
    prod_df = load_production(valid_crops)

    # crops: { "Rice": {rpr, surplus, lhv, residue}, ... }
    # JSON keys (lhv, residue) match what index.html already reads.
    crops = {}
    for row in crops_df.itertuples(index=False):
        crops[row.crop] = {
            "rpr": round(float(row.rpr), 4),
            "surplus": round(float(row.surplus), 4),
            "lhv": round(float(row.lhv_mj_per_kg), 4),
            "residue": row.residue_type,
        }

    # production: { "Punjab": {"Rice": 13.0, ...}, ... }, CSV order preserved.
    production = {}
    for row in prod_df.itertuples(index=False):
        production.setdefault(row.state, {})[row.crop] = round(float(row.production_mt_per_year), 4)

    return {
        "meta": {
            "generated": date.today().isoformat(),
            "source": "Production: DES Area-Production-Yield 2022-23 (district data "
                      "aggregated to state). Residue ratios: National Biomass Atlas. "
                      "See SOURCES.md.",
            "production_year": "2022-23",
            "n_states": len(production),
            "n_crops": len(crops),
            "schema_version": 1,
        },
        "constants": CONSTANTS,
        "crops": crops,
        "production": production,
    }


def main():
    data = build()
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    m = data["meta"]
    rows = sum(len(v) for v in data["production"].values())
    print("  BUILD OK")
    print("  -> " + str(OUT.relative_to(ROOT)))
    print("  -> " + str(m["n_crops"]) + " crops, " + str(m["n_states"]) + " states, " + str(rows) + " production rows")


if __name__ == "__main__":
    main()

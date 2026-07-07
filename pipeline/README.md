# IBIP data pipeline

Turns the editable CSVs in `../data/raw/` into `../data.json`, which the website
loads at runtime.

```
data/raw/crops.csv        residue parameters, one row per crop
data/raw/production.csv   production (Mt/year), one row per state + crop
        |
        |  python3 pipeline/build_data.py   (reads, validates, assembles)
        v
data.json                 fetched by index.html
```

## Run it

```bash
pip install pandas          # one-time
python3 pipeline/build_data.py   # run from the repo root
```

A successful run prints `BUILD OK`. If a value is wrong (non-numeric, out of
range, a crop that isn't defined, a duplicate row) the build **stops** and tells
you exactly which row — so a bad edit can't silently reach the site.

## The CSV schema

`crops.csv`

| column          | meaning                                  |
|-----------------|------------------------------------------|
| crop            | crop name (must match production.csv)    |
| rpr             | residue-to-product ratio                 |
| surplus         | fraction of residue available (0–1)      |
| lhv_mj_per_kg   | lower heating value, MJ/kg               |
| residue_type    | short description (e.g. "straw & husk")  |

`production.csv`

| column                  | meaning                          |
|-------------------------|----------------------------------|
| state                   | state name                       |
| crop                    | crop name (must exist in crops)  |
| production_mt_per_year  | production, million tonnes/year  |

## Where real data comes from

See `../SOURCES.md` for authoritative government sources (Agricultural
Statistics at a Glance for production; National Biomass Atlas for residue
ratios) and an authenticity assessment.


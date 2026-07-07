# India Biomass Intelligence Platform (IBIP)

An open, learning-first project that turns India's fragmented crop-residue data into
**energy intelligence** — from government tables all the way to Life Cycle Assessment.

This repository currently holds the **project's public landing page**: a single, dependency-free
`index.html` with a live, in-browser biomass estimator. It is designed to grow alongside the
data-engineering pipeline described below.

**Live demo:** **https://india-biomass-platform.vercel.app**

---

## Current status

- ✅ Interactive biomass estimator (state × crop × collection efficiency)
- ✅ Interactive India choropleth map (recoverable residue by state)
- ✅ Live public landing page
- 🔄 Government data pipeline (real CSVs → clean `data.json`)
- ⬜ CHP sizing & techno-economics
- ⬜ Life Cycle Assessment (LCA) module
- ⬜ Natural-language query assistant
- ⬜ Full dashboard

*This is a learning-first project, built and released in layers. Each stage is usable on its own.*

---

## What the site shows

- **The gap** — why India's ~500 Mt/yr of crop residue is currently hard to count.
- **A live estimator** — pick a state and crop, set a collection efficiency, and see recoverable
  biomass, energy content, equivalent power capacity, and homes powered. Runs entirely client-side.
- **An interactive choropleth map** — recoverable residue by state, rendered from open India
  district geometry (dissolved to states with Shapely). Hover to read a state; click to load it
  into the estimator. Covers 17 states across 11 crops.
- **The pipeline** — the eight-stage architecture from government data to an AI assistant.
- **The roadmap** — the nine build phases, learning-first.

### The estimator formula

```
available biomass = production × residue-to-product ratio × surplus factor × collection efficiency
```

All input figures are **indicative**, drawn from public agricultural statistics and biomass-atlas
residue ratios. The production platform will pull exact numbers from source government datasets.

---

## Tech

Plain HTML, CSS and vanilla JavaScript — no build step, no framework, no dependencies.
That makes it trivial to host anywhere static (Vercel, GitHub Pages, Netlify).

Type: Fraunces (display) · Public Sans (body) · IBM Plex Mono (data).

---

## Run locally

Just open `index.html` in a browser. Or serve it:

```bash
python -m http.server 8000
# then visit http://localhost:8000
```

---

## Roadmap (the wider platform)

| Phase | Focus | Tools | Status |
|------:|-------|-------|:------:|
| 1 | Python fundamentals | python, pandas | 🔄 |
| 2 | Government data acquisition | requests, beautifulsoup4 | 🔄 |
| 3 | Cleaning pipeline | pandas | ⬜ |
| 4 | Database | SQLite | ⬜ |
| 5 | Biomass estimation | python | ✅ *(in-browser)* |
| 6 | GIS mapping | QGIS | ✅ *(in-browser)* |
| 7 | Techno-economic analysis | python | ⬜ |
| 8 | Life cycle assessment | OpenLCA | ⬜ |
| 9 | AI assistant | LLM | ⬜ |

---

## Author

Jeffrey Saju Mancheril — MSc Biomass Technology.
Built as a portfolio project spanning data engineering, GIS, techno-economics and LCA.

_Figures are indicative and for demonstration only._

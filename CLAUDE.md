# TSR Products Visualizer — Claude Instructions

## Project Overview
A single-page web application for browsing TSR (Tactical Studies Rules) product cover art,
spanning publications from 1974 onward (D&D, AD&D, and related products).

## Architecture
- **index.html** — Self-contained SPA: all HTML, CSS, and JavaScript in one file (no build step)
- **products.json** — Product data consumed by the viewer at runtime via `fetch()`
- **convert_csv.py** — Python 3 script that regenerates `products.json` from the CSV source
- **../tsr_products/tsr_products.csv** — Master source data (30+ columns of bibliographic info)

## Tech Stack
- Vanilla HTML5 / CSS3 / JavaScript (no frameworks, no bundler)
- Google Fonts: Cinzel (serif headings)
- Python 3 (data pipeline only)

## Key Conventions
- All app logic lives in `index.html`; keep it self-contained
- `products.json` is generated — never hand-edit it; run `convert_csv.py` instead
- Dark theme: background `#1a1a2e`, accent `#c9a227`, text `#e8e8e8`
- Responsive breakpoint at 900px (3-column → 1-column layout)

## Data Pipeline
To regenerate `products.json` after editing the CSV:
```bash
python convert_csv.py
```
Input: `../tsr_products/tsr_products.csv`
Output: `products.json`

**IMPORTANT:** Before running `convert_csv.py` (or generating a new JSON), always ask the user:
"What is the MAX_YEAR to use?" — then update `MAX_YEAR` in `convert_csv.py` accordingly before running.

## Running Locally
Open `index.html` via a local server (required — `fetch()` won't work over `file://`):
```bash
python -m http.server 8000
# then open http://localhost:8000
```

## GitHub
https://github.com/balard/tsr_products_visualizer

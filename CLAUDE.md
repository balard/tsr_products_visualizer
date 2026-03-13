# TSR Products Visualizer — Claude Instructions

## Project Overview
A single-page web application for browsing TSR (Tactical Studies Rules) product cover art,
spanning publications from 1974 onward (D&D, AD&D, and related products).

## Architecture
- **index.html** — Self-contained SPA: all HTML, CSS, and JavaScript in one file (no build step)
- **debug.html** — Self-contained developer tool: shows all 18 fields per product in a 7-product context window (±3 around current); same dark theme; keyboard nav (←/→/Home/End)
- **products.json** — Product data consumed by the viewer at runtime via `fetch()`
- **convert_csv.py** — Python 3 script that regenerates `products.json` from the CSV source
- **download_covers.py** — Downloads cover images by year into `covers/full/`
- **covers/full/** — Local image files named `{id}.jpg` (or `.gif`); served via GitHub Pages
- **../tsr_products/tsr_products.csv** — Master source data (30+ columns of bibliographic info)

## Tech Stack
- Vanilla HTML5 / CSS3 / JavaScript (no frameworks, no bundler)
- Google Fonts: Cinzel (serif headings)
- Python 3 (data pipeline only)

## Key Conventions
- All app logic lives in `index.html`; keep it self-contained
- `products.json` is generated — never hand-edit it; run `convert_csv.py` instead
- `products.json` entries include all 18 CSV fields; CSV columns with spaces are normalized to underscores (`product_code`, `module_code`); `cover_url` points to a local path (`covers/full/{id}.jpg`) if the image has been downloaded, otherwise the remote URL from the CSV
- Dark theme: background `#1a1a2e`, accent `#c9a227`, text `#e8e8e8`
- Responsive breakpoint at 900px (3-column → 1-column layout)

## Data Pipeline
To regenerate `products.json` after editing the CSV:
```bash
python convert_csv.py
```
Input: `../tsr_products/tsr_products.csv`
Output: `products.json`

`MAX_YEAR` in `convert_csv.py` is fixed at **2013** — do not change it.

### Image Download Pipeline
To download covers for a specific year (run *before* regenerating JSON):
```bash
python download_covers.py <year>
```
Output: `covers/full/{id}.{ext}` — files are named by the product's CSV `id` field.
- Already-downloaded files are skipped automatically (idempotent).
- If `cover_url` in `products.json` is already a local path, the script skips it.

**Workflow when adding a new year of images:**
1. `python download_covers.py <year>`
2. `python convert_csv.py` ← regenerate JSON; local paths are picked up automatically

## convert_csv.py internals
- Exports 18 fields per product (id, order, year, month, day, product_code, title, module_code, type, system, setting, confidence, edition, authors, cover_url, cover_artist, semester, season)
- CSV columns with spaces (`product code`, `module code`) are normalized to underscores
- `cover_artist` normalization: strips `LIKELY:` prefix; converts `N/A` or empty to `null`
- The remote `SOURCE_URL` (GitHub raw) currently returns 404 — the script always falls back to the local CSV. This is expected, not a bug.

## Image Download Progress
Years fully downloaded to `covers/full/` (run `download_covers.py` then regenerate JSON):
- 1974 ✓, 1975 ✓, 1976 ✓, 1977 ✓, 1978 ✓, 1979 ✓, 1980 ✓, 1981 ✓ (id=57 timed out — retry pending), 1982 ✓, 1983 ✓, 1984 ✓
- Next year to download: **1985**

## Running Locally
Open `index.html` via a local server (required — `fetch()` won't work over `file://`):
```bash
python -m http.server 8000
# then open http://localhost:8000
```

## GitHub
https://github.com/balard/tsr_products_visualizer

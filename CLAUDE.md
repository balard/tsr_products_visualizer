# TSR Products Visualizer — Claude Instructions

## Project Overview
A single-page web application for browsing TSR (Tactical Studies Rules) product cover art,
spanning publications from 1974 onward (D&D, AD&D, and related products).

## Architecture
- **index.html** — Self-contained SPA: all HTML, CSS, and JavaScript in one file (no build step)
- **spread.html** — Self-contained spread viewer: shows front + back covers side by side for a single product; toolbar with Back, Random, and collapsible Details; navigates all products; syncs position with `index.html` via localStorage and `#id=` hash; designed for wide/desktop displays
- **debug.html** — Self-contained developer tool: shows all 23 fields per product in a 7-product context window (±3 around current); same dark theme; keyboard nav (←/→/Home/End)
- **products.json** — Product data consumed by the viewer at runtime via `fetch()`
- **convert_csv.py** — Python 3 script that regenerates `products.json` from the CSV source
- **download_covers.py** — Downloads cover images by year into `covers/full/`
- **covers/full/** — Local image files: front covers named `{id}.{ext}`, back covers named `{id}-back.{ext}`; served via GitHub Pages
- **../tsr_products/tsr_products.csv** — Master product table (18 cols: id through semester; no cover_url)
- **../tsr_products/covers.csv** — Cover URLs (3 cols: id, cover_url, backcover_url)
- **../tsr_products/blurbs.csv** — Product blurb text (2 cols: id, blurb; QUOTE_ALL)
- **../tsr_products/dtrpg.csv** — DriveThruRPG links (3 cols: id, dtrpg_url, dtrpg_title)

## Tech Stack
- Vanilla HTML5 / CSS3 / JavaScript (no frameworks, no bundler)
- Google Fonts: Cinzel (serif headings)
- Python 3 (data pipeline only)

## Key Conventions
- All app logic lives in `index.html`; keep it self-contained (`spread.html` is a separate self-contained page)
- `products.json` is generated — never hand-edit it; run `convert_csv.py` instead
- `products.json` entries include 23 fields; CSV columns with spaces are normalized to underscores (`product_code`, `module_code`); `cover_url` points to a local path (`covers/full/{id}.jpg`) if the image has been downloaded, otherwise the remote URL from covers.csv
- Dark theme: background `#1a1a2e`, accent `#c9a227`, text `#e8e8e8`
- Responsive breakpoint at 900px (3-column → 1-column layout)

## Data Pipeline
To regenerate `products.json` after editing the CSV:
```bash
python convert_csv.py
```
Inputs: `../tsr_products/tsr_products.csv`, `../tsr_products/covers.csv`,
        `../tsr_products/blurbs.csv`, `../tsr_products/dtrpg.csv`
Output: `products.json`

`MAX_YEAR` in `convert_csv.py` is fixed at **2013** — do not change it.

### Image Download Pipeline
To download covers for a specific year (run *before* regenerating JSON):
```bash
python download_covers.py <year>
```
Output:
- `covers/full/{id}.{ext}` — front cover, named by the product's CSV `id` field
- `covers/full/{id}-back.{ext}` — back cover (URL read from `covers.csv` `backcover_url` column)

- Already-downloaded files are skipped automatically (idempotent).
- The script reads `../tsr_products/covers.csv` directly to get `backcover_url` for each product.
- 404s on back covers are expected — not all products have back cover images on tsrarchive.com.

**Workflow when adding a new year of images:**
1. `python download_covers.py <year>`
2. `python convert_csv.py` ← regenerate JSON; local paths are picked up automatically

## download_covers.py internals
- Reads `products.json` to filter products by year
- Reads `../tsr_products/covers.csv` to get `backcover_url` for each product directly (no URL derivation needed)
- Both front and back downloads are idempotent — existing files are skipped

## convert_csv.py internals
- Joins 4 CSV files on `id`: tsr_products.csv (main), covers.csv, blurbs.csv, dtrpg.csv
- Exports 23 fields per product: id, order, year, month, day, product_code, title, module_code, type, system, setting, confidence, edition, authors, pages, isbn, cover_url, cover_artist, semester, backcover_url, blurb, dtrpg_url, dtrpg_title
- CSV columns with spaces (`product code`, `module code`) are normalized to underscores
- `cover_artist` normalization: strips `LIKELY:` prefix; converts `N/A` or empty to `null`
- `season` field removed (no longer in source data)
- Always reads local CSV files directly (no remote URL fallback)

## Image Download Progress
Years fully downloaded to `covers/full/` (run `download_covers.py` then regenerate JSON):
- Front covers: 1974 ✓, 1975 ✓, 1976 ✓, 1977 ✓, 1978 ✓, 1979 ✓, 1980 ✓, 1981 ✓, 1982 ✓, 1983 ✓, 1984 ✓, 1985 ✓, 1986 ✓, 1987 ✓, 1988 ✓, 1989 ✓, 1990 ✓, 1991 ✓, 1992 ✓, 1993 ✓, 1994 ✓, 1995 ✓, 1996 ✓, 1997 ✓, 1998 ✓, 1999 ✓, 2013 ✓
- Back covers: 1974–1999 ✓, 2013 ✓ (id=420 [1992] back added manually)
- Years with no products (skip): 2000–2012
- All years complete — no further downloads needed

## Running Locally
Open `index.html` via a local server (required — `fetch()` won't work over `file://`):
```bash
python -m http.server 8000
# then open http://localhost:8000
```

## GitHub
https://github.com/balard/tsr_products_visualizer

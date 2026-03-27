# DnD Virtual Exhibit — Claude Instructions

## Project Overview
A single-page web application for browsing TSR (Tactical Studies Rules) product cover art,
spanning publications from 1974 onward (D&D, AD&D, and related products).

## Architecture
- **index.html** — Main SPA: HTML, CSS, and JavaScript in one file (no build step); links `common.css` and `utils.js`
- **search.html** — Search/filter page: pill toggles for type/system/setting, live text search across title/code/authors/artist/blurb, thumbnail grid; clicking a result opens `index.html#id=<N>`; links `common.css` and `utils.js`
- **spread.html** — Spread viewer: shows front + back covers side by side for a single product; toolbar with Back, Random, and collapsible Details; navigates all products; syncs position with `index.html` via localStorage and `#id=` hash; designed for wide/desktop displays; links `common.css` and `utils.js`
- **debug.html** — Developer tool: shows all 23 fields per product in a 7-product context window (±3 around current); same dark theme; keyboard nav (←/→/Home/End)
- **common.css** — Shared CSS: design tokens (CSS variables `--bg`, `--bg2`, `--card`, `--border`, `--accent`, `--text`, `--muted`) and error overlay styles; linked by all HTML pages
- **utils.js** — Shared JS: `FILTERS_KEY`, `MONTH_NAMES`, `TEXT_FIELDS`, `loadActiveFilters()`, `applyFiltersToProducts()`; loaded by index.html, search.html, spread.html
- **products.json** — Product data consumed by the viewer at runtime via `fetch()`
- **convert_csv.py** — Python 3 script that regenerates `products.json` from the CSV source
- **download_covers.py** — Downloads cover images by year into `covers/full/`
- **covers/full/** — Local image files: front covers named `{id}.{ext}`, back covers named `{id}-back.{ext}`; served via GitHub Pages
- **covers/thumb/** — 300px-wide JPEG thumbnails generated from `covers/full/`; used by `search.html` and `game.html`
- **generate_thumbs.py** — Python 3 script that generates `covers/thumb/` from `covers/full/` (requires Pillow)
- **../tsr_products/tsr_products.csv** — Master product table (18 cols: id through semester; no cover_url)
- **../tsr_products/covers.csv** — Cover URLs (3 cols: id, cover_url, backcover_url)
- **../tsr_products/blurbs.csv** — Product blurb text (2 cols: id, blurb; QUOTE_ALL)
- **../tsr_products/dtrpg.csv** — DriveThruRPG links (3 cols: id, dtrpg_url, dtrpg_title)

## Tech Stack
- Vanilla HTML5 / CSS3 / JavaScript (no frameworks, no bundler)
- Google Fonts: Cinzel (serif headings)
- Python 3 (data pipeline only)

## search.html internals
- Loads `products.json` via `fetch()` on init (same requirement: must run via local server)
- **Structured filters** — pill toggle buttons, multi-select, OR-logic within a category, AND-logic across categories:
  - **Type** (6 values): `adventure`, `accessory`, `boxed set`, `hardcover`, `Flip-book`, `boardgame`
  - **System** (5 values): `AD&D 2e`, `AD&D 1e`, `Basic D&D`, `OD&D`, `Dragon Quest`
  - **Setting** (17 values + null): Forgotten Realms, Greyhawk, Mystara, Ravenloft, Dragonlance, Planescape, Dark Sun, Birthright, Spelljammer, Al-Qadim, Lankhmar, Thunder Rift, Kara-Tur, Mystara (2E), Blackmoor, Conan, Celtic — plus `(no setting)` for products where `setting` is null
- **Text search** — live, debounced 200ms, case-insensitive, searches: `title`, `dtrpg_title`, `module_code`, `product_code`, `authors`, `cover_artist`, `blurb`
- Pill counts show total products per value (not filtered count) — they are built once on load
- Results render as a thumbnail grid (`aspect-ratio: 3/4`, lazy-loaded); clicking a card → `index.html#id=<N>`
- Filter state is saved to `localStorage` key `tsr_active_filters` (JSON) on every change and restored on load; a "Clear Filters" button removes it
- `index.html` and `spread.html` read `tsr_active_filters` on load and navigate only within the filtered product set; position is tracked by product id (`tsr_current_id`) rather than array index

## Key Conventions
- Page-specific logic stays in its own HTML file; shared filter logic lives in `utils.js`; shared styles in `common.css`
- `products.json` is generated — never hand-edit it; run `convert_csv.py` instead
- `products.json` entries include 23 fields; CSV columns with spaces are normalized to underscores (`product_code`, `module_code`); `cover_url` points to a local path (`covers/full/{id}.jpg`) if the image has been downloaded, otherwise the remote URL from covers.csv
- Dark theme colors are defined as CSS variables in `common.css` — edit them there, not in individual HTML files
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
3. `python generate_thumbs.py <start_id> <end_id>` ← generate thumbnails for the new products

## generate_thumbs.py internals
- Reads `covers/full/` (`.jpg`/`.jpeg`, case-insensitive) and writes 300px-wide JPEGs to `covers/thumb/`
- Maintains aspect ratio; JPEG quality 75; uses Pillow (`pip install Pillow`)
- Idempotent — existing files are skipped
- Optional ID range: `python generate_thumbs.py <start_id> <end_id>`
- `search.html` and `game.html` derive thumb URLs via `cover_url.replace('/full/', '/thumb/')`

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
https://github.com/balard/dnd_virtual_exhibit

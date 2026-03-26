# TSR Products Visualizer

A browser-based cover gallery for TSR (Tactical Studies Rules) products — the publisher
behind Dungeons & Dragons from 1974 through the late 1990s.

## Features

- **Cover viewer** (`index.html`) — navigate hundreds of product covers with keyboard (← →) or on-screen buttons; auto-advance slideshow; metadata panel; progress bar; position persistence via `localStorage`
- **Search & filter** (`search.html`) — pill toggles for type, system, and setting; live text search across title, module code, authors, artist, and blurb; thumbnail grid results
- **Spread viewer** (`spread.html`) — front and back covers side by side; collapsible details panel; syncs position with the main viewer
- **Mini-games** (`game.html`, `odd1out.html`) — Chrono Covers (sort covers into chronological order) and Odd One Out (spot the cover from a different year)
- **Filter persistence** — active filters carry across all pages via `localStorage`
- Responsive layout — works on desktop and mobile

## Quick Start

1. Clone the repo:
   ```bash
   git clone https://github.com/balard/tsr_products_visualizer.git
   cd tsr_products_visualizer
   ```

2. Serve locally (`fetch()` requires HTTP, not `file://`):
   ```bash
   python -m http.server 8000
   ```

3. Open [http://localhost:8000](http://localhost:8000) in your browser.

## Data Pipeline

Product data lives in `products.json`, generated from four CSV source files in the
sister folder `../tsr_products/`.

### Regenerate JSON only

```bash
python convert_csv.py
```

### Add a new year of cover images (full workflow)

```bash
python download_covers.py <year>   # download front + back covers to covers/full/
python convert_csv.py              # regenerate products.json (picks up local paths)
python generate_thumbs.py <start_id> <end_id>  # generate 300px thumbnails to covers/thumb/
```

Already-downloaded files are skipped at each step (all scripts are idempotent).

## Project Structure

```
tsr_products_visualizer/
├── index.html              # Cover viewer SPA
├── search.html             # Search and filter page
├── spread.html             # Side-by-side spread viewer
├── game.html               # Chrono Covers mini-game
├── odd1out.html            # Odd One Out mini-game
├── debug.html              # Developer tool (all fields, context window)
├── products.json           # Generated product data (do not hand-edit)
├── convert_csv.py          # CSV → JSON data pipeline
├── download_covers.py      # Downloads cover images by year to covers/full/
├── generate_thumbs.py      # Generates 300px thumbnails to covers/thumb/
├── covers/
│   ├── full/               # Full-size covers: {id}.jpg / {id}-back.jpg
│   └── thumb/              # 300px-wide JPEG thumbnails
├── ../tsr_products/
│   ├── tsr_products.csv    # Master product table (18 cols)
│   ├── covers.csv          # Cover URLs (front + back)
│   ├── blurbs.csv          # Product blurb text
│   └── dtrpg.csv           # DriveThruRPG links
├── CLAUDE.md               # AI assistant instructions
└── .gitignore
```

## License

Application code: MIT.
Product data sourced from public TSR archive records.

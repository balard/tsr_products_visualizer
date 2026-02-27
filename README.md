# TSR Products Visualizer

A browser-based cover gallery for TSR (Tactical Studies Rules) products — the publisher
behind Dungeons & Dragons from 1974 through the late 1990s.

## Features

- Navigate hundreds of product covers with keyboard (← →) or on-screen buttons
- Auto-advance slideshow with configurable intervals (1 s / 3 s / 5 s / 10 s)
- Metadata display: title, year, authors, cover artist
- Progress bar and position persistence via `localStorage`
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

Product data is stored in `products.json`, generated from the master CSV:

```bash
python convert_csv.py
```

Edit `TSR_products_corrected v4.4.csv` → run the script → commit the updated `products.json`.

## Project Structure

```
tsr_products_visualizer/
├── index.html                        # SPA — all UI, CSS, and JS
├── products.json                     # Generated product data (do not hand-edit)
├── convert_csv.py                    # CSV → JSON data pipeline
├── TSR_products_corrected v4.4.csv   # Master source data
├── CLAUDE.md                         # AI assistant instructions
└── .gitignore
```

## License

Application code: MIT.
Product data sourced from public TSR archive records.

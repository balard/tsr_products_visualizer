"""
download_covers.py — Download cover images for products of a given year.

Usage:
    python download_covers.py <year>

Example:
    python download_covers.py 1980

Images are saved to covers/full/{id}.{ext} (front) and covers/full/{id}-back.{ext}
(back), where the extension is preserved from the original cover_url.
Already-downloaded files are skipped. Back cover URLs are assumed to be the
front cover URL with -back inserted before the extension.
Requires products.json to be up-to-date (run convert_csv.py first).
"""

import csv as csv_module
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

PRODUCTS_FILE = 'products.json'
CSV_FALLBACK = '../tsr_products/tsr_products.csv'
OUTPUT_DIR = Path('covers/full')
DELAY_SECONDS = 0.5  # polite delay between requests


def get_extension(url):
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lower() if ext else '.jpg'


def back_url(url):
    """Insert -back before the file extension in a URL."""
    base, ext = os.path.splitext(url)
    return f'{base}-back{ext}'


def download_image(url, dest_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read()
    with open(dest_path, 'wb') as f:
        f.write(data)


def load_remote_urls():
    """Return {id: remote_cover_url} from the master CSV."""
    mapping = {}
    try:
        with open(CSV_FALLBACK, newline='', encoding='utf-8') as f:
            reader = csv_module.DictReader(f)
            for row in reader:
                rid = row.get('id', '').strip()
                url = row.get('cover_url', '').strip()
                if rid and url:
                    mapping[int(rid)] = url
    except OSError as e:
        print(f'Warning: could not load CSV for back-cover URLs: {e}')
    return mapping


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print('Usage: python download_covers.py <year>')
        print('Example: python download_covers.py 1980')
        sys.exit(1)

    year = int(sys.argv[1])

    with open(PRODUCTS_FILE, encoding='utf-8') as f:
        products = json.load(f)

    remote_urls = load_remote_urls()

    targets = [p for p in products if p.get('year') == year and p.get('cover_url') and p.get('id') is not None]

    if not targets:
        print(f'No products with images found for year {year}.')
        sys.exit(0)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f'Downloading {len(targets)} cover(s) for year {year} -> {OUTPUT_DIR}/')

    ok = 0
    skipped = 0
    failed = 0

    for i, product in enumerate(targets, 1):
        pid = product['id']
        url = product['cover_url']
        ext = get_extension(url)
        dest = OUTPUT_DIR / f'{pid}{ext}'

        prefix = f'[{i}/{len(targets)}]'

        # --- front cover ---
        if dest.exists() or not url.startswith('http'):
            print(f'{prefix} Skip id={pid} front (already exists)')
            skipped += 1
        else:
            try:
                print(f'{prefix} Downloading id={pid} front -> {dest}', end='', flush=True)
                download_image(url, dest)
                print(' OK')
                ok += 1
                time.sleep(DELAY_SECONDS)
            except (urllib.error.URLError, OSError) as e:
                print(f' FAILED: {e}')
                failed += 1

        # --- back cover ---
        remote_url = remote_urls.get(pid)
        if remote_url and remote_url.startswith('http'):
            back_ext = get_extension(remote_url)
            back_dest = OUTPUT_DIR / f'{pid}-back{back_ext}'
            if back_dest.exists():
                print(f'{prefix} Skip id={pid} back (already exists)')
                skipped += 1
            else:
                b_url = back_url(remote_url)
                try:
                    print(f'{prefix} Downloading id={pid} back -> {back_dest}', end='', flush=True)
                    download_image(b_url, back_dest)
                    print(' OK')
                    ok += 1
                    time.sleep(DELAY_SECONDS)
                except (urllib.error.URLError, OSError) as e:
                    print(f' FAILED (back): {e}')
                    failed += 1
        else:
            print(f'{prefix} Skip id={pid} back (no remote URL)')
            skipped += 1

    print(f'\nDone: {ok} downloaded, {skipped} skipped, {failed} failed.')


if __name__ == '__main__':
    main()

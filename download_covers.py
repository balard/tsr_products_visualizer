"""
download_covers.py — Download cover images for products of a given year.

Usage:
    python download_covers.py <year>

Example:
    python download_covers.py 1980

Images are saved to covers/full/{id}.{ext}, where the extension is
preserved from the original cover_url. Already-downloaded files are skipped.
Requires products.json to be up-to-date (run convert_csv.py first).
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

PRODUCTS_FILE = 'products.json'
OUTPUT_DIR = Path('covers/full')
DELAY_SECONDS = 0.5  # polite delay between requests


def get_extension(url):
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lower() if ext else '.jpg'


def download_image(url, dest_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read()
    with open(dest_path, 'wb') as f:
        f.write(data)


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print('Usage: python download_covers.py <year>')
        print('Example: python download_covers.py 1980')
        sys.exit(1)

    year = int(sys.argv[1])

    with open(PRODUCTS_FILE, encoding='utf-8') as f:
        products = json.load(f)

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

        if dest.exists() or not url.startswith('http'):
            print(f'{prefix} Skip id={pid} (already exists)')
            skipped += 1
            continue

        try:
            print(f'{prefix} Downloading id={pid} -> {dest}', end='', flush=True)
            download_image(url, dest)
            print(' OK')
            ok += 1
            time.sleep(DELAY_SECONDS)
        except (urllib.error.URLError, OSError) as e:
            print(f' FAILED: {e}')
            failed += 1

    print(f'\nDone: {ok} downloaded, {skipped} skipped, {failed} failed.')


if __name__ == '__main__':
    main()

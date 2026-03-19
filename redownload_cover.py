"""
redownload_cover.py — Force re-download of cover images for one or more product IDs.

Use this after correcting a product's cover_url in the CSV. It reads the remote
URL directly from the CSV (bypassing products.json), deletes any existing cover
files for each ID, downloads fresh front and back covers, then regenerates
products.json automatically.

Usage:
    python redownload_cover.py <id> [id2 id3 ...]

Examples:
    python redownload_cover.py 554
    python redownload_cover.py 554 420 516
"""

import csv as csv_module
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

CSV_FALLBACK = '../tsr_products/tsr_products.csv'
OUTPUT_DIR = Path('covers/full')
DELAY_SECONDS = 0.5


def get_extension(url):
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lower() if ext else '.jpg'


def back_url(url):
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
        print(f'Error: could not load CSV: {e}')
        sys.exit(1)
    return mapping


def delete_existing(pid):
    """Delete all cover files (any extension) for the given product id."""
    deleted = []
    for pattern in (f'{pid}.*', f'{pid}-back.*'):
        for f in OUTPUT_DIR.glob(pattern):
            f.unlink()
            deleted.append(f.name)
    for name in deleted:
        print(f'  Deleted {OUTPUT_DIR}/{name}')
    if not deleted:
        print(f'  No existing files for id={pid}')


def main():
    if len(sys.argv) < 2 or not all(a.isdigit() for a in sys.argv[1:]):
        print('Usage: python redownload_cover.py <id> [id2 id3 ...]')
        print('Example: python redownload_cover.py 554')
        sys.exit(1)

    ids = [int(a) for a in sys.argv[1:]]
    remote_urls = load_remote_urls()

    ok = 0
    failed = 0

    for pid in ids:
        print(f'\n--- id={pid} ---')
        url = remote_urls.get(pid)
        if not url:
            print(f'  ERROR: id={pid} not found in CSV')
            failed += 1
            continue
        if not url.startswith('http'):
            print(f'  ERROR: cover_url for id={pid} is not a remote URL: {url}')
            failed += 1
            continue

        delete_existing(pid)

        # Front cover
        ext = get_extension(url)
        dest = OUTPUT_DIR / f'{pid}{ext}'
        try:
            print(f'  Downloading front -> {dest}', end='', flush=True)
            download_image(url, dest)
            print(' OK')
            ok += 1
            time.sleep(DELAY_SECONDS)
        except (urllib.error.URLError, OSError) as e:
            print(f' FAILED: {e}')
            failed += 1

        # Back cover
        b_url = back_url(url)
        back_ext = get_extension(url)
        back_dest = OUTPUT_DIR / f'{pid}-back{back_ext}'
        try:
            print(f'  Downloading back  -> {back_dest}', end='', flush=True)
            download_image(b_url, back_dest)
            print(' OK')
            ok += 1
            time.sleep(DELAY_SECONDS)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f' 404 (no back cover)')
            else:
                print(f' FAILED: {e}')
                failed += 1
        except (urllib.error.URLError, OSError) as e:
            print(f' FAILED: {e}')
            failed += 1

    sys.stdout.flush()
    print(f'\nDownloads: {ok} OK, {failed} failed')
    print('\nRegenerating products.json...')
    result = subprocess.run([sys.executable, 'convert_csv.py'], capture_output=False)
    if result.returncode != 0:
        print('WARNING: convert_csv.py exited with an error.')


if __name__ == '__main__':
    main()

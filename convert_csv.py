import csv
import io
import json
import urllib.request
import urllib.error
from pathlib import Path

SOURCE_URL = 'https://raw.githubusercontent.com/balard/tsr_products/main/tsr_products.csv'
LOCAL_FALLBACK = '../tsr_products/tsr_products.csv'
OUTPUT_FILE = 'products.json'
MAX_YEAR = 1996  # Only export products up to and including this year
LOCAL_COVERS_DIR = Path('covers/full')


def load_csv_content():
    try:
        with urllib.request.urlopen(SOURCE_URL, timeout=10) as response:
            content = response.read().decode('utf-8')
        print(f'Loaded CSV from {SOURCE_URL}')
        return io.StringIO(content)
    except urllib.error.URLError as e:
        print(f'Online fetch failed ({e}), falling back to local file...')
        f = open(LOCAL_FALLBACK, newline='', encoding='utf-8')
        print(f'Loaded CSV from {LOCAL_FALLBACK}')
        return f


def str_or_none(val):
    v = val.strip()
    return v if v else None


def int_or_none(val):
    v = val.strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None


products = []
source = load_csv_content()
try:
    reader = csv.DictReader(source)
    for row in reader:
        cover_url = row['cover_url'].strip()
        if not cover_url:
            continue

        artist = row.get('cover_artist', '').strip()
        if artist.upper() == 'N/A' or not artist:
            artist = None
        elif artist.upper().startswith('LIKELY:'):
            artist = artist[len('LIKELY:'):].strip()

        authors = row.get('authors', '').strip() or None
        year_raw = row.get('year', '').strip()
        year = int(year_raw) if year_raw else None

        if year is None or year > MAX_YEAR:
            continue

        row_id = row.get('id', '').strip()
        local_path = None
        if row_id:
            for f in LOCAL_COVERS_DIR.glob(f'{row_id}.*'):
                local_path = f'covers/full/{f.name}'
                break
        products.append({
            'id':           int(row_id) if row_id else None,
            'order':        int_or_none(row.get('order', '')),
            'year':         year,
            'month':        int_or_none(row.get('month', '')),
            'day':          int_or_none(row.get('day', '')),
            'product_code': str_or_none(row.get('product code', '')),
            'title':        row['title'].strip(),
            'module_code':  str_or_none(row.get('module code', '')),
            'type':         str_or_none(row.get('type', '')),
            'system':       str_or_none(row.get('system', '')),
            'setting':      str_or_none(row.get('setting', '')),
            'confidence':   str_or_none(row.get('confidence', '')),
            'edition':      str_or_none(row.get('edition', '')),
            'authors':      authors,
            'cover_url':    local_path if local_path else cover_url,
            'cover_artist': artist,
            'semester':     int_or_none(row.get('semester', '')),
            'season':       str_or_none(row.get('season', '')),
        })
finally:
    source.close()

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f'Exported {len(products)} products to {OUTPUT_FILE}')

import csv
import io
import json
import urllib.request
import urllib.error

SOURCE_URL = 'https://raw.githubusercontent.com/balard/tsr_products/main/tsr_products.csv'
LOCAL_FALLBACK = '../tsr_products/tsr_products.csv'
OUTPUT_FILE = 'products.json'
MAX_YEAR = 1993  # Only export products up to and including this year


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

        products.append({
            'title': row['title'].strip(),
            'year': year,
            'authors': authors,
            'cover_url': cover_url,
            'cover_artist': artist,
        })
finally:
    source.close()

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f'Exported {len(products)} products to {OUTPUT_FILE}')

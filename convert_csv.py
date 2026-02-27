import csv
import json

INPUT_FILE = 'TSR_products_corrected v4.4.csv'
OUTPUT_FILE = 'products.json'

products = []
with open(INPUT_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
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
        year = row.get('year', '').strip()

        products.append({
            'title': row['title'].strip(),
            'year': int(year) if year else None,
            'authors': authors,
            'cover_url': cover_url,
            'cover_artist': artist,
        })

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f'Exported {len(products)} products to {OUTPUT_FILE}')

#!/usr/bin/env python3
"""
generate_thumbs.py — Generate 300px-wide JPEG thumbnails from covers/full/

Usage:
    python generate_thumbs.py               # process all images
    python generate_thumbs.py 100 200       # process only ids 100-200 (inclusive)
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is required. Install it with:  pip install Pillow")
    sys.exit(1)

SOURCE_DIR = Path("covers/full")
OUTPUT_DIR = Path("covers/thumb")
THUMB_WIDTH = 300
JPEG_QUALITY = 75


def extract_id(filename: str) -> int | None:
    """Extract numeric product id from filename like '123.jpg' or '123-back.jpg'."""
    m = re.match(r"^(\d+)(?:-back)?\.jpe?g$", filename.lower())
    return int(m.group(1)) if m else None


def main():
    parser = argparse.ArgumentParser(description="Generate thumbnails from covers/full/")
    parser.add_argument("start_id", nargs="?", type=int, help="Start of id range (inclusive)")
    parser.add_argument("end_id", nargs="?", type=int, help="End of id range (inclusive)")
    args = parser.parse_args()

    if (args.start_id is None) != (args.end_id is None):
        parser.error("Provide both start_id and end_id, or neither.")

    id_range = (args.start_id, args.end_id) if args.start_id is not None else None

    if not SOURCE_DIR.exists():
        print(f"Source directory not found: {SOURCE_DIR}")
        sys.exit(1)

    all_files = sorted(f for ext in ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG") for f in SOURCE_DIR.glob(ext))

    if id_range:
        start, end = id_range
        files = [f for f in all_files if (pid := extract_id(f.name)) is not None and start <= pid <= end]
        print(f"Processing ids {start}–{end}: {len(files)} files found")
    else:
        files = all_files
        print(f"Processing all images: {len(files)} files found")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0
    total = len(files)

    for i, src_path in enumerate(files, 1):
        dest_path = OUTPUT_DIR / src_path.name

        if dest_path.exists():
            print(f"  skip [{i}/{total}] {src_path.name} (exists)")
            skipped += 1
            continue

        with Image.open(src_path) as img:
            img.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 10), Image.LANCZOS)
            img = img.convert("RGB")
            img.save(dest_path, "JPEG", quality=JPEG_QUALITY, optimize=True)

        print(f"  [{i}/{total}] {src_path.name}")
        generated += 1

    print(f"\nDone: {generated} generated, {skipped} skipped.")


if __name__ == "__main__":
    main()

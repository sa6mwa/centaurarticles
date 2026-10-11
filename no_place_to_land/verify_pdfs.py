#!/usr/bin/env python3
"""Check that the distributable PDF preserves content and fits the upload limit."""

import argparse
from pathlib import Path

from pypdf import PdfReader


def uri_links(page):
    return sorted(
        str(annotation.get_object().get("/A", {}).get("/URI", ""))
        for annotation in page.get("/Annots", [])
    )


def verify(original, squeezed, max_bytes=20_000_000):
    size = Path(squeezed).stat().st_size
    if size >= max_bytes:
        raise ValueError(f"Squeezed PDF is {size:,} bytes; must be below {max_bytes:,}")
    full, small = PdfReader(original), PdfReader(squeezed)
    if len(full.pages) != len(small.pages):
        raise ValueError("Page counts differ")
    for number, (before, after) in enumerate(zip(full.pages, small.pages), 1):
        if before.mediabox != after.mediabox or before.cropbox != after.cropbox:
            raise ValueError(f"Page {number}: page dimensions differ")
        if before.extract_text() != after.extract_text():
            raise ValueError(f"Page {number}: text differs")
        if uri_links(before) != uri_links(after):
            raise ValueError(f"Page {number}: links differ")
        if len(before.images) != len(after.images):
            raise ValueError(f"Page {number}: image counts differ")
    print(f"Verified {len(full.pages)} pages: identical text, page sizes, links and image counts; "
          f"squeezed PDF {size / 1_000_000:.2f} MB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("squeezed", type=Path)
    args = parser.parse_args()
    try:
        verify(args.original, args.squeezed)
    except (ValueError, OSError) as error:
        parser.exit(1, f"PDF verification failed: {error}\n")


if __name__ == "__main__":
    main()

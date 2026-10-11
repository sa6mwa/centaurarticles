#!/usr/bin/env python3
"""Stage a LaTeX copy with PNGs sized for their actual PDF placements."""

import argparse
import hashlib
import math
from pathlib import Path
import shutil
import subprocess

from PIL import Image
from pypdf import PdfReader


def pixel_key(image):
    """Match source PNGs to decoded PDF images, including transparency."""
    return image.size, hashlib.sha256(image.convert("RGBA").tobytes()).digest()


def image_resolutions(pdf):
    """Return minimum placement DPI per image object (ignore alpha masks)."""
    result = subprocess.run(
        ["pdfimages", "-list", str(pdf)], check=True, capture_output=True, text=True
    )
    resolutions = {}
    for line in result.stdout.splitlines()[2:]:
        fields = line.split()
        if len(fields) < 16 or fields[2] != "image":
            continue
        # Poppler reports rounded integer DPI and PDF object/generation IDs.
        obj = int(fields[10]), int(fields[11])
        dpi = int(fields[12]), int(fields[13])
        if min(dpi) <= 0:
            raise ValueError(f"Invalid placement resolution for PDF object {obj}")
        previous = resolutions.get(obj, dpi)
        resolutions[obj] = tuple(min(a, b) for a, b in zip(previous, dpi))
    return resolutions


def resized_dimensions(size, resolution, target_dpi):
    if target_dpi <= 0 or min(resolution) <= 0:
        raise ValueError("Resolution must be positive")
    # Preserve aspect ratio and the largest placement; never upscale.
    # Account for half a DPI of rounding in Poppler's listing.
    scale = min(1.0, target_dpi / (min(resolution) - 0.5))
    return tuple(max(1, math.ceil(dimension * scale)) for dimension in size)


def stage_images(source_dir, pdf, output_dir, dpi):
    if dpi <= 0:
        raise ValueError("Target DPI must be positive")
    source_dir, pdf, output_dir = map(Path, (source_dir, pdf, output_dir))
    if output_dir.resolve() == source_dir.resolve():
        raise ValueError("The staged copy must be separate from the source directory")

    sources = {}
    for path in sorted(source_dir.glob("*.png")):
        with Image.open(path) as image:
            sources.setdefault(pixel_key(image), []).append(path)

    placements = image_resolutions(pdf)
    required = {}
    reader = PdfReader(pdf)
    seen = set()
    for page in reader.pages:
        for image in page.images:
            ref = image.indirect_reference
            if ref is None:
                raise ValueError("Inline PDF images cannot be matched to source PNGs")
            obj = ref.idnum, ref.generation
            if obj in seen:
                continue
            seen.add(obj)
            matches = sources.get(pixel_key(image.image))
            if not matches:
                raise ValueError(f"PDF image {obj} does not match a source PNG")
            resolution = placements[obj]
            for path in matches:
                previous = required.get(path, resolution)
                required[path] = tuple(min(a, b) for a, b in zip(previous, resolution))

    if not required:
        raise ValueError("No source PNGs were found in the PDF")

    output_dir.mkdir(parents=True, exist_ok=True)
    assets = source_dir / "assets"
    if assets.is_dir():
        shutil.copytree(assets, output_dir / "assets", dirs_exist_ok=True)
    # The stage is generated from the current sources; remove stale inputs.
    for pattern in ("*.tex", "*.bib", "*.png"):
        for old in output_dir.glob(pattern):
            if not (source_dir / old.name).exists():
                old.unlink()
        for path in sorted(source_dir.glob(pattern)):
            destination = output_dir / path.name
            if path.suffix != ".png" or path not in required:
                shutil.copy2(path, destination)
                continue
            with Image.open(path) as image:
                size = resized_dimensions(image.size, required[path], dpi)
                if size == image.size:
                    shutil.copy2(path, destination)
                else:
                    # Convert indexed PNGs before resizing to retain alpha and
                    # permit high-quality filtering instead of nearest neighbor.
                    resized = image.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                    resized.save(destination, optimize=True)
                print(f"{path.name}: {image.width}x{image.height} -> {size[0]}x{size[1]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Full-size PDF used to measure image placements")
    parser.add_argument("output_dir", type=Path, help="Directory for the generated LaTeX/PNG copy")
    parser.add_argument("--dpi", type=int, default=200, help="Target DPI (default: 200)")
    args = parser.parse_args()
    try:
        stage_images(Path.cwd(), args.pdf, args.output_dir, args.dpi)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Cannot prepare squeezed images: {error}\n")


if __name__ == "__main__":
    main()

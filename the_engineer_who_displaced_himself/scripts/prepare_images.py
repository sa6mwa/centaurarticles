#!/usr/bin/env python3
"""Prepare the essay's JPEG derivatives from its retained PNG originals."""

import argparse
from pathlib import Path

from PIL import Image


# Pixel widths reflect the artwork's actual size on the page. The screen text
# receives extra resolution; the cover is already only about 128 dpi at A4.
WIDTHS = {
    "agent-cutaway": 780,
    "coordination-shift-cover": 600,
    "cover": 1055,
    "growing-foundations": 510,
    "interview-comic": 1629,
    "keyboard-shadow": 1629,
    "letting-go": 1086,
    "narrow-frame": 660,
    "night-workbench": 1086,
    "syntax-shift": 1086,
    "three-roles": 780,
    "working-frontier": 1629,
}
CROPPED = {"letting-go", "night-workbench", "working-frontier"}


def prepare(source: Path, destination: Path) -> None:
    with Image.open(source) as original:
        width = min(WIDTHS[source.stem], original.width)
        scale = width / original.width
        height = round(original.height * scale)
        source_dpi = original.info.get("dpi", (72, 72))
        dpi = tuple(round(value * scale) for value in source_dpi)

        # LaTeX trims these three files in physical points. Exact pixel/DPI
        # scaling retains their natural dimensions and therefore their crops.
        if source.stem in CROPPED and (
            height != original.height * scale
            or any(new != old * scale for new, old in zip(dpi, source_dpi))
        ):
            raise ValueError(f"{source}: resize would change the LaTeX crop; revise its target width")

        image = original.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, "JPEG", quality=90, subsampling=0,
                   optimize=True, progressive=True, dpi=dpi)
        print(f"{destination}: {width}x{height}, {destination.stat().st_size:,} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    prepare(args.source, args.destination)

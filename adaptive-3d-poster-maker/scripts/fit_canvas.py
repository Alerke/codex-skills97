#!/usr/bin/env python3
"""Fit an image to an exact poster canvas without distortion."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageColor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--mode", choices=("cover", "contain"), default="cover")
    parser.add_argument("--anchor", choices=("top", "center", "bottom"), default="center")
    parser.add_argument("--background", default="#FFFFFF")
    return parser.parse_args()


def vertical_offset(extra: int, anchor: str) -> int:
    if anchor == "top":
        return 0
    if anchor == "bottom":
        return extra
    return extra // 2


def fit_image(source: Image.Image, width: int, height: int, mode: str, anchor: str, background: str) -> Image.Image:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    source = source.convert("RGBA")
    source_ratio = source.width / source.height
    target_ratio = width / height

    if mode == "cover":
        scale = width / source.width if source_ratio < target_ratio else height / source.height
        resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
        left = max(0, (resized.width - width) // 2)
        extra_y = max(0, resized.height - height)
        top = vertical_offset(extra_y, anchor)
        return resized.crop((left, top, left + width, top + height))

    scale = min(width / source.width, height / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), ImageColor.getcolor(background, "RGBA"))
    left = (width - resized.width) // 2
    extra_y = height - resized.height
    top = vertical_offset(extra_y, anchor)
    canvas.alpha_composite(resized, (left, top))
    return canvas


def main() -> None:
    args = parse_args()
    with Image.open(args.input) as source:
        result = fit_image(source, args.width, args.height, args.mode, args.anchor, args.background)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() in {".jpg", ".jpeg"}:
        result = result.convert("RGB")
        result.save(args.output, quality=95, subsampling=0)
    else:
        result.save(args.output)

    print(f"Saved {args.output} ({result.width}x{result.height}, mode={args.mode}, anchor={args.anchor})")


if __name__ == "__main__":
    main()

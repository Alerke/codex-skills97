#!/usr/bin/env python3
"""Select one website article palette deterministically."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PALETTES_FILE = Path(__file__).resolve().parent.parent / "references" / "color-palettes.json"


def load_palettes() -> list[dict]:
    payload = json.loads(PALETTES_FILE.read_text(encoding="utf-8"))
    palettes = payload.get("palettes")
    if not isinstance(palettes, list) or len(palettes) < 7:
        raise SystemExit("color-palettes.json must contain at least seven palettes")
    return palettes


def normalize_avoid(values: list[str]) -> set[str]:
    result: set[str] = set()
    for value in values:
        result.update(part.strip().lower() for part in value.split(",") if part.strip())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="为官网文章选择可复现的配色方案")
    parser.add_argument("--title", help="文章标题；自动模式必填")
    parser.add_argument("--palette", help="明确指定配色 ID 或中文名称")
    parser.add_argument("--avoid", action="append", default=[], help="排除一个或多个配色 ID，可重复使用")
    parser.add_argument("--list", action="store_true", help="列出全部配色")
    parser.add_argument("--pretty", action="store_true", help="格式化 JSON 输出")
    args = parser.parse_args()

    palettes = load_palettes()
    indent = 2 if args.pretty else None

    if args.list:
        print(json.dumps({"count": len(palettes), "palettes": palettes}, ensure_ascii=False, indent=indent))
        return 0

    selected: dict | None = None
    reason = ""

    if args.palette:
        needle = args.palette.strip().lower()
        selected = next(
            (
                palette
                for palette in palettes
                if str(palette.get("id", "")).lower() == needle
                or str(palette.get("name", "")).lower() == needle
            ),
            None,
        )
        if selected is None:
            choices = ", ".join(str(palette.get("id", "")) for palette in palettes)
            raise SystemExit(f"unknown palette: {args.palette}; choices: {choices}")
        reason = "explicit"
    else:
        title = (args.title or "").strip()
        if not title:
            raise SystemExit("automatic selection requires --title")
        avoid = normalize_avoid(args.avoid)
        candidates = [palette for palette in palettes if str(palette.get("id", "")).lower() not in avoid]
        if not candidates:
            candidates = palettes
        digest = hashlib.sha256(title.encode("utf-8")).digest()
        selected = candidates[int.from_bytes(digest[:8], "big") % len(candidates)]
        reason = "stable-title-selection"

    print(
        json.dumps(
            {"selection_reason": reason, "palette": selected},
            ensure_ascii=False,
            indent=indent,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path


FORBIDDEN_TAGS = {
    "base",
    "body",
    "button",
    "embed",
    "form",
    "head",
    "html",
    "iframe",
    "input",
    "link",
    "meta",
    "noscript",
    "object",
    "script",
    "style",
    "textarea",
}
LOCAL_RESOURCE_RE = re.compile(
    r"(?:src|href)\s*=\s*['\"]\s*(?:file:/{0,3}|[A-Za-z]:[\\/])",
    re.IGNORECASE,
)
DATA_IMAGE_RE = re.compile(r"src\s*=\s*['\"]\s*data:image/", re.IGNORECASE)
JAVASCRIPT_URL_RE = re.compile(r"(?:src|href)\s*=\s*['\"]\s*javascript:", re.IGNORECASE)
FORBIDDEN_CSS_RE = re.compile(
    r"(?:position\s*:\s*(?:fixed|absolute|sticky)|@(?:media|import|keyframes)|"
    r"display\s*:\s*grid|var\s*\(\s*--)",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(
    r"(?:图片URL|动图URL|待补素材|【\s*(?:插入|待补)|src\s*=\s*['\"]\s*['\"])",
    re.IGNORECASE,
)
WECHAT_TOOL_RE = re.compile(r"(?:复制到公众号|一键复制排版|公众号预览工具)")


class PublishHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: dict[str, int] = {}
        self.styles = 0
        self.text: list[str] = []
        self.errors: list[str] = []
        self.images = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if tag in FORBIDDEN_TAGS:
            self.errors.append(f"forbidden tag: <{tag}>")
        attrs_dict = {name.lower(): (value or "") for name, value in attrs}
        if "style" in attrs_dict and attrs_dict["style"].strip():
            self.styles += 1
        if "class" in attrs_dict or "id" in attrs_dict:
            self.errors.append(f"<{tag}> contains class/id; publish inline styles only")
        for name, value in attrs_dict.items():
            if name.startswith("on"):
                self.errors.append(f"<{tag}> contains event attribute: {name}")
            if name in {"src", "href"} and value.strip().lower().startswith("javascript:"):
                self.errors.append(f"<{tag}> contains a javascript URL")
        if tag == "img":
            self.images += 1
            src = attrs_dict.get("src", "").strip()
            if not src:
                self.errors.append("<img> has an empty src")

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if value:
            self.text.append(value)


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def validate_html(html: str, *, allow_data_images: bool = False) -> dict:
    parser = PublishHTMLParser()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        parser.feed(html)
    except Exception as exc:
        errors.append(f"HTML parse failed: {exc}")
    errors.extend(parser.errors)

    if not html.strip():
        errors.append("content is empty")
    if "section" not in parser.tags:
        errors.append("formatted article must contain at least one <section>")
    if parser.styles == 0:
        errors.append("formatted article has no inline styles")
    if not "".join(parser.text).strip():
        errors.append("article has no visible text")
    if LOCAL_RESOURCE_RE.search(html):
        errors.append("content contains a local file path")
    if DATA_IMAGE_RE.search(html) and not allow_data_images:
        errors.append("content contains a Base64 image")
    if JAVASCRIPT_URL_RE.search(html):
        errors.append("content contains a javascript URL")
    if FORBIDDEN_CSS_RE.search(html):
        errors.append("content contains CSS unsupported by the safe inline layout")
    if PLACEHOLDER_RE.search(html):
        errors.append("content contains an unresolved media placeholder")
    if WECHAT_TOOL_RE.search(html):
        errors.append("content contains a WeChat preview/copy tool element")

    if not any(tag in parser.tags for tag in ("h1", "h2", "h3", "h4", "p")):
        warnings.append("no heading or paragraph tag was detected; review reading structure")

    digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
    return {
        "valid": not errors,
        "sha256": digest,
        "stats": {
            "characters": len(html),
            "visible_text_characters": len("".join(parser.text)),
            "inline_style_attributes": parser.styles,
            "section_tags": parser.tags.get("section", 0),
            "image_tags": parser.images,
        },
        "errors": _unique(errors),
        "warnings": _unique(warnings),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate formatted HTML before website publication.")
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--allow-data-images", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    html = args.html.read_text(encoding="utf-8")
    result = validate_html(html, allow_data_images=args.allow_data_images)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()

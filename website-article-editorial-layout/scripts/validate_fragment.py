#!/usr/bin/env python3
"""Validate a website article rich-text fragment without external dependencies."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


FORBIDDEN_TAGS = {"script", "iframe", "form", "input", "button", "textarea", "object", "embed"}
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
LOCAL_PATH_RE = re.compile(r"^(?:file:|[a-z]:[\\/])", re.IGNORECASE)
UNSAFE_URL_RE = re.compile(r"^(?:javascript:|data:)", re.IGNORECASE)
UNSAFE_POSITION_RE = re.compile(r"position\s*:\s*(?:fixed|absolute|sticky)\b", re.IGNORECASE)


class FragmentValidator(HTMLParser):
    def __init__(self, allow_h1: bool) -> None:
        super().__init__(convert_charrefs=True)
        self.allow_h1 = allow_h1
        self.errors: list[str] = []
        self.section_count = 0
        self.first_tag = ""
        self.first_style = ""
        self.image_count = 0
        self.figure_stack: list[dict[str, object]] = []
        self.caption_numbers: list[int] = []
        self.current_caption_parts: list[str] | None = None
        self.reference_stack: list[dict[str, int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()

        if not self.first_tag:
            self.first_tag = tag
            self.first_style = attrs_map.get("style", "")

        if tag in FORBIDDEN_TAGS:
            self.errors.append(f"禁止标签: <{tag}>")
        if tag == "style":
            self.errors.append("正文片段应使用行内样式，不应包含 <style> 标签")
        if tag == "h1" and not self.allow_h1:
            self.errors.append("正文片段不应重复 <h1>；完整网页模式请使用 --allow-h1")
        if tag == "section":
            self.section_count += 1
        if tag == "p" and attrs_map.get("data-reference-item") == "true":
            reference_style = re.sub(r"\s+", " ", attrs_map.get("style", "").lower()).strip()
            if "display:flex" not in reference_style:
                self.errors.append("参考文献条目必须使用 display:flex 的编号列与正文列")
            if "text-indent:" in reference_style:
                self.errors.append("参考文献条目不得使用 text-indent；续行应由两列结构对齐")
            self.reference_stack.append({"numbers": 0, "contents": 0, "domains": 0})
        if tag == "span" and self.reference_stack:
            span_style = re.sub(r"\s+", " ", attrs_map.get("style", "").lower()).strip()
            if attrs_map.get("data-reference-number") == "true":
                self.reference_stack[-1]["numbers"] += 1
                for required in ("display:block", "flex:0 0 48px", "min-width:48px"):
                    if required not in span_style:
                        self.errors.append(f"参考文献编号列样式缺少 {required}")
            if attrs_map.get("data-reference-content") == "true":
                self.reference_stack[-1]["contents"] += 1
                for required in ("display:block", "flex:1 1 auto", "min-width:0", "text-align:justify", "text-align-last:left"):
                    if required not in span_style:
                        self.errors.append(f"参考文献正文列样式缺少 {required}")
            if attrs_map.get("data-reference-domain") == "true":
                self.reference_stack[-1]["domains"] += 1
                for required in ("white-space:nowrap", "word-break:keep-all", "overflow-wrap:normal"):
                    if required not in span_style:
                        self.errors.append(f"参考文献域名样式缺少 {required}")
        if tag == "figure":
            self.figure_stack.append({"images": 0, "captions": []})
        if tag == "figcaption":
            if not self.figure_stack:
                self.errors.append("图注 <figcaption> 必须位于图片组 <figure> 内")
            self.current_caption_parts = []
        if tag == "img":
            self.image_count += 1
            src = attrs_map.get("src", "").strip()
            image_style = re.sub(r"\s+", "", attrs_map.get("style", "").lower())
            if not src:
                self.errors.append("图片缺少 src")
            if not attrs_map.get("alt"):
                self.errors.append("图片缺少有意义的 alt")
            if LOCAL_PATH_RE.match(src) or UNSAFE_URL_RE.match(src):
                self.errors.append(f"图片使用了不可发布的地址: {src[:80]}")
            if src.lower().startswith("http://"):
                self.errors.append("公网图片应使用 HTTPS")
            for required in ("display:block", "max-width:100%", "height:auto"):
                if required not in image_style:
                    self.errors.append(f"图片样式缺少 {required}")
            if not self.figure_stack:
                self.errors.append("每张正文图片必须放在 <figure> 中并紧跟非空图注")
            else:
                self.figure_stack[-1]["images"] = int(self.figure_stack[-1]["images"]) + 1
        if tag == "a" and attrs_map.get("target") == "_blank":
            rel = set(attrs_map.get("rel", "").split())
            if not {"noopener", "noreferrer"}.issubset(rel):
                self.errors.append("新窗口链接必须包含 rel=\"noopener noreferrer\"")

        if tag == "a":
            href = attrs_map.get("href", "").strip()
            if LOCAL_PATH_RE.match(href) or UNSAFE_URL_RE.match(href):
                self.errors.append(f"链接使用了不可发布的地址: {href[:80]}")

        if UNSAFE_POSITION_RE.search(attrs_map.get("style", "")):
            self.errors.append(f"禁止定位样式: <{tag}> 使用 fixed/absolute/sticky")

        for name in attrs_map:
            if name.startswith("on"):
                self.errors.append(f"禁止事件属性: {name}")

    def handle_data(self, data: str) -> None:
        if self.current_caption_parts is not None:
            self.current_caption_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "p" and self.reference_stack:
            reference = self.reference_stack.pop()
            if reference["numbers"] != 1:
                self.errors.append("每条参考文献必须且只能包含一个编号列")
            if reference["contents"] != 1:
                self.errors.append("每条参考文献必须且只能包含一个正文列")
        elif tag == "figcaption":
            caption = "".join(self.current_caption_parts or []).strip()
            if not caption:
                self.errors.append("图片图注不能为空")
            elif self.figure_stack:
                captions = self.figure_stack[-1]["captions"]
                assert isinstance(captions, list)
                captions.append(caption)
                match = re.match(r"^图\s*(\d+)\s*[｜|：:]", caption)
                if not match:
                    self.errors.append(f"图注必须使用“图 N｜说明”格式: {caption[:40]}")
                else:
                    self.caption_numbers.append(int(match.group(1)))
            self.current_caption_parts = None
        elif tag == "figure":
            if not self.figure_stack:
                self.errors.append("发现未配对的 </figure>")
                return
            figure = self.figure_stack.pop()
            images = int(figure["images"])
            captions = figure["captions"]
            assert isinstance(captions, list)
            if images != 1:
                self.errors.append(f"每个 <figure> 必须且只能包含一张图片，当前为 {images} 张")
            if len(captions) != 1:
                self.errors.append(f"每个 <figure> 必须且只能包含一个图注，当前为 {len(captions)} 个")

    def close_and_check(self) -> list[str]:
        self.close()
        if self.section_count == 0:
            self.errors.append("未找到正文根 <section>")
        if not self.allow_h1:
            if self.first_tag != "section":
                self.errors.append("正文片段必须以根 <section> 开始")
            root_style = re.sub(r"\s+", "", self.first_style.lower())
            if "width:100%" not in root_style or "max-width:100%" not in root_style:
                self.errors.append("正文根 <section> 必须使用 width:100% 和 max-width:100%")
        if self.figure_stack:
            self.errors.append("存在未闭合的 <figure> 图片组")
        if self.reference_stack:
            self.errors.append("存在未闭合的参考文献条目")
        if self.image_count:
            expected = list(range(1, self.image_count + 1))
            if self.caption_numbers != expected:
                self.errors.append(
                    f"图注编号必须从 1 开始连续排列；当前为 {self.caption_numbers}，应为 {expected}"
                )
        return self.errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验官网文章 HTML 正文片段")
    parser.add_argument("html_file", type=Path)
    parser.add_argument("--allow-h1", action="store_true", help="完整网页模式允许 h1")
    args = parser.parse_args()

    try:
        html = args.html_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: 无法读取文件: {exc}", file=sys.stderr)
        return 2

    validator = FragmentValidator(args.allow_h1)
    placeholders = sorted(set(PLACEHOLDER_RE.findall(html)))
    if placeholders:
        validator.errors.append(f"存在未替换占位符: {', '.join(placeholders[:12])}")
    validator.feed(html)
    errors = validator.close_and_check()

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: HTML 正文片段通过结构与安全校验")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

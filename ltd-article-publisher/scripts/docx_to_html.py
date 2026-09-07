from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


URL_RE = re.compile(r"https?://[^\s<>]+")


def escape_and_link(text: str) -> str:
    parts: list[str] = []
    pos = 0
    for match in URL_RE.finditer(text):
        parts.append(html.escape(text[pos : match.start()]))
        url = match.group(0)
        escaped_url = html.escape(url, quote=True)
        parts.append(
            f'<a href="{escaped_url}" target="_blank" '
            f'rel="noopener noreferrer">{html.escape(url)}</a>'
        )
        pos = match.end()
    parts.append(html.escape(text[pos:]))
    return "".join(parts)


def has_image(paragraph: Paragraph) -> bool:
    return bool(paragraph._p.xpath(".//a:blip"))


def is_list(paragraph: Paragraph) -> bool:
    p_pr = paragraph._p.pPr
    return bool(p_pr is not None and p_pr.find(qn("w:numPr")) is not None)


def safe_href(value: str) -> str | None:
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"}:
        return None
    return value


def render_run(run_element) -> str:
    text = "".join(node.text or "" for node in run_element.findall(".//" + qn("w:t")))
    breaks = len(run_element.findall(".//" + qn("w:br")))
    if not text and not breaks:
        return ""
    rendered = escape_and_link(text) + ("<br>" * breaks)
    r_pr = run_element.find(qn("w:rPr"))
    if r_pr is not None:
        if r_pr.find(qn("w:b")) is not None:
            rendered = f"<strong>{rendered}</strong>"
        if r_pr.find(qn("w:i")) is not None:
            rendered = f"<em>{rendered}</em>"
        if r_pr.find(qn("w:u")) is not None:
            rendered = f"<u>{rendered}</u>"
    return rendered


def render_paragraph_text(paragraph: Paragraph) -> str:
    parts: list[str] = []
    for child in paragraph._p:
        if child.tag == qn("w:r"):
            parts.append(render_run(child))
        elif child.tag == qn("w:hyperlink"):
            link_text = "".join(render_run(run) for run in child.findall(qn("w:r")))
            rid = child.get(qn("r:id"))
            href = None
            if rid and rid in paragraph.part.rels:
                href = safe_href(paragraph.part.rels[rid].target_ref)
            if href:
                parts.append(
                    f'<a href="{html.escape(href, quote=True)}" target="_blank" '
                    f'rel="noopener noreferrer">{link_text}</a>'
                )
            else:
                parts.append(link_text)
    rendered = "".join(parts).strip()
    return rendered or escape_and_link(paragraph.text.strip())


def paragraph_tag(paragraph: Paragraph) -> str:
    style = (paragraph.style.name if paragraph.style else "").strip().lower()
    if style in {"heading 1", "标题 1", "标题1"}:
        return "h2"
    if style in {"heading 2", "标题 2", "标题2"}:
        return "h3"
    if style in {"heading 3", "标题 3", "标题3"}:
        return "h4"
    return "p"


def render_table(table: Table) -> str:
    rows: list[str] = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            cell_text = "<br>".join(
                escape_and_link(p.text.strip()) for p in cell.paragraphs if p.text.strip()
            )
            cells.append(f"<td>{cell_text}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<table><tbody>" + "".join(rows) + "</tbody></table>"


def iter_blocks(document: Document):
    for child in document.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, document)
        elif child.tag == qn("w:tbl"):
            yield Table(child, document)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a DOCX article to conservative HTML.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--image-policy", choices=("reject", "omit"), default="reject")
    parser.add_argument(
        "--title-mode", choices=("first-paragraph", "filename"), default="first-paragraph"
    )
    parser.add_argument("--keep-title-in-body", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    document = Document(args.input)
    blocks = list(iter_blocks(document))
    paragraphs = [block for block in blocks if isinstance(block, Paragraph)]
    image_count = len(document.element.xpath(".//a:blip"))
    if image_count and args.image_policy == "reject":
        raise SystemExit(
            f"DOCX contains {image_count} embedded image(s). Choose an upload plan or rerun "
            "with --image-policy omit only after the user approves text-only publication."
        )

    first_paragraph = next((p for p in paragraphs if p.text.strip()), None)
    if args.title_mode == "first-paragraph" and first_paragraph is not None:
        title = first_paragraph.text.strip()
    else:
        title = args.input.stem

    output_blocks: list[str] = []
    in_list = False
    paragraph_count = 0
    table_count = 0
    for block in blocks:
        if isinstance(block, Table):
            if in_list:
                output_blocks.append("</ul>")
                in_list = False
            output_blocks.append(render_table(block))
            table_count += 1
            continue

        paragraph = block
        if paragraph is first_paragraph and not args.keep_title_in_body:
            continue
        if has_image(paragraph) and not paragraph.text.strip():
            continue
        if not paragraph.text.strip():
            continue

        rendered = render_paragraph_text(paragraph)
        if is_list(paragraph):
            if not in_list:
                output_blocks.append("<ul>")
                in_list = True
            output_blocks.append(f"<li>{rendered}</li>")
        else:
            if in_list:
                output_blocks.append("</ul>")
                in_list = False
            tag = paragraph_tag(paragraph)
            output_blocks.append(f"<{tag}>{rendered}</{tag}>")
        paragraph_count += 1
    if in_list:
        output_blocks.append("</ul>")

    article_html = "\n".join(output_blocks)
    args.output.write_text(article_html, encoding="utf-8")
    print(
        json.dumps(
            {
                "title": title,
                "output": str(args.output.resolve()),
                "html_chars": len(article_html),
                "paragraphs": paragraph_count,
                "tables": table_count,
                "images_found": image_count,
                "images_omitted": image_count if args.image_policy == "omit" else 0,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

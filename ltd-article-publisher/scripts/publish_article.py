from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from validate_publish_html import validate_html


IMG_RE = re.compile(r"<img\b", re.IGNORECASE)


class WorkflowError(RuntimeError):
    pass


def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def request_json(url: str, *, data: bytes | None = None, timeout: int = 30) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=data,
        method="POST" if data is not None else "GET",
        headers={"Content-Type": "application/x-www-form-urlencoded"} if data is not None else {},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", errors="replace")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"raw_response": raw[:2000]}
    return status, payload


def origin(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")


def exact_matches(base_url: str, cid: str, title: str, language_type: str, timeout: int) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "mold_types": "1",
            "cat_ids": cid,
            "page": "1",
            "page_size": "100",
            "keywords": title,
            "sort_by": "created_at",
            "sort": "desc",
            "language_type": language_type,
        }
    )
    status, payload = request_json(
        f"{base_url.rstrip('/')}/api/gatewayCms/articles/list?{params}", timeout=timeout
    )
    if status < 200 or status >= 300 or payload.get("code") != 0:
        raise WorkflowError(f"article list query failed: HTTP {status}, response={payload}")
    data = payload.get("data") or {}
    items = data.get("data") if isinstance(data, dict) else []
    if not isinstance(items, list):
        raise WorkflowError("article list response.data.data is not an array")
    matches = []
    for item in items:
        if (
            isinstance(item, dict)
            and str(item.get("cat_id", "")) == cid
            and str(item.get("title", "")) == title
        ):
            matches.append(
                {
                    "id": str(item.get("id", "")),
                    "cat_id": str(item.get("cat_id", "")),
                    "title": str(item.get("title", "")),
                    "created_at": str(item.get("created_at", "")),
                    "published_at": str(item.get("published_at", "")),
                }
            )
    return matches


def verify_detail(url: str, title: str, timeout: int) -> dict:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"url": url, "http_status": response.status, "title_present": title in body}
    except Exception as exc:
        return {"url": url, "error": str(exc), "title_present": False}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish one article through an LTD-compatible API.")
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--site-base")
    parser.add_argument("--cid", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--content-file", required=True, type=Path)
    parser.add_argument("--language-type", default="zh-cn")
    parser.add_argument("--author")
    parser.add_argument("--source")
    parser.add_argument("--original-url")
    parser.add_argument("--seo-title")
    parser.add_argument("--seo-keywords")
    parser.add_argument("--seo-description")
    parser.add_argument("--secret-env", default="LTD_ARTICLE_ACCESS_SECRET")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--verify-attempts", type=int, default=3)
    parser.add_argument("--verify-delay", type=float, default=1.0)
    parser.add_argument("--allow-http", action="store_true")
    parser.add_argument("--allow-data-images", action="store_true")
    parser.add_argument("--allow-duplicate", action="store_true")
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    parser.add_argument("--confirm-publish", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cid = args.cid.strip()
    title = args.title.strip()
    if not cid.isdigit():
        raise SystemExit("cid must contain digits only")
    if not title:
        raise SystemExit("title must not be empty")
    if args.timeout <= 0 or args.verify_attempts <= 0 or args.verify_delay < 0:
        raise SystemExit("timeout/verification options are invalid")

    endpoint_scheme = urllib.parse.urlsplit(args.endpoint).scheme.lower()
    if endpoint_scheme not in {"http", "https"}:
        raise SystemExit("endpoint must use http or https")
    if endpoint_scheme == "http" and not args.allow_http:
        raise SystemExit("HTTP exposes the secret in transit; rerun with --allow-http only after approval")

    content = args.content_file.read_text(encoding="utf-8").strip()
    if not content:
        raise SystemExit("content file is empty")
    layout = validate_html(content, allow_data_images=args.allow_data_images)
    if not layout["valid"]:
        emit({"status": "layout_validation_failed", "layout": layout})
        raise SystemExit(5)

    base_url = (args.site_base or origin(args.endpoint)).rstrip("/")
    if urllib.parse.urlsplit(base_url).scheme.lower() == "http" and not args.allow_http:
        raise SystemExit("HTTP verification base requires --allow-http after approval")

    audit = {
        "endpoint": args.endpoint,
        "site_base": base_url,
        "cid": cid,
        "title": title,
        "language_type": args.language_type,
        "content_chars": len(content),
        "image_tags": len(IMG_RE.findall(content)),
        "layout_sha256": layout["sha256"],
        "layout_stats": layout["stats"],
        "layout_warnings": layout["warnings"],
    }

    if not args.skip_preflight:
        try:
            existing = exact_matches(base_url, cid, title, args.language_type, args.timeout)
        except Exception as exc:
            emit({"status": "preflight_failed", "audit": audit, "error": str(exc)})
            raise SystemExit(2)
        if existing and not args.allow_duplicate:
            emit({"status": "duplicate_detected", "audit": audit, "matches": existing})
            raise SystemExit(3)

    if args.dry_run:
        emit({"status": "dry_run_passed", "audit": audit})
        return
    if not args.confirm_publish:
        raise SystemExit("real publication requires --confirm-publish")

    secret = os.environ.get(args.secret_env)
    if not secret:
        raise SystemExit(f"secret environment variable {args.secret_env} is not set")

    form: dict[str, str] = {
        "cid": cid,
        "title": title,
        "content": content,
        "password": secret,
        "language_type": args.language_type,
    }
    optional_fields = {
        "author": args.author,
        "source": args.source,
        "original_url": args.original_url,
        "seo_title": args.seo_title,
        "seo_keywords": args.seo_keywords,
        "seo_description": args.seo_description,
    }
    form.update({key: value for key, value in optional_fields.items() if value})

    try:
        http_status, response = request_json(
            args.endpoint,
            data=urllib.parse.urlencode(form).encode("utf-8"),
            timeout=args.timeout,
        )
    except Exception as exc:
        emit(
            {
                "status": "transport_unknown",
                "audit": audit,
                "error": str(exc),
                "retry": "Do not retry before checking the article list.",
            }
        )
        raise SystemExit(2)

    result: dict = {
        "status": "api_rejected",
        "audit": audit,
        "http_status": http_status,
        "response": response,
        "verified": False,
    }
    if http_status < 200 or http_status >= 300 or response.get("code") != 0:
        emit(result)
        raise SystemExit(1)

    result["status"] = "api_accepted"
    if args.skip_verify:
        emit(result)
        return

    matches: list[dict] = []
    for attempt in range(args.verify_attempts):
        if attempt:
            time.sleep(args.verify_delay)
        try:
            matches = exact_matches(base_url, cid, title, args.language_type, args.timeout)
        except Exception as exc:
            result["verification_error"] = str(exc)
            continue
        if matches:
            break

    if not matches:
        result["status"] = "accepted_not_visible"
        emit(result)
        raise SystemExit(4)

    response_data = response.get("data") if isinstance(response.get("data"), dict) else {}
    response_id = str(response_data.get("id", "")) if response_data else ""
    match = next((item for item in matches if str(item.get("id", "")) == response_id), matches[0])
    article_id = str(match.get("id", ""))
    article_url = str(response_data.get("url", "")) if response_data else ""
    if not article_url and article_id:
        article_url = f"{base_url}/article/{urllib.parse.quote(article_id, safe='')}"
    detail = verify_detail(article_url, title, args.timeout) if article_url else {}

    result.update(
        {
            "status": "verified_published" if detail.get("title_present") else "record_visible_detail_unverified",
            "verified": bool(detail.get("title_present")),
            "article": {
                "id": article_id,
                "title": str(match.get("title", "")),
                "cat_id": str(match.get("cat_id", "")),
                "url": article_url,
            },
            "detail": detail,
        }
    )
    emit(result)
    if not result["verified"]:
        raise SystemExit(4)


if __name__ == "__main__":
    main()

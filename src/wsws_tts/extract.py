from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Article:
    url: str
    title: str
    authors: list[str]
    published: str | None
    paragraphs: list[str]


class ExtractionError(RuntimeError):
    pass


_WSWS_ALLOWED_PREFIX = "https://www.wsws.org/en/"


def _normalize_ws(text: str) -> str:
    # Collapse whitespace but keep meaningful punctuation.
    return re.sub(r"\s+", " ", text).strip()


def _node_text(node: dict[str, Any] | None) -> str:
    if not node:
        return ""
    node_type = node.get("type")
    if node_type == "text":
        return node.get("content") or ""
    if node_type == "element":
        tag = node.get("tagName")
        if tag == "br":
            return "\n"
        children = node.get("children") or []
        return "".join(_node_text(child) for child in children)
    # Unknown type
    children = node.get("children") if isinstance(node, dict) else None
    if children:
        return "".join(_node_text(child) for child in children)
    return ""


def _extract_paragraphs_from_content_data(
    content_data: list[dict[str, Any]],
) -> list[str]:
    paragraphs: list[str] = []
    for item in content_data:
        if item.get("type") != "element":
            continue
        tag = item.get("tagName")
        if tag not in {"p", "blockquote", "h2", "h3", "li"}:
            continue

        raw = _node_text(item)
        text = _normalize_ws(raw)
        if not text:
            continue

        if tag == "blockquote":
            text = f'"{text}"'
        paragraphs.append(text)
    return paragraphs


def _load_next_data(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        raise ExtractionError("Could not find __NEXT_DATA__ script in page")
    try:
        return json.loads(script.string)
    except json.JSONDecodeError as e:
        raise ExtractionError(f"Failed to parse __NEXT_DATA__ JSON: {e}") from e


def extract_wsws_article(url: str, *, timeout_s: int = 30) -> Article:
    if not url.startswith(_WSWS_ALLOWED_PREFIX):
        raise ExtractionError(
            f"Only WSWS English URLs are supported (must start with {_WSWS_ALLOWED_PREFIX})."
        )

    resp = requests.get(
        url,
        timeout=timeout_s,
        headers={
            "User-Agent": "wsws-tts/0.1 (+https://github.com/resemble-ai/chatterbox)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    resp.raise_for_status()

    data = _load_next_data(resp.text)
    props = (data.get("props") or {}).get("pageProps") or {}

    # Observed on WSWS: props.pageProps.initialData.page
    initial_data = props.get("initialData") or {}
    page = initial_data.get("page")
    if not isinstance(page, dict):
        raise ExtractionError(
            "WSWS page JSON did not include props.pageProps.initialData.page"
        )

    title = page.get("title") or "(untitled)"
    authors = page.get("authors") or []
    published_raw = page.get("published")

    content_data = page.get("contentData")
    if not isinstance(content_data, list):
        raise ExtractionError("WSWS page JSON did not include contentData list")

    paragraphs = _extract_paragraphs_from_content_data(content_data)
    if not paragraphs:
        raise ExtractionError("No paragraphs were extracted from contentData")

    published: str | None
    if published_raw is None:
        published = None
    else:
        # WSWS currently exposes UNIX timestamps (seconds) in __NEXT_DATA__.
        try:
            ts = int(published_raw)
            published = (
                datetime.fromtimestamp(ts, tz=timezone.utc)
                .replace(microsecond=0)
                .isoformat()
            )
        except Exception:
            published = _normalize_ws(str(published_raw))

    return Article(
        url=url,
        title=_normalize_ws(str(title)),
        authors=[_normalize_ws(str(a)) for a in authors if _normalize_ws(str(a))],
        published=published,
        paragraphs=paragraphs,
    )

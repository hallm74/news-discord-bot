"""Utilities for cleaning and normalizing feed entries."""

from __future__ import annotations

import html
import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)


def clean_text(text: str | None) -> str:
    """Strip HTML tags/entities and collapse whitespace."""
    if not text:
        return ""
    unescaped = html.unescape(text)
    without_tags = re.sub(r"<[^>]+>", " ", unescaped)
    without_entities = re.sub(r"&[a-zA-Z]+;", " ", without_tags)
    squashed = re.sub(r"\s+", " ", without_entities)
    return squashed.strip()


def _format_published(entry: Dict[str, Any]) -> str:
    """Convert published date into ISO 8601, falling back to raw string."""
    if "published_parsed" in entry and entry["published_parsed"]:
        try:
            ts = time.mktime(entry["published_parsed"])
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.debug("Failed to parse published_parsed: %s", exc)
    if "published" in entry and entry["published"]:
        return clean_text(str(entry["published"]))
    return ""


def normalize_entry(entry: Dict[str, Any], source: str, section: str) -> Dict[str, str]:
    """Normalize a feedparser entry into a simplified dict."""
    title = clean_text(entry.get("title"))
    link = entry.get("link", "")
    summary = clean_text(entry.get("summary")) or clean_text(entry.get("description"))
    published = _format_published(entry)

    return {
        "source": source,
        "title": title,
        "link": link,
        "published": published,
        "summary": summary,
        "section": section,
    }

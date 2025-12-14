"""Feed loading and fetching utilities."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import feedparser

from clean import normalize_entry

LOGGER = logging.getLogger(__name__)
DEFAULT_FEEDS_PATH = Path(__file__).resolve().parent.parent / "config" / "feeds.json"


def load_feeds(path: Path | None = None) -> List[Dict[str, Any]]:
    feeds_path = path or DEFAULT_FEEDS_PATH
    with feeds_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data


def fetch_feed_items(feeds: List[Dict[str, Any]], limit: int | None = None) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []

    for feed in feeds:
        url = feed.get("url")
        source = feed.get("source", "")
        section = feed.get("section", "top")
        if not url:
            continue

        parsed = feedparser.parse(url)
        if getattr(parsed, "bozo", False):
            LOGGER.debug("Feed parser flagged issues for %s (feed still usable)", url)

        for entry in parsed.entries:
            items.append(normalize_entry(entry, source=source, section=section))

    if limit is not None and limit > 0:
        items = items[:limit]

    return items

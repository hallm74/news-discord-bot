"""Deduplication helpers for feed items."""

from __future__ import annotations

import logging
import re
from difflib import SequenceMatcher
from typing import Dict, List

LOGGER = logging.getLogger(__name__)


def _normalize_title(title: str) -> str:
    lowered = title.lower()
    stripped = re.sub(r"[^a-z0-9 ]", " ", lowered)
    return re.sub(r"\s+", " ", stripped).strip()


def _is_near_duplicate(title: str, existing: List[str]) -> bool:
    for other in existing:
        ratio = SequenceMatcher(None, title, other).ratio()
        if ratio >= 0.9:
            return True
    return False


def dedupe_items(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicates by link and near-duplicate titles while preserving order."""
    seen_links: set[str] = set()
    normalized_titles: List[str] = []
    unique_items: List[Dict[str, str]] = []

    for item in items:
        link = item.get("link", "")
        if link and link in seen_links:
            LOGGER.debug("Dropping duplicate link: %s", link)
            continue

        normalized_title = _normalize_title(item.get("title", ""))
        if normalized_title and _is_near_duplicate(normalized_title, normalized_titles):
            LOGGER.debug("Dropping near-duplicate title: %s", item.get("title", ""))
            continue

        if link:
            seen_links.add(link)
        if normalized_title:
            normalized_titles.append(normalized_title)
        unique_items.append(item)

    return unique_items

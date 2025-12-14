"""Digest creation utilities."""

from __future__ import annotations

import logging
from typing import Dict, List

from llm import LLMClient

LOGGER = logging.getLogger(__name__)

SECTION_TITLES = {
    "top": "Top Headlines",
    "politics": "Politics & Policy",
    "world": "World & Economy",
}


def _group_by_section(items: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = {key: [] for key in SECTION_TITLES}
    for item in items:
        section = item.get("section", "top")
        grouped.setdefault(section, []).append(item)
    return grouped


def _format_fallback(grouped: Dict[str, List[Dict[str, str]]]) -> str:
    lines: List[str] = ["# Daily National News Digest", ""]
    for section, title in SECTION_TITLES.items():
        lines.append(f"## {title}")
        section_items = grouped.get(section, [])
        if not section_items:
            lines.append("- _No items_\n")
            continue
        for item in section_items[:6]:
            source = item.get("source", "")
            title_text = item.get("title", "")
            link = item.get("link", "")
            lines.append(f"- {title_text} — {source} ({link})")
        lines.append("")
    lines.append("Sources: NPR, AP, Reuters")
    return "\n".join(lines).strip()


def build_digest(items: List[Dict[str, str]], use_llm: bool, llm_client: LLMClient | None = None) -> str:
    grouped = _group_by_section(items)
    client = llm_client or LLMClient(disabled=not use_llm)

    LOGGER.info("use_llm=%s, client.available=%s", use_llm, client.available)

    if use_llm and client.available:
        try:
            llm_digest = client.summarize(grouped)
            if llm_digest:
                LOGGER.info("Using LLM-generated digest")
                return llm_digest
            else:
                LOGGER.warning("LLM returned None, using fallback")
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.warning("LLM summarization failed, using fallback: %s", exc)

    LOGGER.info("Using fallback headline format")
    return _format_fallback(grouped)

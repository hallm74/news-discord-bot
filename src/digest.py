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


def _format_key_stories(items: List[Dict[str, str]]) -> str:
    """Build Key Stories section ensuring diverse sources."""
    grouped = _group_by_section(items)
    lines = ["🔗 Key Stories"]
    
    # Alternate between sources to ensure diversity
    for section, section_items in grouped.items():
        # Separate by source
        by_source: Dict[str, List[Dict[str, str]]] = {}
        for item in section_items:
            source = item.get("source", "Unknown")
            by_source.setdefault(source, []).append(item)
        
        # Take up to 3 per source for this section
        idx = 0
        while idx < 6 and any(by_source[s] for s in by_source):
            for source in sorted(by_source.keys()):
                if idx >= 6:
                    break
                if by_source[source]:
                    item = by_source[source].pop(0)
                    title = item.get("title", "")
                    link = item.get("link", "")
                    lines.append(f"- {title} — [{source}]({link})")
                    idx += 1
    
    return "\n".join(lines)


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
    lines.append("Sources: NPR, AP")
    return "\n".join(lines).strip()


def build_digest(items: List[Dict[str, str]], use_llm: bool, llm_client: LLMClient | None = None) -> str:
    grouped = _group_by_section(items)
    client = llm_client or LLMClient(disabled=not use_llm)

    LOGGER.info("use_llm=%s, client.available=%s", use_llm, client.available)

    if use_llm and client.available:
        try:
            llm_digest = client.summarize(items)
            if llm_digest:
                LOGGER.info("Using LLM-generated digest")
                # Append our Key Stories list to ensure all sources included
                key_stories = _format_key_stories(items)
                return llm_digest + "\n\n" + key_stories
            else:
                LOGGER.warning("LLM returned None, using fallback")
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.warning("LLM summarization failed, using fallback: %s", exc)

    LOGGER.info("Using fallback headline format")
    return _format_fallback(grouped)

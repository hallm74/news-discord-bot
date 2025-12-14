"""Discord webhook helper."""

from __future__ import annotations

import logging
from typing import List

import requests

LOGGER = logging.getLogger(__name__)

DISCORD_LIMIT = 1900  # reserve space for code fences/formatting


def _chunk_message(content: str, limit: int = DISCORD_LIMIT) -> List[str]:
    """Chunk content by section boundaries to avoid duplication."""
    chunks: List[str] = []
    lines = content.split("\n")
    current_chunk: List[str] = []
    current_size = 0

    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        # If adding this line exceeds limit and we have content, flush chunk
        if current_size + line_size > limit and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_size = 0

        current_chunk.append(line)
        current_size += line_size

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def post_digest(content: str, webhook_url: str) -> None:
    for chunk in _chunk_message(content):
        response = requests.post(webhook_url, json={"content": chunk})
        try:
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover - network errors
            LOGGER.warning("Failed to post to Discord: %s", exc)
            raise

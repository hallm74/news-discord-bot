"""LLM client abstraction using GitHub Models (OpenAI-compatible)."""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

from openai import OpenAI

LOGGER = logging.getLogger(__name__)

PROMPT_TEMPLATE = """
You are a professional news editor. Create a concise daily news digest.

Structure:
1. Title: "📰 Daily National News Digest"
2. Write 2-4 paragraphs synthesizing the major themes and developments
   - Synthesize key takeaways (do NOT just list headlines)
   - Use clear, neutral language
   - Focus on what readers should know today
   - Do NOT include links in the summary text
   - Reference multiple sources as appropriate

Keep output under 600 words.
""".strip()


class LLMClient:
    def __init__(self, disabled: bool = False) -> None:
        self.disabled = disabled
        self.api_key = os.getenv("GH_MODELS_TOKEN")
        self.base_url = os.getenv("MODELS_ENDPOINT")
        self.model = os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.available = not disabled and bool(self.api_key and self.base_url)
        self._client: Optional[OpenAI] = None
        if self.available:
            self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def summarize(self, items: List[Dict[str, str]]) -> Optional[str]:
        if not self.available or not self._client:
            return None

        # Format items as simple bullet list for LLM context
        bullet_lines = []
        for item in items[:20]:  # Limit to prevent token overflow
            title = item.get("title", "")
            source = item.get("source", "")
            bullet_lines.append(f"- {title} ({source})")
        
        content = "News stories:\n" + "\n".join(bullet_lines)

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PROMPT_TEMPLATE},
                    {"role": "user", "content": content},
                ],
                temperature=0.2,
            )
            result = response.choices[0].message.content
            if result:
                LOGGER.info("LLM response received (%d chars)", len(result))
                LOGGER.info("LLM response preview: %s", result[:200])
            else:
                LOGGER.warning("LLM returned empty response")
            return result
        except Exception as exc:  # pragma: no cover - network errors
            LOGGER.warning("LLM request failed: %s", exc)
            return None

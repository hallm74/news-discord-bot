"""CLI entrypoint for the daily news digest."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Allow running as `python src/main.py` by ensuring sibling modules are importable.
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from dedupe import dedupe_items
from digest import build_digest
from feeds import fetch_feed_items, load_feeds
from llm import LLMClient
from discord import post_digest

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily National News Digest")
    parser.add_argument("--dry-run", action="store_true", help="Print digest to terminal")
    parser.add_argument("--no-llm", action="store_true", help="Skip AI summarization")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of feed items")
    parser.add_argument("--output", type=str, help="Write digest to file")
    parser.add_argument("--post", action="store_true", help="Post to Discord via webhook")
    return parser.parse_args()


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main() -> None:
    configure_logging()
    load_dotenv()

    args = parse_args()
    feeds = load_feeds()

    LOGGER.info("Fetching feeds")
    items = fetch_feed_items(feeds, limit=args.limit)
    items = dedupe_items(items)

    llm_client = LLMClient(disabled=args.no_llm)
    digest_text = build_digest(items, use_llm=not args.no_llm, llm_client=llm_client)

    if args.output:
        Path(args.output).write_text(digest_text, encoding="utf-8")
        LOGGER.info("Wrote digest to %s", args.output)

    if args.dry_run or not args.post:
        print(digest_text)

    if args.post:
        webhook = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook:
            LOGGER.warning("DISCORD_WEBHOOK_URL not set; skipping Discord post")
        else:
            LOGGER.info("Posting digest to Discord")
            post_digest(digest_text, webhook)
            LOGGER.info("Posted digest successfully")


if __name__ == "__main__":
    main()

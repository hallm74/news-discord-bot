# Daily National News Digest

A Python 3.11 CLI that fetches national, politics, and world RSS feeds from NPR, AP, and Reuters, deduplicates headlines, summarizes them with GitHub Models, and can optionally post a Markdown digest to Discord. The same CLI is used locally and in GitHub Actions.

## Quickstart

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill in values (GITHUB_TOKEN, GITHUB_MODELS_ENDPOINT, MODEL_NAME, DISCORD_WEBHOOK_URL).
4. Run a dry run locally (no Discord posting): `make dry-run` or `python src/main.py --dry-run`.

## CLI usage

- Print digest only: `python src/main.py --dry-run`
- Skip LLM (headline-only): `python src/main.py --no-llm --limit 20`
- Save to file: `python src/main.py --dry-run --output digest.md`
- Post to Discord (requires webhook env var): `python src/main.py --post`

Flags:
- `--dry-run` prints to terminal.
- `--no-llm` disables GitHub Models summarization (headline-only).
- `--limit N` limits number of feed items pulled.
- `--output FILE` writes digest to a file.
- `--post` posts to Discord **only if** `DISCORD_WEBHOOK_URL` is set.

## Environment

`.env.example` lists required variables:
- `GITHUB_TOKEN`
- `GITHUB_MODELS_ENDPOINT`
- `MODEL_NAME`
- `DISCORD_WEBHOOK_URL`

If LLM env vars are missing or `--no-llm` is set, the digest falls back to headline bullets.

## Development

- Run: `make run`
- Dry run: `make dry-run`
- Tests: `make test`
- Lint: `make lint`

`PYTHONPATH=src` is set in Make targets so local imports work consistently.

## GitHub Actions

Workflow `.github/workflows/daily-digest.yml` runs daily at 7:00 AM America/Chicago and on manual dispatch. It installs dependencies and runs the **same** CLI command used locally: `python src/main.py --post`.

## Sources

Feed URLs live in `config/feeds.json` (NPR, AP, Reuters: national/top, politics, world). Edit this file to adjust coverage.

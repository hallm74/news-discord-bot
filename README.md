# Daily National News Digest

A Python 3.11 CLI that fetches national and political news from NPR and AP RSS feeds, deduplicates headlines, synthesizes them using GitHub Models (AI), and optionally posts a Markdown digest to Discord. The same CLI runs locally and in GitHub Actions.

## Features

- **Multi-source aggregation**: NPR National, NPR Politics, AP News
- **Deduplication**: Removes duplicate links and near-duplicate titles (90%+ match)
- **AI summarization**: GitHub Models creates readable narrative summaries
- **Source diversity**: Key Stories alternates between AP/NPR for balanced coverage
- **Discord integration**: Posts formatted digests with source-attributed links
- **Fallback mode**: Works without AI (headline-only format)
- **Fully testable locally** before automation
- **Scheduled automation**: Daily at 7 AM America/Chicago via GitHub Actions

## Quickstart

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in values:
   - `GH_MODELS_TOKEN` (Personal Access Token for GitHub Models)
   - `MODELS_ENDPOINT` (default: `https://models.inference.ai.azure.com`)
   - `MODEL_NAME` (default: `gpt-4o-mini`)
   - `DISCORD_WEBHOOK_URL` (optional, for Discord posting)

4. Run a dry run (prints to terminal, no Discord):
   ```bash
   make dry-run
   ```

## CLI Usage

All commands use `PYTHONPATH=src` (handled by Makefile or set manually):

**Print digest to terminal only:**
```bash
make dry-run
# or: PYTHONPATH=src python src/main.py --dry-run
```

**Skip AI summarization (headline-only):**
```bash
PYTHONPATH=src python src/main.py --dry-run --no-llm --limit 20
```

**Save to file:**
```bash
PYTHONPATH=src python src/main.py --dry-run --output digest.md
```

**Post to Discord** (requires `DISCORD_WEBHOOK_URL` in `.env`):
```bash
PYTHONPATH=src python src/main.py --post
```

**Flags:**
- `--dry-run` — Print digest to terminal
- `--no-llm` — Skip AI summarization (fallback format)
- `--limit N` — Limit number of feed items fetched
- `--output FILE` — Write digest to file
- `--post` — Post to Discord (only if webhook URL is set)

Default behavior (no flags) does nothing visible—use `--dry-run` or `--post`.

## Development

**Run tests:**
```bash
make test
```

**Lint code:**
```bash
make lint
```

**Quick test run:**
```bash
make dry-run
```

## Configuration

**Feed sources** are in `config/feeds.json`. Edit to add/remove RSS feeds.

**Environment variables** (`.env`):
- `GH_MODELS_TOKEN` — GitHub Personal Access Token for Models API
- `MODELS_ENDPOINT` — API endpoint (default shown in `.env.example`)
- `MODEL_NAME` — Model to use (e.g., `gpt-4o-mini`)
- `DISCORD_WEBHOOK_URL` — Discord webhook for posting (optional)

## GitHub Actions

The workflow (`.github/workflows/daily-digest.yml`) runs daily at **7:00 AM America/Chicago** and supports manual dispatch.

**Setup:**
1. Push code to GitHub
2. Add repository secrets:
   - `GH_MODELS_TOKEN`
   - `MODELS_ENDPOINT`
   - `MODEL_NAME`
   - `DISCORD_WEBHOOK_URL`
3. Enable Actions in repo settings
4. Test manually: Actions tab → Daily Digest → Run workflow

The workflow runs the same command you test locally:
```bash
python src/main.py --post
```

## Digest Format

The AI generates:
- 📰 Title with emoji
- 2-4 paragraph narrative summary of key themes
- 🔗 Key Stories section with source-attributed links

Example:
```markdown
📰 Daily National News Digest

[Narrative summary paragraphs...]

🔗 Key Stories
- Story title — [NPR](link)
- Another story — [AP](link)
```

If AI fails or is disabled (`--no-llm`), falls back to organized headline bullets.

## Project Structure

```
.
├── src/
│   ├── main.py         # CLI entrypoint
│   ├── feeds.py        # RSS fetching
│   ├── clean.py        # HTML/text normalization
│   ├── dedupe.py       # Deduplication (90%+ similarity)
│   ├── digest.py       # Digest builder with source diversity
│   ├── llm.py          # GitHub Models client (OpenAI-compatible)
│   └── discord.py      # Discord webhook posting with chunking
├── config/
│   └── feeds.json      # RSS feed URLs
├── tests/              # pytest tests
├── .github/workflows/  # GitHub Actions
├── .env.example        # Environment template
├── requirements.txt
├── Makefile
├── README.md
└── .gitignore
```

## Development Continuation

A `.copilot-instructions` file is included (in `.gitignore`) to help GitHub Copilot understand project context for future development. It documents architecture, design patterns, environment setup, and known issues.

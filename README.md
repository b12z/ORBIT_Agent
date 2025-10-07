# ORBIT Agent

An automated reply agent for X (Twitter) with two modes:
- Manual / Telegram approval
- Autopilot (API-based discovery → draft with LLM → optional post)

## Features
- X API OAuth1 posting and fetching (`src/poster.py`, `src/x_fetch.py`)
- Recent search via X API (`src/x_search.py`) with KOL filter (followers ≥ 10k, replies ≥ 10, recent)
- Playwright scraper as fallback (`src/scraper.py`)
- LLM drafting with OpenAI (`src/reply_writer.py`) — adaptive tone, keyword anchoring, ≤200 chars
- Telegram approval flow (`src/telegram_bot.py`, `src/tele_router.py`)
- One-off runners: `src/dev_once.py`, `src/smoke_scrape.py`

## Environment
Create `.env.local` with:
```
OPENAI_API_KEY=...
API_KEY=...
API_KEY_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_SECRET=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
TOPICS=web3
```

## Local quickstart
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

- Manual single tweet (with approval):
```
PYTHONPATH=. MANUAL_TWEET_ID=1234567890 python -m src.main
```

- Autopilot dry-run (discover via API, draft only):
```
PYTHONPATH=. TOPICS="web3" DRY_RUN=true MAX_POSTS=1 python -m src.smoke_scrape
```

- Autopilot post once (no approval):
```
PYTHONPATH=. TOPICS="web3" DRY_RUN=false MAX_POSTS=1 python -m src.smoke_scrape
```

- Telegram router one-shot:
```
PYTHONPATH=. python -m src.tele_cli
```

## GitHub Actions
- `.github/workflows/schedule-3x.yml` runs every 8 hours and posts once via `src/smoke_scrape`.
- Set repo Secrets: `OPENAI_API_KEY`, `X_API_KEY`, `X_API_KEY_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`.
- Optional repo Var: `TOPICS`.

## Notes
- API search preferred; scraper kept as fallback (UI may require auth).
- Rate limiting (429) may occur; consider adding backoff or adjusting frequency.
- `state.json` tracks replied tweet IDs; rotate as needed.

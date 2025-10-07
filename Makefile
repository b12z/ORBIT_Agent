.PHONY: tele smoke smoke-dry manual

# Helper to activate venv if present
define ACTIVATE
if [ -d .venv ]; then . .venv/bin/activate; fi;
endef

tele:
	@$(ACTIVATE) PYTHONPATH=. python -m src.tele_cli

# Post once (no approval). Override TOPICS/ MAX_POSTS as needed
smoke:
	@$(ACTIVATE) TOPICS?=web3; DRY_RUN=false; MAX_POSTS?=1; \
	PYTHONPATH=. TOPICS=$$TOPICS DRY_RUN=$$DRY_RUN MAX_POSTS=$$MAX_POSTS python -m src.smoke_scrape

# Dry run discovery + draft (no post)
smoke-dry:
	@$(ACTIVATE) TOPICS?=web3; DRY_RUN=true; MAX_POSTS?=1; \
	PYTHONPATH=. TOPICS=$$TOPICS DRY_RUN=$$DRY_RUN MAX_POSTS=$$MAX_POSTS python -m src.smoke_scrape

# Manual single tweet (with Telegram approval). Requires MANUAL_TWEET_ID
manual:
	@$(ACTIVATE) \
	if [ -z "$$MANUAL_TWEET_ID" ]; then echo "Set MANUAL_TWEET_ID"; exit 1; fi; \
	PYTHONPATH=. MANUAL_TWEET_ID=$$MANUAL_TWEET_ID python -m src.main



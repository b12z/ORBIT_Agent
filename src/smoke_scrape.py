import os
from dotenv import load_dotenv


def run_scrape_test(topics: str = "web3", dry_run: bool = True, max_posts: int = 1):
    """Load env and run a single scrape/draft cycle for quick testing."""
    load_dotenv('.env.local')
    os.environ['TOPICS'] = topics
    os.environ['DRY_RUN'] = 'true' if dry_run else 'false'
    os.environ['MAX_POSTS'] = str(max_posts)

    from src.dev_once import dev_once
    dev_once()


if __name__ == "__main__":
    # Allow overrides via env when calling as a module
    topics = os.getenv('TOPICS', 'web3')
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
    max_posts = int(os.getenv('MAX_POSTS', '1'))
    run_scrape_test(topics=topics, dry_run=dry_run, max_posts=max_posts)

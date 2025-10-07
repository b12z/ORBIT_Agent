import os, time
from typing import List, Dict
from .scraper import search_posts
from .x_search import search_recent_topics, search_kol_recent
from .reply_writer import write_reply
from .poster import post_tweet

def dev_once():
    topics_env = os.getenv("TOPICS", "web3 growth,KOL,gaming")
    topics = [t.strip() for t in topics_env.split(",") if t.strip()]
    max_posts = int(os.getenv("MAX_POSTS", "1"))
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

    print(f"[dev] topics={topics} dry_run={dry_run} max_posts={max_posts}")

    # Try API-based search first for reliability; fallback to Playwright scraper
    posts: List[Dict] = search_kol_recent(topics=topics, limit=1, hours=12)
    if not posts:
        posts = search_recent_topics(topics=topics, limit_per_topic=3)
    if not posts:
        posts = search_posts(topics=topics)
    print(f"[dev] discovered {len(posts)} posts")
    if not posts:
        return

    count = 0
    for p in posts:
        tid = p.get("id")
        txt = p.get("text", "").strip().replace("\n", " ")
        if not tid or not txt:
            continue
        print(f"\n[dev] candidate id={tid}\n[dev] text={txt[:240]}{'…' if len(txt)>240 else ''}")
        try:
            reply = write_reply(txt)
            print(f"[dev] draft → {reply}")
            if not dry_run:
                post_tweet(reply, in_reply_to=tid)
                print("[dev] posted ✅")
                time.sleep(2)
            count += 1
            if count >= max_posts:
                break
        except Exception as e:
            print("[dev] error:", e)

if __name__ == "__main__":
    dev_once()

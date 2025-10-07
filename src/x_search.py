import os
import requests
from typing import List, Dict
from datetime import datetime, timezone, timedelta
import time
from requests_oauthlib import OAuth1


def _auth() -> OAuth1:
    return OAuth1(
        os.getenv("API_KEY"),
        os.getenv("API_KEY_SECRET"),
        os.getenv("X_ACCESS_TOKEN"),
        os.getenv("X_ACCESS_SECRET"),
    )


def search_recent_for_topic(topic: str, limit: int = 5) -> List[Dict]:
    """Search recent tweets for a topic using X API v2. Returns standardized posts."""
    base = "https://api.twitter.com/2/tweets/search/recent"
    # Build query similar to UI query
    query = f"{topic} -is:reply -is:retweet"
    params = {
        "query": query,
        "max_results": str(max(10, min(100, limit * 3))),  # overfetch a bit
        "tweet.fields": "author_id,text,created_at,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,verified,public_metrics",
    }
    for i in range(3):
        r = requests.get(base, auth=_auth(), params=params, timeout=20)
        if r.status_code != 429:
            break
        time.sleep(2 * (i + 1))
    if r.status_code != 200:
        # Best-effort fallback
        try:
            print("x_search error:", r.status_code, r.json())
        except Exception:
            print("x_search error:", r.status_code, r.text)
        return []

    data = r.json() or {}
    tweets = data.get("data", [])
    users = {u.get("id"): u for u in (data.get("includes", {}).get("users", []) or [])}

    results: List[Dict] = []
    for t in tweets:
        tid = t.get("id")
        txt = (t.get("text") or "").strip()
        uid = t.get("author_id")
        u = users.get(uid, {})
        handle = u.get("username") or ""
        verified = bool(u.get("verified"))
        followers = (u.get("public_metrics") or {}).get("followers_count")
        if not (tid and handle and txt):
            continue
        results.append({
            "id": tid,
            "tweet_id": tid,
            "handle": handle,
            "text": txt,
            "url": f"https://twitter.com/{handle}/status/{tid}",
            "verified": verified,
            "followers": followers,
        })
        if len(results) >= limit:
            break
    return results


def search_recent_topics(topics: List[str], limit_per_topic: int = 5) -> List[Dict]:
    all_results: List[Dict] = []
    for topic in topics:
        try:
            all_results.extend(search_recent_for_topic(topic, limit=limit_per_topic))
        except Exception as e:
            print(f"x_search topic error for '{topic}':", e)
    # Deduplicate by id
    seen = set()
    unique: List[Dict] = []
    for p in all_results:
        pid = p.get("id")
        if pid and pid not in seen:
            seen.add(pid)
            unique.append(p)
    return unique


def search_kol_recent(topics: List[str], limit: int = 1, hours: int = 12) -> List[Dict]:
    """Single-call KOL-oriented recent search with server-side expansions and client filters.
    Filters: followers >= 10000, reply_count >= 10, created within hours window, includes KOL terms.
    Returns up to `limit` standardized posts.
    """
    base = "https://api.twitter.com/2/tweets/search/recent"
    if not topics:
        topics = ["web3"]
    topics_clause = " OR ".join([t.strip() for t in topics if t.strip()])
    kol_clause = 'KOL OR "key opinion leader" OR influencer'
    query = f"({topics_clause}) ({kol_clause}) -is:reply -is:retweet"
    params = {
        "query": query,
        "max_results": "25",
        "tweet.fields": "author_id,text,created_at,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,verified,public_metrics",
    }
    for i in range(3):
        r = requests.get(base, auth=_auth(), params=params, timeout=20)
        if r.status_code != 429:
            break
        time.sleep(2 * (i + 1))
    if r.status_code != 200:
        try:
            print("x_search KOL error:", r.status_code, r.json())
        except Exception:
            print("x_search KOL error:", r.status_code, r.text)
        return []
    data = r.json() or {}
    tweets = data.get("data", [])
    users = {u.get("id"): u for u in (data.get("includes", {}).get("users", []) or [])}
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=max(1, hours))

    results: List[Dict] = []
    for t in tweets:
        tid = t.get("id")
        txt = (t.get("text") or "").strip()
        uid = t.get("author_id")
        u = users.get(uid, {})
        handle = u.get("username") or ""
        verified = bool(u.get("verified"))
        followers = (u.get("public_metrics") or {}).get("followers_count") or 0
        pm = t.get("public_metrics") or {}
        reply_count = pm.get("reply_count") or 0
        created_at = t.get("created_at")
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else None
        except Exception:
            created_dt = None

        if not (tid and handle and txt):
            continue
        if followers < 10000:
            continue
        if reply_count < 10:
            continue
        if created_dt and created_dt < cutoff:
            continue

        results.append({
            "id": tid,
            "tweet_id": tid,
            "handle": handle,
            "text": txt,
            "url": f"https://twitter.com/{handle}/status/{tid}",
            "verified": verified,
            "followers": followers,
        })
        if len(results) >= max(1, limit):
            break
    return results



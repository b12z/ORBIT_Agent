import os
import requests
from typing import List, Dict
from datetime import datetime, timezone, timedelta
import time
from requests_oauthlib import OAuth1


def _auth() -> OAuth1:
    """Create OAuth1 authentication object. Validates credentials are present."""
    api_key = os.getenv("API_KEY")
    api_key_secret = os.getenv("API_KEY_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_secret = os.getenv("X_ACCESS_SECRET")
    
    # Check for missing credentials
    missing = []
    if not api_key:
        missing.append("API_KEY")
    if not api_key_secret:
        missing.append("API_KEY_SECRET")
    if not access_token:
        missing.append("X_ACCESS_TOKEN")
    if not access_secret:
        missing.append("X_ACCESS_SECRET")
    
    if missing:
        raise ValueError(
            f"Missing required X API credentials: {', '.join(missing)}. "
            f"Please set these environment variables or add them to .env.local"
        )
    
    return OAuth1(api_key, api_key_secret, access_token, access_secret)


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
        print(f"⚠️  Rate limited (429), retrying in {2 * (i + 1)}s...")
        time.sleep(2 * (i + 1))
    
    if r.status_code != 200:
        # Detailed error reporting
        try:
            error_data = r.json()
            print(f"❌ x_search error: {r.status_code} {error_data}")
            
            # Provide helpful context for common errors
            if r.status_code == 401:
                print("   → Authentication failed. Check your X API credentials.")
                print("   → Run: python -m src.validate_x_auth")
            elif r.status_code == 403:
                print("   → Access forbidden. Check API access level and permissions.")
            elif r.status_code == 429:
                reset_time = r.headers.get("x-rate-limit-reset", "unknown")
                print(f"   → Rate limit exceeded. Resets at: {reset_time}")
        except Exception:
            print(f"❌ x_search error: {r.status_code} {r.text[:200]}")
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


def search_kol_recent(topics: List[str], limit: int = 1, hours: int = 12, min_replies: int = 10, min_faves: int = 10) -> List[Dict]:
    """Single-call KOL-oriented recent search with server-side engagement filters.
    
    Searches for tweets matching topics + KOL terms with minimum engagement thresholds.
    Supports cashtags (e.g., $POL), hashtags, and keywords.
    
    Args:
        topics: List of search terms (can include cashtags like $POL, hashtags, keywords)
        limit: Maximum number of results to return
        hours: Time window in hours (tweets must be within this timeframe)
        min_replies: Minimum number of replies required (default: 10)
        min_faves: Minimum number of favorites/likes required (default: 10)
    
    Returns:
        List of standardized post dictionaries
    """
    base = "https://api.twitter.com/2/tweets/search/recent"
    if not topics:
        topics = ["web3"]
    
    # Build topic clause - support multiple terms
    topics_clause = " OR ".join([t.strip() for t in topics if t.strip()])
    
    # KOL terms
    kol_clause = 'KOL OR "key opinion leader" OR influencer'
    
    # Build query with engagement filters using X API v2 operators
    # Format: (topics) (KOL terms) min_replies:N min_faves:N -is:reply -is:retweet
    query = f"({topics_clause}) ({kol_clause}) min_replies:{min_replies} min_faves:{min_faves} -is:reply -is:retweet"
    
    params = {
        "query": query,
        "max_results": "25",
        "tweet.fields": "author_id,text,created_at,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,verified,public_metrics",
    }
    
    print(f"🔍 Search query: {query}")
    for i in range(3):
        r = requests.get(base, auth=_auth(), params=params, timeout=20)
        if r.status_code != 429:
            break
        print(f"⚠️  Rate limited (429), retrying in {2 * (i + 1)}s...")
        time.sleep(2 * (i + 1))
    
    if r.status_code != 200:
        # Detailed error reporting
        try:
            error_data = r.json()
            print(f"❌ x_search KOL error: {r.status_code} {error_data}")
            
            # Provide helpful context for common errors
            if r.status_code == 401:
                print("   → Authentication failed. Check your X API credentials.")
                print("   → Run: python -m src.validate_x_auth")
            elif r.status_code == 403:
                print("   → Access forbidden. Check API access level and permissions.")
            elif r.status_code == 429:
                reset_time = r.headers.get("x-rate-limit-reset", "unknown")
                print(f"   → Rate limit exceeded. Resets at: {reset_time}")
        except Exception:
            print(f"❌ x_search KOL error: {r.status_code} {r.text[:200]}")
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
        like_count = pm.get("like_count") or 0
        created_at = t.get("created_at")
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else None
        except Exception:
            created_dt = None

        # Basic validation
        if not (tid and handle and txt):
            continue
        
        # Client-side filters as backup validation (server should already filter these)
        # Keep follower threshold since there's no server-side operator for it
        if followers < 10000:
            continue
        
        # Double-check engagement metrics match our requirements
        if reply_count < min_replies:
            continue
        if like_count < min_faves:
            continue
        
        # Time window filter
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
            "reply_count": reply_count,
            "like_count": like_count,
        })
        if len(results) >= max(1, limit):
            break
    
    print(f"✅ Found {len(results)} posts matching criteria (followers>=10k, replies>={min_replies}, likes>={min_faves})")
    return results



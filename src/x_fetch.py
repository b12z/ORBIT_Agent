import os, requests
from requests_oauthlib import OAuth1


def _auth():
    return OAuth1(
        os.getenv("API_KEY"),
        os.getenv("API_KEY_SECRET"),
        os.getenv("X_ACCESS_TOKEN"),
        os.getenv("X_ACCESS_SECRET"),
    )


def get_tweet_text(tweet_id: str) -> str:
    """Return the tweet text ('' if not found)."""
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    params = {"tweet.fields": "text,lang,conversation_id"}
    r = requests.get(url, auth=_auth(), params=params, timeout=15)
    if r.status_code == 200 and r.json().get("data"):
        return (r.json()["data"].get("text") or "")[:1000]
    return ""

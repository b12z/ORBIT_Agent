import os, requests, json
from requests_oauthlib import OAuth1


def _auth():
    from requests_oauthlib import OAuth1
    return OAuth1(
        os.getenv("API_KEY"),
        os.getenv("API_KEY_SECRET"),
        os.getenv("X_ACCESS_TOKEN"),
        os.getenv("X_ACCESS_SECRET"),
    )


def post_tweet(text: str, in_reply_to: str | None = None) -> dict:
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": text}
    if in_reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": in_reply_to}
    r = requests.post(url, auth=_auth(), json=payload)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    if r.status_code not in (200, 201):
        print("X error:", r.status_code, data)
    return data

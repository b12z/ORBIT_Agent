import os
import sys
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import modules
from src.scraper import search_posts  
from src.x_search import search_recent_topics
from src.telegram_bot import send_drafts  
# from src.poster import post_tweet  # Commented out for now

MANUAL_TWEET_ID = os.getenv("MANUAL_TWEET_ID")


def load_state() -> List[str]:
    """Load replied tweet IDs from state.json"""
    try:
        with open('state.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_state(tweet_id: str) -> None:
    """Append tweet ID to state.json"""
    replied_ids = load_state()
    replied_ids.append(tweet_id)
    
    with open('state.json', 'w') as f:
        json.dump(replied_ids, f, indent=2)


def main():
    """Main workflow"""
    print("🚀 ORBIT Agent starting...")
    
    # Load environment variables
    load_dotenv('.env.local')
    
    # Read TOPICS from env or use default
    topics_str = os.getenv('TOPICS', 'Web3 growth,KOL marketing,Web3 gaming')
    topics = [topic.strip() for topic in topics_str.split(',')]
    print(f"📋 Topics to search: {topics}")
    
    # Search for posts
    print("🔍 Searching for posts...")
    if MANUAL_TWEET_ID:
        from src.x_fetch import get_tweet_text
        from src.reply_writer import write_reply
        from src.telegram_bot import send_drafts
        from src.poster import post_tweet

        tweet_text = get_tweet_text(MANUAL_TWEET_ID) or "No text found for this tweet."
        draft_text = write_reply(tweet_text)

        print("Fetched post text:\n", tweet_text, "\n")
        print("Draft reply:\n", draft_text, "\n")

        approved = send_drafts([{"tweet_id": MANUAL_TWEET_ID, "author": "manual", "text": draft_text}])
        print("Approved:", approved)

        if approved.get("action") == "approve":
            resp = post_tweet(approved["text"], in_reply_to=MANUAL_TWEET_ID)
            print("Posted:", resp)
        else:
            print("Skipped manual reply.")
        sys.exit(0)

    try:
        # Prefer API-based discovery; fallback to Playwright if empty
        posts = search_recent_topics(topics, limit_per_topic=2)
        if not posts:
            posts = search_posts(topics, limit=3)
        print(f"✅ Found {len(posts)} posts")
        
        if not posts:
            print("❌ No posts found to reply to")
            return
            
    except Exception as e:
        print(f"❌ Error searching posts: {e}")
        return
    
    # Load existing replied tweet IDs to avoid duplicates
    replied_ids = load_state()
    print(f"📝 Already replied to {len(replied_ids)} tweets")
    
    # Generate candidate replies
    print("🤖 Generating reply candidates...")
    candidates = []
    
    for post in posts:
        tweet_id = post.get('tweet_id')
        
        # Skip if we've already replied to this tweet
        if tweet_id in replied_ids:
            print(f"⏭️ Skipping {tweet_id} (already replied)")
            continue
            
        try:
            # Use the same LLM writer as manual flow
            from src.reply_writer import write_reply
            reply_text = write_reply(post.get('text', ''))
            
            candidate = {
                "tweet_id": tweet_id,
                "author": post.get('handle') or post.get('author', 'unknown'),
                "text": reply_text
            }
            candidates.append(candidate)
            print(f"✅ Generated reply for @{candidate['author']}: {reply_text[:50]}...")
            
        except Exception as e:
            print(f"❌ Error generating reply for {tweet_id}: {e}")
            continue
    
    if not candidates:
        print("❌ No new candidates to review")
        return
    
    print(f"📝 {len(candidates)} candidates ready for review")
    
    # Send drafts for approval
    print("📤 Sending drafts to Telegram for approval...")
    try:
        approval_result = send_drafts(candidates)
        print(f"📋 Approval result: {approval_result}")

        # Post immediately if approved; otherwise print Skipped and exit
        approved = approval_result
        from src.poster import post_tweet
        if approved.get("action") == "approve":
            resp = post_tweet(approved["text"], in_reply_to=approved["tweet_id"])
            print("Posted:", resp)
        else:
            print("Skipped.")
            return
            
    except Exception as e:
        print(f"❌ Error sending drafts: {e}")
        return
    
    # After approval, just print what would be posted
    approved_text = approval_result.get('text')
    approved_tweet_id = approval_result.get('tweet_id')
    
    if not approved_text or not approved_tweet_id:
        print("❌ Missing approval data")
        return
    
    print("Would post:", approved_text)
    
    # Append approved tweet_id to state.json
    save_state(approved_tweet_id)
    print("State updated.")


if __name__ == "__main__":
    main()
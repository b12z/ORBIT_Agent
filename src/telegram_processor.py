"""
Telegram Message Processor
Handles the two-phase approval process:
1. Generate drafts and save for approval
2. Check approved drafts and post them
"""
import os
import json
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import modules
from src.scraper import search_posts  
from src.x_search import search_recent_topics
from src.telegram_bot import send_drafts, notify_error
from src.poster import post_tweet

load_dotenv()

PENDING_FILE = "pending_approvals.json"
REPLIED_FILE = "replied_tweets.json"


def load_pending() -> List[Dict]:
    """Load pending approvals from file."""
    try:
        with open(PENDING_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_pending(pending: List[Dict]) -> None:
    """Save pending approvals to file."""
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=2)


def load_replied() -> List[str]:
    """Load replied tweet IDs from file."""
    try:
        with open(REPLIED_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_replied(tweet_id: str) -> None:
    """Add tweet ID to replied list."""
    replied = load_replied()
    if tweet_id not in replied:
        replied.append(tweet_id)
        with open(REPLIED_FILE, 'w') as f:
            json.dump(replied, f, indent=2)


def process_new_messages():
    """Phase 1: Generate drafts for new messages and save for approval."""
    print("🔍 Phase 1: Processing new messages...")
    
    # Get topics from environment
    topics_str = os.getenv('TOPICS', 'Web3 growth,KOL marketing,Web3 gaming')
    topics = [topic.strip() for topic in topics_str.split(',')]
    print(f"📋 Topics: {topics}")
    
    # Search for posts
    try:
        posts = search_recent_topics(topics, limit_per_topic=2)
        if not posts:
            posts = search_posts(topics, limit=3)
        print(f"✅ Found {len(posts)} posts")
        
        if not posts:
            print("❌ No posts found")
            return
            
    except Exception as e:
        print(f"❌ Error searching posts: {e}")
        notify_error(f"Search failure: {e}")
        return
    
    # Load existing data
    replied_ids = load_replied()
    pending = load_pending()
    
    print(f"📝 Already replied to {len(replied_ids)} tweets")
    print(f"📝 {len(pending)} pending approvals")
    
    # Generate new candidates
    new_candidates = []
    for post in posts:
        tweet_id = post.get('tweet_id')
        
        # Skip if already replied or pending
        if tweet_id in replied_ids or any(p['tweet_id'] == tweet_id for p in pending):
            print(f"⏭️ Skipping {tweet_id} (already processed)")
            continue
            
        try:
            from src.reply_writer import write_reply
            reply_text = write_reply(post.get('text', ''))
            
            candidate = {
                "tweet_id": tweet_id,
                "author": post.get('handle') or post.get('author', 'unknown'),
                "text": reply_text,
                "original_text": post.get('text', ''),
                "url": post.get('url', ''),
                "created_at": time.time()
            }
            new_candidates.append(candidate)
            print(f"✅ Generated reply for @{candidate['author']}: {reply_text[:50]}...")
            
        except Exception as e:
            print(f"❌ Error generating reply for {tweet_id}: {e}")
            continue
    
    if not new_candidates:
        print("❌ No new candidates")
        return
    
    # Send for approval and save pending
    print(f"📤 Sending {len(new_candidates)} drafts for approval...")
    try:
        approval_result = send_drafts(new_candidates)
        print(f"📋 Approval result: {approval_result}")
        
        if approval_result.get("action") == "approve":
            # Save approved draft for next run
            approved_draft = {
                "tweet_id": approval_result["tweet_id"],
                "text": approval_result["text"],
                "author": new_candidates[0]["author"],
                "original_text": new_candidates[0]["original_text"],
                "url": new_candidates[0]["url"],
                "approved_at": time.time()
            }
            pending.append(approved_draft)
            save_pending(pending)
            print(f"✅ Approved draft saved for next run")
        else:
            print("⏭️ Draft not approved, skipping")
            
    except Exception as e:
        print(f"❌ Error in approval process: {e}")
        notify_error(f"Approval failure: {e}")


def process_approved_drafts():
    """Phase 2: Check approved drafts and post them."""
    print("🚀 Phase 2: Processing approved drafts...")
    
    pending = load_pending()
    if not pending:
        print("📭 No pending approvals")
        return
    
    print(f"📋 Found {len(pending)} pending approvals")
    
    for draft in pending[:1]:  # Process one at a time
        try:
            print(f"📤 Posting approved draft for @{draft['author']}")
            print(f"   Original: {draft['original_text'][:100]}...")
            print(f"   Reply: {draft['text']}")
            
            resp = post_tweet(draft['text'], in_reply_to=draft['tweet_id'])
            print(f"✅ Posted successfully: {resp}")
            
            # Mark as replied and remove from pending
            save_replied(draft['tweet_id'])
            pending.remove(draft)
            save_pending(pending)
            
            # Notify success
            notify_error(f"✅ Posted reply to @{draft['author']}")
            
        except Exception as e:
            print(f"❌ Error posting draft: {e}")
            notify_error(f"Post failure: {e}")
            continue


def main():
    """Main processor - handles both phases in one session."""
    print("🚀 ORBIT Telegram Processor starting...")
    
    # Phase 1: Process approved drafts first
    pending = load_pending()
    if pending:
        print(f"📋 Phase 1: Found {len(pending)} pending approvals, processing...")
        process_approved_drafts()
    else:
        print("📭 Phase 1: No pending approvals")
    
    # Phase 2: Process new messages
    print("\n🔍 Phase 2: Processing new messages...")
    process_new_messages()
    
    print("\n✅ Processing complete - both phases done in one session")


if __name__ == "__main__":
    main()

"""
Safe Testing Script for X API Scraping
Tests the scraping flow with minimal API calls and mock data option.
"""
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv


# Mock data for testing without API calls
MOCK_POSTS = [
    {
        "id": "1234567890123456789",
        "tweet_id": "1234567890123456789",
        "handle": "testuser1",
        "text": "Excited about the future of web3 and decentralized systems! #web3",
        "url": "https://twitter.com/testuser1/status/1234567890123456789",
        "verified": True,
        "followers": 15000,
    },
    {
        "id": "9876543210987654321",
        "tweet_id": "9876543210987654321",
        "handle": "testuser2",
        "text": "KOL marketing strategies are evolving rapidly in the crypto space.",
        "url": "https://twitter.com/testuser2/status/9876543210987654321",
        "verified": False,
        "followers": 25000,
    }
]


def test_with_mocks(topics: List[str], max_posts: int = 1):
    """Test the flow with mock data instead of real API calls."""
    print("\n" + "=" * 60)
    print("🧪 MOCK MODE - Testing with fake data")
    print("=" * 60)
    print(f"Topics: {topics}")
    print(f"Max posts: {max_posts}")
    
    # Simulate discovery
    posts = MOCK_POSTS[:max_posts]
    print(f"\n✅ Discovered {len(posts)} mock posts")
    
    # Test reply generation
    from src.reply_writer import write_reply
    
    for i, post in enumerate(posts, 1):
        print(f"\n--- Post {i}/{len(posts)} ---")
        print(f"Handle: @{post['handle']}")
        print(f"Text: {post['text'][:100]}...")
        print(f"URL: {post['url']}")
        
        try:
            reply = write_reply(post['text'])
            print(f"\n✅ Generated reply:\n   {reply}")
        except Exception as e:
            print(f"❌ Error generating reply: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Mock test complete")
    print("=" * 60)


def test_minimal_api_call(topics: List[str], max_posts: int = 1):
    """
    Test with a SINGLE minimal API call to verify it works.
    This uses the least amount of rate limit quota possible.
    """
    print("\n" + "=" * 60)
    print("🔬 MINIMAL API TEST - Single request only")
    print("=" * 60)
    print(f"Topics: {topics}")
    print(f"Max posts: {max_posts}")
    
    from src.x_search import search_kol_recent
    
    print("\n⚡ Making ONE API call to search_kol_recent...")
    print("   (This tests auth and consumes minimal quota)")
    
    try:
        # Limit to absolute minimum
        posts = search_kol_recent(topics=topics, limit=1, hours=12)
        
        if posts:
            print(f"\n✅ API call successful! Found {len(posts)} post(s)")
            
            for i, post in enumerate(posts, 1):
                print(f"\n--- Post {i} ---")
                print(f"ID: {post.get('id')}")
                print(f"Handle: @{post.get('handle')}")
                print(f"Text: {post.get('text', '')[:100]}...")
                print(f"Followers: {post.get('followers')}")
                print(f"URL: {post.get('url')}")
        else:
            print("\n⚠️  API call succeeded but returned no posts")
            print("   This could mean:")
            print("   - No tweets match the filters (10k+ followers, 10+ replies)")
            print("   - Topics too restrictive")
            print("   - Time window (12 hours) had no matching content")
        
        print("\n✅ API authentication is working!")
        
    except Exception as e:
        print(f"\n❌ API call failed: {e}")
        print("\nTroubleshooting:")
        print("   1. Run: python -m src.validate_x_auth")
        print("   2. Check your credentials in GitHub Secrets")
        print("   3. Verify X API access level (need v2 access)")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Minimal test complete")
    print("=" * 60)


def test_full_flow_limited(topics: List[str], max_posts: int = 1, dry_run: bool = True):
    """
    Test the full flow but with strict limits.
    Only makes the minimum necessary API calls.
    """
    print("\n" + "=" * 60)
    print("🚀 LIMITED FULL FLOW TEST")
    print("=" * 60)
    print(f"Topics: {topics}")
    print(f"Max posts: {max_posts}")
    print(f"Dry run (no posting): {dry_run}")
    
    from src.x_search import search_kol_recent, search_recent_topics
    from src.scraper import search_posts
    from src.reply_writer import write_reply
    
    # Try API methods first (most efficient)
    print("\n1️⃣ Trying KOL search (1 API call)...")
    posts = search_kol_recent(topics=topics, limit=1, hours=12)
    
    if not posts:
        print("   No KOL posts found, trying regular search...")
        posts = search_recent_topics(topics=topics, limit_per_topic=1)
    
    if not posts:
        print("   ⚠️  API searches returned nothing")
        print("   Skipping Playwright scraper to avoid rate limits")
        print("\n   Recommendation: Use broader topics or relax filters")
        return
    
    print(f"\n✅ Discovered {len(posts)} post(s)")
    
    # Process posts
    for i, post in enumerate(posts[:max_posts], 1):
        tid = post.get("id")
        txt = post.get("text", "").strip()
        
        if not tid or not txt:
            continue
        
        print(f"\n--- Post {i} ---")
        print(f"ID: {tid}")
        print(f"Handle: @{post.get('handle')}")
        print(f"Text: {txt[:150]}...")
        
        try:
            reply = write_reply(txt)
            print(f"\n✅ Draft reply:\n   {reply}")
            
            if not dry_run:
                print("   ⚠️  Would post here (dry_run=False)")
                # Actual posting would happen here
            else:
                print("   ℹ️  Dry run - not posting")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Limited flow test complete")
    print("=" * 60)


def main():
    """Main test runner with safe options."""
    load_dotenv('.env.local')
    
    # Parse test mode from environment or args
    test_mode = os.getenv("TEST_MODE", "validate").lower()
    topics = [t.strip() for t in os.getenv("TOPICS", "web3").split(",") if t.strip()]
    max_posts = int(os.getenv("MAX_POSTS", "1"))
    
    print("=" * 60)
    print("Safe X API Testing Tool")
    print("=" * 60)
    print(f"\nTest mode: {test_mode}")
    print(f"Topics: {topics}")
    print(f"Max posts: {max_posts}")
    
    if test_mode == "validate":
        print("\n📋 Mode: VALIDATE")
        print("   Running authentication validation only...")
        from src.validate_x_auth import main as validate_main
        validate_main()
        
    elif test_mode == "mock":
        print("\n🧪 Mode: MOCK")
        print("   Testing flow with fake data (no API calls)...")
        test_with_mocks(topics, max_posts)
        
    elif test_mode == "minimal":
        print("\n🔬 Mode: MINIMAL")
        print("   Testing with ONE API call only...")
        test_minimal_api_call(topics, max_posts)
        
    elif test_mode == "limited":
        print("\n🚀 Mode: LIMITED")
        print("   Testing full flow with minimal API usage...")
        dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        test_full_flow_limited(topics, max_posts, dry_run)
        
    else:
        print(f"\n❌ Unknown test mode: {test_mode}")
        print("\nAvailable modes:")
        print("  validate - Check credentials only (recommended first step)")
        print("  mock     - Test flow with fake data (no API calls)")
        print("  minimal  - Single API call to verify auth")
        print("  limited  - Full flow with minimal API usage")
        print("\nUsage: TEST_MODE=validate python -m src.test_scrape_safe")
        sys.exit(1)


if __name__ == "__main__":
    main()


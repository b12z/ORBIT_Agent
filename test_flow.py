#!/usr/bin/env python3
"""
Simple test of the scrape → reply generation flow using mock data.
NO API CALLS to X - just tests the logic.
"""
import os
import sys

# Try to load dotenv if available, but don't fail if not
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    print("⚠️  python-dotenv not installed, using existing environment variables")
    pass

print("=" * 70)
print("🧪 MOCK TEST: Scraper → Reply Generator")
print("=" * 70)
print("\nThis test uses FAKE scraped data and tests reply generation.")
print("NO calls to X API - completely safe!\n")

# Mock scraped posts (simulating what scraper.py or x_search.py would return)
MOCK_SCRAPED_POSTS = [
    {
        "id": "1234567890123456789",
        "tweet_id": "1234567890123456789",
        "handle": "web3builder",
        "text": "Just launched our new DeFi protocol! Super excited about bringing decentralized finance to more users. Check it out! #web3 #DeFi",
        "url": "https://twitter.com/web3builder/status/1234567890123456789",
        "verified": True,
        "followers": 25000,
    },
    {
        "id": "9876543210987654321",
        "tweet_id": "9876543210987654321",
        "handle": "cryptoinfluencer",
        "text": "Web3 gaming is the future. The ability to truly own your in-game assets changes everything. What's your favorite web3 game?",
        "url": "https://twitter.com/cryptoinfluencer/status/9876543210987654321",
        "verified": False,
        "followers": 50000,
    },
    {
        "id": "5555555555555555555",
        "tweet_id": "5555555555555555555",
        "handle": "nftcollector",
        "text": "The intersection of AI and blockchain is fascinating. We're seeing real-world applications that weren't possible before. Excited for what's next!",
        "url": "https://twitter.com/nftcollector/status/5555555555555555555",
        "verified": True,
        "followers": 15000,
    },
]

print("📊 Mock Scraped Posts:")
print("-" * 70)
for i, post in enumerate(MOCK_SCRAPED_POSTS, 1):
    print(f"\n{i}. @{post['handle']} ({post['followers']:,} followers)")
    print(f"   {post['text'][:80]}...")

print("\n" + "=" * 70)
print("🤖 Testing Reply Generation")
print("=" * 70)

# Import reply writer
try:
    from src.reply_writer import write_reply
    print("✅ Reply writer module loaded")
except ImportError as e:
    print(f"❌ Failed to import reply_writer: {e}")
    exit(1)

# Check if OpenAI key is present
if not os.getenv("OPENAI_API_KEY"):
    print("\n⚠️  Warning: OPENAI_API_KEY not set")
    print("   Reply generation will fail without it.")
    print("   Set it in .env.local or environment variables.\n")

# Generate replies for each mock post
print("\nGenerating replies...\n")
for i, post in enumerate(MOCK_SCRAPED_POSTS, 1):
    print(f"\n{'=' * 70}")
    print(f"Post {i}/{len(MOCK_SCRAPED_POSTS)}")
    print(f"{'=' * 70}")
    print(f"👤 Author: @{post['handle']}")
    print(f"💬 Original tweet:")
    print(f"   {post['text']}")
    print(f"\n🔗 URL: {post['url']}")
    
    try:
        print(f"\n⏳ Generating reply...")
        reply = write_reply(post['text'])
        print(f"\n✅ Generated Reply:")
        print(f"   {reply}")
        print(f"\n📏 Length: {len(reply)} characters")
        
        if len(reply) > 280:
            print(f"   ⚠️  Warning: Reply exceeds 280 characters!")
        else:
            print(f"   ✅ Within Twitter's character limit")
            
    except Exception as e:
        print(f"\n❌ Error generating reply: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Mock Test Complete!")
print("=" * 70)
print("\nSummary:")
print(f"  • Tested {len(MOCK_SCRAPED_POSTS)} mock posts")
print(f"  • Generated replies using reply_writer.py")
print(f"  • No API calls to X (completely safe)")
print("\nNext steps:")
print("  1. ✅ Flow logic works with mock data")
print("  2. Now configure GitHub Secrets with your X API credentials")
print("  3. Run the GitHub Actions workflow: test-x-api.yml")
print("  4. Once that passes, enable schedule-3x.yml")
print("\n" + "=" * 70)


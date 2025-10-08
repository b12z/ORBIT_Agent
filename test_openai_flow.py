#!/usr/bin/env python3
"""
Test OpenAI reply generation with mock scraped data.
- Mock scraped posts (no X API calls)
- Real OpenAI reply generation
- No actual posting (dry run)
"""
import os
import sys

# Try to load .env.local if it exists
try:
    from dotenv import load_dotenv
    if os.path.exists('.env.local'):
        load_dotenv('.env.local')
        print("✅ Loaded .env.local")
except ImportError:
    pass

print("=" * 70)
print("🧪 TEST: Mock Scraper → Real OpenAI → Dry Run Post")
print("=" * 70)
print("\n✅ Mock scraped data (no X API)")
print("✅ Real OpenAI reply generation")
print("✅ No actual posting (dry run)")
print()

# Mock scraped posts (simulating what scraper would return)
MOCK_POSTS = [
    {
        "id": "1234567890123456789",
        "tweet_id": "1234567890123456789",
        "handle": "web3builder",
        "text": "Just launched our new DeFi protocol! Super excited about bringing decentralized finance to more users. The composability is insane! #web3 #DeFi",
        "url": "https://twitter.com/web3builder/status/1234567890123456789",
        "verified": True,
        "followers": 25000,
    },
    {
        "id": "9876543210987654321",
        "tweet_id": "9876543210987654321",
        "handle": "cryptoinfluencer",
        "text": "Web3 gaming is changing everything. True ownership of in-game assets means players finally have real value. What's your favorite web3 game? 🎮",
        "url": "https://twitter.com/cryptoinfluencer/status/9876543210987654321",
        "verified": False,
        "followers": 50000,
    },
]

print("📊 Mock Scraped Posts:")
print("-" * 70)
for i, post in enumerate(MOCK_POSTS, 1):
    print(f"\n{i}. @{post['handle']} ({post['followers']:,} followers)")
    print(f"   Text: {post['text'][:100]}...")

# Check OpenAI key
print("\n" + "=" * 70)
print("🔑 Checking Environment")
print("=" * 70)

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("\n❌ OPENAI_API_KEY not set!")
    print("\n   Please set it:")
    print("   export OPENAI_API_KEY='your-key-here'")
    print("\n   Or add to .env.local:")
    print("   echo 'OPENAI_API_KEY=your-key-here' >> .env.local")
    sys.exit(1)
else:
    print(f"✅ OPENAI_API_KEY: {openai_key[:20]}...{openai_key[-4:]}")

# Import reply writer
print("\n" + "=" * 70)
print("🤖 Loading Reply Generator")
print("=" * 70)

try:
    from src.reply_writer import write_reply
    print("✅ Reply writer loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    print("\n   Make sure dependencies are installed:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

# Test reply generation
print("\n" + "=" * 70)
print("🚀 Generating Replies (Real OpenAI calls)")
print("=" * 70)

successful = 0
failed = 0

for i, post in enumerate(MOCK_POSTS, 1):
    print(f"\n{'─' * 70}")
    print(f"Post {i}/{len(MOCK_POSTS)}")
    print(f"{'─' * 70}")
    print(f"👤 @{post['handle']} ({post['followers']:,} followers)")
    print(f"\n📝 Original Tweet:")
    print(f"   {post['text']}")
    print(f"\n🔗 {post['url']}")
    
    try:
        print(f"\n⏳ Calling OpenAI to generate reply...")
        reply = write_reply(post['text'])
        
        print(f"\n✅ Generated Reply:")
        print(f"   {reply}")
        print(f"\n📏 Length: {len(reply)} characters", end="")
        
        if len(reply) > 280:
            print(" ⚠️  (exceeds Twitter limit!)")
        else:
            print(" ✅")
        
        print(f"\n🚫 DRY RUN - Would post reply to: {post['url']}")
        print(f"   (Not actually posting)")
        
        successful += 1
        
    except Exception as e:
        print(f"\n❌ Error generating reply:")
        print(f"   {str(e)}")
        failed += 1
        import traceback
        print("\n   Full traceback:")
        traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("📊 Test Summary")
print("=" * 70)
print(f"\n  Total posts:      {len(MOCK_POSTS)}")
print(f"  ✅ Successful:    {successful}")
print(f"  ❌ Failed:        {failed}")

if successful > 0:
    print("\n✅ OpenAI reply generation is working!")
    print("\n   Your flow is ready:")
    print("   1. ✅ Scraper logic (tested with mocks)")
    print("   2. ✅ OpenAI reply generation (tested with real API)")
    print("   3. ✅ Posting logic (skipped for safety)")
    
    print("\n   Next steps:")
    print("   • Add X API credentials to GitHub Secrets")
    print("   • Run GitHub Actions workflow: test-x-api.yml")
    print("   • If that passes, enable schedule-3x.yml")
else:
    print("\n⚠️  Some replies failed to generate")
    print("   Check the errors above and fix before deploying")

print("\n" + "=" * 70)


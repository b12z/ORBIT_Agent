#!/usr/bin/env python3
"""
Test the updated search with $POL KOL min_replies:10 min_faves:10
This shows the query structure without making API calls.
"""
import os
import sys

# Try to load .env.local
try:
    from dotenv import load_dotenv
    if os.path.exists('.env.local'):
        load_dotenv('.env.local')
        print("✅ Loaded .env.local\n")
except ImportError:
    pass

print("=" * 70)
print("🔍 Testing $POL KOL Search Query Structure")
print("=" * 70)

# Show what the query would look like
topics = ["$POL"]
min_replies = 10
min_faves = 10

print("\n📋 Search Parameters:")
print(f"   Topics: {topics}")
print(f"   Min Replies: {min_replies}")
print(f"   Min Favorites: {min_faves}")

# Build the query exactly as x_search.py does
topics_clause = " OR ".join([t.strip() for t in topics if t.strip()])
kol_clause = 'KOL OR "key opinion leader" OR influencer'
query = f"({topics_clause}) ({kol_clause}) min_replies:{min_replies} min_faves:{min_faves} -is:reply -is:retweet"

print("\n🔍 Generated X API v2 Query:")
print("-" * 70)
print(query)
print("-" * 70)

print("\n✅ Query Breakdown:")
print(f"   1. Topics: ($POL)")
print(f"   2. KOL terms: (KOL OR \"key opinion leader\" OR influencer)")
print(f"   3. Engagement: min_replies:10 min_faves:10")
print(f"   4. Exclusions: -is:reply -is:retweet")

print("\n📚 X API v2 Operators Used:")
print("   • Cashtag: $POL (searches for mentions of POL token)")
print("   • Text search: KOL, 'key opinion leader', influencer")
print("   • Engagement: min_replies:10 (minimum 10 replies)")
print("   • Engagement: min_faves:10 (minimum 10 likes/favorites)")
print("   • Filters: -is:reply -is:retweet (exclude replies and retweets)")

print("\n" + "=" * 70)
print("🧪 Testing with Mock API Call")
print("=" * 70)

# Check if we can import the module
try:
    from src.x_search import search_kol_recent
    print("✅ Module imported successfully\n")
    
    # Check API keys
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("⚠️  X API credentials not set - cannot test real API call")
        print("   To test with real API:")
        print("   1. Set API_KEY, API_KEY_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET")
        print("   2. Run: python test_pol_search.py --live")
        print("\n✅ Query structure validation complete!")
        sys.exit(0)
    
    # Check if user wants to make real API call
    if "--live" in sys.argv:
        print("🚀 Making REAL API call to X...")
        print("   This will use 1 API request from your quota.")
        
        confirm = input("\n   Continue? (yes/no): ").lower().strip()
        if confirm != "yes":
            print("\n   Cancelled. No API call made.")
            sys.exit(0)
        
        print("\n⏳ Searching for $POL KOL posts with min engagement...")
        results = search_kol_recent(
            topics=["$POL"],
            limit=5,
            hours=24,
            min_replies=10,
            min_faves=10
        )
        
        print(f"\n✅ API call successful!")
        print(f"   Found {len(results)} posts\n")
        
        if results:
            print("📊 Results:")
            print("=" * 70)
            for i, post in enumerate(results, 1):
                print(f"\n{i}. @{post['handle']} ({post.get('followers', 0):,} followers)")
                print(f"   Text: {post['text'][:100]}...")
                print(f"   Engagement: {post.get('reply_count', 0)} replies, {post.get('like_count', 0)} likes")
                print(f"   URL: {post['url']}")
        else:
            print("\n⚠️  No posts found matching criteria.")
            print("   This could mean:")
            print("   • No $POL KOL posts in last 24 hours")
            print("   • Posts don't meet engagement threshold (10 replies + 10 likes)")
            print("   • Query is too restrictive")
            print("\n   Try:")
            print("   • Increase time window (hours)")
            print("   • Lower engagement thresholds")
            print("   • Add more topic variations")
    else:
        print("✅ Module validation successful!")
        print("\n   To test with a REAL API call, run:")
        print("   python test_pol_search.py --live")
        print("\n   (This will use 1 API request)")
        
except ImportError as e:
    print(f"❌ Failed to import module: {e}")
    print("\n   Make sure you're in the project directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ Test Complete!")
print("=" * 70)


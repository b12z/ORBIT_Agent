import os
import re
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright, Page, Browser
from urllib.parse import quote
import time


def search_posts(topics: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for posts on X (Twitter) for given topics and return filtered results.
    
    Args:
        topics: List of search topics
        limit: Maximum number of posts to return per topic
        
    Returns:
        List of dictionaries containing tweet data
    """
    all_posts = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set user agent to avoid detection
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        for topic in topics:
            try:
                posts = _search_topic(page, topic, limit)
                all_posts.extend(posts)
            except Exception as e:
                print(f"Error searching for topic '{topic}': {e}")
                continue
        
        browser.close()
    
    # Filter and deduplicate posts
    filtered_posts = _filter_posts(all_posts)
    return _deduplicate_posts(filtered_posts)


def _search_topic(page: Page, topic: str, limit: int) -> List[Dict[str, Any]]:
    """Search for a specific topic on X."""
    # Construct search query (no live filter)
    query = f'{topic} -is:reply -is:retweet'
    search_url_primary = f"https://x.com/search?q={quote(query)}&src=typed_query"
    search_url_fallback = f"https://twitter.com/search?q={quote(query)}&src=typed_query"
    
    try:
        # goto with small retry, wait for DOM only (no networkidle)
        def navigate_and_prime(url: str):
            tries = 3
            for i in range(tries):
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    break
                except Exception:
                    if i == tries - 1:
                        raise
                    time.sleep(1.5 + 0.5 * i)
            # initial prime scrolls before waiting
            for _ in range(3):
                try:
                    page.mouse.wheel(0, 1400)
                except Exception:
                    page.evaluate("window.scrollBy(0, 1400)")
                time.sleep(0.8)
            # wait for any status link
            page.wait_for_selector('a[href*="/status/"]', timeout=60000)

        # try primary, then fallback domain
        try:
            navigate_and_prime(search_url_primary)
        except Exception:
            navigate_and_prime(search_url_fallback)

        # collect cards (prefer tweet articles, fallback to cell containers)
        cards = page.query_selector_all('article[data-testid="tweet"]')
        if not cards:
            cards = page.query_selector_all('[data-testid="cellInnerDiv"]')
        results = []
        for c in cards[:30]:
            try:
                link = c.query_selector('a[href*="/status/"]')
                text_el = c.query_selector('[data-testid="tweetText"]')
                handle_el = c.query_selector('a[href^="/"][role="link"]')
                if not (link and text_el and handle_el):
                    continue

                href = link.get_attribute("href") or ""  # /user/status/12345
                tweet_id = href.split("/")[-1]
                handle_href = handle_el.get_attribute("href") or "/"
                handle = handle_href[1:].split("/")[0]
                text_node = text_el.text_content() or ""
                text_val = text_node.strip()
                url = f"https://twitter.com/{handle}/status/{tweet_id}" if handle and tweet_id else ""
                verified = c.query_selector('[data-testid="icon-verified"]') is not None

                # Include both id and tweet_id for compatibility across callers
                results.append({
                    "id": tweet_id,
                    "tweet_id": tweet_id,
                    "handle": handle,
                    "text": text_val,
                    "url": url,
                    "verified": verified,
                    "followers": None,
                })
            except Exception as e:
                print("Error extracting post:", e)
                continue

        print(f"Extracted {len(results)} posts for topic {topic}")
        return results[:limit]
        
    except Exception as e:
        print(f"Error searching topic '{topic}': {e}")
        return []


def _extract_posts_from_page(page: Page) -> List[Dict[str, Any]]:
    """Extract post data from the current page."""
    posts = []
    
    try:
        # Wait for tweets to load
        page.wait_for_selector('[data-testid="tweet"]', timeout=10000)
        
        # Get all tweet elements
        tweet_elements = page.query_selector_all('[data-testid="tweet"]')
        
        for tweet_element in tweet_elements:
            try:
                post_data = _extract_tweet_data(tweet_element)
                if post_data:
                    posts.append(post_data)
            except Exception as e:
                print(f"Error extracting tweet data: {e}")
                continue
                
    except Exception as e:
        print(f"Error extracting posts: {e}")
    
    return posts


def _extract_tweet_data(tweet_element) -> Dict[str, Any]:
    """Extract data from a single tweet element."""
    try:
        # Extract tweet ID from URL
        tweet_link = tweet_element.query_selector('a[href*="/status/"]')
        tweet_url = tweet_link.get_attribute('href') if tweet_link else ""
        tweet_id = tweet_url.split('/')[-1] if tweet_url else ""
        
        # Extract author information
        author_element = tweet_element.query_selector('[data-testid="User-Name"]')
        if not author_element:
            return None
            
        author_name = author_element.text_content().strip() if author_element else ""
        
        # Extract handle
        handle_element = tweet_element.query_selector('[data-testid="User-Name"] a')
        handle = ""
        if handle_element:
            handle_url = handle_element.get_attribute('href')
            if handle_url:
                handle = handle_url.replace('/', '').replace('@', '')
        
        # Check if verified
        verified = tweet_element.query_selector('[data-testid="icon-verified"]') is not None
        
        # Extract tweet text
        text_element = tweet_element.query_selector('[data-testid="tweetText"]')
        text = text_element.text_content().strip() if text_element else ""
        
        # Extract follower count (this is challenging with X's current structure)
        # We'll try to get it from the user profile link
        followers = 0
        try:
            # This is a simplified approach - in practice, you might need to visit profile pages
            # or use a different method to get accurate follower counts
            user_link = tweet_element.query_selector('[data-testid="User-Name"] a')
            if user_link:
                # For now, we'll set a default value and rely on other filters
                followers = 1000  # Placeholder
        except:
            followers = 0
        
        return {
            'tweet_id': tweet_id,
            'author': author_name,
            'handle': handle,
            'text': text,
            'url': f"https://twitter.com/{handle}/status/{tweet_id}" if handle and tweet_id else "",
            'verified': verified,
            'followers': followers
        }
        
    except Exception as e:
        print(f"Error extracting tweet data: {e}")
        return None


def _filter_posts(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter posts based on verification, followers, and allowlist."""
    filtered_posts = []
    allowlist = _get_allowlist()
    
    for post in posts:
        if not post or not post.get('tweet_id'):
            continue

        # Temporarily allow only verified or allowlisted; ignore follower threshold placeholder
        is_verified = post.get('verified', False)
        is_allowlisted = post.get('handle', '').lower() in allowlist

        if is_verified or is_allowlisted:
            filtered_posts.append(post)
    
    return filtered_posts


def _get_allowlist() -> List[str]:
    """Get allowlist from environment variable."""
    allowlist_str = os.getenv('ALLOWLIST', '')
    if allowlist_str:
        return [handle.strip().lower().replace('@', '') for handle in allowlist_str.split(',')]
    return []


def _deduplicate_posts(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate posts based on tweet_id."""
    seen_ids = set()
    unique_posts = []
    
    for post in posts:
        tweet_id = post.get('tweet_id')
        if tweet_id and tweet_id not in seen_ids:
            seen_ids.add(tweet_id)
            unique_posts.append(post)
    
    return unique_posts


# Example usage
if __name__ == "__main__":
    # Example topics
    topics = ["Web3 growth", "KOL marketing", "influencer metrics"]
    
    # Set environment variable for testing
    os.environ['ALLOWLIST'] = 'elonmusk,vitalikbuterin'
    
    # Search for posts
    results = search_posts(topics, limit=3)
    
    print(f"Found {len(results)} posts:")
    for post in results:
        print(f"- {post['author']} (@{post['handle']}): {post['text'][:100]}...")

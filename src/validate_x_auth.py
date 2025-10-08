"""
X API Authentication Validator
Tests API credentials without consuming rate limits excessively.
"""
import os
import sys
from typing import Dict, Optional
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv


def check_oauth1_credentials() -> Dict[str, str]:
    """Check if OAuth1 credentials are present in environment."""
    creds = {
        "API_KEY": os.getenv("API_KEY"),
        "API_KEY_SECRET": os.getenv("API_KEY_SECRET"),
        "X_ACCESS_TOKEN": os.getenv("X_ACCESS_TOKEN"),
        "X_ACCESS_SECRET": os.getenv("X_ACCESS_SECRET"),
    }
    
    missing = [k for k, v in creds.items() if not v]
    if missing:
        return {"status": "missing", "missing_vars": ", ".join(missing)}
    
    return {"status": "present", "message": "All OAuth1 credentials found"}


def test_auth_with_minimal_request() -> Dict[str, any]:
    """
    Test authentication with a minimal API request that uses very little quota.
    Uses the /users/me endpoint which is lightweight.
    """
    auth = OAuth1(
        os.getenv("API_KEY"),
        os.getenv("API_KEY_SECRET"),
        os.getenv("X_ACCESS_TOKEN"),
        os.getenv("X_ACCESS_SECRET"),
    )
    
    # Use a minimal endpoint to test auth
    url = "https://api.twitter.com/2/users/me"
    
    try:
        response = requests.get(url, auth=auth, timeout=10)
        
        result = {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": None,
            "error": None,
        }
        
        if response.status_code == 200:
            data = response.json()
            result["response"] = {
                "username": data.get("data", {}).get("username"),
                "id": data.get("data", {}).get("id")
            }
            result["message"] = "✅ Authentication successful!"
        elif response.status_code == 401:
            result["error"] = "Authentication failed - Invalid credentials"
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text
        elif response.status_code == 429:
            result["error"] = "Rate limit exceeded"
            result["response"] = response.headers.get("x-rate-limit-reset")
        else:
            result["error"] = f"Unexpected status code: {response.status_code}"
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            "status_code": None,
            "success": False,
            "error": f"Request failed: {str(e)}",
            "response": None,
        }


def check_rate_limits() -> Optional[Dict]:
    """
    Check current rate limit status without consuming quota.
    Returns rate limit info if auth is successful.
    """
    auth = OAuth1(
        os.getenv("API_KEY"),
        os.getenv("API_KEY_SECRET"),
        os.getenv("X_ACCESS_TOKEN"),
        os.getenv("X_ACCESS_SECRET"),
    )
    
    # Rate limit status endpoint
    url = "https://api.twitter.com/1.1/application/rate_limit_status.json"
    params = {"resources": "search,tweets"}
    
    try:
        response = requests.get(url, auth=auth, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            resources = data.get("resources", {})
            
            # Extract relevant rate limits
            search_tweets = resources.get("search", {}).get("/search/tweets", {})
            search_recent = resources.get("tweets", {}).get("/tweets/search/recent", {})
            
            return {
                "success": True,
                "search_tweets": {
                    "limit": search_tweets.get("limit"),
                    "remaining": search_tweets.get("remaining"),
                    "reset": search_tweets.get("reset"),
                },
                "search_recent": {
                    "limit": search_recent.get("limit"),
                    "remaining": search_recent.get("remaining"),
                    "reset": search_recent.get("reset"),
                },
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": "Could not fetch rate limits"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Exception: {str(e)}"
        }


def main():
    """Run validation checks."""
    print("=" * 60)
    print("X API Authentication Validator")
    print("=" * 60)
    
    # Load environment
    if os.path.exists('.env.local'):
        print("Loading .env.local...")
        load_dotenv('.env.local')
    else:
        print("No .env.local found, using system environment variables")
    
    print("\n1. Checking credentials presence...")
    print("-" * 60)
    cred_check = check_oauth1_credentials()
    
    if cred_check["status"] == "missing":
        print(f"❌ Missing credentials: {cred_check['missing_vars']}")
        print("\nRequired environment variables:")
        print("  - API_KEY")
        print("  - API_KEY_SECRET")
        print("  - X_ACCESS_TOKEN")
        print("  - X_ACCESS_SECRET")
        sys.exit(1)
    else:
        print(f"✅ {cred_check['message']}")
    
    print("\n2. Testing authentication...")
    print("-" * 60)
    auth_result = test_auth_with_minimal_request()
    
    if auth_result["success"]:
        print(f"✅ {auth_result['message']}")
        if auth_result["response"]:
            print(f"   Authenticated as: @{auth_result['response']['username']}")
            print(f"   User ID: {auth_result['response']['id']}")
    else:
        print(f"❌ Authentication failed!")
        print(f"   Status code: {auth_result['status_code']}")
        print(f"   Error: {auth_result['error']}")
        if auth_result["response"]:
            print(f"   Response: {auth_result['response']}")
        sys.exit(1)
    
    print("\n3. Checking rate limits...")
    print("-" * 60)
    rate_limits = check_rate_limits()
    
    if rate_limits and rate_limits.get("success"):
        print("✅ Rate limit status:")
        
        search_recent = rate_limits.get("search_recent", {})
        if search_recent.get("limit"):
            print(f"\n   /tweets/search/recent:")
            print(f"     Limit: {search_recent['limit']}")
            print(f"     Remaining: {search_recent['remaining']}")
            if search_recent.get("reset"):
                import datetime
                reset_time = datetime.datetime.fromtimestamp(search_recent['reset'])
                print(f"     Resets at: {reset_time}")
        
        search_tweets = rate_limits.get("search_tweets", {})
        if search_tweets.get("limit"):
            print(f"\n   /search/tweets:")
            print(f"     Limit: {search_tweets['limit']}")
            print(f"     Remaining: {search_tweets['remaining']}")
    else:
        print(f"⚠️  Could not fetch rate limits")
        if rate_limits:
            print(f"   Error: {rate_limits.get('error')}")
    
    print("\n" + "=" * 60)
    print("✅ Validation complete - credentials are working!")
    print("=" * 60)
    print("\nSafe to proceed with API calls.")


if __name__ == "__main__":
    main()


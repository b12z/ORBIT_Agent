import os
import requests
import json
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')


def post_tweet(text: str, in_reply_to: Optional[str] = None) -> Dict:
    """
    Post a tweet using X API v2 with OAuth2 refresh flow.
    
    Args:
        text: The tweet text to post
        in_reply_to: Optional tweet ID to reply to
        
    Returns:
        Dictionary containing the API response or error information
    """
    # Read OAuth2 credentials from environment
    client_id = os.getenv('X_CLIENT_ID')
    client_secret = os.getenv('X_CLIENT_SECRET')
    redirect_url = os.getenv('X_REDIRECT_URL')
    refresh_token = os.getenv('X_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, redirect_url, refresh_token]):
        error_msg = "Missing required environment variables: X_CLIENT_ID, X_CLIENT_SECRET, X_REDIRECT_URL, X_REFRESH_TOKEN"
        print(f"Error: {error_msg}")
        return {"error": error_msg, "success": False}
    
    # Step 1: Get access token using refresh token
    access_token = _get_access_token(client_id, client_secret, redirect_url, refresh_token)
    if not access_token:
        return {"error": "Failed to obtain access token", "success": False}
    
    # Step 2: Post the tweet
    return _post_tweet_with_token(text, access_token, in_reply_to)


def _get_access_token(client_id: str, client_secret: str, redirect_url: str, refresh_token: str) -> Optional[str]:
    """
    Get access token using OAuth2 refresh flow.
    
    Returns:
        Access token string or None if failed
    """
    token_url = "https://api.x.com/2/oauth2/token"
    
    # Prepare the request data
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_url
    }
    
    # Set headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        print("Refreshing access token...")
        response = requests.post(token_url, data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            if access_token:
                print("Access token obtained successfully")
                return access_token
            else:
                print(f"Error: No access_token in response: {token_data}")
                return None
        else:
            print(f"Error refreshing token - Status: {response.status_code}")
            print(f"Response body: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making token request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing token response JSON: {e}")
        return None


def _post_tweet_with_token(text: str, access_token: str, in_reply_to: Optional[str] = None) -> Dict:
    """
    Post tweet using the access token.
    
    Returns:
        Dictionary with API response or error information
    """
    tweet_url = "https://api.x.com/2/tweets"
    
    # Prepare the tweet payload
    payload = {"text": text}
    
    # Add reply information if specified
    if in_reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": in_reply_to}
    
    # Set headers with Bearer token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Posting tweet: {text[:50]}...")
        response = requests.post(tweet_url, json=payload, headers=headers)
        
        if response.status_code == 201:
            tweet_data = response.json()
            print("Tweet posted successfully!")
            return {
                "success": True,
                "tweet_id": tweet_data.get('data', {}).get('id'),
                "text": tweet_data.get('data', {}).get('text'),
                "response": tweet_data
            }
        else:
            error_msg = f"Failed to post tweet - Status: {response.status_code}"
            print(error_msg)
            print(f"Response body: {response.text}")
            return {
                "success": False,
                "error": error_msg,
                "status_code": response.status_code,
                "response_body": response.text
            }
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Error making tweet request: {e}"
        print(error_msg)
        return {"success": False, "error": error_msg}
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing tweet response JSON: {e}"
        print(error_msg)
        return {"success": False, "error": error_msg}


# Example usage and testing
if __name__ == "__main__":
    # Test posting a tweet
    result = post_tweet("Hello from ORBIT Agent! 🚀")
    print(f"Tweet result: {result}")
    
    # Test posting a reply (uncomment and set a real tweet ID)
    # result = post_tweet("This is a reply!", in_reply_to="1234567890")
    # print(f"Reply result: {result}")

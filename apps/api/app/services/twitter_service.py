import os
import logging
from typing import Dict, Any, Optional
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class TwitterService:
    """Service for posting to Twitter/X using Tweepy"""
    
    def __init__(self):
        # Twitter API credentials
        self.consumer_key = os.getenv("TWITTER_CONSUMER_KEY") 
        self.consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        # Check if all required credentials are present
        required_creds = [
            self.consumer_key, 
            self.consumer_secret, 
            self.access_token, 
            self.access_token_secret,
            self.bearer_token
        ]
        
        if not all(required_creds):
            logger.warning("Twitter API credentials not fully configured. Twitter posting will be disabled.")
            self.client = None
        else:
            try:
                # Initialize Tweepy client with OAuth 1.0a User Context
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )
                
                # Test authentication
                try:
                    me = self.client.get_me()
                    if me.data:
                        logger.info(f"Twitter service initialized successfully for @{me.data.username}")
                    else:
                        logger.warning("Twitter authentication succeeded but couldn't get user info")
                except Exception as auth_error:
                    logger.error(f"Twitter authentication test failed: {str(auth_error)}")
                    self.client = None
                    
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {str(e)}")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if Twitter service is properly configured"""
        return self.client is not None
    
    def generate_repository_tweet(self, repo_info: Dict[str, Any]) -> str:
        """Generate a tweet text for a repository"""
        try:
            name = repo_info.get("name", "Unknown")
            author = repo_info.get("author", "")
            repo_url = repo_info.get("repo_url", "")
            description = repo_info.get("description", "")
            
            # Create tweet content
            tweet_parts = []
            
            # Add repository name and author
            if author:
                tweet_parts.append(f"🚀 {name} by @{author}" if author.startswith("@") else f"🚀 {name} by {author}")
            else:
                tweet_parts.append(f"🚀 {name}")
            
            # Add description if available (truncate if too long)
            if description:
                # Leave space for URL and hashtags (~50 chars)
                max_desc_length = 200
                if len(description) > max_desc_length:
                    description = description[:max_desc_length-3] + "..."
                tweet_parts.append(f"\n\n{description}")
            
            # Add hashtags
            hashtags = ["#OpenSource", "#GitHub", "#Developer", "#Code"]
            tweet_parts.append(f"\n\n{' '.join(hashtags)}")
            
            # Add repository URL
            tweet_parts.append(f"\n\n{repo_url}")
            
            tweet_text = "".join(tweet_parts)
            
            # Ensure tweet is under 280 characters
            if len(tweet_text) > 280:
                # Trim description to fit
                available_chars = 280 - len(tweet_parts[0]) - len(tweet_parts[2]) - len(tweet_parts[3]) - 10  # 10 chars buffer
                if len(description) > available_chars:
                    trimmed_desc = description[:available_chars-3] + "..."
                    tweet_parts[1] = f"\n\n{trimmed_desc}"
                tweet_text = "".join(tweet_parts)
            
            return tweet_text
            
        except Exception as e:
            logger.error(f"Error generating tweet for repository {repo_info.get('name', 'unknown')}: {str(e)}")
            # Fallback to simple tweet
            return f"🚀 Check out this repository: {repo_info.get('repo_url', '')} #OpenSource #GitHub"
    
    async def post_tweet(self, tweet_text: str) -> Dict[str, Any]:
        """Post a tweet to Twitter/X"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Twitter service is not configured",
                "tweet_id": None,
                "tweet_url": None
            }
        
        try:
            logger.info(f"Posting tweet: {tweet_text[:100]}...")
            
            # Post the tweet
            response = self.client.create_tweet(text=tweet_text)
            
            if response.data:
                tweet_id = response.data["id"]
                tweet_url = f"https://twitter.com/intent/tweet?tweet_id={tweet_id}"
                
                logger.info(f"Tweet posted successfully: {tweet_url}")
                
                return {
                    "success": True,
                    "error": None,
                    "tweet_id": tweet_id,
                    "tweet_url": tweet_url,
                    "tweet_text": tweet_text
                }
            else:
                logger.error("Tweet creation failed - no response data")
                return {
                    "success": False,
                    "error": "Tweet creation failed - no response data",
                    "tweet_id": None,
                    "tweet_url": None
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to post tweet: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tweet_id": None,
                "tweet_url": None
            }
    
    async def post_repository_tweet(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and post a tweet for a repository"""
        try:
            # Generate tweet text
            tweet_text = self.generate_repository_tweet(repo_info)
            
            # Post tweet
            result = await self.post_tweet(tweet_text)
            
            # Add repository info to result
            result["repository_id"] = repo_info.get("id")
            result["repository_name"] = repo_info.get("name")
            result["repository_url"] = repo_info.get("repo_url")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to post repository tweet for {repo_info.get('name', 'unknown')}: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tweet_id": None,
                "tweet_url": None,
                "repository_id": repo_info.get("id"),
                "repository_name": repo_info.get("name"),
                "repository_url": repo_info.get("repo_url")
            }
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get Twitter API rate limit status"""
        if not self.is_configured():
            return {"error": "Twitter service not configured"}
        
        try:
            # Note: This would require additional API calls to get rate limit info
            # For now, return a placeholder
            return {
                "tweets_remaining": "Unknown - check Twitter API rate limits",
                "reset_time": "Unknown",
                "note": "Twitter API v2 rate limits: 300 tweets per 15 minutes"
            }
        except Exception as e:
            return {"error": str(e)}

# Global Twitter service instance
twitter_service = TwitterService()
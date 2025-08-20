import os
import logging
from typing import Dict, Any, Optional, List, Union
import tweepy
from dotenv import load_dotenv
import tempfile

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
        
        # Debug logging for environment variables
        logger.debug(f"Twitter credentials check:")
        logger.debug(f"  TWITTER_CONSUMER_KEY: {'✅ Set' if self.consumer_key else '❌ Missing'}")
        logger.debug(f"  TWITTER_CONSUMER_SECRET: {'✅ Set' if self.consumer_secret else '❌ Missing'}")
        logger.debug(f"  TWITTER_ACCESS_TOKEN: {'✅ Set' if self.access_token else '❌ Missing'}")
        logger.debug(f"  TWITTER_ACCESS_TOKEN_SECRET: {'✅ Set' if self.access_token_secret else '❌ Missing'}")
        logger.debug(f"  TWITTER_BEARER_TOKEN: {'✅ Set' if self.bearer_token else '❌ Missing'}")
        
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
            self.api = None
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
                
                # Initialize API v1.1 for media uploads (required for media)
                auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
                auth.set_access_token(self.access_token, self.access_token_secret)
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
                
                # Test authentication
                try:
                    logger.info("🔐 Testing Twitter API authentication...")
                    me = self.client.get_me()
                    if me.data:
                        logger.info(f"✅ Twitter service initialized successfully for @{me.data.username}")
                    else:
                        logger.warning("⚠️ Twitter authentication succeeded but couldn't get user info")
                except Exception as auth_error:
                    error_msg = str(auth_error)
                    logger.error(f"❌ Twitter authentication test failed: {error_msg}")
                    
                    # Provide specific guidance based on error type
                    if "401" in error_msg or "Unauthorized" in error_msg:
                        logger.error("🔑 401 Unauthorized Error - This typically means:")
                        logger.error("   1. Invalid API credentials (check if they're correct)")
                        logger.error("   2. App doesn't have proper permissions")
                        logger.error("   3. Bearer token doesn't match the app")
                        logger.error("   4. Access tokens are expired or revoked")
                        logger.error("💡 Solutions:")
                        logger.error("   - Verify credentials in Twitter Developer Portal")
                        logger.error("   - Regenerate access tokens if needed")
                        logger.error("   - Check if app has 'Read and Write' permissions")
                        logger.error("   - Ensure bearer token matches the app")
                    elif "403" in error_msg or "Forbidden" in error_msg:
                        logger.error("🚫 403 Forbidden Error - Check app permissions")
                    elif "429" in error_msg:
                        logger.error("🚦 429 Rate Limited - Wait before retrying")
                    else:
                        logger.error(f"❓ Unexpected error: {error_msg}")
                    
                    self.client = None
                    self.api = None
                    
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {str(e)}")
                self.client = None
                self.api = None
    
    def is_configured(self) -> bool:
        """Check if Twitter service is properly configured"""
        return self.client is not None and self.api is not None
    
    def validate_credentials(self) -> Dict[str, Any]:
        """Validate Twitter credentials step by step for debugging"""
        results = {
            "credentials_present": False,
            "bearer_token_valid": False,
            "oauth_tokens_valid": False,
            "user_info": None,
            "errors": []
        }
        
        # Check if credentials are present
        if not all([self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret, self.bearer_token]):
            results["errors"].append("Missing required credentials")
            return results
        
        results["credentials_present"] = True
        
        try:
            # Test bearer token with a simple API call
            import tweepy
            bearer_client = tweepy.Client(bearer_token=self.bearer_token)
            bearer_client.get_me()
            results["bearer_token_valid"] = True
        except Exception as e:
            results["errors"].append(f"Bearer token invalid: {str(e)}")
        
        try:
            # Test OAuth 1.0a with full credentials
            oauth_client = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            me = oauth_client.get_me()
            if me.data:
                results["oauth_tokens_valid"] = True
                results["user_info"] = {
                    "username": me.data.username,
                    "name": me.data.name,
                    "id": me.data.id
                }
        except Exception as e:
            results["errors"].append(f"OAuth tokens invalid: {str(e)}")
        
        return results
    
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
    
    def upload_media(self, media_path: str, alt_text: Optional[str] = None) -> Optional[str]:
        """Upload media to Twitter and return media ID"""
        if not self.is_configured():
            logger.error("Twitter service is not configured")
            return None
        
        try:
            logger.info(f"Uploading media: {media_path}")
            
            # Upload media using API v1.1
            media = self.api.media_upload(media_path)
            
            # Add alt text if provided
            if alt_text:
                try:
                    self.api.create_media_metadata(media.media_id, alt_text)
                    logger.info("Alt text added to media")
                except Exception as alt_error:
                    logger.warning(f"Failed to add alt text: {str(alt_error)}")
            
            logger.info(f"Media uploaded successfully: {media.media_id}")
            return str(media.media_id)
            
        except Exception as e:
            logger.error(f"Failed to upload media: {str(e)}")
            return None
    
    def download_and_upload_media(self, image_url: str, alt_text: Optional[str] = None) -> Optional[str]:
        """Download image from URL and upload to Twitter"""
        if not self.is_configured():
            logger.error("Twitter service is not configured")
            return None
        
        try:
            import requests
            
            logger.info(f"Downloading image from: {image_url}")
            
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            try:
                # Upload to Twitter
                media_id = self.upload_media(temp_path, alt_text)
                return media_id
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Failed to download and upload media from {image_url}: {str(e)}")
            return None
    
    async def post_tweet(self, tweet_text: str, media_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post a tweet to Twitter/X with optional media"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Twitter service is not configured",
                "tweet_id": None,
                "tweet_url": None
            }
        
        try:
            logger.info(f"Posting tweet: {tweet_text[:100]}...")
            if media_ids:
                logger.info(f"Including {len(media_ids)} media attachments")
            
            # Post the tweet with or without media
            if media_ids:
                response = self.client.create_tweet(text=tweet_text, media_ids=media_ids)
            else:
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
                    "tweet_text": tweet_text,
                    "media_ids": media_ids
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
    
    async def post_repository_tweet(self, repo_info: Dict[str, Any], include_media: bool = False) -> Dict[str, Any]:
        """Generate and post a tweet for a repository with optional media"""
        try:
            # Generate tweet text
            tweet_text = self.generate_repository_tweet(repo_info)
            
            # Handle media if requested
            media_ids = None
            if include_media and repo_info.get("readme_image_url"):
                try:
                    repo_name = repo_info.get("name", "Repository")
                    alt_text = f"README preview for {repo_name} repository"
                    
                    media_id = self.download_and_upload_media(
                        repo_info["readme_image_url"], 
                        alt_text
                    )
                    
                    if media_id:
                        media_ids = [media_id]
                        logger.info(f"Added README image as media for {repo_name}")
                    else:
                        logger.warning(f"Failed to upload README image for {repo_name}")
                        
                except Exception as media_error:
                    logger.error(f"Error processing media for repository {repo_info.get('name', 'unknown')}: {str(media_error)}")
                    # Continue without media rather than failing the entire tweet
            
            # Post tweet with or without media
            result = await self.post_tweet(tweet_text, media_ids)
            
            # Add repository info to result
            result["repository_id"] = repo_info.get("id")
            result["repository_name"] = repo_info.get("name")
            result["repository_url"] = repo_info.get("repo_url")
            result["included_media"] = media_ids is not None
            
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
                "repository_url": repo_info.get("repo_url"),
                "included_media": False
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

# Global Twitter service instance (lazy initialization)
class TwitterServiceSingleton:
    """Singleton wrapper for TwitterService with lazy initialization"""
    def __init__(self):
        self._service = None
    
    def __getattr__(self, name):
        if self._service is None:
            # Force reload of environment variables
            logger.info("🔄 Initializing Twitter service with fresh environment variables...")
            
            # Try to load .env from multiple possible locations
            import os.path
            possible_env_paths = [
                ".env",
                "../.env", 
                "../../.env",
                "/Users/rafiulm/git-search/.env",
                "/Users/rafiulm/git-search/apps/api/.env"
            ]
            
            env_loaded = False
            for env_path in possible_env_paths:
                if os.path.exists(env_path):
                    logger.info(f"📁 Found .env file at: {env_path}")
                    load_dotenv(env_path, override=True)
                    env_loaded = True
                    break
            
            if not env_loaded:
                logger.warning("⚠️ No .env file found in expected locations")
                load_dotenv(override=True)  # Try default behavior
            
            # Debug: Show what environment variables are actually loaded
            logger.debug("🔍 Environment variables after loading:")
            for key in ["TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET", "TWITTER_BEARER_TOKEN"]:
                value = os.getenv(key)
                if value:
                    logger.debug(f"  {key}: {value[:10]}...")
                else:
                    logger.debug(f"  {key}: ❌ Not set")
            
            self._service = TwitterService()
        return getattr(self._service, name)

# Global instance
twitter_service = TwitterServiceSingleton()
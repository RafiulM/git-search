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
    
    def generate_repository_thread(self, repo_info: Dict[str, Any]) -> Dict[str, str]:
        """Generate a Twitter thread for a repository - main tweet + reply with link"""
        try:
            name = repo_info.get("name", "Unknown")
            author = repo_info.get("author", "")
            repo_url = repo_info.get("repo_url", "")
            description = repo_info.get("description", "")
            
            # === MAIN TWEET (without URL) ===
            main_tweet_parts = []
            
            # Add repository name and author
            if author:
                # Clean up author name (remove @ if present since we're adding it)
                clean_author = author.lstrip("@")
                main_tweet_parts.append(f"🚀 {name} by {clean_author}")
            else:
                main_tweet_parts.append(f"🚀 {name}")
            
            # Always add description if available 
            if description and description.strip():
                # Clean up the description
                clean_desc = description.strip()
                
                # Skip generic fallback descriptions
                generic_descriptions = [
                    f"Repository by {author}",
                    "GitHub repository",
                    f"Repository by {clean_author}" if author else None
                ]
                
                if clean_desc not in [d for d in generic_descriptions if d]:
                    # Calculate available space for description (no URL in main tweet)
                    # Account for: name/author line + thread indicator + newlines + buffer
                    base_length = len(main_tweet_parts[0]) + 10  # thread indicator ~5 + buffer ~5
                    available_for_desc = 270 - base_length  # 270 to leave buffer
                    
                    if len(clean_desc) > available_for_desc:
                        # Smart truncation - try to end at sentence or word boundary
                        truncated = clean_desc[:available_for_desc-3]
                        
                        # Look for sentence ending
                        last_period = truncated.rfind('. ')
                        last_exclamation = truncated.rfind('! ')
                        last_question = truncated.rfind('? ')
                        
                        best_ending = max(last_period, last_exclamation, last_question)
                        
                        if best_ending > available_for_desc * 0.7:  # If we found a good ending point
                            clean_desc = truncated[:best_ending + 1]
                        else:
                            # Fall back to word boundary
                            last_space = truncated.rfind(' ')
                            if last_space > available_for_desc * 0.8:
                                clean_desc = truncated[:last_space] + "..."
                            else:
                                clean_desc = truncated + "..."
                    
                    main_tweet_parts.append(f"\n\n{clean_desc}")
            
            # Add thread indicator (no hashtags)
            main_tweet_parts.append(f"\n\n🧵")
            
            main_tweet = "".join(main_tweet_parts)
            
            # === REPLY TWEET (with URL and additional info) ===
            reply_tweet_parts = []
            
            # Add the repository URL
            if repo_url:
                reply_tweet_parts.append(f"🔗 {repo_url}")
            
            # Add any additional context or call to action
            reply_tweet_parts.append(f"\n\n⭐ Star it if you find it useful!")
            
            reply_tweet = "".join(reply_tweet_parts)
            
            # Final length checks
            if len(main_tweet) > 280:
                logger.warning(f"Main tweet too long ({len(main_tweet)} chars), trimming...")
                # More aggressive trimming for main tweet
                if len(main_tweet_parts) > 2 and description:
                    # Reduce description length
                    base_parts = [main_tweet_parts[0], main_tweet_parts[-1]]  # name, thread indicator
                    base_length = len("".join(base_parts))
                    
                    remaining_for_desc = 270 - base_length
                    if remaining_for_desc > 20:
                        short_desc = description[:remaining_for_desc-6] + "..."
                        main_tweet = main_tweet_parts[0] + f"\n\n{short_desc}" + main_tweet_parts[-1]
                    else:
                        # Skip description in main tweet
                        main_tweet = "".join([main_tweet_parts[0], main_tweet_parts[-1]])
            
            if len(reply_tweet) > 280:
                logger.warning(f"Reply tweet too long ({len(reply_tweet)} chars), trimming...")
                # Simplify reply tweet
                if repo_url:
                    reply_tweet = f"🔗 {repo_url}"
                else:
                    reply_tweet = "⭐ Check it out!"
            
            logger.info(f"Generated thread - Main: {len(main_tweet)} chars, Reply: {len(reply_tweet)} chars")
            
            return {
                "main_tweet": main_tweet,
                "reply_tweet": reply_tweet
            }
            
        except Exception as e:
            logger.error(f"Error generating thread for repository {repo_info.get('name', 'unknown')}: {str(e)}")
            # Fallback to simple thread (no hashtags)
            name = repo_info.get("name", "Repository")
            url = repo_info.get("repo_url", "")
            return {
                "main_tweet": f"🚀 {name}\n\n🧵",
                "reply_tweet": f"🔗 {url}\n\n⭐ Star it if you find it useful!"
            }
    
    def generate_repository_tweet(self, repo_info: Dict[str, Any]) -> str:
        """Generate a single tweet text for a repository (backward compatibility)"""
        thread = self.generate_repository_thread(repo_info)
        # Combine main tweet and reply for single tweet format
        main = thread["main_tweet"].replace("\n\n🧵", "")  # Remove thread indicator
        reply = thread["reply_tweet"]
        
        combined = f"{main}\n\n{reply}"
        
        # If combined is too long, prioritize main content
        if len(combined) > 280:
            return main + f"\n\n{repo_info.get('repo_url', '')}"
        
        return combined
    
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
    
    async def post_thread(self, main_tweet: str, reply_tweet: str, media_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post a Twitter thread with main tweet and reply"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Twitter service is not configured",
                "main_tweet_id": None,
                "reply_tweet_id": None,
                "thread_url": None
            }
        
        try:
            logger.info(f"Posting thread - Main: {main_tweet[:50]}... Reply: {reply_tweet[:50]}...")
            if media_ids:
                logger.info(f"Including {len(media_ids)} media attachments in main tweet")
            
            # Post the main tweet with optional media
            if media_ids:
                main_response = self.client.create_tweet(text=main_tweet, media_ids=media_ids)
            else:
                main_response = self.client.create_tweet(text=main_tweet)
            
            if not main_response.data:
                logger.error("Main tweet creation failed - no response data")
                return {
                    "success": False,
                    "error": "Main tweet creation failed - no response data",
                    "main_tweet_id": None,
                    "reply_tweet_id": None,
                    "thread_url": None
                }
            
            main_tweet_id = main_response.data["id"]
            logger.info(f"Main tweet posted successfully: {main_tweet_id}")
            
            # Post the reply tweet
            reply_response = self.client.create_tweet(
                text=reply_tweet,
                in_reply_to_tweet_id=main_tweet_id
            )
            
            if reply_response.data:
                reply_tweet_id = reply_response.data["id"]
                thread_url = f"https://twitter.com/intent/tweet?tweet_id={main_tweet_id}"
                
                logger.info(f"Thread posted successfully - Main: {main_tweet_id}, Reply: {reply_tweet_id}")
                
                return {
                    "success": True,
                    "error": None,
                    "main_tweet_id": main_tweet_id,
                    "reply_tweet_id": reply_tweet_id,
                    "thread_url": thread_url,
                    "main_tweet_text": main_tweet,
                    "reply_tweet_text": reply_tweet,
                    "media_ids": media_ids
                }
            else:
                logger.error("Reply tweet creation failed - no response data")
                # Main tweet was posted successfully, but reply failed
                return {
                    "success": False,
                    "error": "Reply tweet creation failed - main tweet posted successfully",
                    "main_tweet_id": main_tweet_id,
                    "reply_tweet_id": None,
                    "thread_url": f"https://twitter.com/intent/tweet?tweet_id={main_tweet_id}",
                    "partial_success": True
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to post thread: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "main_tweet_id": None,
                "reply_tweet_id": None,
                "thread_url": None
            }
    
    def validate_repository_description(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that repository has a meaningful description for Twitter posting"""
        description = repo_info.get("description", "").strip()
        repo_name = repo_info.get("name", "Unknown")
        author = repo_info.get("author", "")
        
        # Check if description exists
        if not description:
            return {
                "valid": False,
                "error": f"Repository {repo_name} has no description available"
            }
        
        # Check for generic/fallback descriptions that should be rejected
        generic_descriptions = [
            f"Repository by {author}",
            "GitHub repository",
            f"Repository by {author.lstrip('@')}" if author else None,
        ]
        
        if description in [d for d in generic_descriptions if d]:
            return {
                "valid": False,
                "error": f"Repository {repo_name} only has generic description: '{description}'. AI-generated short description required."
            }
        
        # Check for minimum meaningful length
        if len(description) < 10:
            return {
                "valid": False,
                "error": f"Repository {repo_name} description too short: '{description}'. Minimum 10 characters required."
            }
        
        return {
            "valid": True,
            "description": description
        }

    async def post_repository_tweet(self, repo_info: Dict[str, Any], include_media: bool = False) -> Dict[str, Any]:
        """Generate and post a Twitter thread for a repository with optional media - REQUIRES meaningful description"""
        try:
            # VALIDATION: Ensure repository has meaningful description
            validation = self.validate_repository_description(repo_info)
            if not validation["valid"]:
                error_msg = f"Cannot post tweet: {validation['error']}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "tweet_id": None,
                    "tweet_url": None,
                    "repository_id": repo_info.get("id"),
                    "repository_name": repo_info.get("name"),
                    "repository_url": repo_info.get("repo_url"),
                    "included_media": False,
                    "validation_failed": True
                }
            
            logger.info(f"✅ Repository {repo_info.get('name')} passed description validation")
            
            # Generate thread content (main tweet + reply with link)
            thread_content = self.generate_repository_thread(repo_info)
            main_tweet = thread_content["main_tweet"]
            reply_tweet = thread_content["reply_tweet"]
            
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
                    # Continue without media rather than failing the entire thread
            
            # Post thread with or without media
            result = await self.post_thread(main_tweet, reply_tweet, media_ids)
            
            # Transform thread result to match expected single-tweet format for backward compatibility
            if result["success"]:
                # Use main tweet ID as primary tweet ID and thread URL
                transformed_result = {
                    "success": True,
                    "error": None,
                    "tweet_id": result["main_tweet_id"],
                    "tweet_url": result["thread_url"],
                    "main_tweet_id": result["main_tweet_id"],
                    "reply_tweet_id": result["reply_tweet_id"],
                    "repository_id": repo_info.get("id"),
                    "repository_name": repo_info.get("name"),
                    "repository_url": repo_info.get("repo_url"),
                    "included_media": media_ids is not None,
                    "validation_failed": False,
                    "thread_posted": True,
                    "main_tweet_text": main_tweet,
                    "reply_tweet_text": reply_tweet
                }
            else:
                # Handle partial success (main tweet posted but reply failed)
                if result.get("partial_success"):
                    transformed_result = {
                        "success": True,  # Consider partial success as success
                        "error": result["error"],
                        "tweet_id": result["main_tweet_id"],
                        "tweet_url": result["thread_url"],
                        "main_tweet_id": result["main_tweet_id"],
                        "reply_tweet_id": None,
                        "repository_id": repo_info.get("id"),
                        "repository_name": repo_info.get("name"),
                        "repository_url": repo_info.get("repo_url"),
                        "included_media": media_ids is not None,
                        "validation_failed": False,
                        "thread_posted": False,
                        "partial_success": True
                    }
                else:
                    transformed_result = {
                        "success": False,
                        "error": result["error"],
                        "tweet_id": None,
                        "tweet_url": None,
                        "repository_id": repo_info.get("id"),
                        "repository_name": repo_info.get("name"),
                        "repository_url": repo_info.get("repo_url"),
                        "included_media": False,
                        "validation_failed": False,
                        "thread_posted": False
                    }
            
            return transformed_result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to post repository thread for {repo_info.get('name', 'unknown')}: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tweet_id": None,
                "tweet_url": None,
                "repository_id": repo_info.get("id"),
                "repository_name": repo_info.get("name"),
                "repository_url": repo_info.get("repo_url"),
                "included_media": False,
                "validation_failed": False,
                "thread_posted": False
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
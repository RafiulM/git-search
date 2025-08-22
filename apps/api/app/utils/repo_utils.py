from urllib.parse import urlparse
from typing import Dict, Optional
import requests
import os
import logging

logger = logging.getLogger(__name__)


def extract_repo_info(github_url: str) -> Dict[str, str]:
    """Extract repository information from GitHub URL"""
    try:
        # Handle different GitHub URL formats
        if github_url.endswith(".git"):
            github_url = github_url[:-4]

        # Parse URL
        parsed = urlparse(github_url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")

        owner = path_parts[0]
        repo_name = path_parts[1]

        return {
            "owner": owner,
            "repo_name": repo_name,
            "full_name": f"{owner}/{repo_name}",
            "clone_url": f"https://github.com/{owner}/{repo_name}.git",
        }
    except Exception as e:
        raise ValueError(f"Invalid GitHub URL: {str(e)}")


def get_default_branch(owner: str, repo_name: str) -> str:
    """Get the default branch for a GitHub repository"""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        # Get repository information from GitHub API
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repo_data = response.json()
            default_branch = repo_data.get("default_branch", "main")
            logger.info(f"Found default branch '{default_branch}' for {owner}/{repo_name}")
            return default_branch
        else:
            logger.warning(
                f"Failed to get repository info for {owner}/{repo_name} (status: {response.status_code}). Using 'main' as fallback."
            )
            return "main"
    
    except Exception as e:
        logger.warning(
            f"Error getting default branch for {owner}/{repo_name}: {str(e)}. Using 'main' as fallback."
        )
        return "main"
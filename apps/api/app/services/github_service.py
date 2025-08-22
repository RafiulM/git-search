"""
GitHub Service for repository operations including forking, cloning, and modifications
"""

import os
import tempfile
import shutil
import asyncio
import logging
import time
from typing import Optional, List, Dict, Any
from pathlib import Path

import git
from github import Github, Auth
from github.GithubException import GithubException

from app.models.github_config import (
    GitHubConfig,
    RepositoryInfo,
    FileOperation,
    CommitInfo,
    ForkConfig,
    CloneConfig,
    GitCommitAction,
    ForkAndModifyRequest,
    GitHubOperationResult,
    GitHubForkResult,
    GitHubCloneResult,
    GitHubCommitResult,
    GitHubPushResult,
    GitHubForkAndModifyResult,
)

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for GitHub operations including forking, cloning, and modifications"""

    def __init__(self, config: Optional[GitHubConfig] = None):
        """
        Initialize GitHub service

        Args:
            config: GitHub configuration. If None, will try to load from environment
        """
        self.config = config or self._load_config_from_env()
        self._github_client: Optional[Github] = None
        self._temp_directories: List[str] = []

    def _load_config_from_env(self) -> GitHubConfig:
        """Load GitHub configuration from environment variables"""
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_ACCESS_TOKEN")
        if not token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN or GITHUB_ACCESS_TOKEN environment variable"
            )

        return GitHubConfig(
            token=token,
            git_user_name=os.getenv("GIT_USER_NAME"),
            git_user_email=os.getenv("GIT_USER_EMAIL"),
        )

    @property
    def github_client(self) -> Github:
        """Get or create GitHub API client"""
        if self._github_client is None:
            auth = Auth.Token(self.config.token)
            self._github_client = Github(auth=auth, base_url=self.config.base_url)
        return self._github_client

    def cleanup_temp_directories(self):
        """Clean up all temporary directories created by this service"""
        for temp_dir in self._temp_directories:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(
                    f"Failed to cleanup temporary directory {temp_dir}: {str(e)}"
                )
        self._temp_directories.clear()

    def __del__(self):
        """Cleanup when service is destroyed"""
        try:
            if hasattr(self, "_temp_directories"):
                self.cleanup_temp_directories()
        except Exception:
            # Ignore cleanup errors during destruction
            pass

    async def fork_repository_internal(
        self,
        source_repo: RepositoryInfo,
        fork_name: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> GitHubForkResult:
        """
        Fork a GitHub repository

        Args:
            source_repo: Source repository to fork
            fork_name: Name for the fork (defaults to source name)
            organization: Organization to fork to (defaults to user)

        Returns:
            GitHubForkResult with fork details
        """
        start_time = time.time()

        try:
            logger.info(f"Forking repository {source_repo.full_name}")

            # Check if GitHub client is properly initialized
            if not hasattr(self, "_github_client") or self._github_client is None:
                logger.debug("Initializing GitHub client for fork operation")

            # Verify GitHub authentication before attempting fork
            try:
                user = self.github_client.get_user()
                logger.debug(f"Authenticated as GitHub user: {user.login}")
            except Exception as auth_error:
                raise Exception(f"GitHub authentication failed: {str(auth_error)}")

            # Get source repository
            logger.debug(f"Getting source repository: {source_repo.full_name}")
            if not source_repo.full_name:
                raise ValueError("Repository full_name is required")
            source_gh_repo = self.github_client.get_repo(source_repo.full_name)
            logger.debug(
                f"Successfully retrieved source repository: {source_gh_repo.full_name}"
            )

            # Fork the repository
            if organization:
                # Fork to organization
                logger.debug(f"Forking to organization: {organization}")
                org = self.github_client.get_organization(organization)
                forked_repo = source_gh_repo.create_fork(org, name=fork_name or None)
            else:
                # Fork to user account
                logger.debug("Forking to user account")
                forked_repo = source_gh_repo.create_fork(name=fork_name or None)

            logger.debug(f"Fork created successfully: {forked_repo.full_name}")

            # Wait a bit for fork to be ready
            await asyncio.sleep(2)

            # Create repository info for the fork
            fork_repo_info = RepositoryInfo(
                owner=forked_repo.owner.login,
                name=forked_repo.name,
                default_branch=forked_repo.default_branch,
            )

            return GitHubForkResult(
                success=True,
                source_repo=source_repo,
                target_repo=fork_repo_info,
                fork_url=forked_repo.html_url,
                processing_time=time.time() - start_time,
                metadata={
                    "fork_id": forked_repo.id,
                    "fork_full_name": forked_repo.full_name,
                    "default_branch": forked_repo.default_branch,
                    "private": forked_repo.private,
                },
            )

        except GithubException as e:
            # Handle specific GitHub API errors
            error_msg = (
                f"GitHub API error: {str(e) if e else 'Unknown GitHub API error'}"
            )
            status_code = getattr(e, "status", None)

            if status_code == 422:
                # Repository already forked or validation error
                error_msg = f"Fork already exists or validation error: {str(e)}"
                logger.warning(
                    f"Repository {source_repo.full_name} already forked or validation error: {str(e)}"
                )
            elif status_code == 403:
                # Forbidden - insufficient permissions or rate limited
                error_msg = f"Insufficient permissions or rate limited: {str(e)}"
                logger.error(
                    f"Insufficient permissions to fork {source_repo.full_name}: {str(e)}"
                )
            elif status_code == 404:
                # Repository not found or private
                error_msg = f"Repository not found or private: {str(e)}"
                logger.error(
                    f"Repository {source_repo.full_name} not found or private: {str(e)}"
                )
            else:
                if status_code:
                    error_msg += f" (Status: {status_code})"
                if hasattr(e, "data") and e.data:
                    error_msg += f" (Details: {e.data})"
                logger.error(
                    f"GitHub API error forking repository {source_repo.full_name}: {error_msg}"
                )

            return GitHubForkResult(
                success=False,
                error=error_msg,
                source_repo=source_repo,
                processing_time=time.time() - start_time,
            )
        except Exception as e:
            error_msg = f"Error forking repository: {str(e) if e else 'Unknown error'}"
            logger.error(
                f"Error forking repository {source_repo.full_name}: {error_msg}"
            )
            logger.error(f"Exception type: {type(e).__name__}")
            return GitHubForkResult(
                success=False,
                error=error_msg,
                source_repo=source_repo,
                processing_time=time.time() - start_time,
            )

    async def fork_repository(self, github_url: str) -> Dict[str, Any]:
        """
        Fork a repository from a GitHub URL - Wrapper method for background tasks

        Args:
            github_url: Full GitHub repository URL (e.g., https://github.com/owner/repo)

        Returns:
            Dictionary with success status and forked repository details
        """
        try:
            # Parse GitHub URL to extract owner and repo name
            repo_info = self._parse_github_url(github_url)
            if not repo_info:
                return {
                    "success": False,
                    "error": f"Invalid GitHub URL format: {github_url}",
                    "forked_url": None,
                }

            # Create RepositoryInfo object
            source_repo = RepositoryInfo(
                owner=repo_info["owner"],
                name=repo_info["repo_name"],
                default_branch="main",  # Will be updated by GitHub API
            )

            # Fork the repository using the main fork method
            fork_result = await self.fork_repository_internal(source_repo)

            if fork_result.success:
                return {
                    "success": True,
                    "error": None,
                    "forked_url": fork_result.fork_url,
                    "fork_full_name": (
                        fork_result.metadata.get("fork_full_name")
                        if fork_result.metadata
                        else None
                    ),
                    "default_branch": (
                        fork_result.metadata.get("default_branch")
                        if fork_result.metadata
                        else None
                    ),
                }
            else:
                error_msg = (
                    fork_result.error if fork_result.error else "Unknown fork failure"
                )
                logger.error(f"Fork operation failed for {github_url}: {error_msg}")
                return {"success": False, "error": error_msg, "forked_url": None}

        except Exception as e:
            logger.error(f"Error in fork_repository wrapper: {str(e)}")
            return {"success": False, "error": str(e), "forked_url": None}

    def _parse_github_url(self, github_url: str) -> Optional[Dict[str, str]]:
        """
        Parse a GitHub URL to extract owner and repository name

        Args:
            github_url: GitHub repository URL

        Returns:
            Dictionary with owner and repo_name, or None if invalid
        """
        try:
            # Handle different GitHub URL formats
            url = github_url.strip().rstrip("/")

            # Remove protocol if present
            if url.startswith(("http://", "https://")):
                url = url.split("://", 1)[1]

            # Remove github.com/ prefix
            if url.startswith("github.com/"):
                url = url[11:]
            elif url.startswith("www.github.com/"):
                url = url[15:]

            # Split into parts
            parts = url.split("/")

            if len(parts) >= 2:
                return {"owner": parts[0], "repo_name": parts[1]}
            else:
                return None

        except Exception as e:
            logger.error(f"Error parsing GitHub URL {github_url}: {str(e)}")
            return None

    async def clone_repository(
        self,
        repo: RepositoryInfo,
        target_dir: Optional[str] = None,
        branch: Optional[str] = None,
        depth: int = 1,
        use_ssh: bool = False,
    ) -> GitHubCloneResult:
        """
        Clone a repository to a local directory

        Args:
            repo: Repository to clone
            target_dir: Target directory (creates temp dir if None)
            branch: Specific branch to clone
            depth: Clone depth (1 for shallow clone)
            use_ssh: Use SSH for cloning

        Returns:
            GitHubCloneResult with clone details
        """
        start_time = time.time()

        try:
            # Determine clone URL
            clone_url = repo.ssh_url if use_ssh else repo.clone_url
            if not clone_url:
                raise ValueError("Clone URL is required")

            # Create target directory
            if target_dir is None:
                target_dir = tempfile.mkdtemp(prefix="github_clone_")
                self._temp_directories.append(target_dir)
            else:
                os.makedirs(target_dir, exist_ok=True)

            logger.info(f"Cloning repository {repo.full_name} to {target_dir}")

            # Clone repository
            clone_args = {
                "depth": depth if depth > 0 else None,
                "branch": branch or repo.default_branch,
            }

            # Remove None values
            clone_args = {k: v for k, v in clone_args.items() if v is not None}

            git_repo = git.Repo.clone_from(clone_url, target_dir, **clone_args)

            # Configure git user if provided
            if self.config.git_user_name:
                git_repo.config_writer().set_value(
                    "user", "name", self.config.git_user_name
                ).release()
            if self.config.git_user_email:
                git_repo.config_writer().set_value(
                    "user", "email", self.config.git_user_email
                ).release()

            return GitHubCloneResult(
                success=True,
                source_repo=repo,
                local_path=target_dir,
                processing_time=time.time() - start_time,
                metadata={
                    "clone_url": clone_url,
                    "branch": branch or repo.default_branch,
                    "depth": depth,
                    "use_ssh": use_ssh,
                    "head_commit": git_repo.head.commit.hexsha,
                },
            )

        except Exception as e:
            logger.error(f"Error cloning repository: {str(e)}")
            return GitHubCloneResult(
                success=False,
                error=str(e),
                source_repo=repo,
                processing_time=time.time() - start_time,
            )

    async def apply_file_operations(
        self, repo_path: str, file_operations: List[FileOperation]
    ) -> Dict[str, List[str]]:
        """
        Apply file operations to a local repository

        Args:
            repo_path: Path to local repository
            file_operations: List of file operations to apply

        Returns:
            Dictionary with lists of files by operation type
        """
        result = {"created": [], "updated": [], "deleted": []}

        for operation in file_operations:
            file_path = os.path.join(repo_path, operation.path)

            try:
                if (
                    operation.action == GitCommitAction.CREATE
                    or operation.action == GitCommitAction.UPDATE
                ):
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # Write file content
                    with open(file_path, "w", encoding=operation.encoding) as f:
                        f.write(operation.content or "")

                    if operation.action == GitCommitAction.CREATE:
                        result["created"].append(operation.path)
                    else:
                        result["updated"].append(operation.path)

                elif operation.action == GitCommitAction.DELETE:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        result["deleted"].append(operation.path)

                logger.info(f"Applied {operation.action} operation to {operation.path}")

            except Exception as e:
                logger.error(
                    f"Error applying {operation.action} to {operation.path}: {str(e)}"
                )
                raise

        return result

    async def commit_changes(
        self, repo_path: str, commit_info: CommitInfo
    ) -> GitHubCommitResult:
        """
        Commit changes to a local repository

        Args:
            repo_path: Path to local repository
            commit_info: Commit information

        Returns:
            GitHubCommitResult with commit details
        """
        start_time = time.time()

        try:
            logger.info(f"Committing changes to repository at {repo_path}")

            # Open git repository
            git_repo = git.Repo(repo_path)

            # Apply file operations
            file_results = await self.apply_file_operations(
                repo_path, commit_info.files
            )

            # Add files to git
            for operation in commit_info.files:
                if operation.action == GitCommitAction.DELETE:
                    git_repo.index.remove([operation.path])
                else:
                    git_repo.index.add([operation.path])

            # Configure commit author if provided
            actor = None
            if commit_info.author_name and commit_info.author_email:
                actor = git.Actor(commit_info.author_name, commit_info.author_email)
            elif self.config.git_user_name and self.config.git_user_email:
                actor = git.Actor(self.config.git_user_name, self.config.git_user_email)

            # Make commit
            if actor:
                commit = git_repo.index.commit(
                    commit_info.message, author=actor, committer=actor
                )
            else:
                commit = git_repo.index.commit(commit_info.message)

            return GitHubCommitResult(
                success=True,
                commit_sha=commit.hexsha,
                branch=commit_info.branch,
                files_added=file_results["created"],
                files_updated=file_results["updated"],
                files_deleted=file_results["deleted"],
                files_modified=file_results["created"]
                + file_results["updated"]
                + file_results["deleted"],
                processing_time=time.time() - start_time,
                metadata={
                    "commit_message": commit_info.message,
                    "commit_author": str(commit.author),
                    "commit_date": commit.committed_datetime.isoformat(),
                    "total_files": len(commit_info.files),
                },
            )

        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            return GitHubCommitResult(
                success=False,
                error=str(e),
                branch=commit_info.branch,
                processing_time=time.time() - start_time,
            )

    async def push_changes(
        self,
        repo_path: str,
        repo_info: RepositoryInfo,
        branch: str = "main",
        use_ssh: bool = False,
    ) -> GitHubPushResult:
        """
        Push changes to remote repository

        Args:
            repo_path: Path to local repository
            repo_info: Repository information
            branch: Branch to push
            use_ssh: Use SSH for pushing

        Returns:
            GitHubPushResult with push details
        """
        start_time = time.time()

        try:
            logger.info(f"Pushing changes to {repo_info.full_name}:{branch}")

            # Open git repository
            git_repo = git.Repo(repo_path)

            # Get remote URL
            remote_url = repo_info.ssh_url if use_ssh else repo_info.clone_url

            # If using HTTPS with token, include token in URL
            if not use_ssh and self.config.token:
                # Replace https://github.com with https://token@github.com
                if remote_url.startswith("https://github.com/"):
                    remote_url = remote_url.replace(
                        "https://github.com/",
                        f"https://{self.config.token}@github.com/",
                    )

            # Set remote URL (in case it changed)
            origin = git_repo.remote("origin")
            origin.set_url(remote_url)

            # Push to remote
            push_info = origin.push(branch)

            return GitHubPushResult(
                success=True,
                remote_url=repo_info.url,
                branch=branch,
                processing_time=time.time() - start_time,
                metadata={
                    "push_info": [str(info) for info in push_info],
                    "remote_url": remote_url,
                    "use_ssh": use_ssh,
                },
            )

        except Exception as e:
            logger.error(f"Error pushing changes: {str(e)}")
            return GitHubPushResult(
                success=False,
                error=str(e),
                remote_url=repo_info.url,
                branch=branch,
                processing_time=time.time() - start_time,
            )

    async def fork_and_modify(
        self, request: ForkAndModifyRequest
    ) -> GitHubForkAndModifyResult:
        """
        Complete workflow: Fork repository, clone, modify files, commit, and push

        Args:
            request: Complete request configuration

        Returns:
            GitHubForkAndModifyResult with all operation results
        """
        start_time = time.time()

        try:
            logger.info(
                f"Starting fork and modify workflow for {request.source_repo.full_name}"
            )

            # Step 1: Fork repository
            fork_result = await self.fork_repository_internal(
                source_repo=request.source_repo,
                fork_name=request.fork_config.fork_name,
                organization=request.fork_config.organization,
            )

            if not fork_result.success:
                return GitHubForkAndModifyResult(
                    success=False,
                    error=f"Fork failed: {fork_result.error}",
                    source_repo=request.source_repo,
                    fork_result=fork_result,
                    processing_time=time.time() - start_time,
                )

            # Step 2: Clone the fork
            clone_config = request.clone_config or CloneConfig(
                repo=fork_result.target_repo
            )
            clone_result = await self.clone_repository(
                repo=fork_result.target_repo,
                branch=clone_config.branch,
                depth=clone_config.depth,
                use_ssh=clone_config.use_ssh,
            )

            if not clone_result.success:
                return GitHubForkAndModifyResult(
                    success=False,
                    error=f"Clone failed: {clone_result.error}",
                    source_repo=request.source_repo,
                    target_repo=fork_result.target_repo,
                    fork_result=fork_result,
                    clone_result=clone_result,
                    processing_time=time.time() - start_time,
                )

            # Step 3: Commit changes
            commit_result = await self.commit_changes(
                repo_path=clone_result.local_path, commit_info=request.commit_info
            )

            if not commit_result.success:
                return GitHubForkAndModifyResult(
                    success=False,
                    error=f"Commit failed: {commit_result.error}",
                    source_repo=request.source_repo,
                    target_repo=fork_result.target_repo,
                    fork_result=fork_result,
                    clone_result=clone_result,
                    commit_result=commit_result,
                    processing_time=time.time() - start_time,
                )

            # Step 4: Push changes (if requested)
            push_result = None
            if request.push_after_commit:
                push_result = await self.push_changes(
                    repo_path=clone_result.local_path,
                    repo_info=fork_result.target_repo,
                    branch=request.commit_info.branch,
                    use_ssh=clone_config.use_ssh,
                )

                if not push_result.success:
                    return GitHubForkAndModifyResult(
                        success=False,
                        error=f"Push failed: {push_result.error}",
                        source_repo=request.source_repo,
                        target_repo=fork_result.target_repo,
                        fork_result=fork_result,
                        clone_result=clone_result,
                        commit_result=commit_result,
                        push_result=push_result,
                        processing_time=time.time() - start_time,
                    )

            # Step 5: Cleanup (if requested)
            temp_dir = clone_result.local_path
            if request.cleanup_after:
                try:
                    shutil.rmtree(clone_result.local_path)
                    if clone_result.local_path in self._temp_directories:
                        self._temp_directories.remove(clone_result.local_path)
                    temp_dir = None
                except Exception as e:
                    logger.warning(f"Failed to cleanup temporary directory: {str(e)}")

            return GitHubForkAndModifyResult(
                success=True,
                source_repo=request.source_repo,
                target_repo=fork_result.target_repo,
                fork_url=fork_result.fork_url,
                commit_sha=commit_result.commit_sha,
                files_modified=commit_result.files_modified,
                temp_directory=temp_dir,
                fork_result=fork_result,
                clone_result=clone_result,
                commit_result=commit_result,
                push_result=push_result,
                processing_time=time.time() - start_time,
                metadata={
                    "workflow_steps": [
                        "fork" if fork_result.success else "fork_failed",
                        "clone" if clone_result.success else "clone_failed",
                        "commit" if commit_result.success else "commit_failed",
                        (
                            "push"
                            if push_result and push_result.success
                            else "push_skipped_or_failed"
                        ),
                        "cleanup" if request.cleanup_after else "no_cleanup",
                    ],
                    "total_files_modified": (
                        len(commit_result.files_modified)
                        if commit_result.success
                        else 0
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Error in fork and modify workflow: {str(e)}")
            return GitHubForkAndModifyResult(
                success=False,
                error=str(e),
                source_repo=request.source_repo,
                processing_time=time.time() - start_time,
            )

    async def health_check(self) -> Dict[str, Any]:
        """
        Check GitHub service health

        Returns:
            Dictionary with health status
        """
        try:
            # Test GitHub API connection
            user = self.github_client.get_user()

            return {
                "github_api": {
                    "available": True,
                    "authenticated_user": user.login,
                    "rate_limit_remaining": self.github_client.get_rate_limit().core.remaining,
                    "error": None,
                },
                "git_config": {
                    "user_name": self.config.git_user_name,
                    "user_email": self.config.git_user_email,
                    "configured": bool(
                        self.config.git_user_name and self.config.git_user_email
                    ),
                },
            }

        except Exception as e:
            return {
                "github_api": {"available": False, "error": str(e)},
                "git_config": {
                    "user_name": self.config.git_user_name,
                    "user_email": self.config.git_user_email,
                    "configured": bool(
                        self.config.git_user_name and self.config.git_user_email
                    ),
                },
            }


# Create a singleton instance (will be created when GitHub token is available)
def create_github_service(config: Optional[GitHubConfig] = None) -> GitHubService:
    """Create a GitHub service instance"""
    return GitHubService(config)


# Default instance (only created if token is available)
try:
    github_service = create_github_service()
except ValueError:
    github_service = None
    logger.warning("GitHub service not initialized - missing GitHub token")

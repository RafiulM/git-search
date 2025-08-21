"""
GitHub Configuration Models for repository operations
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class GitHubAuthMethod(str, Enum):
    """GitHub authentication methods"""
    TOKEN = "token"
    APP = "app"


class GitCommitAction(str, Enum):
    """Git commit actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class GitHubConfig(BaseModel):
    """Configuration for GitHub operations"""
    token: str = Field(description="GitHub personal access token")
    auth_method: GitHubAuthMethod = Field(default=GitHubAuthMethod.TOKEN, description="Authentication method")
    base_url: str = Field(default="https://api.github.com", description="GitHub API base URL")
    
    # Git configuration
    git_user_name: Optional[str] = Field(default=None, description="Git user name for commits")
    git_user_email: Optional[str] = Field(default=None, description="Git user email for commits")


class RepositoryInfo(BaseModel):
    """Information about a repository"""
    owner: str = Field(description="Repository owner")
    name: str = Field(description="Repository name")
    full_name: Optional[str] = Field(default=None, description="Full repository name (owner/name)")
    url: Optional[HttpUrl] = Field(default=None, description="Repository URL")
    clone_url: Optional[str] = Field(default=None, description="Clone URL")
    ssh_url: Optional[str] = Field(default=None, description="SSH URL")
    default_branch: str = Field(default="main", description="Default branch name")
    
    def model_post_init(self, __context: Any) -> None:
        """Set computed fields after initialization"""
        if not self.full_name:
            self.full_name = f"{self.owner}/{self.name}"
        if not self.url:
            self.url = f"https://github.com/{self.owner}/{self.name}"
        if not self.clone_url:
            self.clone_url = f"https://github.com/{self.owner}/{self.name}.git"
        if not self.ssh_url:
            self.ssh_url = f"git@github.com:{self.owner}/{self.name}.git"


class FileOperation(BaseModel):
    """Represents a file operation (create, update, delete)"""
    action: GitCommitAction = Field(description="Action to perform on the file")
    path: str = Field(description="File path relative to repository root")
    content: Optional[str] = Field(default=None, description="File content (for create/update)")
    encoding: str = Field(default="utf-8", description="File encoding")
    message: Optional[str] = Field(default=None, description="Optional specific message for this file")


class CommitInfo(BaseModel):
    """Information about a commit"""
    message: str = Field(description="Commit message")
    author_name: Optional[str] = Field(default=None, description="Commit author name")
    author_email: Optional[str] = Field(default=None, description="Commit author email")
    branch: str = Field(default="main", description="Target branch")
    files: List[FileOperation] = Field(default_factory=list, description="File operations to include in commit")


class ForkConfig(BaseModel):
    """Configuration for forking a repository"""
    source_repo: RepositoryInfo = Field(description="Source repository to fork")
    fork_name: Optional[str] = Field(default=None, description="Name for the fork (defaults to source name)")
    organization: Optional[str] = Field(default=None, description="Organization to fork to (defaults to user)")
    default_branch_only: bool = Field(default=True, description="Only fork the default branch")


class CloneConfig(BaseModel):
    """Configuration for cloning a repository"""
    repo: RepositoryInfo = Field(description="Repository to clone")
    branch: Optional[str] = Field(default=None, description="Specific branch to clone")
    depth: Optional[int] = Field(default=1, description="Clone depth (1 for shallow clone)")
    use_ssh: bool = Field(default=False, description="Use SSH for cloning")


class GitHubOperationRequest(BaseModel):
    """Base request for GitHub operations"""
    github_config: GitHubConfig = Field(description="GitHub configuration")
    source_repo: RepositoryInfo = Field(description="Source repository")
    target_repo: Optional[RepositoryInfo] = Field(default=None, description="Target repository (for fork operations)")


class ForkAndModifyRequest(GitHubOperationRequest):
    """Request to fork a repository and make modifications"""
    fork_config: ForkConfig = Field(description="Fork configuration")
    clone_config: Optional[CloneConfig] = Field(default=None, description="Clone configuration")
    commit_info: CommitInfo = Field(description="Commit information")
    push_after_commit: bool = Field(default=True, description="Push changes after committing")
    cleanup_after: bool = Field(default=True, description="Cleanup temporary files after operation")


class GitHubOperationResult(BaseModel):
    """Result of a GitHub operation"""
    success: bool = Field(description="Whether the operation was successful")
    error: Optional[str] = Field(default=None, description="Error message if operation failed")
    
    # Operation details
    operation_type: str = Field(description="Type of operation performed")
    source_repo: Optional[RepositoryInfo] = Field(default=None, description="Source repository")
    target_repo: Optional[RepositoryInfo] = Field(default=None, description="Target repository (fork)")
    
    # Results
    fork_url: Optional[str] = Field(default=None, description="URL of created fork")
    commit_sha: Optional[str] = Field(default=None, description="SHA of created commit")
    files_modified: List[str] = Field(default_factory=list, description="List of files that were modified")
    
    # Metadata
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")
    temp_directory: Optional[str] = Field(default=None, description="Temporary directory used (if not cleaned up)")
    
    # Additional data
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional operation metadata")


class GitHubForkResult(GitHubOperationResult):
    """Result of a fork operation"""
    operation_type: str = Field(default="fork", description="Operation type")


class GitHubCloneResult(GitHubOperationResult):
    """Result of a clone operation"""
    operation_type: str = Field(default="clone", description="Operation type")
    local_path: Optional[str] = Field(default=None, description="Local path where repository was cloned")


class GitHubCommitResult(GitHubOperationResult):
    """Result of a commit operation"""
    operation_type: str = Field(default="commit", description="Operation type")
    branch: Optional[str] = Field(default=None, description="Branch where commit was made")
    files_added: List[str] = Field(default_factory=list, description="Files added in commit")
    files_updated: List[str] = Field(default_factory=list, description="Files updated in commit")
    files_deleted: List[str] = Field(default_factory=list, description="Files deleted in commit")


class GitHubPushResult(GitHubOperationResult):
    """Result of a push operation"""
    operation_type: str = Field(default="push", description="Operation type")
    remote_url: Optional[str] = Field(default=None, description="Remote URL pushed to")
    branch: Optional[str] = Field(default=None, description="Branch pushed")


class GitHubForkAndModifyResult(GitHubOperationResult):
    """Result of a complete fork and modify operation"""
    operation_type: str = Field(default="fork_and_modify", description="Operation type")
    
    # Sub-operation results
    fork_result: Optional[GitHubForkResult] = Field(default=None, description="Fork operation result")
    clone_result: Optional[GitHubCloneResult] = Field(default=None, description="Clone operation result")
    commit_result: Optional[GitHubCommitResult] = Field(default=None, description="Commit operation result")
    push_result: Optional[GitHubPushResult] = Field(default=None, description="Push operation result")


# Utility functions for creating common configurations

def create_basic_github_config(token: str, user_name: str = None, user_email: str = None) -> GitHubConfig:
    """Create a basic GitHub configuration"""
    return GitHubConfig(
        token=token,
        git_user_name=user_name,
        git_user_email=user_email
    )


def create_repository_info(owner: str, name: str, branch: str = "main") -> RepositoryInfo:
    """Create repository information"""
    return RepositoryInfo(
        owner=owner,
        name=name,
        default_branch=branch
    )


def create_file_operation(action: GitCommitAction, path: str, content: str = None) -> FileOperation:
    """Create a file operation"""
    return FileOperation(
        action=action,
        path=path,
        content=content
    )


def create_commit_info(message: str, files: List[FileOperation], branch: str = "main") -> CommitInfo:
    """Create commit information"""
    return CommitInfo(
        message=message,
        files=files,
        branch=branch
    )


# Example configurations

EXAMPLE_FORK_CONFIG = ForkConfig(
    source_repo=RepositoryInfo(owner="original-owner", name="repo-name"),
    fork_name="my-fork",
    default_branch_only=True
)

EXAMPLE_COMMIT_INFO = CommitInfo(
    message="Add new feature",
    branch="main",
    files=[
        FileOperation(
            action=GitCommitAction.CREATE,
            path="new-file.txt",
            content="This is a new file"
        ),
        FileOperation(
            action=GitCommitAction.UPDATE,
            path="existing-file.txt",
            content="Updated content"
        )
    ]
)
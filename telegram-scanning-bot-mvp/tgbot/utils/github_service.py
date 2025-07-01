"""
GitHub API Service for Telegram Bot
Handles GitHub repository operations, issue management, and API interactions.
"""

import logging
import asyncio
from typing import Optional, Dict, List, Any
from github import Github, Auth
from github.GithubException import GithubException
import aiohttp
import json

from ..config import config

logger = logging.getLogger(__name__)

class GitHubService:
    """GitHub API service for bot operations."""
    
    def __init__(self):
        """Initialize GitHub service with authentication."""
        self.github = None
        self.authenticated = False
        self._setup_github_client()
    
    def _setup_github_client(self):
        """Setup GitHub client with authentication."""
        try:
            if config.GITHUB_TOKEN:
                # Use token authentication
                auth = Auth.Token(config.GITHUB_TOKEN)
                self.github = Github(auth=auth)
                
                # Test authentication
                user = self.github.get_user()
                logger.info(f"GitHub authenticated as: {user.login}")
                self.authenticated = True
            else:
                logger.warning("GitHub token not provided - using unauthenticated access")
                self.github = Github()
                self.authenticated = False
                
        except GithubException as e:
            logger.error(f"GitHub authentication failed: {e}")
            self.authenticated = False
        except Exception as e:
            logger.error(f"Error setting up GitHub client: {e}")
            self.authenticated = False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test GitHub API connection and return status."""
        try:
            if not self.github:
                return {
                    "success": False,
                    "error": "GitHub client not initialized",
                    "authenticated": False
                }
            
            # Test API access
            rate_limit = self.github.get_rate_limit()
            user = self.github.get_user() if self.authenticated else None
            
            return {
                "success": True,
                "authenticated": self.authenticated,
                "user": user.login if user else None,
                "rate_limit": {
                    "core": {
                        "limit": rate_limit.core.limit,
                        "remaining": rate_limit.core.remaining,
                        "reset": rate_limit.core.reset.isoformat()
                    }
                }
            }
            
        except GithubException as e:
            logger.error(f"GitHub API test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "authenticated": self.authenticated
            }
        except Exception as e:
            logger.error(f"Unexpected error testing GitHub connection: {e}")
            return {
                "success": False,
                "error": str(e),
                "authenticated": False
            }
    
    async def get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """Get repository information."""
        try:
            if not self.github:
                return {"success": False, "error": "GitHub client not available"}
            
            repo = self.github.get_repo(repo_name)
            
            return {
                "success": True,
                "repository": {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "issues": repo.open_issues_count,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                    "url": repo.html_url,
                    "clone_url": repo.clone_url
                }
            }
            
        except GithubException as e:
            logger.error(f"Error getting repository info: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_repositories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for repositories."""
        try:
            if not self.github:
                return {"success": False, "error": "GitHub client not available"}
            
            repositories = self.github.search_repositories(query)
            
            results = []
            count = 0
            for repo in repositories:
                if count >= limit:
                    break
                
                results.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "url": repo.html_url
                })
                count += 1
            
            return {
                "success": True,
                "total_count": repositories.totalCount,
                "results": results
            }
            
        except GithubException as e:
            logger.error(f"Error searching repositories: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_repositories(self, username: str) -> Dict[str, Any]:
        """Get user's repositories."""
        try:
            if not self.github:
                return {"success": False, "error": "GitHub client not available"}
            
            user = self.github.get_user(username)
            repos = user.get_repos()
            
            repositories = []
            for repo in repos:
                repositories.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "private": repo.private,
                    "url": repo.html_url,
                    "updated_at": repo.updated_at.isoformat()
                })
            
            return {
                "success": True,
                "user": username,
                "repositories": repositories
            }
            
        except GithubException as e:
            logger.error(f"Error getting user repositories: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_issue(self, repo_name: str, title: str, body: str, labels: List[str] = None) -> Dict[str, Any]:
        """Create an issue in a repository."""
        try:
            if not self.authenticated:
                return {"success": False, "error": "Authentication required for creating issues"}
            
            repo = self.github.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body, labels=labels or [])
            
            return {
                "success": True,
                "issue": {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat()
                }
            }
            
        except GithubException as e:
            logger.error(f"Error creating issue: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close GitHub client resources."""
        try:
            if self.github:
                # PyGithub doesn't have explicit close method
                # but we can clear the reference
                self.github = None
                logger.info("GitHub service closed")
        except Exception as e:
            logger.error(f"Error closing GitHub service: {e}")

# Global GitHub service instance
github_service = GitHubService()

async def test_github_connection() -> Dict[str, Any]:
    """Convenience function to test GitHub connection."""
    return await github_service.test_connection()
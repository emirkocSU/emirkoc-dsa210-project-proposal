"""
GitHub handler for Telegram bot.
Handles GitHub-related commands and operations.
"""

import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from ..utils.github_service import github_service

logger = logging.getLogger(__name__)

# Create router for GitHub handlers
router = Router()

@router.message(Command("github"))
async def cmd_github_test(message: Message):
    """Test GitHub connection command."""
    try:
        await message.answer("🔍 Testing GitHub connection...")
        
        # Test GitHub connection
        result = await github_service.test_connection()
        
        if result["success"]:
            status = "✅ Connected" if result["authenticated"] else "⚠️ Connected (unauthenticated)"
            user_info = f"User: {result['user']}" if result.get('user') else "User: Anonymous"
            rate_limit = result.get('rate_limit', {}).get('core', {})
            
            response = f"""
🔗 <b>GitHub Connection Status</b>

{status}
{user_info}

📊 <b>Rate Limit:</b>
• Limit: {rate_limit.get('limit', 'N/A')}
• Remaining: {rate_limit.get('remaining', 'N/A')}
• Reset: {rate_limit.get('reset', 'N/A')}
            """
        else:
            response = f"""
❌ <b>GitHub Connection Failed</b>

Error: {result['error']}
Authenticated: {result.get('authenticated', False)}

💡 <b>Troubleshooting:</b>
1. Check if GITHUB_TOKEN is set in .env file
2. Verify token permissions
3. Check network connectivity
            """
        
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Error in GitHub test command: {e}")
        await message.answer(f"❌ Error testing GitHub connection: {str(e)}")

@router.message(Command("repo"))
async def cmd_repo_info(message: Message):
    """Get repository information command."""
    try:
        # Extract repository name from command
        command_args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not command_args:
            await message.answer("""
📖 <b>Repository Info Command</b>

Usage: <code>/repo owner/repository</code>

Example: <code>/repo microsoft/vscode</code>
            """)
            return
        
        repo_name = command_args[0]
        await message.answer(f"🔍 Getting info for repository: {repo_name}")
        
        # Get repository information
        result = await github_service.get_repository_info(repo_name)
        
        if result["success"]:
            repo = result["repository"]
            response = f"""
📦 <b>{repo['name']}</b>

<b>Description:</b> {repo['description'] or 'No description'}
<b>Language:</b> {repo['language'] or 'N/A'}
<b>Stars:</b> ⭐ {repo['stars']}
<b>Forks:</b> 🍴 {repo['forks']}
<b>Open Issues:</b> 🐛 {repo['issues']}

<b>Created:</b> {repo['created_at'][:10]}
<b>Updated:</b> {repo['updated_at'][:10]}

🔗 <a href="{repo['url']}">View on GitHub</a>
            """
        else:
            response = f"❌ Error getting repository info: {result['error']}"
        
        await message.answer(response, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Error in repo info command: {e}")
        await message.answer(f"❌ Error: {str(e)}")

@router.message(Command("search"))
async def cmd_search_repos(message: Message):
    """Search repositories command."""
    try:
        # Extract search query from command
        command_args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not command_args:
            await message.answer("""
🔍 <b>Repository Search Command</b>

Usage: <code>/search query</code>

Example: <code>/search machine learning</code>
            """)
            return
        
        query = " ".join(command_args)
        await message.answer(f"🔍 Searching repositories for: {query}")
        
        # Search repositories
        result = await github_service.search_repositories(query, limit=5)
        
        if result["success"]:
            if result["results"]:
                response = f"🔍 <b>Search Results for '{query}'</b>\n"
                response += f"Total found: {result['total_count']}\n\n"
                
                for i, repo in enumerate(result["results"], 1):
                    response += f"{i}. <b>{repo['name']}</b>\n"
                    response += f"   {repo['description'] or 'No description'}\n"
                    response += f"   Language: {repo['language'] or 'N/A'} | ⭐ {repo['stars']}\n"
                    response += f"   🔗 <a href='{repo['url']}'>{repo['full_name']}</a>\n\n"
            else:
                response = f"No repositories found for '{query}'"
        else:
            response = f"❌ Error searching repositories: {result['error']}"
        
        await message.answer(response, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Error in search command: {e}")
        await message.answer(f"❌ Error: {str(e)}")
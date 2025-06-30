"""
Throttling middleware for rate limiting user requests.
Prevents spam and ensures optimal bot performance.
"""

import asyncio
import logging
from typing import Dict, Any, Callable, Awaitable
from datetime import datetime, timedelta
from cachetools import TTLCache

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from config import config

logger = logging.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for throttling user requests to prevent spam.
    Uses TTL cache to track user request rates.
    """
    
    def __init__(
        self,
        rate_limit: int = None,
        time_window: int = None,
        key_generator: Callable[[TelegramObject], str] = None
    ):
        """
        Initialize throttling middleware.
        
        Args:
            rate_limit: Maximum number of messages per time window
            time_window: Time window in seconds
            key_generator: Function to generate cache key from update
        """
        self.rate_limit = rate_limit or config.RATE_LIMIT_MESSAGES
        self.time_window = time_window or config.RATE_LIMIT_WINDOW
        self.key_generator = key_generator or self._default_key_generator
        
        # TTL cache to store user request counts
        self.cache: TTLCache = TTLCache(
            maxsize=10000,  # Store up to 10k users
            ttl=self.time_window
        )
        
        logger.info(
            f"Throttling middleware initialized: "
            f"{self.rate_limit} messages per {self.time_window} seconds"
        )
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process incoming update with rate limiting.
        
        Args:
            handler: Next handler in the chain
            event: Telegram update object
            data: Handler data
            
        Returns:
            Handler result or None if throttled
        """
        # Generate cache key for this user/chat
        cache_key = self.key_generator(event)
        
        if not cache_key:
            # If we can't generate a key, allow the request
            return await handler(event, data)
        
        # Get current request count for this key
        current_count = self.cache.get(cache_key, 0)
        
        # Check if rate limit exceeded
        if current_count >= self.rate_limit:
            await self._handle_rate_limit_exceeded(event, current_count)
            return None  # Don't process the update
        
        # Increment counter
        self.cache[cache_key] = current_count + 1
        
        # Log rate limiting info (debug level)
        logger.debug(
            f"Rate limit check: {cache_key} = {current_count + 1}/{self.rate_limit}"
        )
        
        # Process the update
        return await handler(event, data)
    
    def _default_key_generator(self, event: TelegramObject) -> str:
        """
        Default key generator based on user ID.
        
        Args:
            event: Telegram update object
            
        Returns:
            Cache key string or empty string if no user found
        """
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        
        return f"user:{user_id}" if user_id else ""
    
    async def _handle_rate_limit_exceeded(self, event: TelegramObject, current_count: int):
        """
        Handle rate limit exceeded scenario.
        
        Args:
            event: Telegram update object
            current_count: Current request count for user
        """
        # Try to send warning message to user
        try:
            if isinstance(event, Message):
                # Send rate limit warning
                warning_text = (
                    "⚠️ <b>Rate limit exceeded</b>\n\n"
                    f"You're sending messages too quickly. "
                    f"Please wait a moment before trying again.\n\n"
                    f"<i>Limit: {self.rate_limit} messages per {self.time_window} seconds</i>"
                )
                
                await event.answer(
                    warning_text,
                    parse_mode="HTML"
                )
                
                logger.warning(
                    f"Rate limit exceeded for user {event.from_user.id}: "
                    f"{current_count} messages"
                )
            
        except Exception as e:
            logger.error(f"Error sending rate limit warning: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get current rate limiting stats for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with user stats
        """
        cache_key = f"user:{user_id}"
        current_count = self.cache.get(cache_key, 0)
        
        return {
            "user_id": user_id,
            "current_count": current_count,
            "rate_limit": self.rate_limit,
            "time_window": self.time_window,
            "remaining": max(0, self.rate_limit - current_count)
        }
    
    def reset_user_limit(self, user_id: int) -> bool:
        """
        Reset rate limit for a specific user (admin function).
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if reset successful, False otherwise
        """
        try:
            cache_key = f"user:{user_id}"
            if cache_key in self.cache:
                del self.cache[cache_key]
                logger.info(f"Reset rate limit for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resetting rate limit for user {user_id}: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get overall cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return {
            "cache_size": len(self.cache),
            "max_size": self.cache.maxsize,
            "ttl": self.cache.ttl,
            "rate_limit": self.rate_limit,
            "time_window": self.time_window
        }

class CommandThrottlingMiddleware(ThrottlingMiddleware):
    """
    Specialized throttling middleware for commands only.
    More restrictive rate limiting for command usage.
    """
    
    def __init__(self, command_rate_limit: int = 5, time_window: int = 60):
        """
        Initialize command throttling middleware.
        
        Args:
            command_rate_limit: Max commands per time window
            time_window: Time window in seconds
        """
        super().__init__(
            rate_limit=command_rate_limit,
            time_window=time_window,
            key_generator=self._command_key_generator
        )
    
    def _command_key_generator(self, event: TelegramObject) -> str:
        """
        Key generator that only applies to command messages.
        
        Args:
            event: Telegram update object
            
        Returns:
            Cache key for commands or empty string for non-commands
        """
        if isinstance(event, Message) and event.text and event.text.startswith('/'):
            user_id = event.from_user.id if event.from_user else None
            command = event.text.split()[0]  # Get the command part
            return f"cmd:{user_id}:{command}" if user_id else ""
        
        return ""  # Don't throttle non-command messages
    
    async def _handle_rate_limit_exceeded(self, event: TelegramObject, current_count: int):
        """
        Handle command rate limit exceeded.
        
        Args:
            event: Telegram update object
            current_count: Current command count for user
        """
        try:
            if isinstance(event, Message):
                warning_text = (
                    "⚠️ <b>Command rate limit exceeded</b>\n\n"
                    f"You're using commands too frequently. "
                    f"Please wait before using this command again.\n\n"
                    f"<i>Limit: {self.rate_limit} commands per {self.time_window} seconds</i>"
                )
                
                await event.answer(
                    warning_text,
                    parse_mode="HTML"
                )
                
                logger.warning(
                    f"Command rate limit exceeded for user {event.from_user.id}: "
                    f"command '{event.text}', count: {current_count}"
                )
                
        except Exception as e:
            logger.error(f"Error sending command rate limit warning: {e}")

# Factory functions for easy middleware creation
def create_throttling_middleware(
    rate_limit: int = None,
    time_window: int = None
) -> ThrottlingMiddleware:
    """
    Factory function to create throttling middleware with custom settings.
    
    Args:
        rate_limit: Messages per time window
        time_window: Time window in seconds
        
    Returns:
        Configured ThrottlingMiddleware instance
    """
    return ThrottlingMiddleware(
        rate_limit=rate_limit or config.RATE_LIMIT_MESSAGES,
        time_window=time_window or config.RATE_LIMIT_WINDOW
    )

def create_command_throttling_middleware(
    command_rate_limit: int = 5,
    time_window: int = 60
) -> CommandThrottlingMiddleware:
    """
    Factory function to create command throttling middleware.
    
    Args:
        command_rate_limit: Commands per time window
        time_window: Time window in seconds
        
    Returns:
        Configured CommandThrottlingMiddleware instance
    """
    return CommandThrottlingMiddleware(
        command_rate_limit=command_rate_limit,
        time_window=time_window
    )
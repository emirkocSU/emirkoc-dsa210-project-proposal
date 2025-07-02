"""
Custom filters for the Telegram Car Listing Bot.
Provides filters for subscription checking, user authorization, and admin privileges.
"""

import logging
from typing import Any, Dict, Optional
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery, TelegramObject

from database import db_manager

logger = logging.getLogger(__name__)

class UserIsSubscribed(BaseFilter):
    """Filter to check if user has an active subscription."""
    
    async def __call__(self, obj: TelegramObject) -> bool:
        """Check if user has active subscription."""
        try:
            # Get user ID from message or callback query
            if isinstance(obj, Message):
                telegram_id = obj.from_user.id
            elif isinstance(obj, CallbackQuery):
                telegram_id = obj.from_user.id
            else:
                return False
            
            # Get user from database
            user = await db_manager.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            # Check subscription status
            if not user.subscription_active:
                return False
            
            # Check subscription expiry if set
            if user.subscription_expires_at:
                from datetime import datetime
                if user.subscription_expires_at < datetime.utcnow():
                    # Subscription expired, update status
                    await db_manager.update_subscription_status(user.id, False)
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking subscription status: {e}")
            return False

class UserIsLinked(BaseFilter):
    """Filter to check if user has linked their Telegram account."""
    
    async def __call__(self, obj: TelegramObject) -> bool:
        """Check if user has linked account."""
        try:
            # Get user ID from message or callback query
            if isinstance(obj, Message):
                telegram_id = obj.from_user.id
            elif isinstance(obj, CallbackQuery):
                telegram_id = obj.from_user.id
            else:
                return False
            
            # Check if user exists in database
            user = await db_manager.get_user_by_telegram_id(telegram_id)
            return user is not None
            
        except Exception as e:
            logger.error(f"Error checking link status: {e}")
            return False

class UserHasFilters(BaseFilter):
    """Filter to check if user has set up search filters."""
    
    async def __call__(self, obj: TelegramObject) -> bool:
        """Check if user has filters configured."""
        try:
            # Get user ID from message or callback query
            if isinstance(obj, Message):
                telegram_id = obj.from_user.id
            elif isinstance(obj, CallbackQuery):
                telegram_id = obj.from_user.id
            else:
                return False
            
            # Get user from database
            user = await db_manager.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            # Check if filters are set
            return user.search_filters is not None and user.search_filters.strip() != ""
            
        except Exception as e:
            logger.error(f"Error checking filters: {e}")
            return False

class AdminFilter(BaseFilter):
    """Filter to check if user is an admin."""
    
    def __init__(self, admin_ids: Optional[list] = None):
        self.admin_ids = admin_ids or []
    
    async def __call__(self, obj: TelegramObject) -> bool:
        """Check if user is admin."""
        try:
            # Get user ID from message or callback query
            if isinstance(obj, Message):
                telegram_id = obj.from_user.id
            elif isinstance(obj, CallbackQuery):
                telegram_id = obj.from_user.id
            else:
                return False
            
            return telegram_id in self.admin_ids
            
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False

class ValidCarListingURL(BaseFilter):
    """Filter to validate car listing URLs."""
    
    def __init__(self, allowed_domains: Optional[list] = None):
        from config import config
        self.allowed_domains = allowed_domains or [config.LISTING_SITE_DOMAIN]
    
    async def __call__(self, obj: TelegramObject) -> bool:
        """Check if message contains valid car listing URL."""
        try:
            if not isinstance(obj, Message) or not obj.text:
                return False
            
            # Check if message contains URL
            import re
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, obj.text)
            
            if not urls:
                return False
            
            # Check if any URL is from allowed domains
            for url in urls:
                for domain in self.allowed_domains:
                    if domain in url:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False

# Convenience instances
user_is_subscribed = UserIsSubscribed()
user_is_linked = UserIsLinked()
user_has_filters = UserHasFilters()
valid_car_url = ValidCarListingURL()

# Admin filter would be initialized with actual admin IDs
# admin_filter = AdminFilter([123456789, 987654321])  # Replace with actual admin IDs
"""
Start command handler with deep linking and account linking functionality.
Handles the /start command, account linking via tokens, and user onboarding.
"""

import logging
from typing import Optional

from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.deep_linking import decode_payload, create_start_link

from database import db_manager
from utils.validators import SecurityValidator
from config import config

logger = logging.getLogger(__name__)

# Create router for start-related handlers
router = Router()

@router.message(CommandStart(deep_link=True))
async def start_with_deep_link(message: Message, command: CommandObject):
    """
    Handle /start command with deep link payload (account linking).
    
    Args:
        message: Telegram message object
        command: Command object with arguments
    """
    user = message.from_user
    if not user:
        await message.answer("❌ Unable to identify user. Please try again.")
        return
    
    logger.info(f"Deep link start from user {user.id} ({user.username})")
    
    try:
        # Extract and validate the deep link token
        token = command.args
        if not token:
            await handle_regular_start(message)
            return
        
        # Decode token if it was encoded
        try:
            decoded_token = decode_payload(token)
            if decoded_token:
                token = decoded_token
        except Exception:
            # If decoding fails, use the token as-is
            pass
        
        # Validate token format
        is_valid, error_msg = SecurityValidator.validate_token(token)
        if not is_valid:
            await message.answer(
                f"❌ <b>Invalid Link Token</b>\n\n"
                f"The link token is invalid: {error_msg}\n"
                f"Please request a new Telegram link from the app.",
                parse_mode="HTML"
            )
            return
        
        # Verify token and get associated user ID
        user_id = await db_manager.verify_link_token(token)
        if not user_id:
            await message.answer(
                "❌ <b>Invalid or Expired Link</b>\n\n"
                "This link token is either invalid, expired, or has already been used.\n"
                "Please generate a new Telegram link from the app.",
                parse_mode="HTML"
            )
            return
        
        # Check if this Telegram account is already linked
        existing_user = await db_manager.get_user_by_telegram_id(user.id)
        if existing_user:
            if existing_user.id == user_id:
                # Same user, already linked
                await message.answer(
                    f"✅ <b>Already Linked</b>\n\n"
                    f"Hello {user.full_name}! Your Telegram account is already linked to your app account.\n\n"
                    f"You can now use all bot features. Try /scan to start scanning URLs!",
                    parse_mode="HTML"
                )
            else:
                # Different user, conflict
                await message.answer(
                    "⚠️ <b>Account Conflict</b>\n\n"
                    "This Telegram account is already linked to a different app account.\n"
                    "Please use /unlink first if you want to link to a different account.",
                    parse_mode="HTML"
                )
            return
        
        # Link the accounts
        success = await db_manager.link_telegram_account(
            user_id=user_id,
            telegram_id=user.id,
            telegram_username=user.username
        )
        
        if success:
            # Get user details for personalized greeting
            app_user = await db_manager.get_user_by_telegram_id(user.id)
            user_name = app_user.full_name if app_user and app_user.full_name else user.full_name
            
            # Create welcome message with inline keyboard
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔍 Set Filters", callback_data="set_filters"),
                    InlineKeyboardButton(text="📖 Help", callback_data="help")
                ],
                [
                    InlineKeyboardButton(text="📊 My Alerts", callback_data="recent_alerts"),
                    InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")
                ]
            ])
            
            await message.answer(
                f"🎉 <b>Account Successfully Linked!</b>\n\n"
                f"Welcome, <b>{user_name}</b>! Your Telegram account is now connected to your Car Alert Bot account.\n\n"
                f"🚀 <b>You can now:</b>\n"
                f"• Set up car search filters\n"
                f"• Receive automatic alerts for new listings\n"
                f"• Get AI-powered damage analysis\n"
                f"• Access your alert history\n\n"
                f"<i>Start by setting up your car search filters with /filters!</i>",
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
            logger.info(f"Successfully linked Telegram user {user.id} to app user {user_id}")
        else:
            await message.answer(
                "❌ <b>Linking Failed</b>\n\n"
                "Unable to link your accounts due to a technical error.\n"
                "Please try again or contact support if the problem persists.",
                parse_mode="HTML"
            )
            logger.error(f"Failed to link Telegram user {user.id} to app user {user_id}")
    
    except Exception as e:
        logger.error(f"Error in deep link start handler: {e}")
        await message.answer(
            "❌ <b>Unexpected Error</b>\n\n"
            "An unexpected error occurred while processing your link.\n"
            "Please try again or contact support.",
            parse_mode="HTML"
        )

@router.message(CommandStart())
async def handle_regular_start(message: Message):
    """
    Handle regular /start command without deep link.
    
    Args:
        message: Telegram message object
    """
    user = message.from_user
    if not user:
        await message.answer("❌ Unable to identify user. Please try again.")
        return
    
    logger.info(f"Regular start from user {user.id} ({user.username})")
    
    # Check if user is already linked
    existing_user = await db_manager.get_user_by_telegram_id(user.id)
    
    if existing_user:
        # User is already linked
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Set Filters", callback_data="set_filters"),
                InlineKeyboardButton(text="📖 Help", callback_data="help")
            ],
            [
                InlineKeyboardButton(text="📊 My Alerts", callback_data="recent_alerts"),
                InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")
            ]
        ])
        
        await message.answer(
            f"👋 <b>Welcome back, {existing_user.full_name or user.full_name}!</b>\n\n"
            f"Your Car Alert Bot is ready to find your perfect car.\n\n"
            f"🔍 <b>Quick Actions:</b>\n"
            f"• Use <code>/filters</code> to set up your search criteria\n"
            f"• Send <code>/scan [URL]</code> to analyze a specific listing\n"
            f"• Check <code>/alerts</code> for your recent alerts\n\n"
            f"<i>What would you like to do today?</i>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        # User is not linked
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 Download App", url="https://example.com/app"),
                InlineKeyboardButton(text="❓ How to Link", callback_data="how_to_link")
            ],
            [
                InlineKeyboardButton(text="📖 Learn More", callback_data="about_bot")
            ]
        ])
        
        await message.answer(
            f"👋 <b>Hello, {user.full_name}!</b>\n\n"
            f"Welcome to the Premium Car Alert Bot! �\n\n"
            f"🔗 <b>Account Linking Required</b>\n"
            f"To use this bot, you need to link your Telegram account with our mobile app.\n\n"
            f"📱 <b>How to get started:</b>\n"
            f"1. Download our mobile app\n"
            f"2. Create an account and subscribe\n"
            f"3. Tap 'Connect to Telegram'\n"
            f"4. You'll be redirected here automatically\n\n"
            f"� <b>What you'll get:</b>\n"
            f"• Automatic car listing alerts\n"
            f"• AI-powered damage detection\n"
            f"• Real-time price notifications\n"
            f"• Smart filtering system\n\n"
            f"<i>Find your perfect car today!</i>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

@router.callback_query(F.data == "set_filters")
async def set_filters_callback(callback_query):
    """Handle set filters button press."""
    await callback_query.answer()
    await callback_query.message.answer(
        "🔍 <b>Set Car Search Filters</b>\n\n"
        "Use the <code>/filters</code> command to set up your car search criteria.\n\n"
        "You can filter by:\n"
        "• Make and Model\n"
        "• Year range\n"
        "• Price range\n"
        "• Location\n"
        "• And more!\n\n"
        "Once set, you'll receive automatic alerts for matching cars.",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "how_to_link")
async def how_to_link_callback(callback_query):
    """Handle how to link button press."""
    await callback_query.answer()
    await callback_query.message.answer(
        "🔗 <b>How to Link Your Account</b>\n\n"
        "Follow these simple steps:\n\n"
        "1️⃣ <b>Download the App</b>\n"
        "   Download our mobile app from the app store\n\n"
        "2️⃣ <b>Create Account</b>\n"
        "   Register with your email or log in if you have an account\n\n"
        "3️⃣ <b>Connect Telegram</b>\n"
        "   In the app, tap 'Connect to Telegram' button\n\n"
        "4️⃣ <b>Automatic Link</b>\n"
        "   You'll be redirected to this bot and automatically linked\n\n"
        "❓ <b>Need Help?</b>\n"
        "Contact our support team if you encounter any issues.\n\n"
        "<i>The linking process is secure and takes less than a minute!</i>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "about_bot")
async def about_bot_callback(callback_query):
    """Handle about bot button press."""
    await callback_query.answer()
    await callback_query.message.answer(
        "🛡️ <b>Professional URL Scanner Bot</b>\n\n"
        "Our advanced security bot provides comprehensive URL analysis and threat detection.\n\n"
        "🔍 <b>Key Features:</b>\n"
        "• Multi-phase scanning (Static, Domain, HTTP, Content)\n"
        "• Advanced damage scoring algorithm (0-100)\n"
        "• Malware and phishing detection\n"
        "• Typosquatting and homograph attack detection\n"
        "• Real-time threat intelligence\n"
        "• Detailed security reports\n\n"
        "🏆 <b>Professional Grade:</b>\n"
        "• Enterprise-level security algorithms\n"
        "• Continuous threat database updates\n"
        "• 99.9% uptime guarantee\n"
        "• Privacy-focused design\n\n"
        "🚀 <b>Built for Excellence</b>\n"
        "This bot represents a partnership commitment to delivering market-leading security solutions.\n\n"
        "<i>Your security is our priority!</i>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "recent_alerts")
async def recent_alerts_callback(callback_query):
    """Handle recent alerts button press."""
    user = callback_query.from_user
    if not user:
        await callback_query.answer("Unable to identify user", show_alert=True)
        return
    
    await callback_query.answer()
    
    # Get user from database
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    if not db_user:
        await callback_query.message.answer(
            "❌ <b>Account Not Linked</b>\n\n"
            "Please link your account first to view alert history.",
            parse_mode="HTML"
        )
        return
    
    # Get recent car alerts
    try:
        from database import CarAlert
        from sqlalchemy import select
        
        async with db_manager.async_session() as session:
            result = await session.execute(
                select(CarAlert)
                .where(CarAlert.user_id == db_user.id)
                .order_by(CarAlert.sent_at.desc())
                .limit(5)
            )
            recent_alerts = result.scalars().all()
        
        if not recent_alerts:
            await callback_query.message.answer(
                "📊 <b>Recent Alerts</b>\n\n"
                "No car alerts found yet.\n\n"
                "Set up your filters with /filters to start receiving alerts!",
                parse_mode="HTML"
            )
            return
        
        message = "📊 <b>Your Recent Car Alerts</b>\n\n"
        
        for i, alert in enumerate(recent_alerts, 1):
            # Format timestamp
            time_str = alert.sent_at.strftime("%m/%d %H:%M")
            
            # Get damage emoji
            damage_score = alert.damage_score or 0
            if damage_score < 20:
                emoji = "✅"
            elif damage_score < 40:
                emoji = "🟡"
            elif damage_score < 70:
                emoji = "🟠"
            else:
                emoji = "🔴"
            
            # Truncate title if too long
            title_display = alert.listing_title or "Unknown Car"
            if len(title_display) > 40:
                title_display = title_display[:37] + "..."
            
            message += f"{i}. {emoji} <b>{title_display}</b>\n"
            message += f"   Price: {alert.listing_price or 'N/A'} | Damage: {damage_score}/100\n"
            message += f"   {time_str}\n\n"
        
        message += "<i>Use /filters to update your search criteria</i>"
        
        await callback_query.message.answer(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error fetching recent alerts: {e}")
        await callback_query.message.answer(
            "❌ <b>Error</b>\n\n"
            "Unable to fetch recent alerts. Please try again.",
            parse_mode="HTML"
        )

@router.callback_query(F.data == "settings")
async def settings_callback(callback_query):
    """Handle settings button press."""
    await callback_query.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔔 Notifications", callback_data="settings_notifications"),
            InlineKeyboardButton(text="🔒 Privacy", callback_data="settings_privacy")
        ],
        [
            InlineKeyboardButton(text="📊 Scan Preferences", callback_data="settings_scan"),
            InlineKeyboardButton(text="❌ Unlink Account", callback_data="settings_unlink")
        ],
        [
            InlineKeyboardButton(text="« Back", callback_data="main_menu")
        ]
    ])
    
    await callback_query.message.answer(
        "⚙️ <b>Settings</b>\n\n"
        "Configure your bot preferences and account settings.\n\n"
        "Choose an option below:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "settings_unlink")
async def settings_unlink_callback(callback_query):
    """Handle unlink account button press."""
    await callback_query.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, Unlink", callback_data="confirm_unlink"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="settings")
        ]
    ])
    
    await callback_query.message.answer(
        "⚠️ <b>Unlink Account</b>\n\n"
        "Are you sure you want to unlink your Telegram account?\n\n"
        "This will:\n"
        "• Remove access to bot features\n"
        "• Clear your scan history\n"
        "• Require re-linking to use the bot again\n\n"
        "<b>This action cannot be undone.</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "confirm_unlink")
async def confirm_unlink_callback(callback_query):
    """Handle confirmed unlink action."""
    user = callback_query.from_user
    if not user:
        await callback_query.answer("Unable to identify user", show_alert=True)
        return
    
    await callback_query.answer()
    
    try:
        # Get user from database
        db_user = await db_manager.get_user_by_telegram_id(user.id)
        if not db_user:
            await callback_query.message.answer(
                "❌ Account not found or already unlinked.",
                parse_mode="HTML"
            )
            return
        
        # Unlink account (set telegram_id to None)
        success = await db_manager.link_telegram_account(
            user_id=db_user.id,
            telegram_id=None,
            telegram_username=None
        )
        
        if success:
            await callback_query.message.answer(
                "✅ <b>Account Unlinked</b>\n\n"
                "Your Telegram account has been successfully unlinked.\n\n"
                "To use the bot again, you'll need to generate a new link from the mobile app.\n\n"
                "Thank you for using our security service!",
                parse_mode="HTML"
            )
            logger.info(f"Unlinked Telegram user {user.id} from app account {db_user.id}")
        else:
            await callback_query.message.answer(
                "❌ <b>Unlink Failed</b>\n\n"
                "Unable to unlink your account due to a technical error.\n"
                "Please try again or contact support.",
                parse_mode="HTML"
            )
    
    except Exception as e:
        logger.error(f"Error unlinking account for user {user.id}: {e}")
        await callback_query.message.answer(
            "❌ <b>Unexpected Error</b>\n\n"
            "An unexpected error occurred while unlinking your account.\n"
            "Please contact support for assistance.",
            parse_mode="HTML"
        )

# Utility function to create deep link
def create_telegram_deep_link(token: str) -> str:
    """
    Create a Telegram deep link with the given token.
    
    Args:
        token: Link token to embed in the deep link
        
    Returns:
        Complete Telegram deep link URL
    """
    try:
        # Encode the token for URL safety
        encoded_token = token  # For MVP, we'll use the token as-is
        
        # Create the deep link
        bot_username = config.BOT_USERNAME
        if bot_username.startswith('@'):
            bot_username = bot_username[1:]  # Remove @ if present
        
        deep_link = f"https://t.me/{bot_username}?start={encoded_token}"
        
        logger.info(f"Created deep link for token: {token[:10]}...")
        return deep_link
    
    except Exception as e:
        logger.error(f"Error creating deep link: {e}")
        return f"https://t.me/{config.BOT_USERNAME}"
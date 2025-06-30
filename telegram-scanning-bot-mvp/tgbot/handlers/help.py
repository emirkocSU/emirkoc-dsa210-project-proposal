"""
Help command handler providing comprehensive bot documentation and user guidance.
Includes command explanations, usage examples, and feature descriptions.
"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from database import db_manager

logger = logging.getLogger(__name__)

# Create router for help-related handlers
router = Router()

@router.message(Command("help"))
async def help_command(message: Message):
    """
    Handle /help command with comprehensive bot documentation.
    
    Args:
        message: Telegram message object
    """
    user = message.from_user
    if not user:
        await message.answer("❌ Unable to identify user.")
        return
    
    logger.info(f"Help command from user {user.id} ({user.username})")
    
    # Check if user is linked
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    
    if db_user:
        # User is linked - show full help
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Scanning Commands", callback_data="help_scanning"),
                InlineKeyboardButton(text="📊 Statistics", callback_data="help_stats")
            ],
            [
                InlineKeyboardButton(text="⚙️ Settings", callback_data="help_settings"),
                InlineKeyboardButton(text="🛡️ Security Features", callback_data="help_security")
            ],
            [
                InlineKeyboardButton(text="❓ FAQ", callback_data="help_faq"),
                InlineKeyboardButton(text="📞 Support", callback_data="help_support")
            ]
        ])
        
        help_text = (
            f"🛡️ <b>Professional URL Scanner Bot - Help</b>\n\n"
            f"Welcome, <b>{db_user.full_name or user.full_name}</b>! Your account is linked and ready.\n\n"
            f"🚀 <b>Quick Start Commands:</b>\n"
            f"• <code>/scan [URL]</code> - Comprehensive URL security analysis\n"
            f"• <code>/quickscan [URL]</code> - Fast security scan\n"
            f"• <code>/scanstats</code> - View your scanning statistics\n"
            f"• <code>/history</code> - Recent scan results\n\n"
            f"📋 <b>Available Features:</b>\n"
            f"• Multi-phase threat detection\n"
            f"• Advanced damage scoring (0-100)\n"
            f"• Real-time malware analysis\n"
            f"• Phishing protection\n"
            f"• Detailed security reports\n\n"
            f"<i>Select a topic below for detailed information:</i>"
        )
    else:
        # User is not linked - show linking help
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔗 How to Link", callback_data="how_to_link"),
                InlineKeyboardButton(text="📱 Download App", url="https://example.com/app")
            ],
            [
                InlineKeyboardButton(text="🛡️ About Security", callback_data="help_security"),
                InlineKeyboardButton(text="❓ FAQ", callback_data="help_faq")
            ]
        ])
        
        help_text = (
            f"🛡️ <b>Professional URL Scanner Bot - Help</b>\n\n"
            f"Hello, <b>{user.full_name}</b>! To use this bot, you need to link your account first.\n\n"
            f"🔗 <b>Account Linking Required:</b>\n"
            f"This bot requires linking with our mobile app for security and personalization.\n\n"
            f"📱 <b>How to Get Started:</b>\n"
            f"1. Download our mobile app\n"
            f"2. Create an account or log in\n"
            f"3. Tap 'Connect to Telegram'\n"
            f"4. You'll be redirected here automatically\n\n"
            f"🛡️ <b>What You'll Get:</b>\n"
            f"• Professional-grade URL scanning\n"
            f"• Advanced threat detection\n"
            f"• Personalized security reports\n"
            f"• Scan history and statistics\n\n"
            f"<i>Select a topic below for more information:</i>"
        )
    
    await message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "help_scanning")
async def help_scanning_callback(callback_query: CallbackQuery):
    """Handle scanning commands help."""
    await callback_query.answer()
    
    help_text = (
        "🔍 <b>Scanning Commands Help</b>\n\n"
        "<b>1. /scan [URL]</b>\n"
        "Comprehensive URL security analysis with detailed reporting.\n\n"
        "<i>Examples:</i>\n"
        "• <code>/scan https://example.com</code>\n"
        "• <code>/scan</code> (then send URL when prompted)\n\n"
        "<b>2. /quickscan [URL]</b>\n"
        "Fast security scan for immediate results.\n\n"
        "<i>Example:</i>\n"
        "• <code>/quickscan https://suspicious-site.com</code>\n\n"
        "<b>🔄 Scanning Process:</b>\n"
        "1. <b>Static Analysis</b> - URL structure and patterns\n"
        "2. <b>Domain Analysis</b> - Reputation and DNS checks\n"
        "3. <b>HTTP Analysis</b> - Response headers and redirects\n"
        "4. <b>Content Analysis</b> - Page content and scripts\n\n"
        "<b>📊 Results Include:</b>\n"
        "• Damage score (0-100)\n"
        "• Risk level (Safe to Critical)\n"
        "• Threat descriptions\n"
        "• Confidence ratings\n"
        "• Detailed evidence\n\n"
        "<i>Scans typically complete in 10-30 seconds.</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Help", callback_data="help_main")]
    ])
    
    await callback_query.message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "help_stats")
async def help_stats_callback(callback_query: CallbackQuery):
    """Handle statistics help."""
    await callback_query.answer()
    
    help_text = (
        "📊 <b>Statistics Commands Help</b>\n\n"
        "<b>1. /scanstats</b>\n"
        "View comprehensive scanning statistics including:\n"
        "• Total scans performed\n"
        "• Success/failure rates\n"
        "• Average damage scores\n"
        "• Risk level distribution\n\n"
        "<b>2. /history</b>\n"
        "View your recent scan results with:\n"
        "• Last 10 scanned URLs\n"
        "• Damage scores\n"
        "• Scan timestamps\n"
        "• Quick risk indicators\n\n"
        "<b>📈 Understanding Your Stats:</b>\n\n"
        "<b>Damage Score Ranges:</b>\n"
        "• 0: Safe - No threats detected\n"
        "• 1-20: Low risk - Minor concerns\n"
        "• 21-50: Medium risk - Exercise caution\n"
        "• 51-80: High risk - Avoid if possible\n"
        "• 81-100: Critical - Highly dangerous\n\n"
        "<b>Risk Indicators:</b>\n"
        "✅ Safe | ⚠️ Low | 🟡 Medium | 🔴 High | 💀 Critical\n\n"
        "<i>Regular scanning helps improve your security awareness!</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Help", callback_data="help_main")]
    ])
    
    await callback_query.message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "help_settings")
async def help_settings_callback(callback_query: CallbackQuery):
    """Handle settings help."""
    await callback_query.answer()
    
    help_text = (
        "⚙️ <b>Settings & Account Management</b>\n\n"
        "<b>Account Settings:</b>\n"
        "• View account linking status\n"
        "• Manage notification preferences\n"
        "• Configure scan settings\n"
        "• Privacy controls\n\n"
        "<b>🔗 Account Linking:</b>\n"
        "Your Telegram account is linked to your mobile app account. This enables:\n"
        "• Synchronized scan history\n"
        "• Personalized threat reports\n"
        "• Cross-platform access\n"
        "• Secure user identification\n\n"
        "<b>🔓 Unlinking Account:</b>\n"
        "If you need to unlink your account:\n"
        "1. Go to Settings → Unlink Account\n"
        "2. Confirm the action\n"
        "3. Your data will be preserved\n"
        "4. Re-link anytime from the app\n\n"
        "<b>🔔 Notifications:</b>\n"
        "• Scan completion alerts\n"
        "• Critical threat warnings\n"
        "• Security updates\n"
        "• Feature announcements\n\n"
        "<i>Access settings through the main menu or /start command.</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Help", callback_data="help_main")]
    ])
    
    await callback_query.message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "help_security")
async def help_security_callback(callback_query: CallbackQuery):
    """Handle security features help."""
    await callback_query.answer()
    
    help_text = (
        "🛡️ <b>Advanced Security Features</b>\n\n"
        "<b>🔍 Multi-Phase Scanning:</b>\n\n"
        "<b>1. Static Analysis</b>\n"
        "• URL structure examination\n"
        "• Malware pattern detection\n"
        "• Phishing indicator analysis\n"
        "• Suspicious domain patterns\n\n"
        "<b>2. Domain Intelligence</b>\n"
        "• Reputation database lookup\n"
        "• Homograph attack detection\n"
        "• Typosquatting identification\n"
        "• Domain age and history\n\n"
        "<b>3. HTTP Response Analysis</b>\n"
        "• Security header validation\n"
        "• Redirect chain analysis\n"
        "• Server fingerprinting\n"
        "• Response code evaluation\n\n"
        "<b>4. Content Inspection</b>\n"
        "• JavaScript malware detection\n"
        "• Hidden iframe analysis\n"
        "• Phishing content identification\n"
        "• Obfuscation detection\n\n"
        "<b>🎯 Threat Detection:</b>\n"
        "• Malware downloads\n"
        "• Phishing attempts\n"
        "• Scam websites\n"
        "• Cryptocurrency miners\n"
        "• Command & control servers\n"
        "• Social engineering attacks\n\n"
        "<i>Our algorithms are continuously updated with the latest threat intelligence.</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Help", callback_data="help_main")]
    ])
    
    await callback_query.message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "help_faq")
async def help_faq_callback(callback_query: CallbackQuery):
    """Handle FAQ help."""
    await callback_query.answer()
    
    help_text = (
        "❓ <b>Frequently Asked Questions</b>\n\n"
        "<b>Q: How accurate are the scan results?</b>\n"
        "A: Our multi-phase scanning achieves 95%+ accuracy using enterprise-grade algorithms and real-time threat intelligence.\n\n"
        "<b>Q: How long do scans take?</b>\n"
        "A: Most scans complete in 10-30 seconds. Complex sites may take up to 60 seconds.\n\n"
        "<b>Q: Is my data private?</b>\n"
        "A: Yes! We only analyze URLs you explicitly request. No browsing history is collected.\n\n"
        "<b>Q: Can I scan any website?</b>\n"
        "A: You can scan most public websites. Private/internal sites may not be accessible.\n\n"
        "<b>Q: What if a scan fails?</b>\n"
        "A: Scans may fail due to network issues, site blocking, or timeouts. Simply try again.\n\n"
        "<b>Q: How is the damage score calculated?</b>\n"
        "A: Our proprietary algorithm considers threat severity, confidence levels, and multiple risk factors.\n\n"
        "<b>Q: Can I scan the same URL multiple times?</b>\n"
        "A: Yes! Threats change over time, so rescanning is recommended for important sites.\n\n"
        "<b>Q: Is there a scan limit?</b>\n"
        "A: Linked accounts have generous limits. Rate limiting prevents spam and ensures performance.\n\n"
        "<i>Still have questions? Contact our support team!</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Help", callback_data="help_main")]
    ])
    
    await callback_query.message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "help_support")
async def help_support_callback(callback_query: CallbackQuery):
    """Handle support help."""
    await callback_query.answer()
    
    help_text = (
        "📞 <b>Support & Contact Information</b>\n\n"
        "<b>🆘 Getting Help:</b>\n\n"
        "<b>1. Common Issues:</b>\n"
        "• Account linking problems\n"
        "• Scan errors or timeouts\n"
        "• App synchronization issues\n"
        "• Feature questions\n\n"
        "<b>2. Self-Help Resources:</b>\n"
        "• Use /help for command documentation\n"
        "• Check FAQ for common questions\n"
        "• Review security feature descriptions\n"
        "• Try relinking your account\n\n"
        "<b>3. Contact Support:</b>\n"
        "• Email: support@scanbot.example.com\n"
        "• Response time: Within 24 hours\n"
        "• Include your user ID and error details\n\n"
        "<b>🐛 Bug Reports:</b>\n"
        "Help us improve by reporting:\n"
        "• Unexpected behavior\n"
        "• False positives/negatives\n"
        "• Performance issues\n"
        "• Feature suggestions\n\n"
        "<b>📋 When Contacting Support:</b>\n"
        "Please include:\n"
        "• Your Telegram username\n"
        "• Description of the issue\n"
        "• Steps to reproduce\n"
        "• Screenshots if applicable\n\n"
        "<i>We're committed to providing excellent support for our security service!</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Help", callback_data="help_main")]
    ])
    
    await callback_query.message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "help_main")
async def help_main_callback(callback_query: CallbackQuery):
    """Return to main help menu."""
    await callback_query.answer()
    
    # Redirect to main help command
    await help_command(callback_query.message)

# History command
@router.message(Command("history"))
async def history_command(message: Message):
    """
    Handle /history command to show recent scans.
    
    Args:
        message: Telegram message object
    """
    user = message.from_user
    if not user:
        await message.answer("❌ Unable to identify user.")
        return
    
    logger.info(f"History command from user {user.id} ({user.username})")
    
    # Check if user is linked
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    if not db_user:
        await message.answer(
            "🔒 <b>Account Linking Required</b>\n\n"
            "Please link your account first to view scan history.\n"
            "Use /start to get started.",
            parse_mode="HTML"
        )
        return
    
    # Get recent scan results
    recent_scans = await db_manager.get_user_scan_results(db_user.id, limit=10)
    
    if not recent_scans:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Start Scanning", callback_data="quick_scan")]
        ])
        
        await message.answer(
            "📊 <b>Scan History</b>\n\n"
            "No scans found yet.\n\n"
            "Use /scan [URL] to perform your first security scan!",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return
    
    history_message = "📊 <b>Your Recent Scan History</b>\n\n"
    
    for i, scan in enumerate(recent_scans, 1):
        # Format timestamp
        time_str = scan.created_at.strftime("%m/%d %H:%M")
        
        # Get risk emoji based on damage score
        if scan.damage_score is None:
            emoji = "❓"
            risk_text = "Unknown"
        elif scan.damage_score == 0:
            emoji = "✅"
            risk_text = "Safe"
        elif scan.damage_score <= 20:
            emoji = "⚠️"
            risk_text = "Low"
        elif scan.damage_score <= 50:
            emoji = "🟡"
            risk_text = "Medium"
        elif scan.damage_score <= 80:
            emoji = "🔴"
            risk_text = "High"
        else:
            emoji = "💀"
            risk_text = "Critical"
        
        # Truncate URL if too long
        url_display = scan.url
        if len(url_display) > 35:
            url_display = url_display[:32] + "..."
        
        history_message += f"{i}. {emoji} <code>{url_display}</code>\n"
        history_message += f"   {risk_text} ({scan.damage_score or 0}/100) • {time_str}\n"
        
        if scan.status != "completed":
            history_message += f"   <i>Status: {scan.status.title()}</i>\n"
        
        history_message += "\n"
    
    history_message += f"<i>Showing last {len(recent_scans)} scans. Use /scanstats for detailed statistics.</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 New Scan", callback_data="new_scan"),
            InlineKeyboardButton(text="📊 Statistics", callback_data="help_stats")
        ]
    ])
    
    await message.answer(history_message, parse_mode="HTML", reply_markup=keyboard)

# About command
@router.message(Command("about"))
async def about_command(message: Message):
    """
    Handle /about command with bot information.
    
    Args:
        message: Telegram message object
    """
    about_text = (
        "🛡️ <b>Professional URL Scanner Bot</b>\n\n"
        "<b>🚀 Version:</b> 1.0 MVP\n"
        "<b>🏗️ Built with:</b> aiogram 3.x + Python\n"
        "<b>🔍 Scanner:</b> Multi-phase threat detection\n"
        "<b>📱 Integration:</b> React Native (Expo) app\n\n"
        "<b>🎯 Mission:</b>\n"
        "To provide professional-grade URL security analysis accessible to everyone through Telegram's convenient interface.\n\n"
        "<b>🏆 Features:</b>\n"
        "• Advanced damage scoring (0-100)\n"
        "• Real-time threat intelligence\n"
        "• Multi-user account support\n"
        "• Cross-platform synchronization\n"
        "• Comprehensive security reports\n\n"
        "<b>🤝 Partnership Excellence:</b>\n"
        "This bot represents our commitment to delivering market-leading security solutions with professional-grade architecture and user experience.\n\n"
        "<b>🔒 Privacy & Security:</b>\n"
        "• No browsing history collected\n"
        "• Secure account linking\n"
        "• Encrypted data transmission\n"
        "• GDPR compliant\n\n"
        "<i>Your security is our priority. Built for excellence.</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📖 Help", callback_data="help_main"),
            InlineKeyboardButton(text="🔍 Start Scanning", callback_data="quick_scan")
        ]
    ])
    
    await message.answer(about_text, parse_mode="HTML", reply_markup=keyboard)
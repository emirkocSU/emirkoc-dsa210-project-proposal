"""
Scan command handler with professional URL scanning and damage assessment.
Implements multi-step scanning workflow with FSM and comprehensive threat analysis.
"""

import asyncio
import logging
import json
from typing import Optional, Dict, Any

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from database import db_manager
from utils.validators import CommandValidator, validate_url
from utils.scanner import perform_scan, format_scan_result
from config import config

logger = logging.getLogger(__name__)

# Create router for scan-related handlers
router = Router()

class ScanFlow(StatesGroup):
    """FSM states for scanning workflow."""
    awaiting_url = State()
    scanning = State()
    results = State()

@router.message(Command("scan"))
async def scan_command(message: Message, state: FSMContext):
    """
    Handle /scan command with optional URL argument.
    
    Args:
        message: Telegram message object
        state: FSM context for managing conversation state
    """
    user = message.from_user
    if not user:
        await message.answer("❌ Unable to identify user. Please try again.")
        return
    
    logger.info(f"Scan command from user {user.id} ({user.username})")
    
    # Check if user is linked
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    if not db_user:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Link Account", callback_data="how_to_link")]
        ])
        
        await message.answer(
            "🔒 <b>Account Linking Required</b>\n\n"
            "To use the scanning features, you need to link your Telegram account with our mobile app.\n\n"
            "Please download the app and generate a Telegram link to get started.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return
    
    # Extract command arguments
    command_text = message.text or ""
    args = command_text[5:].strip()  # Remove "/scan" prefix
    
    if args:
        # URL provided directly in command
        await process_scan_url(message, state, args, db_user)
    else:
        # No URL provided, ask for it
        await message.answer(
            "🔍 <b>URL Scanner</b>\n\n"
            "Please send me the URL you want to scan for threats and malware.\n\n"
            "Example: <code>https://example.com</code>\n\n"
            "<i>I'll analyze the URL and provide a comprehensive security report.</i>",
            parse_mode="HTML"
        )
        await state.set_state(ScanFlow.awaiting_url)

@router.message(ScanFlow.awaiting_url, F.text)
async def process_url_input(message: Message, state: FSMContext):
    """
    Process URL input from user in FSM state.
    
    Args:
        message: Telegram message object
        state: FSM context
    """
    user = message.from_user
    if not user:
        await message.answer("❌ Unable to identify user.")
        await state.clear()
        return
    
    # Get user from database
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    if not db_user:
        await message.answer("❌ Account not linked. Please link your account first.")
        await state.clear()
        return
    
    url = message.text.strip() if message.text else ""
    await process_scan_url(message, state, url, db_user)

async def process_scan_url(message: Message, state: FSMContext, url: str, db_user):
    """
    Process and validate URL for scanning.
    
    Args:
        message: Telegram message object
        state: FSM context
        url: URL to scan
        db_user: Database user object
    """
    # Validate URL format
    is_valid, error_msg = validate_url(url)
    if not is_valid:
        await message.answer(
            f"❌ <b>Invalid URL</b>\n\n"
            f"Error: {error_msg}\n\n"
            f"Please provide a valid URL starting with http:// or https://",
            parse_mode="HTML"
        )
        
        # If in FSM, stay in awaiting_url state
        if await state.get_state() == ScanFlow.awaiting_url:
            await message.answer(
                "Please send a valid URL to scan:",
                parse_mode="HTML"
            )
        return
    
    # Start scanning process
    await initiate_scan(message, state, url, db_user)

async def initiate_scan(message: Message, state: FSMContext, url: str, db_user):
    """
    Initiate the URL scanning process.
    
    Args:
        message: Telegram message object
        state: FSM context
        url: Validated URL to scan
        db_user: Database user object
    """
    try:
        # Create scan result entry in database
        scan_result_db = await db_manager.create_scan_result(
            user_id=db_user.id,
            url=url,
            scan_type="url_scan"
        )
        
        if not scan_result_db:
            await message.answer(
                "❌ <b>Database Error</b>\n\n"
                "Unable to create scan record. Please try again.",
                parse_mode="HTML"
            )
            await state.clear()
            return
        
        # Store scan ID in FSM data
        await state.update_data(scan_id=scan_result_db.id, url=url)
        await state.set_state(ScanFlow.scanning)
        
        # Send scanning started message
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel Scan", callback_data=f"cancel_scan_{scan_result_db.id}")]
        ])
        
        scanning_message = await message.answer(
            f"🔍 <b>Scanning in Progress</b>\n\n"
            f"URL: <code>{url}</code>\n\n"
            f"🔄 <b>Analysis Phases:</b>\n"
            f"• Static URL analysis\n"
            f"• Domain reputation check\n"
            f"• HTTP response analysis\n"
            f"• Content threat detection\n\n"
            f"<i>This may take up to {config.MAX_SCAN_TIMEOUT} seconds...</i>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        # Store message ID for updates
        await state.update_data(scanning_message_id=scanning_message.message_id)
        
        # Perform the actual scan (async task)
        asyncio.create_task(perform_background_scan(
            scan_result_db.id, url, db_user.id, message.chat.id, scanning_message.message_id
        ))
        
        logger.info(f"Started scan {scan_result_db.id} for user {db_user.id}: {url}")
    
    except Exception as e:
        logger.error(f"Error initiating scan: {e}")
        await message.answer(
            "❌ <b>Scan Error</b>\n\n"
            "An unexpected error occurred while starting the scan.\n"
            "Please try again or contact support.",
            parse_mode="HTML"
        )
        await state.clear()

async def perform_background_scan(scan_id: int, url: str, user_id: int, chat_id: int, message_id: int):
    """
    Perform the actual URL scan in the background.
    
    Args:
        scan_id: Database scan result ID
        url: URL to scan
        user_id: User ID
        chat_id: Telegram chat ID
        message_id: Message ID to update
    """
    try:
        # Perform the comprehensive scan
        scan_result = await perform_scan(url)
        
        # Update database with results
        await db_manager.update_scan_result(
            scan_id=scan_id,
            status=scan_result.status,
            result_data=json.dumps({
                "overall_risk": scan_result.overall_risk,
                "threats_found": [
                    {
                        "threat_type": threat.threat_type,
                        "severity": threat.severity,
                        "description": threat.description,
                        "confidence": threat.confidence,
                        "evidence": threat.evidence
                    }
                    for threat in scan_result.threats_found
                ],
                "metadata": scan_result.metadata
            }),
            damage_score=scan_result.damage_score,
            threats_found=json.dumps([threat.threat_type for threat in scan_result.threats_found]),
            scan_duration=int(scan_result.scan_duration)
        )
        
        # Format result message
        result_message = format_scan_result(scan_result)
        
        # Create result keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Scan Another", callback_data="new_scan"),
                InlineKeyboardButton(text="📊 View Details", callback_data=f"scan_details_{scan_id}")
            ],
            [
                InlineKeyboardButton(text="📈 Scan History", callback_data="recent_scans"),
                InlineKeyboardButton(text="🔗 Share Result", callback_data=f"share_scan_{scan_id}")
            ]
        ])
        
        # Update the scanning message with results
        from aiogram import Bot
        bot = Bot(token=config.BOT_TOKEN)
        
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=result_message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as edit_error:
            # If editing fails, send a new message
            await bot.send_message(
                chat_id=chat_id,
                text=result_message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        
        await bot.session.close()
        
        logger.info(f"Completed scan {scan_id}: {scan_result.overall_risk} risk, score {scan_result.damage_score}")
    
    except Exception as e:
        logger.error(f"Error in background scan {scan_id}: {e}")
        
        # Update database with error
        await db_manager.update_scan_result(
            scan_id=scan_id,
            status="failed",
            result_data=json.dumps({"error": str(e)})
        )
        
        # Send error message
        try:
            from aiogram import Bot
            bot = Bot(token=config.BOT_TOKEN)
            
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"❌ <b>Scan Failed</b>\n\n"
                     f"URL: <code>{url}</code>\n\n"
                     f"An error occurred during scanning. Please try again.\n\n"
                     f"<i>If the problem persists, contact support.</i>",
                parse_mode="HTML"
            )
            
            await bot.session.close()
        except:
            pass  # Ignore errors in error handling

@router.callback_query(F.data.startswith("cancel_scan_"))
async def cancel_scan_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle scan cancellation."""
    await callback_query.answer()
    
    scan_id = int(callback_query.data.split("_")[-1])
    
    # Update database
    await db_manager.update_scan_result(
        scan_id=scan_id,
        status="cancelled"
    )
    
    # Clear FSM state
    await state.clear()
    
    await callback_query.message.edit_text(
        "❌ <b>Scan Cancelled</b>\n\n"
        "The scan has been cancelled by user request.\n\n"
        "Use /scan to start a new scan.",
        parse_mode="HTML"
    )
    
    logger.info(f"Cancelled scan {scan_id}")

@router.callback_query(F.data == "new_scan")
async def new_scan_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle new scan button press."""
    await callback_query.answer()
    
    await callback_query.message.answer(
        "🔍 <b>New URL Scan</b>\n\n"
        "Send me the URL you want to scan, or use:\n"
        "<code>/scan [URL]</code>\n\n"
        "I'll provide a comprehensive security analysis.",
        parse_mode="HTML"
    )
    
    await state.set_state(ScanFlow.awaiting_url)

@router.callback_query(F.data.startswith("scan_details_"))
async def scan_details_callback(callback_query: CallbackQuery):
    """Handle scan details button press."""
    await callback_query.answer()
    
    scan_id = int(callback_query.data.split("_")[-1])
    user = callback_query.from_user
    
    if not user:
        await callback_query.message.answer("❌ Unable to identify user.")
        return
    
    # Get user from database
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    if not db_user:
        await callback_query.message.answer("❌ Account not linked.")
        return
    
    # Get scan results
    scan_results = await db_manager.get_user_scan_results(db_user.id, limit=50)
    scan_result = next((s for s in scan_results if s.id == scan_id), None)
    
    if not scan_result:
        await callback_query.message.answer(
            "❌ <b>Scan Not Found</b>\n\n"
            "The requested scan result could not be found.",
            parse_mode="HTML"
        )
        return
    
    # Parse detailed results
    details_message = f"📊 <b>Detailed Scan Report</b>\n\n"
    details_message += f"🔗 <b>URL:</b> <code>{scan_result.url}</code>\n"
    details_message += f"📅 <b>Scanned:</b> {scan_result.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    details_message += f"⏱️ <b>Duration:</b> {scan_result.scan_duration or 0}s\n"
    details_message += f"📊 <b>Damage Score:</b> {scan_result.damage_score or 0}/100\n"
    details_message += f"🏷️ <b>Status:</b> {scan_result.status.title()}\n\n"
    
    # Parse result data for detailed threats
    if scan_result.result_data:
        try:
            result_data = json.loads(scan_result.result_data)
            threats = result_data.get("threats_found", [])
            
            if threats:
                details_message += f"🚨 <b>Threats Detected ({len(threats)}):</b>\n\n"
                
                for i, threat in enumerate(threats[:5], 1):  # Show max 5 threats
                    severity_emoji = {
                        "critical": "💀", "high": "🔴", 
                        "medium": "🟡", "low": "⚠️"
                    }
                    emoji = severity_emoji.get(threat.get("severity", "low"), "⚠️")
                    confidence = int(threat.get("confidence", 0) * 100)
                    
                    details_message += f"{emoji} <b>{threat.get('threat_type', 'Unknown').replace('_', ' ').title()}</b>\n"
                    details_message += f"   {threat.get('description', 'No description')}\n"
                    details_message += f"   <i>Confidence: {confidence}%</i>\n\n"
                
                if len(threats) > 5:
                    details_message += f"<i>... and {len(threats) - 5} more threats</i>\n\n"
            else:
                details_message += "✅ <b>No threats detected</b>\n\n"
        except:
            details_message += "❓ <b>Unable to parse threat details</b>\n\n"
    
    details_message += f"<i>Scan ID: {scan_result.id}</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Rescan URL", callback_data=f"rescan_{scan_result.id}"),
            InlineKeyboardButton(text="📋 Copy URL", callback_data=f"copy_url_{scan_result.id}")
        ],
        [
            InlineKeyboardButton(text="« Back to Results", callback_data="recent_scans")
        ]
    ])
    
    await callback_query.message.answer(
        details_message,
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("rescan_"))
async def rescan_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle rescan button press."""
    await callback_query.answer()
    
    scan_id = int(callback_query.data.split("_")[-1])
    user = callback_query.from_user
    
    if not user:
        await callback_query.message.answer("❌ Unable to identify user.")
        return
    
    # Get user from database
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    if not db_user:
        await callback_query.message.answer("❌ Account not linked.")
        return
    
    # Get original scan result
    scan_results = await db_manager.get_user_scan_results(db_user.id, limit=50)
    original_scan = next((s for s in scan_results if s.id == scan_id), None)
    
    if not original_scan:
        await callback_query.message.answer("❌ Original scan not found.")
        return
    
    # Start new scan with the same URL
    await initiate_scan(callback_query.message, state, original_scan.url, db_user)

@router.callback_query(F.data.startswith("share_scan_"))
async def share_scan_callback(callback_query: CallbackQuery):
    """Handle share scan result button press."""
    await callback_query.answer()
    
    scan_id = int(callback_query.data.split("_")[-1])
    
    # For MVP, we'll just provide a shareable summary
    await callback_query.message.answer(
        f"🔗 <b>Share Scan Result</b>\n\n"
        f"Scan ID: <code>{scan_id}</code>\n\n"
        f"You can share this scan ID with others who have access to the bot.\n\n"
        f"<i>Full sharing features will be available in future updates.</i>",
        parse_mode="HTML"
    )

# Quick scan command for power users
@router.message(Command("quickscan"))
async def quick_scan_command(message: Message):
    """Handle /quickscan command for immediate scanning."""
    user = message.from_user
    if not user:
        await message.answer("❌ Unable to identify user.")
        return
    
    # Check if user is linked
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    if not db_user:
        await message.answer(
            "🔒 Account linking required. Use /start to link your account.",
            parse_mode="HTML"
        )
        return
    
    command_text = message.text or ""
    args = command_text[10:].strip()  # Remove "/quickscan" prefix
    
    if not args:
        await message.answer(
            "⚡ <b>Quick Scan</b>\n\n"
            "Usage: <code>/quickscan [URL]</code>\n\n"
            "Example: <code>/quickscan https://example.com</code>",
            parse_mode="HTML"
        )
        return
    
    # Validate and process URL immediately
    is_valid, error_msg = validate_url(args)
    if not is_valid:
        await message.answer(
            f"❌ Invalid URL: {error_msg}",
            parse_mode="HTML"
        )
        return
    
    # Send immediate scanning message
    quick_message = await message.answer(
        f"⚡ <b>Quick Scan Started</b>\n\n"
        f"URL: <code>{args}</code>\n\n"
        f"🔄 Processing...",
        parse_mode="HTML"
    )
    
    try:
        # Create scan record
        scan_result_db = await db_manager.create_scan_result(
            user_id=db_user.id,
            url=args,
            scan_type="quick_scan"
        )
        
        if scan_result_db:
            # Perform quick scan in background
            asyncio.create_task(perform_background_scan(
                scan_result_db.id, args, db_user.id, message.chat.id, quick_message.message_id
            ))
        else:
            await quick_message.edit_text("❌ Failed to create scan record.")
    
    except Exception as e:
        logger.error(f"Error in quick scan: {e}")
        await quick_message.edit_text("❌ Quick scan failed. Please try again.")

# Admin command to view scan statistics
@router.message(Command("scanstats"))
async def scan_stats_command(message: Message):
    """Handle /scanstats command for scan statistics."""
    user = message.from_user
    if not user:
        await message.answer("❌ Unable to identify user.")
        return
    
    # Check if user is linked
    db_user = await db_manager.get_user_by_telegram_id(user.id)
    if not db_user:
        await message.answer("🔒 Account linking required.")
        return
    
    # Get user's scan statistics
    all_scans = await db_manager.get_user_scan_results(db_user.id, limit=100)
    
    if not all_scans:
        await message.answer(
            "📊 <b>Scan Statistics</b>\n\n"
            "No scans found yet.\n\n"
            "Use /scan to perform your first security scan!",
            parse_mode="HTML"
        )
        return
    
    # Calculate statistics
    total_scans = len(all_scans)
    completed_scans = len([s for s in all_scans if s.status == "completed"])
    failed_scans = len([s for s in all_scans if s.status == "failed"])
    
    # Risk level distribution
    risk_counts = {"safe": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    total_damage_score = 0
    
    for scan in all_scans:
        if scan.damage_score is not None:
            total_damage_score += scan.damage_score
            
            # Determine risk level from damage score
            if scan.damage_score == 0:
                risk_counts["safe"] += 1
            elif scan.damage_score <= 20:
                risk_counts["low"] += 1
            elif scan.damage_score <= 50:
                risk_counts["medium"] += 1
            elif scan.damage_score <= 80:
                risk_counts["high"] += 1
            else:
                risk_counts["critical"] += 1
    
    avg_damage_score = total_damage_score / max(completed_scans, 1)
    
    stats_message = f"📊 <b>Your Scan Statistics</b>\n\n"
    stats_message += f"📈 <b>Total Scans:</b> {total_scans}\n"
    stats_message += f"✅ <b>Completed:</b> {completed_scans}\n"
    stats_message += f"❌ <b>Failed:</b> {failed_scans}\n"
    stats_message += f"📊 <b>Average Score:</b> {avg_damage_score:.1f}/100\n\n"
    
    stats_message += f"🎯 <b>Risk Distribution:</b>\n"
    stats_message += f"✅ Safe: {risk_counts['safe']}\n"
    stats_message += f"⚠️ Low: {risk_counts['low']}\n"
    stats_message += f"🟡 Medium: {risk_counts['medium']}\n"
    stats_message += f"🔴 High: {risk_counts['high']}\n"
    stats_message += f"💀 Critical: {risk_counts['critical']}\n\n"
    
    stats_message += f"<i>Keep scanning to improve your security awareness!</i>"
    
    await message.answer(stats_message, parse_mode="HTML")
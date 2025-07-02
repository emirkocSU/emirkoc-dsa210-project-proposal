"""
Main entry point for the Professional Telegram Scanning Bot.
Initializes the bot, registers handlers and middleware, and starts polling.
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database import init_database, db_manager
from middlewares.throttling import ThrottlingMiddleware, CommandThrottlingMiddleware
from handlers import start, scan, help, filters
from utils.car_scanner import car_scanner, init_car_scanner, cleanup_car_scanner
from utils.yolo import init_damage_detector

logger = logging.getLogger(__name__)

# Global bot instance for use in other modules
bot_instance = None

class ProfessionalScanBot:
    """
    Professional URL Scanner Bot with comprehensive features.
    Manages bot lifecycle, handlers, and middleware.
    """
    
    def __init__(self):
        """Initialize the bot with configuration and components."""
        self.bot = None
        self.dp = None
        self.is_running = False
        
        logger.info("Initializing Professional Telegram Scanning Bot")
    
    async def setup_bot(self):
        """Setup bot instance and dispatcher with all components."""
        try:
            # Initialize bot with default properties
            self.bot = Bot(
                token=config.BOT_TOKEN,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML,
                    link_preview_is_disabled=True
                )
            )
            
            # Set global bot instance
            global bot_instance
            bot_instance = self.bot
            
            # Initialize dispatcher
            self.dp = Dispatcher()
            
            # Setup database
            await init_database()
            
            # Initialize car scanner and damage detector
            await init_car_scanner()
            await init_damage_detector()
            
            # Register middleware (order matters!)
            self.dp.message.middleware(ThrottlingMiddleware())
            self.dp.callback_query.middleware(ThrottlingMiddleware())
            self.dp.message.middleware(CommandThrottlingMiddleware())
            
            # Register handlers
            self.dp.include_router(start.router)
            self.dp.include_router(scan.router)
            self.dp.include_router(help.router)
            self.dp.include_router(filters.router)
            
            # Set bot commands for user convenience
            await self._setup_bot_commands()
            
            logger.info("Bot setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error setting up bot: {e}")
            raise
    
    async def _setup_bot_commands(self):
        """Setup bot commands menu for users."""
        commands = [
            BotCommand(command="start", description="🏠 Start bot / Link account"),
            BotCommand(command="filters", description="🔍 Set car search filters"),
            BotCommand(command="scan", description="🚗 Analyze car listing"),
            BotCommand(command="alerts", description="📊 View recent alerts"),
            BotCommand(command="help", description="❓ Help and documentation"),
            BotCommand(command="about", description="ℹ️ About this bot"),
        ]
        
        try:
            await self.bot.set_my_commands(commands)
            logger.info("Bot commands menu set successfully")
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")
    
    async def _background_scanner(self):
        """Background task for scanning car listings."""
        logger.info("Starting background car listing scanner")
        
        while self.is_running:
            try:
                await car_scanner.check_new_listings()
                logger.debug("Background scan completed")
                
                # Wait for next scan interval
                await asyncio.sleep(config.SCAN_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in background scanner: {e}")
                # Wait a bit before retrying on error
                await asyncio.sleep(60)
        
        logger.info("Background scanner stopped")
    
    async def start_polling(self):
        """Start the bot with long polling."""
        if not self.bot or not self.dp:
            raise RuntimeError("Bot not properly initialized. Call setup_bot() first.")
        
        try:
            self.is_running = True
            
            # Get bot info
            bot_info = await self.bot.get_me()
            logger.info(f"Starting bot: @{bot_info.username} (ID: {bot_info.id})")
            
            # Start background scanning task
            asyncio.create_task(self._background_scanner())
            
            # Start polling
            logger.info("Bot is now running. Press Ctrl+C to stop.")
            await self.dp.start_polling(
                self.bot,
                allowed_updates=["message", "callback_query", "inline_query"],
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources on shutdown."""
        logger.info("Shutting down bot...")
        
        self.is_running = False
        
        try:
            # Close car scanner HTTP client
            await cleanup_car_scanner()
            
            # Close bot session
            if self.bot:
                await self.bot.session.close()
            
            # Cleanup database connections
            # (SQLite doesn't need explicit cleanup, but we could add it here)
            
            logger.info("Bot shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            if self.is_running:
                # This will be caught by the event loop
                raise KeyboardInterrupt()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """
    Main entry point for the bot application.
    Handles initialization, startup, and graceful shutdown.
    """
    # Create bot instance
    bot_app = ProfessionalScanBot()
    
    try:
        # Setup signal handlers
        bot_app.setup_signal_handlers()
        
        # Initialize bot
        await bot_app.setup_bot()
        
        # Start the bot
        await bot_app.start_polling()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Ensure cleanup happens
        await bot_app.cleanup()

def run_bot():
    """
    Convenience function to run the bot.
    Handles event loop creation and exception handling.
    """
    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Print startup banner
    print("🛡️  Professional Telegram Scanning Bot")
    print("=" * 50)
    print(f"🚀 Version: 1.0 MVP")
    print(f"🏗️  Built with: aiogram 3.x + Python")
    print(f"🔍 Scanner: Multi-phase threat detection")
    print(f"📱 Integration: React Native (Expo) app")
    print("=" * 50)
    print(f"🔧 Configuration:")
    print(f"   Bot Token: {'✅ Set' if config.BOT_TOKEN else '❌ Missing'}")
    print(f"   Bot Username: {config.BOT_USERNAME or '❌ Missing'}")
    print(f"   Database: {config.DATABASE_PATH}")
    print(f"   Log Level: {config.LOG_LEVEL}")
    print(f"   Rate Limit: {config.RATE_LIMIT_MESSAGES}/min")
    print("=" * 50)
    
    # Validate configuration
    if not config.BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN is not set!")
        print("Please set your bot token in the .env file or environment variables.")
        sys.exit(1)
    
    if not config.BOT_USERNAME:
        print("⚠️  WARNING: BOT_USERNAME is not set!")
        print("Some features may not work properly without the bot username.")
    
    print("🚀 Starting bot...")
    print()
    
    # Run the bot
    run_bot()
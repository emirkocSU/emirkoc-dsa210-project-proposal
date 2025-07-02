#!/usr/bin/env python3
"""
Premium Car Listing Alert Bot - Telegram Bot Setup Utility

This script helps configure a Telegram bot with all necessary settings
for the Premium Car Listing Alert Bot service.
"""

import asyncio
import aiohttp
import json
import os
import sys
from typing import Dict, Optional

class TelegramBotConfigurator:
    """Utility class for configuring Telegram bot settings"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    async def get_bot_info(self) -> Optional[Dict]:
        """Get bot information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/getMe") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result')
                    else:
                        print(f"❌ Error getting bot info: HTTP {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Error getting bot info: {e}")
            return None
    
    async def set_webhook(self, webhook_url: str, secret_token: Optional[str] = None) -> bool:
        """Set webhook URL for the bot"""
        try:
            data = {
                "url": webhook_url,
                "allowed_updates": ["message", "callback_query", "inline_query"],
                "drop_pending_updates": True
            }
            
            if secret_token:
                data["secret_token"] = secret_token
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/setWebhook", json=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        print(f"✅ Webhook set successfully: {webhook_url}")
                        return True
                    else:
                        print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error setting webhook: {e}")
            return False
    
    async def get_webhook_info(self) -> Optional[Dict]:
        """Get current webhook information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/getWebhookInfo") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result')
                    else:
                        print(f"❌ Error getting webhook info: HTTP {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Error getting webhook info: {e}")
            return None
    
    async def set_commands(self) -> bool:
        """Set bot commands"""
        commands = [
            {"command": "start", "description": "🚀 Start using the bot and create account"},
            {"command": "help", "description": "❓ Get help and usage instructions"},
            {"command": "filters", "description": "🔧 Configure your car search filters"},
            {"command": "alerts", "description": "🔔 View and manage your alerts"},
            {"command": "scan", "description": "🔍 Analyze a car listing URL for damage"},
            {"command": "subscription", "description": "💎 Manage your premium subscription"},
            {"command": "profile", "description": "👤 View and edit your profile"},
            {"command": "settings", "description": "⚙️ Bot settings and preferences"},
            {"command": "support", "description": "💬 Contact support team"},
            {"command": "about", "description": "ℹ️ About this bot and features"}
        ]
        
        try:
            data = {"commands": commands}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/setMyCommands", json=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        print(f"✅ Commands set successfully ({len(commands)} commands)")
                        return True
                    else:
                        print(f"❌ Failed to set commands: {result.get('description', 'Unknown error')}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error setting commands: {e}")
            return False
    
    async def set_description(self, description: str) -> bool:
        """Set bot description"""
        try:
            data = {"description": description}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/setMyDescription", json=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        print("✅ Bot description set successfully")
                        return True
                    else:
                        print(f"❌ Failed to set description: {result.get('description', 'Unknown error')}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error setting description: {e}")
            return False
    
    async def set_short_description(self, short_description: str) -> bool:
        """Set bot short description"""
        try:
            data = {"short_description": short_description}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/setMyShortDescription", json=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        print("✅ Bot short description set successfully")
                        return True
                    else:
                        print(f"❌ Failed to set short description: {result.get('description', 'Unknown error')}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error setting short description: {e}")
            return False
    
    async def send_test_message(self, chat_id: str, message: str) -> bool:
        """Send a test message"""
        try:
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/sendMessage", json=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        print(f"✅ Test message sent successfully to {chat_id}")
                        return True
                    else:
                        print(f"❌ Failed to send test message: {result.get('description', 'Unknown error')}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error sending test message: {e}")
            return False

async def main():
    """Main configuration function"""
    print("🤖 Premium Car Listing Alert Bot - Setup Utility")
    print("=" * 60)
    
    # Get bot token from environment or user input
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        bot_token = input("Enter your bot token: ").strip()
        if not bot_token:
            print("❌ Bot token is required")
            sys.exit(1)
    
    # Initialize configurator
    configurator = TelegramBotConfigurator(bot_token)
    
    # Get bot info
    print("\n🔍 Getting bot information...")
    bot_info = await configurator.get_bot_info()
    
    if not bot_info:
        print("❌ Failed to get bot information. Please check your bot token.")
        sys.exit(1)
    
    print(f"✅ Bot found: {bot_info.get('first_name')} (@{bot_info.get('username')})")
    print(f"   ID: {bot_info.get('id')}")
    print(f"   Can join groups: {bot_info.get('can_join_groups')}")
    print(f"   Supports inline: {bot_info.get('supports_inline_queries')}")
    
    # Set bot description
    print("\n📝 Setting bot description...")
    description = """🚗 Premium Car Listing Alert Bot

Get instant notifications about new car listings that match your criteria with AI-powered damage detection.

✨ Features:
• Real-time car listing alerts
• Advanced filtering options  
• AI damage assessment with YOLOv8
• Turkish market integration
• Premium subscription service

Start with /start to begin!"""
    
    await configurator.set_description(description)
    
    # Set short description
    short_description = "Premium Car Listing Alert Bot with AI-powered damage detection. Get notified instantly when cars matching your criteria are listed for sale."
    await configurator.set_short_description(short_description)
    
    # Set commands
    print("\n📋 Setting bot commands...")
    await configurator.set_commands()
    
    # Configure webhook if URL provided
    webhook_url = os.getenv('WEBHOOK_URL')
    webhook_secret = os.getenv('WEBHOOK_SECRET')
    
    if webhook_url:
        print(f"\n🌐 Setting webhook URL: {webhook_url}")
        success = await configurator.set_webhook(webhook_url, webhook_secret)
        
        if success:
            # Verify webhook
            print("🔍 Verifying webhook...")
            webhook_info = await configurator.get_webhook_info()
            
            if webhook_info:
                print(f"✅ Webhook URL: {webhook_info.get('url')}")
                print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                print(f"   Max connections: {webhook_info.get('max_connections', 0)}")
                
                if webhook_info.get('last_error_date'):
                    print(f"⚠️ Last error: {webhook_info.get('last_error_message')}")
    else:
        print("\n⚠️ No webhook URL provided (WEBHOOK_URL environment variable)")
        print("   You can set it later using the Telegram Bot API")
    
    # Send test message if chat ID provided
    test_chat_id = os.getenv('TEST_CHAT_ID')
    if test_chat_id:
        print(f"\n📤 Sending test message to {test_chat_id}...")
        test_message = """🤖 <b>Premium Car Alert Bot is now active!</b>

✅ Bot configuration completed
✅ Commands set up
✅ Webhook configured
✅ Ready for production

Type /start to begin using the bot!"""
        
        await configurator.send_test_message(test_chat_id, test_message)
    
    print("\n🎉 Bot setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the bot by sending /start command")
    print("2. Configure your domain and SSL certificates")
    print("3. Deploy to production using ./scripts/deploy.sh")
    print("4. Monitor bot performance and user feedback")
    
    print(f"\n🔗 Your bot is available at: https://t.me/{bot_info.get('username')}")

def print_usage():
    """Print usage instructions"""
    print("""
Usage: python scripts/setup_bot.py

Environment variables:
  BOT_TOKEN       - Your Telegram bot token (required)
  WEBHOOK_URL     - Webhook URL for production (optional)
  WEBHOOK_SECRET  - Webhook secret token (optional)
  TEST_CHAT_ID    - Chat ID for test message (optional)

Example:
  export BOT_TOKEN="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  export WEBHOOK_URL="https://your-domain.com/webhook"
  export WEBHOOK_SECRET="your-secret-token"
  export TEST_CHAT_ID="123456789"
  python scripts/setup_bot.py
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_usage()
        sys.exit(0)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
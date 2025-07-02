# 🤖 Telegram Bot Setup Guide
## Premium Car Listing Alert Bot Configuration

This guide provides step-by-step instructions for creating and configuring a professional Telegram bot for the Premium Car Listing Alert Bot service.

## 📋 Table of Contents

1. [Creating the Bot](#creating-the-bot)
2. [Bot Configuration](#bot-configuration)
3. [Commands Setup](#commands-setup)
4. [Webhook Configuration](#webhook-configuration)
5. [Testing and Validation](#testing-and-validation)
6. [Production Deployment](#production-deployment)
7. [Security Considerations](#security-considerations)

## 🚀 Creating the Bot

### 1. Contact BotFather

1. Open Telegram and search for `@BotFather`
2. Start a conversation with `/start`
3. Create a new bot with `/newbot`

### 2. Bot Creation Process

```
You: /newbot
BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.

You: Premium Car Alert Bot
BotFather: Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.

You: PremiumCarAlertBot
BotFather: Done! Congratulations on your new bot. You will find it at t.me/PremiumCarAlertBot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. You can use this token to access the HTTP API:

1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ-EXAMPLE

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

### 3. Save Your Bot Token

**IMPORTANT**: Save your bot token securely. This is your `BOT_TOKEN` for the environment configuration.

```bash
# Example bot token (replace with your actual token)
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ-EXAMPLE
```

## ⚙️ Bot Configuration

### 1. Set Bot Description

```
/setdescription

🚗 Premium Car Listing Alert Bot

Get instant notifications about new car listings that match your criteria with AI-powered damage detection.

✨ Features:
• Real-time car listing alerts
• Advanced filtering options
• AI damage assessment with YOLOv8
• Turkish market integration
• Premium subscription service

Start with /start to begin!
```

### 2. Set About Section

```
/setabouttext

Premium Car Listing Alert Bot with AI-powered damage detection. Get notified instantly when cars matching your criteria are listed for sale.

🔗 Website: https://your-domain.com
📱 Mobile App: Coming Soon
💬 Support: @YourSupportBot
```

### 3. Set Bot Profile Picture

1. Use `/setuserpic`
2. Upload a professional logo/image for your bot
3. Recommended: 512x512 pixels, PNG format

### 4. Configure Bot Settings

```bash
# Enable inline mode (optional)
/setinline

# Set inline placeholder
/setinlinefeedback
Search cars: @PremiumCarAlertBot Toyota Corolla

# Enable groups (optional)
/setjoingroups
Enable

# Set privacy mode
/setprivacy
Disable
```

## 📝 Commands Setup

### 1. Set Bot Commands

```
/setcommands

start - 🚀 Start using the bot and create account
help - ❓ Get help and usage instructions
filters - 🔧 Configure your car search filters
alerts - 🔔 View and manage your alerts
scan - 🔍 Analyze a car listing URL for damage
subscription - 💎 Manage your premium subscription
profile - 👤 View and edit your profile
settings - ⚙️ Bot settings and preferences
support - 💬 Contact support team
about - ℹ️ About this bot and features
```

### 2. Advanced Command Configuration

For premium features, you can set up additional commands:

```bash
# Admin commands (for bot administrators)
/setcommands
@admin

admin - 🔧 Admin panel access
stats - 📊 Bot usage statistics
broadcast - 📢 Send message to all users
users - 👥 User management
logs - 📋 View system logs
```

## 🌐 Webhook Configuration

### 1. Set Webhook URL

Replace `YOUR_DOMAIN` and `YOUR_BOT_TOKEN` with your actual values:

```bash
# Set webhook
curl -X POST "https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://YOUR_DOMAIN.com/webhook",
       "allowed_updates": ["message", "callback_query", "inline_query"],
       "drop_pending_updates": true,
       "secret_token": "your-webhook-secret-here"
     }'
```

### 2. Verify Webhook

```bash
# Check webhook info
curl "https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getWebhookInfo"
```

Expected response:
```json
{
  "ok": true,
  "result": {
    "url": "https://your-domain.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": 0,
    "max_connections": 40,
    "allowed_updates": ["message", "callback_query", "inline_query"]
  }
}
```

## 🧪 Testing and Validation

### 1. Basic Bot Testing

```bash
# Test bot info
curl "https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getMe"

# Expected response
{
  "ok": true,
  "result": {
    "id": 1234567890,
    "is_bot": true,
    "first_name": "Premium Car Alert Bot",
    "username": "PremiumCarAlertBot",
    "can_join_groups": true,
    "can_read_all_group_messages": false,
    "supports_inline_queries": true
  }
}
```

### 2. Send Test Message

```bash
# Send test message to yourself
curl -X POST "https://api.telegram.org/bot{YOUR_BOT_TOKEN}/sendMessage" \
     -H "Content-Type: application/json" \
     -d '{
       "chat_id": "YOUR_CHAT_ID",
       "text": "🤖 Premium Car Alert Bot is now active!\n\n✅ Webhook configured\n✅ Commands set up\n✅ Ready for production"
     }'
```

### 3. Test Commands

Start a conversation with your bot and test:

1. `/start` - Should show welcome message
2. `/help` - Should display help information
3. `/filters` - Should show filter configuration
4. `/about` - Should show bot information

## 🚀 Production Deployment

### 1. Environment Configuration

Create your production `.env` file:

```bash
# Copy template
cp .env.production .env

# Edit with your bot details
nano .env
```

Update these values:
```bash
# Telegram Bot Configuration
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ-EXAMPLE
BOT_USERNAME=PremiumCarAlertBot
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_SECRET=your-secure-webhook-secret

# Generate secure webhook secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Deploy with Bot Token

```bash
# Deploy to production
./scripts/deploy.sh v1.0.0 production

# Verify bot is running
docker-compose logs -f telegram_bot
```

### 3. Set Production Webhook

```bash
# Set webhook in production
docker-compose exec telegram_bot python -c "
import os
import asyncio
import aiohttp

async def setup_webhook():
    bot_token = os.getenv('BOT_TOKEN')
    webhook_url = os.getenv('WEBHOOK_URL')
    webhook_secret = os.getenv('WEBHOOK_SECRET')
    
    url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
    data = {
        'url': webhook_url,
        'secret_token': webhook_secret,
        'allowed_updates': ['message', 'callback_query', 'inline_query'],
        'drop_pending_updates': True
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            print('Webhook setup result:', result)

asyncio.run(setup_webhook())
"
```

## 🔒 Security Considerations

### 1. Token Security

- **Never commit bot tokens to version control**
- Store tokens in environment variables only
- Use different tokens for development and production
- Regularly rotate tokens if compromised

### 2. Webhook Security

```bash
# Generate secure webhook secret
WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "WEBHOOK_SECRET=$WEBHOOK_SECRET" >> .env
```

### 3. Access Control

- Enable webhook secret verification
- Implement rate limiting
- Use HTTPS only
- Validate all incoming requests

### 4. Bot Permissions

```bash
# Disable unnecessary permissions
/setprivacy
Enable  # Bot can only see messages directed to it

/setjoingroups
Disable  # Prevent bot from being added to groups (optional)
```

## 📊 Monitoring and Analytics

### 1. Bot Analytics

Track important metrics:
- User registrations
- Message volume
- Command usage
- Error rates
- Response times

### 2. Webhook Monitoring

```bash
# Check webhook status regularly
curl "https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"

# Monitor webhook logs
docker-compose logs -f nginx | grep webhook
```

### 3. Health Checks

```bash
# Bot health endpoint
curl https://your-domain.com/health

# Bot status check
curl "https://api.telegram.org/bot{BOT_TOKEN}/getMe"
```

## 🔧 Advanced Configuration

### 1. Menu Button

```bash
# Set menu button
curl -X POST "https://api.telegram.org/bot{BOT_TOKEN}/setChatMenuButton" \
     -H "Content-Type: application/json" \
     -d '{
       "menu_button": {
         "type": "web_app",
         "text": "🚗 Car Search",
         "web_app": {
           "url": "https://your-domain.com/webapp"
         }
       }
     }'
```

### 2. Bot Commands Scope

```bash
# Set commands for different user types
curl -X POST "https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands" \
     -H "Content-Type: application/json" \
     -d '{
       "commands": [
         {"command": "start", "description": "🚀 Start using the bot"},
         {"command": "filters", "description": "🔧 Configure search filters"},
         {"command": "alerts", "description": "🔔 View your alerts"},
         {"command": "subscription", "description": "💎 Manage subscription"}
       ],
       "scope": {"type": "default"}
     }'
```

## 🎯 Bot Optimization

### 1. Message Templates

Create reusable message templates:

```python
# Welcome message template
WELCOME_MESSAGE = """
🚗 **Welcome to Premium Car Alert Bot!**

Get instant notifications about new car listings with AI-powered damage detection.

🎯 **Quick Setup:**
1. Configure your search filters with /filters
2. Activate premium subscription for full features
3. Receive instant alerts when cars match your criteria

✨ **Features:**
• Real-time listing alerts
• AI damage assessment
• Advanced filtering
• Turkish market integration

Ready to start? Use /filters to configure your preferences!
"""
```

### 2. Error Handling

```python
# Error message templates
ERROR_MESSAGES = {
    'subscription_required': '💎 This feature requires a premium subscription. Use /subscription to upgrade.',
    'invalid_url': '❌ Please provide a valid car listing URL.',
    'rate_limit': '⏱️ Please wait a moment before sending another request.',
    'maintenance': '🔧 The bot is currently under maintenance. Please try again later.'
}
```

## ✅ Deployment Checklist

- [ ] Bot created with BotFather
- [ ] Bot token saved securely
- [ ] Bot description and about text set
- [ ] Profile picture uploaded
- [ ] Commands configured
- [ ] Webhook URL set
- [ ] Environment variables configured
- [ ] Production deployment completed
- [ ] Webhook verified working
- [ ] Basic commands tested
- [ ] Error handling verified
- [ ] Monitoring enabled
- [ ] Security measures implemented

## 🚀 Next Steps

After completing the bot setup:

1. **Test thoroughly** - Verify all commands and features
2. **Monitor performance** - Watch logs and metrics
3. **User onboarding** - Create user guides and tutorials
4. **Marketing** - Promote your bot to target users
5. **Feedback collection** - Gather user feedback for improvements

---

## 🎉 Bot Setup Complete!

Your Premium Car Listing Alert Bot is now configured and ready for production use with:

✅ **Professional bot identity**  
✅ **Comprehensive command set**  
✅ **Secure webhook configuration**  
✅ **Production-ready deployment**  
✅ **Monitoring and analytics**  
✅ **Security best practices**

**Your bot is live at**: `https://t.me/PremiumCarAlertBot`

---

*For technical support or questions about bot configuration, please refer to the Telegram Bot API documentation or contact the development team.*
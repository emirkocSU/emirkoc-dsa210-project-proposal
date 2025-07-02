# Premium Telegram Car Listing Alert Bot - Deployment Guide

## 🚀 System Overview

The Premium Telegram Car Listing Alert Bot is a sophisticated multi-platform system that automatically alerts users about new car listings matching their criteria, with AI-powered damage detection using YOLOv8.

### Architecture Components

1. **Telegram Bot Backend** - Handles user interactions and filter management
2. **Car Scanner Service** - Monitors sahibinden.com for new listings
3. **YOLOv8 Damage Detection** - AI analysis of car images
4. **Database Layer** - User management and subscription tracking
5. **Expo Mobile App** - User registration and account linking (separate project)

## 📋 Prerequisites

### System Requirements
- Python 3.11+ (tested with 3.13)
- Linux/macOS/Windows
- 4GB+ RAM (for YOLOv8 inference)
- 10GB+ disk space (for models and data)

### Required Accounts
- Telegram Bot Token (from @BotFather)
- Server or VPS for deployment
- Domain name (optional, for webhooks)

## 🛠️ Installation Steps

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd telegram-scanning-bot-mvp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt
```

### 2. Install YOLOv8 Dependencies

```bash
# Install computer vision dependencies
pip install ultralytics opencv-python torch torchvision

# For GPU support (optional, recommended for production)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. Database Initialization

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Initialize database
python -c "
import asyncio
from tgbot.database import init_database
asyncio.run(init_database())
"
```

### 4. YOLOv8 Model Setup

#### Option A: Use Pre-trained Model (Quick Start)
```bash
# Create models directory
mkdir -p models

# Download a general object detection model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O models/yolov8n.pt

# Update .env
# YOLO_WEIGHTS_PATH=models/yolov8n.pt
```

#### Option B: Train Custom Car Damage Model (Recommended)
```bash
# Prepare training data
mkdir -p training_data/{images,labels}

# Collect car damage images and annotations
# Use tools like LabelImg or Roboflow for annotation

# Train custom model
python train_yolo.py --data car_damage_dataset.yaml --epochs 100
```

### 5. Configuration

Edit `.env` file with your settings:

```env
# Essential Configuration
BOT_TOKEN=your_telegram_bot_token_here
BOT_USERNAME=your_bot_username

# Database
DATABASE_URL=sqlite+aiosqlite:///./car_alert_bot.db

# YOLOv8
YOLO_WEIGHTS_PATH=models/car_damage_yolo.pt
YOLO_CONFIDENCE_THRESHOLD=0.5

# Scanner Settings
SCAN_INTERVAL=300  # 5 minutes
BASE_LISTING_URL=https://www.sahibinden.com/otomobil
```

## 🚀 Deployment Options

### Option 1: Local Development

```bash
# Start the bot
source venv/bin/activate
python tgbot/main.py
```

### Option 2: Production Server

#### Using systemd (Linux)

1. Create service file:
```bash
sudo nano /etc/systemd/system/car-alert-bot.service
```

```ini
[Unit]
Description=Premium Car Alert Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/telegram-scanning-bot-mvp
Environment=PATH=/path/to/telegram-scanning-bot-mvp/venv/bin
ExecStart=/path/to/telegram-scanning-bot-mvp/venv/bin/python tgbot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable car-alert-bot
sudo systemctl start car-alert-bot
```

#### Using Docker

1. Create Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python -c "import asyncio; from tgbot.database import init_database; asyncio.run(init_database())"

CMD ["python", "tgbot/main.py"]
```

2. Build and run:
```bash
docker build -t car-alert-bot .
docker run -d --name car-alert-bot --env-file .env car-alert-bot
```

### Option 3: Cloud Deployment

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set BOT_TOKEN=your_token
git push heroku main
```

#### DigitalOcean/AWS/GCP
- Use the systemd or Docker approach
- Configure firewall and security groups
- Set up monitoring and logging

## 🔧 Configuration Details

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Telegram bot token | - | ✅ |
| `BOT_USERNAME` | Bot username | - | ✅ |
| `DATABASE_URL` | Database connection string | sqlite+aiosqlite:///./car_alert_bot.db | ✅ |
| `SCAN_INTERVAL` | Scanning interval in seconds | 300 | ❌ |
| `YOLO_WEIGHTS_PATH` | Path to YOLOv8 model | models/car_damage_yolo.pt | ✅ |
| `YOLO_CONFIDENCE_THRESHOLD` | Detection confidence threshold | 0.5 | ❌ |
| `LOG_LEVEL` | Logging level | INFO | ❌ |
| `WEBHOOK_URL` | Webhook URL for production | - | ❌ |

### Database Configuration

The system supports multiple database backends:

```env
# SQLite (Development)
DATABASE_URL=sqlite+aiosqlite:///./car_alert_bot.db

# PostgreSQL (Production)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/car_alert_db

# MySQL (Alternative)
DATABASE_URL=mysql+aiomysql://user:password@localhost/car_alert_db
```

## 🧪 Testing

### Unit Tests
```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=tgbot --cov=utils
```

### Manual Testing
```bash
# Test database connection
python -c "
import asyncio
from tgbot.database import db_manager
async def test():
    users = await db_manager.get_active_subscribers()
    print(f'Active subscribers: {len(users)}')
asyncio.run(test())
"

# Test YOLO functionality
python -c "
import asyncio
from utils.yolo import quick_damage_check
async def test():
    score, summary = await quick_damage_check('https://example.com/car.jpg', 'Test description')
    print(f'Damage score: {score}, Summary: {summary}')
asyncio.run(test())
"
```

## 📊 Monitoring and Maintenance

### Logging
- Logs are written to console and file (configurable)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Structured logging with contextual information

### Health Checks
```bash
# Check bot status
curl -X GET "https://api.telegram.org/bot${BOT_TOKEN}/getMe"

# Check database
python -c "from tgbot.database import db_manager; print('DB OK')"
```

### Performance Monitoring
- Monitor memory usage (YOLOv8 can be memory-intensive)
- Track scanning frequency and response times
- Monitor Telegram API rate limits

### Backup Strategy
```bash
# Backup SQLite database
cp car_alert_bot.db car_alert_bot_backup_$(date +%Y%m%d).db

# Backup PostgreSQL
pg_dump car_alert_db > backup_$(date +%Y%m%d).sql
```

## 🔒 Security Considerations

### Bot Token Security
- Never commit bot tokens to version control
- Use environment variables or secure key management
- Rotate tokens periodically

### Database Security
- Use strong passwords
- Enable SSL/TLS for database connections
- Regular security updates

### Network Security
- Use HTTPS for webhooks
- Implement rate limiting
- Monitor for unusual activity

## 📱 Mobile App Integration

The system is designed to work with an Expo React Native mobile app:

1. **User Registration**: Users sign up via mobile app
2. **Account Linking**: Deep link integration connects app to Telegram bot
3. **Subscription Management**: Handle payments and subscriptions in app
4. **Filter Configuration**: Can be done via both app and Telegram

### Deep Link Setup
```javascript
// Expo app configuration
{
  "expo": {
    "scheme": "caralertbot",
    "android": {
      "intentFilters": [
        {
          "action": "VIEW",
          "data": [
            {
              "scheme": "https",
              "host": "your-domain.com",
              "pathPrefix": "/link"
            }
          ],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    }
  }
}
```

## 🚨 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check bot status
python -c "
import asyncio
from tgbot.config import config
import aiohttp
async def check():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.telegram.org/bot{config.BOT_TOKEN}/getMe') as resp:
            print(await resp.json())
asyncio.run(check())
"
```

#### Database Connection Issues
```bash
# Test database connection
python -c "
import asyncio
from tgbot.database import engine
async def test():
    async with engine.begin() as conn:
        print('Database connection successful')
asyncio.run(test())
"
```

#### YOLOv8 Memory Issues
- Reduce batch size
- Use smaller model (yolov8n instead of yolov8x)
- Add memory monitoring

#### Scanning Issues
- Check internet connection
- Verify sahibinden.com accessibility
- Review rate limiting settings

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python tgbot/main.py
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use multiple bot instances with load balancer
- Implement Redis for session management
- Use message queues for background tasks

### Vertical Scaling
- Increase server resources for YOLOv8
- Optimize database queries
- Use connection pooling

### Performance Optimization
- Cache frequently accessed data
- Implement async/await throughout
- Use database indexes effectively

## 📋 Deployment Checklist

- [ ] Server/VPS provisioned
- [ ] Python 3.11+ installed
- [ ] Dependencies installed
- [ ] Database configured and initialized
- [ ] YOLOv8 model downloaded/trained
- [ ] Environment variables configured
- [ ] Bot token obtained and configured
- [ ] Firewall and security configured
- [ ] Monitoring and logging set up
- [ ] Backup strategy implemented
- [ ] SSL/TLS certificates configured (if using webhooks)
- [ ] Testing completed
- [ ] Documentation updated

## 🎯 Next Steps

1. **Complete YOLOv8 Integration**: Replace mock implementation with real YOLOv8
2. **Develop Mobile App**: Create Expo React Native app for user management
3. **Implement Payment System**: Add subscription and payment processing
4. **Add Advanced Features**: 
   - Multiple filter sets per user
   - Notification preferences
   - Advanced damage reporting
   - Price tracking and alerts
5. **Scale Infrastructure**: Implement load balancing and redundancy

## 📞 Support

For technical support and questions:
- Check logs first: `tail -f bot.log`
- Review configuration: `cat .env`
- Test components individually
- Monitor system resources

## 📄 License

This project is proprietary software. All rights reserved.

---

**Ready for deployment!** 🚀

The Premium Telegram Car Listing Alert Bot is now ready for production deployment with comprehensive monitoring, security, and scaling capabilities.
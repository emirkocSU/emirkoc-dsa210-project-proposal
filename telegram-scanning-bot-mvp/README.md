# 🚗 Premium Car Alert Bot
## AI-Powered Telegram Bot with YOLOv8 Damage Detection

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-AI-green.svg)](https://ultralytics.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Premium Telegram bot that provides real-time car listing alerts with AI-powered damage detection using YOLOv8. Get instant notifications when cars matching your criteria are listed, complete with damage assessment and detailed analysis.

## ✨ Features

- 🤖 **Smart Telegram Bot** - Interactive bot with intuitive commands
- 🧠 **YOLOv8 AI Integration** - Real-time car damage detection
- 🔔 **Real-time Alerts** - Instant notifications for matching cars
- 🔍 **Advanced Filtering** - Precise search criteria configuration
- 📱 **Mobile App** - Cross-platform React Native companion app
- 💎 **Premium Subscription** - Advanced features with payment integration
- 🇹🇷 **Turkish Market Focus** - Optimized for Turkish car listings
- 🐳 **Docker Ready** - Production-ready containerized deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- PostgreSQL Database
- Redis Cache

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/premium-car-alert-bot.git
cd premium-car-alert-bot
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.production .env

# Edit configuration
nano .env
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Initialize database
python -c "
import asyncio
from tgbot.database import DatabaseManager

async def init_db():
    db = DatabaseManager()
    await db.initialize()
    print('✅ Database initialized')

asyncio.run(init_db())
"
```

### 5. Run Development Server

```bash
# Start the bot
python -m tgbot.main
```

## 🐳 Production Deployment

### Docker Compose (Recommended)

```bash
# Deploy with Docker Compose
./scripts/deploy.sh v1.0.0 production

# Or manually
docker-compose up -d
```

### Manual Deployment

```bash
# Build Docker image
docker build -t premium-car-bot .

# Run with environment
docker run -d --env-file .env premium-car-bot
```

## � Mobile App Development

The companion mobile app is built with Expo and React Native:

```bash
# Navigate to mobile app
cd expo-app

# Install dependencies
npm install

# Start development server
npx expo start
```

## 🔧 Configuration

### Telegram Bot Setup

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Set webhook URL
4. Configure bot commands

```bash
# Use our setup script
python scripts/setup_bot.py
```

### Environment Variables

```bash
# Telegram Configuration
BOT_TOKEN=your_telegram_bot_token
BOT_USERNAME=your_bot_username
WEBHOOK_URL=https://your-domain.com/webhook

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=car_listing_bot
POSTGRES_USER=car_bot_user
POSTGRES_PASSWORD=your_secure_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# YOLOv8 Configuration
YOLO_WEIGHTS_PATH=models/car_damage_yolo.pt
YOLO_CONFIDENCE_THRESHOLD=0.4
```

## 🧠 AI Damage Detection

The bot uses YOLOv8 for real-time car damage detection:

- **Damage Types**: Dents, scratches, cracks, rust, broken parts, paint damage
- **Processing Time**: < 30 seconds per analysis
- **Accuracy**: 85%+ detection rate
- **Languages**: Turkish keyword detection + visual analysis

### Usage

```bash
# Analyze car listing
/scan https://sahibinden.com/ilan/vasita-otomobil-toyota-corolla-12345

# Quick damage check
/quick_scan [image_url]
```

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and create account |
| `/help` | Get help and usage instructions |
| `/filters` | Configure car search filters |
| `/alerts` | View and manage your alerts |
| `/scan [url]` | Analyze car listing for damage |
| `/subscription` | Manage premium subscription |
| `/profile` | View and edit profile |
| `/settings` | Bot settings and preferences |

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │  Telegram Bot   │    │   Web Admin     │
│  (iOS/Android)  │    │   (Premium)     │    │    Panel        │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │       API Gateway           │
                    │    (Nginx + Rate Limiting)  │
                    └─────────────┬───────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │     Backend Services        │
                    │  (Python + FastAPI/aiogram) │
                    └─────────────┬───────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│   PostgreSQL    │    │      Redis      │    │   YOLOv8 AI     │
│   Database      │    │     Cache       │    │    Engine       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## � Monitoring

The system includes comprehensive monitoring:

- **Prometheus** - Metrics collection
- **Grafana** - Dashboards and visualization
- **Sentry** - Error tracking
- **Custom Metrics** - Bot-specific KPIs

Access monitoring at:
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

## 🧪 Testing

### Unit Tests

```bash
# Run unit tests
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=tgbot
```

### Integration Tests

```bash
# Test bot functionality
python tests/test_bot_integration.py

# Test AI detection
python tests/test_yolo_integration.py
```

### Beta Testing

We have a comprehensive beta testing program:

```bash
# Join beta program
# Visit: beta.premiumcaralert.com
```

## � Documentation

- [🚀 Production Deployment Guide](PRODUCTION_DEPLOYMENT.md)
- [🤖 Telegram Bot Setup](TELEGRAM_BOT_SETUP.md)
- [📱 Mobile App Development](EXPO_APP_DEVELOPMENT.md)
- [🧪 Beta Testing Program](BETA_TESTING_PROGRAM.md)
- [🏛️ Architecture Overview](ARCHITECTURE.md)
- [🔧 API Documentation](API_DOCUMENTATION.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- � Email: support@premiumcaralert.com
- 💬 Telegram: [@PremiumCarAlertBot](https://t.me/PremiumCarAlertBot)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/premium-car-alert-bot/issues)
- 📚 Wiki: [Project Wiki](https://github.com/yourusername/premium-car-alert-bot/wiki)

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://ultralytics.com) - AI object detection
- [aiogram](https://aiogram.dev) - Telegram Bot framework
- [Expo](https://expo.dev) - React Native development platform
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework

---

**Made with ❤️ for the Turkish automotive community**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/premium-car-alert-bot.svg?style=social&label=Star)](https://github.com/yourusername/premium-car-alert-bot)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/premium-car-alert-bot.svg?style=social&label=Fork)](https://github.com/yourusername/premium-car-alert-bot/fork)
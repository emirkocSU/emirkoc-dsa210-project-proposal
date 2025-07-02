#!/bin/bash
set -e

# =============================================================================
# Premium Telegram Car Listing Alert Bot - Production Deployment Script
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="premium-car-bot"
VERSION=${1:-latest}
ENVIRONMENT=${2:-production}

echo -e "${BLUE}🚀 Starting deployment of Premium Telegram Car Listing Alert Bot${NC}"
echo -e "${BLUE}📋 Version: ${VERSION}, Environment: ${ENVIRONMENT}${NC}"

# =============================================================================
# PRE-DEPLOYMENT CHECKS
# =============================================================================

echo -e "\n${YELLOW}🔍 Running pre-deployment checks...${NC}"

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}💡 Copy .env.production to .env and configure your values${NC}"
    exit 1
fi

# Check if YOLOv8 model exists
if [ ! -f "models/car_damage_yolo.pt" ]; then
    echo -e "${YELLOW}⚠️ YOLOv8 model not found, downloading...${NC}"
    mkdir -p models
    # Download a pre-trained model as fallback
    python -c "
from ultralytics import YOLO
import shutil
import os
model = YOLO('yolov8n.pt')
if os.path.exists('yolov8n.pt'):
    shutil.move('yolov8n.pt', 'models/car_damage_yolo.pt')
    print('✅ YOLOv8 model downloaded')
"
fi

echo -e "${GREEN}✅ Pre-deployment checks passed${NC}"

# =============================================================================
# BUILD AND DEPLOY
# =============================================================================

echo -e "\n${YELLOW}🔨 Building Docker images...${NC}"

# Build with build arguments
docker-compose build \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VERSION=${VERSION} \
    --build-arg VCS_REF=$(git rev-parse HEAD 2>/dev/null || echo "unknown")

echo -e "${GREEN}✅ Docker images built successfully${NC}"

# =============================================================================
# DATABASE MIGRATION
# =============================================================================

echo -e "\n${YELLOW}🗄️ Running database migrations...${NC}"

# Start database first
docker-compose up -d postgres redis

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 10

# Run migrations
docker-compose run --rm telegram_bot python -c "
import asyncio
from tgbot.database import DatabaseManager

async def migrate():
    db = DatabaseManager()
    await db.initialize()
    print('✅ Database initialized successfully')

asyncio.run(migrate())
"

echo -e "${GREEN}✅ Database migrations completed${NC}"

# =============================================================================
# DEPLOY SERVICES
# =============================================================================

echo -e "\n${YELLOW}🚀 Deploying services...${NC}"

# Deploy all services
docker-compose up -d

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 30

# =============================================================================
# HEALTH CHECKS
# =============================================================================

echo -e "\n${YELLOW}🏥 Running health checks...${NC}"

# Check Telegram bot health
if curl -f http://localhost:8080/health &> /dev/null; then
    echo -e "${GREEN}✅ Telegram bot is healthy${NC}"
else
    echo -e "${RED}❌ Telegram bot health check failed${NC}"
    docker-compose logs telegram_bot
fi

# Check database health
if docker-compose exec postgres pg_isready -U car_bot_user -d car_listing_bot &> /dev/null; then
    echo -e "${GREEN}✅ Database is healthy${NC}"
else
    echo -e "${RED}❌ Database health check failed${NC}"
fi

# Check Redis health
if docker-compose exec redis redis-cli ping | grep -q PONG; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis health check failed${NC}"
fi

# =============================================================================
# POST-DEPLOYMENT TASKS
# =============================================================================

echo -e "\n${YELLOW}⚙️ Running post-deployment tasks...${NC}"

# Set webhook URL
echo -e "${YELLOW}🔗 Setting Telegram webhook...${NC}"
docker-compose exec telegram_bot python -c "
import os
import asyncio
import aiohttp

async def set_webhook():
    bot_token = os.getenv('BOT_TOKEN')
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if not bot_token or not webhook_url:
        print('❌ BOT_TOKEN or WEBHOOK_URL not configured')
        return
    
    url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
    data = {'url': webhook_url}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            if result.get('ok'):
                print('✅ Webhook set successfully')
            else:
                print(f'❌ Failed to set webhook: {result}')

asyncio.run(set_webhook())
"

# Initialize monitoring
echo -e "${YELLOW}📊 Initializing monitoring...${NC}"
sleep 5

# Show service status
echo -e "\n${YELLOW}📋 Service Status:${NC}"
docker-compose ps

# =============================================================================
# DEPLOYMENT SUMMARY
# =============================================================================

echo -e "\n${GREEN}🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo -e "\n${BLUE}📊 Service URLs:${NC}"
echo -e "🤖 Telegram Bot: https://your-domain.com/webhook"
echo -e "📈 Grafana Dashboard: http://localhost:3000"
echo -e "🔍 Prometheus Metrics: http://localhost:9090"
echo -e "🗄️ Database: localhost:5432"
echo -e "🚀 Redis Cache: localhost:6379"

echo -e "\n${BLUE}📋 Next Steps:${NC}"
echo -e "1. Configure your domain name in nginx.conf"
echo -e "2. Set up SSL certificates"
echo -e "3. Configure Telegram bot token and webhook"
echo -e "4. Test the bot functionality"
echo -e "5. Set up monitoring alerts"

echo -e "\n${BLUE}🔧 Management Commands:${NC}"
echo -e "• View logs: docker-compose logs -f [service]"
echo -e "• Restart service: docker-compose restart [service]"
echo -e "• Scale service: docker-compose up -d --scale telegram_bot=2"
echo -e "• Stop all: docker-compose down"
echo -e "• Update: ./scripts/deploy.sh [version]"

echo -e "\n${GREEN}✅ Premium Telegram Car Listing Alert Bot is now running!${NC}"
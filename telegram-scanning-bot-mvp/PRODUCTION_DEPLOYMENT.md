# 🚀 Production Deployment Guide
## Premium Telegram Car Listing Alert Bot with YOLOv8 AI

This guide provides step-by-step instructions for deploying the Premium Telegram Car Listing Alert Bot to production with enterprise-grade infrastructure.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Domain and SSL Configuration](#domain-and-ssl-configuration)
4. [Environment Configuration](#environment-configuration)
5. [Deployment Process](#deployment-process)
6. [Monitoring Setup](#monitoring-setup)
7. [Security Hardening](#security-hardening)
8. [Backup and Recovery](#backup-and-recovery)
9. [Maintenance and Updates](#maintenance-and-updates)
10. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Server Requirements
- **CPU**: Minimum 4 cores (8 cores recommended for YOLOv8)
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: Minimum 100GB SSD
- **Network**: Stable internet connection with public IP
- **OS**: Ubuntu 20.04+ or CentOS 8+

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Nginx (handled by container)
- Git
- SSL certificates

### Telegram Bot Setup
1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Set bot commands and description
4. Configure webhook URL

## 🖥️ Server Setup

### 1. Initial Server Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git htop nano ufw fail2ban

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Create application user
sudo useradd -m -s /bin/bash carbot
sudo usermod -aG sudo carbot
```

### 2. Docker Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker carbot

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 3. Application Deployment

```bash
# Switch to application user
sudo su - carbot

# Clone repository
git clone https://github.com/your-username/premium-car-bot.git
cd premium-car-bot

# Create necessary directories
mkdir -p logs data nginx/ssl
```

## 🌐 Domain and SSL Configuration

### 1. Domain Setup
1. Point your domain to your server's IP address
2. Configure DNS A records:
   - `your-domain.com` → `YOUR_SERVER_IP`
   - `www.your-domain.com` → `YOUR_SERVER_IP`

### 2. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Generate SSL certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown -R carbot:carbot nginx/ssl/
```

### 3. Update Nginx Configuration

```bash
# Edit nginx configuration
nano nginx/nginx.conf

# Replace 'your-domain.com' with your actual domain
sed -i 's/your-domain.com/yourdomain.com/g' nginx/nginx.conf
```

## ⚙️ Environment Configuration

### 1. Create Production Environment File

```bash
# Copy template
cp .env.production .env

# Edit configuration
nano .env
```

### 2. Required Configuration Values

```bash
# Telegram Bot
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ
BOT_USERNAME=your_bot_username
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_SECRET=your-secure-webhook-secret

# Database
POSTGRES_PASSWORD=your-secure-database-password
SECRET_KEY=your-32-character-secret-key-here
ENCRYPTION_KEY=your-32-character-encryption-key

# Domain
DOMAIN=your-domain.com

# Monitoring
GRAFANA_PASSWORD=your-grafana-admin-password
```

### 3. Generate Secure Keys

```bash
# Generate secure keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('WEBHOOK_SECRET=' + secrets.token_urlsafe(16))"
```

## 🚀 Deployment Process

### 1. Run Deployment Script

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Deploy to production
./scripts/deploy.sh v1.0.0 production
```

### 2. Manual Deployment Steps

If you prefer manual deployment:

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f telegram_bot
```

### 3. Set Telegram Webhook

```bash
# Set webhook URL
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
     -H "Content-Type: application/json" \
     -d "{\"url\":\"https://your-domain.com/webhook\"}"

# Verify webhook
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
```

## 📊 Monitoring Setup

### 1. Access Monitoring Dashboards

- **Grafana**: http://your-domain.com:3000
  - Username: `admin`
  - Password: Set in `.env` file

- **Prometheus**: http://your-domain.com:9090

### 2. Configure Alerting

```bash
# Create alert rules
mkdir -p monitoring/rules

# Add alert rules for critical metrics
cat > monitoring/rules/alerts.yml << EOF
groups:
  - name: telegram_bot_alerts
    rules:
      - alert: BotDown
        expr: up{job="telegram-bot"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Telegram bot is down"
          
      - alert: HighMemoryUsage
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
EOF
```

## 🔒 Security Hardening

### 1. Server Security

```bash
# Configure fail2ban
sudo nano /etc/fail2ban/jail.local

# Add SSH protection
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

# Restart fail2ban
sudo systemctl restart fail2ban
```

### 2. Docker Security

```bash
# Enable Docker content trust
echo 'export DOCKER_CONTENT_TRUST=1' >> ~/.bashrc

# Scan images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image premium-car-bot_telegram_bot
```

### 3. Application Security

- Change default passwords
- Enable rate limiting
- Configure IP whitelisting for admin endpoints
- Regular security updates

## 💾 Backup and Recovery

### 1. Database Backup

```bash
# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/carbot/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T postgres pg_dump -U car_bot_user car_listing_bot > $BACKUP_DIR/db_$DATE.sql

# Compress and clean old backups
gzip $BACKUP_DIR/db_$DATE.sql
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x scripts/backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /home/carbot/premium-car-bot/scripts/backup.sh
```

### 2. Full System Backup

```bash
# Backup application data
tar -czf backup_$(date +%Y%m%d).tar.gz \
  --exclude='venv' --exclude='__pycache__' \
  --exclude='*.pyc' --exclude='logs' \
  /home/carbot/premium-car-bot/
```

## 🔄 Maintenance and Updates

### 1. Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Clean up old images
docker system prune -a
```

### 2. Application Updates

```bash
# Pull latest code
git pull origin main

# Deploy new version
./scripts/deploy.sh v1.1.0 production

# Rollback if needed
docker-compose down
git checkout v1.0.0
./scripts/deploy.sh v1.0.0 production
```

### 3. Health Monitoring

```bash
# Check service health
curl -f https://your-domain.com/health

# Monitor logs
docker-compose logs -f --tail=100 telegram_bot

# Check resource usage
docker stats
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Bot Not Responding
```bash
# Check bot logs
docker-compose logs telegram_bot

# Verify webhook
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"

# Test webhook endpoint
curl -X POST https://your-domain.com/webhook
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check database logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U car_bot_user -d car_listing_bot
```

#### 3. YOLOv8 Model Issues
```bash
# Check model file
ls -la models/car_damage_yolo.pt

# Test YOLOv8 functionality
docker-compose exec telegram_bot python -c "
from utils.yolo import initialize_yolo_model
detector = initialize_yolo_model()
print('YOLOv8 status:', 'OK' if detector else 'FAILED')
"
```

#### 4. SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Renew certificate
sudo certbot renew
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Connect to database and run optimization queries
VACUUM ANALYZE;
REINDEX DATABASE car_listing_bot;

-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### 2. Memory Optimization
```bash
# Adjust Docker memory limits
# Edit docker-compose.yml memory settings

# Monitor memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## 📞 Support and Maintenance

### Monitoring Checklist
- [ ] All services running
- [ ] Webhook responding
- [ ] Database accessible
- [ ] SSL certificate valid
- [ ] Backup working
- [ ] Logs rotating
- [ ] Alerts configured

### Emergency Contacts
- Server Provider Support
- Domain Registrar Support
- Telegram Bot Support: @BotSupport

---

## 🎉 Deployment Complete!

Your Premium Telegram Car Listing Alert Bot is now running in production with:

✅ **Real YOLOv8 AI damage detection**  
✅ **Enterprise-grade infrastructure**  
✅ **Comprehensive monitoring**  
✅ **Security hardening**  
✅ **Automated backups**  
✅ **SSL encryption**  
✅ **Production-ready architecture**

**Next Steps**: Configure your Telegram bot, test functionality, and begin user onboarding!

---

*For technical support or questions, please refer to the documentation or contact the development team.*
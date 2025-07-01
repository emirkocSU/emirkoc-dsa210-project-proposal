# GitHub Bağlantı Sorunu Çözüm Kılavuzu

## 🔍 Sorun Analizi

Workspace'ten GitHub'a bağlantı çalışıyor ancak uygulamadan bağlanmıyor. Bu durumun olası nedenleri:

1. **Eksik Environment Variables (.env dosyası)**
2. **GitHub API Token eksik veya yanlış**
3. **Gerekli Python kütüphaneleri eksik**
4. **Network/Firewall kısıtlamaları**
5. **GitHub API rate limiting**

## ✅ Çözüm Adımları

### 1. Environment Variables Kurulumu

Önce `.env` dosyasını düzgün şekilde yapılandırın:

```bash
cd /workspace/telegram-scanning-bot-mvp/tgbot
```

`.env` dosyasını düzenleyin ve şu değerleri ekleyin:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_actual_bot_token_here
BOT_USERNAME=your_actual_bot_username

# GitHub API Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_API_URL=https://api.github.com

# Database Configuration
DATABASE_PATH=../shared/database.db

# Security Settings
SECRET_KEY=your-secret-key-change-in-production
TOKEN_EXPIRATION_HOURS=24

# Rate Limiting
RATE_LIMIT_MESSAGES=10
RATE_LIMIT_WINDOW=60

# Scanning Settings
MAX_SCAN_TIMEOUT=30
MAX_URL_LENGTH=2048

# Logging
LOG_LEVEL=INFO
```

### 2. GitHub Personal Access Token Oluşturma

1. GitHub'da Settings > Developer settings > Personal access tokens > Tokens (classic) sayfasına gidin
2. "Generate new token (classic)" butonuna tıklayın
3. Token için bir isim verin (örn: "Telegram Bot API Access")
4. Gerekli izinleri seçin:
   - `repo` (repository erişimi için)
   - `read:user` (kullanıcı bilgileri için)
   - `read:org` (organizasyon bilgileri için)
5. Token'ı kopyalayın ve `.env` dosyasında `GITHUB_TOKEN` değerine yapıştırın

### 3. Gerekli Kütüphaneleri Yükleme

```bash
cd /workspace/telegram-scanning-bot-mvp
pip install -r requirements.txt
```

Eğer hata alırsanız, manuel olarak GitHub kütüphanelerini yükleyin:

```bash
pip install PyGithub github3.py requests aiohttp
```

### 4. Bağlantı Testi

Bot'u çalıştırın ve GitHub bağlantısını test edin:

```bash
cd /workspace/telegram-scanning-bot-mvp/tgbot
python main.py
```

Bot çalıştıktan sonra Telegram'da şu komutları test edin:

- `/github` - GitHub bağlantı durumunu kontrol eder
- `/repo microsoft/vscode` - Repository bilgilerini getirir
- `/search python` - Repository arama yapar

### 5. Hata Ayıklama

#### Yaygın Hatalar ve Çözümleri:

**Hata: "GitHub client not initialized"**
```bash
# Çözüm: GITHUB_TOKEN'ı kontrol edin
echo $GITHUB_TOKEN  # Boş ise .env dosyasını kontrol edin
```

**Hata: "Authentication failed"**
```bash
# Çözüm: Token'ın geçerli olduğunu kontrol edin
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

**Hata: "Rate limit exceeded"**
```bash
# Çözüm: Rate limit durumunu kontrol edin
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

**Hata: "Import github could not be resolved"**
```bash
# Çözüm: PyGithub kütüphanesini yükleyin
pip install PyGithub
```

### 6. Network Bağlantı Kontrolü

GitHub API'ye erişimi test edin:

```bash
# GitHub API'ye erişim testi
curl -v https://api.github.com

# DNS çözümleme testi
nslookup api.github.com

# Port bağlantı testi
telnet api.github.com 443
```

### 7. Bot Konfigürasyon Kontrolü

Bot başlatıldığında şu çıktıları görmelisiniz:

```
🛡️  Professional Telegram Scanning Bot
==================================================
🚀 Version: 1.0 MVP
🏗️  Built with: aiogram 3.x + Python
🔍 Scanner: Multi-phase threat detection
📱 Integration: React Native (Expo) app
🔗 GitHub: ✅ Enabled
==================================================
🔧 Configuration:
   Bot Token: ✅ Set
   Bot Username: your_bot_username
   GitHub Token: ✅ Set
   Database: ../shared/database.db
   Log Level: INFO
   Rate Limit: 10/min
==================================================
```

## 🚀 Test Senaryoları

### Temel Bağlantı Testi
1. Bot'u başlatın
2. Telegram'da `/github` komutunu gönderin
3. Başarılı bağlantı mesajı görmelisiniz

### Repository Bilgi Testi
1. `/repo microsoft/vscode` komutunu gönderin
2. Repository detaylarını görmelisiniz

### Arama Testi
1. `/search machine learning` komutunu gönderin
2. Arama sonuçlarını görmelisiniz

## 🔧 İleri Düzey Sorun Giderme

### Log Dosyası İnceleme
```bash
cd /workspace/telegram-scanning-bot-mvp/tgbot
tail -f bot.log
```

### Debug Modu Etkinleştirme
`.env` dosyasında:
```env
LOG_LEVEL=DEBUG
```

### Manuel API Testi
Python konsolu ile test:
```python
from github import Github
g = Github("your_token_here")
user = g.get_user()
print(f"Authenticated as: {user.login}")
```

## 📞 Yardım

Eğer sorun devam ediyorsa:

1. **Log dosyalarını kontrol edin** (`bot.log`)
2. **GitHub token'ın geçerli olduğunu doğrulayın**
3. **Network bağlantısını test edin**
4. **Rate limit durumunu kontrol edin**

## 🎯 Başarı Kriterleri

Aşağıdaki durumlar gerçekleştiğinde GitHub entegrasyonu başarılı çalışıyor demektir:

- ✅ Bot başlatılırken "GitHub: ✅ Enabled" görünür
- ✅ `/github` komutu bağlantı durumunu gösterir
- ✅ `/repo` komutu repository bilgilerini getirir
- ✅ `/search` komutu arama sonuçları döndürür
- ✅ Log dosyasında GitHub ile ilgili hata mesajları yok

Bu kılavuzu takip ederek GitHub bağlantı sorununuzu çözebilirsiniz. 🚀
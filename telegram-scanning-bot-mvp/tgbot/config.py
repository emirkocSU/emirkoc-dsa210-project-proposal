"""
Configuration module for the Telegram Scanning Bot.
Handles environment variables, database settings, and bot configuration.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Telegram bot."""
    
    # Bot configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")
    
    # Database configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "../shared/database.db")
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATABASE_PATH}"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    TOKEN_EXPIRATION_HOURS: int = int(os.getenv("TOKEN_EXPIRATION_HOURS", "24"))
    
    # Rate limiting settings
    RATE_LIMIT_MESSAGES: int = int(os.getenv("RATE_LIMIT_MESSAGES", "10"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Scanning settings
    MAX_SCAN_TIMEOUT: int = int(os.getenv("MAX_SCAN_TIMEOUT", "30"))  # seconds
    MAX_URL_LENGTH: int = int(os.getenv("MAX_URL_LENGTH", "2048"))
    
    # Car listing specific settings
    SCAN_INTERVAL: int = int(os.getenv("SCAN_INTERVAL", "300"))  # 5 minutes
    MAX_LISTINGS_PER_SCAN: int = int(os.getenv("MAX_LISTINGS_PER_SCAN", "50"))
    
    # YOLOv8 settings
    YOLO_WEIGHTS_PATH: str = os.getenv("YOLO_WEIGHTS_PATH", "models/car_damage_yolov8.pt")
    YOLO_CONFIDENCE_THRESHOLD: float = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.25"))
    YOLO_MAX_IMAGES: int = int(os.getenv("YOLO_MAX_IMAGES", "3"))
    
    # Car listing site settings
    BASE_LISTING_URL: str = os.getenv("BASE_LISTING_URL", "https://www.sahibinden.com/otomobil")
    LISTING_SITE_DOMAIN: str = os.getenv("LISTING_SITE_DOMAIN", "sahibinden.com")
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # API server settings (optional)
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Deep linking settings
    DEEP_LINK_DOMAIN: str = os.getenv("DEEP_LINK_DOMAIN", "t.me")
    CUSTOM_SCHEME: str = os.getenv("CUSTOM_SCHEME", "scanapp")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration values."""
        if not cls.BOT_TOKEN:
            logging.error("BOT_TOKEN is required but not set")
            return False
        
        if not cls.BOT_USERNAME:
            logging.error("BOT_USERNAME is required but not set")
            return False
        
        # Create database directory if it doesn't exist
        db_path = Path(cls.DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        return True
    
    @classmethod
    def setup_logging(cls) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("bot.log", encoding="utf-8")
            ]
        )

# Global configuration instance
config = Config()

# Validation on import
if not config.validate():
    raise ValueError("Invalid configuration. Please check your environment variables.")

# Setup logging
config.setup_logging()
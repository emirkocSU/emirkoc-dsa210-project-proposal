"""
Database module for the Telegram Scanning Bot.
Handles SQLAlchemy models, database operations, and user management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4
import hashlib
import secrets

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from .config import config

# Create async engine and session
engine = create_async_engine(
    config.DATABASE_URL,
    echo=config.LOG_LEVEL.upper() == "DEBUG",
    future=True
)

async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

logger = logging.getLogger(__name__)

class User(Base):
    """User model for app users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    telegram_id = Column(Integer, unique=True, nullable=True, index=True)
    telegram_username = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Subscription fields
    subscription_active = Column(Boolean, default=False)
    subscription_expires_at = Column(DateTime, nullable=True)
    subscription_type = Column(String(50), default="basic")
    
    # Car search filters (JSON string)
    search_filters = Column(Text, nullable=True)
    last_seen_listing_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    link_tokens = relationship("LinkToken", back_populates="user")
    scan_results = relationship("ScanResult", back_populates="user")
    car_alerts = relationship("CarAlert", back_populates="user")

class LinkToken(Base):
    """Link token model for account linking between app and Telegram."""
    __tablename__ = "link_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="link_tokens")

class ScanResult(Base):
    """Scan result model for storing scanning results."""
    __tablename__ = "scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(Text, nullable=False)
    scan_type = Column(String(100), nullable=False, default="car_listing")
    status = Column(String(50), nullable=False, default="pending")  # pending, completed, failed
    result_data = Column(Text, nullable=True)  # JSON string of results
    damage_score = Column(Integer, nullable=True)  # 0-100 damage score
    damage_types = Column(Text, nullable=True)  # JSON array of detected damages
    scan_duration = Column(Integer, nullable=True)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="scan_results")

class CarAlert(Base):
    """Car alert model for storing sent alerts to avoid duplicates."""
    __tablename__ = "car_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(String(255), nullable=False, index=True)
    listing_url = Column(Text, nullable=False)
    listing_title = Column(String(500), nullable=True)
    listing_price = Column(String(100), nullable=True)
    damage_score = Column(Integer, nullable=True)
    damage_summary = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="car_alerts")

class DatabaseManager:
    """Database manager for handling all database operations."""
    
    def __init__(self):
        self.engine = engine
        self.async_session = async_session
    
    async def create_tables(self):
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    async def get_session(self) -> AsyncSession:
        """Get async database session."""
        return self.async_session()
    
    # User operations
    async def create_user(self, email: str, password: str, full_name: str = None) -> Optional[User]:
        """Create a new user with hashed password."""
        try:
            password_hash = self._hash_password(password)
            user = User(
                email=email.lower().strip(),
                password_hash=password_hash,
                full_name=full_name
            )
            
            async with self.async_session() as session:
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"Created new user: {email}")
                return user
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.email == email.lower().strip())
            )
            return result.scalar_one_or_none()
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    async def verify_password(self, email: str, password: str) -> Optional[User]:
        """Verify user password and return user if valid."""
        user = await self.get_user_by_email(email)
        if user and self._verify_password(password, user.password_hash):
            return user
        return None
    
    async def link_telegram_account(self, user_id: int, telegram_id: int, telegram_username: str = None) -> bool:
        """Link Telegram account to user."""
        try:
            async with self.async_session() as session:
                # Check if telegram_id is already linked to another user
                existing_link = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                if existing_link.scalar_one_or_none():
                    logger.warning(f"Telegram ID {telegram_id} already linked to another user")
                    return False
                
                # Update user with Telegram info
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                if not user:
                    logger.error(f"User {user_id} not found")
                    return False
                
                user.telegram_id = telegram_id
                user.telegram_username = telegram_username
                user.updated_at = datetime.utcnow()
                
                await session.commit()
                logger.info(f"Linked Telegram account {telegram_id} to user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error linking Telegram account: {e}")
            return False
    
    # Link token operations
    async def create_link_token(self, user_id: int) -> Optional[str]:
        """Create a new link token for user."""
        try:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=config.TOKEN_EXPIRATION_HOURS)
            
            link_token = LinkToken(
                token=token,
                user_id=user_id,
                expires_at=expires_at
            )
            
            async with self.async_session() as session:
                session.add(link_token)
                await session.commit()
                logger.info(f"Created link token for user {user_id}")
                return token
        except Exception as e:
            logger.error(f"Error creating link token: {e}")
            return None
    
    async def verify_link_token(self, token: str) -> Optional[int]:
        """Verify link token and return user_id if valid."""
        async with self.async_session() as session:
            result = await session.execute(
                select(LinkToken).where(
                    and_(
                        LinkToken.token == token,
                        LinkToken.is_used == False,
                        LinkToken.expires_at > datetime.utcnow()
                    )
                )
            )
            link_token = result.scalar_one_or_none()
            
            if link_token:
                # Mark token as used
                link_token.is_used = True
                link_token.used_at = datetime.utcnow()
                await session.commit()
                logger.info(f"Verified and used link token for user {link_token.user_id}")
                return link_token.user_id
            
            return None
    
    # Scan result operations
    async def create_scan_result(self, user_id: int, url: str, scan_type: str = "url_scan") -> Optional[ScanResult]:
        """Create a new scan result entry."""
        try:
            scan_result = ScanResult(
                user_id=user_id,
                url=url,
                scan_type=scan_type,
                status="pending"
            )
            
            async with self.async_session() as session:
                session.add(scan_result)
                await session.commit()
                await session.refresh(scan_result)
                logger.info(f"Created scan result {scan_result.id} for user {user_id}")
                return scan_result
        except Exception as e:
            logger.error(f"Error creating scan result: {e}")
            return None
    
    async def update_scan_result(self, scan_id: int, status: str, result_data: str = None, 
                               damage_score: int = None, threats_found: str = None, 
                               scan_duration: int = None) -> bool:
        """Update scan result with completion data."""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(ScanResult).where(ScanResult.id == scan_id)
                )
                scan_result = result.scalar_one_or_none()
                
                if not scan_result:
                    logger.error(f"Scan result {scan_id} not found")
                    return False
                
                scan_result.status = status
                if result_data:
                    scan_result.result_data = result_data
                if damage_score is not None:
                    scan_result.damage_score = damage_score
                if threats_found:
                    scan_result.threats_found = threats_found
                if scan_duration is not None:
                    scan_result.scan_duration = scan_duration
                
                if status == "completed":
                    scan_result.completed_at = datetime.utcnow()
                
                await session.commit()
                logger.info(f"Updated scan result {scan_id} with status {status}")
                return True
        except Exception as e:
            logger.error(f"Error updating scan result: {e}")
            return False
    
    async def get_user_scan_results(self, user_id: int, limit: int = 10) -> List[ScanResult]:
        """Get recent scan results for user."""
        async with self.async_session() as session:
            result = await session.execute(
                select(ScanResult)
                .where(ScanResult.user_id == user_id)
                .order_by(ScanResult.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    # Car listing specific methods
    async def update_user_filters(self, user_id: int, filters_dict: Dict[str, Any]) -> bool:
        """Update user's car search filters."""
        try:
            import json
            async with self.async_session() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"User {user_id} not found")
                    return False
                
                user.search_filters = json.dumps(filters_dict)
                user.updated_at = datetime.utcnow()
                
                await session.commit()
                logger.info(f"Updated filters for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error updating user filters: {e}")
            return False
    
    async def get_user_filters(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's car search filters."""
        try:
            import json
            user = await self.get_user_by_id(user_id)
            if user and user.search_filters:
                return json.loads(user.search_filters)
            return None
        except Exception as e:
            logger.error(f"Error getting user filters: {e}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    
    async def update_subscription_status(self, user_id: int, active: bool, expires_at: datetime = None) -> bool:
        """Update user's subscription status."""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"User {user_id} not found")
                    return False
                
                user.subscription_active = active
                if expires_at:
                    user.subscription_expires_at = expires_at
                user.updated_at = datetime.utcnow()
                
                await session.commit()
                logger.info(f"Updated subscription for user {user_id}: active={active}")
                return True
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            return False
    
    async def get_active_subscribers(self) -> List[User]:
        """Get all users with active subscriptions and filters set."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(
                    and_(
                        User.subscription_active == True,
                        User.search_filters.isnot(None),
                        User.telegram_id.isnot(None)
                    )
                )
            )
            return result.scalars().all()
    
    async def record_car_alert(self, user_id: int, listing_id: str, listing_url: str, 
                              listing_title: Optional[str] = None, listing_price: Optional[str] = None,
                              damage_score: Optional[int] = None, damage_summary: Optional[str] = None) -> bool:
        """Record that a car alert was sent to avoid duplicates."""
        try:
            car_alert = CarAlert(
                user_id=user_id,
                listing_id=listing_id,
                listing_url=listing_url,
                listing_title=listing_title,
                listing_price=listing_price,
                damage_score=damage_score,
                damage_summary=damage_summary
            )
            
            async with self.async_session() as session:
                session.add(car_alert)
                await session.commit()
                logger.info(f"Recorded car alert for user {user_id}, listing {listing_id}")
                return True
        except Exception as e:
            logger.error(f"Error recording car alert: {e}")
            return False
    
    async def was_alert_sent(self, user_id: int, listing_id: str) -> bool:
        """Check if alert was already sent for this listing."""
        async with self.async_session() as session:
            result = await session.execute(
                select(CarAlert).where(
                    and_(
                        CarAlert.user_id == user_id,
                        CarAlert.listing_id == listing_id
                    )
                )
            )
            return result.scalar_one_or_none() is not None
    
    async def update_last_seen_listing(self, user_id: int, listing_id: str) -> bool:
        """Update the last seen listing ID for a user."""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"User {user_id} not found")
                    return False
                
                user.last_seen_listing_id = listing_id
                user.updated_at = datetime.utcnow()
                
                await session.commit()
                logger.info(f"Updated last seen listing for user {user_id}: {listing_id}")
                return True
        except Exception as e:
            logger.error(f"Error updating last seen listing: {e}")
            return False
    
    # Utility methods
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            salt, password_hash = stored_hash.split(":")
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except ValueError:
            return False
    
    async def cleanup_expired_tokens(self):
        """Clean up expired link tokens."""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(LinkToken).where(LinkToken.expires_at < datetime.utcnow())
                )
                expired_tokens = result.scalars().all()
                
                for token in expired_tokens:
                    await session.delete(token)
                
                await session.commit()
                logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")

# Global database manager instance
db_manager = DatabaseManager()

async def init_database():
    """Initialize database tables."""
    await db_manager.create_tables()
    logger.info("Database initialized successfully")
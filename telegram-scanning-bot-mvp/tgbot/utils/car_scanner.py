"""
Car Listing Scanner Module.
Handles scraping car listings from sahibinden.com and analyzing them for damage.
"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs
import json
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from config import config
from database import db_manager
from utils.yolo import damage_detector

logger = logging.getLogger(__name__)

class CarListingScanner:
    """Scanner for car listings with damage detection."""
    
    def __init__(self):
        self.client = None
        self.base_url = config.BASE_LISTING_URL
        self.domain = config.LISTING_SITE_DOMAIN
        
    async def initialize(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        logger.info("Car listing scanner initialized")
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            logger.info("Car listing scanner closed")
    
    async def check_new_listings(self):
        """Check for new listings for all active subscribers."""
        if not self.client:
            await self.initialize()
        
        try:
            # Get all active subscribers
            subscribers = await db_manager.get_active_subscribers()
            logger.info(f"Checking listings for {len(subscribers)} active subscribers")
            
            for user in subscribers:
                try:
                    await self._check_user_listings(user)
                    # Small delay between users to avoid overwhelming the server
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error checking listings for user {user.id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in check_new_listings: {e}")
    
    async def _check_user_listings(self, user):
        """Check new listings for a specific user."""
        try:
            # Get user's filters
            filters = await db_manager.get_user_filters(user.id)
            if not filters:
                logger.warning(f"No filters found for user {user.id}")
                return
            
            # Build search URL
            search_url = self._build_search_url(filters)
            logger.debug(f"Searching for user {user.id}: {search_url}")
            
            # Fetch listings
            listings = await self._fetch_listings(search_url)
            if not listings:
                logger.debug(f"No listings found for user {user.id}")
                return
            
            # Find new listings
            new_listings = await self._find_new_listings(user, listings)
            
            if new_listings:
                logger.info(f"Found {len(new_listings)} new listings for user {user.id}")
                
                # Process each new listing
                for listing in new_listings:
                    try:
                        await self._process_new_listing(user, listing)
                        # Small delay between listings
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.error(f"Error processing listing {listing.get('id', 'unknown')}: {e}")
                        continue
                
                # Update last seen listing
                if new_listings:
                    latest_listing_id = new_listings[0].get('id')
                    if latest_listing_id:
                        await db_manager.update_last_seen_listing(user.id, latest_listing_id)
            
        except Exception as e:
            logger.error(f"Error checking user listings: {e}")
    
    def _build_search_url(self, filters: Dict[str, Any]) -> str:
        """Build search URL from user filters."""
        params = []
        
        # Add sorting to get newest first
        params.append("sorting=newest")
        
        # Brand filter
        if filters.get('make'):
            # This would need to be mapped to sahibinden's brand codes
            params.append(f"a7={filters['make']}")
        
        # Model filter
        if filters.get('model'):
            params.append(f"a8={filters['model']}")
        
        # Year range
        if filters.get('year_min'):
            params.append(f"a5_min={filters['year_min']}")
        if filters.get('year_max'):
            params.append(f"a5_max={filters['year_max']}")
        
        # Price range
        if filters.get('price_min'):
            params.append(f"price_min={filters['price_min']}")
        if filters.get('price_max'):
            params.append(f"price_max={filters['price_max']}")
        
        # Mileage
        if filters.get('mileage_max'):
            params.append(f"a6_max={filters['mileage_max']}")
        
        # Fuel type
        if filters.get('fuel_type'):
            params.append(f"a9={filters['fuel_type']}")
        
        # Transmission
        if filters.get('transmission'):
            params.append(f"a10={filters['transmission']}")
        
        # City
        if filters.get('city'):
            params.append(f"a24={filters['city']}")
        
        # Build final URL
        query_string = "&".join(params)
        return f"{self.base_url}?{query_string}"
    
    async def _fetch_listings(self, url: str) -> List[Dict[str, Any]]:
        """Fetch listings from search URL."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = []
            
            # Find listing containers (this selector would need to be adjusted for actual sahibinden structure)
            listing_elements = soup.find_all('tr', class_='searchResultsItem')
            
            for element in listing_elements[:config.MAX_LISTINGS_PER_SCAN]:
                try:
                    listing = self._parse_listing_element(element)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error parsing listing element: {e}")
                    continue
            
            return listings
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching listings: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching listings: {e}")
            return []
    
    def _parse_listing_element(self, element) -> Optional[Dict[str, Any]]:
        """Parse a single listing element from the search results."""
        try:
            # Extract listing ID from URL or data attributes
            link_elem = element.find('a', class_='classifiedTitle')
            if not link_elem:
                return None
            
            listing_url = link_elem.get('href')
            if not listing_url:
                return None
            
            # Make absolute URL
            if listing_url.startswith('/'):
                listing_url = f"https://{self.domain}{listing_url}"
            
            # Extract listing ID from URL
            listing_id = self._extract_listing_id(listing_url)
            if not listing_id:
                return None
            
            # Extract title
            title = link_elem.get_text(strip=True)
            
            # Extract price
            price_elem = element.find('td', class_='searchResultsPriceValue')
            price = price_elem.get_text(strip=True) if price_elem else "N/A"
            
            # Extract location
            location_elem = element.find('td', class_='searchResultsLocationValue')
            location = location_elem.get_text(strip=True) if location_elem else "N/A"
            
            # Extract date
            date_elem = element.find('td', class_='searchResultsDateValue')
            date_str = date_elem.get_text(strip=True) if date_elem else ""
            
            # Extract basic info (year, mileage, etc.)
            info_elem = element.find('td', class_='searchResultsAttributeValue')
            attributes = info_elem.get_text(strip=True) if info_elem else ""
            
            return {
                'id': listing_id,
                'url': listing_url,
                'title': title,
                'price': price,
                'location': location,
                'date': date_str,
                'attributes': attributes
            }
            
        except Exception as e:
            logger.warning(f"Error parsing listing element: {e}")
            return None
    
    def _extract_listing_id(self, url: str) -> Optional[str]:
        """Extract listing ID from URL."""
        try:
            # Common patterns for sahibinden URLs
            patterns = [
                r'/ilan/(\d+)',
                r'/detay/(\d+)',
                r'id=(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            # Fallback: use the URL itself as ID
            return str(hash(url))
            
        except Exception as e:
            logger.warning(f"Error extracting listing ID from {url}: {e}")
            return None
    
    async def _find_new_listings(self, user, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find new listings that haven't been sent to the user."""
        if not listings:
            return []
        
        new_listings = []
        last_seen_id = user.last_seen_listing_id
        
        for listing in listings:
            listing_id = listing.get('id')
            if not listing_id:
                continue
            
            # Check if we've already sent this listing
            if await db_manager.was_alert_sent(user.id, listing_id):
                continue
            
            # If we have a last seen ID, stop when we reach it
            if last_seen_id and listing_id == last_seen_id:
                break
            
            new_listings.append(listing)
        
        return new_listings
    
    async def _process_new_listing(self, user, listing: Dict[str, Any]):
        """Process a new listing: fetch details, analyze damage, and send alert."""
        try:
            listing_id = listing['id']
            listing_url = listing['url']
            
            # Fetch detailed listing info
            details = await self._fetch_listing_details(listing_url)
            if not details:
                logger.warning(f"Could not fetch details for listing {listing_id}")
                return
            
            # Analyze for damage
            damage_analysis = await self._analyze_listing_damage(details)
            
            # Send alert to user
            await self._send_listing_alert(user, listing, details, damage_analysis)
            
            # Record that we sent this alert
            await db_manager.record_car_alert(
                user_id=user.id,
                listing_id=listing_id,
                listing_url=listing_url,
                listing_title=listing.get('title'),
                listing_price=listing.get('price'),
                damage_score=damage_analysis.get('final_damage_score'),
                damage_summary=json.dumps(damage_analysis)
            )
            
        except Exception as e:
            logger.error(f"Error processing new listing: {e}")
    
    async def _fetch_listing_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed information about a listing."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract description
            desc_elem = soup.find('div', class_='classifiedDescription')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract images
            image_urls = []
            img_elements = soup.find_all('img', class_='stdImg')
            for img in img_elements:
                img_url = img.get('src') or img.get('data-src')
                if img_url:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = f"https://{self.domain}{img_url}"
                    image_urls.append(img_url)
            
            # Extract attributes
            attributes = {}
            attr_elements = soup.find_all('li', class_='classifiedInfoList')
            for attr in attr_elements:
                label_elem = attr.find('span', class_='classifiedInfoLabel')
                value_elem = attr.find('span', class_='classifiedInfoValue')
                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    attributes[label] = value
            
            return {
                'description': description,
                'images': image_urls,
                'attributes': attributes
            }
            
        except Exception as e:
            logger.error(f"Error fetching listing details from {url}: {e}")
            return None
    
    async def _analyze_listing_damage(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze listing for damage using YOLO and text analysis."""
        try:
            # Analyze images with YOLO
            image_urls = details.get('images', [])
            yolo_results = await damage_detector.detect_damage(image_urls)
            
            # Analyze description text
            description = details.get('description', '')
            text_results = await damage_detector.analyze_text_for_damage(description)
            
            # Combine results
            combined_analysis = damage_detector.combine_damage_analysis(yolo_results, text_results)
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing listing damage: {e}")
            return {
                'final_damage_score': 0,
                'final_severity': 'unknown',
                'analysis_complete': False,
                'error': str(e)
            }
    
    async def _send_listing_alert(self, user, listing: Dict[str, Any], 
                                details: Dict[str, Any], damage_analysis: Dict[str, Any]):
        """Send listing alert to user via Telegram."""
        try:
            from main import bot_instance  # Import here to avoid circular imports
            
            if not bot_instance or not user.telegram_id:
                logger.error("Bot instance or user telegram_id not available")
                return
            
            # Format the alert message
            message = self._format_alert_message(listing, details, damage_analysis)
            
            # Create inline keyboard
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔗 View Listing", url=listing['url'])],
                [InlineKeyboardButton(text="ℹ️ More Details", callback_data=f"details_{listing['id']}")]
            ])
            
            # Send message
            await bot_instance.send_message(
                chat_id=user.telegram_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"Sent listing alert to user {user.id} for listing {listing['id']}")
            
        except Exception as e:
            logger.error(f"Error sending listing alert: {e}")
    
    def _format_alert_message(self, listing: Dict[str, Any], 
                            details: Dict[str, Any], damage_analysis: Dict[str, Any]) -> str:
        """Format the alert message for Telegram."""
        title = listing.get('title', 'Unknown Car')
        price = listing.get('price', 'N/A')
        location = listing.get('location', 'N/A')
        
        # Damage info
        damage_score = damage_analysis.get('final_damage_score', 0)
        severity = damage_analysis.get('final_severity', 'unknown')
        
        # Severity emoji
        severity_emoji = {
            'minimal': '✅',
            'low': '🟡',
            'moderate': '🟠',
            'high': '🔴',
            'unknown': '❓'
        }.get(severity, '❓')
        
        # Damage types
        damage_types = damage_analysis.get('damage_types', [])
        damage_keywords = damage_analysis.get('damage_keywords', [])
        
        message = f"🚗 <b>New Car Alert!</b>\n\n"
        message += f"<b>{title}</b>\n"
        message += f"💰 Price: <b>{price}</b>\n"
        message += f"📍 Location: {location}\n\n"
        
        message += f"{severity_emoji} <b>Damage Assessment:</b>\n"
        message += f"Score: {damage_score}/100 ({severity.title()})\n"
        
        if damage_types:
            message += f"Visual damage: {', '.join(damage_types)}\n"
        
        if damage_keywords:
            message += f"Keywords found: {', '.join(damage_keywords[:3])}\n"
        
        if not damage_analysis.get('analysis_complete', False):
            message += "⚠️ Analysis incomplete\n"
        
        message += f"\n🕐 Posted: {listing.get('date', 'Recently')}"
        
        return message
    
    async def scan_specific_listing(self, url: str) -> Dict[str, Any]:
        """Scan a specific listing URL for damage analysis."""
        try:
            if not self.client:
                await self.initialize()
            
            # Validate URL
            if self.domain not in url:
                return {"error": "Invalid URL domain"}
            
            # Fetch listing details
            details = await self._fetch_listing_details(url)
            if not details:
                return {"error": "Could not fetch listing details"}
            
            # Analyze for damage
            damage_analysis = await self._analyze_listing_damage(details)
            
            # Extract basic info
            listing_id = self._extract_listing_id(url)
            
            return {
                "success": True,
                "listing_id": listing_id,
                "url": url,
                "details": details,
                "damage_analysis": damage_analysis
            }
            
        except Exception as e:
            logger.error(f"Error scanning specific listing: {e}")
            return {"error": str(e)}

# Global scanner instance
car_scanner = CarListingScanner()

async def init_car_scanner():
    """Initialize the car scanner."""
    await car_scanner.initialize()
    logger.info("Car listing scanner initialized")

async def cleanup_car_scanner():
    """Cleanup the car scanner."""
    await car_scanner.close()
    logger.info("Car listing scanner cleaned up")
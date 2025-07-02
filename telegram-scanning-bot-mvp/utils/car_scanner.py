"""
Car Scanner Module for Sahibinden.com

This module handles scanning car listings from sahibinden.com,
extracting listing details, and analyzing them for damage using YOLO.
"""

import asyncio
import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
# Mock implementations for dependencies
class MockSession:
    async def get(self, url, timeout=None):
        class MockResponse:
            status = 200
            async def text(self):
                return "<html><body>Mock content</body></html>"
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        return MockResponse()
    
    async def close(self):
        pass

class MockBeautifulSoup:
    def __init__(self, content, parser):
        self.content = content
    
    def select(self, selector):
        return []
    
    def select_one(self, selector):
        return None

# Use mock implementations
class MockAiohttp:
    @staticmethod
    def ClientSession(headers=None):
        return MockSession()

aiohttp = MockAiohttp()
BeautifulSoup = MockBeautifulSoup

from .yolo import analyze_car_images

logger = logging.getLogger(__name__)

class CarScanner:
    """Car listing scanner for sahibinden.com"""
    
    def __init__(self, base_url: str = "https://www.sahibinden.com/otomobil", 
                 request_delay: float = 1.0, max_listings: int = 50):
        self.base_url = base_url
        self.request_delay = request_delay
        self.max_listings = max_listings
        self.session = None
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def build_search_url(self, filters: Dict[str, Any]) -> str:
        """
        Build search URL from user filters
        
        Args:
            filters: Dictionary of search filters
            
        Returns:
            Complete search URL
        """
        url_parts = [self.base_url]
        
        # Add car make
        if filters.get('make'):
            url_parts.append(filters['make'].lower())
        
        # Build query parameters
        params = []
        
        # Price range
        if filters.get('price_min'):
            params.append(f"price_min={filters['price_min']}")
        if filters.get('price_max'):
            params.append(f"price_max={filters['price_max']}")
        
        # Year range
        if filters.get('year_min'):
            params.append(f"date_min={filters['year_min']}")
        if filters.get('year_max'):
            params.append(f"date_max={filters['year_max']}")
        
        # Location
        if filters.get('city'):
            params.append(f"address_city={filters['city']}")
        
        # Fuel type
        if filters.get('fuel_type'):
            fuel_map = {
                'benzin': 'gasoline',
                'dizel': 'diesel',
                'lpg': 'lpg',
                'hybrid': 'hybrid',
                'elektrik': 'electric'
            }
            fuel_code = fuel_map.get(filters['fuel_type'].lower(), filters['fuel_type'])
            params.append(f"fuel={fuel_code}")
        
        # Transmission
        if filters.get('transmission'):
            trans_map = {
                'manuel': 'manual',
                'otomatik': 'automatic',
                'yarı_otomatik': 'semi_automatic'
            }
            trans_code = trans_map.get(filters['transmission'].lower(), filters['transmission'])
            params.append(f"gear={trans_code}")
        
        # Combine URL
        search_url = "/".join(url_parts)
        if params:
            search_url += "?" + "&".join(params)
        
        logger.info(f"Built search URL: {search_url}")
        return search_url
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a web page with error handling
        
        Args:
            url: URL to fetch
            
        Returns:
            Page content or None if failed
        """
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.debug(f"Successfully fetched: {url}")
                    return content
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_listing_urls(self, html_content: str) -> List[str]:
        """
        Extract individual listing URLs from search results
        
        Args:
            html_content: HTML content of search results page
            
        Returns:
            List of listing URLs
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            listing_urls = []
            
            # Find listing links (sahibinden.com specific selectors)
            # This is a mock implementation - real selectors would need to be determined
            # by inspecting the actual sahibinden.com HTML structure
            
            # Common patterns for listing links
            link_selectors = [
                'a[href*="/ilan/"]',
                '.classifiedTitle a',
                '.searchResultsItem a',
                '.result-item a'
            ]
            
            for selector in link_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    if href and '/ilan/' in href:
                        if href.startswith('/'):
                            full_url = urljoin('https://www.sahibinden.com', href)
                        else:
                            full_url = href
                        
                        if full_url not in listing_urls:
                            listing_urls.append(full_url)
            
            # Limit results
            listing_urls = listing_urls[:self.max_listings]
            logger.info(f"Extracted {len(listing_urls)} listing URLs")
            return listing_urls
            
        except Exception as e:
            logger.error(f"Error extracting listing URLs: {e}")
            return []
    
    def extract_listing_details(self, html_content: str, listing_url: str) -> Dict[str, Any]:
        """
        Extract details from a car listing page
        
        Args:
            html_content: HTML content of listing page
            listing_url: URL of the listing
            
        Returns:
            Dictionary with listing details
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            details = {
                'url': listing_url,
                'listing_id': self.extract_listing_id(listing_url),
                'title': '',
                'price': '',
                'location': '',
                'year': '',
                'mileage': '',
                'fuel_type': '',
                'transmission': '',
                'description': '',
                'images': [],
                'contact_info': {},
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extract title
            title_selectors = ['h1', '.classifiedDetailTitle', '.classified-detail-title', 'title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    details['title'] = title_elem.get_text(strip=True)
                    break
            
            # Extract price
            price_selectors = ['.classifiedPrice', '.price', '.fiyat', '[class*="price"]']
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    details['price'] = price_elem.get_text(strip=True)
                    break
            
            # Extract location
            location_selectors = ['.classifiedLocation', '.location', '.konum']
            for selector in location_selectors:
                location_elem = soup.select_one(selector)
                if location_elem:
                    details['location'] = location_elem.get_text(strip=True)
                    break
            
            # Extract description
            desc_selectors = ['.classifiedDescription', '.description', '.aciklama', '#classifiedDescription']
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    details['description'] = desc_elem.get_text(strip=True)
                    break
            
            # Extract images
            img_selectors = ['img[src*="img.sahibinden.com"]', '.classifiedDetailMainPhoto img', '.gallery img']
            for selector in img_selectors:
                images = soup.select(selector)
                for img in images:
                    src = img.get('src') or img.get('data-src')
                    if src and src not in details['images']:
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://www.sahibinden.com' + src
                        details['images'].append(src)
            
            # Limit images
            details['images'] = details['images'][:10]
            
            logger.info(f"Extracted details for listing: {details['title'][:50]}...")
            return details
            
        except Exception as e:
            logger.error(f"Error extracting listing details: {e}")
            return {
                'url': listing_url,
                'listing_id': self.extract_listing_id(listing_url),
                'error': str(e),
                'extracted_at': datetime.now().isoformat()
            }
    
    def extract_listing_id(self, url: str) -> str:
        """Extract listing ID from URL"""
        try:
            # Common patterns for listing IDs in URLs
            patterns = [
                r'/ilan/([0-9]+)',
                r'id=([0-9]+)',
                r'/([0-9]+)$',
                r'/([0-9]+)/'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            # Fallback: use hash of URL
            return str(hash(url))[-8:]
            
        except Exception:
            return str(hash(url))[-8:]
    
    async def scan_for_new_listings(self, user_filters: Dict[str, Any], 
                                   last_seen_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scan for new car listings based on user filters
        
        Args:
            user_filters: User's search filters
            last_seen_id: ID of last seen listing to detect new ones
            
        Returns:
            List of new listings with damage analysis
        """
        try:
            # Build search URL
            search_url = self.build_search_url(user_filters)
            
            # Fetch search results
            logger.info(f"Scanning for new listings: {search_url}")
            search_html = await self.fetch_page(search_url)
            
            if not search_html:
                logger.error("Failed to fetch search results")
                return []
            
            # Extract listing URLs
            listing_urls = self.extract_listing_urls(search_html)
            
            if not listing_urls:
                logger.warning("No listing URLs found")
                return []
            
            new_listings = []
            found_last_seen = False
            
            for url in listing_urls:
                listing_id = self.extract_listing_id(url)
                
                # Stop if we've reached the last seen listing
                if last_seen_id and listing_id == last_seen_id:
                    found_last_seen = True
                    break
                
                # Fetch listing details
                await asyncio.sleep(self.request_delay)  # Rate limiting
                
                listing_html = await self.fetch_page(url)
                if not listing_html:
                    continue
                
                # Extract listing details
                listing_details = self.extract_listing_details(listing_html, url)
                
                # Analyze images for damage
                if listing_details.get('images'):
                    logger.info(f"Analyzing damage for listing {listing_id}")
                    try:
                        damage_analysis = await analyze_car_images(
                            listing_details['images'], 
                            listing_details.get('description', '')
                        )
                        listing_details['damage_analysis'] = damage_analysis
                        listing_details['damage_score'] = damage_analysis.get('combined_damage_score', 0)
                        listing_details['damage_summary'] = damage_analysis.get('analysis_summary', '')
                    except Exception as e:
                        logger.error(f"Error analyzing damage for {listing_id}: {e}")
                        listing_details['damage_analysis'] = None
                        listing_details['damage_score'] = 0
                        listing_details['damage_summary'] = "Hasar analizi yapılamadı"
                
                new_listings.append(listing_details)
                
                # Limit number of new listings processed
                if len(new_listings) >= 10:
                    break
            
            logger.info(f"Found {len(new_listings)} new listings")
            return new_listings
            
        except Exception as e:
            logger.error(f"Error scanning for new listings: {e}")
            return []
    
    async def analyze_single_listing(self, listing_url: str) -> Dict[str, Any]:
        """
        Analyze a single car listing
        
        Args:
            listing_url: URL of the listing to analyze
            
        Returns:
            Listing details with damage analysis
        """
        try:
            logger.info(f"Analyzing single listing: {listing_url}")
            
            # Fetch listing page
            listing_html = await self.fetch_page(listing_url)
            if not listing_html:
                return {'error': 'Failed to fetch listing page', 'url': listing_url}
            
            # Extract details
            listing_details = self.extract_listing_details(listing_html, listing_url)
            
            # Analyze for damage
            if listing_details.get('images'):
                try:
                    damage_analysis = await analyze_car_images(
                        listing_details['images'], 
                        listing_details.get('description', '')
                    )
                    listing_details['damage_analysis'] = damage_analysis
                    listing_details['damage_score'] = damage_analysis.get('combined_damage_score', 0)
                    listing_details['damage_summary'] = damage_analysis.get('analysis_summary', '')
                except Exception as e:
                    logger.error(f"Error analyzing damage: {e}")
                    listing_details['damage_analysis'] = None
                    listing_details['damage_score'] = 0
                    listing_details['damage_summary'] = "Hasar analizi yapılamadı"
            else:
                listing_details['damage_analysis'] = None
                listing_details['damage_score'] = 0
                listing_details['damage_summary'] = "Analiz için resim bulunamadı"
            
            logger.info(f"Analysis completed for listing: {listing_details.get('title', 'Unknown')}")
            return listing_details
            
        except Exception as e:
            logger.error(f"Error analyzing listing {listing_url}: {e}")
            return {
                'error': str(e),
                'url': listing_url,
                'extracted_at': datetime.now().isoformat()
            }

# Utility functions
async def scan_all_users(db_manager, bot_instance=None) -> None:
    """
    Scan for new listings for all active subscribers
    
    Args:
        db_manager: Database manager instance
        bot_instance: Telegram bot instance for sending alerts
    """
    try:
        logger.info("Starting scan for all active subscribers")
        
        # Get all active subscribers
        active_users = await db_manager.get_active_subscribers()
        logger.info(f"Found {len(active_users)} active subscribers")
        
        if not active_users:
            return
        
        async with CarScanner() as scanner:
            for user in active_users:
                try:
                    # Get user filters
                    filters = await db_manager.get_user_filters(user.id)
                    if not filters:
                        logger.warning(f"No filters found for user {user.id}")
                        continue
                    
                    # Scan for new listings
                    new_listings = await scanner.scan_for_new_listings(
                        filters, 
                        user.last_seen_listing_id
                    )
                    
                    if new_listings:
                        logger.info(f"Found {len(new_listings)} new listings for user {user.id}")
                        
                        # Update last seen listing
                        if new_listings:
                            latest_listing = new_listings[0]
                            await db_manager.update_last_seen_listing(
                                user.id, 
                                latest_listing['listing_id']
                            )
                        
                        # Send alerts if bot instance is provided
                        if bot_instance:
                            await send_listing_alerts(bot_instance, user, new_listings, db_manager)
                    
                    # Small delay between users
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error scanning for user {user.id}: {e}")
                    continue
        
        logger.info("Completed scan for all active subscribers")
        
    except Exception as e:
        logger.error(f"Error in scan_all_users: {e}")

async def send_listing_alerts(bot_instance, user, listings: List[Dict[str, Any]], db_manager) -> None:
    """
    Send listing alerts to a user
    
    Args:
        bot_instance: Telegram bot instance
        user: User object
        listings: List of new listings
        db_manager: Database manager instance
    """
    try:
        for listing in listings:
            # Check if alert was already sent
            was_sent = await db_manager.was_alert_sent(user.id, listing['listing_id'])
            if was_sent:
                continue
            
            # Format alert message
            message = format_listing_alert(listing)
            
            # Send message
            try:
                await bot_instance.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
                
                # Record that alert was sent
                await db_manager.record_car_alert(
                    user.id,
                    listing['listing_id'],
                    listing['url'],
                    listing.get('title'),
                    listing.get('price'),
                    listing.get('damage_score'),
                    listing.get('damage_summary')
                )
                
                logger.info(f"Sent alert to user {user.id} for listing {listing['listing_id']}")
                
            except Exception as e:
                logger.error(f"Error sending alert to user {user.id}: {e}")
            
            # Delay between messages
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error sending listing alerts: {e}")

def format_listing_alert(listing: Dict[str, Any]) -> str:
    """
    Format a listing alert message
    
    Args:
        listing: Listing details dictionary
        
    Returns:
        Formatted message string
    """
    try:
        title = listing.get('title', 'Başlık bulunamadı')
        price = listing.get('price', 'Fiyat belirtilmemiş')
        location = listing.get('location', 'Konum belirtilmemiş')
        damage_score = listing.get('damage_score', 0)
        damage_summary = listing.get('damage_summary', 'Hasar analizi yapılamadı')
        url = listing.get('url', '')
        
        # Damage emoji based on score
        if damage_score >= 70:
            damage_emoji = "🔴"
        elif damage_score >= 40:
            damage_emoji = "🟡"
        elif damage_score >= 20:
            damage_emoji = "🟢"
        else:
            damage_emoji = "✅"
        
        message = f"""
🚗 <b>Yeni Araç İlanı</b>

<b>{title}</b>

💰 <b>Fiyat:</b> {price}
📍 <b>Konum:</b> {location}

{damage_emoji} <b>Hasar Analizi:</b>
{damage_summary}

<a href="{url}">İlanı Görüntüle</a>
""".strip()
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting listing alert: {e}")
        return f"Yeni araç ilanı mevcut: {listing.get('url', 'URL bulunamadı')}"

# Export main classes and functions
__all__ = [
    'CarScanner',
    'scan_all_users',
    'send_listing_alerts',
    'format_listing_alert'
]
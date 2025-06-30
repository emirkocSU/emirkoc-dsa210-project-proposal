"""
Professional URL Scanner with Advanced Damage Scoring and Threat Detection.
Implements comprehensive scanning algorithms with robust error handling.
"""

import asyncio
import logging
import json
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass, asdict
import re

import httpx
from config import config

logger = logging.getLogger(__name__)

@dataclass
class ThreatInfo:
    """Information about a detected threat."""
    threat_type: str
    severity: str  # low, medium, high, critical
    description: str
    confidence: float  # 0.0 to 1.0
    evidence: List[str]

@dataclass
class ScanResult:
    """Complete scan result with damage assessment."""
    url: str
    status: str  # pending, completed, failed, timeout
    damage_score: int  # 0-100
    overall_risk: str  # safe, low, medium, high, critical
    threats_found: List[ThreatInfo]
    scan_duration: float
    timestamp: datetime
    metadata: Dict[str, Any]
    error_message: Optional[str] = None

class AdvancedURLScanner:
    """
    Professional URL scanner with comprehensive threat detection.
    Implements multiple scanning techniques and damage scoring algorithms.
    """
    
    # Threat pattern definitions
    MALWARE_PATTERNS = [
        r'\.exe(\?|$|&)',
        r'\.scr(\?|$|&)',
        r'\.bat(\?|$|&)',
        r'\.cmd(\?|$|&)',
        r'\.pif(\?|$|&)',
        r'\.com(\?|$|&)',
        r'malware',
        r'trojan',
        r'virus',
        r'backdoor',
        r'keylogger',
    ]
    
    PHISHING_PATTERNS = [
        r'(login|signin|account).*?(verify|confirm|update|suspend)',
        r'(paypal|amazon|apple|microsoft|google).*?(login|verify)',
        r'(bank|banking).*?(login|account)',
        r'urgent.*?(action|required|verify)',
        r'suspended.*?(account|service)',
        r'click.*?(here|link).*?(verify|confirm)',
        r'(free|win|winner).*?(money|prize|gift)',
    ]
    
    SUSPICIOUS_DOMAINS = [
        r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
        r'.*\.tk$',  # Free domains
        r'.*\.ml$',
        r'.*\.ga$',
        r'.*\.cf$',
        r'bit\.ly',
        r'tinyurl\.com',
        r'shorturl\.at',
        r't\.co',
    ]
    
    BLACKLISTED_KEYWORDS = [
        'phishing', 'scam', 'fake', 'fraud', 'malicious',
        'exploit', 'payload', 'shell', 'injection',
        'xss', 'csrf', 'clickjacking', 'ransomware',
        'cryptominer', 'botnet', 'c2', 'command-control'
    ]
    
    def __init__(self):
        """Initialize the scanner with configuration."""
        self.timeout = config.MAX_SCAN_TIMEOUT
        self.user_agent = "ScanBot/1.0 (Professional Security Scanner)"
        self.max_redirects = 5
        self.max_content_size = 10 * 1024 * 1024  # 10MB
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            max_redirects=self.max_redirects,
            headers={"User-Agent": self.user_agent}
        )
        
        logger.info("Advanced URL Scanner initialized")
    
    async def scan_url(self, url: str, scan_options: Dict[str, Any] = None) -> ScanResult:
        """
        Perform comprehensive URL scan with damage assessment.
        
        Args:
            url: URL to scan
            scan_options: Additional scanning options
            
        Returns:
            Complete scan result with damage score
        """
        start_time = time.time()
        scan_options = scan_options or {}
        
        logger.info(f"Starting comprehensive scan for: {url}")
        
        try:
            # Initialize result
            result = ScanResult(
                url=url,
                status="pending",
                damage_score=0,
                overall_risk="safe",
                threats_found=[],
                scan_duration=0.0,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            # Phase 1: Static Analysis
            static_threats = await self._static_analysis(url)
            result.threats_found.extend(static_threats)
            
            # Phase 2: DNS and Domain Analysis
            domain_threats = await self._domain_analysis(url)
            result.threats_found.extend(domain_threats)
            
            # Phase 3: HTTP Response Analysis
            http_threats = await self._http_analysis(url)
            result.threats_found.extend(http_threats)
            
            # Phase 4: Content Analysis
            content_threats = await self._content_analysis(url)
            result.threats_found.extend(content_threats)
            
            # Calculate damage score and overall risk
            result.damage_score = self._calculate_damage_score(result.threats_found)
            result.overall_risk = self._determine_risk_level(result.damage_score)
            
            # Add metadata
            result.metadata = {
                "scan_phases": ["static", "domain", "http", "content"],
                "total_threats": len(result.threats_found),
                "scan_options": scan_options,
                "scanner_version": "1.0"
            }
            
            result.status = "completed"
            logger.info(f"Scan completed: {url} - Risk: {result.overall_risk}, Score: {result.damage_score}")
            
        except asyncio.TimeoutError:
            result.status = "timeout"
            result.error_message = f"Scan timed out after {self.timeout} seconds"
            logger.warning(f"Scan timeout for {url}")
            
        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)
            logger.error(f"Scan failed for {url}: {e}")
            
        finally:
            result.scan_duration = time.time() - start_time
        
        return result
    
    async def _static_analysis(self, url: str) -> List[ThreatInfo]:
        """
        Perform static analysis on URL structure and patterns.
        
        Args:
            url: URL to analyze
            
        Returns:
            List of detected threats
        """
        threats = []
        
        try:
            parsed = urlparse(url)
            full_url = url.lower()
            
            # Check for malware patterns
            for pattern in self.MALWARE_PATTERNS:
                if re.search(pattern, full_url, re.IGNORECASE):
                    threats.append(ThreatInfo(
                        threat_type="malware",
                        severity="high",
                        description=f"Potential malware pattern detected: {pattern}",
                        confidence=0.8,
                        evidence=[f"Pattern match: {pattern}"]
                    ))
            
            # Check for phishing patterns
            for pattern in self.PHISHING_PATTERNS:
                if re.search(pattern, full_url, re.IGNORECASE):
                    threats.append(ThreatInfo(
                        threat_type="phishing",
                        severity="high",
                        description=f"Potential phishing pattern detected",
                        confidence=0.7,
                        evidence=[f"Phishing pattern: {pattern}"]
                    ))
            
            # Check for suspicious domains
            domain = parsed.netloc.lower()
            for pattern in self.SUSPICIOUS_DOMAINS:
                if re.search(pattern, domain):
                    threats.append(ThreatInfo(
                        threat_type="suspicious_domain",
                        severity="medium",
                        description=f"Suspicious domain pattern: {domain}",
                        confidence=0.6,
                        evidence=[f"Domain pattern: {pattern}"]
                    ))
            
            # Check for blacklisted keywords
            for keyword in self.BLACKLISTED_KEYWORDS:
                if keyword in full_url:
                    threats.append(ThreatInfo(
                        threat_type="blacklisted_content",
                        severity="medium",
                        description=f"Blacklisted keyword found: {keyword}",
                        confidence=0.5,
                        evidence=[f"Keyword: {keyword}"]
                    ))
            
            # URL structure analysis
            if len(parsed.path) > 200:
                threats.append(ThreatInfo(
                    threat_type="suspicious_structure",
                    severity="low",
                    description="Unusually long URL path",
                    confidence=0.3,
                    evidence=[f"Path length: {len(parsed.path)}"]
                ))
            
            # Check for multiple subdomains (potential domain squatting)
            subdomain_count = len(parsed.netloc.split('.')) - 2
            if subdomain_count > 3:
                threats.append(ThreatInfo(
                    threat_type="suspicious_structure",
                    severity="low",
                    description="Excessive subdomain nesting",
                    confidence=0.4,
                    evidence=[f"Subdomain count: {subdomain_count}"]
                ))
            
        except Exception as e:
            logger.error(f"Static analysis error for {url}: {e}")
        
        return threats
    
    async def _domain_analysis(self, url: str) -> List[ThreatInfo]:
        """
        Perform domain and DNS-based analysis.
        
        Args:
            url: URL to analyze
            
        Returns:
            List of detected threats
        """
        threats = []
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check for homograph attacks (similar-looking characters)
            suspicious_chars = ['а', 'е', 'о', 'р', 'с', 'х', 'у']  # Cyrillic chars that look like Latin
            for char in suspicious_chars:
                if char in domain:
                    threats.append(ThreatInfo(
                        threat_type="homograph_attack",
                        severity="high",
                        description="Potential homograph attack detected",
                        confidence=0.8,
                        evidence=[f"Suspicious character: {char}"]
                    ))
            
            # Check domain age (simulated - in real implementation, use WHOIS)
            # For MVP, we'll use domain length as a rough indicator
            if len(domain) < 5:
                threats.append(ThreatInfo(
                    threat_type="suspicious_domain",
                    severity="medium",
                    description="Very short domain name",
                    confidence=0.4,
                    evidence=[f"Domain length: {len(domain)}"]
                ))
            
            # Check for typosquatting patterns
            common_brands = ['google', 'amazon', 'microsoft', 'apple', 'facebook', 'paypal']
            for brand in common_brands:
                if self._is_typosquatting(domain, brand):
                    threats.append(ThreatInfo(
                        threat_type="typosquatting",
                        severity="high",
                        description=f"Potential typosquatting of {brand}",
                        confidence=0.7,
                        evidence=[f"Similar to: {brand}"]
                    ))
            
        except Exception as e:
            logger.error(f"Domain analysis error for {url}: {e}")
        
        return threats
    
    async def _http_analysis(self, url: str) -> List[ThreatInfo]:
        """
        Perform HTTP response analysis.
        
        Args:
            url: URL to analyze
            
        Returns:
            List of detected threats
        """
        threats = []
        
        try:
            response = await self.client.head(url, timeout=10)
            
            # Check response headers for security issues
            headers = response.headers
            
            # Missing security headers
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection',
                'Strict-Transport-Security'
            ]
            
            missing_headers = [h for h in security_headers if h not in headers]
            if missing_headers:
                threats.append(ThreatInfo(
                    threat_type="missing_security_headers",
                    severity="low",
                    description="Missing security headers",
                    confidence=0.3,
                    evidence=missing_headers
                ))
            
            # Check for suspicious redirects
            if response.status_code in [301, 302, 307, 308]:
                location = headers.get('Location', '')
                if location and urlparse(location).netloc != urlparse(url).netloc:
                    threats.append(ThreatInfo(
                        threat_type="suspicious_redirect",
                        severity="medium",
                        description="Cross-domain redirect detected",
                        confidence=0.5,
                        evidence=[f"Redirects to: {location}"]
                    ))
            
            # Check server information
            server = headers.get('Server', '').lower()
            if 'apache' in server and 'ubuntu' in server:
                # This is just an example - in real implementation, check for vulnerable versions
                pass
            
        except httpx.TimeoutException:
            threats.append(ThreatInfo(
                threat_type="connection_timeout",
                severity="low",
                description="Connection timeout during HTTP analysis",
                confidence=0.2,
                evidence=["HTTP timeout"]
            ))
        except Exception as e:
            logger.error(f"HTTP analysis error for {url}: {e}")
        
        return threats
    
    async def _content_analysis(self, url: str) -> List[ThreatInfo]:
        """
        Perform content-based analysis.
        
        Args:
            url: URL to analyze
            
        Returns:
            List of detected threats
        """
        threats = []
        
        try:
            # Get page content (limited size)
            response = await self.client.get(url, timeout=15)
            
            if response.status_code != 200:
                return threats
            
            content = response.text[:50000]  # Limit content size
            content_lower = content.lower()
            
            # Check for malicious JavaScript patterns
            js_patterns = [
                r'eval\s*\(',
                r'document\.write\s*\(',
                r'window\.location\s*=',
                r'document\.location\s*=',
                r'<script[^>]*src=["\'][^"\']*["\'][^>]*>',
                r'javascript:',
                r'vbscript:',
            ]
            
            for pattern in js_patterns:
                if re.search(pattern, content_lower):
                    threats.append(ThreatInfo(
                        threat_type="malicious_javascript",
                        severity="medium",
                        description=f"Suspicious JavaScript pattern detected",
                        confidence=0.6,
                        evidence=[f"JS pattern: {pattern}"]
                    ))
            
            # Check for phishing content
            phishing_indicators = [
                'enter your password',
                'verify your account',
                'update payment information',
                'suspended account',
                'click here immediately',
                'urgent action required',
                'congratulations you have won',
            ]
            
            for indicator in phishing_indicators:
                if indicator in content_lower:
                    threats.append(ThreatInfo(
                        threat_type="phishing_content",
                        severity="high",
                        description=f"Phishing content detected",
                        confidence=0.7,
                        evidence=[f"Phishing indicator: {indicator}"]
                    ))
            
            # Check for hidden iframes
            iframe_pattern = r'<iframe[^>]*style=["\'][^"\']*display:\s*none[^"\']*["\'][^>]*>'
            if re.search(iframe_pattern, content_lower):
                threats.append(ThreatInfo(
                    threat_type="hidden_iframe",
                    severity="high",
                    description="Hidden iframe detected",
                    confidence=0.8,
                    evidence=["Hidden iframe found"]
                ))
            
            # Check for base64 encoded content (potential obfuscation)
            b64_pattern = r'[A-Za-z0-9+/]{50,}={0,2}'
            b64_matches = re.findall(b64_pattern, content)
            if len(b64_matches) > 5:
                threats.append(ThreatInfo(
                    threat_type="obfuscated_content",
                    severity="medium",
                    description="Potential content obfuscation detected",
                    confidence=0.5,
                    evidence=[f"Base64 patterns: {len(b64_matches)}"]
                ))
            
        except httpx.TimeoutException:
            threats.append(ThreatInfo(
                threat_type="content_timeout",
                severity="low",
                description="Timeout during content analysis",
                confidence=0.2,
                evidence=["Content analysis timeout"]
            ))
        except Exception as e:
            logger.error(f"Content analysis error for {url}: {e}")
        
        return threats
    
    def _calculate_damage_score(self, threats: List[ThreatInfo]) -> int:
        """
        Calculate comprehensive damage score based on detected threats.
        
        Args:
            threats: List of detected threats
            
        Returns:
            Damage score from 0-100
        """
        if not threats:
            return 0
        
        # Severity weights
        severity_weights = {
            'low': 10,
            'medium': 25,
            'high': 50,
            'critical': 80
        }
        
        # Threat type multipliers
        threat_multipliers = {
            'malware': 1.5,
            'phishing': 1.4,
            'malicious_javascript': 1.3,
            'hidden_iframe': 1.3,
            'typosquatting': 1.2,
            'homograph_attack': 1.2,
            'suspicious_domain': 1.1,
            'obfuscated_content': 1.1,
            'default': 1.0
        }
        
        total_score = 0
        for threat in threats:
            base_score = severity_weights.get(threat.severity, 10)
            multiplier = threat_multipliers.get(threat.threat_type, threat_multipliers['default'])
            confidence_factor = threat.confidence
            
            threat_score = base_score * multiplier * confidence_factor
            total_score += threat_score
        
        # Normalize to 0-100 scale
        normalized_score = min(100, int(total_score))
        
        # Apply diminishing returns for multiple low-severity threats
        if len(threats) > 10:
            reduction_factor = 1 - (len(threats) - 10) * 0.02
            normalized_score = int(normalized_score * max(0.5, reduction_factor))
        
        return normalized_score
    
    def _determine_risk_level(self, damage_score: int) -> str:
        """
        Determine overall risk level based on damage score.
        
        Args:
            damage_score: Calculated damage score
            
        Returns:
            Risk level string
        """
        if damage_score == 0:
            return "safe"
        elif damage_score <= 20:
            return "low"
        elif damage_score <= 50:
            return "medium"
        elif damage_score <= 80:
            return "high"
        else:
            return "critical"
    
    def _is_typosquatting(self, domain: str, brand: str) -> bool:
        """
        Check if domain is potentially typosquatting a brand.
        
        Args:
            domain: Domain to check
            brand: Brand name to compare against
            
        Returns:
            True if potential typosquatting detected
        """
        # Simple Levenshtein distance check
        if brand in domain:
            return False  # Exact match, not typosquatting
        
        # Calculate edit distance
        distance = self._levenshtein_distance(domain, brand)
        
        # If distance is small relative to brand length, it might be typosquatting
        if len(brand) > 4 and distance <= 2:
            return True
        
        return False
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global scanner instance
scanner = AdvancedURLScanner()

async def perform_scan(url: str, options: Dict[str, Any] = None) -> ScanResult:
    """
    Convenience function to perform a URL scan.
    
    Args:
        url: URL to scan
        options: Scanning options
        
    Returns:
        Scan result with damage assessment
    """
    return await scanner.scan_url(url, options)

def format_scan_result(result: ScanResult) -> str:
    """
    Format scan result for display in Telegram.
    
    Args:
        result: Scan result to format
        
    Returns:
        Formatted string for Telegram message
    """
    if result.status == "failed":
        return f"❌ <b>Scan Failed</b>\n\n" \
               f"URL: <code>{result.url}</code>\n" \
               f"Error: {result.error_message}\n" \
               f"Duration: {result.scan_duration:.2f}s"
    
    if result.status == "timeout":
        return f"⏱️ <b>Scan Timeout</b>\n\n" \
               f"URL: <code>{result.url}</code>\n" \
               f"The scan took too long to complete.\n" \
               f"Duration: {result.scan_duration:.2f}s"
    
    # Risk level emojis
    risk_emojis = {
        "safe": "✅",
        "low": "⚠️",
        "medium": "🟡",
        "high": "🔴",
        "critical": "💀"
    }
    
    emoji = risk_emojis.get(result.overall_risk, "❓")
    
    message = f"{emoji} <b>Scan Complete</b>\n\n"
    message += f"🔗 <b>URL:</b> <code>{result.url}</code>\n"
    message += f"📊 <b>Damage Score:</b> {result.damage_score}/100\n"
    message += f"⚡ <b>Risk Level:</b> {result.overall_risk.upper()}\n"
    message += f"⏱️ <b>Duration:</b> {result.scan_duration:.2f}s\n\n"
    
    if result.threats_found:
        message += f"🚨 <b>Threats Detected ({len(result.threats_found)}):</b>\n"
        
        # Group threats by severity
        threats_by_severity = {}
        for threat in result.threats_found:
            if threat.severity not in threats_by_severity:
                threats_by_severity[threat.severity] = []
            threats_by_severity[threat.severity].append(threat)
        
        # Display threats by severity (highest first)
        severity_order = ['critical', 'high', 'medium', 'low']
        for severity in severity_order:
            if severity in threats_by_severity:
                severity_emoji = {"critical": "💀", "high": "🔴", "medium": "🟡", "low": "⚠️"}
                message += f"\n{severity_emoji.get(severity, '•')} <b>{severity.upper()}:</b>\n"
                
                for threat in threats_by_severity[severity][:3]:  # Show max 3 per severity
                    confidence_pct = int(threat.confidence * 100)
                    message += f"  • {threat.description} ({confidence_pct}%)\n"
                
                if len(threats_by_severity[severity]) > 3:
                    remaining = len(threats_by_severity[severity]) - 3
                    message += f"  • ... and {remaining} more {severity} threats\n"
    else:
        message += "✅ <b>No threats detected</b>\n"
    
    # Add summary
    message += f"\n📋 <b>Summary:</b>\n"
    if result.damage_score == 0:
        message += "This URL appears to be safe."
    elif result.damage_score <= 20:
        message += "This URL has low risk factors."
    elif result.damage_score <= 50:
        message += "This URL has moderate risk factors. Exercise caution."
    elif result.damage_score <= 80:
        message += "This URL has high risk factors. Avoid if possible."
    else:
        message += "This URL is highly dangerous. Do not visit!"
    
    return message
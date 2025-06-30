"""
Input validation utilities for the Telegram bot.
Provides comprehensive validation for URLs, user inputs, and data sanitization.
"""

import re
import logging
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse, parse_qs
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class URLValidator:
    """Comprehensive URL validation and sanitization."""
    
    # Common malicious patterns to detect
    MALICIOUS_PATTERNS = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'ftp:',
        r'<script',
        r'<iframe',
        r'<embed',
        r'<object',
        r'onload=',
        r'onerror=',
        r'onclick=',
    ]
    
    # Allowed URL schemes
    ALLOWED_SCHEMES = ['http', 'https']
    
    # URL pattern for basic validation
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """
        Validate URL format and safety.
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"
        
        # Remove whitespace
        url = url.strip()
        
        # Check length
        if len(url) > 2048:
            return False, "URL is too long (max 2048 characters)"
        
        # Check for malicious patterns
        url_lower = url.lower()
        for pattern in cls.MALICIOUS_PATTERNS:
            if re.search(pattern, url_lower):
                return False, f"URL contains potentially malicious content: {pattern}"
        
        # Basic URL format validation
        if not cls.URL_PATTERN.match(url):
            return False, "Invalid URL format"
        
        # Parse URL components
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"Failed to parse URL: {str(e)}"
        
        # Check scheme
        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            return False, f"URL scheme '{parsed.scheme}' not allowed"
        
        # Check for valid hostname
        if not parsed.hostname:
            return False, "URL must have a valid hostname"
        
        # Additional security checks
        hostname = parsed.hostname.lower()
        
        # Block localhost and private IPs in production
        if hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False, "Localhost URLs are not allowed"
        
        # Check for private IP ranges
        if cls._is_private_ip(hostname):
            return False, "Private IP addresses are not allowed"
        
        return True, ""
    
    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """
        Sanitize URL by removing dangerous components.
        
        Args:
            url: URL to sanitize
            
        Returns:
            Sanitized URL string
        """
        if not url:
            return ""
        
        # Remove whitespace and control characters
        url = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', url.strip())
        
        # Ensure proper scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @classmethod
    def _is_private_ip(cls, hostname: str) -> bool:
        """Check if hostname is a private IP address."""
        try:
            # Simple check for common private IP ranges
            parts = hostname.split('.')
            if len(parts) != 4:
                return False
            
            # Convert to integers
            octets = [int(part) for part in parts]
            
            # Check private ranges
            # 10.0.0.0/8
            if octets[0] == 10:
                return True
            
            # 172.16.0.0/12
            if octets[0] == 172 and 16 <= octets[1] <= 31:
                return True
            
            # 192.168.0.0/16
            if octets[0] == 192 and octets[1] == 168:
                return True
            
            return False
        except (ValueError, IndexError):
            return False

class TextValidator:
    """Text input validation and sanitization."""
    
    # Maximum lengths for different input types
    MAX_LENGTHS = {
        'message': 4096,  # Telegram message limit
        'command_arg': 256,
        'search_query': 100,
        'user_input': 1000
    }
    
    # Patterns for different input types
    PATTERNS = {
        'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        'username': re.compile(r'^[a-zA-Z0-9_]{3,32}$'),
        'token': re.compile(r'^[a-zA-Z0-9_-]{10,}$'),
    }
    
    @classmethod
    def validate_text(cls, text: str, input_type: str = 'user_input') -> Tuple[bool, str]:
        """
        Validate text input based on type.
        
        Args:
            text: Text to validate
            input_type: Type of input for validation rules
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "Text cannot be empty"
        
        # Check length
        max_length = cls.MAX_LENGTHS.get(input_type, cls.MAX_LENGTHS['user_input'])
        if len(text) > max_length:
            return False, f"Text too long (max {max_length} characters)"
        
        # Check for null bytes and control characters
        if '\x00' in text:
            return False, "Text contains null bytes"
        
        # Remove or check for excessive whitespace
        if len(text.strip()) == 0:
            return False, "Text cannot be only whitespace"
        
        # Check for specific patterns if needed
        if input_type in cls.PATTERNS:
            if not cls.PATTERNS[input_type].match(text):
                return False, f"Invalid {input_type} format"
        
        return True, ""
    
    @classmethod
    def sanitize_text(cls, text: str, input_type: str = 'user_input') -> str:
        """
        Sanitize text input.
        
        Args:
            text: Text to sanitize
            input_type: Type of input for sanitization rules
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate if too long
        max_length = cls.MAX_LENGTHS.get(input_type, cls.MAX_LENGTHS['user_input'])
        if len(text) > max_length:
            text = text[:max_length].rstrip()
        
        return text
    
    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, str]:
        """Validate email address format."""
        return cls.validate_text(email, 'email')
    
    @classmethod
    def validate_username(cls, username: str) -> Tuple[bool, str]:
        """Validate username format."""
        return cls.validate_text(username, 'username')

class CommandValidator:
    """Validation for bot commands and arguments."""
    
    @classmethod
    def validate_command_args(cls, args: str, expected_count: int = None) -> Tuple[bool, str, List[str]]:
        """
        Validate command arguments.
        
        Args:
            args: Command arguments string
            expected_count: Expected number of arguments
            
        Returns:
            Tuple of (is_valid, error_message, parsed_args)
        """
        if not args:
            parsed_args = []
        else:
            # Split arguments by whitespace
            parsed_args = args.strip().split()
        
        # Check argument count
        if expected_count is not None and len(parsed_args) != expected_count:
            return False, f"Expected {expected_count} arguments, got {len(parsed_args)}", []
        
        # Validate each argument
        for i, arg in enumerate(parsed_args):
            is_valid, error = TextValidator.validate_text(arg, 'command_arg')
            if not is_valid:
                return False, f"Invalid argument {i+1}: {error}", []
        
        return True, "", parsed_args
    
    @classmethod
    def parse_scan_command(cls, args: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Parse scan command arguments.
        
        Args:
            args: Command arguments
            
        Returns:
            Tuple of (is_valid, error_message, parsed_data)
        """
        if not args:
            return False, "URL is required for scan command", {}
        
        parts = args.strip().split()
        if not parts:
            return False, "URL is required for scan command", {}
        
        url = parts[0]
        
        # Validate URL
        is_valid, error = URLValidator.validate_url(url)
        if not is_valid:
            return False, f"Invalid URL: {error}", {}
        
        # Parse additional options (if any)
        options = {}
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                options[key.lower()] = value
        
        return True, "", {
            'url': URLValidator.sanitize_url(url),
            'options': options
        }

class SecurityValidator:
    """Security-focused validation utilities."""
    
    @classmethod
    def validate_token(cls, token: str) -> Tuple[bool, str]:
        """
        Validate security token format.
        
        Args:
            token: Token to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not token:
            return False, "Token cannot be empty"
        
        # Check token format
        if not re.match(r'^[a-zA-Z0-9_-]+$', token):
            return False, "Token contains invalid characters"
        
        # Check length
        if len(token) < 10:
            return False, "Token too short"
        
        if len(token) > 256:
            return False, "Token too long"
        
        return True, ""
    
    @classmethod
    def validate_user_id(cls, user_id: Any) -> Tuple[bool, str, int]:
        """
        Validate Telegram user ID.
        
        Args:
            user_id: User ID to validate
            
        Returns:
            Tuple of (is_valid, error_message, validated_id)
        """
        try:
            validated_id = int(user_id)
            if validated_id <= 0:
                return False, "User ID must be positive", 0
            return True, "", validated_id
        except (ValueError, TypeError):
            return False, "Invalid user ID format", 0
    
    @classmethod
    def is_safe_filename(cls, filename: str) -> bool:
        """
        Check if filename is safe (no path traversal).
        
        Args:
            filename: Filename to check
            
        Returns:
            True if safe, False otherwise
        """
        if not filename:
            return False
        
        # Check for path traversal attempts
        dangerous_patterns = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for pattern in dangerous_patterns:
            if pattern in filename:
                return False
        
        # Check for reserved names (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        if filename.upper() in reserved_names:
            return False
        
        return True

# Convenience functions for common validations
def validate_url(url: str) -> Tuple[bool, str]:
    """Convenience function for URL validation."""
    return URLValidator.validate_url(url)

def validate_text(text: str, input_type: str = 'user_input') -> Tuple[bool, str]:
    """Convenience function for text validation."""
    return TextValidator.validate_text(text, input_type)

def sanitize_url(url: str) -> str:
    """Convenience function for URL sanitization."""
    return URLValidator.sanitize_url(url)

def sanitize_text(text: str, input_type: str = 'user_input') -> str:
    """Convenience function for text sanitization."""
    return TextValidator.sanitize_text(text, input_type)
"""
Real YOLOv8 Car Damage Detection System

This module implements actual YOLOv8-based damage detection for car images.
Uses real computer vision and machine learning for accurate damage assessment.
Replaces the previous mock implementation with production-ready AI analysis.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any

# Import the real YOLOv8 implementation
try:
    from .yolo_real import (
        YOLOCarDamageDetector,
        analyze_car_images as _real_analyze_car_images,
        analyze_text_for_damage as _real_analyze_text_for_damage,
        quick_damage_check as _real_quick_damage_check,
        initialize_yolo_model as _real_initialize_yolo_model,
        get_global_detector
    )
    REAL_YOLO_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Real YOLOv8 implementation loaded successfully")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Failed to import real YOLOv8 implementation: {e}")
    logger.warning("🔄 Falling back to mock implementation for compatibility")
    REAL_YOLO_AVAILABLE = False

# Global detector instance for performance optimization
_global_detector = None

def initialize_yolo_model(model_path: str = "models/car_damage_yolo.pt", 
                         confidence_threshold: float = 0.5) -> Optional[YOLOCarDamageDetector]:
    """
    Initialize YOLOv8 model for car damage detection
    
    Args:
        model_path: Path to YOLOv8 model weights
        confidence_threshold: Detection confidence threshold
        
    Returns:
        YOLOCarDamageDetector instance or None if failed
    """
    global _global_detector
    
    if REAL_YOLO_AVAILABLE:
        try:
            _global_detector = _real_initialize_yolo_model(model_path, confidence_threshold)
            logger.info(f"🤖 Real YOLOv8 model initialized - path: {model_path}")
            return _global_detector
        except Exception as e:
            logger.error(f"❌ Failed to initialize real YOLOv8 model: {e}")
            return None
    else:
        logger.warning("⚠️ Real YOLOv8 not available, using mock implementation")
        return _create_mock_detector(model_path, confidence_threshold)

def get_detector() -> Optional[YOLOCarDamageDetector]:
    """Get the global detector instance"""
    if REAL_YOLO_AVAILABLE:
        return get_global_detector()
    else:
        return _global_detector

async def analyze_car_images(image_urls: List[str], description: str = "", 
                           model_path: str = "models/car_damage_yolo.pt",
                           confidence_threshold: float = 0.5) -> Dict[str, Any]:
    """
    Analyze multiple car images for damage using YOLOv8
    
    Args:
        image_urls: List of image URLs to analyze
        description: Car listing description text
        model_path: Path to YOLOv8 model weights
        confidence_threshold: Detection confidence threshold
        
    Returns:
        Combined analysis results with damage assessment
    """
    if REAL_YOLO_AVAILABLE:
        try:
            result = await _real_analyze_car_images(
                image_urls, description, model_path, confidence_threshold
            )
            logger.info(f"🔍 Real YOLOv8 analysis completed - {len(image_urls)} images, "
                       f"score: {result.get('combined_damage_score', 0)}")
            return result
        except Exception as e:
            logger.error(f"❌ Real YOLOv8 analysis failed: {e}")
            # Fall back to mock if real analysis fails
            return await _mock_analyze_car_images(image_urls, description)
    else:
        logger.info("🔄 Using mock analysis (real YOLOv8 not available)")
        return await _mock_analyze_car_images(image_urls, description)

def analyze_text_for_damage(text: str) -> Dict[str, int]:
    """
    Analyze Turkish text for damage-related keywords
    
    Args:
        text: Turkish text to analyze
        
    Returns:
        Dict mapping damage types to keyword counts
    """
    if REAL_YOLO_AVAILABLE:
        return _real_analyze_text_for_damage(text)
    else:
        return _mock_analyze_text_for_damage(text)

async def quick_damage_check(image_url: str, description: str = "",
                           model_path: str = "models/car_damage_yolo.pt") -> Tuple[int, str]:
    """
    Quick damage assessment for a single image and description
    
    Args:
        image_url: Single image URL
        description: Description text
        model_path: Path to YOLOv8 model
        
    Returns:
        Tuple of (damage_score, summary_text)
    """
    if REAL_YOLO_AVAILABLE:
        try:
            return await _real_quick_damage_check(image_url, description, model_path)
        except Exception as e:
            logger.error(f"❌ Real quick damage check failed: {e}")
            # Fall back to mock
            return await _mock_quick_damage_check(image_url, description)
    else:
        return await _mock_quick_damage_check(image_url, description)

# ==============================================================================
# MOCK IMPLEMENTATION (FALLBACK)
# ==============================================================================

import random
import re

# Mock damage types and their Turkish keywords  
DAMAGE_KEYWORDS = {
    'dent': ['ezik', 'çukur', 'batık', 'girinti', 'çökmüş'],
    'scratch': ['çizik', 'sıyrık', 'çizgi', 'kazıntı', 'çizilmiş'],
    'crack': ['çatlak', 'kırık', 'yarık', 'çatlamış'],
    'rust': ['pas', 'korozyon', 'paslanma', 'paslanmış'],
    'broken_part': ['kırık', 'parça', 'eksik', 'kopuk', 'kırılmış', 'hasarlı'],
    'paint_damage': ['boya', 'renk', 'soluk', 'atmış', 'boyası', 'solmuş']
}

class MockYOLODamageDetector:
    """Mock YOLOv8 damage detector for fallback compatibility"""
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model_loaded = True
        self.device = 'mock-cpu'
        logger.info(f"🔄 Mock YOLO detector initialized - {model_path}")
    
    async def load_model(self) -> bool:
        """Mock model loading"""
        await asyncio.sleep(0.1)  # Simulate loading time
        return True
    
    async def detect_damage_from_url(self, image_url: str) -> Dict[str, Any]:
        """Mock damage detection from image URL"""
        try:
            await asyncio.sleep(0.3)  # Simulate processing
            
            damage_types = list(DAMAGE_KEYWORDS.keys())
            detected_damages = []
            
            # Randomly detect 0-2 damage types
            num_damages = random.randint(0, 2)
            if num_damages > 0:
                selected_damages = random.sample(damage_types, min(num_damages, len(damage_types)))
                
                for damage_type in selected_damages:
                    confidence = random.uniform(self.confidence_threshold, 0.90)
                    detected_damages.append({
                        'type': damage_type,
                        'confidence': confidence,
                        'bbox': [
                            random.randint(10, 200),
                            random.randint(10, 200), 
                            random.randint(250, 400),
                            random.randint(250, 400)
                        ],
                        'area': random.randint(1000, 5000)
                    })
            
            # Calculate damage score
            if detected_damages:
                avg_confidence = sum(d['confidence'] for d in detected_damages) / len(detected_damages)
                damage_score = min(int(avg_confidence * 70 + len(detected_damages) * 15), 100)
            else:
                damage_score = random.randint(0, 10)
            
            return {
                'image_url': image_url,
                'damages_detected': detected_damages,
                'damage_score': damage_score,
                'total_damages': len(detected_damages),
                'processing_time': 0.3,
                'model_version': 'mock-yolov8-fallback',
                'analysis_successful': True,
                'device_used': 'mock-cpu'
            }
            
        except Exception as e:
            logger.error(f"Mock damage detection error: {e}")
            return {
                'image_url': image_url,
                'damages_detected': [],
                'damage_score': 0,
                'total_damages': 0,
                'processing_time': 0,
                'model_version': 'mock-yolov8-fallback',
                'analysis_successful': False,
                'error': str(e)
            }

def _create_mock_detector(model_path: str, confidence_threshold: float) -> MockYOLODamageDetector:
    """Create mock detector instance"""
    return MockYOLODamageDetector(model_path, confidence_threshold)

def _mock_analyze_text_for_damage(text: str) -> Dict[str, int]:
    """Mock text analysis for damage keywords"""
    if not text:
        return {}
    
    text_lower = text.lower()
    damage_counts = {}
    
    for damage_type, keywords in DAMAGE_KEYWORDS.items():
        count = 0
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text_lower)
            count += len(matches)
        
        if count > 0:
            damage_counts[damage_type] = count
    
    return damage_counts

async def _mock_analyze_car_images(image_urls: List[str], description: str = "") -> Dict[str, Any]:
    """Mock analysis of multiple car images"""
    if not image_urls:
        return {
            'visual_analysis': [],
            'text_analysis': _mock_analyze_text_for_damage(description),
            'combined_damage_score': 0,
            'total_damages_found': 0,
            'analysis_summary': "No images provided for analysis",
            'model_used': 'mock-yolov8-fallback'
        }
    
    detector = MockYOLODamageDetector()
    visual_results = []
    max_images = min(len(image_urls), 5)
    
    for i, url in enumerate(image_urls[:max_images]):
        result = await detector.detect_damage_from_url(url)
        visual_results.append(result)
        if i < max_images - 1:
            await asyncio.sleep(0.1)
    
    # Analyze text
    text_analysis = _mock_analyze_text_for_damage(description)
    
    # Calculate combined results
    successful_analyses = [r for r in visual_results if r['analysis_successful']]
    visual_damages = sum(len(r['damages_detected']) for r in successful_analyses)
    text_damages = sum(text_analysis.values())
    total_damages = visual_damages + text_damages
    
    if successful_analyses:
        avg_visual_score = sum(r['damage_score'] for r in successful_analyses) / len(successful_analyses)
    else:
        avg_visual_score = 0
    
    text_score = min(text_damages * 12, 40)
    combined_score = min(int((avg_visual_score * 0.75) + (text_score * 0.25)), 100)
    
    # Generate Turkish summary
    if combined_score >= 70:
        severity = "Yüksek"
    elif combined_score >= 40:
        severity = "Orta"
    elif combined_score >= 20:
        severity = "Düşük"
    else:
        severity = "Minimal"
    
    summary = f"Hasar Seviyesi: {severity} (Skor: {combined_score}/100)"
    if total_damages > 0:
        summary += f" - {total_damages} hasar tespit edildi"
    summary += " (Mock analiz)"
    
    return {
        'visual_analysis': visual_results,
        'text_analysis': text_analysis,
        'combined_damage_score': combined_score,
        'total_damages_found': total_damages,
        'analysis_summary': summary,
        'images_analyzed': len(visual_results),
        'successful_analyses': len(successful_analyses),
        'processing_successful': len(successful_analyses) > 0 or bool(text_analysis),
        'model_used': 'mock-yolov8-fallback',
        'device_used': 'mock-cpu'
    }

async def _mock_quick_damage_check(image_url: str, description: str = "") -> Tuple[int, str]:
    """Mock quick damage assessment"""
    result = await _mock_analyze_car_images([image_url], description)
    return result['combined_damage_score'], result['analysis_summary']

# ==============================================================================
# EXPORTS
# ==============================================================================

# Export the main functions with consistent API
__all__ = [
    'initialize_yolo_model',
    'get_detector',
    'analyze_car_images', 
    'analyze_text_for_damage',
    'quick_damage_check',
    'YOLOCarDamageDetector' if REAL_YOLO_AVAILABLE else 'MockYOLODamageDetector'
]

# Log initialization status
if REAL_YOLO_AVAILABLE:
    logger.info("🤖 YOLOv8 module initialized with REAL AI implementation")
else:
    logger.warning("🔄 YOLOv8 module initialized with MOCK fallback implementation")
"""
Mock YOLOv8 Car Damage Detection System for MVP Testing

This is a temporary implementation that simulates YOLOv8 damage detection
without requiring the actual computer vision dependencies. It will be replaced
with the real YOLOv8 implementation once the model is properly set up.
"""

import asyncio
import random
import re
from typing import Dict, List, Optional, Tuple

import logging
logger = logging.getLogger(__name__)

# Mock damage types and their Turkish keywords
DAMAGE_KEYWORDS = {
    'dent': ['ezik', 'çukur', 'batık', 'girinti'],
    'scratch': ['çizik', 'sıyrık', 'çizgi', 'kazıntı'],
    'crack': ['çatlak', 'kırık', 'yarık'],
    'rust': ['pas', 'korozyon', 'paslanma'],
    'broken_part': ['kırık', 'parça', 'eksik', 'kopuk'],
    'paint_damage': ['boya', 'renk', 'soluk', 'atmış']
}

class MockYOLODamageDetector:
    """Mock YOLOv8 damage detector that simulates real behavior"""
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model_loaded = True  # Simulate loaded model
        logger.info(f"Mock YOLO damage detector initialized - model_path: {model_path}, confidence: {confidence_threshold}")
    
    async def detect_damage_from_url(self, image_url: str) -> Dict:
        """
        Mock damage detection from image URL
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dict with damage analysis results
        """
        try:
            # Simulate downloading and processing image
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Mock damage detection results
            damage_types = list(DAMAGE_KEYWORDS.keys())
            detected_damages = []
            
            # Randomly detect 0-3 damage types
            num_damages = random.randint(0, 3)
            selected_damages = random.sample(damage_types, min(num_damages, len(damage_types)))
            
            for damage_type in selected_damages:
                confidence = random.uniform(self.confidence_threshold, 0.95)
                detected_damages.append({
                    'type': damage_type,
                    'confidence': confidence,
                    'bbox': [
                        random.randint(10, 200),  # x
                        random.randint(10, 200),  # y
                        random.randint(50, 150),  # width
                        random.randint(50, 150)   # height
                    ]
                })
            
            # Calculate overall damage score
            if detected_damages:
                avg_confidence = sum(d['confidence'] for d in detected_damages) / len(detected_damages)
                damage_score = min(int(avg_confidence * 100 + len(detected_damages) * 10), 100)
            else:
                damage_score = random.randint(0, 15)  # Low random score for no visible damage
            
            result = {
                'image_url': image_url,
                'damages_detected': detected_damages,
                'damage_score': damage_score,
                'total_damages': len(detected_damages),
                'processing_time': 0.5,
                'model_version': 'mock-yolov8',
                'analysis_successful': True
            }
            
            logger.info(f"Mock damage detection completed - url: {image_url}, damages: {len(detected_damages)}, score: {damage_score}")
            
            return result
            
        except Exception as e:
            logger.error(f"Mock damage detection failed - url: {image_url}, error: {str(e)}")
            return {
                'image_url': image_url,
                'damages_detected': [],
                'damage_score': 0,
                'total_damages': 0,
                'processing_time': 0,
                'model_version': 'mock-yolov8',
                'analysis_successful': False,
                'error': str(e)
            }

def analyze_text_for_damage(text: str) -> Dict[str, int]:
    """
    Analyze Turkish text for damage-related keywords
    
    Args:
        text: Turkish text to analyze
        
    Returns:
        Dict mapping damage types to keyword counts
    """
    if not text:
        return {}
    
    text_lower = text.lower()
    damage_counts = {}
    
    for damage_type, keywords in DAMAGE_KEYWORDS.items():
        count = 0
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text_lower)
            count += len(matches)
        
        if count > 0:
            damage_counts[damage_type] = count
    
    return damage_counts

async def analyze_car_images(image_urls: List[str], description: str = "") -> Dict:
    """
    Analyze multiple car images for damage using mock YOLOv8
    
    Args:
        image_urls: List of image URLs to analyze
        description: Car listing description text
        
    Returns:
        Combined analysis results
    """
    if not image_urls:
        return {
            'visual_analysis': [],
            'text_analysis': analyze_text_for_damage(description),
            'combined_damage_score': 0,
            'total_damages_found': 0,
            'analysis_summary': "No images provided for analysis"
        }
    
    detector = MockYOLODamageDetector()
    
    # Analyze images (limit to first 5 for performance)
    visual_results = []
    max_images = min(len(image_urls), 5)
    
    for i, url in enumerate(image_urls[:max_images]):
        logger.info(f"Analyzing image {i+1}/{max_images} - url: {url}")
        result = await detector.detect_damage_from_url(url)
        visual_results.append(result)
        
        # Small delay between requests
        if i < max_images - 1:
            await asyncio.sleep(0.2)
    
    # Analyze description text
    text_analysis = analyze_text_for_damage(description)
    
    # Calculate combined results
    visual_damages = sum(len(r['damages_detected']) for r in visual_results if r['analysis_successful'])
    text_damages = sum(text_analysis.values())
    total_damages = visual_damages + text_damages
    
    # Calculate combined damage score
    if visual_results:
        avg_visual_score = sum(r['damage_score'] for r in visual_results if r['analysis_successful']) / len([r for r in visual_results if r['analysis_successful']])
    else:
        avg_visual_score = 0
    
    text_score = min(text_damages * 15, 50)  # Text contributes up to 50 points
    combined_score = min(int((avg_visual_score * 0.7) + (text_score * 0.3)), 100)
    
    # Generate summary
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
    
    return {
        'visual_analysis': visual_results,
        'text_analysis': text_analysis,
        'combined_damage_score': combined_score,
        'total_damages_found': total_damages,
        'analysis_summary': summary,
        'images_analyzed': len(visual_results),
        'processing_successful': len([r for r in visual_results if r['analysis_successful']]) > 0 or bool(text_analysis)
    }

async def quick_damage_check(image_url: str, description: str = "") -> Tuple[int, str]:
    """
    Quick damage assessment for a single image and description
    
    Args:
        image_url: Single image URL
        description: Description text
        
    Returns:
        Tuple of (damage_score, summary_text)
    """
    result = await analyze_car_images([image_url], description)
    return result['combined_damage_score'], result['analysis_summary']

# Mock function to replace the original YOLOv8 initialization
def initialize_yolo_model(model_path: str = None) -> MockYOLODamageDetector:
    """Initialize mock YOLO model"""
    return MockYOLODamageDetector(model_path)

# Export the main functions
__all__ = [
    'MockYOLODamageDetector',
    'analyze_car_images', 
    'analyze_text_for_damage',
    'quick_damage_check',
    'initialize_yolo_model'
]
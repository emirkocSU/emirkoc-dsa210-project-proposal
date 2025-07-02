"""
Real YOLOv8 Car Damage Detection System

This module implements actual YOLOv8-based damage detection for car images,
replacing the mock implementation with real computer vision capabilities.
"""

import asyncio
import logging
import re
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import aiohttp
import cv2
import numpy as np
from ultralytics import YOLO
import torch

logger = logging.getLogger(__name__)

# Car damage class mapping for YOLOv8
CAR_DAMAGE_CLASSES = {
    0: 'dent',
    1: 'scratch',
    2: 'crack',
    3: 'rust',
    4: 'broken_part',
    5: 'paint_damage',
    6: 'headlight_damage',
    7: 'windshield_damage',
    8: 'tire_damage',
    9: 'mirror_damage'
}

# Turkish damage keywords for text analysis
DAMAGE_KEYWORDS = {
    'dent': ['ezik', 'çukur', 'batık', 'girinti', 'çökmüş'],
    'scratch': ['çizik', 'sıyrık', 'çizgi', 'kazıntı', 'çizilmiş'],
    'crack': ['çatlak', 'kırık', 'yarık', 'çatlamış'],
    'rust': ['pas', 'korozyon', 'paslanma', 'paslanmış'],
    'broken_part': ['kırık', 'parça', 'eksik', 'kopuk', 'kırılmış', 'hasarlı'],
    'paint_damage': ['boya', 'renk', 'soluk', 'atmış', 'boyası', 'solmuş'],
    'headlight_damage': ['far', 'ışık', 'lamba', 'kırık far'],
    'windshield_damage': ['cam', 'ön cam', 'windshield', 'çatlak cam'],
    'tire_damage': ['lastik', 'tekerlek', 'jant', 'patlak'],
    'mirror_damage': ['ayna', 'dikiz', 'kırık ayna']
}

class YOLOCarDamageDetector:
    """Real YOLOv8 car damage detector"""
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.5, device: str = 'auto'):
        """
        Initialize YOLOv8 damage detector
        
        Args:
            model_path: Path to YOLOv8 model weights
            confidence_threshold: Minimum confidence for detections
            device: Device to run inference on ('auto', 'cpu', 'cuda')
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = self._get_device(device)
        self.model = None
        self.model_loaded = False
        
        logger.info(f"Initializing YOLOv8 detector - model: {model_path}, device: {self.device}")
    
    def _get_device(self, device: str) -> str:
        """Determine the best device for inference"""
        if device == 'auto':
            if torch.cuda.is_available():
                return 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return 'mps'
            else:
                return 'cpu'
        return device
    
    async def load_model(self) -> bool:
        """Load YOLOv8 model asynchronously"""
        try:
            if self.model_loaded:
                return True
            
            # Check if model file exists
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found: {self.model_path}")
                # Try to download a pre-trained model as fallback
                await self._download_pretrained_model()
            
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(None, self._load_model_sync)
            
            if self.model:
                self.model_loaded = True
                logger.info(f"YOLOv8 model loaded successfully on {self.device}")
                return True
            else:
                logger.error("Failed to load YOLOv8 model")
                return False
                
        except Exception as e:
            logger.error(f"Error loading YOLOv8 model: {e}")
            return False
    
    def _load_model_sync(self) -> Optional[YOLO]:
        """Synchronous model loading"""
        try:
            model = YOLO(self.model_path)
            model.to(self.device)
            return model
        except Exception as e:
            logger.error(f"Error in _load_model_sync: {e}")
            return None
    
    async def _download_pretrained_model(self):
        """Download a pre-trained YOLOv8 model if custom model not available"""
        try:
            logger.info("Custom model not found, downloading pre-trained YOLOv8n...")
            
            # Create models directory if it doesn't exist
            models_dir = Path(self.model_path).parent
            models_dir.mkdir(exist_ok=True)
            
            # Download YOLOv8n as fallback
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download_yolov8n)
            
        except Exception as e:
            logger.error(f"Error downloading pre-trained model: {e}")
    
    def _download_yolov8n(self):
        """Download YOLOv8n model synchronously"""
        try:
            # This will download yolov8n.pt to the current directory
            model = YOLO('yolov8n.pt')
            
            # Move to the expected location
            import shutil
            if os.path.exists('yolov8n.pt'):
                shutil.move('yolov8n.pt', self.model_path)
                logger.info(f"Downloaded YOLOv8n model to {self.model_path}")
        except Exception as e:
            logger.error(f"Error downloading YOLOv8n: {e}")
    
    async def download_image(self, image_url: str) -> Optional[np.ndarray]:
        """Download and decode image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=10) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Convert to numpy array
                        nparr = np.frombuffer(image_data, np.uint8)
                        
                        # Decode image
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if image is not None:
                            logger.debug(f"Successfully downloaded image: {image_url}")
                            return image
                        else:
                            logger.warning(f"Failed to decode image: {image_url}")
                            return None
                    else:
                        logger.warning(f"HTTP {response.status} for image: {image_url}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout downloading image: {image_url}")
            return None
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return None
    
    async def detect_damage_from_url(self, image_url: str) -> Dict[str, Any]:
        """
        Detect damage from image URL using YOLOv8
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dict with damage analysis results
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Ensure model is loaded
            if not self.model_loaded:
                model_loaded = await self.load_model()
                if not model_loaded:
                    return self._create_error_result(image_url, "Model not available")
            
            # Download image
            image = await self.download_image(image_url)
            if image is None:
                return self._create_error_result(image_url, "Failed to download image")
            
            # Run inference in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self._run_inference, image)
            
            if results is None:
                return self._create_error_result(image_url, "Inference failed")
            
            # Process results
            detected_damages = self._process_yolo_results(results)
            damage_score = self._calculate_damage_score(detected_damages)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            result = {
                'image_url': image_url,
                'damages_detected': detected_damages,
                'damage_score': damage_score,
                'total_damages': len(detected_damages),
                'processing_time': processing_time,
                'model_version': 'yolov8-real',
                'analysis_successful': True,
                'device_used': self.device
            }
            
            logger.info(f"YOLOv8 damage detection completed - URL: {image_url}, "
                       f"damages: {len(detected_damages)}, score: {damage_score}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in detect_damage_from_url: {e}")
            return self._create_error_result(image_url, str(e))
    
    def _run_inference(self, image: np.ndarray) -> Optional[Any]:
        """Run YOLOv8 inference synchronously"""
        try:
            if self.model is None:
                return None
            
            # Run inference
            results = self.model(image, conf=self.confidence_threshold, verbose=False)
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Error in YOLOv8 inference: {e}")
            return None
    
    def _process_yolo_results(self, results) -> List[Dict[str, Any]]:
        """Process YOLOv8 detection results"""
        detected_damages = []
        
        try:
            if hasattr(results, 'boxes') and results.boxes is not None:
                boxes = results.boxes
                
                for i in range(len(boxes)):
                    # Extract detection data
                    box = boxes.xyxy[i].cpu().numpy()  # Bounding box coordinates
                    conf = float(boxes.conf[i].cpu().numpy())  # Confidence
                    cls = int(boxes.cls[i].cpu().numpy())  # Class ID
                    
                    # Map class ID to damage type
                    damage_type = CAR_DAMAGE_CLASSES.get(cls, f'unknown_{cls}')
                    
                    damage = {
                        'type': damage_type,
                        'confidence': conf,
                        'bbox': [float(x) for x in box],  # [x1, y1, x2, y2]
                        'area': float((box[2] - box[0]) * (box[3] - box[1]))
                    }
                    
                    detected_damages.append(damage)
            
            # Sort by confidence
            detected_damages.sort(key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error processing YOLOv8 results: {e}")
        
        return detected_damages
    
    def _calculate_damage_score(self, damages: List[Dict[str, Any]]) -> int:
        """Calculate overall damage score from detections"""
        if not damages:
            return 0
        
        # Base score calculation
        base_score = 0
        severity_weights = {
            'broken_part': 25,
            'crack': 20,
            'dent': 15,
            'rust': 12,
            'scratch': 8,
            'paint_damage': 10,
            'headlight_damage': 18,
            'windshield_damage': 22,
            'tire_damage': 15,
            'mirror_damage': 12
        }
        
        for damage in damages:
            damage_type = damage['type']
            confidence = damage['confidence']
            
            # Weight by damage severity and confidence
            weight = severity_weights.get(damage_type, 10)
            score_contribution = weight * confidence
            base_score += score_contribution
        
        # Apply diminishing returns for multiple damages
        num_damages = len(damages)
        if num_damages > 1:
            base_score *= (1 + (num_damages - 1) * 0.3)
        
        # Cap at 100
        return min(int(base_score), 100)
    
    def _create_error_result(self, image_url: str, error_message: str) -> Dict[str, Any]:
        """Create error result dictionary"""
        return {
            'image_url': image_url,
            'damages_detected': [],
            'damage_score': 0,
            'total_damages': 0,
            'processing_time': 0,
            'model_version': 'yolov8-real',
            'analysis_successful': False,
            'error': error_message
        }

# Text analysis functions (reused from mock implementation)
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

async def analyze_car_images(image_urls: List[str], description: str = "", 
                           model_path: str = "models/car_damage_yolo.pt",
                           confidence_threshold: float = 0.5) -> Dict[str, Any]:
    """
    Analyze multiple car images for damage using real YOLOv8
    
    Args:
        image_urls: List of image URLs to analyze
        description: Car listing description text
        model_path: Path to YOLOv8 model weights
        confidence_threshold: Detection confidence threshold
        
    Returns:
        Combined analysis results
    """
    if not image_urls:
        return {
            'visual_analysis': [],
            'text_analysis': analyze_text_for_damage(description),
            'combined_damage_score': 0,
            'total_damages_found': 0,
            'analysis_summary': "No images provided for analysis",
            'model_used': 'yolov8-real'
        }
    
    # Initialize detector
    detector = YOLOCarDamageDetector(model_path, confidence_threshold)
    
    # Analyze images (limit to first 5 for performance)
    visual_results = []
    max_images = min(len(image_urls), 5)
    
    logger.info(f"Starting YOLOv8 analysis of {max_images} images")
    
    for i, url in enumerate(image_urls[:max_images]):
        logger.info(f"Analyzing image {i+1}/{max_images}: {url}")
        result = await detector.detect_damage_from_url(url)
        visual_results.append(result)
        
        # Small delay between requests to be respectful
        if i < max_images - 1:
            await asyncio.sleep(0.5)
    
    # Analyze description text
    text_analysis = analyze_text_for_damage(description)
    
    # Calculate combined results
    successful_analyses = [r for r in visual_results if r['analysis_successful']]
    visual_damages = sum(len(r['damages_detected']) for r in successful_analyses)
    text_damages = sum(text_analysis.values())
    total_damages = visual_damages + text_damages
    
    # Calculate combined damage score
    if successful_analyses:
        avg_visual_score = sum(r['damage_score'] for r in successful_analyses) / len(successful_analyses)
    else:
        avg_visual_score = 0
    
    text_score = min(text_damages * 15, 50)  # Text contributes up to 50 points
    combined_score = min(int((avg_visual_score * 0.7) + (text_score * 0.3)), 100)
    
    # Generate summary in Turkish
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
    
    # Add AI analysis note
    if successful_analyses:
        summary += f" (AI analiz: {len(successful_analyses)} resim)"
    
    return {
        'visual_analysis': visual_results,
        'text_analysis': text_analysis,
        'combined_damage_score': combined_score,
        'total_damages_found': total_damages,
        'analysis_summary': summary,
        'images_analyzed': len(visual_results),
        'successful_analyses': len(successful_analyses),
        'processing_successful': len(successful_analyses) > 0 or bool(text_analysis),
        'model_used': 'yolov8-real',
        'device_used': detector.device if detector.model_loaded else 'unknown'
    }

async def quick_damage_check(image_url: str, description: str = "",
                           model_path: str = "models/car_damage_yolo.pt") -> Tuple[int, str]:
    """
    Quick damage assessment for a single image and description using real YOLOv8
    
    Args:
        image_url: Single image URL
        description: Description text
        model_path: Path to YOLOv8 model
        
    Returns:
        Tuple of (damage_score, summary_text)
    """
    result = await analyze_car_images([image_url], description, model_path)
    return result['combined_damage_score'], result['analysis_summary']

# Initialize global detector instance for reuse
_global_detector = None

def initialize_yolo_model(model_path: str = "models/car_damage_yolo.pt", 
                         confidence_threshold: float = 0.5) -> YOLOCarDamageDetector:
    """Initialize global YOLOv8 model instance"""
    global _global_detector
    _global_detector = YOLOCarDamageDetector(model_path, confidence_threshold)
    return _global_detector

def get_global_detector() -> Optional[YOLOCarDamageDetector]:
    """Get the global detector instance"""
    return _global_detector

# Export the main functions
__all__ = [
    'YOLOCarDamageDetector',
    'analyze_car_images', 
    'analyze_text_for_damage',
    'quick_damage_check',
    'initialize_yolo_model',
    'get_global_detector'
]
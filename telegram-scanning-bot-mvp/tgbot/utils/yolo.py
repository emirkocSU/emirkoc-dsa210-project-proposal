"""
YOLOv8 Car Damage Detection Module.
Handles loading YOLOv8 model and performing damage detection on car images.
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO

from config import config

logger = logging.getLogger(__name__)

class CarDamageDetector:
    """YOLOv8-based car damage detection system."""
    
    def __init__(self):
        self.model = None
        self.is_loaded = False
        self.damage_classes = {
            0: "dent",
            1: "scratch", 
            2: "crack",
            3: "rust",
            4: "broken_part",
            5: "paint_damage"
        }
        
    async def load_model(self) -> bool:
        """Load YOLOv8 model asynchronously."""
        try:
            # Check if model file exists
            model_path = Path(config.YOLO_WEIGHTS_PATH)
            if not model_path.exists():
                logger.warning(f"YOLO model not found at {model_path}")
                logger.info("Damage detection will be disabled")
                return False
            
            # Load model in executor to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, self._load_model_sync, str(model_path)
            )
            
            if self.model:
                self.is_loaded = True
                logger.info(f"YOLOv8 model loaded successfully from {model_path}")
                return True
            else:
                logger.error("Failed to load YOLOv8 model")
                return False
                
        except Exception as e:
            logger.error(f"Error loading YOLOv8 model: {e}")
            return False
    
    def _load_model_sync(self, model_path: str):
        """Synchronous model loading."""
        try:
            from ultralytics import YOLO
            return YOLO(model_path)
        except ImportError:
            logger.error("ultralytics not installed. Install with: pip install ultralytics")
            return None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    async def detect_damage(self, image_urls: List[str]) -> Dict[str, Any]:
        """
        Detect car damage from a list of image URLs.
        Returns damage analysis results.
        """
        if not self.is_loaded:
            logger.warning("YOLO model not loaded, skipping damage detection")
            return {
                "damage_found": False,
                "damage_score": 0,
                "damage_types": [],
                "damage_count": 0,
                "analysis_available": False,
                "error": "Model not available"
            }
        
        try:
            # Limit number of images to process
            limited_urls = image_urls[:config.YOLO_MAX_IMAGES]
            
            all_detections = []
            processed_images = 0
            
            for url in limited_urls:
                try:
                    # Download and process image
                    image_data = await self._download_image(url)
                    if image_data:
                        detections = await self._process_image(image_data)
                        all_detections.extend(detections)
                        processed_images += 1
                except Exception as e:
                    logger.warning(f"Failed to process image {url}: {e}")
                    continue
            
            # Analyze all detections
            analysis = self._analyze_detections(all_detections)
            analysis["processed_images"] = processed_images
            analysis["total_images"] = len(limited_urls)
            analysis["analysis_available"] = True
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in damage detection: {e}")
            return {
                "damage_found": False,
                "damage_score": 0,
                "damage_types": [],
                "damage_count": 0,
                "analysis_available": False,
                "error": str(e)
            }
    
    async def _download_image(self, url: str) -> Optional[np.ndarray]:
        """Download image from URL and convert to numpy array."""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, requests.get, url, {"timeout": 10}
            )
            
            if response.status_code == 200:
                # Convert to PIL Image then to numpy array
                image = Image.open(BytesIO(response.content))
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                # Convert to numpy array
                image_array = np.array(image)
                return image_array
            else:
                logger.warning(f"Failed to download image: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"Error downloading image from {url}: {e}")
            return None
    
    async def _process_image(self, image_array: np.ndarray) -> List[Dict[str, Any]]:
        """Process image with YOLO model and return detections."""
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self._run_inference, image_array
            )
            
            detections = []
            if results and len(results) > 0:
                for result in results:
                    if hasattr(result, 'boxes') and result.boxes is not None:
                        boxes = result.boxes
                        for i in range(len(boxes)):
                            confidence = float(boxes.conf[i])
                            if confidence >= config.YOLO_CONFIDENCE_THRESHOLD:
                                class_id = int(boxes.cls[i])
                                damage_type = self.damage_classes.get(class_id, "unknown")
                                
                                detections.append({
                                    "damage_type": damage_type,
                                    "confidence": confidence,
                                    "class_id": class_id,
                                    "bbox": boxes.xyxy[i].tolist() if hasattr(boxes, 'xyxy') else None
                                })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error processing image with YOLO: {e}")
            return []
    
    def _run_inference(self, image_array: np.ndarray):
        """Run YOLO inference synchronously."""
        try:
            return self.model.predict(image_array, verbose=False)
        except Exception as e:
            logger.error(f"YOLO inference error: {e}")
            return None
    
    def _analyze_detections(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze all detections and compute damage score."""
        if not detections:
            return {
                "damage_found": False,
                "damage_score": 0,
                "damage_types": [],
                "damage_count": 0,
                "severity": "none"
            }
        
        # Count damage types
        damage_counts = {}
        total_confidence = 0
        
        for detection in detections:
            damage_type = detection["damage_type"]
            confidence = detection["confidence"]
            
            if damage_type not in damage_counts:
                damage_counts[damage_type] = 0
            damage_counts[damage_type] += 1
            total_confidence += confidence
        
        # Calculate damage score (0-100)
        damage_count = len(detections)
        avg_confidence = total_confidence / damage_count if damage_count > 0 else 0
        
        # Score based on number of damages and confidence
        base_score = min(damage_count * 15, 60)  # Max 60 from count
        confidence_bonus = int(avg_confidence * 40)  # Max 40 from confidence
        damage_score = min(base_score + confidence_bonus, 100)
        
        # Determine severity
        if damage_score < 20:
            severity = "minimal"
        elif damage_score < 40:
            severity = "low"
        elif damage_score < 70:
            severity = "moderate"
        else:
            severity = "high"
        
        return {
            "damage_found": True,
            "damage_score": damage_score,
            "damage_types": list(damage_counts.keys()),
            "damage_counts": damage_counts,
            "damage_count": damage_count,
            "severity": severity,
            "avg_confidence": round(avg_confidence, 2)
        }
    
    async def analyze_text_for_damage(self, description: str) -> Dict[str, Any]:
        """Analyze listing description for damage keywords."""
        if not description:
            return {"text_damage_found": False, "damage_keywords": []}
        
        # Turkish damage keywords
        damage_keywords = [
            "hasar", "kaza", "çarpma", "çizik", "göçük", "boya", "boyalı",
            "değişen", "değişmiş", "tramer", "sigorta", "onarım", "tamir",
            "hasarlı", "kazalı", "çarpık", "ezik", "kırık", "çatlak",
            "pas", "korozyon", "delik", "yamuk"
        ]
        
        description_lower = description.lower()
        found_keywords = []
        
        for keyword in damage_keywords:
            if keyword in description_lower:
                found_keywords.append(keyword)
        
        # Calculate text damage score
        text_score = min(len(found_keywords) * 10, 50)  # Max 50 from text
        
        return {
            "text_damage_found": len(found_keywords) > 0,
            "damage_keywords": found_keywords,
            "text_damage_score": text_score
        }
    
    def combine_damage_analysis(self, yolo_results: Dict[str, Any], 
                              text_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine YOLO and text analysis results."""
        combined_score = yolo_results.get("damage_score", 0) + text_results.get("text_damage_score", 0)
        combined_score = min(combined_score, 100)
        
        # Determine final severity
        if combined_score < 20:
            final_severity = "minimal"
        elif combined_score < 40:
            final_severity = "low"
        elif combined_score < 70:
            final_severity = "moderate"
        else:
            final_severity = "high"
        
        return {
            "final_damage_score": combined_score,
            "final_severity": final_severity,
            "visual_damage": yolo_results.get("damage_found", False),
            "text_damage": text_results.get("text_damage_found", False),
            "damage_types": yolo_results.get("damage_types", []),
            "damage_keywords": text_results.get("damage_keywords", []),
            "analysis_complete": yolo_results.get("analysis_available", False)
        }

# Global damage detector instance
damage_detector = CarDamageDetector()

async def init_damage_detector():
    """Initialize the damage detector."""
    success = await damage_detector.load_model()
    if success:
        logger.info("Car damage detection system initialized")
    else:
        logger.warning("Car damage detection system not available")
    return success
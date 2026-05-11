import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class FaceEngine:
    def __init__(self):
        # Initialize InsightFace
        # name=settings.FACE_MODEL (e.g., 'buffalo_l')
        # providers=['CPUExecutionProvider'] because no GPU
        self.app = FaceAnalysis(
            name=settings.FACE_MODEL,
            root='models',
            providers=['CPUExecutionProvider']
        )
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
    def extract_embedding(self, image_bytes: bytes):
        """
        Extract face embedding from image bytes.
        Returns: (embedding, quality_score) or (None, None)
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return None, None
            
        # Detect and analyze faces
        faces = self.app.get(img)
        
        if not faces:
            logger.info("No face detected in image")
            return None, None
            
        if len(faces) > 1:
            logger.info(f"Multiple faces detected: {len(faces)}")
            # For enrollment, we usually expect exactly one face
            # But we return the first one and the caller can decide
            
        face = faces[0]
        
        # quality_score can be derived from detection score or other metrics
        # InsightFace's face.det_score is the detection confidence
        quality_score = float(face.det_score)
        embedding = face.normed_embedding
        
        return embedding, quality_score

# Singleton instance
face_engine = None

def get_face_engine():
    global face_engine
    if face_engine is None:
        face_engine = FaceEngine()
    return face_engine

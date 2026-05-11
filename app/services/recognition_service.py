from sqlalchemy.ext.asyncio import AsyncSession
from app.core.face_engine import get_face_engine
from app.core.matcher import FaceMatcher
from app.models.recognition_result import RecognitionResult
from app.config import settings
from fastapi import HTTPException
import time
from sqlalchemy.sql import func
from app.core.adaptive_router import AdaptiveRouter
from app.tasks.recognition_task import process_recognition_task

class RecognitionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = get_face_engine()
        self.matcher = FaceMatcher(db)

    async def recognize_adaptive(self, image_bytes: bytes, user_id: str):
        """
        Entry point utama yang memutuskan apakah akan diproses realtime atau queue.
        """
        if AdaptiveRouter.should_use_queue():
            return await self.queue_recognition(image_bytes, user_id)
        else:
            return await self.recognize_realtime(image_bytes, user_id)

    async def recognize_realtime(self, image_bytes: bytes, user_id: str = None):
        start_time = time.time()
        
        # 1. Extract embedding
        embedding, quality_score = self.engine.extract_embedding(image_bytes)
        
        if embedding is None:
            raise HTTPException(status_code=400, detail="No face detected in image")
            
        # 2. Find match (Identification or Verification)
        match = await self.matcher.find_nearest(
            embedding, 
            threshold=settings.SIMILARITY_THRESHOLD,
            user_id=user_id
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 3. Save result
        result = RecognitionResult(
            matched_user_id=match["user_id"] if match else None,
            similarity=match["similarity"] if match else None,
            mode="realtime",
            status="success" if match else "no_match",
            processed_at=func.now()
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        
        return {
            "mode": "realtime",
            "matched": match is not None,
            "user_id": match["user_id"] if match else None,
            "similarity": round(match["similarity"], 4) if match else 0.0,
            "latency_ms": latency_ms
        }

    async def queue_recognition(self, image_bytes: bytes, user_id: str):
        """
        Mendaftarkan request ke antrean Celery.
        """
        # 1. Simpan record 'pending' ke DB
        result = RecognitionResult(
            mode="queued",
            status="pending"
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        
        # 2. Kirim task ke Celery
        # Konversi bytes ke hex string agar bisa di-serialize ke JSON
        image_hex = image_bytes.hex()
        
        task = process_recognition_task.delay(
            image_hex, 
            user_id, 
            str(result.id)
        )
        
        # 3. Update job_id di record
        result.job_id = task.id
        await self.db.commit()
        
        return {
            "mode": "queued",
            "job_id": task.id,
            "status_url": f"/jobs/{task.id}",
            "message": "Server sibuk, proses diantrekan"
        }

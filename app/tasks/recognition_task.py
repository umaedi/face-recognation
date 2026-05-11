import asyncio
from app.tasks.celery_app import celery_app
from app.core.face_engine import get_face_engine
from app.core.matcher import FaceMatcher
from app.dependencies import AsyncSessionLocal
from app.models.recognition_result import RecognitionResult
from app.config import settings
import logging
from sqlalchemy import update
from sqlalchemy.sql import func
import uuid

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, name="app.tasks.recognition_task.process_recognition_task")
def process_recognition_task(self, image_bytes_hex: str, user_id: str, result_db_id: str):
    """
    Task background untuk memproses pengenalan wajah.
    image_bytes_hex dikirim sebagai string hex karena Celery JSON serializer tidak mendukung bytes secara default.
    """
    return asyncio.run(_run_recognition_logic(image_bytes_hex, user_id, result_db_id))

async def _run_recognition_logic(image_bytes_hex: str, user_id: str, result_db_id: str):
    image_bytes = bytes.fromhex(image_bytes_hex)
    
    async with AsyncSessionLocal() as db:
        try:
            engine = get_face_engine()
            matcher = FaceMatcher(db)
            
            # 1. Extract embedding
            embedding, quality_score = engine.extract_embedding(image_bytes)
            
            if embedding is None:
                await _update_result(db, result_db_id, status="failed")
                return {"status": "failed", "reason": "no_face_detected"}
                
            # 2. Match
            match = await matcher.find_nearest(
                embedding, 
                threshold=settings.SIMILARITY_THRESHOLD,
                user_id=user_id
            )
            
            # 3. Update Result in DB
            status = "success" if match else "no_match"
            await _update_result(
                db, 
                result_db_id, 
                status=status,
                matched_user_id=match["user_id"] if match else None,
                similarity=match["similarity"] if match else None
            )
            
            return {
                "status": status,
                "matched": match is not None,
                "user_id": match["user_id"] if match else None,
                "similarity": match["similarity"] if match else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error in recognition task: {str(e)}")
            await _update_result(db, result_db_id, status="failed")
            raise e

async def _update_result(db, result_id, **kwargs):
    from sqlalchemy import update
    stmt = (
        update(RecognitionResult)
        .where(RecognitionResult.id == uuid.UUID(result_id))
        .values(**kwargs, processed_at=func.now())
    )
    await db.execute(stmt)
    await db.commit()

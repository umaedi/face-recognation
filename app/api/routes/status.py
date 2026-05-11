from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.recognition_result import RecognitionResult

router = APIRouter()

@router.get("/{job_id}")
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    query = select(RecognitionResult).where(RecognitionResult.job_id == job_id)
    result = await db.execute(query)
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "job_id": record.job_id,
        "status": record.status,
        "matched": record.matched_user_id is not None,
        "user_id": str(record.matched_user_id) if record.matched_user_id else None,
        "similarity": round(record.similarity, 4) if record.similarity else 0.0,
        "processed_at": record.processed_at,
        "mode": record.mode
    }

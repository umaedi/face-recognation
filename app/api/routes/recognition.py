from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.services.recognition_service import RecognitionService
from app.limiter import limiter

router = APIRouter()

@router.post("")
@limiter.limit("5/minute")
async def recognize_face(
    request: Request,
    user_id: str = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    service = RecognitionService(db)
    image_bytes = await image.read()
    
    return await service.recognize_adaptive(image_bytes, user_id=user_id)

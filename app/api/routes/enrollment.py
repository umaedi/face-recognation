from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.services.enrollment_service import EnrollmentService
from typing import List
import uuid

router = APIRouter()

@router.post("/enroll", status_code=201)
async def enroll_face(
    user_id: str = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    service = EnrollmentService(db)
    image_bytes = await image.read()
    
    face = await service.enroll_face(user_id, image_bytes)
    
    return {
        "face_id": str(face.id),
        "user_id": str(face.user_id),
        "quality_score": round(face.quality_score, 2),
        "message": "Wajah berhasil didaftarkan"
    }

@router.get("/latest/{user_id}")
async def get_latest_face(user_id: str, db: AsyncSession = Depends(get_db)):
    service = EnrollmentService(db)
    result = await service.get_latest_face_url(user_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="No face data found for this user")
        
    return result

@router.get("/{user_id}")
async def list_faces(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = EnrollmentService(db)
    faces = await service.get_user_faces(user_id)
    
    return {
        "user_id": user_id,
        "total_faces": len(faces),
        "faces": [
            {
                "face_id": str(f.id),
                "quality_score": round(f.quality_score, 2),
                "created_at": f.created_at
            } for f in faces
        ]
    }

@router.delete("/{user_id}")
async def delete_all_faces(user_id: str, db: AsyncSession = Depends(get_db)):
    service = EnrollmentService(db)
    deleted_count = await service.delete_user_faces(user_id)
    
    return {
        "user_id": user_id,
        "deleted": deleted_count,
        "message": "Data wajah dihapus"
    }

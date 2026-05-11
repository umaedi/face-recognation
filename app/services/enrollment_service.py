from sqlalchemy.ext.asyncio import AsyncSession
from app.models.face import Face
from app.core.face_engine import get_face_engine
from app.config import settings
from fastapi import HTTPException
import uuid

from typing import Union

class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = get_face_engine()

    async def enroll_face(self, user_id: Union[str, uuid.UUID], image_bytes: bytes):
        # 1. Extract embedding
        embedding, quality_score = self.engine.extract_embedding(image_bytes)
        
        if embedding is None:
            raise HTTPException(status_code=400, detail="No face detected in image")
            
        # 2. Validate quality
        if quality_score < settings.MIN_QUALITY_SCORE:
            raise HTTPException(
                status_code=422, 
                detail=f"Face quality too low ({quality_score:.2f} < {settings.MIN_QUALITY_SCORE})"
            )
            
        # 3. Rolling Enrollment Logic (Max 3 faces)
        from sqlalchemy import select, delete, desc
        u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        # Count existing faces
        query_count = select(Face).where(Face.user_id == u_id).order_by(Face.created_at.asc())
        result = await self.db.execute(query_count)
        existing_faces = result.scalars().all()
        
        if len(existing_faces) >= 3:
            # Delete the oldest one
            oldest_face = existing_faces[0]
            await self.db.delete(oldest_face)
            await self.db.flush() # Ensure it's deleted before inserting new one
            
        # 4. Save to DB
        face = Face(
            user_id=u_id,
            embedding=embedding.tolist(),
            quality_score=quality_score
        )
        
        self.db.add(face)
        await self.db.commit()
        await self.db.refresh(face)
        
        return face

    async def get_user_faces(self, user_id: Union[str, uuid.UUID]):
        from sqlalchemy import select
        u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        query = select(Face).where(Face.user_id == u_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_user_faces(self, user_id: Union[str, uuid.UUID]):
        from sqlalchemy import delete
        u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        query = delete(Face).where(Face.user_id == u_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount

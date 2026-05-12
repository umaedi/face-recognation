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
            
        from app.services.storage_service import storage_service
        
        # 3. Rolling Enrollment Logic (Max 3 faces)
        from sqlalchemy import select, delete, desc
        u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        # Count existing faces
        query_faces = select(Face).where(Face.user_id == u_id).order_by(Face.created_at.asc())
        result = await self.db.execute(query_faces)
        existing_faces = result.scalars().all()
        
        # LOGIKA PENGHEMATAN STORAGE:
        # Hapus SEMUA foto lama di Minio milik user ini sebelum upload yang baru
        # (Kita hanya ingin menyimpan 1 foto terakhir di Minio)
        for old_face in existing_faces:
            if old_face.image_path:
                await storage_service.delete_image(old_face.image_path)
                old_face.image_path = None # Kosongkan path di DB untuk record lama
        
        # Hapus record tertua jika sudah 3
        if len(existing_faces) >= 3:
            oldest_face = existing_faces[0]
            await self.db.delete(oldest_face)
            await self.db.flush() 
            
        # 4. Upload to Minio (Foto Terbaru)
        image_path = await storage_service.upload_image(image_bytes, str(u_id))
        
        # 5. Save to DB
        face = Face(
            user_id=u_id,
            embedding=embedding.tolist(),
            quality_score=quality_score,
            image_path=image_path
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

    async def get_latest_face_url(self, user_id: Union[str, uuid.UUID]):
        from sqlalchemy import select, desc
        from app.services.storage_service import storage_service
        u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        query = select(Face).where(Face.user_id == u_id).order_by(desc(Face.created_at)).limit(1)
        result = await self.db.execute(query)
        face = result.scalars().first()
        
        if not face or not face.image_path:
            return None
            
        # Gunakan URL publik yang di-proxy lewat endpoint /stream/
        filename = face.image_path.split('/')[-1]
        public_url = f"{settings.BASE_PUBLIC_URL}/stream/{filename}"
            
        return {
            "user_id": str(u_id),
            "face_id": str(face.id),
            "image_url": public_url,
            "created_at": face.created_at
        }

    async def delete_user_faces(self, user_id: Union[str, uuid.UUID]):
        from sqlalchemy import delete
        u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        query = delete(Face).where(Face.user_id == u_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount

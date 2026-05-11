from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.face import Face
import numpy as np

class FaceMatcher:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_nearest(self, embedding: np.ndarray, threshold: float = 0.6, user_id: str = None):
        """
        Find the nearest face in the database using pgvector cosine distance.
        If user_id is provided, it performs 1:1 verification.
        """
        embedding_list = embedding.tolist()
        
        # Base query
        query_str = """
            SELECT user_id, 1 - (embedding <=> :embedding) as similarity
            FROM faces
            WHERE is_active = True
        """
        
        params = {
            "embedding": str(embedding_list),
            "threshold": threshold
        }
        
        # Add user_id filter if provided
        if user_id:
            query_str += " AND user_id = :user_id"
            params["user_id"] = user_id
            
        query_str += " AND 1 - (embedding <=> :embedding) >= :threshold"
        query_str += " ORDER BY embedding <=> :embedding LIMIT 1"
        
        result = await self.db.execute(text(query_str), params)
        
        row = result.fetchone()
        if row:
            return {
                "user_id": str(row[0]),
                "similarity": float(row[1])
            }
            
        return None

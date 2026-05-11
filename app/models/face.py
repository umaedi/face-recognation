import uuid
from sqlalchemy import Column, UUID, Boolean, DateTime, Float, Text, Index
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Face(Base):
    __tablename__ = "faces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    embedding = Column(Vector(512), nullable=False)
    image_path = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_faces_user_id", "user_id"),
        # IVFFlat index will be added via migration as it requires specific parameters
    )

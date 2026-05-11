import uuid
from sqlalchemy import Column, UUID, DateTime, Float, Text, String, Index
from sqlalchemy.sql import func
from app.models.face import Base

class RecognitionResult(Base):
    __tablename__ = "recognition_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String(100), unique=True, nullable=True)
    matched_user_id = Column(UUID(as_uuid=True), nullable=True)
    similarity = Column(Float, nullable=True)
    mode = Column(String(20), nullable=False) # 'realtime' | 'queued'
    status = Column(String(20), server_default="pending") # pending | success | failed | no_match
    input_image_path = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_rec_results_job_id", "job_id"),
        Index("idx_rec_results_matched_user", "matched_user_id"),
    )

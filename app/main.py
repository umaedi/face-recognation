from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import enrollment, recognition, status
from app.config import settings
from app.limiter import limiter

app = FastAPI(
    title="Face Recognition System",
    description="Python-based face recognition with adaptive routing and PostgreSQL + pgvector",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from app.models import Base, Face, RecognitionResult
from app.dependencies import engine

@app.on_event("startup")
async def startup():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {
        "message": "Face Recognition System API",
        "status": "online",
        "environment": settings.APP_ENV
    }

# Include routers
app.include_router(enrollment.router, prefix="/faces", tags=["Enrollment"])
app.include_router(recognition.router, prefix="/recognize", tags=["Recognition"])
app.include_router(status.router, prefix="/jobs", tags=["Status"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

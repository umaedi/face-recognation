from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from app.services.storage_service import storage_service
import io

router = APIRouter()

@router.get("/{filename}")
async def stream_image(filename: str):
    """
    Proxy endpoint to stream images from Minio to the public.
    """
    object_name = f"face_recognation/{filename}"
    image_bytes = await storage_service.get_image_bytes(object_name)
    
    if not image_bytes:
        raise HTTPException(status_code=404, detail="Image not found")
        
    return Response(content=image_bytes, media_type="image/jpeg")

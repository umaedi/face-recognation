import aioboto3
import uuid
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket = settings.AWS_BUCKET
        self.endpoint = settings.AWS_ENDPOINT
        self.access_key = settings.AWS_ACCESS_KEY_ID
        self.secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.region = settings.AWS_DEFAULT_REGION

    async def upload_image(self, image_bytes: bytes, user_id: str) -> str:
        """
        Upload image to Minio and return the object name/path.
        Path format: face_recognation/{uuid}.jpg
        """
        file_extension = "jpg"
        object_name = f"face_recognation/{uuid.uuid4()}.{file_extension}"
        
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            ) as s3:
                await s3.put_object(
                    Bucket=self.bucket,
                    Key=object_name,
                    Body=image_bytes,
                    ContentType='image/jpeg'
                )
                logger.info(f"Successfully uploaded image to {object_name}")
                return object_name
        except Exception as e:
            logger.error(f"Failed to upload image to Minio: {str(e)}")
            return None

    async def delete_image(self, object_name: str):
        """
        Delete an image from Minio.
        """
        if not object_name:
            return
            
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            ) as s3:
                await s3.delete_object(Bucket=self.bucket, Key=object_name)
                logger.info(f"Successfully deleted image {object_name}")
        except Exception as e:
            logger.error(f"Failed to delete image from Minio: {str(e)}")

    async def get_image_bytes(self, object_name: str) -> bytes:
        """
        Get image bytes from Minio.
        """
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            ) as s3:
                response = await s3.get_object(Bucket=self.bucket, Key=object_name)
                async with response['Body'] as stream:
                    return await stream.read()
        except Exception as e:
            logger.error(f"Failed to get image from Minio: {str(e)}")
            return None

    def get_presigned_url(self, object_name: str, expiration=3600) -> str:
        """
        Note: Generating presigned URL usually needs to be done via a client.
        For Minio inside private network, we might need to handle public vs private endpoint.
        """
        # Untuk sementara kita return path aslinya, 
        # atau bisa diintegrasikan dengan proxy URL jika Minio tidak publik.
        return f"{self.endpoint}/{self.bucket}/{object_name}"

# Singleton
storage_service = StorageService()

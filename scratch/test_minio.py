import asyncio
import aioboto3
from app.config import settings

async def test_minio():
    print(f"--- Mengetes Koneksi Minio ---")
    print(f"Endpoint: {settings.AWS_ENDPOINT}")
    print(f"Bucket: {settings.AWS_BUCKET}")
    
    session = aioboto3.Session()
    try:
        async with session.client(
            's3',
            endpoint_url=settings.AWS_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION
        ) as s3:
            # 1. Cek koneksi dengan list buckets
            print("Mencoba list buckets...")
            response = await s3.list_buckets()
            print("Berhasil konek! Daftar bucket:", [b['Name'] for b in response['Buckets']])
            
            # 2. Cek apakah bucket target ada
            buckets = [b['Name'] for b in response['Buckets']]
            if settings.AWS_BUCKET not in buckets:
                print(f"Error: Bucket '{settings.AWS_BUCKET}' belum ada di Minio.")
                return

            # 3. Cek upload file kecil
            print(f"Mencoba upload file tes ke '{settings.AWS_BUCKET}/test_file.txt'...")
            await s3.put_object(
                Bucket=settings.AWS_BUCKET,
                Key="test_file.txt",
                Body=b"Koneksi Berhasil",
                ContentType='text/plain'
            )
            print("Upload berhasil!")
            
    except Exception as e:
        print(f"Gagal koneksi ke Minio: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_minio())

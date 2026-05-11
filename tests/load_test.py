import asyncio
import httpx
import time
import os

API_URL = "http://localhost:8000/recognize"
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
IMAGE_PATH = "tests/sample_face.jpg" # Pastikan file ini ada

async def send_request(client, i):
    files = {"image": open(IMAGE_PATH, "rb")}
    data = {"user_id": TEST_USER_ID}
    
    start = time.time()
    try:
        response = client.post(API_URL, data=data, files=files)
        latency = (time.time() - start) * 1000
        print(f"Req {i}: Status {response.status_code} | Mode: {response.json().get('mode')} | Latency: {latency:.2f}ms")
    except Exception as e:
        print(f"Req {i}: Failed | {e}")

async def run_load_test(num_requests=10):
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: {IMAGE_PATH} not found. Please provide a sample image for testing.")
        return

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [send_request(client, i) for i in range(num_requests)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("Starting load test...")
    asyncio.run(run_load_test(10))

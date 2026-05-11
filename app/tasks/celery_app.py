from celery import Celery
from app.config import settings

celery_app = Celery(
    "face_recognition",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL, # Menggunakan Upstash Redis untuk result backend juga
)

celery_app.conf.update(
    task_serializer            = "json",
    accept_content             = ["json"],
    result_serializer          = "json",
    result_expires             = 3600,
    # Shared server: hanya gunakan concurrency rendah agar tidak memonopoli CPU
    worker_concurrency         = 4,
    task_acks_late             = True,
    worker_prefetch_multiplier = 1,
    task_soft_time_limit       = 15,
    task_time_limit            = 20,
    task_routes                = {
        "app.tasks.recognition_task.process_recognition_task": {"queue": "recognition"},
    },
)

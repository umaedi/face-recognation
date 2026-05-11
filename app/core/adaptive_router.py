import psutil
from app.tasks.celery_app import celery_app
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class AdaptiveRouter:
    @staticmethod
    def get_cpu_usage() -> float:
        # interval=0.1 agar responsif tapi tidak memblokir lama
        return psutil.cpu_percent(interval=0.1)

    @staticmethod
    def get_queue_depth() -> int:
        """
        Mengecek jumlah task yang sedang antre di Redis.
        """
        try:
            with celery_app.pool.acquire(block=True) as conn:
                # Mengakses queue 'recognition' (sesuai config task_routes)
                queue = conn.default_channel.client.llen("recognition")
                return queue
        except Exception as e:
            logger.error(f"Error checking queue depth: {e}")
            return 0

    @classmethod
    def should_use_queue(cls) -> bool:
        cpu_usage = cls.get_cpu_usage()
        queue_depth = cls.get_queue_depth()
        
        is_busy = cpu_usage > settings.CPU_THRESHOLD or queue_depth > settings.QUEUE_THRESHOLD
        
        if is_busy:
            logger.info(f"Server BUSY (CPU: {cpu_usage}%, Queue: {queue_depth}). Routing to QUEUE.")
        
        return is_busy

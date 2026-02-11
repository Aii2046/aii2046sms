from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.CELERY_BROKER_URL, include=["app.worker.tasks"])

celery_app.conf.task_routes = {
    "app.worker.tasks.send_message_task": "send_queue",
    "app.worker.tasks.process_received_message_task": "receive_queue",
}

celery_app.conf.beat_schedule = {
    "check-heartbeat-every-interval": {
        "task": "app.worker.tasks.check_heartbeat_task",
        "schedule": settings.MONITOR_CHECK_INTERVAL,
    },
}

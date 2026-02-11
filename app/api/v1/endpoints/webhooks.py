from fastapi import APIRouter, Request, BackgroundTasks
from app.worker.tasks import process_received_message_task
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/feishu")
async def feishu_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # 1. URL Verification (Feishu requires this)
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}
    
    # 2. Event Handling
    # Ideally verify signature here using settings.FEISHU_ENCRYPT_KEY
    
    # 3. Async Process
    # We can use Celery for reliability
    logger.info(f"Dispatching task for event: {data.get('header', {}).get('event_id')}")
    try:
        task = process_received_message_task.delay(data)
        logger.info(f"Task dispatched successfully: {task.id}")
    except Exception as e:
        logger.error(f"Failed to dispatch task: {e}")
    
    return {"msg": "ok"}

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
    process_received_message_task.delay(data)
    
    return {"msg": "ok"}

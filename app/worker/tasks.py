from app.worker.celery_app import celery_app
from app.services.feishu_service import FeishuService
from app.core.database import AsyncSessionLocal
from app.services.message_service import MessageService
from app.schemas.message import MessageUpdate, MessageCreate
from app.core.config import settings
import asyncio
import logging
import redis.asyncio as redis
import time

logger = logging.getLogger(__name__)

@celery_app.task(name="app.worker.tasks.send_message_task")
def send_message_task(message_id: int, recipient_id: str, recipient_type: str, msg_type: str, content: dict):
    async def _process():
        async with AsyncSessionLocal() as db:
            try:
                # Update status to sending
                await MessageService.update_message(db, message_id, MessageUpdate(status="sending"))
                
                if recipient_type in ['email', 'feishu_chat', 'feishu_user']:
                    # Call Feishu API
                    response = await FeishuService.send_message(recipient_id, recipient_type, msg_type, content)
                    
                    if response.get("code") == 0:
                        feishu_msg_id = response.get("data", {}).get("message_id")
                        await MessageService.update_message(db, message_id, MessageUpdate(status="sent", feishu_message_id=feishu_msg_id))
                    else:
                        error_msg = f"Feishu Error: {response}"
                        await MessageService.update_message(db, message_id, MessageUpdate(status="failed", error_log=error_msg))
                else:
                    print('其它消息，暂不处理')
                    await MessageService.update_message(db, message_id, MessageUpdate(status="ignore"))
            except Exception as e:
                logger.exception(f"Task failed for message {message_id}")
                # We might want to re-acquire DB session if it failed during transaction? 
                # Ideally, if update_message fails, we are in trouble.
                # Here assuming simple failure logging.
                pass

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_process())
    loop.close()

@celery_app.task(name="app.worker.tasks.process_received_message_task")
def process_received_message_task(event_data: dict):
    # Process received webhook event
    # Logic: Parse event -> Save to DB -> Maybe reply?
    async def _process():
        async with AsyncSessionLocal() as db:
            # TODO: Implement receive logic
            pass
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_process())
    loop.close()

@celery_app.task(name="app.worker.tasks.check_heartbeat_task")
def check_heartbeat_task():
    async def create_and_send_alert(db, system_id: str, status: str):
        if not settings.MONITOR_ALERT_RECIPIENT_ID:
            logger.warning("No recipient configured for monitor alerts.")
            return

        msg = f"警告：{system_id} 心跳超时。" if status == "DOWN" else f"恢复：{system_id} 心跳正常。"
        
        # Add @mention if configured
        if settings.MONITOR_ALERT_AT_USER_ID:
            if settings.MONITOR_ALERT_AT_USER_ID == "all":
                msg += " <at user_id=\"all\">所有人</at>"
            else:
                msg += f" <at user_id=\"{settings.MONITOR_ALERT_AT_USER_ID}\"></at>"
                
        content = {"text": msg}
        
        message_in = MessageCreate(
            content=content,
            recipient_id=settings.MONITOR_ALERT_RECIPIENT_ID,
            recipient_type=settings.MONITOR_ALERT_RECIPIENT_TYPE,
            msg_type="text",
            sender="MonitorSystem",
            user_id=None
        )
        
        try:
            message = await MessageService.create_message(db, message_in)
            # Use delay to invoke the task
            send_message_task.delay(
                message.id, 
                message.recipient_id, 
                message.recipient_type, 
                message.msg_type, 
                message.content
            )
        except Exception as e:
            logger.error(f"Failed to create alert message: {e}")

    async def _process():
        redis_client = redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
        try:
            systems = await redis_client.smembers("Monitored_Systems")
            if not systems:
                return

            current_time = int(time.time())
            
            async with AsyncSessionLocal() as db:
                for system_id in systems:
                    heartbeat_key = f"SystemA_Heartbeat:{system_id}"
                    status_key = f"Monitor_Status:{system_id}"
                    fail_count_key = f"Monitor_Fail_Count:{system_id}"
                    
                    last_seen = await redis_client.get(heartbeat_key)
                    current_status = await redis_client.get(status_key) or "UP"
                    fail_count = int(await redis_client.get(fail_count_key) or 0)
                    
                    if not last_seen:
                        last_seen_time = 0
                    else:
                        last_seen_time = int(last_seen)
                    
                    # Check if timeout
                    is_timeout = (current_time - last_seen_time) > settings.MONITOR_HEARTBEAT_TIMEOUT
                    
                    if is_timeout:
                        fail_count += 1
                        await redis_client.set(fail_count_key, fail_count)
                        
                        if fail_count >= 3 and current_status == "UP":
                            await redis_client.set(status_key, "DOWN")
                            # Send Alert
                            await create_and_send_alert(db, system_id, "DOWN")
                            
                    else:
                        # Reset fail count if healthy
                        await redis_client.set(fail_count_key, 0)
                        
                        if current_status == "DOWN":
                            await redis_client.set(status_key, "UP")
                            # Send Recovery Alert
                            await create_and_send_alert(db, system_id, "UP")

        except Exception as e:
            logger.exception("Check heartbeat task failed")
        finally:
            await redis_client.close()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_process())
    loop.close()

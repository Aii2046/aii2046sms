from fastapi import APIRouter, HTTPException
from app.core.config import settings
import redis.asyncio as redis
import time

router = APIRouter()

@router.post("/heartbeat/{system_id}")
async def heartbeat(system_id: str):
    """
    Receive heartbeat from internal system A.
    """
    # Token verification is skipped as per requirements.
    
    # Connect to Redis
    # decode_responses=True ensures we get strings back, which is easier to work with
    redis_client = redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
    try:
        current_time = int(time.time())
        
        # Update heartbeat timestamp
        heartbeat_key = f"SystemA_Heartbeat:{system_id}"
        await redis_client.set(heartbeat_key, current_time)
        
        # Add to set of monitored systems to enable iteration during checks
        await redis_client.sadd("Monitored_Systems", system_id)
        
        return {
            "status": "received",
            "system_id": system_id,
            "timestamp": current_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record heartbeat: {str(e)}")
    finally:
        await redis_client.close()

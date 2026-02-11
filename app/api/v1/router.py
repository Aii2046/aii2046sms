from fastapi import APIRouter
from app.api.v1.endpoints import messages, webhooks, monitor

api_router = APIRouter()

api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(monitor.router, prefix="/monitor", tags=["monitor"])

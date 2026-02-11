from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.message import MessageCreate, MessageResponse, GroupBuyStatusRequest
from app.services.message_service import MessageService
from app.services.feishu_message_wrap import generate_group_buy_card
from app.worker.tasks import send_message_task

router = APIRouter()

@router.post("/send_tuangou_autorelease_status", response_model=MessageResponse)
async def send_tuangou_autorelease_status(request: GroupBuyStatusRequest, db: AsyncSession = Depends(get_db)):
    # 1. Generate Feishu Card
    items_dict = [item.model_dump() for item in request.items]
    card_content = generate_group_buy_card(
        items=items_dict,
        node_name=request.node_name,
        release_time=request.release_time,
        header_color=request.header_color,
        at_user_id=request.at_user_id
    )
    
    # 2. Create Message Object
    message_in = MessageCreate(
        content=card_content,
        recipient_id=request.recipient_id,
        recipient_type=request.recipient_type,
        msg_type="interactive",
        sender=request.sender,
        user_id=None # Or some system user id if needed
    )
    
    # 3. Save to DB
    message = await MessageService.create_message(db, message_in)
    
    # 4. Trigger Async Task
    send_message_task.delay(
        message.id, 
        message.recipient_id, 
        message.recipient_type, 
        message.msg_type, 
        message.content
    )
    
    return message

@router.post("/send", response_model=MessageResponse)
async def send_message(message_in: MessageCreate, db: AsyncSession = Depends(get_db)):
    # 1. Create DB record (Pending)
    message = await MessageService.create_message(db, message_in)
    
    # 2. Trigger Async Task
    send_message_task.delay(
        message.id, 
        message.recipient_id, 
        message.recipient_type, 
        message.msg_type, 
        message.content
    )
    
    return message

@router.get("/", response_model=list[MessageResponse])
async def read_messages(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    messages = await MessageService.get_messages(db, skip=skip, limit=limit)
    return messages

@router.get("/{message_id}", response_model=MessageResponse)
async def read_message(message_id: int, db: AsyncSession = Depends(get_db)):
    message = await MessageService.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate

class MessageService:
    @staticmethod
    async def create_message(db: AsyncSession, message_in: MessageCreate) -> Message:
        db_message = Message(**message_in.model_dump())
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    @staticmethod
    async def get_message(db: AsyncSession, message_id: int) -> Message:
        result = await db.execute(select(Message).filter(Message.id == message_id))
        return result.scalars().first()

    @staticmethod
    async def get_messages(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Message]:
        result = await db.execute(select(Message).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def update_message(db: AsyncSession, message_id: int, message_in: MessageUpdate) -> Message:
        db_message = await MessageService.get_message(db, message_id)
        if not db_message:
            return None
        
        update_data = message_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_message, key, value)
            
        await db.commit()
        await db.refresh(db_message)
        return db_message

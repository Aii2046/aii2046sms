from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(JSON, nullable=False)  # Stores the flexible content
    recipient_id = Column(String, index=True)
    recipient_type = Column(String, default="feishu_user")
    msg_type = Column(String, default="text")
    
    user_id = Column(String, nullable=True)
    sender = Column(String, nullable=False)
    
    status = Column(String, default="pending", index=True) # pending, sending, sent, failed, received
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    feishu_message_id = Column(String, nullable=True) # ID returned by Feishu
    error_log = Column(Text, nullable=True)

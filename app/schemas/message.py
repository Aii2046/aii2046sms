from pydantic import BaseModel
from typing import Optional, Any, Dict, List, Union
from datetime import datetime

class GroupBuyItem(BaseModel):
    name: str
    status: Union[bool, str]

class GroupBuyStatusRequest(BaseModel):
    items: List[GroupBuyItem]
    node_name: str = ""
    release_time: str = ""
    header_color: str = "blue"
    recipient_id: str
    recipient_type: str = "feishu_chat"
    sender: str
    at_user_id: Optional[str] = ""

class MessageBase(BaseModel):
    content: Dict[str, Any]
    recipient_id: str
    recipient_type: str = "feishu_user"
    msg_type: str = "text"
    user_id: Optional[str] = None
    sender: str

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    status: Optional[str] = None
    feishu_message_id: Optional[str] = None
    error_log: Optional[str] = None

class MessageResponse(MessageBase):
    id: int
    status: str
    user_id: Optional[str]
    sender: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    feishu_message_id: Optional[str] = None
    error_log: Optional[str] = None

    class Config:
        from_attributes = True

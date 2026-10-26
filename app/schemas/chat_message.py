from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatMessageBase(BaseModel):
    role: str  # mentor, ai
    content: str
    context_snapshot: Optional[str] = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageOut(ChatMessageBase):
    id: str
    session_id: Optional[str] = None
    session_plan_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Chat"


class ChatSessionUpdate(BaseModel):
    title: str


class ChatSessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    last_message: Optional[str] = None

    model_config = {"from_attributes": True}


class ChatSessionDetail(ChatSessionOut):
    messages: List[ChatMessageOut] = []


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    session_plan_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    model_used: str
    session_id: Optional[str] = None
    session_title: Optional[str] = None

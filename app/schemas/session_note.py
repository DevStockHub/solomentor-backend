from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionNoteBase(BaseModel):
    topic_id: Optional[str] = None
    content: str
    approach_used: Optional[str] = None
    student_struggle: Optional[str] = None
    effectiveness_rating: Optional[int] = None


class SessionNoteCreate(SessionNoteBase):
    pass


class SessionNoteUpdate(BaseModel):
    content: Optional[str] = None
    approach_used: Optional[str] = None
    student_struggle: Optional[str] = None
    effectiveness_rating: Optional[int] = None


class SessionNoteOut(SessionNoteBase):
    id: str
    session_plan_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
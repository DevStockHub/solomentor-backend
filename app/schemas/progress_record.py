from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProgressRecordBase(BaseModel):
    subject_id: str
    topic_id: Optional[str] = None
    session_plan_id: Optional[str] = None
    approach_used: Optional[str] = None
    struggle_noted: Optional[str] = None
    outcome: Optional[str] = None
    effectiveness_rating: Optional[int] = None


class ProgressRecordCreate(ProgressRecordBase):
    student_id: str


class ProgressRecordOut(ProgressRecordBase):
    id: str
    student_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
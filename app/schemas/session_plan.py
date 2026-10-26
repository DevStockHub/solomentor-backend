from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TopicBase(BaseModel):
    title: str
    order_index: int
    planned_minutes: int


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    order_index: Optional[int] = None
    planned_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    extra_minutes: Optional[int] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TopicOut(TopicBase):
    id: str
    session_plan_id: str
    actual_minutes: int
    extra_minutes: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionPlanBase(BaseModel):
    student_id: str
    subject_id: str
    title: str
    planned_minutes: Optional[int] = None


class SessionPlanCreate(SessionPlanBase):
    topics: List[TopicCreate] = []


class SessionPlanUpdate(BaseModel):
    title: Optional[str] = None
    planned_minutes: Optional[int] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class SessionPlanOut(SessionPlanBase):
    id: str
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    topics: List[TopicOut] = []

    model_config = {"from_attributes": True}
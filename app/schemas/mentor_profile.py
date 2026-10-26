from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MentorProfileBase(BaseModel):
    name: str
    email: Optional[str] = None
    subjects: Optional[str] = None
    bio: Optional[str] = None


class MentorProfileCreate(MentorProfileBase):
    pass


class MentorProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    subjects: Optional[str] = None
    bio: Optional[str] = None


class MentorProfileOut(MentorProfileBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
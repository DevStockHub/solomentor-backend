from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    name: str
    school: Optional[str] = None
    grade: Optional[str] = None
    contact: Optional[str] = None
    notes: Optional[str] = None


class StudentCreate(StudentBase):
    mentor_id: Optional[str] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    school: Optional[str] = None
    grade: Optional[str] = None
    contact: Optional[str] = None
    notes: Optional[str] = None


class StudentOut(StudentBase):
    id: str
    mentor_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class SubjectOut(SubjectBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
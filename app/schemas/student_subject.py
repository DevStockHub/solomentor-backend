from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudentSubjectBase(BaseModel):
    student_id: str
    subject_id: str


class StudentSubjectCreate(StudentSubjectBase):
    pass


class StudentSubjectOut(StudentSubjectBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
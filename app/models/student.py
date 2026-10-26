from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.mentor_profile import MentorProfile
    from app.models.student_subject import StudentSubject
    from app.models.session_plan import SessionPlan
    from app.models.progress_record import ProgressRecord


class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    mentor_id: Mapped[str] = mapped_column(String(36), ForeignKey("mentor_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    school: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "Upper Sixth"
    contact: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    mentor: Mapped["MentorProfile"] = relationship("MentorProfile", back_populates="students")
    subjects: Mapped[List["StudentSubject"]] = relationship("StudentSubject", back_populates="student", cascade="all, delete-orphan")
    session_plans: Mapped[List["SessionPlan"]] = relationship("SessionPlan", back_populates="student", cascade="all, delete-orphan")
    progress_records: Mapped[List["ProgressRecord"]] = relationship("ProgressRecord", back_populates="student", cascade="all, delete-orphan")

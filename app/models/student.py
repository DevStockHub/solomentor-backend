from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_uuid


class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    mentor_id: Mapped[str] = mapped_column(String(36), ForeignKey("mentor_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    school: Mapped[str] = mapped_column(String(255), nullable=True)
    grade: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., "Upper Sixth"
    contact: Mapped[str] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    mentor: Mapped["MentorProfile"] = relationship("MentorProfile", back_populates="students")
    subjects: Mapped[list["StudentSubject"]] = relationship("StudentSubject", back_populates="student", cascade="all, delete-orphan")
    session_plans: Mapped[list["SessionPlan"]] = relationship("SessionPlan", back_populates="student", cascade="all, delete-orphan")
    progress_records: Mapped[list["ProgressRecord"]] = relationship("ProgressRecord", back_populates="student", cascade="all, delete-orphan")
from sqlalchemy import String, DateTime, func, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_uuid


class SessionPlan(Base):
    __tablename__ = "session_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(36), ForeignKey("subjects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_minutes: Mapped[int] = mapped_column(Integer, nullable=True)  # total planned session time
    status: Mapped[str] = mapped_column(String(50), default="planned")  # planned, in_progress, completed, cancelled
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["Student"] = relationship("Student", back_populates="session_plans")
    subject: Mapped["Subject"] = relationship("Subject")
    topics: Mapped[list["Topic"]] = relationship("Topic", back_populates="session_plan", cascade="all, delete-orphan")
    session_notes: Mapped[list["SessionNote"]] = relationship("SessionNote", back_populates="session_plan", cascade="all, delete-orphan")
    chat_messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="session_plan", cascade="all, delete-orphan")
from sqlalchemy import String, DateTime, func, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_uuid


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("session_plans.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_minutes: Mapped[int] = mapped_column(Integer, default=0)
    extra_minutes: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, in_progress, completed, struggling
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session_plan: Mapped["SessionPlan"] = relationship("SessionPlan", back_populates="topics")
    session_notes: Mapped[list["SessionNote"]] = relationship("SessionNote", back_populates="topic", cascade="all, delete-orphan")
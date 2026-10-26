from sqlalchemy import String, DateTime, func, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_uuid


class SessionNote(Base):
    __tablename__ = "session_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("session_plans.id"), nullable=False)
    topic_id: Mapped[str] = mapped_column(String(36), ForeignKey("topics.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    approach_used: Mapped[str] = mapped_column(String(255), nullable=True)
    student_struggle: Mapped[str] = mapped_column(Text, nullable=True)
    effectiveness_rating: Mapped[int] = mapped_column(Integer, nullable=True)  # 1-5
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session_plan: Mapped["SessionPlan"] = relationship("SessionPlan", back_populates="session_notes")
    topic: Mapped["Topic"] = relationship("Topic", back_populates="session_notes")
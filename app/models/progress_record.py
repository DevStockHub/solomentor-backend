from sqlalchemy import String, DateTime, func, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_uuid


class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(36), ForeignKey("subjects.id"), nullable=False)
    topic_id: Mapped[str] = mapped_column(String(36), ForeignKey("topics.id"), nullable=True)
    session_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("session_plans.id"), nullable=True)
    approach_used: Mapped[str] = mapped_column(String(255), nullable=True)
    struggle_noted: Mapped[str] = mapped_column(Text, nullable=True)
    outcome: Mapped[str] = mapped_column(String(255), nullable=True)  # e.g., "mastered", "improved", "struggled"
    effectiveness_rating: Mapped[int] = mapped_column(Integer, nullable=True)  # 1-5
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["Student"] = relationship("Student", back_populates="progress_records")
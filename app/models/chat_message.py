from typing import Optional
from sqlalchemy import String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_uuid


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    session_plan_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("session_plans.id"), nullable=True, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # mentor, ai
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context_snapshot: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of context
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chat_session: Mapped[Optional["ChatSession"]] = relationship("ChatSession", back_populates="messages")
    session_plan: Mapped[Optional["SessionPlan"]] = relationship("SessionPlan", back_populates="chat_messages")

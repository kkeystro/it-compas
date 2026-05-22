from sqlalchemy import String, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.database import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    session_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    current_question_order: Mapped[int] = mapped_column(Integer, default=0)
    answers_json: Mapped[str] = mapped_column(Text, default="{}")
    finished: Mapped[bool] = mapped_column(Boolean, default=False)


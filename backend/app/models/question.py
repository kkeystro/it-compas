from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_text: Mapped[str] = mapped_column(String(500))
    question_type: Mapped[str] = mapped_column(
        String(20), default="single_choice"
    )  # single_choice | multiple_choice | scale
    order: Mapped[int] = mapped_column(Integer, default=0)

    options = relationship("AnswerOption", back_populates="question", order_by="AnswerOption.id")


class AnswerOption(Base):
    __tablename__ = "answer_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column(String(300))
    # weights is a JSON dict: {"frontend": 8, "backend": 2, ...}
    weights: Mapped[str] = mapped_column(JSON, default=dict)

    question = relationship("Question", back_populates="options")

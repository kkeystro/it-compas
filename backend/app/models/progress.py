from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    session_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    profession_id: Mapped[str] = mapped_column(String(50), ForeignKey("professions.id"))
    finished_quiz: Mapped[bool] = mapped_column(Boolean, default=False)

    completed_steps = relationship("CompletedStep", back_populates="session")


class CompletedStep(Base):
    __tablename__ = "completed_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), ForeignKey("user_progress.session_id"))
    step_id: Mapped[int] = mapped_column(Integer, ForeignKey("steps.id"))

    session = relationship("UserProgress", back_populates="completed_steps")

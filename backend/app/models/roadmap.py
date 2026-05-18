from sqlalchemy import String, Integer, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Stage(Base):
    __tablename__ = "stages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profession_id: Mapped[str] = mapped_column(String(50), ForeignKey("professions.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(500), default="")
    order: Mapped[int] = mapped_column(Integer, default=0)

    profession = relationship("Profession", back_populates="stages")
    steps = relationship("Step", back_populates="stage", order_by="Step.order")


class Step(Base):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stage_id: Mapped[int] = mapped_column(Integer, ForeignKey("stages.id"))
    title: Mapped[str] = mapped_column(String(300))
    step_type: Mapped[str] = mapped_column(
        String(30), default="theory"
    )  # theory | practice | milestone | hackathon | job_search
    resources: Mapped[str] = mapped_column(JSON, default=list)  # list of {title, url}
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=0)
    order: Mapped[int] = mapped_column(Integer, default=0)

    stage = relationship("Stage", back_populates="steps")

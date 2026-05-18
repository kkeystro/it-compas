from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Profession(Base):
    __tablename__ = "professions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. "frontend", "backend"
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500), default="")
    market_coefficient: Mapped[float] = mapped_column(Float, default=1.0)

    stages = relationship("Stage", back_populates="profession", order_by="Stage.order")

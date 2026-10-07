from sqlalchemy import ForeignKey, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    measurement_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    feature: Mapped["Feature"] = relationship(
        back_populates="measurement",
    )
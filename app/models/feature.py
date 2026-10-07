from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Feature(Base):
    __tablename__ = "features"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    file_id: Mapped[str] = mapped_column(
        ForeignKey("files.id"),
        nullable=False,
        index=True,
    )

    feature_index: Mapped[int] = mapped_column(
        nullable=False,
    )

    geometry_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    geometry: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    crs: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    properties: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    file: Mapped["File"] = relationship(
        back_populates="features",
    )

    measurement: Mapped["Measurement | None"] = relationship(
        back_populates="feature",
        cascade="all, delete-orphan",
        uselist=False,
    )
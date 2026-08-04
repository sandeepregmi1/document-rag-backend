from datetime import datetime, date, time
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    filename: Mapped[str] = mapped_column(String(255))

    filetype: Mapped[str] = mapped_column(String(20))

    chunk_strategy: Mapped[str] = mapped_column(String(50))

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    chunks = relationship(
        "ChunkMetadata",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class ChunkMetadata(Base):
    __tablename__ = "chunk_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id")
    )

    chunk_number: Mapped[int]

    vector_id: Mapped[str] = mapped_column(String(100))

    chunk_size: Mapped[int]

    document = relationship(
        "Document",
        back_populates="chunks",
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(String(255))

    date: Mapped[date] = mapped_column(Date)

    time: Mapped[time] = mapped_column(Time)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
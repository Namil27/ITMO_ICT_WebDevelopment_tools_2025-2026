import enum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class BookExchangeStatus(str, enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    EXCHANGED = "exchanged"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)

    exchange_status: Mapped[BookExchangeStatus] = mapped_column(
        Enum(
            BookExchangeStatus,
            name="book_exchange_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=BookExchangeStatus.AVAILABLE,
        server_default=BookExchangeStatus.AVAILABLE.value,
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    owner = relationship(
        "User",
        back_populates="books",
    )

    exchange_requests = relationship(
        "ExchangeRequest",
        back_populates="book",
        cascade="all, delete-orphan",
    )
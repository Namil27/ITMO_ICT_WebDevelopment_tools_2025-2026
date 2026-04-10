import enum

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ExchangeRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ExchangeRequest(Base):
    __tablename__ = "exchange_requests"

    __table_args__ = (
        CheckConstraint("requester_id <> owner_id", name="check_requester_not_owner"),
        UniqueConstraint(
            "book_id",
            "requester_id",
            "status",
            name="uq_book_requester_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    requester_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[ExchangeRequestStatus] = mapped_column(
        Enum(
            ExchangeRequestStatus,
            name="exchange_request_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=ExchangeRequestStatus.PENDING,
        server_default=ExchangeRequestStatus.PENDING.value,
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
    responded_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    book = relationship(
        "Book",
        back_populates="exchange_requests",
    )

    requester = relationship(
        "User",
        back_populates="sent_exchange_requests",
        foreign_keys=[requester_id],
    )

    owner = relationship(
        "User",
        back_populates="received_exchange_requests",
        foreign_keys=[owner_id],
    )
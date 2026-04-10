from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ExchangeRequestStatusSchema(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ExchangeRequestBase(BaseModel):
    message: str | None = None


class ExchangeRequestCreate(ExchangeRequestBase):
    book_id: int = Field(gt=0)


class ExchangeRequestUpdate(BaseModel):
    message: str | None = None
    status: ExchangeRequestStatusSchema | None = None
    responded_at: datetime | None = None


class ExchangeRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    requester_id: int
    owner_id: int
    message: str | None
    status: ExchangeRequestStatusSchema
    created_at: datetime
    updated_at: datetime
    responded_at: datetime | None


class ExchangeRequestShortRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    requester_id: int
    owner_id: int
    status: ExchangeRequestStatusSchema
    created_at: datetime


class ExchangeRequestWithBookRead(ExchangeRequestRead):
    book: "BookShortRead"


class ExchangeRequestWithUsersRead(ExchangeRequestRead):
    requester: "UserShortRead"
    owner: "UserShortRead"


class ExchangeRequestFullRead(ExchangeRequestRead):
    book: "BookShortRead"
    requester: "UserShortRead"
    owner: "UserShortRead"


from src.schemas.book import BookShortRead
from src.schemas.user import UserShortRead
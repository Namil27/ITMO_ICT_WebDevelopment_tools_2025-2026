from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class BookExchangeStatusSchema(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    EXCHANGED = "exchanged"


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    description: str | None = None
    genre: str | None = Field(default=None, max_length=100)
    condition: str | None = Field(default=None, max_length=50)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    genre: str | None = Field(default=None, max_length=100)
    condition: str | None = Field(default=None, max_length=50)
    exchange_status: BookExchangeStatusSchema | None = None
    is_available: bool | None = None


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    title: str
    author: str
    description: str | None
    genre: str | None
    condition: str | None
    exchange_status: BookExchangeStatusSchema
    is_available: bool
    created_at: datetime
    updated_at: datetime


class BookShortRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    title: str
    author: str
    exchange_status: BookExchangeStatusSchema
    is_available: bool


class BookWithOwnerRead(BookRead):
    owner: "UserShortRead"


class BookWithRequestsRead(BookRead):
    exchange_requests: list["ExchangeRequestShortRead"] = []


from src.schemas.user import UserShortRead
from src.schemas.exchange_request import ExchangeRequestShortRead
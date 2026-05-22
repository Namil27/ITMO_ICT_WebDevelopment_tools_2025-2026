from pydantic import BaseModel, Field, HttpUrl

from src.schemas.book import BookRead


class ParseBookRequest(BaseModel):
    url: HttpUrl
    owner_id: int = Field(gt=0)
    author: str | None = Field(default=None, max_length=255)
    genre: str | None = Field(default="parsed", max_length=100)
    condition: str | None = Field(default="unknown", max_length=50)


class ParseBookResponse(BaseModel):
    url: HttpUrl
    parsed_title: str
    book: BookRead


class ParseBookTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class ParseTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None

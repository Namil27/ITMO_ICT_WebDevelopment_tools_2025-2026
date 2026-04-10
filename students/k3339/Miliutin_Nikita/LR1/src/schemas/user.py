from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    bio: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=50)
    full_name: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    bio: str | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    full_name: str | None
    city: str | None
    bio: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserShortRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str | None
    city: str | None


class UserPasswordChange(BaseModel):
    old_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)


class UserWithBooksRead(UserRead):
    books: list["BookShortRead"] = []


from src.schemas.book import BookShortRead
from src.schemas.user import (
    UserCreate,
    UserPasswordChange,
    UserRead,
    UserShortRead,
    UserUpdate,
    UserWithBooksRead,
)
from src.schemas.book import (
    BookCreate,
    BookExchangeStatusSchema,
    BookRead,
    BookShortRead,
    BookUpdate,
    BookWithOwnerRead,
    BookWithRequestsRead,
)
from src.schemas.exchange_request import (
    ExchangeRequestCreate,
    ExchangeRequestFullRead,
    ExchangeRequestRead,
    ExchangeRequestShortRead,
    ExchangeRequestStatusSchema,
    ExchangeRequestUpdate,
    ExchangeRequestWithBookRead,
    ExchangeRequestWithUsersRead,
)

# Импортируем здесь для разрешения forward references
from src.schemas.user import UserWithBooksRead
from src.schemas.book import BookWithOwnerRead, BookWithRequestsRead
from src.schemas.exchange_request import (
    ExchangeRequestFullRead,
    ExchangeRequestWithBookRead,
    ExchangeRequestWithUsersRead,
)

UserWithBooksRead.model_rebuild()
BookWithOwnerRead.model_rebuild()
BookWithRequestsRead.model_rebuild()
ExchangeRequestWithBookRead.model_rebuild()
ExchangeRequestWithUsersRead.model_rebuild()
ExchangeRequestFullRead.model_rebuild()

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserShortRead",
    "UserWithBooksRead",
    "UserPasswordChange",
    "BookCreate",
    "BookUpdate",
    "BookRead",
    "BookShortRead",
    "BookWithOwnerRead",
    "BookWithRequestsRead",
    "BookExchangeStatusSchema",
    "ExchangeRequestCreate",
    "ExchangeRequestUpdate",
    "ExchangeRequestRead",
    "ExchangeRequestShortRead",
    "ExchangeRequestWithBookRead",
    "ExchangeRequestWithUsersRead",
    "ExchangeRequestFullRead",
    "ExchangeRequestStatusSchema",
]
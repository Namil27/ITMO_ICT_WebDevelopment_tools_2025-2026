from src.routers.book import router as book_router
from src.routers.exchange_request import router as exchange_request_router
from src.routers.user import router as user_router

__all__ = [
    "user_router",
    "book_router",
    "exchange_request_router",
]
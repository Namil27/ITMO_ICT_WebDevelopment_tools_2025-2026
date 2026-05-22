import os
from urllib.parse import urlparse

import httpx

from src.celery_app import celery_app
from src.crud.book import create_book
from src.crud.user import get_user_by_id
from src.database import SessionLocal
from src.schemas.book import BookCreate

PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001/parse")


@celery_app.task(name="parser.import_book")
def import_book_task(
    url: str,
    owner_id: int,
    author: str | None = None,
    genre: str | None = "parsed",
    condition: str | None = "unknown",
) -> dict:
    db = SessionLocal()
    try:
        owner = get_user_by_id(db, owner_id)
        if not owner:
            raise ValueError("Владелец книги не найден.")

        with httpx.Client(timeout=15.0) as client:
            response = client.post(PARSER_SERVICE_URL, json={"url": url})
            response.raise_for_status()

        parsed = response.json()
        parsed_title = parsed.get("title") or "Untitled parsed page"
        parsed_domain = urlparse(url).netloc or "unknown source"

        book = create_book(
            db,
            BookCreate(
                title=parsed_title[:255],
                author=(author or parsed_domain)[:255],
                description=f"Imported from {url}",
                genre=genre,
                condition=condition,
            ),
            owner_id=owner_id,
        )

        return {
            "url": url,
            "parsed_title": parsed_title,
            "book": {
                "id": book.id,
                "owner_id": book.owner_id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "genre": book.genre,
                "condition": book.condition,
                "exchange_status": book.exchange_status.value,
                "is_available": book.is_available,
                "created_at": book.created_at.isoformat(),
                "updated_at": book.updated_at.isoformat(),
            },
        }
    finally:
        db.close()

import os
from urllib.parse import urlparse

from celery.result import AsyncResult
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.celery_app import celery_app
from src.crud.book import create_book
from src.crud.user import get_user_by_id
from src.dependencies import get_db
from src.schemas.book import BookCreate
from src.schemas.parser import (
    ParseBookRequest,
    ParseBookResponse,
    ParseBookTaskResponse,
    ParseTaskStatusResponse,
)
from src.tasks.parser import import_book_task

PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001/parse")

router = APIRouter(prefix="/parser", tags=["Parser"])


@router.post("/import-book", response_model=ParseBookResponse)
async def import_book_from_url(
    request: ParseBookRequest,
    db: Session = Depends(get_db),
):
    owner = get_user_by_id(db, request.owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Владелец книги не найден.",
        )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                PARSER_SERVICE_URL,
                json={"url": str(request.url)},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Parser service error: {exc}",
        ) from exc

    parsed = response.json()
    parsed_title = parsed.get("title") or "Untitled parsed page"
    parsed_url = str(request.url)
    parsed_domain = urlparse(parsed_url).netloc or "unknown source"

    book = create_book(
        db,
        BookCreate(
            title=parsed_title[:255],
            author=(request.author or parsed_domain)[:255],
            description=f"Imported from {parsed_url}",
            genre=request.genre,
            condition=request.condition,
        ),
        owner_id=request.owner_id,
    )

    return ParseBookResponse(
        url=request.url,
        parsed_title=parsed_title,
        book=book,
    )


@router.post("/import-book-async", response_model=ParseBookTaskResponse)
def import_book_from_url_async(
    request: ParseBookRequest,
    db: Session = Depends(get_db),
):
    owner = get_user_by_id(db, request.owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Владелец книги не найден.",
        )

    task = import_book_task.delay(
        str(request.url),
        request.owner_id,
        request.author,
        request.genre,
        request.condition,
    )

    return ParseBookTaskResponse(
        task_id=task.id,
        status="queued",
        message="Задача парсинга добавлена в очередь.",
    )


@router.get("/tasks/{task_id}", response_model=ParseTaskStatusResponse)
def get_parse_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)

    if task.failed():
        return ParseTaskStatusResponse(
            task_id=task_id,
            status=task.status,
            error=str(task.result),
        )

    return ParseTaskStatusResponse(
        task_id=task_id,
        status=task.status,
        result=task.result if task.successful() else None,
    )

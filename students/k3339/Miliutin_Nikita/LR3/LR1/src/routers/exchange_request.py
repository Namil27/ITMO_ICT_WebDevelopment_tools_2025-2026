from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.crud.book import get_book_by_id
from src.crud.exchange_request import (
    create_exchange_request,
    delete_exchange_request,
    get_exchange_request_by_id,
    get_exchange_request_full,
    get_exchange_requests,
    get_incoming_exchange_requests,
    get_outgoing_exchange_requests,
    update_exchange_request,
)
from src.crud.user import get_user_by_id
from src.dependencies import get_db
from src.schemas.exchange_request import (
    ExchangeRequestCreate,
    ExchangeRequestFullRead,
    ExchangeRequestRead,
    ExchangeRequestUpdate,
)

router = APIRouter(prefix="/exchange-requests", tags=["Exchange Requests"])


@router.post("/", response_model=ExchangeRequestRead, status_code=status.HTTP_201_CREATED)
def create_exchange_request_endpoint(
    request_in: ExchangeRequestCreate,
    requester_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    db_book = get_book_by_id(db, request_in.book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена.",
        )

    db_requester = get_user_by_id(db, requester_id)
    if not db_requester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отправитель запроса не найден.",
        )

    owner_id = db_book.owner_id

    if requester_id == owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя отправить запрос на собственную книгу.",
        )

    if not db_book.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Книга сейчас недоступна для обмена.",
        )

    try:
        return create_exchange_request(
            db,
            request_in=request_in,
            requester_id=requester_id,
            owner_id=owner_id,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось создать запрос на обмен.",
        )


@router.get("/", response_model=list[ExchangeRequestRead])
def get_exchange_requests_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_exchange_requests(db, skip=skip, limit=limit)


@router.get("/incoming/{owner_id}", response_model=list[ExchangeRequestRead])
def get_incoming_exchange_requests_endpoint(
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    db_owner = get_user_by_id(db, owner_id)
    if not db_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )

    return get_incoming_exchange_requests(db, owner_id=owner_id, skip=skip, limit=limit)


@router.get("/outgoing/{requester_id}", response_model=list[ExchangeRequestRead])
def get_outgoing_exchange_requests_endpoint(
    requester_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    db_requester = get_user_by_id(db, requester_id)
    if not db_requester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )

    return get_outgoing_exchange_requests(
        db,
        requester_id=requester_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{request_id}", response_model=ExchangeRequestRead)
def get_exchange_request_by_id_endpoint(request_id: int, db: Session = Depends(get_db)):
    db_request = get_exchange_request_by_id(db, request_id)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запрос на обмен не найден.",
        )
    return db_request


@router.get("/{request_id}/full", response_model=ExchangeRequestFullRead)
def get_exchange_request_full_endpoint(request_id: int, db: Session = Depends(get_db)):
    db_request = get_exchange_request_full(db, request_id)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запрос на обмен не найден.",
        )
    return db_request


@router.patch("/{request_id}", response_model=ExchangeRequestRead)
def update_exchange_request_endpoint(
    request_id: int,
    request_in: ExchangeRequestUpdate,
    db: Session = Depends(get_db),
):
    db_request = get_exchange_request_by_id(db, request_id)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запрос на обмен не найден.",
        )

    update_data = request_in.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] in {"accepted", "rejected", "cancelled"}:
        if "responded_at" not in update_data:
            request_in = ExchangeRequestUpdate(
                **update_data,
                responded_at=datetime.now(timezone.utc),
            )

    try:
        return update_exchange_request(db, db_request, request_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось обновить запрос на обмен.",
        )


@router.delete("/{request_id}", response_model=ExchangeRequestRead)
def delete_exchange_request_endpoint(request_id: int, db: Session = Depends(get_db)):
    db_request = get_exchange_request_by_id(db, request_id)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запрос на обмен не найден.",
        )

    return delete_exchange_request(db, db_request)
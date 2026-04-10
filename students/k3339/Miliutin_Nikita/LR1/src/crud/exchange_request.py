from sqlalchemy.orm import Session, joinedload

from src.models.exchange_request import ExchangeRequest
from src.schemas.exchange_request import ExchangeRequestCreate, ExchangeRequestUpdate


def create_exchange_request(
    db: Session,
    request_in: ExchangeRequestCreate,
    requester_id: int,
    owner_id: int,
) -> ExchangeRequest:
    db_request = ExchangeRequest(
        book_id=request_in.book_id,
        requester_id=requester_id,
        owner_id=owner_id,
        message=request_in.message,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def get_exchange_request_by_id(db: Session, request_id: int) -> ExchangeRequest | None:
    return db.query(ExchangeRequest).filter(ExchangeRequest.id == request_id).first()


def get_exchange_request_full(db: Session, request_id: int) -> ExchangeRequest | None:
    return (
        db.query(ExchangeRequest)
        .options(
            joinedload(ExchangeRequest.book),
            joinedload(ExchangeRequest.requester),
            joinedload(ExchangeRequest.owner),
        )
        .filter(ExchangeRequest.id == request_id)
        .first()
    )


def get_exchange_requests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[ExchangeRequest]:
    return db.query(ExchangeRequest).offset(skip).limit(limit).all()


def get_incoming_exchange_requests(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[ExchangeRequest]:
    return (
        db.query(ExchangeRequest)
        .filter(ExchangeRequest.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_outgoing_exchange_requests(
    db: Session,
    requester_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[ExchangeRequest]:
    return (
        db.query(ExchangeRequest)
        .filter(ExchangeRequest.requester_id == requester_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_exchange_request(
    db: Session,
    db_request: ExchangeRequest,
    request_in: ExchangeRequestUpdate,
) -> ExchangeRequest:
    update_data = request_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_request, field, value)

    db.commit()
    db.refresh(db_request)
    return db_request


def delete_exchange_request(db: Session, db_request: ExchangeRequest) -> ExchangeRequest:
    db.delete(db_request)
    db.commit()
    return db_request
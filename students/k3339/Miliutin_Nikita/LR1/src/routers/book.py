from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.crud.book import (
    create_book,
    delete_book,
    get_available_books,
    get_book_by_id,
    get_book_with_owner,
    get_books,
    get_books_by_owner,
    update_book,
)
from src.crud.user import get_user_by_id
from src.dependencies import get_db
from src.schemas.book import BookCreate, BookRead, BookUpdate, BookWithOwnerRead

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book_endpoint(
    book_in: BookCreate,
    owner_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    db_owner = get_user_by_id(db, owner_id)
    if not db_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Владелец книги не найден.",
        )

    return create_book(db, book_in, owner_id=owner_id)


@router.get("/", response_model=list[BookRead])
def get_books_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_books(db, skip=skip, limit=limit)


@router.get("/available", response_model=list[BookRead])
def get_available_books_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_available_books(db, skip=skip, limit=limit)


@router.get("/owner/{owner_id}", response_model=list[BookRead])
def get_books_by_owner_endpoint(
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

    return get_books_by_owner(db, owner_id=owner_id, skip=skip, limit=limit)


@router.get("/{book_id}", response_model=BookRead)
def get_book_by_id_endpoint(book_id: int, db: Session = Depends(get_db)):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена.",
        )
    return db_book


@router.get("/{book_id}/owner", response_model=BookWithOwnerRead)
def get_book_with_owner_endpoint(book_id: int, db: Session = Depends(get_db)):
    db_book = get_book_with_owner(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена.",
        )
    return db_book


@router.patch("/{book_id}", response_model=BookRead)
def update_book_endpoint(book_id: int, book_in: BookUpdate, db: Session = Depends(get_db)):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена.",
        )

    return update_book(db, db_book, book_in)


@router.delete("/{book_id}", response_model=BookRead)
def delete_book_endpoint(book_id: int, db: Session = Depends(get_db)):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена.",
        )

    return delete_book(db, db_book)
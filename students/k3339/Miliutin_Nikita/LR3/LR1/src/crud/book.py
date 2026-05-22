from sqlalchemy.orm import Session, joinedload

from src.models.book import Book
from src.schemas.book import BookCreate, BookUpdate


def create_book(db: Session, book_in: BookCreate, owner_id: int) -> Book:
    db_book = Book(
        owner_id=owner_id,
        title=book_in.title,
        author=book_in.author,
        description=book_in.description,
        genre=book_in.genre,
        condition=book_in.condition,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_book_by_id(db: Session, book_id: int) -> Book | None:
    return db.query(Book).filter(Book.id == book_id).first()


def get_book_with_owner(db: Session, book_id: int) -> Book | None:
    return (
        db.query(Book)
        .options(joinedload(Book.owner))
        .filter(Book.id == book_id)
        .first()
    )


def get_book_with_requests(db: Session, book_id: int) -> Book | None:
    return (
        db.query(Book)
        .options(joinedload(Book.exchange_requests))
        .filter(Book.id == book_id)
        .first()
    )


def get_books(db: Session, skip: int = 0, limit: int = 100) -> list[Book]:
    return db.query(Book).offset(skip).limit(limit).all()


def get_books_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> list[Book]:
    return (
        db.query(Book)
        .filter(Book.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_available_books(db: Session, skip: int = 0, limit: int = 100) -> list[Book]:
    return (
        db.query(Book)
        .filter(Book.is_available.is_(True))
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_book(db: Session, db_book: Book, book_in: BookUpdate) -> Book:
    update_data = book_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_book, field, value)

    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, db_book: Book) -> Book:
    db.delete(db_book)
    db.commit()
    return db_book
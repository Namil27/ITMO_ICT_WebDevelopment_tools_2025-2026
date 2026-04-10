import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud.user import (
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    get_user_with_books,
    get_users,
    update_user,
)
from src.dependencies import get_db
from src.schemas.user import UserCreate, UserRead, UserUpdate, UserWithBooksRead

router = APIRouter(prefix="/users", tags=["Users"])


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user_by_email = get_user_by_email(db, user_in.email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует.",
        )

    existing_user_by_username = get_user_by_username(db, user_in.username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует.",
        )

    hashed_password = _hash_password(user_in.password)
    return create_user(db, user_in, hashed_password)


@router.get("/", response_model=list[UserRead])
def get_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )
    return db_user


@router.get("/{user_id}/books", response_model=UserWithBooksRead)
def get_user_with_books_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user_with_books(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )
    return db_user


@router.patch("/{user_id}", response_model=UserRead)
def update_user_endpoint(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )

    if user_in.email and user_in.email != db_user.email:
        existing_user_by_email = get_user_by_email(db, user_in.email)
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует.",
            )

    if user_in.username and user_in.username != db_user.username:
        existing_user_by_username = get_user_by_username(db, user_in.username)
        if existing_user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким username уже существует.",
            )

    return update_user(db, db_user, user_in)


@router.delete("/{user_id}", response_model=UserRead)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )

    return delete_user(db, db_user)
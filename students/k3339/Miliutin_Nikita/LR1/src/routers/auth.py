from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.security import create_access_token, verify_password
from src.crud.auth import (
    authenticate_user,
    change_user_password,
    get_user_by_email,
    get_user_by_username,
    register_user,
)
from src.dependencies import get_db
from src.dependencies.auth import get_current_user
from src.schemas.auth import ChangePassword, Token, UserRegister
from src.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_endpoint(user_in: UserRegister, db: Session = Depends(get_db)):
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

    return register_user(db, user_in)


@router.post("/login", response_model=Token)
def login_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def read_current_user_endpoint(current_user=Depends(get_current_user)):
    return current_user


@router.post("/change-password", response_model=UserRead)
def change_password_endpoint(
    password_in: ChangePassword,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Старый пароль введен неверно.",
        )

    if password_in.old_password == password_in.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль должен отличаться от старого.",
        )

    return change_user_password(db, current_user, password_in)
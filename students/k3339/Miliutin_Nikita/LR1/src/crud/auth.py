from sqlalchemy.orm import Session

from src.core.security import get_password_hash, verify_password
from src.models.user import User
from src.schemas.auth import ChangePassword, UserRegister


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def register_user(db: Session, user_in: UserRegister) -> User:
    hashed_password = get_password_hash(user_in.password)

    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        city=user_in.city,
        bio=user_in.bio,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def change_user_password(db: Session, db_user: User, password_in: ChangePassword) -> User:
    db_user.hashed_password = get_password_hash(password_in.new_password)
    db.commit()
    db.refresh(db_user)
    return db_user
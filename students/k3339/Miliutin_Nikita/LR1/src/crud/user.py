from sqlalchemy.orm import Session, joinedload

from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user_in: UserCreate, hashed_password: str) -> User:
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


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_with_books(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.books))
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: User) -> User:
    db.delete(db_user)
    db.commit()
    return db_user
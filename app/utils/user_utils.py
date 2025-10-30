from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta

from ..models import User
from ..schemas import UserCreate
from .auth import hash_password, verify_password, create_access_token
from .constants import INITIAL_BALANCE, ACCESS_TOKEN_EXPIRE_MINUTES


def get_user_by_username(db: Session, username: str):
    """
    Get user from DB by username.
    :param db: SQLAlchemy Session used to run the query.
    :param username: Username to search for.
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """
    Get user from DB by email address.
    :param db: SQLAlchemy Session used to run the query.
    :param email: Email address to search for.
    """
    return db.query(User).filter(User.email == email).first()


def create_user_in_db(db: Session, user: UserCreate, initial_balance: float = INITIAL_BALANCE):
    """
    Create a new user in DB.
    :param db: SQLAlchemy Session used for inserting and committing the new User instance.
    :param user: Pydantic model containing the creation info.
    :param initial_balance: Initial balance to assign to the new user.
    """
    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
        balance=initial_balance,
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError:
        db.rollback()
        raise

def authenticate_user(db: Session, username: str, password: str):
    """
    Verify user's credentials.
    :param db: SQLAlchemy Session used to load the user record.
    :param username: Username to authenticate.
    :param password: Plaintext password to verify against the stored hash.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_token_for_user(user: User, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    """
    Create a JWT access token for an authenticated user.
    :param user: Authenticated User instance for whom to create the token.
    :param expires_minutes: Token validity period in minutes.
    """
    access_token_expires = timedelta(minutes=expires_minutes)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

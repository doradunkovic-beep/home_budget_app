from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
 
from ..schemas import UserOut, UserCreate, UserLogin, Token
from ..database import get_db
from ..utils.user_utils import get_user_by_username, get_user_by_email, create_user_in_db, authenticate_user, create_token_for_user
from ..utils.category_utils import create_predefined_categories_for_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    if get_user_by_username(db, user.username) or get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")

    try:
        new_user = create_user_in_db(db, user)
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

    create_predefined_categories_for_user(db, new_user.id)
    
    return new_user


@router.post("/login", response_model=Token)
def login_user(form_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return create_token_for_user(user)

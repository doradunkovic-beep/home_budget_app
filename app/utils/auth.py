from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt, ExpiredSignatureError
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from .constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


bearer_scheme = HTTPBearer(auto_error=False)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def truncate_password_for_bcrypt(password: str):
    """
    Truncate the password to 72 bytes.
    """
    encoded = password.encode("utf-8")

    if len(encoded) <= 72:
        return password
    truncated = encoded[:72]
    
    return truncated.decode("utf-8", errors="ignore")

def hash_password(password: str):
    """
    Hash a plaintext password and return the hash string.
    """
    safe_pw = truncate_password_for_bcrypt(password)
    return pwd_context.hash(safe_pw)

def verify_password(plain_password, hashed_password):
    """
    Verify a plaintext password against the stored hash.
    """
    safe_pw = truncate_password_for_bcrypt(plain_password)
    return pwd_context.verify(safe_pw, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token.
    :param data: data with token.
    :param expires_delta: Optional expiry override.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """
    Decode a JWT and return username or None for invalid tokens.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except ExpiredSignatureError:
        raise
    except JWTError:
        return None
    
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)):
    """
    Returns the authenticated User instance or raises HTTPException.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization credentials missing")
    token = credentials.credentials

    try:
        username = decode_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user
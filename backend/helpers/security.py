import jwt
import uuid
import bcrypt
from typing import Optional
from jwt.types import Options
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Response, Request
from core.config import settings
from .constants import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


def set_tokens_cookies(
    response: Response, 
    access_token: str, 
    refresh_token: str, 
    expire_seconds: int,
) -> None:
    is_prod = settings.IS_PRODUCTION == "True"

    response.set_cookie(
        key="lior_access_token",
        value=access_token,
        max_age=expire_seconds,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        path="/"
    )
    
    response.set_cookie(
        key="lior_refresh_token",
        value=refresh_token,
        max_age=expire_seconds,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        path="/"
    )


def get_current_user_id(request: Request) -> int:
    user_payload = request.state.user
    user_id = user_payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token data"
        )
    
    try:
        validated_user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID inside token must be a valid integer"
        )
    
    return validated_user_id


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: Optional[str] = None) -> bool:
    if not hashed_password:
        return False

    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(user_id: int, username: str, refresh_jti: str, current_time: Optional[datetime] = None) -> str:
    base_time = current_time or datetime.now(timezone.utc)
    
    access_payload = {
        "sub": str(user_id),
        "username": username,
        "type": "access",
        "jti": refresh_jti,
        "exp": base_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(access_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_tokens(user_id: int, username: str) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    
    refresh_jti = str(uuid.uuid4())
    access_token = create_access_token(user_id, username, refresh_jti, current_time=now)
    
    refresh_payload = {
        "sub": str(user_id),
        "username": username,
        "type": "refresh",
        "jti": refresh_jti,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    return access_token, refresh_token


def decode_token(token: str, options: Optional[Options] = None) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], options=options)
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired. Please log in again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

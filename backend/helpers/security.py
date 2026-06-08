import jwt
import uuid
import bcrypt
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Response, Request
from core.config import settings
from services.container import auth_cache
from .constants import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, TOKEN_COOKIES_EXPIRE_SECONDS


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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(user_id: int, username: str, refresh_jti: str, current_time: Optional[datetime]) -> str:
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


def decode_token(token: str, options: Optional[dict] = None) -> dict:
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


def verify_access_jti_match(lior_access_token: str | None, refresh_jti: str) -> None:
    if not lior_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Access token missing for verification."
        )
    try:
        access_payload = decode_token(lior_access_token, {"verify_exp": False})
        expected_refresh_jti = access_payload.get("jti")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid access token structure."
        )

    if refresh_jti != expected_refresh_jti:
        print(f"Security Alert: JTI mismatch! Refresh: {refresh_jti}, Access expected: {expected_refresh_jti}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token reuse or invalid session detected."
        )
    

async def handle_new_tokens_generation(response: Response, user_id: int, username: str) -> tuple[str, str]:
    new_access_token, new_refresh_token = create_tokens(user_id, username)
    data = {
        "status": "active"
    }
    await auth_cache.save_token(new_refresh_token, data, TOKEN_COOKIES_EXPIRE_SECONDS)
    set_tokens_cookies(response, new_access_token, new_refresh_token, TOKEN_COOKIES_EXPIRE_SECONDS)
    return new_access_token, new_refresh_token

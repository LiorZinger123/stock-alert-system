import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from core.database import get_db
from services.container import auth_cache
from services.auth_service import AuthService
from services.user_service import UserService
from api.schemas.auth import RegisterPayload, Credentials
from helpers.constants import TOKEN_COOKIES_EXPIRE_SECONDS
from helpers.security import hash_password, verify_password, set_tokens_cookies, decode_token


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterPayload, response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        user_service = UserService(db)
        auth_service = AuthService(auth_cache)
        
        if await user_service.get_user_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        if await user_service.get_user_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        new_user = await user_service.create_user(payload, hash_password(payload.password))
        access, refresh = await auth_service.login_user(new_user)
        set_tokens_cookies(response, access, refresh, TOKEN_COOKIES_EXPIRE_SECONDS)
        
        return {
            "message": "User registered successfully",
            "user_id": new_user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(payload: Credentials, response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        user_service = UserService(db)
        auth_service = AuthService(auth_cache)
        user = await user_service.get_user_by_username(payload.username)

        if not user or not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credentials"
            )
        
        access, refresh = await auth_service.login_user(user)
        set_tokens_cookies(response, access, refresh, TOKEN_COOKIES_EXPIRE_SECONDS)
        return {
            "message": "Login successful",
            "user_id": user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, lior_refresh_token: str | None = Cookie(None)) -> dict[str, str]:
    try:
        if lior_refresh_token:
            auth_service = AuthService(auth_cache)
            await auth_service.logout_user(lior_refresh_token)
    except Exception as e:
        logger.error(f"Logout cleanup error (Redis): {e}")

    response.delete_cookie("lior_access_token")
    response.delete_cookie("lior_refresh_token")
    return {"message": "Logged out successfully"}


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(response: Response, 
                  lior_refresh_token: str | None = Cookie(None),
                  lior_access_token: str | None = Cookie(None)) -> dict[str, str]:
    if not lior_refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    try:
        payload = decode_token(lior_refresh_token)
        sub = payload.get("sub")
        username = payload.get("username")
        jti = payload.get("jti")

        if sub is None or username is None or jti is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing required claims")
            
        user_id = int(sub)
        auth_service = AuthService(auth_cache)
        
        return await auth_service.refresh_tokens(
            old_refresh_token=lior_refresh_token,
            lior_access_token=lior_access_token,
            user_id=user_id,
            username=username,
            refresh_jti=jti,
            response=response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )

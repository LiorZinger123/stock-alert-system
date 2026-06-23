import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from core.database import get_db
from services.container import auth_cache
from services.auth_service import AuthService
from services.user_service import UserService
from api.schemas.auth import RegisterPayload, LoginCredentials, GoogleAuthRequest


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterPayload, response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        user_service = UserService(db)
        auth_service = AuthService(auth_cache, user_service)
        
        new_user_id = await auth_service.register_user(payload, response)
        
        return {
            "message": "User registered successfully",
            "user_id": new_user_id
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
async def login(payload: LoginCredentials, response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        user_service = UserService(db)
        auth_service = AuthService(auth_cache, user_service)
       
        user_id = await auth_service.login_user(payload, response)

        return {
            "message": "Login successful",
            "user_id": user_id
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
        auth_service = AuthService(auth_cache)
        
        return await auth_service.refresh_tokens(
            old_refresh_token=lior_refresh_token,
            lior_access_token=lior_access_token,
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


@router.post("/google", status_code=status.HTTP_200_OK)
async def google_auth(
    request: GoogleAuthRequest, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        auth_service = AuthService(auth_cache, user_service)
        
        user_id = await auth_service.authenticate_google_user(
            token=request.token,
            response=response
        )

        return {
            "message": "Google login successful",
            "user_id": user_id
        }
    except HTTPException:
            raise
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )

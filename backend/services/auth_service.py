import jwt
import httpx
import random
from typing import Optional
from fastapi import HTTPException, status, Response
from db.models import User
from .container import auth_cache
from helpers.enums import UserProviders
from services.cache_managers import AuthCache
from services.user_service import UserService
from api.schemas.auth import RegisterPayload, LoginCredentials
from helpers.constants import TOKEN_COOKIES_EXPIRE_SECONDS, USED_TOKEN_TTL_SECONDS, GOOGLE_USER_AUTH
from helpers.security import (
    decode_token,
    create_tokens, 
    hash_password,
    verify_password,
    set_tokens_cookies,
    create_access_token,
)


class AuthService:
    def __init__(self, auth_cache: AuthCache, user_service: Optional[UserService] = None):
        self.auth_cache = auth_cache
        self.user_service = user_service

    async def create_and_save_tokens(self, user: User, expire: int = TOKEN_COOKIES_EXPIRE_SECONDS) -> tuple[str, str]:
        access_token, refresh_token = create_tokens(user.id, user.username)
        await self.auth_cache.save_token(refresh_token, {"status": "active"}, expire)
        return access_token, refresh_token
    
    
    def verify_access_jti_match(self, lior_access_token: str | None, refresh_jti: str) -> None:
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
    

    async def handle_new_tokens_generation(self, response: Response, user_id: int, username: str) -> tuple[str, str]:
        new_access_token, new_refresh_token = create_tokens(user_id, username)
        data = {
            "status": "active"
        }
        await auth_cache.save_token(new_refresh_token, data, TOKEN_COOKIES_EXPIRE_SECONDS)
        set_tokens_cookies(response, new_access_token, new_refresh_token, TOKEN_COOKIES_EXPIRE_SECONDS)
        return new_access_token, new_refresh_token


    async def register_user(self, payload: RegisterPayload, response: Response) -> int:
        if not self.user_service:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service misconfigured: User database access required."
            )

        if await self.user_service.get_user_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        existing_user = await self.user_service.get_user_by_email(payload.email)

        if existing_user:
            if existing_user.provider:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email already registered via {existing_user.provider}. Please log in using that method."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered. Please log in."
                )
        
        new_user = await self.user_service.create_user(payload, hash_password(payload.password))
        access, refresh = await self.create_and_save_tokens(new_user)
        set_tokens_cookies(response, access, refresh, TOKEN_COOKIES_EXPIRE_SECONDS)
        return new_user.id

    async def login_user(self, payload: LoginCredentials, response: Response) -> int:
        if not self.user_service:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service misconfigured: User database access required."
            )
          
        user = await self.user_service.get_user_by_username(payload.username)

        if not user or not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credentials"
            )
        
        access, refresh = await self.create_and_save_tokens(user)
        set_tokens_cookies(response, access, refresh, TOKEN_COOKIES_EXPIRE_SECONDS)
        return user.id

    async def logout_user(self, refresh_token: str) -> None:
        await self.auth_cache.delete_token(refresh_token)

    async def refresh_tokens(self,
                            old_refresh_token: str,
                            lior_access_token: str | None,
                            response: Response) -> dict[str, str]:
        payload = decode_token(old_refresh_token)
        sub = payload.get("sub")
        username = payload.get("username")
        jti = payload.get("jti")

        if sub is None or username is None or jti is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing required claims")
            
        user_id = int(sub)
        token_status = await self.auth_cache.get_token(old_refresh_token)

        if not token_status:
            self.verify_access_jti_match(lior_access_token, jti)
            _, new_refresh_token = await self.handle_new_tokens_generation(response, user_id, username)
            
            await self.auth_cache.save_token(
                old_refresh_token, 
                {"status": "used", "new_refresh_token": new_refresh_token},
                USED_TOKEN_TTL_SECONDS
            )
            return {"message": "Token refreshed and re-synced"}

        status_val = token_status.get("status")

        if status_val == "active":
            _, new_refresh_token = await self.handle_new_tokens_generation(response, user_id, username)
            await self.auth_cache.save_token(
                old_refresh_token, 
                {"status": "used", "new_refresh_token": new_refresh_token},
                USED_TOKEN_TTL_SECONDS
            )
            return {"message": "Token refreshed successfully"}

        elif status_val == "used":
            new_refresh_token = token_status.get("new_refresh_token")
            new_refresh_payload = decode_token(new_refresh_token)

            jti = new_refresh_payload.get("jti")

            if jti is None:
                raise HTTPException(status_code=401, detail="Invalid token: missing JTI")
            
            new_access_token = create_access_token(user_id, username, jti)
            
            set_tokens_cookies(response, new_access_token, new_refresh_token, TOKEN_COOKIES_EXPIRE_SECONDS)
            return {"message": "Token refreshed successfully (from cached)"}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    async def authenticate_google_user(self, token: str, response: Response) -> int:
        if not self.user_service:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service misconfigured."
            )

        async with httpx.AsyncClient() as client:
            res = await client.get(
                GOOGLE_USER_AUTH,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if res.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Google token")
            
            id_info = res.json()

        email = id_info['email']
        google_id = id_info['sub']

        user = await self.user_service.get_user_by_email(email)

        if not user:
            base_name = id_info.get('name', 'user').lower().replace(' ', '_')
            username = f"{base_name}_{random.randint(1000, 9999)}"
            user = await self.user_service.create_oauth_user(email, username, UserProviders.GOOGLE.value, google_id)
        else:
            if not user.provider_id:
                user = await self.user_service.update_user_oauth_id(user.id, UserProviders.GOOGLE.value, google_id)

        access, refresh = await self.create_and_save_tokens(user)
        set_tokens_cookies(response, access, refresh, TOKEN_COOKIES_EXPIRE_SECONDS)

        return user.id

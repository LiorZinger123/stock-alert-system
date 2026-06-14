from fastapi import HTTPException, status, Response
from db.models import User
from services.cache_managers import AuthCache
from helpers.constants import TOKEN_COOKIES_EXPIRE_SECONDS, USED_TOKEN_TTL_SECONDS
from helpers.security import (
    decode_token,
    create_tokens, 
    set_tokens_cookies,
    create_access_token,
    verify_access_jti_match,
    handle_new_tokens_generation,
)


class AuthService:
    def __init__(self, auth_cache: AuthCache):
        self.auth_cache = auth_cache

    async def login_user(self, user: User, expire: int = TOKEN_COOKIES_EXPIRE_SECONDS) -> tuple[str, str]:
        access_token, refresh_token = create_tokens(user.id, user.username)
        await self.auth_cache.save_token(refresh_token, {"status": "active"}, expire)
        return access_token, refresh_token

    async def logout_user(self, refresh_token: str) -> None:
        await self.auth_cache.delete_token(refresh_token)

    async def refresh_tokens(self,
                            old_refresh_token: str,
                            lior_access_token: str | None,
                            user_id: int,
                            username: str,
                            refresh_jti: str,
                            response: Response) -> dict[str, str]:
        token_status = await self.auth_cache.get_token(old_refresh_token)

        if not token_status:
            verify_access_jti_match(lior_access_token, refresh_jti)
            _, new_refresh_token = await handle_new_tokens_generation(response, user_id, username)
            
            await self.auth_cache.save_token(
                old_refresh_token, 
                {"status": "used", "new_refresh_token": new_refresh_token},
                USED_TOKEN_TTL_SECONDS
            )
            return {"message": "Token refreshed and re-synced"}

        status_val = token_status.get("status")

        if status_val == "active":
            _, new_refresh_token = await handle_new_tokens_generation(response, user_id, username)
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

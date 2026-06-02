import jwt
from fastapi import Request, Response
from typing import Callable, Awaitable
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings
from helpers.constants import AUTH_MIDDLEWARE_FREE_ROUTES


class AuthMiddleware(BaseHTTPMiddleware):
    def validate_token(self, request: Request) -> dict | None:
        token = request.cookies.get("lior_access_token")

        if not token:
            return None
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
            
        except:
            return None

    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if any(request.url.path.startswith(route) for route in AUTH_MIDDLEWARE_FREE_ROUTES):
            return await call_next(request)

        token_data = self.validate_token(request)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Could not validate credentials or token expired"}
            )

        request.state.user = token_data
        return await call_next(request)

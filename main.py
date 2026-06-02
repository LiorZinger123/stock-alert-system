import sys
import logging
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import engine
from services.container import redis_service
from api.routes.auth import router as auth_router
from api.routes.assets import router as assets_router
from api.routes.alerts import router as alerts_router
from middlewares.auth_middleware import AuthMiddleware


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    
    await redis_service.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
app.include_router(assets_router, prefix="/assets", tags=["Assets"])
app.add_middleware(AuthMiddleware)


@app.get("/health")
async def root():
    return {"status": "healthy", "message": "Welcome to the API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

import sys
import logging
import uvicorn
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
from services.container import redis_service
from api.routes.me import router as me_router
from api.routes.ws import router as ws_router
from api.routes.auth import router as auth_router
from api.routes.assets import router as assets_router
from api.routes.alerts import router as alerts_router
from middlewares.auth_middleware import AuthMiddleware
from helpers.rabbitmq_utils import alert_status_consumer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("--- LIFESPAN STARTING ---")
    task = asyncio.create_task(alert_status_consumer())

    yield
    
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    await redis_service.close()
    await engine.dispose()


origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
app.include_router(assets_router, prefix="/assets", tags=["Assets"])
app.include_router(me_router, prefix="/me", tags=["Me"])
app.include_router(ws_router, prefix="/ws", tags=["Ws"])
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def root():
    return {"status": "healthy", "message": "Welcome to the API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

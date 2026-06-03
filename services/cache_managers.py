import json
from typing import Optional, Any
from db.models import Alert
from .redis_service import RedisService
from helpers.constants import CACHE_TTL_PRICE, EMAIL_NOTIFICATION_QUEUE_NAME


class AuthCache:
    def __init__(self, redis: RedisService):
        self.redis = redis

    async def get_token(self, token: str) -> Any | None:
        return await self.redis.read(f"auth:token:{token}")

    async def save_token(self, token: str, data: dict, expire: int) -> None:
        await self.redis.write(f"auth:token:{token}", data, expire=expire)

    async def delete_token(self, token: str) -> None:
        await self.redis.delete(f"auth:token:{token}")


class MarketCache:
    def __init__(self, redis: RedisService):
        self.redis = redis

    async def get_price(self, symbol: str) -> Optional[float]:
        return await self.redis.read(f"stock:price:{symbol}")

    async def get_prices(self, symbols: list[str]) -> dict:
        raw_values = await self.redis.mget(symbols)
        result = {}

        for key, val in zip(symbols, raw_values):
            if val is None:
                result[key] = None
            elif isinstance(val, (int, float)):
                result[key] = val
            elif isinstance(val, (str, bytes)):
                try:
                    result[key] = json.loads(val)
                except json.JSONDecodeError:
                    result[key] = float(val)
            else:
                result[key] = val
                
        return result
    
    async def get_prices_bulk(self, symbols: list[str]) -> list[float | None]:
        keys = [f"stock:price:{s}" for s in symbols]
        prices_dict = await self.get_prices(keys)
        return [prices_dict.get(key) for key in keys]

    async def set_price(self, symbol: str, price: float, expire: int = CACHE_TTL_PRICE) -> None:
        await self.redis.write(f"stock:price:{symbol}", price, expire=expire)

    async def set_prices(self, price_dict: dict[str, float]) -> None:
        await self.redis.mset_with_expire(price_dict)


class NotificationService:
    def __init__(self, redis: RedisService):
        self.redis = redis
        self.queue_name = EMAIL_NOTIFICATION_QUEUE_NAME

    async def queue_notification(self, alert: Alert, current_price: float) -> None:
        await self.redis.enqueue_task(
            "send_email_task",
            _queue_name=self.queue_name,
            alert_id=alert.id, 
            user_email=alert.owner.email,
            symbol=alert.asset.symbol,
            target_price=str(alert.target_price),
            current_price=str(current_price),
            condition=str(alert.condition.value) if hasattr(alert.condition, 'value') else str(alert.condition)
        )

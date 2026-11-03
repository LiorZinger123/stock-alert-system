import json
from typing import Optional, Any
from .redis_service import RedisService
from helpers.constants import CACHE_TTL_PRICE


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

    async def get_prices(self, symbols: list[str]) -> dict[str, Optional[float]]:
        cache_keys = [f"stock:price:{symbol}" for symbol in symbols]
        
        raw_values = await self.redis.mget(cache_keys)
        result = {}

        for symbol, val in zip(symbols, raw_values):
            if val is None:
                result[symbol] = None
                continue

            try:
                parsed_val = json.loads(val) if isinstance(val, (str, bytes)) else val
                result[symbol] = float(parsed_val) if parsed_val is not None else None
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                result[symbol] = None

        return result
    
    async def set_price(self, symbol: str, price: float, expire: int = CACHE_TTL_PRICE) -> None:
        await self.redis.write(f"stock:price:{symbol}", price, expire=expire)

    async def set_prices(self, price_dict: dict[str, float]) -> None:
        await self.redis.mset_with_expire(price_dict)

import json
from typing import Optional, Any
import redis.asyncio as aioredis
from redis.client import Pipeline


class RedisService:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = aioredis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.host = host
        self.port = port

    def pipeline(self, **kwargs) -> Pipeline:
        return self.client.pipeline(**kwargs)

    async def read(self, key: str) -> Optional[Any]:
        data = await self.client.get(key)
        return json.loads(data) if data else None
    
    async def mget(self, keys: list[str]) -> list[Any]:
        raw_values = await self.client.mget(keys)
        return [json.loads(v) if v is not None else None for v in raw_values]

    async def write(self, key: str, value: Any, expire: int = None) -> None:
        await self.client.set(key, json.dumps(value), ex=expire)

    async def mset_with_expire(self, mapping: dict[str, Any], expire: int = 60) -> None:
        async with self.client.pipeline(transaction=True) as pipe:
            for key, value in mapping.items():
                pipe.set(key, json.dumps(value), ex=expire)
            await pipe.execute()

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

    async def close(self) -> None:
        await self.client.close()

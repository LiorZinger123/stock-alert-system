import json
import logging
from arq import create_pool
from typing import Optional, Any
import redis.asyncio as aioredis
from arq.connections import RedisSettings

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = aioredis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.arq_pool = None
        self.host = host
        self.port = port

    async def init_arq(self):
        self.arq_pool = await create_pool(RedisSettings(host=self.host, port=self.port))

    def pipeline(self, **kwargs):
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

    async def enqueue_task(self, task_name: str, **kwargs) -> None:
        if not self.arq_pool:
            await self.init_arq()
        await self.arq_pool.enqueue_job(task_name, **kwargs)

    async def close(self) -> None:
        await self.client.close()
        if self.arq_pool:
            await self.arq_pool.close()

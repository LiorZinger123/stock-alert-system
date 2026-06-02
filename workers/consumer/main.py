import asyncio
import logging
from arq import Worker
from .worker_settings import WorkerSettings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConsumerWorker")


async def main():
    logger.info("Starting Consumer Worker...")
    
    worker = Worker(
        functions=WorkerSettings.functions,
        redis_settings=WorkerSettings.redis_settings,
    )
    
    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Consumer Worker stopped.")

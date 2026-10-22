from core.config import settings
from .redis_service import RedisService
from .rabbitmq_publisher import RabbitMQPublisher
from .cache_managers import AuthCache, MarketCache


redis_service = RedisService(host=settings.REDIS_HOST)
auth_cache = AuthCache(redis_service)
market_cache = MarketCache(redis_service)
rabbitmq_publisher = RabbitMQPublisher(settings.RABBITMQ_URL)

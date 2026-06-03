from core.config import settings
from .redis_service import RedisService
from .cache_managers import AuthCache, MarketCache, NotificationService


redis_service = RedisService(host=settings.REDIS_HOST)
auth_cache = AuthCache(redis_service)
market_cache = MarketCache(redis_service)
notification_service = NotificationService(redis_service)

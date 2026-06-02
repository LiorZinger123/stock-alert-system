from arq.connections import RedisSettings
from .email_worker import send_email_task
from helpers.constants import EMAIL_NOTIFICATION_QUEUE_NAME


class WorkerSettings:
    functions = [send_email_task]
    redis_settings = RedisSettings(host="redis")
    queue_name = EMAIL_NOTIFICATION_QUEUE_NAME

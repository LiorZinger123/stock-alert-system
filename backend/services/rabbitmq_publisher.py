import json
import logging
import aio_pika


logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def get_channel(self):
        if self.connection is None or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
        if self.channel is None or self.channel.is_closed:
            self.channel = await self.connection.channel()
        return self.channel

    async def publish(self, queue_name: str, message_body: dict) -> None:
        channel = await self.get_channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue.name,
        )

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQPublisher connection closed.")

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

    async def publish_to_queue(self, queue_name: str, message_body: dict | list) -> None:
        channel = await self.get_channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue.name,
        )
        logger.debug(f"Published message directly to queue: {queue_name}")

    async def publish_to_exchange(self, exchange_name: str, message_body: dict | list, exchange_type=aio_pika.ExchangeType.FANOUT) -> None:
        channel = await self.get_channel()
        
        exchange = await channel.declare_exchange(
            name=exchange_name,
            type=exchange_type,
            durable=True
        )

        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="",
        )
        logger.info(f"Published message to exchange: {exchange_name}")

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQPublisher connection closed.")

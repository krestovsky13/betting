import json
import logging
import os
from pathlib import Path

import aio_pika
import asyncio

from dotenv import load_dotenv

env_path = os.path.join(Path(__file__).resolve().parent.parent.parent, '.env')

load_dotenv(env_path)
logger = logging.getLogger(__name__)

RMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
RMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')


async def send_event_status_update(event_id: str, state: int) -> None:
    connection = await aio_pika.connect_robust(
        f'amqp://{RMQ_USER}:{RMQ_PASSWORD}@rabbitmq/',
        loop=asyncio.get_event_loop(),
    )
    logger.info('Connection with broker has been successfully established')

    async with connection:
        msg = {'event_id': event_id, 'state': state}
        channel = await connection.channel()

        await channel.default_exchange.publish(
            message=aio_pika.Message(
                json.dumps(msg).encode('utf-8'),
                app_id='Line provider',
            ),
            routing_key='state_queue',
        )
        logger.info(f'Message {msg} has been sent successfully')

import asyncio
import json
import os
from pathlib import Path

import aio_pika
from aio_pika.abc import AbstractRobustConnection
from asyncpg import Pool, exceptions
from dotenv import load_dotenv
from fastapi.logger import logger

from src.db import create_database_pool

env_path = os.path.join(Path(__file__).resolve().parent.parent.parent, '.env')

load_dotenv(env_path)

RMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
RMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')


async def update_bets(event_id: str, state: int) -> None:
    while True:
        try:
            pool: Pool = await create_database_pool()
            async with pool.acquire() as connection:
                query = "UPDATE bets SET state = $1 WHERE event_id = $2;"
                res = await connection.execute(query, state, event_id)
                logger.info(f'Update bets completed: {res.split()[-1]} records')
        except exceptions.PostgresConnectionError as e:
            logger.error(f'PostgreSQL connection error: {str(e)}')
            await asyncio.sleep(5)
        else:
            break


async def message_consumer() -> None:
    while True:
        try:
            connection = await connect_to_rabbitmq()
            logger.info('Connection with broker has been successfully established')
            async with connection:
                channel = await connection.channel()

                queue = await channel.declare_queue('state_queue')
                logger.info('Waiting incoming messages')

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        event_id, state = json.loads(message.body.decode('utf-8')).values()
                        logger.info(f'Incoming message from "{message.app_id}" (size: {message.body_size} bytes)')
                        await update_bets(event_id, state)
                        await message.ack()
        except Exception as e:
            logger.error(f'An error occurred: {str(e)}')
            await asyncio.sleep(5)


async def connect_to_rabbitmq() -> AbstractRobustConnection:
    while True:
        try:
            connection = await aio_pika.connect_robust(
                f'amqp://{RMQ_USER}:{RMQ_PASSWORD}@rabbitmq/',
                loop=asyncio.get_event_loop(),
            )
            return connection
        except Exception as e:
            logger.error(f'Failed to connect to RabbitMQ: {str(e)}')
            await asyncio.sleep(5)

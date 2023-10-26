import asyncio
import json
import os
from pathlib import Path

import aio_pika
from aio_pika.abc import AbstractRobustConnection
from asyncpg import Pool
from dotenv import load_dotenv
from fastapi.logger import logger

from src.db import create_database_pool

env_path = os.path.join(Path(__file__).resolve().parent.parent.parent, '.env')

load_dotenv(env_path)

RMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
RMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')


async def update_bets(event_id: str, state: int) -> None:
    pool: Pool = await create_database_pool()
    async with pool.acquire() as connection:
        query = "UPDATE bets SET state = $1 WHERE event_id = $2;"
        res = await connection.execute(query, state, event_id)
        logger.info(f'Update bets completed: {res.split()[-1]} records')


async def message_consumer() -> None:
    connection: AbstractRobustConnection = await aio_pika.connect_robust(
        f'amqp://{RMQ_USER}:{RMQ_PASSWORD}@rabbitmq/',
        loop=asyncio.get_event_loop(),
    )
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

import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

from fastapi import Depends
from fastapi.logger import logger

env_path = os.path.join(Path(__file__).resolve().parent.parent, '.env')

load_dotenv(env_path)

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
DATABASE_URL = (
    f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


async def create_table():
    connection = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    create_table_query = """
        CREATE TABLE IF NOT EXISTS bets (
            bet_id SERIAL PRIMARY KEY,
            event_id text,
            amount numeric(8, 2) CHECK (amount > 0),
            state integer DEFAULT 1 CHECK (state IN (1, 2, 3)) 
        );
    """

    await connection.execute(create_table_query)
    logger.info('Table was created successfully')
    await connection.close()


async def create_database_pool() -> asyncpg.Pool:
    pool = await asyncpg.create_pool(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    return pool


def get_db_pool(pool: asyncpg.Pool = Depends(create_database_pool)):
    return pool

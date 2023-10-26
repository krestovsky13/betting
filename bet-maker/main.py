import asyncio

from fastapi import FastAPI

from src.amqp import message_consumer
from src.api import router
from src.db import create_table

app = FastAPI()

app.include_router(router=router)


@app.on_event('startup')
async def startup_event():
    await create_table()
    asyncio.create_task(message_consumer())

import time
from typing import Optional

import aiohttp
from asyncpg import Pool
from cachetools import TTLCache, cached
from fastapi import APIRouter, Depends, status, HTTPException

from src.db import get_db_pool
from src.models import Event, BaseBet, Bet, CreateBet

router = APIRouter()


@cached(TTLCache(maxsize=128, ttl=30))
async def get_open_events():
    async with aiohttp.ClientSession() as session:
        url = 'http://line-provider:8000/api/events'
        async with session.get(url) as response:
            data = await response.json()
            return data


async def get_event(event_id: str) -> Optional[dict]:
    async with aiohttp.ClientSession() as session:
        url = f'http://line-provider:8000/api/event/{event_id}'
        async with session.get(url) as response:
            if response.status == status.HTTP_200_OK:
                return await response.json()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Event not found')


@router.post('/bet', response_model=BaseBet, status_code=status.HTTP_201_CREATED)
async def create_bet(bet: CreateBet, pool: Pool = Depends(get_db_pool)):
    event = await get_event(bet.event_id)
    if deadline := event.get('deadline', None):
        if deadline > time.time():
            async with pool.acquire() as connection:
                query = "INSERT INTO bets (event_id, amount) VALUES ($1, $2) RETURNING bet_id"
                bet_id = await connection.fetchval(query, bet.event_id, bet.amount)
            return Bet(bet_id=str(bet_id))
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Event not available')


@router.get('/events', response_model=list[Event], status_code=status.HTTP_200_OK)
async def get_events():
    return await get_open_events()


@router.get('/bets', response_model=list[Bet], status_code=status.HTTP_200_OK)
async def get_bets_history(pool: Pool = Depends(get_db_pool)):
    query = "SELECT bet_id, state FROM bets"
    async with pool.acquire() as connection:
        records = await connection.fetch(query)
        bets = [Bet(bet_id=str(record['bet_id']), state=record['state']) for record in records]
    return bets

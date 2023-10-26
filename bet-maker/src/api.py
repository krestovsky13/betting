import aiohttp
from asyncpg import Pool
from fastapi import APIRouter, Depends, status, HTTPException

from src.db import get_db_pool
from src.models import Event, BaseBet, Bet, CreateBet

router = APIRouter()


async def get_open_events():
    async with aiohttp.ClientSession() as session:
        url = 'http://line-provider:8000/api/events'
        async with session.get(url) as response:
            data = await response.json()
            return data


@router.post('/bet', response_model=BaseBet, status_code=status.HTTP_201_CREATED)
async def create_bet(bet: CreateBet, pool: Pool = Depends(get_db_pool)):
    if any(event.get('event_id') == bet.event_id for event in await get_open_events()):
        async with pool.acquire() as connection:
            query = "INSERT INTO bets (event_id, amount) VALUES ($1, $2) RETURNING bet_id"
            bet_id = await connection.fetchval(query, bet.event_id, bet.amount)

        return Bet(bet_id=str(bet_id))
    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Event not available')


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

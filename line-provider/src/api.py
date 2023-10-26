import time

from fastapi import APIRouter, Path, HTTPException, status, Depends, Body

from src.amqp import send_event_status_update
from src.db import FakeDatabase
from src.models import Event, ChangeState

router = APIRouter()


@router.put('/event', response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: Event, db: FakeDatabase = Depends()):
    return db.update_or_create(event)


@router.get('/event/{event_id}', response_model=Event, status_code=status.HTTP_200_OK)
async def get_event(event_id: str = Path(), db: FakeDatabase = Depends()):
    if event := db.get(event_id):
        return event

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Event not found')


@router.get('/events', response_model=list[Event], status_code=status.HTTP_200_OK)
async def get_events(db: FakeDatabase = Depends()):
    return list(filter(lambda e: e.deadline > time.time(), db.list()))


@router.post('/{event_id}', response_model=Event, status_code=status.HTTP_200_OK)
async def update_event_status(event_id: str = Path(), change_state: ChangeState = Body(), db: FakeDatabase = Depends()):
    event, upd = db.change_state(Event(event_id=event_id, state=change_state.state))
    if event:
        if upd:
            await send_event_status_update(event_id, change_state.state.value)
        return event
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Event not found')

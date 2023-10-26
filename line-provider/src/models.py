import enum
from typing import Optional, Annotated

from decimal import Decimal
from pydantic import BaseModel, Field


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class ChangeState(BaseModel):
    state: EventState


class Event(BaseModel):
    event_id: str
    coefficient: Optional[Annotated[Decimal, Field(ge=0.01, decimal_places=2)]] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None

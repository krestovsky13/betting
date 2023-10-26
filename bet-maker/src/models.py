import enum

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class Event(BaseModel):
    event_id: str
    coefficient: Optional[Annotated[Decimal, Field(ge=0.01, decimal_places=2)]] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None


class BaseBet(BaseModel):
    bet_id: str


class Bet(BaseBet):
    state: Optional[EventState] = None


class CreateBet(BaseModel):
    event_id: str
    amount: Annotated[Decimal, Field(ge=0.01, decimal_places=2)]

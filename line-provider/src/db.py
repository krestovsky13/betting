import time
from typing import Optional

from src.models import Event, EventState


class FakeDatabase:
    _instance = None
    events: dict[str, Event] = {
        '1': Event(event_id='1', coefficient=1.2, deadline=int(time.time()) + 600, state=EventState.NEW),
        '2': Event(event_id='2', coefficient=1.15, deadline=int(time.time()) + 60, state=EventState.NEW),
        '3': Event(event_id='3', coefficient=1.67, deadline=int(time.time()) + 90, state=EventState.NEW),
    }

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def _get(self, key: str) -> Optional[Event]:
        return self.events.get(key, None)

    def create(self, event: Event) -> Optional[Event]:
        if not self._get(event.event_id):
            self.events[event.event_id] = event
            return event

    def get(self, key: str) -> Optional[Event]:
        return self._get(key)

    def list(self) -> list[Event]:
        return [e for e in self.events.values()]

    def update(self, upd_event: Event) -> Optional[Event]:
        if event := self._get(upd_event.event_id):
            for p_name, p_value in upd_event.model_dump(exclude_unset=True).items():
                setattr(event, p_name, p_value)
            return event

    def delete(self, key: str) -> Optional[Event]:
        return self.events.pop(key, None)

    def update_or_create(self, event: Event) -> Event:
        if not (new_event := self.update(event)):
            new_event = self.create(event)
        return new_event

    def change_state(self, change_event: Event) -> (Optional[Event], bool):
        change = False
        if event := self._get(change_event.event_id):
            if event.state != change_event.state:
                change = True
            return self.update(change_event), change
        return None, change

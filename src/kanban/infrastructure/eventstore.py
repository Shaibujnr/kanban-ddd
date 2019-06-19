import abc
import typing
import uuid
from kanban.domain.events import DomainEvent

class EventStream:
    events: typing.List[DomainEvent]
    uuid: uuid.UUID
    version: int

    def __init__(self, uuid: uuid.UUID, events: typing.List[DomainEvent], version: int):
        self._uuid = uuid
        self._events = events
        self._version = version

    @property
    def events(self):
        return self._events

    @property
    def version(self):
        return self._version

    @property
    def uuid(self):
        return self._uuid


class EventStore(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load_stream(self, aggregate_uuid: uuid.UUID) -> EventStream:
        pass
 
    @abc.abstractmethod
    def append_to_stream(
            self,
            aggregate_uuid: uuid.UUID,
            expected_version: typing.Optional[int],
            events: typing.List[DomainEvent]
    ) -> None:
        pass


class JsonFileEventStore(EventStore):
    def __init__(self, filename: str):
        self.filename = filename

    def load_stream(self, aggregate_uuid: uuid.UUID) -> EventStream:
        pass

    def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: typing.Optional[int],
        events: typing.List[DomainEvent]
    ) -> None:
        pass
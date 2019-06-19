import abc
import typing 
import uuid
from kanban.domain.events import DomainEvent
from kanban.infrastructure.eventstore import EventStream
from kanban.domain.errors import DiscardedEntityError


class AggregateRoot(metaclass=abc.ABCMeta):
    def __init__(self, stream: EventStream):
        self._version = stream.version
        self._uuid = stream.uuid
        self._discarded = False
        for event in stream.events:
            self.apply(event)
        self._changes = []

    @abc.abstractmethod
    def apply(self, event: DomainEvent):
        pass

    @abc.abstractmethod
    def _can_discard(self) -> bool:
        pass

    @abc.abstractmethod
    def discard(self):
        pass

    @property
    def discarded(self) -> bool:
        return self._discarded

    @property
    def version(self) -> int:
        self._check_not_discarded()
        return self._version

    @property
    def uuid(self) -> uuid.UUID:
        self._check_not_discarded()
        return self._uuid

    @property
    def changes(self) -> typing.List[DomainEvent]:
        self._check_not_discarded()
        return self._changes

    def _check_not_discarded(self):
        if self._discarded:
            raise DiscardedEntityError("Aggregate has been discarded")
        
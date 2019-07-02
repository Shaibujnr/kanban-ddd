import datetime
import uuid
from eventsourcing.domain.model.aggregate import AggregateRoot
from eventsourcing.domain.model.decorators import attribute
from eventsourcing.domain.model.events import DomainEvent


class WorkItem(AggregateRoot):
    """Workitem class for holding tasks
    """

    class Event(AggregateRoot.Event, DomainEvent):
        """Base class for all workitem events"""

    class Created(Event, AggregateRoot.Created):
        """Event for workitem created"""

    class AttributeChanged(Event, AggregateRoot.AttributeChanged):
        """Event for attribute changed"""

    def __init__(self, name: str, content: str, duedate: datetime.date, 
        board_id: uuid.UUID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._content = content
        self._duedate = duedate
        self._board_id = board_id

    @attribute
    def name(self) -> str:
        """ workitem name"""

    @attribute
    def content(self) -> str:
        """ workitem content """

    @attribute
    def duedate(self) -> datetime.date:
        """ workitem duedate """

    # TODO use methods that actually depict meaning on the domain and trigger the
    # appropraite event rather than use attributes

    @property
    def board_id(self) -> uuid.UUID:
        return self._board_id

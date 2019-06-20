import datetime
import uuid

utc_now = datetime.datetime.now(datetime.timezone.utc).timestamp()


class DomainEvent:
    """
    Base class for all kanban events, all events are value objects

    Attributes:
        event_name: Name of the event which is the class name
        timestamp: Time event was created
    """
    aggregate_uuid: uuid.UUID
    event_name: str
    timestamp: datetime.datetime
    data: dict
    attribute_name: str
    attribute_value: object
    
    def __init__(self, aggregate_uuid: uuid.UUID,  **kwargs):
        self.__dict__["aggregate_uuid"] = aggregate_uuid
        self.__dict__["event_name"] = self.__class__.__name__
        self.__dict__["timestamp"] = utc_now
        self.__dict__["data"] = kwargs
        self.__dict__.update(kwargs)

    def __setattr__(self, key, value):
        raise AttributeError("Domain events attributes are read only")

    def __eq__(self, event):
        if isinstance(self, event.__class__):
            return self.__dict__ == event.__dict__
        return False

    def as_dict(self):
        return {
            'aggregate_uuid': str(self.aggregate_uuid),
            'event_name': self.event_name,
            'timestamp': self.timestamp,
            'data': self.data
        }


class EntityCreatedEvent(DomainEvent):
    def __init__(self, uuid: uuid.UUID, **kwargs):
        super().__init__(uuid,**kwargs)


class EntityDiscardedEvent(DomainEvent):
    pass


class AttributeChangedEvent(DomainEvent):
    def __init__(self, aggregate_uuid: uuid.UUID, attribute_name: str, attribute_value: object):
        super().__init__(
            aggregate_uuid, 
            attribute_name=attribute_name, 
            attribute_value=attribute_value
        )

class BoardCreatedEvent(EntityCreatedEvent):
    def __init__(self, board_uuid: uuid.UUID, board_name: str, description: str):
        super().__init__(board_uuid, board_name=board_name, description=description)


class WorkItemCreatedEvent(EntityCreatedEvent):
    def __init__(self, item_uuid: uuid.UUID, item_name: str, content: str, duedate: datetime.date):
        super().__init__(item_uuid, item_name=item_name, content=content, duedate=duedate)

class ColumnAddedEvent(DomainEvent):
    def __init__(self, board_uuid: uuid.UUID,  column_name:str):
        super().__init__(board_uuid, column_name=column_name)


class ColumnRemovedEvent(DomainEvent):
    def __init__(self, board_uuid: uuid.UUID, column_id: uuid.UUID):
        super().__init__(board_uuid, column_id=column_id)


class ColumnInsertedEvent(DomainEvent):
    def __init__(self, board_uuid: uuid.UUID, index: int, column_name: str):
        super().__init__(board_uuid, index=index, column_name=column_name)


class WorkItemScheduledEvent(DomainEvent):
    def __init__(self, board_uuid: uuid.UUID, item_id: uuid.UUID):
        super().__init__(board_uuid, item_id=item_id)


class WorkItemAdvancedEvent(DomainEvent):
    def __init__(self, board_uuid: uuid.UUID, item_id: uuid.UUID, 
        source_column_index: int):
        super().__init__(
            board_uuid,
            item_id=item_id, 
            source_column_index=source_column_index
        )

class WorkItemRetiredEvent(DomainEvent):
    def __init__(self, board_uuid: uuid.UUID, item_id: uuid.UUID):
        super().__init__(board_uuid, item_id=item_id)


__event_handlers = {}


def subscribe(handler, event_predicate):
    """
    Subscribe to events

    Args:
        handler: a callable funtion which handles the passed event
        event_predicate: a callable which determines if the event should be handled
    """
    if event_predicate not in __event_handlers:
        __event_handlers[event_predicate] = set()
    __event_handlers[event_predicate].add(handler)


def unsubscribe(handler, event_predicate):
    """Unsubscribe from events.

    Args:
        handler: The subscriber to disconnect.
        event_predicate: The callable predicate which was used to identify the events to which to subscribe.
    """
    if event_predicate in __event_handlers:
        __event_handlers[event_predicate].discard(handler)


def publish(event):
    """
    Send an event to all subscribers.
     
     Each subscriber will receive each event only once, even if it has been subscribed multiple
     times, possibly with different predicates.

     Args:
         event: The object to be tested against by all registered predicate functions and sent to
         all matching subscribers.
    """
    matching_handlers = set()
    for event_predicate, handlers in __event_handlers.items():
        if event_predicate(event):
            matching_handlers.update(handlers)
    for handler in matching_handlers:
        handler(event)

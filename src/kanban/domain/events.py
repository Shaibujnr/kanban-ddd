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
    def __init__(self, originator_id: uuid.UUID, originator_version: int, **kwargs):
        self.__dict__["originator_id"] = originator_id
        self.__dict__["originator_version"] = originator_version
        self.__dict__["event_name"] = self.__class__.__name__
        self.__dict__["timestamp"] = utc_now
        self.__dict__.update(kwargs)

    def __setattr__(self, key, value):
        raise AttributeError("Domain events attributes are read only")

    def __eq__(self, event):
        if isinstance(self, event.__class__):
            return self.__dict__ == event.__dict__
        return False


class EntityCreatedEvent(DomainEvent):
    def __init__(self, **kwargs):
        super().__init__(uuid.uuid4(), 0, **kwargs)


class EntityDiscardedEvent(DomainEvent):
    pass


class AttributeChangedEvent(DomainEvent):
    def __init__(self, entity_id: uuid.UUID, entity_version: int, attribute_name: str, attribute_value: object):
        super().__init__(
            entity_id, 
            entity_version, 
            attribute_name=attribute_name, 
            attribute_value=attribute_value
        )

class BoardCreatedEvent(EntityCreatedEvent):
    def __init__(self, board_name: str, description: str):
        super().__init__(board_name=board_name, description=description)


class WorkItemCreatedEvent(EntityCreatedEvent):
    def __init__(self, item_name: str, content: str, duedate: datetime.date):
        super().__init__(item_name=item_name, content=content, duedate=duedate)

class ColumnAddedEvent(DomainEvent):
    def __init__(self, board_id: uuid.UUID, board_version: int, column_name:str):
        super().__init__(board_id, board_version, column_name=column_name)


class ColumnRemovedEvent(DomainEvent):
    def __init__(self, board_id: uuid.UUID, board_version: int, column_id: uuid.UUID):
        super().__init__(board_id, board_version, column_id=column_id)


class ColumnInsertedEvent(DomainEvent):
    def __init__(self, board_id: uuid.UUID, board_version: int, index: int, column_name: str):
        super().__init__(board_id, board_version, index=index, column_name=column_name)


class WorkItemScheduledEvent(DomainEvent):
    def __init__(self, board_id: uuid.UUID, board_version: int, item_id: uuid.UUID):
        super().__init__(board_id, board_version, item_id=item_id)


class WorkItemAdvancedEvent(DomainEvent):
    def __init__(self, board_id: uuid.UUID, board_version: int, item_id: uuid.UUID, 
        source_column_index: int):
        super().__init__(
            board_id,
            board_version,
            item_id=item_id, 
            source_column_index=source_column_index
        )

class WorkItemRetiredEvent(DomainEvent):
    def __init__(self, board_id: uuid.UUID, board_version: int, item_id: uuid.UUID):
        super().__init__(board_id, board_version, item_id=item_id)

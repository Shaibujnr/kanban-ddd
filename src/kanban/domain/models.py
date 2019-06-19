import uuid
import datetime
import typing
import functools
import kanban.domain.events as ev
from .entity import Entity
from .aggregate import AggregateRoot
from kanban.errors import ConstraintError, ColumnNotEmptyError, DiscardedEntityError
from kanban.infrastructure.eventstore import EventStream


def _validate_content(content: str) -> str:
    if not content or len(content) < 1:
        raise ValueError("Can not be empty")
    return content


def method_dispatch(func):
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


class WorkItem(AggregateRoot):

    @method_dispatch
    def apply(self, event):
        raise ValueError("Unrecognised event")

    @apply.register(ev.WorkItemCreatedEvent)
    def _(self, event: ev.WorkItemCreatedEvent):
        self._name = event.item_name
        self._content = event.content
        self._duedate = event.duedate

    @apply.register(ev.AttributeChangedEvent)
    def _(self, event: ev.AttributeChangedEvent):
        self.__dict__[event.attribute_name] = event.attribute_value   

    @property
    def name(self) -> str:
        """Return item name if not discarded"""
        self._check_not_discarded()
        return self._name

    @property
    def content(self) -> str:
        """Return item property if not discarded"""
        self._check_not_discarded()
        return self._content

    @property
    def duedate(self) -> datetime.date:
        """Return item due date if not discarded"""
        self._check_not_discarded()
        return self._duedate

    @classmethod
    def create(cls, name: str, content: str, duedate: datetime.date):
        item_id: uuid.UUID = uuid.uuid4()
        name = _validate_content(name)
        content = _validate_content(content)
        duedate = cls._validate_date(duedate)
        event = ev.WorkItemCreatedEvent(item_id, name, content, duedate)
        stream = EventStream(item_id, [event], 0)
        instance = cls(stream)
        instance._changes = [event]
        return instance

    @staticmethod
    def _validate_date(date: datetime.date):
        if date < datetime.date.today():
            raise ValueError("Duedate cannot be in the past")
        return date

    def _can_discard(self) -> bool:
        return True

    def discard(self) -> None:
        if self._can_discard():
            self._discarded = True

    def update_name(self, name: str) -> None: 
        """Update workitem name"""
        self._check_not_discarded()
        name = _validate_content(name)
        event = ev.AttributeChangedEvent(self.uuid, '_name', name)
        self.apply(event)
        self.changes.append(event)

    def update_content(self, content: str):
        """Update workitem content"""
        self._check_not_discarded()
        content = _validate_content(content)
        event = ev.AttributeChangedEvent(self.uuid,  '_content', content)
        self.apply(event)
        self.changes.append(event)

    def update_duedate(self, date: datetime.date):
        """Update duedate for the workitem"""
        self._check_not_discarded()
        duedate = self._validate_date(date)
        event = ev.AttributeChangedEvent(self.uuid, '_duedate', duedate)
        self.apply(event)
        self.changes.append(event)


class Column(Entity):
    def __init__(self, name: str):
        super().__init__(uuid.uuid4())
        self._name = name
        self._work_item_ids = []

    @property
    def name(self):
        self._check_not_discarded()
        return self._name

    @property
    def work_item_ids(self) -> list:
        self._check_not_discarded()
        return self._work_item_ids

    @property
    def is_empty(self) -> bool:
        self._check_not_discarded()
        return len(self._work_item_ids) == 0

    def __contains__(self, item: WorkItem):
        for item_id in self._work_item_ids:
            if item.uuid == item_id:
                return True
        return False

    def update_name(self, name: str):
        """Update column name"""
        self._check_not_discarded()
        if not name or len(name) < 1:
            raise ValueError("Column name cannot be empty")
        self._name = name


class Board(AggregateRoot):
    def __init__(self, stream: EventStream):
        self._columns = []
        super().__init__(stream)
        

    @property
    def name(self) -> str:
        self._check_not_discarded()
        return self._name

    @property
    def description(self) -> str:
        self._check_not_discarded()
        return self._description

    @classmethod
    def create(cls, name: str, description: str):
        board_uuid: uuid.UUID = uuid.uuid4()
        name = _validate_content(name)
        description = _validate_content(description)
        event = ev.BoardCreatedEvent(board_uuid, name, description)
        stream = EventStream(board_uuid, [event], 0)
        instance = cls(stream)
        instance._changes = [event]
        return instance

    def __contains__(self, item: WorkItem):
        for column in self._columns:
            if item in column:
                return True
        return False

    def _can_discard(self) -> bool:
        return True

    def discard(self) -> None:
        if self._can_discard():
            self._discarded = True


    def _column_with_id(self, column_id: uuid.UUID) -> Column:
        for column in self._columns:
            if column.uuid == column_id:
                return column
        raise ValueError(f"Column with id {column_id} not on board")

    def _column_index_with_id(self, column_id: uuid.UUID) -> int:
        for index, column in self._columns:
            if column.uuid == column_id:
                return index
        raise ValueError(f"Column with id {column_id} not on board")

    def _can_remove_column(self, column: Column):
        if column not in self._columns:
            raise ValueError(f"Column with id {Column} not on board")
        return True if column.is_empty else False

    def _find_work_item_by_id(self, item_id: uuid.UUID):
        for column_index, column in enumerate(self._columns):
            try:
                priority = column.work_item_ids.index(item_id)
                return column_index, priority
            except ValueError:
                pass
        raise ValueError(f"Work Item with id={item_id} is not on board")
            

    def update_name(self, name: str):
        self._check_not_discarded()
        if not name or len(name) < 1:
            raise ValueError("Board name can not be empty")
        event = ev.AttributeChangedEvent(self.uuid,  '_name', name)
        self.apply(event)
        self.changes.append(event)

    def update_description(self, desciption: str):
        self._check_not_discarded()
        if not desciption or len(desciption) < 1:
            raise ValueError("Board description can not be empty")
        event = ev.AttributeChangedEvent(self.uuid,  '_description', desciption)
        self.apply(event)
        self.changes.append(event)

    def add_new_column(self, column_name: str):
        """Add a new column to the board"""
        self._check_not_discarded()
        column_name = _validate_content(column_name)
        event = ev.ColumnAddedEvent(self.uuid, column_name)
        self.apply(event)
        self.changes.append(event)

    def insert_column_before(self, target_column_id: uuid.UUID, name: str):
        """
        Insert a column before(to the left of) column with target_column_id
        """
        self._check_not_discarded()
        name = _validate_content(name)
        target_column_index = self._column_index_with_id(target_column_id)
        event = ev.ColumnInsertedEvent(self.uuid,  target_column_index, name)
        self.app(event)
        self.changes.append(event)

    def insert_column_after(self, target_column_id: uuid.UUID, name:str):
        """
        Insert a column after(to the right of) column with target_column_id
        """
        self._check_not_discarded()
        name = _validate_content(name)
        target_column_index = self._column_index_with_id(target_column_id)
        event = ev.ColumnInsertedEvent(self.uuid,  target_column_index+1, name)
        self.app(event)
        self.changes.append(event)

    def remove_column(self, column: Column):
        self._check_not_discarded()
        if self._can_remove_column(column):
            event = ev.ColumnRemovedEvent(self.uuid,  column.uuid)
            self.apply(event)
            self.changes.append(event)
        raise ColumnNotEmptyError(f"Cannot remove column {column.uuid}")

    def remove_column_with_id(self, column_id: uuid.UUID):
        self._check_not_discarded()
        column: Column = self._column_with_id(column_id)
        self.remove_column(column)

    def schedule_work_item(self, item: WorkItem):
        """Queue workitem on first column"""
        self._check_not_discarded()
        if item.discarded: # ensure item is still in use
            raise DiscardedEntityError(f"Workitem {item.uuid} is no longer in use")

        if len(self._columns) < 1: # ensure board has columns
            raise ConstraintError("Board has no columns")

        if item in self: # ensure item not already on board
            raise ConstraintError(f"Workitem {item.uuid} already on board")
        
        first_column: Column = self._columns[0]
        if first_column.discarded: # ensure first column is not discarded
            raise DiscardedEntityError(f"Column {first_column.uuid} is no longer in use")
        event = ev.WorkItemScheduledEvent(self.uuid, item.uuid)
        self.apply(event)
        self.changes.append(event)

    def advance_work_item(self, item: WorkItem):
        """Move workitem to the next column"""
        self._check_not_discarded()
        if item.discarded: # ensure item is still in use
            raise DiscardedEntityError(f"Workitem {item.uuid} is no longer in use")
        source_column_index, priority = self._find_work_item_by_id(item.uuid)
        destination_column_index: int = source_column_index + 1
        if destination_column_index >= len(self._columns):
            raise ConstraintError(f"Cannot advance workitem {item.uuid} from last column")
        destination_column: Column = self._columns[destination_column_index]
        if destination_column.discarded:
            raise DiscardedEntityError(f"Column {destination_column.uuid} is no longer in use")
        event = ev.WorkItemAdvancedEvent(self.uuid, item.uuid, source_column_index)
        self.apply(event)
        self.changes.append(event)

    def retire_work_item(self, item: WorkItem):
        """ Retire work item from the last column"""
        self._check_not_discarded()
        if item.discarded: # ensure item is still in use
            raise DiscardedEntityError(f"Workitem {item.uuid} is no longer in use")
        try:
            priority = self._columns[-1].work_item_ids.index(item.uuid)
        except IndexError:
            raise ConstraintError(f"Cannot retire item {item.uuid} from a board with no columns")
        except ValueError:
            raise ConstraintError(f"{item.uuid} not available for retiring from last column of board")
        event = ev.WorkItemRetiredEvent(self.uuid,  item.uuid)
        self.apply(event)
        self.changes.append(event)
    
    @method_dispatch
    def apply(self, event):
        raise NotImplementedError("Unrecognized event")

    @apply.register(ev.BoardCreatedEvent)
    def _(self, event: ev.BoardCreatedEvent):
        self._name = event.board_name
        self._description = event.description

    @apply.register(ev.ColumnAddedEvent)
    def _(self, event: ev.ColumnAddedEvent):
        column: Column = Column(event.column_name)
        self._columns.append(column)

    @apply.register(ev.ColumnInsertedEvent)
    def _(self, event: ev.ColumnInsertedEvent):
        column: Column = Column(event.column_name)
        self._columns.insert(event.index, column)

    @apply.register(ev.ColumnRemovedEvent)
    def _(self, event: ev.ColumnRemovedEvent):
        column: Column = self._column_with_id(event.column_id)
        self._columns.remove(column)

    @apply.register(ev.WorkItemScheduledEvent)
    def _(self, event: ev.WorkItemScheduledEvent):
        first_column: Column = self._columns[0]
        first_column.work_item_ids.append(event.item_id)

    @apply.register(ev.WorkItemAdvancedEvent)
    def _(self, event: ev.WorkItemAdvancedEvent):
        source_column: Column = self._columns[event.source_column_index]
        next_column: Column = self._columns[event.source_column_index+1]
        source_column.work_item_ids.remove(event.item_id)
        next_column.work_item_ids.append(event.item_id)
        

    @apply.register(ev.WorkItemRetiredEvent)
    def _(self, event: ev.WorkItemRetiredEvent):
        last_column: Column = self._columns[-1]
        last_column.work_item_ids.remove(event.item_id)

    @apply.register(ev.AttributeChangedEvent)
    def _(self, event: ev.AttributeChangedEvent):
        self.__dict__[event.attribute_name] = event.attribute_value        
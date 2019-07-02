import datetime
import typing
import uuid
from eventsourcing.domain.model.aggregate import AggregateRoot
from eventsourcing.domain.model.events import DomainEvent
from eventsourcing.domain.model.entity import DomainEntity
from eventsourcing.domain.model.decorators import attribute


class Column(DomainEntity):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not name:
            raise Exception("Column name must cannot be empty")
        self._name = name
        self._workitem_ids = []

    def __contains__(self, workitem):
        for workitem_id in self.workitem_ids:
            if workitem.id == workitem_id:
                return True
        return False

    @classmethod
    def __create__(cls, *args, **kwargs):
        """override this method to prevent event from being triggered"""

    @property
    def name(self) -> str:
        return self._name

    @property
    def workitem_ids(self):
        return self._workitem_ids

    @property
    def is_empty(self) -> bool:
        return len(self.workitem_ids) == 0

    def change_name(self, name: str):
        self.__assert_not_discarded__()
        if not name:
            raise Exception("Column name must cannot be empty")
        self._name = name


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


class Board(AggregateRoot):
    """Board class"""

    class Event(AggregateRoot.Event, DomainEvent):
        """Base class for all board events """

    class Created(Event, AggregateRoot.Created):
        """Board created event"""

    class AttributeChanged(Event, AggregateRoot.AttributeChanged):
        """Board attribute changed event"""

    class Discarded(Event, AggregateRoot.Discarded):
        """Board discarded event """

    class ColumnAdded(Event):
        """A new column has been added"""
        def mutate(self, obj):
            column = Column(id=self.column_id, name=self.column_name)
            obj._columns.append(column)

    class ColumnInserted(Event):
        """A new column has been inserted in a specified position"""
        def mutate(self, obj):
            column = Column(id=self.column_id, name=self.column_name)
            obj._columns.insert(self.column_position, column)

    class ColumnDeleted(Event):
        """An existing column has been deleted """
        def mutate(self, obj):
            column = obj._columns[self.column_position]
            obj._columns.remove(column)

    class WorkItemScheduled(Event):
        """Board has scheduled a workitem"""
        def mutate(self, obj):
            first_column: Column = obj._columns[0]
            first_column.workitem_ids.append(self.workitem_id)

    class WorkItemUncheduled(Event):
        """Board has unscheduled a workitem"""


    class WorkItemAdvanced(Event):
        """Board has advanced workitem to the next column"""
        def mutate(self, obj):
            target_column: Column = obj._columns[self.workitem_column_position]
            target_column.workitem_ids.remove(self.workitem_id)
            nex_column: Column = obj._columns[self.workitem_column_position+1]
            nex_column.workitem_ids.append(self.workitem_id)

    class WorkItemRetired(Event):
        """Board has retired workitem from the last column"""
        def mutate(self, obj):
            last_column: Column = obj._columns[-1]
            last_column.workitem_ids.remove(self.workitem_id)
            obj._retired_workitem_ids.append(self.workitem_id)
    
    def __init__(self, name: str, description: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._description = description
        self._columns: typing.List[Column] = []
        self._retired_workitem_ids: typing.List[uuid.UUID] = []

    @attribute
    def name(self):
        """Name of the board """

    @attribute
    def description(self):
        """Description of the board"""

    @property
    def columns(self):
        """Board columns"""
        return self._columns

    @property
    def retired_workitem_ids(self):
        """Retired worktitem ids"""
        return self._retired_workitem_ids

    def __validate_column_name(self, name: str) -> None:
        for column in self._columns:
            if column.name == name:
                raise Exception('Column name already exists')
        return name

    def __find_column_index(self, column_id: uuid.UUID) -> int:
        for index, column in enumerate(self._columns):
            if column.id == column_id:
                return index
        raise Exception("Column is not on board")

    def __find_column(self, column_id: uuid.UUID) -> Column:
        for column in self._columns:
            if column.id == column_id:
                return column
        raise Exception("Column is not on board")

    def __get_workitem_column_index(self, workitem: WorkItem):
        for column in self._columns:
            if workitem in column:
                return self._columns.index(column)
        raise Exception(f"Workitem {workitem.id} not scheduled")


    def create_work_item(self, item_name: str, item_content: str, item_duedate: datetime.date) -> WorkItem:
        return WorkItem.__create__(
            name=item_name,
            content=item_content,
            duedate=item_duedate,
            board_id=self.id
        )

    def add_column(self, name: str) -> Column:
        """create a new column on the board"""
        column_id = uuid.uuid4()
        name = self.__validate_column_name(name)
        self.__trigger_event__(self.ColumnAdded, column_id=column_id, column_name=name)

    def insert_column_before(self, name:str, target_column_id: uuid.UUID):
        """add a column before the specified column"""
        column_index = self.__find_column_index(target_column_id)
        column_id = uuid.uuid4()
        name = self.__validate_column_name(name)
        self.__trigger_event__(
            self.ColumnInserted,
            column_id=column_id, 
            column_position=column_index, 
            column_name=name
        )

    def insert_column_after(self, name:str, target_column_id: uuid.UUID):
        """add a column after the specified column"""
        column_index = self.__find_column_index(target_column_id)
        name = self.__validate_column_name(name)
        column_id = uuid.uuid4()
        self.__trigger_event__(
            self.ColumnInserted, 
            column_position=column_index+1, 
            column_name=name,
            column_id=column_id
        )

    def delete_column(self, column_id: uuid.UUID):
        """Deleting a column from the board

        Columns can only be deleted if they are empty 
        """
        column = self.__find_column(column_id)
        if not column.is_empty:
            raise Exception(f"Column {column_id} is not empty")
        column_position = self._columns.index(column)
        self.__trigger_event__(self.ColumnDeleted, column_position=column_position)
        

    def schedule_work_item(self, workitem: WorkItem):
        """Schedule a workitem"""
        if len(self._columns) < 1:
            raise Exception("Board has no columns")
        if(workitem.board_id != self.id):
            raise Exception(f"Workitem {workitem.id} has been scheduled by another board")
        for column in self.columns:
            if workitem.id in column:
                raise Exception(f"Workitem {workitem.id} has already been scheduled")
        self.__trigger_event__(self.WorkItemScheduled, workitem_id=workitem.id)

    def advance_work_item(self, workitem: WorkItem):
        """Advance workitem from its current column to the next"""
        workitem_column_index: int = self.__get_workitem_column_index(workitem)
        if workitem_column_index == len(self._columns)-1:
            raise  Exception(f"Workitem {workitem.id} is on the last column")
        target_column: Column = self._columns[workitem_column_index]
        workitem_position_in_column = target_column.workitem_ids.index(workitem.id)
        self.__trigger_event__(
            self.WorkItemAdvanced, 
            workitem_column_position=workitem_column_index, 
            workitem_id=workitem.id
        )
    
    def retire_work_item(self, workitem: WorkItem):
        """Retire workitem from last column"""
        workitem_column_index = self.__get_workitem_column_index(workitem)
        if workitem_column_index != len(self._columns)-1:
            # check if workitem is on last column
            raise Exception(f"Workitem {workitem.id} is not on the last column")
        self.__trigger_event__(self.WorkItemRetired, workitem_id=workitem.id)

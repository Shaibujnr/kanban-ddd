import uuid
from .entity import Entity
import datetime


class WorkItem(Entity):
    def __init__(self, name: str, content: str, duedate: datetime.date):
        super().__init__(uuid.uuid4(), 0)
        self._name = name
        self._content = content
        self._duedate = duedate
    
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

    def update_name(self, name: str) -> None: 
        """Update workitem name"""
        self._check_not_discarded()
        if not name or len(name) < 1:
            raise ValueError("Workitem name cannot be empty")
        self._name = name

    def update_content(self, content: str):
        """Update workitem content"""
        self._check_not_discarded()
        if not content or len(content) < 1:
            raise ValueError("Workitem content cannot be empty")
        self._content = content

    def update_duedate(self, date: datetime.date):
        """Update duedate for the workitem"""
        self._check_not_discarded()
        self._duedate = date


class Column(Entity):
    def __init__(self, name: str):
        super().__init__(uuid.uuid4(),0)
        self._name = name
        self._work_item_ids = []

    @property
    def name(self):
        self._check_not_discarded()
        return self._name

    


# import uuid
# import datetime
# from .entity import Entity
# from .errors import ConstraintError

# # ================ Aggregate Root Entities ===============
# class Board(Entity):
#     """
#     A kanban board which tracks the progress of workitems in a step-wise process.
#     """

#     def __init__(self, name: str, description: str):
#         """Initialize a board"""
#         super.__init__(uuid.uuid4(), 0)
#         self._name =  name
#         self._description = description
#         self._columns = []

#     @property
#     def name(self):
#         """Name of board"""
#         self._check_not_discarded()
#         return self._name

#     @name.setter
#     def name(self, value):
#         self._check_not_discarded()
#         if len(value) <= 4 or len(value) > 15:
#             raise ConstraintError("Name of board must be between 5-15 characters")
#         self._name = value 

#     @property
#     def desciption(self):
#         """Board description"""
#         self._check_not_discarded()
#         return self._description

#     @desciption.setter
#     def description(self, value: str):
#         """Description of board, usually the purpose of the board"""
#         self._check_not_discarded()
#         if len(value) < 10 or len(value) > 100:
#             raise ConstraintError("Board description must be between 10 to 100 characters")
#         self._description = value

#     def __contains__(self, workitem: WorkItem):
#         for column in self._columns:
#             if workitem in column:
#                 return True
#         return False

#     def _find_column(self, column_id: uuid.UUID) -> Column:
#         for column in self._columns:
#             if column.id == column_id:
#                 return column
#         raise ValueError(f"Column {uuid} is not in board")

#     def _find_column_by_name(self, column_name: str) -> Column:
#         for column in self._columns:
#             if column.name == column_name:
#                 return column
#         raise ValueError(f"Column with name {column_name} is not in board")

#     def _find_column_index(self, column: Column):
#         for index, column in enumerate(self._columns):
#             if column == column:
#                 return index
#         raise ValueError(f"Column {column.id} is not on board")

#     def _find_column_index_by_id(self, column_id: int):
#         for index, column in enumerate(self._columns):
#             if column.id == column_id:
#                 return index
#         raise ValueError(f"Column {column.id} is not on board")

#     def add_column(self, column: Column) -> None:
#         """Add a new column to the board"""
#         self._check_not_discarded()
#         self._columns.append(column)

#     def remove_column(self, column_id: uuid.UUID) -> None:
#         """Remove a column from the board by id"""
#         self._check_not_discarded()
#         target_column = self._find_column(column_id)
#         self._columns.remove(target_column)

#     def remove_column_with_name(self, column_name: str) -> None:
#         """Remove a column from the board by name"""
#         self._check_not_discarded()
#         target_column = self._find_column_by_name(column_name)
#         self._columns.remove(target_column)

    
#     def insert_column_before(self, target_column_id: uuid.UUID, name: str): 
#         """Insert a column before the column in target id """
#         self._check_not_discarded()
#         column_index = self._find_column_index_by_id(target_column_id)
#         self._columns.insert(column_index, Column(name))

#     def insert_column_after(self, column_id: uuid.UUID, name: str):
#          """Insert a column after the column in target id """
#         self._check_not_discarded()
#         column_index = self._find_column_index_by_id(target_column_id)
#         self._columns.insert(column_index+, Column(name))

#     def schedule_work_item(self, workitem: WorkItem) -> None:
#         self._check_not_discarded()
#         workitem._check_not_discarded()
#         if len(self._columns) < 1:
#             raise ConstraintError("Board has no columns")
#         if workitem in self:
#             raise ConstraintError(f"Workitem {workitem.id} already exists")
#         first_column = self._columns[0]
#         first_column._check_not_discarded()
#         first_column._work_item_ids.add(workitem.id)

#     def advance_work_item(self, workitem: WorkItem) -> None:
#         pass

#     def reverse_work_item(self, workitem: WorkItem) -> None:
#         pass



# class WorkItem(Entity):
    
#     def __init__(self, name: str, content: str, duedate):
#         self._name = name
#         self._content = content
#         self._duedate = duedate


# # ================== Entities =========================
# class Column(Entity):
    
#     def __init__(self, name):
#         self._name = name
#         self._work_item_ids = []



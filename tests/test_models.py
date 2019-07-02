import datetime
import pytest
import uuid
from kanban.domain.models import WorkItem, Column, Board
import kanban.errors as kanban_error


def test_create_workitem():
	item: WorkItem = WorkItem.__create__(
		name='hello', 
		content="hi", 
		duedate=datetime.date.today(),
		board_id=uuid.uuid4()
	)
	assert item.id, item.id
	assert item.__version__ == 0, item.__version__
	assert len(item.__pending_events__) > 0
	assert item.board_id

def test_update_workitem():
	item: WorkItem = WorkItem.__create__(
		name="initial", 
		content="lorem", 
		duedate=datetime.date.today(),
		board_id=uuid.uuid4()
	)
	assert item.id, item.id
	assert item.__version__ == 0, item.__version__
	assert len(item.__pending_events__)   == 1
	item.name = "final name"
	assert len(item.__pending_events__) == 2
	assert item.name == "final name"
	item.content = item.content+" ipsum"
	assert len(item.__pending_events__) == 3
	assert item.content == "lorem ipsum"
	assert item.board_id


def test_create_column():
	column = Column.__create__(id=2, name='column name')
	assert not column


def test_init_column():
	column = Column(id=uuid.uuid4(), name='namec')
	assert column.id
	assert column.name


def test_column_contains_workitem():
	item: WorkItem = WorkItem.__create__(
		name='item name',
		content='supposed item content',
		duedate=datetime.date.today(),
		board_id=uuid.uuid4()
	)
	column = Column(id=uuid.uuid4(), name='column name')
	assert item not in column
	column._workitem_ids.append(item.id)
	assert item in column


def test_create_board():
	board: Board = Board.__create__(name='hello', description='board desc')
	assert len(board._columns) == 0
	assert board.id
	assert board.name == 'hello'
	assert board.description == "board desc"


def test_update_board():
	board: Board = Board.__create__(name='board name', description='board desc')
	assert board.id
	assert len(board.__pending_events__) == 1
	assert board.name == 'board name'
	assert board.description == 'board desc'
	board.name = 'trello'
	assert len(board.__pending_events__) == 2
	assert board.name == 'trello'
	board.description = 'scrum'
	assert len(board.__pending_events__) == 3
	assert board.description == 'scrum'


def test_create_workitem_on_board():
	board: Board = Board.__create__(name='trello', description='scrum/agile')
	assert board.id
	assert len(board.__pending_events__) == 1
	item: WorkItem = board.create_work_item('ddd','domain driven design',datetime.date.today())
	assert len(board.__pending_events__) == 1
	assert item.board_id == board.id
	assert len(item.__pending_events__) == 1


def test_board_columns():
	board: Board = Board.__create__(name='trello', description='scrum')
	assert len(board.columns) == 0
	board.add_column('column one')
	assert len(board.columns) == 1
	board.add_column('column two')
	assert len(board.columns) == 2
	first_column: Column = board.columns[0]
	assert first_column.id
	board.insert_column_before('column zero', first_column.id)
	assert len(board.columns) == 3
	current_first_column: Column = board.columns[0]
	assert first_column != current_first_column
	assert current_first_column.name  == 'column zero'
	board.insert_column_after('column 1.5', first_column.id)
	assert len(board.columns) == 4
	assert board.columns[2].name == 'column 1.5'
	board.delete_column(first_column.id)
	assert len(board.columns) == 3
	assert first_column not in board.columns


def test_board_operations():
	board: Board = Board.__create__(name='trello', description='scrum')
	board.add_column('one')
	board.add_column('two')
	board.add_column('three')
	assert len(board.columns) == 3
	item: WorkItem = board.create_work_item('todo', 'tasks', datetime.date.today())
	board.schedule_work_item(item)
	assert item in board.columns[0]
	board.advance_work_item(item)
	assert item not in board.columns[0]
	assert item in board.columns[1]
	board.advance_work_item(item)
	assert item not in board.columns[0]
	assert item not in board.columns[1]
	assert item in board.columns[2]
	assert len(board.retired_workitem_ids) == 0
	board.retire_work_item(item)
	assert item not in board.columns[2]
	assert item.id in board.retired_workitem_ids


def test_schedule_item_on_board_with_no_columns(board: Board, item: WorkItem):
	with pytest.raises(Exception):
		board.schedule_work_item(item)

def test_schedule_already_scheduled_workitem(board: Board, item: WorkItem):
	board.add_column('one')
	board.schedule_work_item(item)
	with pytest.raises(Exception):
		board.schedule_work_item(item)


def test_advance_unscheduled_workitem(board: Board, item: WorkItem):
	board.add_column('one')
	with pytest.raises(Exception):
		board.advance_work_item(item)

def test_delete_non_empty_column(board: Board, item: WorkItem):
	board.add_column('one')
	board.add_column('two')
	board.schedule_work_item(item)
	board.advance_work_item(item)
	with pytest.raises(Exception):
		board.delete_column(board.columns[1])


def test_advance_workitem_from_last_column(board: Board, item: WorkItem):
	board.add_column('one')
	board.add_column('two')
	board.add_column('three')
	board.schedule_work_item(item)
	board.advance_work_item(item)
	board.advance_work_item(item)
	with pytest.raises(Exception):
		board.advance_work_item(item)


def test_retire_item_not_on_last_column(board: Board, item: WorkItem):
	board.add_column('one')
	board.add_column('two')
	board.add_column('three')
	board.schedule_work_item(item)
	with pytest.raises(Exception):
		board.retire_work_item(item)

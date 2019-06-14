import datetime
import pytest
from kanban.domain.models import WorkItem, Column, Board
import kanban.domain.errors as kanban_error


def test_init_workitem():
    workitem = WorkItem("test","this is a test workitem",datetime.date.today())
    assert not workitem.discarded
    assert workitem.version == 0
    assert workitem.id is not None


def test_update_workitem():
    wi = WorkItem("test", "content", datetime.date.today())
    assert not wi.discarded
    wi.update_content('updated content')
    assert wi.content == 'updated content'
    wi.update_name("hello")
    assert wi.name == "hello"
    wi.update_duedate(datetime.date.fromtimestamp(750057))
    assert wi.duedate != datetime.date.today()


def test_wrong_update_workitem():
    wi = WorkItem("hello", "content", datetime.date.today())
    assert not wi.discarded
    with pytest.raises(ValueError):
        wi.update_name("")

def test_init_board():
    board = Board("board", "a test board")
    assert not board.discarded
    assert board.id is not None
    assert board.name == "board"
    assert board.desciption == "a test board"
    assert len(board._columns) == 0

def test_add_column_to_board():
    board = Board("board", "test")
    assert not board.discarded
    assert len(board._columns) == 0
    board.add_new_column("column_one")
    assert len(board._columns) == 1

def test_schedule_work_item_on_board_with_no_columns():
    item = WorkItem("wi", "item content", datetime.date.today())
    board = Board('board', 'test board')
    assert board._columns == []
    with pytest.raises(kanban_error.ConstraintError):
        board.schedule_work_item(item)

def test_workitem_cycle():
    item = WorkItem("wi", "item content", datetime.date.today())
    board = Board('board', 'test board')
    assert board._columns == []
    board.add_new_column("column_one")
    board.add_new_column("column_two")
    board.add_new_column("column_three")
    assert len(board._columns) == 3
    assert item not in board
    board.schedule_work_item(item)
    assert item in board
    assert item in board._columns[0]
    board.advance_work_item(item)
    assert item not in board._columns[0]
    assert item in board._columns[1]
    board.advance_work_item(item)
    assert item not in board._columns[1]
    assert item in board._columns[2]
    board.retire_work_item(item)
    assert item not in board._columns[2]

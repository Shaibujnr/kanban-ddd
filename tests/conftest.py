import datetime
import pytest
from kanban.domain.models import Board, WorkItem


@pytest.fixture
def board():
    board: Board = Board.__create__(name='trello', description='scrum')
    assert board.id
    return board

@pytest.fixture
def item(board: Board):
    item: WorkItem = board.create_work_item("todo", 'tasks', datetime.date.today())
    assert item.board_id == board.id
    return item
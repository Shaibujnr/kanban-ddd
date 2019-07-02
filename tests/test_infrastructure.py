from kanban.domain.models import Board, WorkItem
from kanban.infrastructure import eventstore, repository

def test_eventstore(board: Board):
    assert len(eventstore.get_domain_events(board.id)) == 0
    assert len(board.__pending_events__) == 1
    board.add_column('one')
    board.add_column('two')
    board.add_column('three')
    assert len(board.__pending_events__) == 4
    eventstore.store(list(board.__pending_events__))
    assert len(eventstore.get_domain_events(board.id)) == 4


def test_repository(board: Board):
    assert len(eventstore.get_domain_events(board.id)) == 0
    assert len(board.__pending_events__) == 1
    board.add_column('one')
    board.add_column('two')
    board.add_column('three')
    assert len(board.__pending_events__) == 4
    eventstore.store(list(board.__pending_events__))
    assert len(eventstore.get_domain_events(board.id)) == 4
    b: Board = repository[board.id]
    assert b.id == board.id 
    
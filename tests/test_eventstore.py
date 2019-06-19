import datetime
import json
import kanban.domain.events as ev
from kanban.infrastructure.eventstore import JsonFileEventStore
from kanban.domain.models import Board, WorkItem

def test_create_store():
    store = JsonFileEventStore('events.json')
    with open('events.json') as json_file:
        data = json.load(json_file)
        assert 'events' in data
        assert 'aggregates' in data

def test_append_to_stream():
    store = JsonFileEventStore('events.json')
    board = Board.create("hello", "description")
    board.add_new_column('hello')
    store.append_to_stream(board)
    with open('events.json') as json_file:
        data = json.load(json_file)
        assert 'events' in data
        assert 'aggregates' in data
        assert len(data['events']) == 2
        assert len(data['aggregates']) == 1


def test_load_stream():
    store = JsonFileEventStore('eventso.json')
    board = Board.create("test", "hello test")
    item = WorkItem.create("hello", "content", datetime.date.today())
    board.add_new_column('column_one')
    board.add_new_column('column_two')
    board.add_new_column('column_three')
    board.schedule_work_item(item)
    board.advance_work_item(item)
    board.advance_work_item(item)
    store.append_to_stream(board)
    store.append_to_stream(item)
    target_id = board.uuid
    stream = store.load_stream(target_id)
    istream = store.load_stream(item.uuid)
    assert stream is not None
    nb = Board(stream)
    nt = WorkItem(istream)
    assert nb.uuid == board.uuid
    assert nb.version == 1
    assert len(nb.changes) == 0
    # assert len(nb._columns) == 3


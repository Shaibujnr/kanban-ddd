import datetime
import pytest
from kanban.domain.models import WorkItem
import kanban.errors as kanban_error


def test_create_workitem():
	item: WorkItem = WorkItem.__create__(name='hello', content="hi", duedate=datetime.date.today())
	assert item.id, item.id
	assert item.__version__ == 0, item.__version__
	assert len(item.__pending_events__) > 0
	assert not item.board_id


def test_update_workitem():
	item: WorkItem = WorkItem.__create__(
		name="initial", 
		content="lorem", 
		duedate=datetime.date.today()
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
	assert not item.board_id

import datetime
import pytest
from kanban.domain.models import WorkItem


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
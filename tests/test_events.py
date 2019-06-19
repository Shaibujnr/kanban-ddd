import pytest
import uuid
from kanban.domain.events import DomainEvent


def test_event_is_value_object():
    agg_uuid = uuid.uuid4()
    data = {
        "name": "hello",
        "action": "move",
        "number": 10
    }
    event1 = DomainEvent(agg_uuid, **data)
    event2 = DomainEvent(agg_uuid, **data)
    assert event1 == event2


def test_event_as_dict():
    agg_uuid = uuid.uuid4()
    data = {
        "name": "hello",
        "action": "move",
        "number": 10
    }
    event = DomainEvent(agg_uuid, **data)
    event_dict = event.as_dict()
    print(event_dict)
    assert isinstance(event_dict, dict)
    assert "aggregate_uuid" in event_dict
    assert "event_name" in event_dict
    assert "timestamp" in event_dict
    assert "data" in event_dict
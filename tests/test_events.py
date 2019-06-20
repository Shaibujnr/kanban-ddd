import pytest
import uuid
from kanban.domain.events import DomainEvent, publish, subscribe, unsubscribe


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


def test_subscribe_event():
    def handler(event):
        published_events.append(event.__dict__)
    published_events = []
    event = DomainEvent(uuid.uuid4())
    subscribe(handler, all_events_predicate)
    assert published_events == []
    publish(event)
    assert len(published_events) == 1


def test_unsubscribe_event():
    def handler(event):
        published_events.append(event.__dict__)
    published_events = []
    event = DomainEvent(uuid.uuid4())
    subscribe(handler, all_events_predicate)
    assert published_events == []
    publish(event)
    assert len(published_events) == 1
    event2 = DomainEvent(uuid.uuid4())
    unsubscribe(handler, all_events_predicate)
    publish(event)
    assert len(published_events) == 1
    


def all_events_predicate(event):
    return isinstance(event, DomainEvent)
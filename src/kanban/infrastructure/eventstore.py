import abc
import json
import typing
import uuid
import kanban.domain.events as ev
from kanban.errors import AggregateNotFoundError, ConcurrentWriteError

class EventStream:
    events: typing.List[ev.DomainEvent]
    uuid: uuid.UUID
    version: int

    def __init__(self, uuid: uuid.UUID, events: typing.List[ev.DomainEvent], version: int):
        self._uuid = uuid
        self._events = events
        self._version = version

    @property
    def events(self):
        return self._events

    @property
    def version(self):
        return self._version

    @property
    def uuid(self):
        return self._uuid


class EventStore(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load_stream(self, aggregate_uuid: uuid.UUID) -> EventStream:
        pass
 
    @abc.abstractmethod
    def append_to_stream(self, aggregate) -> None:
        pass


class JsonFileEventStore(EventStore):
    def __init__(self, filename: str):
        self.filename = filename
        with open(self.filename, 'w') as json_file:
            data = {
                'events': [],
                'aggregates': {}
            }
            json.dump(data, json_file)

    def load_stream(self, aggregate_uuid: uuid.UUID) -> EventStream:
        with open(self.filename) as json_file:
            try:  
                data = json.load(json_file)
                events = data['events']
                event_list: typing.List[dict] = []
                expected_version = self._get_expected_version(aggregate_uuid)
                for event_dict in events:
                    print(event_dict)
                    print('\n\n')
                    print(aggregate_uuid)
                    if event_dict['aggregate_uuid'] == str(aggregate_uuid):
                        print(event_dict)
                        event_list.append(self._event_from_dict(event_dict))
                print("\n\n\ndone")
                print(event_list)
                stream = EventStream(aggregate_uuid, event_list, expected_version)
                return stream
            except Exception as e:
                print(str(e))
                raise e

    def append_to_stream(self, aggregate) -> None:
        with open(self.filename, 'r+') as json_file:
            try:  
                data: dict = json.load(json_file)
                events: typing.List[dict] = data['events']
                expected_version: int = self._get_expected_version(aggregate.uuid)
                if aggregate.version != expected_version:
                    raise ConcurrentWriteError("Concurrent write error")
                for event in aggregate.changes:
                    events.append(event.as_dict())
                data['aggregates'][str(aggregate.uuid)] = expected_version + 1
                json_file.truncate(0)
                json.dump(data, json_file, indent=4, default=str)
            except AggregateNotFoundError:
                # new aggregate save and write 
                for event in aggregate.changes:
                    events.append(event.as_dict())
                data['aggregates'][str(aggregate.uuid)] = 1
                json_file.seek(0)
                json_file.truncate(0)
                json.dump(data, json_file, indent=4, default=str)
            except Exception as e:
                print(str(e))
                raise e

    def _get_expected_version(self, aggregate_uuid: uuid.UUID) -> int:
        with open(self.filename) as json_file:
            try:  
                data = json.load(json_file)
                aggregates = data['aggregates']
                expected_version = int(aggregates[str(aggregate_uuid)])
                return expected_version
            except KeyError:
                raise AggregateNotFoundError(f"Aggregate {aggregate_uuid} not found")
            except Exception as e:
                print(str(e))
                raise e

    def _event_from_dict(self, event_dict) -> ev.DomainEvent:
        """This method is responsible for translating models to event classes instances"""
        event_uuid = event_dict['aggregate_uuid']
        class_name = event_dict['event_name']
        kwargs = event_dict['data']
        # assuming `events` is a module containing all events classes we can easily get
        # desired class by its name saved along with event data
        event_class: typing.Type[ev.DomainEvent] = getattr(ev, class_name)
        return event_class(event_uuid, **kwargs)
import uuid
from eventsourcing.infrastructure.sequenceditemmapper import SequencedItemMapper
from eventsourcing.infrastructure.eventsourcedrepository import EventSourcedRepository
from eventsourcing.infrastructure.eventstore import EventStore
from eventsourcing.infrastructure.sequenceditem import StoredEvent
from eventsourcing.infrastructure.sqlalchemy.datastore import SQLAlchemyDatastore, SQLAlchemySettings
from eventsourcing.infrastructure.sqlalchemy.manager import SQLAlchemyRecordManager
from eventsourcing.infrastructure.sqlalchemy.records import StoredEventRecord

datastore = SQLAlchemyDatastore(
    tables=(StoredEventRecord,),
    settings=SQLAlchemySettings(uri='sqlite:///mydatabase')
)

datastore.setup_connection()
datastore.setup_tables()

recordmanager = SQLAlchemyRecordManager(
    session=datastore.session,
    record_class=StoredEventRecord,
    application_name=uuid.uuid4().hex,
    contiguous_record_ids=True,
    sequenced_item_class=StoredEvent
)

sequenceitemmapper = SequencedItemMapper(
    sequenced_item_class=StoredEvent
)

eventstore = EventStore(
    record_manager=recordmanager,
    sequenced_item_mapper=sequenceitemmapper
)

repository = EventSourcedRepository(event_store=eventstore)

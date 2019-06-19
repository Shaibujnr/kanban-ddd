import uuid
from .errors import DiscardedEntityError


class Entity:
    """
    Base class for all entities.

    Attributes:
        uuid: unique identifier
        discarded: True if entity should no longer be used otherwise False
    """

    def __init__(self, uuid: uuid.UUID):
        self._uuid: uuid.UUID = uuid
        self._discarded: bool = False

    def _check_not_discarded(self):
        if self._discarded:
            raise DiscardedEntityError(f"Entity {repr(self)} is no longer in use")

    @property
    def uuid(self) -> uuid.UUID:
        """String unique identifier(uuid) for the entity"""
        self._check_not_discarded()
        return self._id

    @property
    def discarded(self) -> bool:
        """True if this entity is marked as discarded, otherwise False."""
        return self._discarded

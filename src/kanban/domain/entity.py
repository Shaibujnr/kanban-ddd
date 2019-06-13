import uuid
from .errors import DiscardedEntityError

class Entity:
    """
    Base class for all entities.

    Attributes:
        id: unique identifier
        version: integer version
        discarded: True if entity should no longer be used otherwise False
    """

    def __init__(self, id: uuid.UUID, version: int):
        self._id: uuid.UUID = id
        self._version: int = version
        self._discarded: bool = False
    
    def _increment_version(self) -> None:
        self._version += 1

    def _check_not_discarded(self):
        if self._discarded:
            raise DiscardedEntityError(f"Entity {repr(self)} is no longer in use")

    @property
    def id(self) -> uuid.UUID:
        """String unique identifier(uuid) for the entity"""
        self._check_not_discarded()
        return self._id

    @property
    def version(self) -> int:
        """Integer version for entity"""
        self._check_not_discarded()
        return self._version

    @property
    def discarded(self) -> bool:
        """True if this entity is marked as discarded, otherwise False."""
        return self._discarded

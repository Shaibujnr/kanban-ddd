class DiscardedEntityError(Exception):
    """Raises when trying to use a discarded entity."""
    pass


class ConstraintError(Exception):
    pass


class ColumnNotEmptyError(ConstraintError):
    pass

class AggregateNotFoundError(Exception):
    """Raises when the aggregate does not exist in the store"""
    pass


class ConcurrentWriteError(Exception):
    pass
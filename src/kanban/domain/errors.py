class DiscardedEntityError(Exception):
    """Raises when trying to use a discarded entity."""
    pass


class ConstraintError(Exception):
    pass


class ColumnNotEmptyError(ConstraintError):
    pass
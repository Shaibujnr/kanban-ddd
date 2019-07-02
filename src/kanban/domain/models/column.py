from eventsourcing.domain.model.entity import DomainEntity


class Column(DomainEntity):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not name:
            raise Exception("Column name must cannot be empty")
        self._name = name
        self._workitem_ids = []

    def __contains__(self, workitem):
        for workitem_id in self.workitem_ids:
            if workitem.id == workitem_id:
                return True
        return False

    @classmethod
    def __create__(cls, *args, **kwargs):
        """override this method to prevent event from being triggered"""

    @property
    def name(self) -> str:
        return self._name

    @property
    def workitem_ids(self):
        return self._workitem_ids

    @property
    def is_empty(self) -> bool:
        return len(self.workitem_ids) == 0

    def change_name(self, name: str):
        self.__assert_not_discarded__()
        if not name:
            raise Exception("Column name must cannot be empty")
        self._name = name

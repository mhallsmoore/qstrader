class AbstractEmptyDataRow(Exception):
    pass


class EmptyTickEvent(AbstractEmptyDataRow):
    pass


class EmptyBarEvent(AbstractEmptyDataRow):
    pass

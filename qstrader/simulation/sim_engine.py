from abc import ABCMeta, abstractmethod


class SimulationEngine(object):
    """
    Interface to a tradinh event simulation engine.

    Subclasses are designed to take starting and ending
    timestamps to generate events at a specific frequency.

    This is achieved by overriding __iter__ and yielding Event
    entities. These entities would include signalling an exchange
    opening, an exchange closing, as well as pre- and post-opening
    events to allow handling of cash-flows and corporate actions.

    In this way the necessary events can be carried out for
    the entities in the system, such as dividend handling,
    capital changes, performance calculations and trading
    orders.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError(
            "Should implement __iter__()"
        )

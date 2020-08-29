class PortfolioEvent(object):
    """
    Stores an individual instance of a portfolio event used to create
    an event trail to track all changes to a portfolio through time.

    Parameters
    ----------
    dt : `datetime`
        Datetime of the event.
    type : `str`
        The type of portfolio event, e.g. 'subscription', 'withdrawal'.
    description ; `str`
        Human-readable portfolio event type.
    debit : `float`
        A debit to the cash balance of the portfolio.
    credit : `float`
        A credit to the cash balance of the portfolio.
    balance : `float`
        The current cash balance of the portfolio.
    """

    def __init__(
        self,
        dt,
        type,
        description,
        debit,
        credit,
        balance
    ):
        self.dt = dt
        self.type = type
        self.description = description
        self.debit = debit
        self.credit = credit
        self.balance = balance

    def __eq__(self, other):
        if self.dt != other.dt:
            return False
        if self.type != other.type:
            return False
        if self.description != other.description:
            return False
        if self.debit != other.debit:
            return False
        if self.credit != other.credit:
            return False
        if self.balance != other.balance:
            return False
        return True

    def __repr__(self):
        return (
            "PortfolioEvent(dt=%s, type=%s, description=%s, "
            "debit=%s, credit=%s, balance=%s)" % (
                self.dt, self.type, self.description,
                self.debit, self.credit, self.balance
            )
        )

    @classmethod
    def create_subscription(cls, dt, credit, balance):
        return cls(
            dt, type='subscription', description='SUBSCRIPTION',
            debit=0.0, credit=round(credit, 2), balance=round(balance, 2)
        )

    @classmethod
    def create_withdrawal(cls, dt, debit, balance):
        return cls(
            dt, type='withdrawal', description='WITHDRAWAL',
            debit=round(debit, 2), credit=0.0, balance=round(balance, 2)
        )

    def to_dict(self):
        return {
            'dt': self.dt,
            'type': self.type,
            'description': self.description,
            'debit': self.debit,
            'credit': self.credit,
            'balance': self.balance
        }

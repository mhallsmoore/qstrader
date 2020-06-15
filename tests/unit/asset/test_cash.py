import pytest

from qstrader.asset.cash import Cash


@pytest.mark.parametrize(
    'currency,expected',
    [
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR')
    ]
)
def test_cash(currency, expected):
    """
    Tests that the Cash asset is correctly instantiated.
    """
    cash = Cash(currency)

    assert cash.cash_like
    assert cash.currency == expected

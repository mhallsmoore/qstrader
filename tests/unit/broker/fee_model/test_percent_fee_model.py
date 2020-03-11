import pytest

from qstrader.broker.fee_model.percent_fee_model import PercentFeeModel


class AssetMock(object):
    def __init__(self):
        pass


class BrokerMock(object):
    def __init__(self):
        pass


@pytest.mark.parametrize(
    "commission_pct,tax_pct,quantity,consideration,"
    "expected_commission,expected_tax,expected_total", [
        (0.0, 0.0, 100, 1000.0, 0.0, 0.0, 0.0),
        (0.002, 0.0, 100, 1000.0, 2.0, 0.0, 2.0),
        (0.0, 0.005, 100, 1000.0, 0.0, 5.0, 5.0),
        (0.001, 0.005, 100, 1000.0, 1.0, 5.0, 6.0),
        (0.001, 0.005, -100, -1000.0, 1.0, 5.0, 6.0),
        (0.002, 0.0025, -50, -8542.0, 17.084, 21.355, 38.439),
    ]
)
def test_percent_commission(
    commission_pct, tax_pct, quantity, consideration,
    expected_commission, expected_tax, expected_total
):
    """
    Tests that each method returns the appropriate
    percentage tax/commision.
    """
    pfm = PercentFeeModel(commission_pct=commission_pct, tax_pct=tax_pct)
    asset = AssetMock()
    broker = BrokerMock()

    assert pfm._calc_commission(asset, quantity, consideration, broker=broker) == expected_commission
    assert pfm._calc_tax(asset, quantity, consideration, broker=broker) == expected_tax
    assert pfm.calc_total_cost(asset, quantity, consideration, broker=broker) == expected_total

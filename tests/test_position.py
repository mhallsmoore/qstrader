import unittest

from qstrader.position import Position
from qstrader.price_parser import PriceParser


class TestRoundTripXOMPosition(unittest.TestCase):
    """
    Test a round-trip trade in Exxon-Mobil where the initial
    trade is a buy/long of 100 shares of XOM, at a price of
    $74.78, with $1.00 commission.
    """
    def setUp(self):
        """
        Set up the Position object that will store the PnL.
        """
        self.position = Position(
            "BOT", "XOM", 100,
            PriceParser.parse(74.78), PriceParser.parse(1.00),
            PriceParser.parse(74.78), PriceParser.parse(74.80)
        )

    def test_calculate_round_trip(self):
        """
        After the subsequent purchase, carry out two more buys/longs
        and then close the position out with two additional sells/shorts.

        The following prices have been tested against those calculated
        via Interactive Brokers' Trader Workstation (TWS).
        """
        self.position.transact_shares(
            "BOT", 100, PriceParser.parse(74.63), PriceParser.parse(1.00)
        )
        self.position.transact_shares(
            "BOT", 250, PriceParser.parse(74.620), PriceParser.parse(1.25)
        )
        self.position.transact_shares(
            "SLD", 200, PriceParser.parse(74.58), PriceParser.parse(1.00)
        )
        self.position.transact_shares(
            "SLD", 250, PriceParser.parse(75.26), PriceParser.parse(1.25)
        )
        self.position.update_market_value(
            PriceParser.parse(77.75), PriceParser.parse(77.77)
        )

        self.assertEqual(self.position.action, "BOT")
        self.assertEqual(self.position.ticker, "XOM")
        self.assertEqual(self.position.quantity, 0)

        self.assertEqual(self.position.buys, 450)
        self.assertEqual(self.position.sells, 450)
        self.assertEqual(self.position.net, 0)
        self.assertEqual(
            PriceParser.display(self.position.avg_bot, 5), 74.65778
        )
        self.assertEqual(
            PriceParser.display(self.position.avg_sld, 5), 74.95778
        )
        self.assertEqual(PriceParser.display(self.position.total_bot), 33596.00)
        self.assertEqual(PriceParser.display(self.position.total_sld), 33731.00)
        self.assertEqual(PriceParser.display(self.position.net_total), 135.00)
        self.assertEqual(PriceParser.display(self.position.total_commission), 5.50)
        self.assertEqual(PriceParser.display(self.position.net_incl_comm), 129.50)

        self.assertEqual(
            PriceParser.display(self.position.avg_price, 3), 74.665
        )
        self.assertEqual(PriceParser.display(self.position.cost_basis), 0.00)
        self.assertEqual(PriceParser.display(self.position.market_value), 0.00)
        self.assertEqual(PriceParser.display(self.position.unrealised_pnl), 0.00)
        self.assertEqual(PriceParser.display(self.position.realised_pnl), 129.50)


class TestRoundTripPGPosition(unittest.TestCase):
    """
    Test a round-trip trade in Proctor & Gamble where the initial
    trade is a sell/short of 100 shares of PG, at a price of
    $77.69, with $1.00 commission.
    """
    def setUp(self):
        self.position = Position(
            "SLD", "PG", 100,
            PriceParser.parse(77.69), PriceParser.parse(1.00),
            PriceParser.parse(77.68), PriceParser.parse(77.70)
        )

    def test_calculate_round_trip(self):
        """
        After the subsequent sale, carry out two more sells/shorts
        and then close the position out with two additional buys/longs.

        The following prices have been tested against those calculated
        via Interactive Brokers' Trader Workstation (TWS).
        """
        self.position.transact_shares(
            "SLD", 100, PriceParser.parse(77.68), PriceParser.parse(1.00)
        )
        self.position.transact_shares(
            "SLD", 50, PriceParser.parse(77.70), PriceParser.parse(1.00)
        )
        self.position.transact_shares(
            "BOT", 100, PriceParser.parse(77.77), PriceParser.parse(1.00)
        )
        self.position.transact_shares(
            "BOT", 150, PriceParser.parse(77.73), PriceParser.parse(1.00)
        )
        self.position.update_market_value(
            PriceParser.parse(77.72), PriceParser.parse(77.72)
        )

        self.assertEqual(self.position.action, "SLD")
        self.assertEqual(self.position.ticker, "PG")
        self.assertEqual(self.position.quantity, 0)

        self.assertEqual(self.position.buys, 250)
        self.assertEqual(self.position.sells, 250)
        self.assertEqual(self.position.net, 0)
        self.assertEqual(
            PriceParser.display(self.position.avg_bot, 3), 77.746
        )
        self.assertEqual(
            PriceParser.display(self.position.avg_sld, 3), 77.688
        )
        self.assertEqual(PriceParser.display(self.position.total_bot), 19436.50)
        self.assertEqual(PriceParser.display(self.position.total_sld), 19422.00)
        self.assertEqual(PriceParser.display(self.position.net_total), -14.50)
        self.assertEqual(PriceParser.display(self.position.total_commission), 5.00)
        self.assertEqual(PriceParser.display(self.position.net_incl_comm), -19.50)

        self.assertEqual(
            PriceParser.display(self.position.avg_price, 5), 77.67600
        )
        self.assertEqual(PriceParser.display(self.position.cost_basis), 0.00)
        self.assertEqual(PriceParser.display(self.position.market_value), 0.00)
        self.assertEqual(PriceParser.display(self.position.unrealised_pnl), 0.00)
        self.assertEqual(PriceParser.display(self.position.realised_pnl), -19.50)


class TestShortPosition(unittest.TestCase):
    """
    Test a short position in Proctor & Gamble where the initial
    trade is a sell/short of 100 shares of PG, at a price of
    $77.69, with $1.00 commission.
    """
    def setUp(self):
        self.position = Position(
            "SLD", "PG", 100,
            PriceParser.parse(77.69), PriceParser.parse(1.00),
            PriceParser.parse(77.68), PriceParser.parse(77.70)
        )

    def test_open_short_position(self):
        self.assertEqual(PriceParser.display(self.position.cost_basis), -7768.00)
        self.assertEqual(PriceParser.display(self.position.market_value), -7769.00)
        self.assertEqual(PriceParser.display(self.position.unrealised_pnl), -1.00)
        self.assertEqual(PriceParser.display(self.position.realised_pnl), -1.0)

        self.position.update_market_value(
            PriceParser.parse(77.72), PriceParser.parse(77.72)
        )

        self.assertEqual(PriceParser.display(self.position.cost_basis), -7768.00)
        self.assertEqual(PriceParser.display(self.position.market_value), -7772.00)
        self.assertEqual(PriceParser.display(self.position.unrealised_pnl), -4.00)
        self.assertEqual(PriceParser.display(self.position.realised_pnl), -4.0)


if __name__ == "__main__":
    unittest.main()

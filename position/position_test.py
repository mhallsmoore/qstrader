from decimal import Decimal
import unittest

from position import Position


class TestRoundTripXOMPosition(unittest.TestCase):
    def setUp(self):
        self.position = Position(
            "BOT", "XOM", Decimal('100'), 
            Decimal("74.78"), Decimal("1.00"), 
            Decimal('74.78'), Decimal('74.80')
        )

    def test_calculate_round_trip(self):
        self.position.transact_shares(
            "BOT", Decimal('100'), Decimal('74.63'), Decimal('1.00')
        )
        self.position.transact_shares(
            "BOT", Decimal('250'), Decimal('74.620'), Decimal('1.25')
        )
        self.position.transact_shares(
            "SLD", Decimal('200'), Decimal('74.58'), Decimal('1.00')
        )
        self.position.transact_shares(
            "SLD", Decimal('250'), Decimal('75.26'), Decimal('1.25')
        )
        self.position.update_market_value(Decimal("77.75"), Decimal("77.77"))

        self.assertEqual(self.position.action, "BOT")
        self.assertEqual(self.position.ticker, "XOM")
        self.assertEqual(self.position.quantity, Decimal("0"))
        
        self.assertEqual(self.position.buys, Decimal("450"))
        self.assertEqual(self.position.sells, Decimal("450"))
        self.assertEqual(self.position.net, Decimal("0"))
        self.assertEqual(self.position.avg_bot, Decimal("74.65778"))
        self.assertEqual(self.position.avg_sld, Decimal("74.95778"))
        self.assertEqual(self.position.total_bot, Decimal("33596.00"))
        self.assertEqual(self.position.total_sld, Decimal("33731.00"))
        self.assertEqual(self.position.net_total, Decimal("135.00"))
        self.assertEqual(self.position.total_commission, Decimal("5.50"))
        self.assertEqual(self.position.net_incl_comm, Decimal("129.50"))

        self.assertEqual(self.position.avg_price, Decimal("74.665"))
        self.assertEqual(self.position.cost_basis, Decimal("0.00"))
        self.assertEqual(self.position.market_value, Decimal("0.00"))
        self.assertEqual(self.position.unrealised_pnl, Decimal("0.00"))
        self.assertEqual(self.position.realised_pnl, Decimal("129.50"))


class TestRoundTripPGPosition(unittest.TestCase):
    def setUp(self):
        self.position = Position(
            "SLD", "PG", Decimal('100'), 
            Decimal("77.69"), Decimal("1.00"), 
            Decimal('77.68'), Decimal('77.70')
        )

    def test_calculate_round_trip(self):
        self.position.transact_shares(
            "SLD", Decimal('100'), Decimal('77.68'), Decimal('1.00')
        )
        self.position.transact_shares(
            "SLD", Decimal('50'), Decimal('77.70'), Decimal('1.00')
        )
        self.position.transact_shares(
            "BOT", Decimal('100'), Decimal('77.77'), Decimal('1.00')
        )
        self.position.transact_shares(
            "BOT", Decimal('150'), Decimal('77.73'), Decimal('1.00')
        )
        self.position.update_market_value(Decimal("77.72"), Decimal("77.72"))

        self.assertEqual(self.position.action, "SLD")
        self.assertEqual(self.position.ticker, "PG")
        self.assertEqual(self.position.quantity, Decimal("0"))
        
        self.assertEqual(self.position.buys, Decimal("250"))
        self.assertEqual(self.position.sells, Decimal("250"))
        self.assertEqual(self.position.net, Decimal("0"))
        self.assertEqual(self.position.avg_bot, Decimal("77.746"))
        self.assertEqual(self.position.avg_sld, Decimal("77.688"))
        self.assertEqual(self.position.total_bot, Decimal("19436.50"))
        self.assertEqual(self.position.total_sld, Decimal("19422.00"))
        self.assertEqual(self.position.net_total, Decimal("-14.50"))
        self.assertEqual(self.position.total_commission, Decimal("5.00"))
        self.assertEqual(self.position.net_incl_comm, Decimal("-19.50"))

        self.assertEqual(self.position.avg_price, Decimal("77.67600"))
        self.assertEqual(self.position.cost_basis, Decimal("0.00"))
        self.assertEqual(self.position.market_value, Decimal("0.00"))
        self.assertEqual(self.position.unrealised_pnl, Decimal("0.00"))
        self.assertEqual(self.position.realised_pnl, Decimal("-19.50"))


if __name__ == "__main__":
    unittest.main()

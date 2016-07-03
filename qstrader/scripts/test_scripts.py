"""
Test scripts
"""
import unittest

from qstrader import settings
import qstrader.scripts.generate_simulated_prices


class TestScripts(unittest.TestCase):
    """
    Test example are executing correctly
    """
    def setUp(self):
        """
        Set up configuration.
        """
        self.config = settings.TEST

    def test_generate_simulated_prices(self):
        """
        Test generate_simulated_prices
        """
        qstrader.scripts.generate_simulated_prices.run(
            '',  # outdir
            'GOOG',  # ticker
            700,  # init_price
            42,  # seed
            1.5000,  # s0
            0.02,  # spread
            400,  # mu_dt
            100,  # sigma_dt
            2014,  # year
            1,  # month
            3,  # nb_days (number of days of data to create)
            config=self.config
        )

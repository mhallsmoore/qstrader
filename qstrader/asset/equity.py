from qstrader.asset.asset import Asset


class Equity(Asset):
    """
    Stores meta data about an equity common stock or ETF.

    Parameters
    ----------
    name : `str`
        The asset's name (e.g. the company name and/or
        share class).
    symbol : `str`
        The asset's original ticker symbol.
        TODO: This will require modification to handle proper
        ticker mapping.
    tax_exempt: `boolean`, optional
        Is the share exempt from government taxation?
        Necessary for taxation on share transactions, such
        as UK stamp duty.
    """

    def __init__(
        self,
        name,
        symbol,
        tax_exempt=True
    ):
        self.cash_like = False
        self.name = name
        self.symbol = symbol
        self.tax_exempt = tax_exempt

    def __repr__(self):
        """
        String representation of the Equity Asset.
        """
        return (
            "Equity(name='%s', symbol='%s', tax_exempt=%s)" % (
                self.name, self.symbol, self.tax_exempt
            )
        )

from qstrader.asset.universe.universe import Universe


class DynamicUniverse(Universe):
    """
    An Asset Universe that allows additions of assets
    beyond a certain datetime.

    TODO: This does not currently support removal of assets
    or sequences of additions/removals.

    Parameters
    ----------
    asset_dates : `dict{str: pd.Timestamp}`
        Map of assets and their entry date.
    """

    def __init__(self, asset_dates):
        self.asset_dates = asset_dates

    def get_assets(self, dt):
        """
        Obtain the list of assets in the Universe at a particular
        point in time. This will always return a static list
        independent of the timestamp provided.

        If no date is provided do not include the asset. Only
        return those assets where the current datetime exceeds the
        provided datetime.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The timestamp at which to retrieve the Asset list.

        Returns
        -------
        `list[str]`
            The list of Asset symbols in the static Universe.
        """
        return [
            asset for asset, asset_date in self.asset_dates.items()
            if asset_date is not None and dt >= asset_date
        ]

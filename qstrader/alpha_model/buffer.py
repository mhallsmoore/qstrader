from abc import ABCMeta, abstractmethod

from qstrader.alpha_model.alpha_import import AlphaModel


class BufferAlphaModel(AlphaModel):
    """
    """

    def __init__(
        self, buffer_types, start_dt, universe,
        data_handler, lookbacks=[12]
    ):
        self.buffer_types = buffer_types
        self.start_dt = start_dt
        self.universe = universe
        self.data_handler = data_handler
        self.lookbacks = lookbacks
        self.buffers = self._generate_asset_signal_buffers()
        self.warmups = 0
        
    def _generate_asset_signal_buffers(self):
        assets = self.universe.get_assets(self.start_dt)
        return {
            buffer_type.__name__.replace('Signal', '').lower(): buffer_type(
                assets, lookbacks=self.lookbacks
            )
            for buffer_type in self.buffer_types
        }

    @abstractmethod
    def generate_signals(self, dt, weights):
        raise NotImplementedError(
            "Must override generate_signals in order to specify "
            "buffer strategy logic."
        )

    def __call__(self, dt):
        assets = self.universe.get_assets(dt)
        weights = {asset: 0.0 for asset in assets}
        
        for asset in assets:
            price = self.data_handler.get_asset_latest_mid_price(dt, asset)
            for buffer_type in self.buffer_types:
                buffer_name = buffer_type.__name__.replace('Signal', '').lower()
                self.buffers[buffer_name].append(asset, price)
        self.warmups += 1

        if self.warmups > max(self.lookbacks):
            weights = self.generate_signals(dt, weights)

        return weights
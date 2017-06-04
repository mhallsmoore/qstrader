import logging
import logging.config
from datetime import timedelta

import requests_cache
from trading_ig import IGService

from qstrader import setup_logging

setup_logging


class IGClient(object):
    # Initialises IG Service and Session to support REST API or Streaming services from IG Markets
    def __init__(self, config):
        CACHE_NAME = 'igcache'
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Establishing cached session with IG Markets")
        session_cached = requests_cache.CachedSession(cache_name=CACHE_NAME,
                                                      backend='sqlite',
                                                      expire_after=timedelta(hours=1))
        self.ig_service = IGService(config.IG_USERNAME, config.IG_PASSWORD, config.IG_API_KEY,
                                    config.IG_ACC_TYPE, session_cached)
        # Creates REST session
        self.ig_session = self.ig_service.create_session()

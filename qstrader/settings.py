import os
import warnings
import quandl

ENV_VAR_ROOT = 'QSTRADER'

def get_info(key, default_value=None):
    """Returns a value (url, login, password)
    using either default_value or using environment variable"""
    ENV_VAR_KEY = ENV_VAR_ROOT + "_" + key.upper()
    if default_value == '' or default_value is None:
        try:
            return(os.environ[ENV_VAR_KEY])
        except:
            warnings.warn("You should pass %s using --%s or using environment variable %r" % (key, key, ENV_VAR_KEY))
            return(default_value)
    else:
        return(default_value)


class SettingsDefault(object):
    _CSV_DATA_DIR = "~/data"
    _OUTPUT_DIR = "~/qstrader"

    # Quandl config is separated out to a config file to protect private keys,
    # but left in setting.py to keep all settings organized in one place.
    try:
       import quandl_conf
       _QUANDL_KEY = quandl_conf.QUANDL_API_KEY
       _QUANDL_BASE = quandl_conf.QUANDL_API_BASE
       _QUANDL_VERSION = quandl_conf.QUANDL_API_VERSION
       _QUANDL_PAGE_LIMIT = quandl_conf.QUANDL_PAGE_LIMIT
    except ImportError:
       # quandl_conf.py is missing.  Grab quandl defaults.
       _QUANDL_KEY = quandl.ApiConfig.api_key
       _QUANDL_BASE = quandl.ApiConfig.api_base
       _QUANDL_VERSION = quandl.ApiConfig.api_version
       _QUANDL_PAGE_LIMIT = quandl.ApiConfig.page_limit

    @property
    def CSV_DATA_DIR(self):
        return get_info("CSV_DATA_DIR", os.path.expanduser(self._CSV_DATA_DIR))

    @property
    def OUTPUT_DIR(self):
        return get_info("OUTPUT_DIR", os.path.expanduser(self._CSV_DATA_DIR))

    #**************************************************************************
    # Quandl config data
    # Note: Do not use get_info because default_values could be 'None'
    #**************************************************************************
    @property
    def QUANDL_API_KEY(self):
        return self._QUANDL_KEY

    @property
    def QUANDL_API_BASE(self):
        return self._QUANDL_BASE

    @property
    def QUANDL_API_VERSION(self):
        return self._QUANDL_VERSION

    @property
    def QUANDL_PAGE_LIMIT(self):
        return self._QUANDL_PAGE_LIMIT



class SettingsTest(SettingsDefault):
    _CSV_DATA_DIR = "data"
    _OUTPUT_DIR = "out"
    _QUANDL_KEY = quandl.ApiConfig.api_key
    _QUANDL_BASE = quandl.ApiConfig.api_base
    _QUANDL_VERSION = quandl.ApiConfig.api_version
    _QUANDL_PAGE_LIMIT = quandl.ApiConfig.page_limit


DEFAULT = SettingsDefault()
TEST = SettingsTest()

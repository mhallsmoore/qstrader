import os
import warnings


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
    _OUTPUT_DIR = "~/out"

    @property
    def CSV_DATA_DIR(self):
        return get_info("CSV_DATA_DIR", os.path.expanduser(self._CSV_DATA_DIR))

    @property
    def OUTPUT_DIR(self):
        return get_info("OUTPUT_DIR", os.path.expanduser(self._OUTPUT_DIR))


class SettingsTest(SettingsDefault):
    _CSV_DATA_DIR = "data"
    _OUTPUT_DIR = "out"


DEFAULT = SettingsDefault()
TEST = SettingsTest()

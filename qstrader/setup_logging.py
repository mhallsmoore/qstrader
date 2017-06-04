import logging.config
import os.path


default_path = os.path.join(os.path.dirname(__file__), "logging.conf")
# default_path = 'logging.conf',
default_level = logging.INFO
env_key = 'LOG_CFG'
"""Setup logging configuration

"""
path = default_path
value = os.getenv(env_key, None)
if value:
    path = value
if os.path.exists(path[0]):
    # with open(path, 'rt') as f:
        # config = yaml.safe_load(f.read())
    # logging.config.dictConfig(config)
    logging.config.fileConfig(path, disable_existing_loggers=False)
else:
    logging.basicConfig(level=default_level)

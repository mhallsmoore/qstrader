# flake8: noqa

import sys

PY2 = sys.version_info[0] == 2
PY3 = (sys.version_info[0] >= 3)

if PY2:
    import Queue as queue
else:  # PY3
    import queue

try:
    import cPickle as pickle
except ImportError:
    import pickle

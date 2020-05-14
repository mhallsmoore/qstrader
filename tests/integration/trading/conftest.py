import os

import pytest


@pytest.fixture
def etf_filepath():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

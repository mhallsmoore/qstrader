# QSTrader Default Backtest Settings

import os

def project_path(*args):
    paths = [os.path.dirname(__file__)] + list(args)
    return os.path.normpath(os.path.join(*paths))


# Data configuration
# ==================

DATA = {
    'TYPE': 'CSV',
    'ASSETS': [],
    'ROOT': 'data'
}


# Exchange configuration
# ======================

EXCHANGE = {
    'SYMBOL': 'NYSE',
    'TIMEZONE': 'US/Eastern',
    'OPENING_UTC': '09:30:00',
    'CLOSING_UTC': '16:00:00'
}


# Broker Configuration
# ====================

BROKER = {
    'ACCOUNT_NAME': 'Backtest-Broker-Account',
    'INITIAL_CASH': 1000000.0,
    'PORTFOLIO_ID': '1234',
    'PORTFOLIO_NAME': 'Backtest-Portfolio',
    'COMMISSION': {
        'MODEL': 'Zero Commission'
    }
}


# Statistics
# ==========

STATISTICS_ROOT = 'statistics'


# Simulation settings
# ===================

SIMULATION = {
    'START_DATE': '',
    'END_DATE': '',
    'FORECAST': {},
    'PORTFOLIO_CONSTRUCTION': {}
}

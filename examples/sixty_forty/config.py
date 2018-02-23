"""
Fixed proportion portfolio with 60% allocated to a broad US
equities index (S&P500) via SPY ETF and 40% allocated to
AGG, an aggregate US bond ETF.

The backtest is carried out from 1st November 2006 until
12th October 2016.

The portfolio carries out pre-market rebalance logic on a
weekly basis on Wednesday mornings.

The model requires Yahoo Finance-style CSVs of daily
bars for SPY and AGG in order to carry out the backtest.
"""

# Data configuration
# ==================

DATA = {
    'TYPE': 'CSV',
    'ASSETS': ['SPY', 'AGG'],
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
        'MODEL': 'Zero'
    }
}


# Statistics
# ==========

STATISTICS_ROOT = 'statistics'


# Simulation settings
# ===================

SIMULATION = {
    'TITLE': 'Fixed-Weight 60-40 SPY/AGG Portfolio Weekly Rebalanced',
    'START_DATE': '2006-11-01',
    'END_DATE': '2016-10-12', 
    'ALPHA': {
        'MODEL': 'Fixed Weight',
        'WEIGHTS': {'SPY': 0.6, 'AGG': 0.4}
    },
    'PORTFOLIO_CONSTRUCTION': {
        'MODEL': 'Fixed Weight',
        'REBALANCE': {
            'FREQUENCY': 'Weekly',
            'WEEKDAY': 'WED'
        }
    }
}

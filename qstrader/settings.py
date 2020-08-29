SUPPORTED = {
    'CURRENCIES': [
        'USD', 'GBP', 'EUR'
    ],
    'FEE_MODEL': {
        'ZeroFeeModel': 'qstrader.broker.fee_model.zero_fee_model'
    }
}

LOGGING = {
    'DATE_FORMAT': '%Y-%m-%d %H:%M:%S'
}

PRINT_EVENTS = True


def set_print_events(print_events=True):
    global PRINT_EVENTS
    PRINT_EVENTS = print_events

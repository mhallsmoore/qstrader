import quandl

# Quandl Key
# see https://www.quandl.com/blog/getting-started-with-the-quandl-api
# see https://www.quandl.com/docs/api#api-keys
#
# Requests without an API key (anonymous requests) are accepted, but subject to
# strict rate limits. This allows users to test the API without signing up for
# a Quandl account.
#
# Anonymous requests are subject to a limit of 50 calls per day.
# Anonymous requests for premium databases are not accepted.
# Authenticated users have a limit of 2,000 calls per 10 minutes, and a limit
# of 50,000 calls per day.  Premium data subscribers have a limit of 5,000
# calls per 10 minutes, and a limit of 720,000 calls per day.
#
# If a valid API key is not used, some datatables will default
# to returning sample data. If you are not receiving all expected data,
# please double check your API key.
# i.e. QUANDL_API_KEY="<enter your free quandl key here>"
QUANDL_API_KEY = "yA_NszzCmR28ghYh8d_H"

# Specifies the Quandl API version to use
# i.e. QUANDL_API_VERSION = '2015-04-09'
QUANDL_API_VERSION = quandl.ApiConfig.api_version    # uses default

# API base
# i.e. QUANDL_API_BASE = 'https://www.quandl.com/api/v3'
QUANDL_API_BASE = quandl.ApiConfig.api_base          # uses default

# Page Limit
# i.e. QUANDL_PAGE_LIMIT = 100
QUANDL_PAGE_LIMIT = quandl.ApiConfig.page_limit      # uses default


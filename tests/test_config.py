
url = 'http://fake.domain/'
username = 'test'
password = 'test'

# Override this configration in local_test_config.py
try:
    from local_test_config.py import *
except ImportError:
    pass


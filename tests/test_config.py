url = 'http://fake.domain/'
username = 'test'
password = 'test'
list_id = 999

# Override this configration in local_test_config.py
try:
    from local_test_config import *
except ImportError:
    pass


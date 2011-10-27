url = 'http://fake.domain/'
username = 'test'
password = 'test'
list_id = 999
sessionid = 1
retrieve_email = 'test@fake.tld'

# Override this configration in local_test_config.py
try:
    from local_test_config import *
except ImportError:
    pass


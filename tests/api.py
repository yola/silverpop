from testify import *

from silverpop import API
from silverpop.exceptions import AuthException

from test_config import *

class GoodLoginTestCase(TestCase):
    @class_setup
    def init_api_object(self):
        self.good_api = API(url, username, password)
    
    def test_good_login_returns_session_id(self):
        assert_not_equal(self.good_api.sessionid, None)
    
class BadLoginTestCase(TestCase):
    def test_bad_login_raises_exception(self):
        assert_raises(AuthException, API, url, 'test', 'test')
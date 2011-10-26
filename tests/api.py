from testify import *

from silverpop import API
from silverpop.exceptions import AuthException, ResponseException

from test_config import *

class GoodLoginTestCase(TestCase):
    @class_setup
    def init_api_object(self):
        self.good_api = API(url, username, password)
    
    def test_good_login_sets_session_id(self):
        assert_not_equal(self.good_api.sessionid, None)
    
class BadLoginTestCase(TestCase):
    def test_bad_login_raises_exception(self):
        assert_raises(AuthException, API, url, 'test', 'test')

class DataRetrievalTestCase(TestCase):
    @class_setup
    def init_api_object(self):
        self.api = API(url, username, password, sessionid)
        self.data = self.api.get_user_info(list_id, retrieve_email)
    
    def test_valid_address_retrieval(self):
        assert_equal(retrieve_email, self.data['EMAIL'])
    
    def test_invalid_address_retrieval(self):
        assert_raises(ResponseException, self.api.get_user_info, list_id,
                                                              'fake@fake.tld')
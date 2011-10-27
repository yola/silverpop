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

#class RetryTestCase(TestCase):
#    '''This test case is not working because the machine I'm using to write 
#    this is whitelisted and the API does not require authentication from
#    whitelisted machines.'''
#    
#    @setup
#    def init_api_object(self):
#        self.api = API(url, username, password, sessionid='gogogadget')
#    
#    def test_retrieval_retries(self):
#        data = self.api.update_user(list_id, retrieve_email,
#                                                {'PurchasedDomainCount': 72})
#        assert_equal(data, True)
#    
#    def test_retrieval_throws_auth_exception_if_auth_fails(self):
#        self.api.password = 'failed'
#        assert_raises(AuthException, self.api.update_user, list_id,
#                                retrieve_email, {'PurchasedDomainCount': 90})


class AddUserTestCase(TestCase):
    @class_setup
    def init_api_object(self):
        from time import time
        self.api = API(url, username, password, sessionid)
        self.email = 'test%s@fake.tld' % time()
        self.created = self.api.add_user(list_id, self.email,
                                                  {'Currency': 'USD'})
    def test_add_user(self):
        assert_equal(self.created, True)
    
    def test_retrieval_of_new_user(self):
        assert_in('USD', 
           self.api.get_user_info(list_id, self.email)['COLUMNS']['Currency'])
             
class UpdateUserTestCase(TestCase):
    @class_setup
    def init_api_object(self):
        self.api = API(url, username, password, sessionid)
        self.user_info = self.api.get_user_info(list_id, retrieve_email)
        self.domain_count = \
                            self.user_info['COLUMNS']['PurchasedDomainCount']
        self.new_domain_count = 0 if self.domain_count == '' else \
                                                    int(self.domain_count) + 1
                                                    
        self.result = self.api.update_user(list_id, retrieve_email,
                               {'PurchasedDomainCount':self.new_domain_count})
        
        self.updated_user_info = \
                               self.api.get_user_info(list_id, retrieve_email)
        self.updated_domain_count = \
                     self.updated_user_info['COLUMNS']['PurchasedDomainCount']
                     
    def test_data_param_required(self):
        assert_raises(AssertionError, self.api.update_user,
                                                  list_id, retrieve_email, {})
    
    def test_data_param_must_be_dict(self):
        assert_raises(AssertionError, self.api.update_user,
                                                list_id, retrieve_email, [1,])
    
    def test_update_succeeded(self):
        assert_equal(self.result, True)
        assert_equal(self.updated_domain_count, str(self.new_domain_count))
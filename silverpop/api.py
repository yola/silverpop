import requests
import logging

from elementtree import ElementTree

from xml import ConvertXmlToDict, ConvertDictToXml
from exceptions import AuthException, ResponseException

logger = logging.getLogger(__name__)

class API(object):
    def __init__(self, url, username, password, sessionid=None):
        self.url = url
        self.username = username
        self.password = password
        self.sessionid = sessionid if sessionid else self.login()
        
    def login(self):
        '''Connects to Silverpop and attempts to retrieve a jsessionid for
        secure request purposes.'''
        xml = self._get_xml_document()
        xml['Envelope']['Body'] = \
            {'Login': {'USERNAME': self.username, 'PASSWORD': self.password}}
        
        sessionid = None
        response = self._submit_request(xml, retry=False, auth=True)
        success = response.get('SUCCESS', 'false').lower()
        
        if success == 'success' or success == 'true':
            sessionid = response.get('SESSIONID', None)
        
        if not sessionid:
            raise AuthException()
            
        logger.info("New Silverpop sessionid acquired: %s" % sessionid)
        
        return sessionid
    
    def get_user_info(self, list_id, email):
        '''Returns data from the specified list about the specified user.
        The email address must be used as the primary key.'''
        xml = self._get_xml_document()
        xml['Envelope']['Body'] = {
            'SelectRecipientData': {
                'LIST_ID': list_id,
                'EMAIL': email
            }
        }
        result = self._submit_request(xml)
        
        return result
    
    def _get_xml_document(self):
        return {'Envelope': {'Body': None}}
    
    def _submit_request(self, xml_dict, retry=True, auth=False):
        '''Submits an XML payload to silverpop, parses the result, and returns
        it.'''
        xml = ElementTree.tostring(ConvertDictToXml(xml_dict))
        url = '%s;jsessionid=%s' % (self.url, self.sessionid) if not auth \
                                                                 else self.url
        
        # Connect to silverpop and get our response
        response = requests.post(self.url, data=xml,
                           headers={"Content-Type": "text/xml;charset=utf-8"})
        response = ConvertXmlToDict(response.content, dict)
        response = response.get('Envelope', {}).get('Body')
        
        # Determine if the request succeeded
        success = response.get('RESULT', {}).get('SUCCESS', 'false').lower()
        success = False if success != 'true' and success != 'success' \
                                                                     else True
        
        # Generate an exception if the API request failed.
        if not success:
            exc = ResponseException(response['Fault'])
            error_id = \
                exc.fault.get('detail', {}).get('error', {}).get(
                                                              'errorid', None)
            
            # We want to try and resend the request on auth failures if retry
            # is enabled. 140 is the error_id for unauthenticated api attempts
            if error_id == str(140) and retry:
                self.sessionid = self.login()
                return self._submit_request(xml_dict, retry=False,
                                                                secure=secure)
            elif auth:
                pass
            else:
                raise exc
        
        return response['RESULT']
        
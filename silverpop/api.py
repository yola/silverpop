import requests
import logging

from elementtree import ElementTree

from xml import ConvertXmlToDict, ConvertDictToXml
from exceptions import AuthException

logger = logging.getLogger(__name__)

class API(object):
    def __init__(self, url, username, password, sessionid=None):
        self.url = url
        self.username = username
        self.password = password
        self.sessionid = sessionid if sessionid else self.login()
        self.secure_url = '%s;jsessionid=%s' % (url, self.sessionid)
        
    def login(self):
        '''Connects to Silverpop and attempts to retrieve a jsessionid for
        secure request purposes.'''
        xml = self._get_xml_document()
        xml['Envelope']['Body'] = \
            {'Login': {'USERNAME': self.username, 'PASSWORD': self.password}}
        
        sessionid = None
        response = self._submit_request(xml, secure=False, retry=False)
        success = response.get('RESULT', {}).get('SUCCESS', 'false').lower()
        
        if success == 'success' or success == 'true':
            sessionid = response.get('RESULT', {}).get('SESSIONID')
        
        if not sessionid:
            raise AuthException()
            
        logging.info("New Silverpop sessionid acquired: %s" % sessionid)
        
        return sessionid
    
    def _get_xml_document(self):
        return {'Envelope': {'Body': None}}
    
    def _submit_request(self, xml, retry=True, secure=True):
        '''Submits an XML payload to silverpop, parses the result, and returns
        it.'''
        xml = ElementTree.tostring(ConvertDictToXml(xml))
        url = self.secure_url if secure else self.url
        
        response = requests.post(self.url, data=xml,
                           headers={"Content-Type": "text/xml;charset=utf-8"})
        response = ConvertXmlToDict(response.content, dict)
        response = response.get('Envelope').get('Body')
        
        return response
        
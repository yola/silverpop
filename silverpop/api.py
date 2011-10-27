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
        response, success = self._submit_request(xml, retry=False, auth=True)
        sessionid = response.get('SESSIONID') if success else None
        
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
        result, success = self._submit_request(xml)
        
        return result
    
    def add_user(self, list_id, email, data={}):
        '''Adds a user to the specified list. Supports adding additional 
        attributes via passing a dictionary to the data parameter.'''
        # Build the XML
        xml = self._get_xml_document()
        xml['Envelope']['Body'] = {
            'AddRecipient': {
                'LIST_ID': list_id,
                'CREATED_FROM': 2,
                'COLUMN': [
                    {'NAME':'EMAIL', 'VALUE':email}
                ],
            }
        }
        xml['Envelope']['Body']['AddRecipient']['COLUMN'].extend(
                                                  self._data_to_columns(data))
        
        result, success = self._submit_request(xml)
        
        return success
    
    def update_user(self, list_id, email, data):
        '''Updates an existing user in Silverpop based on the email address as
        the primary key. The data parameter is a dictionary that maps column
        names to their new values.'''
        
        assert len(data) >= 1, \
                  'Data parameter must contain at least one column/value pair'
        
        xml = self._get_xml_document()
        xml['Envelope']['Body'] = {
            'UpdateRecipient': {
                'LIST_ID': list_id,
                'CREATED_FROM': 2,
                'OLD_EMAIL': email,
                'COLUMN': self._data_to_columns(data),
            }
        }
        
        result, success = self._submit_request(xml)

        return success
    
    def _sanitize_columns_in_api_result(self, data):
        '''Post result parsing, the value of the columns key, if it exists,
        will look something this format:
        
        COLUMNS:[{'COLUMN':{'NAME':'<name>', 'VALUE':'<value>'}, ...}]. This
        method replaces the value of the columns key with a dictionary that
        looks like this:
        
        COLUMNS: {'<name>': <value>}'''
        columns = data.get('COLUMNS', {}).get('COLUMN', [])
        
        # Don't touch the original data if there aren't any columns.
        if len(columns) < 1:
            return data
        
        out= {}
        if type(columns) == dict:
            out[columns['NAME']] = columns['VALUE']
        else:
            for column in columns:
                out[column['NAME']] = column['VALUE']
        
        data['COLUMNS'] = out
        
        return data
    
    def _data_to_columns(self, data):
        '''Iterates through a data dictionary, building a list of the format
        [{'NAME':'<name>', 'VALUE':'<value>'},...]. The result can be set to
        the COLUMN key in a dictionary that will be converted to XML for
        Silverpop consumption.'''
        assert callable(getattr(data, 'items', None)), \
                            'Data parameter must have a callable called items'
        
        # Append the data dictionary to the column list
        columns = []
        for column, value in data.items():
            columns.append({'NAME':column, 'VALUE':value,})
            
        return columns
    
    def _get_xml_document(self):
        return {'Envelope': {'Body': None}}
    
    def _submit_request(self, xml_dict, retry=True, auth=False):
        '''Submits an XML payload to Silverpop, parses the result, and returns
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
        
        return self._sanitize_columns_in_api_result(response['RESULT']), \
                                                                       success
        
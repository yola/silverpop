import logging

logger = logging.getLogger(__name__)

class AuthException(Exception):
    def __init__(self, message="Authentication failed."):
        logger.error(message)
        super(AuthException, self).__init__(message)

class ResponseException(Exception):
    def __init__(self, api_response):
        self.fault = api_response
        logger.info("API Call failed: %s" % api_response)
        super(ResponseException, self).__init__('API call failed.')
        
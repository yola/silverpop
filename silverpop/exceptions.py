import logging

logger = logging.getLogger(__name__)

class AuthException(Exception):
    def __init__(self, message="Authentication failed."):
        logger.error(message)
        super(AuthException, self).__init__(message)
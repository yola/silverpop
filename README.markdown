# Python Silverpop API Wrapper

This is a simple wrapper for the Silverpop API.

## Usage:

    >>> from silverpop import API
    >>> api = API('https://api.silverpop.com/XMLAPI', 'username', 'email')
    >>> print api.get_user_info(list_id=102, email='test@fake.tld')
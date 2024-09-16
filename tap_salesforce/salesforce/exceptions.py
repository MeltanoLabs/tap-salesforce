# pylint: disable=super-init-not-called

class TapSalesforceException(Exception):
    pass


class TapSalesforceQuotaExceededException(TapSalesforceException):
    pass


class SFDCCustomNotAcceptableError(Exception):
    """
    SFDC returned CustomNotAcceptable error with HTTP Error code 406.

    This error is sometimes returned when many discovery calls are made
    in quick succession. There does not seem to be documentation on this error
    on any salesforce documentation page or forum.
    Example Error Message:
    ```
    requests.exceptions.HTTPError: 406 Client Error: CustomNotAcceptable for 
    url: https://XXX.salesforce.com/services/data/v53.0/sobjects/XXX/describe
    """

class RetriableSalesforceAuthenticationError(Exception):
    """
    A general classification for SFDC HTTP Authentication Errors.

    The class is used to identify cases in which authentication should be
    retried. It is primarily setup to handle simultaneous token requests during
    the refresh token flow which returns the 400 Bad Request response. However,
    it could be further expanded to handle other authentication errors that
    could require retries.
    """

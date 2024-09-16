import threading
import logging
import requests
import backoff
from collections import namedtuple
from simple_salesforce import SalesforceLogin

from tap_salesforce.salesforce.exceptions import RetriableSalesforceAuthenticationError

LOGGER = logging.getLogger(__name__)

    # The minimum expiration setting for SF Refresh Tokens is 15 minutes
    REFRESH_TOKEN_EXPIRATION_PERIOD = 900

    # Errors that can be retried
    RETRIABLE_SALESFORCE_RESPONSES = [
        {'error': 'invalid_grant', 'error_description': 'expired authorization code'}
    ]

    @property
    def _login_body(self):
        return {'grant_type': 'refresh_token', **self._credentials._asdict()}

        return login_url

    @backoff.on_exception(
        backoff.expo,
        RetriableSalesforceAuthenticationError,
        max_tries=5,
        factor=4,
        jitter=None
    )
    def login(self):
        resp = None  # Ensure resp is defined outside the try block
        try:
            LOGGER.info("OAuth2 login successful")
            self._access_token = auth['access_token']
            self._instance_url = auth['instance_url']

            LOGGER.info("Starting new login timer")
            self.login_timer = threading.Timer(self.REFRESH_TOKEN_EXPIRATION_PERIOD, self.login)
            self.login_timer.start()
        except requests.exceptions.HTTPError as e:
            error_message = f"{e}, Response from Salesforce: {resp.text}"
            failed_auth_response = resp.json()
            if failed_auth_response in self.RETRIABLE_SALESFORCE_RESPONSES:
                raise RetriableSalesforceAuthenticationError(error_message) from e
            else:
                raise Exception(error_message) from e
        except Exception as e:
            error_message = str(e)
            if resp is not None:
                # Ensure we capture the response body even when an error occurs
                error_message += ", Response from Salesforce: {}".format(resp.text)
            raise Exception(error_message) from e
        finally:
            LOGGER.info("Starting new login timer")
            self.login_timer = threading.Timer(self.REFRESH_TOKEN_EXPIRATION_PERIOD, self.login)
            self.login_timer.start()


class SalesforceAuthPassword(SalesforceAuth):

        self._access_token, host = login
        self._instance_url = "https://" + host

if __name__ == "__main__":
    sfdc_auth = SalesforceAuth.from_credentials(
        is_sandbox=False,
        credentials= parse_credentials({
            "client_id": "secret_client_id",
            "client_secret": "secret_client_secret",
            "refresh_token": "abc123",
        }),
    )
    sfdc_auth.login()

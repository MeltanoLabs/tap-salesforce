from collections import namedtuple


LOGGER = singer.get_logger()


OAuthCredentials = namedtuple('OAuthCredentials', ("client_id", "client_secret", "refresh_token"))
PasswordCredentials = namedtuple('PasswordCredentials', ("username", "password", "security_token"))


class SalesforceAuthOAuth():
    @property
    def _login_body(self):
        return {'grant_type': 'refresh_token', **self._credentials._asdict()}

    @property
    def _login_url(self):
        login_url = 'https://login.salesforce.com/services/oauth2/token'

        if self.is_sandbox:
            login_url = 'https://test.salesforce.com/services/oauth2/token'

        return login_url

    def login(self):
        LOGGER.info("Attempting login via OAuth2")
        super().login()


class SalesforceAuth():
    # The minimum expiration setting for SF Refresh Tokens is 15 minutes
    REFRESH_TOKEN_EXPIRATION_PERIOD = 900

    def __init__(self, credentials, is_sandbox=False):
        self.is_sandbox = is_sandbox
        self._credentials = credentials


    def login(self):
        resp = None
        try:
            resp = self._make_request("POST",
                                      self._login_url,
                                      body=self._login_body,
                                      headers={"Content-Type": "application/x-www-form-urlencoded"})

            LOGGER.info("OAuth2 login successful")

            auth = resp.json()

            self.access_token = auth['access_token']
            self.instance_url = auth['instance_url']
        except Exception as e:
            error_message = str(e)
            if resp:
                error_message = error_message + ", Response from Salesforce: {}".format(resp.text)
            raise Exception(error_message) from e
        finally:
            LOGGER.info("Starting new login timer")
            self.login_timer = threading.Timer(REFRESH_TOKEN_EXPIRATION_PERIOD, self.login)
            self.login_timer.start()

        pass

    @property
    def auth_header(self)
        if not self._auth_header:
            self._auth_header = self._generate_auth_headers()

        return self._auth_header

    def _get_standard_headers(self):
        return {"Authorization": "Bearer {}".format(self.access_token)}

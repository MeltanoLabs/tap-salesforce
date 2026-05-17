import logging
import threading
import time
from collections import namedtuple

import jwt
import requests
from simple_salesforce import SalesforceLogin

LOGGER = logging.getLogger(__name__)


OAuthCredentials = namedtuple("OAuthCredentials", ("client_id", "client_secret", "refresh_token"))

PasswordCredentials = namedtuple("PasswordCredentials", ("username", "password", "security_token"))

JWTCredentials = namedtuple("JWTCredentials", ("jwt_client_id", "jwt_username", "jwt_private_key"))


def parse_credentials(config):
    for cls in (JWTCredentials, OAuthCredentials, PasswordCredentials):
        creds = cls(*(config.get(key) for key in cls._fields))
        if all(creds):
            _validate_api_type(creds, config.get("api_type"))
            return creds

    raise Exception("Cannot create credentials from config.")


def _validate_api_type(creds, api_type):
    # Bulk API 1.0 (`/services/async/...`) authenticates via X-SFDC-Session, which
    # requires a SOAP-style session id. The OAuth2 JWT Bearer flow never mints one,
    # so combining JWTCredentials with api_type="BULK" results in InvalidSessionId
    # errors on every stream at job-create time. Bulk 2.0 uses Bearer tokens and
    # works fine. Fail fast with a clear message rather than letting the run die
    # later mid-sync.
    if isinstance(creds, JWTCredentials) and (api_type or "").upper() == "BULK":
        raise Exception(
            "Configuration conflict: api_type='BULK' (Bulk API 1.0) is not "
            "compatible with OAuth2 JWT Bearer authentication. Bulk 1.0 requires "
            "a SOAP session id, which JWT bearer does not issue. "
            "Use api_type='BULK2' (recommended) or 'REST' instead, or switch "
            "to password-based authentication if you must use Bulk 1.0."
        )


class SalesforceAuth:
    def __init__(self, credentials, is_sandbox=False):
        self.is_sandbox = is_sandbox
        self._credentials = credentials
        self._access_token = None
        self._instance_url = None
        self._auth_header = None
        self.login_timer = None

    def login(self):
        """Attempt to login and set the `instance_url` and `access_token` on success."""

    @property
    def rest_headers(self):
        return {"Authorization": f"Bearer {self._access_token}"}

    @property
    def bulk_headers(self):
        return {
            "X-SFDC-Session": self._access_token,
            "Content-Type": "application/json",
        }

    @property
    def instance_url(self):
        return self._instance_url

    @classmethod
    def from_credentials(cls, credentials, **kwargs):
        if isinstance(credentials, OAuthCredentials):
            return SalesforceAuthOAuth(credentials, **kwargs)

        if isinstance(credentials, PasswordCredentials):
            return SalesforceAuthPassword(credentials, **kwargs)

        if isinstance(credentials, JWTCredentials):
            return SalesforceAuthJWT(credentials, **kwargs)

        raise Exception("Invalid credentials")


class SalesforceAuthOAuth(SalesforceAuth):
    # The minimum expiration setting for SF Refresh Tokens is 15 minutes
    REFRESH_TOKEN_EXPIRATION_PERIOD = 900

    @property
    def _login_body(self):
        return {"grant_type": "refresh_token", **self._credentials._asdict()}

    @property
    def _login_url(self):
        login_url = "https://login.salesforce.com/services/oauth2/token"

        if self.is_sandbox:
            login_url = "https://test.salesforce.com/services/oauth2/token"

        return login_url

    def login(self):
        try:
            LOGGER.info("Attempting login via OAuth2")

            resp = requests.post(
                self._login_url,
                data=self._login_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            resp.raise_for_status()
            auth = resp.json()

            LOGGER.info("OAuth2 login successful")
            self._access_token = auth["access_token"]
            self._instance_url = auth["instance_url"]
        except Exception as e:
            error_message = str(e)
            if resp:
                error_message = error_message + f", Response from Salesforce: {resp.text}"
            raise Exception(error_message) from e
        finally:
            LOGGER.info("Starting new login timer")
            self.login_timer = threading.Timer(self.REFRESH_TOKEN_EXPIRATION_PERIOD, self.login)
            self.login_timer.start()


class SalesforceAuthPassword(SalesforceAuth):
    def login(self):
        login = SalesforceLogin(sandbox=self.is_sandbox, **self._credentials._asdict())

        self._access_token, host = login
        self._instance_url = "https://" + host


class SalesforceAuthJWT(SalesforceAuth):
    # Re-login periodically; Salesforce access tokens default to ~2h but org policy can shorten it.
    LOGIN_REFRESH_PERIOD = 1800
    JWT_LIFETIME_SECONDS = 300

    @property
    def _audience(self):
        if self.is_sandbox:
            return "https://test.salesforce.com"
        return "https://login.salesforce.com"

    @property
    def _login_url(self):
        if self.is_sandbox:
            return "https://test.salesforce.com/services/oauth2/token"
        return "https://login.salesforce.com/services/oauth2/token"

    def _build_assertion(self):
        claims = {
            "iss": self._credentials.jwt_client_id,
            "sub": self._credentials.jwt_username,
            "aud": self._audience,
            "exp": int(time.time()) + self.JWT_LIFETIME_SECONDS,
        }
        return jwt.encode(claims, self._credentials.jwt_private_key, algorithm="RS256")

    def login(self):
        resp = None
        try:
            LOGGER.info("Attempting login via OAuth2 JWT Bearer")

            resp = requests.post(
                self._login_url,
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": self._build_assertion(),
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            resp.raise_for_status()
            auth = resp.json()

            LOGGER.info("OAuth2 JWT Bearer login successful")
            self._access_token = auth["access_token"]
            self._instance_url = auth["instance_url"]
        except Exception as e:
            error_message = str(e)
            if resp is not None:
                error_message = error_message + f", Response from Salesforce: {resp.text}"
            raise Exception(error_message) from e
        finally:
            LOGGER.info("Starting new login timer")
            self.login_timer = threading.Timer(self.LOGIN_REFRESH_PERIOD, self.login)
            self.login_timer.daemon = True
            self.login_timer.start()

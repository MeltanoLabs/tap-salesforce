import base64
import logging
import os
import threading
from collections import namedtuple

import requests
from simple_salesforce import SalesforceLogin

LOGGER = logging.getLogger(__name__)


OAuthCredentials = namedtuple("OAuthCredentials", ("client_id", "client_secret", "refresh_token"))

PasswordCredentials = namedtuple("PasswordCredentials", ("username", "password", "security_token"))


_ARGO_MODE_REQUIRED = (
    "ARGO_URL",
    "TENANT",
    "ARGO_CONNECTOR_API_KEY",
    "BONGO_API_TARGET_URL",
    "BONGO_API_BASIC_AUTH_USERNAME",
)


def parse_credentials(config):
    # Argo mode: all credentials come from Argo/bongo at runtime.
    # Fail fast if any required env var is absent — do not start the sync
    # with missing auth config. Password-auth tenants must NOT set ARGO_URL.
    if os.environ.get("ARGO_URL"):
        missing = [k for k in _ARGO_MODE_REQUIRED if not os.environ.get(k)]
        if missing:
            raise RuntimeError(
                f"SF RTR: missing required env vars for Argo mode: {', '.join(missing)}. "
                "Set them in the ECS task definition."
            )
        return OAuthCredentials(client_id="", client_secret="", refresh_token="")

    for cls in reversed((OAuthCredentials, PasswordCredentials)):
        creds = cls(*(config.get(key) for key in cls._fields))
        if all(creds):
            return creds

    raise Exception("Cannot create credentials from config.")


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
        raise Exception("Invalid credentials")


class SalesforceAuthOAuth(SalesforceAuth):
    # The minimum expiration setting for SF Refresh Tokens is 15 minutes
    REFRESH_TOKEN_EXPIRATION_PERIOD = 900

    def login(self):
        # parse_credentials() already validated all required env vars at startup.
        # If we reach here without them, something bypassed the normal entry point.
        argo_url = os.environ.get("ARGO_URL", "")
        tenant = os.environ.get("TENANT", "")
        if not argo_url or not tenant:
            raise RuntimeError(
                "ARGO_URL and TENANT are required. "
                "Ensure parse_credentials() was called with ARGO_URL set."
            )
        self._sync_from_argo(argo_url, tenant)

    # ── Timer path: read-only Argo sync ────────────────────────────────────────

    def _sync_from_argo(self, argo_url: str, tenant: str) -> None:
        """Read access_token and instance_url from Argo. No SF call, no lock.

        Called at startup and every 15 min by the timer. Picks up any fresh AT
        that node services (mk-push, mk-pull, mk-bongo) may have rotated into
        Argo since the last sync. If the AT is expired, the next SF data query
        will return 401 which triggers refresh_access_token().
        """
        try:
            creds = self._fetch_argo_credentials(argo_url, tenant)
            at_updated = self._update_credentials(creds)
            if not self._access_token:
                LOGGER.warning(
                    "SF RTR: Argo returned no access_token — next SF query will fail "
                    "event=argo_no_at tenant=%s",
                    tenant,
                )
            else:
                LOGGER.info(
                    "SF RTR: credentials synced from Argo event=credentials_synced "
                    "tenant=%s at_updated=%s",
                    tenant, at_updated,
                )
        except Exception as e:
            LOGGER.error(
                "SF RTR: failed to sync credentials from Argo event=argo_sync_failed "
                "tenant=%s error=%s", tenant, e,
            )
            raise
        finally:
            self.login_timer = threading.Timer(self.REFRESH_TOKEN_EXPIRATION_PERIOD, self.login)
            self.login_timer.start()

    # ── 401 path: delegate refresh to bongo ────────────────────────────────────

    def refresh_access_token(self) -> None:
        """Refresh the AT by delegating to bongo's SF ping endpoint.

        Bongo owns the full RTR-safe lock protocol (lockAwareRefreshFn in
        mk-node-libs). The tap never calls SF OAuth directly — it just triggers
        bongo to refresh and then reads the result from Argo.
        """
        argo_url, bongo_url, tenant, bongo_auth = self._argo_config()
        LOGGER.info(
            "SF RTR: AT expired — delegating refresh to bongo "
            "event=at_refresh_triggered tenant=%s",
            tenant,
        )
        try:
            self._ping_bongo(bongo_url, bongo_auth, tenant)
            LOGGER.info(
                "SF RTR: reading fresh AT from Argo event=argo_read_after_ping tenant=%s", tenant,
            )
            creds = self._fetch_argo_credentials(argo_url, tenant)
            self._apply_fresh_at(creds, tenant)
        except Exception as e:
            LOGGER.error(
                "SF RTR: AT refresh via bongo failed event=at_refresh_error "
                "tenant=%s error=%s", tenant, e,
            )
            raise

    # ── Private helpers ─────────────────────────────────────────────────────────

    def _argo_config(self):
        """Read and validate Argo/bongo env vars; return (argo_url, bongo_url, tenant, bongo_auth)."""
        argo_url = os.environ.get("ARGO_URL", "")
        bongo_url = os.environ.get("BONGO_API_TARGET_URL", "")
        tenant = os.environ.get("TENANT", "")
        if not argo_url or not bongo_url or not tenant:
            raise RuntimeError(
                "ARGO_URL, BONGO_API_TARGET_URL, and TENANT are required. "
                "Ensure parse_credentials() was called with ARGO_URL set."
            )
        bongo_username = os.environ.get("BONGO_API_BASIC_AUTH_USERNAME", "")
        if not bongo_username:
            LOGGER.warning(
                "SF RTR: BONGO_API_BASIC_AUTH_USERNAME not set — bongo requests unauthenticated "
                "tenant=%s", tenant,
            )
        return argo_url, bongo_url, tenant, self._basic_auth(bongo_username)

    def _ping_bongo(self, bongo_url: str, bongo_auth: str, tenant: str) -> None:
        """Call bongo's SF ping endpoint. Bongo triggers lockAwareRefreshFn if AT is expired."""
        LOGGER.info("SF RTR: calling bongo ping event=bongo_ping_started tenant=%s", tenant)
        resp = requests.get(
            f"{bongo_url}/v1/org/{tenant}/integrations/salesforce/ping",
            headers={"Authorization": bongo_auth},
            timeout=60,  # bongo may need to wait for the Argo lock + call SF
        )
        resp.raise_for_status()
        tested = resp.json().get("tested", False)
        if tested:
            LOGGER.info("SF RTR: bongo ping succeeded event=bongo_ping_success tenant=%s", tenant)
        else:
            # tested=false is unlikely for Salesforce (broken connections raise exceptions).
            LOGGER.warning(
                "SF RTR: bongo ping returned tested=false event=bongo_ping_failed "
                "tenant=%s — SF connector may need reconnection", tenant,
            )

    def _update_credentials(self, creds: dict) -> bool:
        """Apply access_token and instance_url from Argo creds. Returns True if AT changed."""
        prev = self._access_token
        if creds.get("access_token"):
            self._access_token = creds["access_token"]
        if creds.get("instance_url"):
            self._instance_url = creds["instance_url"]
        return prev is not None and self._access_token != prev

    def _apply_fresh_at(self, creds: dict, tenant: str) -> None:
        """Update AT from Argo creds after a bongo ping; log whether it changed."""
        changed = self._update_credentials(creds)
        if changed:
            LOGGER.info(
                "SF RTR: AT refreshed successfully event=at_refresh_success tenant=%s", tenant,
            )
        else:
            # AT unchanged — bongo may have adopted an existing valid AT,
            # or the connected app does not rotate tokens. The retry may still 401.
            LOGGER.warning(
                "SF RTR: AT unchanged after bongo ping event=at_unchanged_after_ping "
                "tenant=%s — retry may still return 401", tenant,
            )

    @staticmethod
    def _basic_auth(key: str) -> str:
        """Basic auth header value: Basic base64(key + ':')."""
        return "Basic " + base64.b64encode(f"{key}:".encode()).decode()

    def _argo_auth(self) -> str:
        return self._basic_auth(os.environ.get("ARGO_CONNECTOR_API_KEY", ""))

    def _fetch_argo_credentials(self, argo_url: str, tenant: str) -> dict:
        """GET current connector credentials from Argo."""
        resp = requests.get(
            f"{argo_url}/v1/tenant/{tenant}/connectors/salesforce",
            headers={"Authorization": self._argo_auth()},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("credentials") or {}


class SalesforceAuthPassword(SalesforceAuth):
    def login(self):
        login = SalesforceLogin(sandbox=self.is_sandbox, **self._credentials._asdict())
        self._access_token, host = login
        self._instance_url = "https://" + host

# ruff: noqa: SLF001
"""Unit tests for Argo/bongo-backed credential management in SalesforceAuthOAuth."""

import base64
import importlib.util
import os
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_spec = importlib.util.spec_from_file_location(
    "credentials",
    Path(__file__).parent.parent / "tap_salesforce" / "salesforce" / "credentials.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
OAuthCredentials = _mod.OAuthCredentials
SalesforceAuthOAuth = _mod.SalesforceAuthOAuth
parse_credentials = _mod.parse_credentials


CREDS = OAuthCredentials(client_id="", client_secret="", refresh_token="")
ARGO_ENV = {"ARGO_URL": "http://argo", "TENANT": "42", "ARGO_CONNECTOR_API_KEY": "argo-key"}
BONGO_ENV = {**ARGO_ENV, "BONGO_API_TARGET_URL": "http://bongo", "BONGO_API_BASIC_AUTH_USERNAME": "F4BFB409-TEST"}

_ARGO_AUTH  = "Basic " + base64.b64encode(b"argo-key:").decode()
_BONGO_AUTH = "Basic " + base64.b64encode(b"F4BFB409-TEST:").decode()


def _make_auth():
    return SalesforceAuthOAuth(CREDS)


def _mock_resp(json_data, status=200):
    r = MagicMock()
    r.json.return_value = json_data
    r.raise_for_status = MagicMock()
    if status >= 400:
        r.raise_for_status.side_effect = Exception(f"HTTP {status}")
    return r


def _argo_creds(at="AT1"):
    return _mock_resp({"credentials": {"access_token": at, "instance_url": "https://sf"}})


# ── parse_credentials ──────────────────────────────────────────────────────────

_ALL_REQUIRED = {
    "ARGO_URL": "http://argo",
    "TENANT": "42",
    "ARGO_CONNECTOR_API_KEY": "argo-key",
    "BONGO_API_TARGET_URL": "http://bongo",
    "BONGO_API_BASIC_AUTH_USERNAME": "bongo-user",
}


class TestParseCredentials:
    def test_argo_mode_returns_empty_oauth_credentials(self):
        """All 5 vars set → returns empty OAuthCredentials for Argo bootstrap."""
        with patch.dict("os.environ", _ALL_REQUIRED):
            creds = parse_credentials({})
        assert isinstance(creds, OAuthCredentials)
        assert creds.client_id == "" and creds.client_secret == "" and creds.refresh_token == ""

    def test_argo_mode_ignores_config_fields(self):
        """Config fields are irrelevant in Argo mode — credentials come from Argo at runtime."""
        with patch.dict("os.environ", _ALL_REQUIRED):
            creds = parse_credentials({"client_id": "ignored", "refresh_token": "ignored"})
        assert creds.client_id == "" and creds.refresh_token == ""

    @pytest.mark.parametrize("missing", [
        "TENANT", "ARGO_CONNECTOR_API_KEY", "BONGO_API_TARGET_URL", "BONGO_API_BASIC_AUTH_USERNAME",
    ])
    def test_fails_immediately_when_any_required_var_missing(self, missing):
        """When ARGO_URL is set (Argo mode), all other vars must be present — fail fast."""
        env = {k: v for k, v in _ALL_REQUIRED.items() if k != missing}
        with patch.dict("os.environ", env, clear=False):
            os.environ.pop(missing, None)
            with pytest.raises(RuntimeError, match="missing required env vars"):
                parse_credentials({})

    def test_error_message_names_missing_vars(self):
        """Error message lists which specific vars are missing."""
        env = {"ARGO_URL": "http://argo"}  # missing 4 vars
        with patch.dict("os.environ", env, clear=False):
            for k in _ALL_REQUIRED:
                if k != "ARGO_URL":
                    os.environ.pop(k, None)
            with pytest.raises(RuntimeError) as exc_info:
                parse_credentials({})
        msg = str(exc_info.value)
        assert "TENANT" in msg
        assert "BONGO_API_TARGET_URL" in msg

    @pytest.mark.parametrize("empty_var", [
        "TENANT", "ARGO_CONNECTOR_API_KEY", "BONGO_API_TARGET_URL", "BONGO_API_BASIC_AUTH_USERNAME",
    ])
    def test_empty_string_var_treated_as_missing(self, empty_var):
        """Empty string is falsy — treated same as absent. ECS task with blank Variable fails fast."""
        env = {**_ALL_REQUIRED, empty_var: ""}
        with patch.dict("os.environ", env, clear=False):
            with pytest.raises(RuntimeError, match="missing required env vars"):
                parse_credentials({})


# ── login() ────────────────────────────────────────────────────────────────────

class TestLogin:
    def test_raises_when_argo_url_missing_at_login(self):
        """Defense-in-depth: login() raises if ARGO_URL is absent even after parse_credentials."""
        auth = _make_auth()
        with patch.dict("os.environ", {}, clear=False):
            os.environ.pop("ARGO_URL", None)
            with pytest.raises(RuntimeError):
                auth.login()


# ── _sync_from_argo() — timer path ────────────────────────────────────────────

class TestSyncFromArgo:
    def test_sets_access_token_and_instance_url(self):
        auth = _make_auth()
        with patch.dict("os.environ", ARGO_ENV), \
             patch("requests.get", return_value=_argo_creds("AT_LIVE")), \
             patch.object(threading.Timer, "start"):
            auth._sync_from_argo("http://argo", "42")
        assert auth._access_token == "AT_LIVE"
        assert auth._instance_url == "https://sf"

    def test_timer_restarts_on_success(self):
        mock_timer = MagicMock()
        auth = _make_auth()
        with patch.dict("os.environ", ARGO_ENV), \
             patch("requests.get", return_value=_argo_creds()), \
             patch("threading.Timer", return_value=mock_timer):
            auth._sync_from_argo("http://argo", "42")
        mock_timer.start.assert_called_once()

    def test_timer_restarts_on_failure(self):
        mock_timer = MagicMock()
        auth = _make_auth()
        with patch.dict("os.environ", ARGO_ENV), \
             patch("requests.get", side_effect=Exception("Argo down")), \
             patch("threading.Timer", return_value=mock_timer), \
             pytest.raises(Exception):
            auth._sync_from_argo("http://argo", "42")
        mock_timer.start.assert_called_once()

    def test_keeps_existing_at_when_argo_returns_empty(self):
        auth = _make_auth()
        auth._access_token = "EXISTING_AT"
        with patch.dict("os.environ", ARGO_ENV), \
             patch("requests.get", return_value=_mock_resp({"credentials": {}})), \
             patch.object(threading.Timer, "start"):
            auth._sync_from_argo("http://argo", "42")
        assert auth._access_token == "EXISTING_AT"

    def test_subsequent_calls_pick_up_updated_at(self):
        auth = _make_auth()
        with patch.dict("os.environ", ARGO_ENV), \
             patch("requests.get") as mock_get, \
             patch.object(threading.Timer, "start"):
            mock_get.return_value = _argo_creds("AT1")
            auth._sync_from_argo("http://argo", "42")
            assert auth._access_token == "AT1"

            mock_get.return_value = _argo_creds("AT2")
            auth._sync_from_argo("http://argo", "42")
            assert auth._access_token == "AT2"

    def test_argo_failure_raises_and_logs(self, caplog):
        auth = _make_auth()
        with patch.dict("os.environ", ARGO_ENV), \
             patch("requests.get", side_effect=Exception("timeout")), \
             patch.object(threading.Timer, "start"), \
             caplog.at_level("ERROR"), \
             pytest.raises(Exception, match="timeout"):
            auth._sync_from_argo("http://argo", "42")
        assert any("argo_sync_failed" in r.message for r in caplog.records)

    def test_empty_argo_credentials_logs_warning(self, caplog):
        """Argo returns empty credentials at startup — AT stays None, warning logged."""
        auth = _make_auth()
        with patch.dict("os.environ", ARGO_ENV), \
             patch("requests.get", return_value=_mock_resp({"credentials": {}})), \
             patch.object(threading.Timer, "start"), \
             caplog.at_level("WARNING"):
            auth._sync_from_argo("http://argo", "42")
        assert auth._access_token is None
        assert any("argo_no_at" in r.message for r in caplog.records)

    def test_update_credentials_returns_true_when_at_changes(self):
        """_update_credentials returns True iff AT changed from a previous non-None value."""
        auth = _make_auth()
        auth._access_token = "OLD"
        changed = auth._update_credentials({"access_token": "NEW", "instance_url": "https://sf"})
        assert changed is True
        assert auth._access_token == "NEW"

    def test_update_credentials_returns_false_on_first_call(self):
        """_update_credentials returns False on first call (prev AT was None)."""
        auth = _make_auth()
        changed = auth._update_credentials({"access_token": "AT1"})
        assert changed is False  # prev was None → not "changed"
        assert auth._access_token == "AT1"

    def test_update_credentials_skips_empty_at(self):
        """Empty access_token in creds is ignored — existing AT preserved."""
        auth = _make_auth()
        auth._access_token = "KEEP"
        auth._update_credentials({"access_token": ""})
        assert auth._access_token == "KEEP"


# ── refresh_access_token() — 401 path ─────────────────────────────────────────

class TestRefreshAccessToken:
    def test_happy_path_pings_bongo_then_reads_from_argo(self):
        """Bongo ping succeeds, fresh AT read from Argo."""
        auth = _make_auth()
        auth._access_token = "EXPIRED_AT"

        with patch.dict("os.environ", BONGO_ENV), \
             patch("requests.get") as mock_get, \
             patch.object(threading.Timer, "start"):
            mock_get.side_effect = [_mock_resp({"tested": True}), _argo_creds("FRESH_AT")]
            auth.refresh_access_token()

        assert auth._access_token == "FRESH_AT"
        assert mock_get.call_count == 2
        assert "bongo" in mock_get.call_args_list[0][0][0] and "ping" in mock_get.call_args_list[0][0][0]
        assert "argo" in mock_get.call_args_list[1][0][0]

    def test_both_requests_use_correct_basic_auth(self):
        """Bongo uses Basic auth with BONGO username; Argo uses Basic auth with ARGO key."""
        auth = _make_auth()
        with patch.dict("os.environ", BONGO_ENV), \
             patch("requests.get") as mock_get, \
             patch.object(threading.Timer, "start"):
            mock_get.side_effect = [_mock_resp({"tested": True}), _argo_creds("AT2")]
            auth.refresh_access_token()

        ping_auth = mock_get.call_args_list[0][1]["headers"]["Authorization"]
        argo_auth = mock_get.call_args_list[1][1]["headers"]["Authorization"]
        assert ping_auth == _BONGO_AUTH, f"Expected {_BONGO_AUTH}, got {ping_auth}"
        assert argo_auth == _ARGO_AUTH,  f"Expected {_ARGO_AUTH}, got {argo_auth}"

    def test_ping_tested_false_logs_warning_but_still_reads_argo(self, caplog):
        """tested=false is an unlikely bongo non-failure — warn but still read from Argo."""
        auth = _make_auth()
        auth._access_token = "OLD_AT"
        with patch.dict("os.environ", BONGO_ENV), \
             patch("requests.get") as mock_get, \
             patch.object(threading.Timer, "start"), \
             caplog.at_level("WARNING"):
            mock_get.side_effect = [_mock_resp({"tested": False}), _argo_creds("NEW_AT")]
            auth.refresh_access_token()
        assert any("bongo_ping_failed" in r.message for r in caplog.records)
        assert auth._access_token == "NEW_AT"

    def test_at_unchanged_after_ping_logs_warning(self, caplog):
        auth = _make_auth()
        auth._access_token = "SAME_AT"
        with patch.dict("os.environ", BONGO_ENV), \
             patch("requests.get") as mock_get, \
             patch.object(threading.Timer, "start"), \
             caplog.at_level("WARNING"):
            mock_get.side_effect = [_mock_resp({"tested": True}), _argo_creds("SAME_AT")]
            auth.refresh_access_token()
        assert any("at_unchanged_after_ping" in r.message for r in caplog.records)

    def test_bongo_error_raises_and_logs(self, caplog):
        auth = _make_auth()
        with patch.dict("os.environ", BONGO_ENV), \
             patch("requests.get", side_effect=Exception("bongo unreachable")), \
             patch.object(threading.Timer, "start"), \
             caplog.at_level("ERROR"), \
             pytest.raises(Exception, match="bongo unreachable"):
            auth.refresh_access_token()
        assert any("at_refresh_error" in r.message for r in caplog.records)

    def test_raises_without_bongo_url(self):
        auth = _make_auth()
        with patch.dict("os.environ", ARGO_ENV):
            with pytest.raises(RuntimeError, match="BONGO_API_TARGET_URL"):
                auth.refresh_access_token()

    def test_missing_bongo_auth_username_logs_warning(self, caplog):
        auth = _make_auth()
        env = {**BONGO_ENV, "BONGO_API_BASIC_AUTH_USERNAME": ""}
        with patch.dict("os.environ", env), \
             patch("requests.get") as mock_get, \
             patch.object(threading.Timer, "start"), \
             caplog.at_level("WARNING"):
            mock_get.side_effect = [_mock_resp({"tested": True}), _argo_creds("AT2")]
            auth.refresh_access_token()
        assert any("BONGO_API_BASIC_AUTH_USERNAME not set" in r.message for r in caplog.records)

    def test_bongo_non_json_response_raises_and_logs(self, caplog):
        """Bongo returns HTTP 200 with non-JSON body (proxy HTML) → at_refresh_error."""
        auth = _make_auth()
        bad_resp = MagicMock()
        bad_resp.raise_for_status = MagicMock()
        bad_resp.json.side_effect = Exception("not json")
        with patch.dict("os.environ", BONGO_ENV), \
             patch("requests.get", return_value=bad_resp), \
             patch.object(threading.Timer, "start"), \
             caplog.at_level("ERROR"), \
             pytest.raises(Exception, match="not json"):
            auth.refresh_access_token()
        assert any("at_refresh_error" in r.message for r in caplog.records)

    def test_argo_returns_no_at_after_bongo_ping_logs_warning(self, caplog):
        """Bongo ping succeeds but Argo returns no AT — at_unchanged_after_ping warning."""
        auth = _make_auth()
        auth._access_token = "CURRENT"
        with patch.dict("os.environ", BONGO_ENV), \
             patch("requests.get") as mock_get, \
             patch.object(threading.Timer, "start"), \
             caplog.at_level("WARNING"):
            mock_get.side_effect = [
                _mock_resp({"tested": True}),
                _mock_resp({"credentials": {}}),  # Argo returns empty
            ]
            auth.refresh_access_token()
        # AT stays unchanged since Argo returned nothing
        assert auth._access_token == "CURRENT"
        assert any("at_unchanged_after_ping" in r.message for r in caplog.records)

    def test_apply_fresh_at_with_no_at_in_creds(self, caplog):
        """_apply_fresh_at with no AT in creds dict logs at_unchanged_after_ping."""
        auth = _make_auth()
        auth._access_token = "OLD"
        with patch.dict("os.environ", ARGO_ENV), \
             caplog.at_level("WARNING"):
            auth._apply_fresh_at({}, "42")
        assert auth._access_token == "OLD"  # unchanged
        assert any("at_unchanged_after_ping" in r.message for r in caplog.records)

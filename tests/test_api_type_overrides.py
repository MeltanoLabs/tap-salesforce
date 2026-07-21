"""Unit tests for per-stream api_type overrides + Task Bulk operation handling.

Changes covered:
- api_type_overrides validation/normalization (case-insensitive keys, uppercased
  and validated values)
- Salesforce.effective_api_type() resolution (override wins, else global)
- Salesforce.query() routes per-stream (Task -> Bulk, others -> global Rest)
- Bulk._job_operation() picks `query` for Task, `queryAll` otherwise

Run with:
    pytest tests/test_api_type_overrides.py -v
"""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import HTTPError

from tap_salesforce.salesforce import (
    BULK_API_TYPE,
    BULK2_API_TYPE,
    REST_API_TYPE,
    Salesforce,
)
from tap_salesforce.salesforce.bulk import Bulk, _error_code
from tap_salesforce.salesforce.exceptions import (
    TapSalesforceExceptionError,
    TapSalesforceOperationTooLargeError,
)


def make_sf(api_type=REST_API_TYPE, api_type_overrides=None):
    """Build a minimal Salesforce instance without network calls."""
    sf = Salesforce.__new__(Salesforce)
    sf.api_type = api_type
    sf.api_type_overrides = Salesforce._normalize_api_type_overrides(api_type_overrides)
    return sf


def catalog_entry(stream):
    return {"stream": stream, "tap_stream_id": stream, "metadata": []}


# ---------------------------------------------------------------------------
# 1. _normalize_api_type_overrides
# ---------------------------------------------------------------------------

class TestNormalizeApiTypeOverrides:
    def test_none_yields_empty_map(self):
        assert Salesforce._normalize_api_type_overrides(None) == {}

    def test_keys_lowercased_values_uppercased(self):
        result = Salesforce._normalize_api_type_overrides({"Task": "bulk"})
        assert result == {"task": BULK_API_TYPE}

    def test_all_valid_api_types_accepted(self):
        result = Salesforce._normalize_api_type_overrides(
            {"Task": "BULK", "Event": "bulk2", "Lead": "rest"}
        )
        assert result == {"task": BULK_API_TYPE, "event": BULK2_API_TYPE, "lead": REST_API_TYPE}

    def test_invalid_value_raises(self):
        with pytest.raises(TapSalesforceExceptionError):
            Salesforce._normalize_api_type_overrides({"Task": "BLUK"})


# ---------------------------------------------------------------------------
# 2. effective_api_type
# ---------------------------------------------------------------------------

class TestEffectiveApiType:
    def test_override_wins(self):
        sf = make_sf(api_type=REST_API_TYPE, api_type_overrides={"Task": "BULK"})
        assert sf.effective_api_type("Task") == BULK_API_TYPE

    def test_override_lookup_is_case_insensitive(self):
        sf = make_sf(api_type=REST_API_TYPE, api_type_overrides={"task": "BULK"})
        assert sf.effective_api_type("Task") == BULK_API_TYPE
        assert sf.effective_api_type("TASK") == BULK_API_TYPE

    def test_falls_back_to_global_for_unlisted_stream(self):
        sf = make_sf(api_type=REST_API_TYPE, api_type_overrides={"Task": "BULK"})
        assert sf.effective_api_type("Lead") == REST_API_TYPE


# ---------------------------------------------------------------------------
# 3. query() routing
# ---------------------------------------------------------------------------

class TestQueryRouting:
    def test_override_routes_to_bulk(self):
        sf = make_sf(api_type=REST_API_TYPE, api_type_overrides={"Task": "BULK"})
        with patch("tap_salesforce.salesforce.Bulk") as mock_bulk, patch(
            "tap_salesforce.salesforce.Rest"
        ) as mock_rest:
            mock_bulk.return_value.query.return_value = iter([])
            list(sf.query(catalog_entry("Task"), {}))
            mock_bulk.assert_called_once_with(sf)
            mock_rest.assert_not_called()

    def test_rest_stream_uses_rest(self):
        sf = make_sf(api_type=REST_API_TYPE, api_type_overrides={"Task": "BULK"})
        with patch("tap_salesforce.salesforce.Bulk") as mock_bulk, patch(
            "tap_salesforce.salesforce.Rest"
        ) as mock_rest:
            mock_rest.return_value.query.return_value = iter([])
            list(sf.query(catalog_entry("Lead"), {}))
            mock_rest.assert_called_once_with(sf)
            mock_bulk.assert_not_called()

    def test_query_resets_pk_chunking(self):
        sf = make_sf()
        sf.pk_chunking = True
        with patch("tap_salesforce.salesforce.Rest") as mock_rest:
            mock_rest.return_value.query.return_value = iter([])
            list(sf.query(catalog_entry("Lead"), {}))
        assert sf.pk_chunking is False


# ---------------------------------------------------------------------------
# 5. REST -> Bulk fallback on OPERATION_TOO_LARGE
# ---------------------------------------------------------------------------

class TestRestBulkFallback:
    def test_falls_back_to_bulk_when_rest_too_large_and_nothing_emitted(self):
        sf = make_sf(api_type=REST_API_TYPE)

        def rest_raises():
            raise TapSalesforceOperationTooLargeError("boom")
            yield  # pragma: no cover - marks this a generator

        with patch("tap_salesforce.salesforce.Rest") as mock_rest, patch(
            "tap_salesforce.salesforce.Bulk"
        ) as mock_bulk:
            mock_rest.return_value.query.return_value = rest_raises()
            mock_bulk.return_value.query.return_value = iter([{"Id": "b1"}])
            records = list(sf.query(catalog_entry("Task"), {}))
        assert records == [{"Id": "b1"}]
        mock_bulk.assert_called_once_with(sf)

    def test_does_not_fall_back_after_records_emitted(self):
        sf = make_sf(api_type=REST_API_TYPE)

        def rest_emit_then_raise():
            yield {"Id": "1"}
            raise TapSalesforceOperationTooLargeError("boom")

        with patch("tap_salesforce.salesforce.Rest") as mock_rest, patch(
            "tap_salesforce.salesforce.Bulk"
        ) as mock_bulk:
            mock_rest.return_value.query.return_value = rest_emit_then_raise()
            with pytest.raises(TapSalesforceOperationTooLargeError):
                list(sf.query(catalog_entry("Task"), {}))
            mock_bulk.assert_not_called()

    def test_no_fallback_for_bulk_unsupported_object(self):
        # TaskWhoRelation is REST-queryable but Bulk-unsupported; escalation would
        # fail at Bulk job creation, so the original REST error must surface.
        from tap_salesforce.salesforce import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS

        assert "TaskWhoRelation" in UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS
        sf = make_sf(api_type=REST_API_TYPE)

        def rest_raises():
            raise TapSalesforceOperationTooLargeError("boom")
            yield  # pragma: no cover - marks this a generator

        with patch("tap_salesforce.salesforce.Rest") as mock_rest, patch(
            "tap_salesforce.salesforce.Bulk"
        ) as mock_bulk:
            mock_rest.return_value.query.return_value = rest_raises()
            with pytest.raises(TapSalesforceOperationTooLargeError):
                list(sf.query(catalog_entry("TaskWhoRelation"), {}))
            mock_bulk.assert_not_called()

    def test_no_fallback_when_rest_succeeds(self):
        sf = make_sf(api_type=REST_API_TYPE)
        with patch("tap_salesforce.salesforce.Rest") as mock_rest, patch(
            "tap_salesforce.salesforce.Bulk"
        ) as mock_bulk:
            mock_rest.return_value.query.return_value = iter([{"Id": "1"}])
            records = list(sf.query(catalog_entry("Lead"), {}))
        assert records == [{"Id": "1"}]
        mock_bulk.assert_not_called()


# ---------------------------------------------------------------------------
# 6. Bulk quota check tolerates disabled /limits
# ---------------------------------------------------------------------------

def _fake_sf_for_quota(make_request):
    return SimpleNamespace(
        data_url="{}/services/data/v60.0/{}",
        instance_url="https://x.my.salesforce.com",
        auth=SimpleNamespace(rest_headers={}),
        _make_request=make_request,
        quota_percent_total=95,
        quota_percent_per_run=25,
        jobs_completed=0,
    )


def _http_error(status_code, body):
    resp = Mock()
    resp.status_code = status_code
    resp.json.return_value = body
    return HTTPError(response=resp)


class TestCheckBulkQuotaUsage:
    def test_skips_on_api_disabled_for_org_403(self):
        raiser = Mock(side_effect=_http_error(403, [{"errorCode": "API_DISABLED_FOR_ORG"}]))
        bulk = Bulk(_fake_sf_for_quota(raiser))
        assert bulk.check_bulk_quota_usage() is None  # no raise

    def test_reraises_non_403_http_error(self):
        raiser = Mock(side_effect=_http_error(500, [{"errorCode": "SERVER_ERROR"}]))
        bulk = Bulk(_fake_sf_for_quota(raiser))
        with pytest.raises(HTTPError):
            bulk.check_bulk_quota_usage()

    def test_reraises_other_403(self):
        # A 403 that is NOT API_DISABLED_FOR_ORG (e.g. rate limit) must surface,
        # not be swallowed into a Bulk job.
        raiser = Mock(side_effect=_http_error(403, [{"errorCode": "REQUEST_LIMIT_EXCEEDED"}]))
        bulk = Bulk(_fake_sf_for_quota(raiser))
        with pytest.raises(HTTPError):
            bulk.check_bulk_quota_usage()


class TestErrorCode:
    def test_parses_list_body(self):
        resp = Mock()
        resp.json.return_value = [{"errorCode": "API_DISABLED_FOR_ORG"}]
        assert _error_code(resp) == "API_DISABLED_FOR_ORG"

    def test_parses_dict_body(self):
        resp = Mock()
        resp.json.return_value = {"errorCode": "X"}
        assert _error_code(resp) == "X"

    def test_none_on_unparseable(self):
        resp = Mock()
        resp.json.side_effect = ValueError("no json")
        assert _error_code(resp) is None


# ---------------------------------------------------------------------------
# 4. Bulk._job_operation
# ---------------------------------------------------------------------------

class TestBulkJobOperation:
    @pytest.mark.parametrize("stream", ["Task", "task", "TASK"])
    def test_task_uses_query(self, stream):
        assert Bulk._job_operation(stream) == "query"

    @pytest.mark.parametrize("stream", ["Lead", "Account", "Event", "Opportunity"])
    def test_non_task_uses_query_all(self, stream):
        assert Bulk._job_operation(stream) == "queryAll"

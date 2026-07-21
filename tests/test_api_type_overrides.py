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

from unittest.mock import patch

import pytest

from tap_salesforce.salesforce import (
    BULK_API_TYPE,
    BULK2_API_TYPE,
    REST_API_TYPE,
    Salesforce,
)
from tap_salesforce.salesforce.bulk import Bulk
from tap_salesforce.salesforce.exceptions import TapSalesforceExceptionError


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
    def test_task_routes_to_bulk_others_to_global(self):
        sf = make_sf(api_type=REST_API_TYPE, api_type_overrides={"Task": "BULK"})
        state = {}

        with patch("tap_salesforce.salesforce.Bulk") as mock_bulk, patch(
            "tap_salesforce.salesforce.Rest"
        ) as mock_rest:
            sf.query(catalog_entry("Task"), state)
            mock_bulk.assert_called_once_with(sf)
            mock_rest.assert_not_called()

        with patch("tap_salesforce.salesforce.Bulk") as mock_bulk, patch(
            "tap_salesforce.salesforce.Rest"
        ) as mock_rest:
            sf.query(catalog_entry("Lead"), state)
            mock_rest.assert_called_once_with(sf)
            mock_bulk.assert_not_called()


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

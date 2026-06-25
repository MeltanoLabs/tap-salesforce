# ruff: noqa: SLF001
"""Unit tests for observability module."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from tap_salesforce.observability import (
    _dd_metric,
    get_tenant_id,
    log_quota_consumed,
    log_quota_status,
    log_stream_sync_complete,
    log_sync_complete,
    log_sync_start,
)


class TestDdMetric:
    """Tests for _dd_metric helper."""

    def test_dd_metric_default_gauge(self) -> None:
        """Test _dd_metric returns gauge type by default."""
        result = _dd_metric("mdi.salesforce.api.pre_extract", 42.5)

        assert result == {
            "dd": {
                "metric_name": "mdi.salesforce.api.pre_extract",
                "metric_value": 42.5,
                "metric_type": "gauge",
            }
        }

    def test_dd_metric_count_type(self) -> None:
        """Test _dd_metric with count type."""
        result = _dd_metric("mdi.salesforce.api.requests_by_job", 150, "count")

        assert result == {
            "dd": {
                "metric_name": "mdi.salesforce.api.requests_by_job",
                "metric_value": 150,
                "metric_type": "count",
            }
        }

    def test_dd_metric_zero_value(self) -> None:
        """Test _dd_metric with zero value."""
        result = _dd_metric("mdi.salesforce.stream.records", 0, "count")

        assert result["dd"]["metric_value"] == 0


class TestGetTenantId:
    """Tests for get_tenant_id."""

    def test_get_tenant_id_from_env(self) -> None:
        """Test get_tenant_id returns TENANT from environment."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            assert get_tenant_id() == "3303"

    def test_get_tenant_id_missing(self) -> None:
        """Test get_tenant_id returns None when TENANT not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert get_tenant_id() is None


class TestLogSyncStart:
    """Tests for log_sync_start."""

    @pytest.fixture
    def mock_sf(self) -> MagicMock:
        """Create a mock Salesforce client."""
        sf = MagicMock()
        sf.api_type = "REST"
        sf.quota_percent_total = 80
        sf.quota_percent_per_run = 25
        sf.is_sandbox = False
        sf.instance_url = "https://test.salesforce.com"
        return sf

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_sync_start_emits_structured_log(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_sync_start emits structured JSON log."""
        catalog = {"streams": [{"stream": "Lead"}, {"stream": "Contact"}]}
        config = {"max_workers": 4}

        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_sync_start(mock_sf, catalog, config)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["event_type"] == "salesforce_sync_start"
        assert log_json["tenant_id"] == "3303"
        assert log_json["api_type"] == "REST"
        assert log_json["streams_count"] == 2
        assert log_json["streams"] == ["Lead", "Contact"]
        assert log_json["max_workers"] == 4


class TestLogSyncComplete:
    """Tests for log_sync_complete."""

    @pytest.fixture
    def mock_sf(self) -> MagicMock:
        """Create a mock Salesforce client."""
        sf = MagicMock()
        sf.api_type = "REST"
        sf.rest_requests_attempted = 500
        sf.jobs_completed = 3
        sf.quota_percent_total = 80
        sf.quota_percent_per_run = 25
        return sf

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_sync_complete_contains_dd_metric(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_sync_complete emits dd metric for requests_by_job."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_sync_complete(mock_sf, {})

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["event_type"] == "salesforce_sync_complete"
        assert log_json["dd"]["metric_name"] == "mdi.salesforce.api.requests_by_job"
        assert log_json["dd"]["metric_value"] == 500
        assert log_json["dd"]["metric_type"] == "count"

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_sync_complete_with_error(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_sync_complete includes error info on failure."""
        error = RuntimeError("Connection timed out")

        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_sync_complete(mock_sf, {}, success=False, error=error)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["success"] is False
        assert log_json["error_type"] == "RuntimeError"
        assert "Connection timed out" in log_json["error_message"]

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_sync_complete_with_records_synced(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_sync_complete includes records_synced when provided."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_sync_complete(mock_sf, {}, records_synced=10000)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["records_synced"] == 10000


class TestLogQuotaStatus:
    """Tests for log_quota_status."""

    @pytest.fixture
    def mock_sf(self) -> MagicMock:
        """Create a mock Salesforce client."""
        sf = MagicMock()
        sf.api_type = "REST"
        sf.quota_percent_total = 80
        return sf

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_quota_status_pre_extract_phase(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_quota_status with pre_extract phase."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_quota_status(mock_sf, used=5000, allotted=100000, phase="pre_extract")

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["event_type"] == "salesforce_quota_status"
        assert log_json["phase"] == "pre_extract"
        assert log_json["quota_used"] == 5000
        assert log_json["quota_allotted"] == 100000
        assert log_json["quota_remaining"] == 95000
        assert log_json["quota_percent_used"] == 5.0
        assert log_json["dd"]["metric_name"] == "mdi.salesforce.api.pre_extract"
        assert log_json["dd"]["metric_value"] == 5.0

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_quota_status_post_extract_phase(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_quota_status with post_extract phase."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_quota_status(mock_sf, used=7500, allotted=100000, phase="post_extract")

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["phase"] == "post_extract"
        assert log_json["dd"]["metric_name"] == "mdi.salesforce.api.post_extract"
        assert log_json["dd"]["metric_value"] == 7.5

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_quota_status_current_phase_default(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_quota_status defaults to 'current' phase."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_quota_status(mock_sf, used=5000, allotted=100000)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["phase"] == "current"
        assert log_json["dd"]["metric_name"] == "mdi.salesforce.api.current"

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_quota_status_near_limit(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_quota_status detects near-limit condition."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_quota_status(mock_sf, used=85000, allotted=100000, phase="post_extract")

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["is_near_limit"] is True
        assert log_json["quota_percent_used"] == 85.0

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_quota_status_zero_allotted(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_quota_status handles zero allotted gracefully."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_quota_status(mock_sf, used=0, allotted=0, phase="pre_extract")

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["quota_percent_used"] == 0
        assert log_json["dd"]["metric_value"] == 0


class TestLogQuotaConsumed:
    """Tests for log_quota_consumed."""

    @pytest.fixture
    def mock_sf(self) -> MagicMock:
        """Create a mock Salesforce client."""
        sf = MagicMock()
        sf.api_type = "REST"
        return sf

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_quota_consumed_emits_delta(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_quota_consumed emits the delta between pre and post."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_quota_consumed(mock_sf, pre_used=5000, post_used=7500, allotted=100000)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["event_type"] == "salesforce_quota_consumed"
        assert log_json["tenant_id"] == "3303"
        assert log_json["calls_consumed"] == 2500
        assert log_json["percent_consumed"] == 2.5
        assert log_json["pre_used"] == 5000
        assert log_json["post_used"] == 7500
        assert log_json["allotted"] == 100000
        assert log_json["dd"]["metric_name"] == "mdi.salesforce.api.calls_consumed"
        assert log_json["dd"]["metric_value"] == 2500

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_quota_consumed_zero_delta(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_quota_consumed with no API calls consumed."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_quota_consumed(mock_sf, pre_used=5000, post_used=5000, allotted=100000)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["calls_consumed"] == 0
        assert log_json["dd"]["metric_value"] == 0

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_quota_consumed_zero_allotted(self, mock_logger: MagicMock, mock_sf: MagicMock) -> None:
        """Test log_quota_consumed handles zero allotted gracefully."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_quota_consumed(mock_sf, pre_used=0, post_used=0, allotted=0)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["percent_consumed"] == 0


class TestLogStreamSyncComplete:
    """Tests for log_stream_sync_complete."""

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_stream_sync_complete_contains_dd_metric(self, mock_logger: MagicMock) -> None:
        """Test log_stream_sync_complete emits dd metric for records count."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_stream_sync_complete("Lead", records_count=5000)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["event_type"] == "salesforce_stream_complete"
        assert log_json["stream_name"] == "Lead"
        assert log_json["records_count"] == 5000
        assert log_json["dd"]["metric_name"] == "mdi.salesforce.stream.records"
        assert log_json["dd"]["metric_value"] == 5000
        assert log_json["dd"]["metric_type"] == "count"

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_stream_sync_complete_none_records(self, mock_logger: MagicMock) -> None:
        """Test log_stream_sync_complete defaults to 0 when records_count is None."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_stream_sync_complete("Contact", records_count=None)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["dd"]["metric_value"] == 0

    @patch("tap_salesforce.observability.LOGGER")
    def test_log_stream_sync_complete_failure(self, mock_logger: MagicMock) -> None:
        """Test log_stream_sync_complete with failure."""
        with patch.dict(os.environ, {"TENANT": "3303"}):
            log_stream_sync_complete("Lead", records_count=0, success=False)

        call_args = mock_logger.info.call_args
        log_json = json.loads(call_args[0][1])

        assert log_json["success"] is False

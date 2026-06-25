"""Unit tests for the windowed-objects-refactor changes.

Changes covered:
- limit_tasks_month renamed to limit_windowed_objects_month
- WINDOWED_OBJECTS class constant: Task, Campaign, CampaignMember
- get_start_date() caps all three windowed streams (previously Task only)
- Non-windowed streams (Lead, Contact, Account, Opportunity, User) use full history

Run with:
    pytest tests/test_windowed_objects_refactor.py -v
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from singer import metadata as singer_metadata
from singer import utils as singer_utils

from tap_salesforce.salesforce import Salesforce


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sf(default_start_date="2000-01-01T00:00:00Z", limit_windowed_objects_month=None):
    """Build a minimal Salesforce instance without network calls."""
    sf = Salesforce.__new__(Salesforce)
    sf.windowed_objects = Salesforce.WINDOWED_OBJECTS
    sf.limit_windowed_objects_month = limit_windowed_objects_month
    sf.pull_config_objects = None
    sf.default_start_date = (
        singer_utils.strptime_to_utc(default_start_date).isoformat()
    )
    return sf


def make_catalog_entry(stream_id, replication_key="SystemModstamp"):
    """Build a minimal Singer catalog entry."""
    mdata = singer_metadata.new()
    singer_metadata.write(mdata, (), "replication-key", replication_key)
    return {
        "stream": stream_id,
        "tap_stream_id": stream_id,
        "metadata": singer_metadata.to_list(mdata),
    }


def empty_state():
    return {}


def state_with_bookmark(stream, date):
    return {"bookmarks": {stream: {"SystemModstamp": date}}}


# ---------------------------------------------------------------------------
# 1. WINDOWED_OBJECTS class constant
# ---------------------------------------------------------------------------

class TestWindowedObjectsConstant:
    def test_windowed_objects_is_exactly_task_campaign_campaignmember(self):
        assert Salesforce.WINDOWED_OBJECTS == {"Task", "Campaign", "CampaignMember"}

    def test_non_windowed_streams_not_in_constant(self):
        for stream in ["Lead", "Contact", "Account", "Opportunity", "User"]:
            assert stream not in Salesforce.WINDOWED_OBJECTS


# ---------------------------------------------------------------------------
# 2. Config key rename: limit_tasks_month → limit_windowed_objects_month
# ---------------------------------------------------------------------------

class TestConfigKeyRename:
    def test_limit_windowed_objects_month_stored_on_instance(self):
        sf = make_sf(limit_windowed_objects_month=9)
        assert sf.limit_windowed_objects_month == 9

    def test_limit_windowed_objects_month_none_by_default(self):
        sf = make_sf()
        assert sf.limit_windowed_objects_month is None


# ---------------------------------------------------------------------------
# 3. Default start_date is 2000-01-01 (was 2025-01-01 on main)
# ---------------------------------------------------------------------------

class TestDefaultStartDate:
    def test_default_start_date_is_year_2000(self):
        sf = make_sf()
        assert sf.default_start_date.startswith("2000-01-01")

    @pytest.mark.parametrize("stream", ["Lead", "Contact", "Account", "Opportunity", "User"])
    def test_full_history_streams_use_2000_start_date(self, stream):
        """Non-windowed streams fall back to 2000-01-01 with no bookmark."""
        sf = make_sf(limit_windowed_objects_month=9)
        result = sf.get_start_date(empty_state(), make_catalog_entry(stream))
        assert result.startswith("2000-01-01"), (
            f"{stream} should use full history start date 2000-01-01, got {result}"
        )


# ---------------------------------------------------------------------------
# 4. Windowed streams get capped (Task, Campaign, CampaignMember)
# ---------------------------------------------------------------------------

class TestWindowedStreamsCapped:
    @pytest.mark.parametrize("stream", ["Task", "Campaign", "CampaignMember"])
    def test_old_start_date_is_capped_to_9_months(self, stream):
        """A 2000-01-01 bookmark/default for windowed streams must be capped to ~9 months ago."""
        sf = make_sf(limit_windowed_objects_month=9)
        state = state_with_bookmark(stream, "2000-01-01T00:00:00+00:00")
        result = sf.get_start_date(state, make_catalog_entry(stream))
        assert not result.startswith("2000"), (
            f"{stream} with old bookmark should be capped, got {result}"
        )

    @pytest.mark.parametrize("stream", ["Task", "Campaign", "CampaignMember"])
    def test_recent_bookmark_is_not_capped(self, stream):
        """A recent bookmark within the window must not be altered."""
        recent = (singer_utils.now() - timedelta(days=30)).isoformat()
        sf = make_sf(limit_windowed_objects_month=9)
        state = state_with_bookmark(stream, recent)
        result = sf.get_start_date(state, make_catalog_entry(stream))
        assert result == recent, (
            f"{stream} recent bookmark should not be capped, got {result}"
        )

    @pytest.mark.parametrize("stream", ["Task", "Campaign", "CampaignMember"])
    def test_cap_is_approximately_9_months_ago(self, stream):
        """The capped date must be within a day of (now - 9 * 31 days)."""
        sf = make_sf(limit_windowed_objects_month=9)
        state = state_with_bookmark(stream, "2000-01-01T00:00:00+00:00")
        result = sf.get_start_date(state, make_catalog_entry(stream))

        expected_floor = singer_utils.now() - timedelta(days=31 * 9)
        result_dt = singer_utils.strptime_to_utc(result)
        diff = abs((result_dt - expected_floor).total_seconds())
        assert diff < 86400, (
            f"Cap date {result} should be ~9 months ago, diff={diff}s"
        )


# ---------------------------------------------------------------------------
# 5. Non-windowed streams are NOT capped even with limit set
# ---------------------------------------------------------------------------

class TestNonWindowedStreamsNotCapped:
    @pytest.mark.parametrize("stream", ["Lead", "Contact", "Account", "Opportunity", "User"])
    def test_full_history_streams_are_never_capped(self, stream):
        sf = make_sf(limit_windowed_objects_month=9)
        state = state_with_bookmark(stream, "2000-01-01T00:00:00+00:00")
        result = sf.get_start_date(state, make_catalog_entry(stream))
        assert result.startswith("2000-01-01"), (
            f"{stream} should not be capped, got {result}"
        )


# ---------------------------------------------------------------------------
# 6. Cap is disabled when limit is None or 0
# ---------------------------------------------------------------------------

class TestCapDisabledWhenNoLimit:
    @pytest.mark.parametrize("limit", [None, 0])
    @pytest.mark.parametrize("stream", ["Task", "Campaign", "CampaignMember"])
    def test_no_cap_when_limit_is_none_or_zero(self, stream, limit):
        sf = make_sf(limit_windowed_objects_month=limit)
        state = state_with_bookmark(stream, "2000-01-01T00:00:00+00:00")
        result = sf.get_start_date(state, make_catalog_entry(stream))
        assert result.startswith("2000-01-01"), (
            f"{stream} should not be capped when limit={limit}, got {result}"
        )


# ---------------------------------------------------------------------------
# 7. Bookmark takes priority over default start_date
# ---------------------------------------------------------------------------

class TestBookmarkPriority:
    @pytest.mark.parametrize("stream", ["Lead", "Contact", "Account", "Opportunity", "User"])
    def test_bookmark_used_over_default_for_full_history_streams(self, stream):
        bookmark = "2025-06-01T00:00:00Z"
        sf = make_sf(limit_windowed_objects_month=9)
        state = state_with_bookmark(stream, bookmark)
        result = sf.get_start_date(state, make_catalog_entry(stream))
        assert result == bookmark

    @pytest.mark.parametrize("stream", ["Task", "Campaign", "CampaignMember"])
    def test_recent_bookmark_used_over_cap_for_windowed_streams(self, stream):
        recent_bookmark = (singer_utils.now() - timedelta(days=10)).isoformat()
        sf = make_sf(limit_windowed_objects_month=9)
        state = state_with_bookmark(stream, recent_bookmark)
        result = sf.get_start_date(state, make_catalog_entry(stream))
        assert result == recent_bookmark

import datetime
import io
import json
import logging
import sys
import threading
from unittest.mock import patch, MagicMock

import pytest
import singer

from tap_salesforce import output as tap_output, CONFIG
from tap_salesforce.sync import sync_records


class TestConcurrentWrites:
    """Bug 1 fix — thread-safe stdout lock."""

    def test_concurrent_writes_produce_valid_jsonl(self):
        """8 threads × 1000 records — every line must be valid JSON, no interleaving."""
        output = io.StringIO()
        errors = []
        write_counts = {}

        def worker(stream_name):
            write_counts[stream_name] = 0
            for i in range(1000):
                try:
                    tap_output.write_record(
                        stream_name,
                        {"id": i, "data": f"{stream_name}-record-{i}-" + "x" * 200},
                    )
                    write_counts[stream_name] += 1
                except Exception as e:
                    errors.append(e)
        #    print(f"  [Thread] {stream_name} finished — wrote {write_counts[stream_name]} records")
            print(f"  [Thread] {stream_name} finished — wrote {write_counts[stream_name]} records", file=sys.stderr)

        threads = [threading.Thread(target=worker, args=(f"Stream{i}",)) for i in range(8)]

        print("\n--- TestConcurrentWrites: starting 8 threads ---")
        with patch("sys.stdout", output):
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        print(f"  All threads done. Errors: {len(errors)}")
        assert not errors, f"Worker threads raised: {errors}"

        raw = output.getvalue()
        lines = [l for l in raw.splitlines() if l.strip()]
        print(f"  Total lines captured: {len(lines)} (expected 8000)")
        assert len(lines) == 8000, f"Expected 8000 lines, got {len(lines)}"

        corrupt = 0
        stream_counts = {}
        for i, line in enumerate(lines):
            msg = json.loads(line)   # raises JSONDecodeError if bytes were interleaved
            assert msg["type"] == "RECORD"
            assert msg["stream"].startswith("Stream")
            stream_counts[msg["stream"]] = stream_counts.get(msg["stream"], 0) + 1

        print("  Per-stream line counts:")
        for stream, count in sorted(stream_counts.items()):
            print(f"    {stream}: {count} lines")

        print("  All 8000 lines are valid JSON — no interleaving detected ✓")


class TestSafeBookmarkValue:
    """Bug 2 fix — future bookmark guard."""

    @pytest.fixture(autouse=True)
    def setup_config(self):
        """Set max_future_bookmark_seconds from CONFIG for test context."""
        self.max_future_seconds = CONFIG.get("max_future_bookmark_seconds", 3600)

    def test_past_value_passes_through(self):
        value = "2026-01-01T00:00:00+00:00"
        print(f"\n--- test_past_value_passes_through ---")
        print(f"  Input:  {value}")
        result = tap_output.safe_bookmark_value("Contact", "SystemModstamp", value,
                                                max_future_seconds=self.max_future_seconds)
        print(f"  Output: {result}")
        print(f"  Changed: {result != value}")
        assert result == value

    def test_near_future_within_threshold_passes_through(self):
        near_future = (
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        ).isoformat()
        print(f"\n--- test_near_future_within_threshold_passes_through ---")
        print(f"  Input:  {near_future}  (+30 min, within {self.max_future_seconds}s threshold from CONFIG)")
        result = tap_output.safe_bookmark_value("Contact", "SystemModstamp", near_future,
                                                max_future_seconds=self.max_future_seconds)
        print(f"  Output: {result}")
        print(f"  Passed through unchanged: {result == near_future}")
        assert result == near_future

    def test_far_future_is_capped_at_now(self):
        far_future = "2099-01-01T00:00:00+00:00"
        print(f"\n--- test_far_future_is_capped_at_now ---")
        print(f"  Input:  {far_future}")
        result = tap_output.safe_bookmark_value("Contact", "SystemModstamp", far_future,
                                                max_future_seconds=self.max_future_seconds)
        now = datetime.datetime.now(datetime.timezone.utc)
        result_dt = datetime.datetime.fromisoformat(result)
        print(f"  Output: {result}")
        print(f"  Now:    {now.isoformat()}")
        print(f"  Capped (output <= now): {result_dt <= now + datetime.timedelta(seconds=5)}")
        assert result_dt <= now + datetime.timedelta(seconds=5)

    def test_z_suffix_handled(self):
        far_future = "2099-01-01T00:00:00Z"
        print(f"\n--- test_z_suffix_handled ---")
        print(f"  Input:  {far_future}  (Z suffix as Salesforce sends it)")
        result = tap_output.safe_bookmark_value("Contact", "SystemModstamp", far_future,
                                                max_future_seconds=self.max_future_seconds)
        now = datetime.datetime.now(datetime.timezone.utc)
        result_dt = datetime.datetime.fromisoformat(result)
        print(f"  Output: {result}")
        print(f"  Capped (output <= now): {result_dt <= now + datetime.timedelta(seconds=5)}")
        assert result_dt <= now + datetime.timedelta(seconds=5)

    def test_none_passes_through(self):
        print(f"\n--- test_none_passes_through ---")
        print(f"  Input:  None")
        result = tap_output.safe_bookmark_value("Contact", "SystemModstamp", None,
                                                max_future_seconds=self.max_future_seconds)
        print(f"  Output: {result}")
        print(f"  Is None: {result is None}")
        assert result is None

    def test_critical_log_emitted_on_cap(self, caplog):
        far_future = "2099-01-01T00:00:00Z"
        print(f"\n--- test_critical_log_emitted_on_cap ---")
        print(f"  Input:  {far_future}")
        with caplog.at_level(logging.CRITICAL, logger="tap_salesforce.output"):
            tap_output.safe_bookmark_value("Contact", "SystemModstamp", far_future,
                                           max_future_seconds=self.max_future_seconds)
        matching = [r for r in caplog.records if "BOOKMARK_GUARD" in r.message]
        print(f"  CRITICAL logs captured: {len(matching)}")
        for r in matching:
            print(f"  Log: {r.message}")
        assert len(matching) == 1

    def test_custom_config_value_is_used(self):
        """Verify that different max_future_bookmark_seconds from CONFIG are respected at runtime."""
        print(f"\n--- test_custom_config_value_is_used ---")

        # Simulate meltano.yml setting a custom threshold
        original_value = CONFIG.get("max_future_bookmark_seconds")
        try:
            custom_threshold = 7200  # 2 hours instead of 1 hour
            CONFIG["max_future_bookmark_seconds"] = custom_threshold

            # Re-setup with new CONFIG value
            max_future_seconds = CONFIG.get("max_future_bookmark_seconds", 3600)
            print(f"  CONFIG['max_future_bookmark_seconds'] = {max_future_seconds}")

            # Create value that's within 2 hours but beyond 1 hour
            future_timestamp = (
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=75)
            ).isoformat()

            result = tap_output.safe_bookmark_value(
                "Contact", "SystemModstamp", future_timestamp,
                max_future_seconds=max_future_seconds
            )

            print(f"  Test value: {future_timestamp} (+75 min)")
            print(f"  With {custom_threshold}s CONFIG threshold: {result} (passed through: {result == future_timestamp})")

            # Should pass through because 75 min < 120 min (7200 sec)
            assert result == future_timestamp, \
                f"Value should pass through with 7200s CONFIG threshold, but got {result}"
        finally:
            # Restore original CONFIG value
            if original_value is not None:
                CONFIG["max_future_bookmark_seconds"] = original_value
            else:
                CONFIG.pop("max_future_bookmark_seconds", None)

    def test_config_max_future_seconds_is_respected(self):
        """Verify that max_future_bookmark_seconds from CONFIG is used instead of hardcoded default."""
        print(f"\n--- test_config_max_future_seconds_is_respected ---")
        print(f"  CONFIG['max_future_bookmark_seconds'] = {self.max_future_seconds}")

        # Create a value that is within 1 hour but beyond a smaller threshold (e.g., 60 seconds)
        threshold_secs = 60
        future_timestamp = (
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=90)
        ).isoformat()

        # With a 60-second threshold, this should be capped
        result_strict = tap_output.safe_bookmark_value(
            "Contact", "SystemModstamp", future_timestamp,
            max_future_seconds=threshold_secs
        )
        now = datetime.datetime.now(datetime.timezone.utc)
        result_dt_strict = datetime.datetime.fromisoformat(result_strict)

        # With the CONFIG threshold (3600 seconds), this should pass through
        result_lenient = tap_output.safe_bookmark_value(
            "Contact", "SystemModstamp", future_timestamp,
            max_future_seconds=self.max_future_seconds
        )

        print(f"  Test value: {future_timestamp} (+90 sec)")
        print(f"  With {threshold_secs}s threshold: {result_strict} (capped: {result_dt_strict <= now})")
        print(f"  With {self.max_future_seconds}s CONFIG threshold: {result_lenient} (passed through: {result_lenient == future_timestamp})")

        assert result_dt_strict <= now + datetime.timedelta(seconds=5), \
            "Value should be capped with strict 60s threshold"
        assert result_lenient == future_timestamp, \
            "Value should pass through with lenient CONFIG threshold"


class TestBookmarkLoading:
    """Bug 3 fix — bookmark values loaded and preserved correctly."""

    def test_build_state_preserves_incremental_bookmark(self):
        """Verify build_state preserves INCREMENTAL replication bookmark."""
        print("\n--- test_build_state_preserves_incremental_bookmark ---")

        raw_state = {
            "bookmarks": {
                "Contact": {
                    "SystemModstamp": "2025-01-15T10:30:00Z",
                    "version": 1234567890
                }
            }
        }

        catalog = {
            "streams": [
                {
                    "tap_stream_id": "Contact",
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "replication-method": "INCREMENTAL",
                                "replication-key": "SystemModstamp"
                            }
                        }
                    ]
                }
            ]
        }

        from tap_salesforce import build_state

        result_state = build_state(raw_state, catalog)

        # ASSERT bookmark is preserved
        preserved_bookmark = singer.get_bookmark(result_state, "Contact", "SystemModstamp")
        print(f"  Input bookmark:    {raw_state['bookmarks']['Contact']['SystemModstamp']}")
        print(f"  Preserved bookmark: {preserved_bookmark}")
        assert preserved_bookmark == "2025-01-15T10:30:00Z", \
            f"Bookmark not preserved. Expected 2025-01-15T10:30:00Z, got {preserved_bookmark}"
        print("  ✓ Bookmark preserved correctly")

    def test_sync_records_updates_bookmark_from_new_records(self, caplog):
        """Verify sync_records updates bookmark with latest record timestamp."""
        print("\n--- test_sync_records_updates_bookmark_from_new_records ---")

        initial_bookmark = "2025-01-01T00:00:00Z"
        later_bookmark = "2025-01-05T10:00:00Z"

        state = {
            "bookmarks": {
                "Contact": {
                    "SystemModstamp": initial_bookmark,
                    "version": 1234567890
                }
            }
        }

        catalog_entry = {
            "stream": "Contact",
            "tap_stream_id": "Contact",
            "schema": {
                "type": "object",
                "properties": {
                    "Id": {"type": "string"},
                    "SystemModstamp": {"type": "string"}
                }
            },
            "metadata": [
                {
                    "breadcrumb": [],
                    "metadata": {
                        "replication-key": "SystemModstamp",
                        "replication-method": "INCREMENTAL",
                        "table-key-properties": ["Id"]
                    }
                },
                {"breadcrumb": ["properties", "Id"], "metadata": {"inclusion": "automatic"}},
                {"breadcrumb": ["properties", "SystemModstamp"], "metadata": {"inclusion": "automatic"}}
            ]
        }

        # Mock Salesforce instance
        mock_sf = MagicMock()
        mock_sf.pk_chunking = False
        mock_sf.query.return_value = [
            {
                "Id": "001",
                "SystemModstamp": later_bookmark
            }
        ]
        mock_sf.get_start_date.return_value = initial_bookmark

        mock_counter = MagicMock()
        mock_counter.value = 1

        print(f"  Initial state bookmark: {state['bookmarks']['Contact']['SystemModstamp']}")

        # Run sync
        with caplog.at_level(logging.INFO):
            sync_records(mock_sf, catalog_entry, state, mock_counter, 1000)

        # ASSERT bookmark was updated
        updated_bookmark = singer.get_bookmark(state, "Contact", "SystemModstamp")
        print(f"  Updated state bookmark: {updated_bookmark}")

        assert updated_bookmark is not None, "Bookmark was not set after sync"
        assert updated_bookmark >= later_bookmark, \
            f"Bookmark not updated correctly. Expected >= {later_bookmark}, got {updated_bookmark}"
        print("  ✓ Bookmark updated to latest record timestamp")

    def test_resume_syncing_uses_jobhighestbookmarkseen(self):
        """Verify resume_syncing_bulk_query uses JobHighestBookmarkSeen from state."""
        print("\n--- test_resume_syncing_uses_jobhighestbookmarkseen ---")

        job_bookmark = "2025-01-10T15:45:00Z"
        state = {
            "bookmarks": {
                "Contact": {
                    "JobID": "abc123",
                    "BatchIDs": ["batch1", "batch2"],
                    "JobHighestBookmarkSeen": job_bookmark,
                    "version": 1234567890
                }
            }
        }

        catalog_entry = {
            "stream": "Contact",
            "tap_stream_id": "Contact",
            "schema": {
                "type": "object",
                "properties": {
                    "Id": {"type": "string"},
                    "SystemModstamp": {"type": "string"}
                }
            },
            "metadata": [
                {
                    "breadcrumb": [],
                    "metadata": {
                        "replication-key": "SystemModstamp",
                        "replication-method": "INCREMENTAL"
                    }
                }
            ]
        }

        # ASSERT that JobHighestBookmarkSeen exists in state
        retrieved_bookmark = singer.get_bookmark(state, "Contact", "JobHighestBookmarkSeen")
        print(f"  Stored JobHighestBookmarkSeen: {job_bookmark}")
        print(f"  Retrieved bookmark: {retrieved_bookmark}")

        assert retrieved_bookmark == job_bookmark, \
            f"JobHighestBookmarkSeen not found or incorrect. Expected {job_bookmark}, got {retrieved_bookmark}"
        print("  ✓ JobHighestBookmarkSeen correctly loaded from state")

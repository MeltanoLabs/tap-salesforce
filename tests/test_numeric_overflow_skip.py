"""Tests for the Numeric Overflow row-skip path in tap_salesforce.salesforce.rest.

Covers:
  - _classify_error helper: maps SF error codes to "bisect" | "isolate" | None
  - _sync_isolated_rows: per-Id fetch with skip-on-overflow
  - _query_recur end-to-end: Numeric Overflow → bisect → isolate-mode → skip offender
  - Regression: pure OPERATION_TOO_LARGE that bottoms out at <1h still raises

Mocks Salesforce REST by patching `Rest.sf._make_request` to return canned
Response-like objects based on the SOQL `q` parameter, so the test exercises
the actual bisection + isolation logic without network access.

Source: RGI tenant 5578 Task Call_Log_Link__c — 2026-05-28.
"""
import logging
from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

from tap_salesforce.salesforce.rest import (
    Rest,
    MIN_BISECT_SECONDS,
    _classify_error,
)
from tap_salesforce.salesforce.exceptions import TapSalesforceExceptionError


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _http_error(status_code, body):
    """Build a requests.HTTPError carrying a JSON body, as Salesforce returns."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = body
    return HTTPError(response=response)


def _ok_response(records, next_records_url=None):
    """Build a Response-like object with .json() returning a SF query payload."""
    resp = MagicMock()
    resp.json.return_value = {
        "records": records,
        "nextRecordsUrl": next_records_url,
        "done": next_records_url is None,
    }
    return resp


def _catalog_entry(stream="Contact", replication_key="SystemModstamp"):
    """Minimal catalog_entry shape expected by _query_recur and _build_query_string."""
    return {
        "stream": stream,
        "tap_stream_id": stream,
        "metadata": [
            {
                "breadcrumb": [],
                "metadata": {
                    "replication-key": replication_key,
                    "replication-method": "INCREMENTAL",
                },
            }
        ],
    }


def _make_fake_sf(request_dispatcher, build_query_string=None):
    """Construct a fake Salesforce instance suitable for Rest._query_recur.

    `request_dispatcher` receives (method, url, headers, params) on each
    `_make_request` call and returns either a Response-like object or raises
    HTTPError. It lets tests script the sequence of SF responses.

    `build_query_string` mimics the real one with enough fidelity for tests:
    returns "SELECT * FROM <stream> WHERE <repl_key> >= <start> [AND <repl_key> < <end>] ORDER BY <repl_key> ASC".
    """
    def default_build_query_string(catalog_entry, start_date, end_date=None,
                                   order_by_clause=True):
        # Emit a multi-column projection so dispatchers can distinguish:
        #   - bisect / normal query:     "SELECT Id,SystemModstamp FROM ..."
        #   - isolate Id-enumeration:    "SELECT Id FROM ..."        (literal in _sync_isolated_rows)
        #   - per-Id fetch (isolate):    "SELECT Id,SystemModstamp FROM ... AND Id = '...'"
        repl = "SystemModstamp"
        q = f"SELECT Id,{repl} FROM {catalog_entry['stream']} WHERE {repl} >= {start_date}"
        if end_date:
            q += f" AND {repl} < {end_date}"
        if order_by_clause:
            q += f" ORDER BY {repl} ASC"
        return q

    sf = MagicMock()
    sf.instance_url = "https://test.my.salesforce.com"
    sf.auth.rest_headers = {"Authorization": "Bearer fake"}
    sf._make_request.side_effect = request_dispatcher
    sf._build_query_string.side_effect = build_query_string or default_build_query_string
    return sf


# --------------------------------------------------------------------------- #
# 1. _classify_error helper                                                    #
# --------------------------------------------------------------------------- #


class TestClassifyError:
    """Unit tests for the pure error-classification helper."""

    @pytest.mark.parametrize("code", ["QUERY_TIMEOUT", "OPERATION_TOO_LARGE"])
    def test_bisectable_codes_return_bisect(self, code):
        print(f"\n--- test_bisectable_codes_return_bisect ({code}) ---")
        body = [{"errorCode": code, "message": "x"}]
        result = _classify_error(body)
        print(f"  Input errorCode: {code} → classified as: {result}")
        assert result == "bisect"

    def test_numeric_overflow_returns_isolate(self):
        print("\n--- test_numeric_overflow_returns_isolate ---")
        body = [{"errorCode": "UNKNOWN_EXCEPTION", "message": "Numeric Overflow"}]
        result = _classify_error(body)
        print(f"  Input: UNKNOWN_EXCEPTION/'Numeric Overflow' → classified as: {result}")
        assert result == "isolate"

    def test_numeric_overflow_within_longer_message_returns_isolate(self):
        """Salesforce sometimes wraps the message with extra context; substring match."""
        print("\n--- test_numeric_overflow_within_longer_message_returns_isolate ---")
        body = [{"errorCode": "UNKNOWN_EXCEPTION",
                 "message": "An exception occurred: Numeric Overflow at row 5"}]
        result = _classify_error(body)
        assert result == "isolate"

    def test_unknown_exception_without_numeric_overflow_returns_none(self):
        """Don't broaden the skip path — only Numeric Overflow opts in."""
        print("\n--- test_unknown_exception_without_numeric_overflow_returns_none ---")
        body = [{"errorCode": "UNKNOWN_EXCEPTION", "message": "Something else broke"}]
        result = _classify_error(body)
        print(f"  Input: UNKNOWN_EXCEPTION/'Something else broke' → classified as: {result}")
        assert result is None

    @pytest.mark.parametrize("body", [
        None,
        [],
        "not a list",
        [{"errorCode": "INVALID_FIELD", "message": "No such column"}],
    ])
    def test_other_inputs_return_none(self, body):
        print(f"\n--- test_other_inputs_return_none ({body!r}) ---")
        assert _classify_error(body) is None


# --------------------------------------------------------------------------- #
# 2. _sync_isolated_rows direct                                                #
# --------------------------------------------------------------------------- #


class TestSyncIsolatedRows:
    """Unit tests for the per-Id isolation helper."""

    def test_skips_offending_row_yields_others(self, caplog):
        """Given 5 Ids where one returns Numeric Overflow on full-projection
        fetch, _sync_isolated_rows yields the other 4 and logs an ERROR for
        the skipped one."""
        print("\n--- test_skips_offending_row_yields_others ---")

        bad_id = "00TPV00001AZX842AH"
        good_ids = ["00TPV00001AAA000001", "00TPV00001BBB000002",
                    "00TPV00001CCC000003", "00TPV00001DDD000004"]
        all_ids = [good_ids[0], good_ids[1], bad_id, good_ids[2], good_ids[3]]

        # Track call sequence so we can assert behaviour after.
        calls = []

        def dispatcher(method, url, headers, params):
            q = params["q"]
            calls.append(q)
            # Order matters: per-Id branches first (full-projection queries that
            # happen to contain `Id = '…'`), then the literal "SELECT Id FROM"
            # enumeration. The fake _build_query_string emits "SELECT Id,SystemModstamp …"
            # for the full projection, while _sync_isolated_rows builds a literal
            # "SELECT Id FROM …" for its enumeration step.
            if f"Id = '{bad_id}'" in q:
                raise _http_error(500, [{
                    "errorCode": "UNKNOWN_EXCEPTION",
                    "message": "Numeric Overflow",
                }])
            for gid in good_ids:
                if f"Id = '{gid}'" in q:
                    return _ok_response([{"Id": gid, "SystemModstamp": "2025-09-15T16:44:36.000+0000"}])
            if q.startswith("SELECT Id FROM Contact"):
                return _ok_response([{"Id": _id} for _id in all_ids])
            raise AssertionError(f"Unexpected query: {q}")

        rest = Rest(_make_fake_sf(dispatcher))

        with caplog.at_level(logging.ERROR, logger=""):
            yielded = list(rest._sync_isolated_rows(
                _catalog_entry(stream="Contact"),
                "2025-09-15T16:44:31Z",
                "2025-09-15T16:44:36Z",
            ))

        print(f"  Rows yielded: {len(yielded)} (expected 4)")
        print(f"  Yielded Ids:  {[r['Id'] for r in yielded]}")
        assert len(yielded) == 4
        assert {r["Id"] for r in yielded} == set(good_ids)

        # ERROR log assertions
        skip_logs = [r for r in caplog.records
                     if "MDI_SFDC_NUMERIC_OVERFLOW_ROW_SKIPPED" in r.message]
        print(f"  Skip log entries: {len(skip_logs)}")
        assert len(skip_logs) == 1
        assert bad_id in skip_logs[0].message
        assert "stream=Contact" in skip_logs[0].message

        # We expect 1 Id-list query + 5 per-Id queries = 6 total
        print(f"  Total REST calls: {len(calls)} (expected 6 = 1 Id-list + 5 per-Id)")
        assert len(calls) == 6

    def test_empty_window_yields_nothing_and_does_not_error(self):
        """If the Id list is empty (nothing in the window), we just return."""
        print("\n--- test_empty_window_yields_nothing_and_does_not_error ---")

        def dispatcher(method, url, headers, params):
            if params["q"].startswith("SELECT Id FROM Contact"):
                return _ok_response([])  # empty
            raise AssertionError(f"Unexpected query: {params['q']}")

        rest = Rest(_make_fake_sf(dispatcher))
        yielded = list(rest._sync_isolated_rows(
            _catalog_entry(),
            "2025-09-15T16:44:31Z",
            "2025-09-15T16:44:36Z",
        ))
        assert yielded == []

    def test_non_overflow_http_error_propagates(self):
        """If a per-Id fetch fails for a different reason, don't swallow it."""
        print("\n--- test_non_overflow_http_error_propagates ---")

        def dispatcher(method, url, headers, params):
            q = params["q"]
            # Per-Id full-projection fetch (contains `Id = '…'`): non-overflow error
            if "Id = '00TX001'" in q:
                raise _http_error(401, [{
                    "errorCode": "INVALID_SESSION_ID",
                    "message": "Session expired or invalid",
                }])
            # Bare "SELECT Id FROM …" enumeration: return our one Id
            if q.startswith("SELECT Id FROM Contact"):
                return _ok_response([{"Id": "00TX001"}])
            raise AssertionError(f"Unexpected query: {q}")

        rest = Rest(_make_fake_sf(dispatcher))
        with pytest.raises(HTTPError):
            list(rest._sync_isolated_rows(
                _catalog_entry(),
                "2025-09-15T16:44:31Z",
                "2025-09-15T16:44:36Z",
            ))


# --------------------------------------------------------------------------- #
# 3. _query_recur end-to-end: bisect → isolate                                 #
# --------------------------------------------------------------------------- #


class TestQueryRecurIsolatePath:
    """Integration: full _query_recur flow exercising the Numeric Overflow path."""

    def test_numeric_overflow_at_full_window_falls_through_to_isolate(self, caplog):
        """A small-enough full window with Numeric Overflow goes:
           top-level call → bisect (still overflows on left half, succeeds on right)
           → left half bisects below MIN_BISECT_SECONDS → isolate mode kicks in
           → bad Id skipped, others yielded.

        We pick a 2-hour total window so a single bisect lands at 1 h
        (== MIN_BISECT_SECONDS — actually below the strict `<` guard) and
        switches into isolate-mode immediately on the bottom half.
        """
        print("\n--- test_numeric_overflow_at_full_window_falls_through_to_isolate ---")

        bad_id = "00TPV00001AZX842AH"
        good_id = "00TPV00001AAA000001"

        # 2-hour window: 2025-09-15T16:00 → 18:00. half_range = 1h, which is
        # NOT < MIN_BISECT_SECONDS (3600s) on the first bisect — so we need a
        # smaller window. Pick 1h59m so half = 59m30s = 3570s < 3600s.
        start_str = "2025-09-15T16:00:00.000Z"
        end_str = "2025-09-15T17:59:00.000Z"

        # Use an end_date in the past so _query_recur's "chunk to now" branch
        # is short-circuited (end_date < sync_start is True but the recursive
        # call uses end_date as new start, which is fine for this test as we
        # script the dispatcher to return empty for it).
        import datetime as _dt
        end_date = _dt.datetime(2025, 9, 15, 17, 59, 0, tzinfo=_dt.timezone.utc)

        def dispatcher(method, url, headers, params):
            q = params["q"]
            print(f"  dispatcher: {q[:140]}")
            # Branch order matters — see comment in TestSyncIsolatedRows.
            # 1. Per-Id full-projection fetches (isolate mode): match the bad
            #    Id first so it raises Numeric Overflow; good Ids return cleanly.
            if f"Id = '{bad_id}'" in q:
                raise _http_error(500, [{
                    "errorCode": "UNKNOWN_EXCEPTION",
                    "message": "Numeric Overflow",
                }])
            if f"Id = '{good_id}'" in q:
                return _ok_response([{"Id": good_id,
                                      "SystemModstamp": "2025-09-15T16:30:00.000+0000"}])
            # 2. The literal "SELECT Id FROM …" enumeration that _sync_isolated_rows
            #    builds (only Id in projection, both date bounds).
            if q.startswith("SELECT Id FROM Contact") and " AND SystemModstamp <" in q:
                return _ok_response([{"Id": good_id}, {"Id": bad_id}])
            # 3. Any full-projection windowed query (fake builder emits
            #    "SELECT Id,SystemModstamp FROM …"): raise Numeric Overflow to
            #    drive the bisection chain.
            if q.startswith("SELECT Id,SystemModstamp FROM Contact") and " AND SystemModstamp <" in q:
                raise _http_error(500, [{
                    "errorCode": "UNKNOWN_EXCEPTION",
                    "message": "Numeric Overflow",
                }])
            # 4. The post-chunk "from end_date → now" sub-recursion (no upper
            #    bound). Return empty so we don't drift into unrelated paths.
            return _ok_response([])

        rest = Rest(_make_fake_sf(dispatcher))

        # Build the initial query the same way the real query() entry-point
        # would, so the first REST call matches the bisect-trigger pattern in
        # rule #3 of the dispatcher.
        catalog = _catalog_entry(stream="Contact")
        initial_query = rest.sf._build_query_string(
            catalog, start_str, end_str_iso := "2025-09-15T17:59:00.000Z",
        )
        assert "AND SystemModstamp <" in initial_query, (
            f"Initial query must trigger dispatcher rule #3 for the test to be "
            f"meaningful; got: {initial_query}"
        )

        with caplog.at_level(logging.INFO, logger=""):
            yielded = list(rest._query_recur(
                query=initial_query,
                catalog_entry=catalog,
                start_date_str=start_str,
                end_date=end_date,
                retries=8,
            ))

        ids = [r["Id"] for r in yielded if "Id" in r]
        print(f"  Yielded Ids (deduped): {sorted(set(ids))}")
        assert good_id in ids, "Good record should be yielded via isolate mode"
        assert bad_id not in ids, "Bad record must be skipped"

        # Confirm isolate-mode log fired
        skip_logs = [r for r in caplog.records
                     if "MDI_SFDC_NUMERIC_OVERFLOW_ROW_SKIPPED" in r.message]
        assert len(skip_logs) >= 1
        assert bad_id in skip_logs[0].message

    def test_pure_operation_too_large_below_1h_still_raises(self):
        """Regression: pure OPERATION_TOO_LARGE that bisects below 1h must
        still raise the existing TapSalesforceExceptionError — we did not
        change that branch."""
        print("\n--- test_pure_operation_too_large_below_1h_still_raises ---")

        import datetime as _dt
        start_str = "2025-09-15T16:00:00.000Z"
        end_date = _dt.datetime(2025, 9, 15, 17, 59, 0, tzinfo=_dt.timezone.utc)

        def dispatcher(method, url, headers, params):
            # Every query fails with OPERATION_TOO_LARGE so bisection bottoms out.
            raise _http_error(400, [{
                "errorCode": "OPERATION_TOO_LARGE",
                "message": "Too many records",
            }])

        rest = Rest(_make_fake_sf(dispatcher))
        with pytest.raises(TapSalesforceExceptionError, match="less than 1 hour"):
            list(rest._query_recur(
                query="initial",
                catalog_entry=_catalog_entry(stream="Contact"),
                start_date_str=start_str,
                end_date=end_date,
                retries=8,
            ))


# --------------------------------------------------------------------------- #
# 4. Module-level constants sanity                                             #
# --------------------------------------------------------------------------- #


def test_min_bisect_seconds_is_one_hour():
    """If this changes, the cost/coverage tradeoff for isolate-mode shifts —
    surface it as a deliberate test failure rather than a silent edit."""
    assert MIN_BISECT_SECONDS == 3600

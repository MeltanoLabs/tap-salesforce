# pylint: disable=protected-access
import singer
import singer.utils as singer_utils
from singer import metadata as singer_metadata
from requests.exceptions import HTTPError

from tap_salesforce.salesforce.exceptions import TapSalesforceExceptionError

LOGGER = singer.get_logger()

MAX_RETRIES = 8
# Bisection bottom: any smaller range and we fall through to per-Id isolation
# (for 'isolate' errors) or raise (for 'bisect' errors).
MIN_BISECT_SECONDS = 3600
# Errors recoverable by date-range bisection alone.
_BISECT_ERROR_CODES = {"QUERY_TIMEOUT", "OPERATION_TOO_LARGE"}


def _classify_error(response):
    """Classify a Salesforce REST error body returned alongside an HTTPError.

    Returns one of:
      - "bisect"  : recoverable by halving the date range (QUERY_TIMEOUT,
                    OPERATION_TOO_LARGE).
      - "isolate" : cannot be fixed by bisection alone — a specific row's
                    formula field overflows during serialisation. Bisecting
                    narrows the offending window, then per-Id isolation skips
                    the bad row(s). Specifically catches
                    UNKNOWN_EXCEPTION:"Numeric Overflow".
      - None      : not recoverable here; caller should re-raise.
    """
    if not isinstance(response, list) or not response:
        return None
    err = response[0]
    code = err.get("errorCode")
    msg = (err.get("message") or "").strip()
    if code in _BISECT_ERROR_CODES:
        return "bisect"
    if code == "UNKNOWN_EXCEPTION" and "Numeric Overflow" in msg:
        return "isolate"
    return None


class Rest:
    def __init__(self, sf):
        self.sf = sf

    def query(self, catalog_entry, state):
        start_date = self.sf.get_start_date(state, catalog_entry)
        query = self.sf._build_query_string(catalog_entry, start_date)

        return self._query_recur(query, catalog_entry, start_date)

    # pylint: disable=too-many-arguments
    def _query_recur(self, query, catalog_entry, start_date_str, end_date=None,
                     retries=MAX_RETRIES, isolate_mode=False):
        params = {"q": query}
        # Use query endpoint for Task to exclude soft-deleted records (prevents OPERATION_TOO_LARGE)
        # Use queryAll for other objects to preserve soft-deleted records
        stream_name = catalog_entry["stream"]
        is_task = stream_name.lower() == "task"
        endpoint = "query" if is_task else "queryAll"
        url = f"{self.sf.instance_url}/services/data/v60.0/{endpoint}"
        headers = self.sf.auth.rest_headers

        # Resolve the replication key so we can track progress during pagination
        catalog_meta = singer_metadata.to_map(catalog_entry.get("metadata", []))
        replication_key = catalog_meta.get((), {}).get("replication-key")

        sync_start = singer_utils.now()
        if end_date is None:
            end_date = sync_start

        if retries == 0:
            raise TapSalesforceExceptionError(
                "Ran out of retries attempting to query Salesforce Object {}".format(catalog_entry["stream"])
            )

        # None | "bisect" | "isolate"
        error_class = None
        # Track the last replication-key value yielded so that if pagination fails
        # mid-stream we can resume from that point instead of re-querying from the
        # original start date (which would re-yield already-streamed records).
        last_seen_replication_value = None
        try:
            for record in self._sync_records(url, headers, params):
                if replication_key and record.get(replication_key):
                    last_seen_replication_value = record[replication_key]
                yield record

            # If the date range was chunked (an end_date was passed), sync
            # from the end_date -> now
            if end_date < sync_start:
                next_start_date_str = singer_utils.strftime(end_date)
                query = self.sf._build_query_string(catalog_entry, next_start_date_str)
                for record in self._query_recur(query, catalog_entry, next_start_date_str, retries=retries):
                    yield record

        except HTTPError as ex:
            response = ex.response.json()
            error_class = _classify_error(response)
            if error_class is None:
                raise ex
            start_date = singer_utils.strptime_with_tz(start_date_str)
            total_seconds = (end_date - start_date).total_seconds()
            end_date_str = singer_utils.strftime(end_date)
            if total_seconds >= 86400:
                range_label = f"{int(total_seconds // 86400)} days"
            else:
                range_label = f"{total_seconds / 3600:.1f} hours"
            LOGGER.info(
                "Salesforce returned %s querying %s of %s (range: %s to %s) — will %s",
                response[0].get("errorCode"),
                range_label,
                catalog_entry["stream"],
                start_date_str,
                end_date_str,
                ("bisect date range" if error_class == "bisect"
                 else "bisect then isolate per-Id if needed"),
            )

        if error_class is not None:
            # Carry isolate_mode forward through recursion once we've seen a
            # Numeric Overflow — even if a later sub-range surfaces a different
            # bisect-able error, we still want to fall through to per-Id mode
            # at the bottom rather than raising.
            next_isolate_mode = isolate_mode or (error_class == "isolate")

            if last_seen_replication_value is not None:
                # Partial pagination: some records were already streamed to the target
                # before the error. Re-querying from start_date_str would duplicate them.
                # Resume from the last seen replication-key value instead.
                LOGGER.info(
                    "Partial pagination detected for %s — %s records already streamed up to %s. "
                    "Resuming from that value to avoid duplicates.",
                    catalog_entry["stream"],
                    replication_key,
                    last_seen_replication_value,
                )
                resume_query = self.sf._build_query_string(
                    catalog_entry,
                    last_seen_replication_value,
                    singer_utils.strftime(end_date) if end_date < sync_start else None,
                )
                for record in self._query_recur(
                    resume_query, catalog_entry, last_seen_replication_value, end_date,
                    retries - 1, isolate_mode=next_isolate_mode,
                ):
                    yield record
            else:
                # No records were yielded yet — safe to bisect the full range.
                start_date = singer_utils.strptime_with_tz(start_date_str)
                half_range = (end_date - start_date) // 2

                if half_range.total_seconds() < MIN_BISECT_SECONDS:
                    # Bisect bottomed out. For 'bisect' errors that's an infinite
                    # loop — raise as before. For 'isolate' (Numeric Overflow)
                    # switch to per-Id mode: bad row(s) get skipped, the rest
                    # stream cleanly.
                    if next_isolate_mode:
                        for record in self._sync_isolated_rows(
                            catalog_entry,
                            start_date_str,
                            singer_utils.strftime(end_date),
                        ):
                            yield record
                        return
                    raise TapSalesforceExceptionError(
                        "Attempting to query by less than 1 hour range, this would cause infinite looping."
                    )

                end_date = end_date - half_range
                query = self.sf._build_query_string(
                    catalog_entry,
                    singer_utils.strftime(start_date),
                    singer_utils.strftime(end_date),
                )
                for record in self._query_recur(
                    query, catalog_entry, start_date_str, end_date,
                    retries - 1, isolate_mode=next_isolate_mode,
                ):
                    yield record

    def _sync_isolated_rows(self, catalog_entry, start_date_str, end_date_str):
        """Fallback for Numeric Overflow at sub-bisect-bottom windows.

        When `_query_recur`'s date-range bisection has narrowed to a window
        smaller than MIN_BISECT_SECONDS but Salesforce is still returning
        UNKNOWN_EXCEPTION:"Numeric Overflow" (i.e. a specific row's formula
        field overflows during serialisation), we can't shrink the window
        further. Instead we enumerate Ids in the window with a minimal
        projection, then re-fetch each Id alone with the full projection.
        Rows that still overflow get logged with their Id and skipped; the
        rest stream cleanly.

        Cost: O(rows-in-window) extra REST calls (one cheap Id list + one
        per row). With MIN_BISECT_SECONDS=3600 this is bounded.
        """
        stream_name = catalog_entry["stream"]
        is_task = stream_name.lower() == "task"
        endpoint = "query" if is_task else "queryAll"
        url = f"{self.sf.instance_url}/services/data/v60.0/{endpoint}"
        headers = self.sf.auth.rest_headers

        catalog_meta = singer_metadata.to_map(catalog_entry.get("metadata", []))
        replication_key = catalog_meta.get((), {}).get("replication-key") or "SystemModstamp"

        # Step 1: list Ids in the offending window with minimal projection.
        id_query = (
            f"SELECT Id FROM {stream_name} "
            f"WHERE {replication_key} >= {start_date_str} "
            f"AND {replication_key} < {end_date_str} "
            f"ORDER BY {replication_key} ASC"
        )
        LOGGER.info(
            "isolate-mode: enumerating Ids for %s in [%s, %s)",
            stream_name, start_date_str, end_date_str,
        )
        ids = [row["Id"] for row in self._sync_records(url, headers, {"q": id_query})]
        LOGGER.info(
            "isolate-mode: fetching %d %s rows individually",
            len(ids), stream_name,
        )

        # Step 2: re-fetch each row alone with the full projection. Skip ones
        # that still overflow, emit a structured ERROR log + counter metric so
        # the platform team can chase the offending formula values.
        skipped = 0
        for sf_id in ids:
            # Build the full-projection query then constrain to a single Id.
            # `order_by_clause=False` keeps the trailing `AND Id = '...'` syntactically valid.
            single_query = self.sf._build_query_string(
                catalog_entry, start_date_str, end_date_str, order_by_clause=False,
            ) + f" AND Id = '{sf_id}'"
            try:
                for record in self._sync_records(url, headers, {"q": single_query}):
                    yield record
            except HTTPError as ex:
                response = ex.response.json()
                if _classify_error(response) == "isolate":
                    skipped += 1
                    LOGGER.error(
                        "MDI_SFDC_NUMERIC_OVERFLOW_ROW_SKIPPED stream=%s id=%s "
                        "message=%r — row triggers Numeric Overflow during serialisation. "
                        "Identify the offending formula field with: "
                        "SELECT Id, <formula_field> FROM %s WHERE Id='%s'",
                        stream_name, sf_id, response[0].get("message"),
                        stream_name, sf_id,
                    )
                    # Emit a counter so the run summary + Datadog log-based metric pick it up.
                    singer.metrics.Counter(
                        metric="tap_salesforce_numeric_overflow_skipped",
                        tags={"stream": stream_name},
                    ).increment()
                    continue
                raise
        if skipped:
            LOGGER.warning(
                "isolate-mode summary: %s — %d/%d row(s) skipped due to Numeric Overflow",
                stream_name, skipped, len(ids),
            )

    def _sync_records(self, url, headers, params):
        while True:
            resp = self.sf._make_request("GET", url, headers=headers, params=params)
            resp_json = resp.json()

            yield from resp_json.get("records")

            next_records_url = resp_json.get("nextRecordsUrl")

            if next_records_url is None:
                break
            else:
                url = f"{self.sf.instance_url}{next_records_url}"

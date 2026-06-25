# pylint: disable=protected-access
import singer
import singer.utils as singer_utils
from singer import metadata as singer_metadata
from requests.exceptions import HTTPError

from tap_salesforce.salesforce.exceptions import TapSalesforceExceptionError

LOGGER = singer.get_logger()

MAX_RETRIES = 8


class Rest:
    def __init__(self, sf):
        self.sf = sf

    def query(self, catalog_entry, state):
        start_date = self.sf.get_start_date(state, catalog_entry)
        query = self.sf._build_query_string(catalog_entry, start_date)

        return self._query_recur(query, catalog_entry, start_date)

    # pylint: disable=too-many-arguments
    def _query_recur(self, query, catalog_entry, start_date_str, end_date=None, retries=MAX_RETRIES):
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

        retryable = False
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
            if isinstance(response, list) and response[0].get("errorCode") in ("QUERY_TIMEOUT", "OPERATION_TOO_LARGE"):
                start_date = singer_utils.strptime_with_tz(start_date_str)
                total_seconds = (end_date - start_date).total_seconds()
                end_date_str = singer_utils.strftime(end_date)
                if total_seconds >= 86400:
                    range_label = f"{int(total_seconds // 86400)} days"
                else:
                    range_label = f"{total_seconds / 3600:.1f} hours"
                LOGGER.info(
                    "Salesforce returned %s querying %s of %s (range: %s to %s) — bisecting date range",
                    response[0].get("errorCode"),
                    range_label,
                    catalog_entry["stream"],
                    start_date_str,
                    end_date_str,
                )
                retryable = True
            else:
                raise ex

        if retryable:
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
                    resume_query, catalog_entry, last_seen_replication_value, end_date, retries - 1
                ):
                    yield record
            else:
                # No records were yielded yet — safe to bisect the full range.
                start_date = singer_utils.strptime_with_tz(start_date_str)
                half_range = (end_date - start_date) // 2
                end_date = end_date - half_range

                if half_range.total_seconds() < 3600:
                    raise TapSalesforceExceptionError(
                        "Attempting to query by less than 1 hour range, this would cause infinite looping."
                    )

                query = self.sf._build_query_string(
                    catalog_entry,
                    singer_utils.strftime(start_date),
                    singer_utils.strftime(end_date),
                )
                for record in self._query_recur(query, catalog_entry, start_date_str, end_date, retries - 1):
                    yield record

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

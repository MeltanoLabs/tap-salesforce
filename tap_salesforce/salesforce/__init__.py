import json
import os
import re
from datetime import timedelta

import backoff
import requests
import singer
import singer.utils as singer_utils
from singer import metadata, metrics

from tap_salesforce.observability import (
    emit_describe_call_metric,
    log_api_call,
    log_describe_call,
    log_quota_status,
)
from tap_salesforce.salesforce.bulk import Bulk
from tap_salesforce.salesforce.bulk2 import Bulk2
from tap_salesforce.salesforce.credentials import SalesforceAuth
from tap_salesforce.salesforce.exceptions import (
    SFDCCustomNotAcceptableError,
    TapSalesforceExceptionError,
    TapSalesforceQuotaExceededError,
)
from tap_salesforce.salesforce.rest import Rest

LOGGER = singer.get_logger()

BULK_API_TYPE = "BULK"
BULK2_API_TYPE = "BULK2"
REST_API_TYPE = "REST"

STRING_TYPES = {
    "id",
    "string",
    "picklist",
    "textarea",
    "phone",
    "url",
    "reference",
    "multipicklist",
    "combobox",
    "encryptedstring",
    "email",
    "complexvalue",  # TODO: Unverified
    "masterrecord",
    "datacategorygroupreference",
    "base64",
}

NUMBER_TYPES = {"double", "currency", "percent"}

DATE_TYPES = {"datetime", "date"}

BINARY_TYPES = {"byte"}

LOOSE_TYPES = {
    "anyType",
    # A calculated field's type can be any of the supported
    # formula data types (see https://developer.salesforce.com/docs/#i1435527)
    "calculated",
}


# The following objects are not supported by the bulk API.
UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS = {
    "AssetTokenEvent",
    "AttachedContentNote",
    "EventWhoRelation",
    "QuoteTemplateRichTextData",
    "TaskWhoRelation",
    "SolutionStatus",
    "ContractStatus",
    "RecentlyViewed",
    "DeclinedEventRelation",
    "AcceptedEventRelation",
    "TaskStatus",
    "PartnerRole",
    "TaskPriority",
    "CaseStatus",
    "UndecidedEventRelation",
    "OrderStatus",
}

# The following objects have certain WHERE clause restrictions so we exclude them.
QUERY_RESTRICTED_SALESFORCE_OBJECTS = {
    "Announcement",
    "CollaborationGroupRecord",
    "Vote",
    "IdeaComment",
    "FieldDefinition",
    "PlatformAction",
    "UserEntityAccess",
    "RelationshipInfo",
    "ContentFolderMember",
    "ContentFolderItem",
    "SearchLayout",
    "SiteDetail",
    "EntityParticle",
    "OwnerChangeOptionInfo",
    "DataStatistics",
    "UserFieldAccess",
    "PicklistValueInfo",
    "RelationshipDomain",
    "FlexQueueItem",
    "NetworkUserHistoryRecent",
    "FieldHistoryArchive",
    "RecordActionHistory",
    "FlowVersionView",
    "FlowVariableView",
    "AppTabMember",
    "ColorDefinition",
    "IconDefinition",
}

# The following objects are not supported by the query method being used.
QUERY_INCOMPATIBLE_SALESFORCE_OBJECTS = {
    "DataType",
    "ListViewChartInstance",
    "FeedLike",
    "OutgoingEmail",
    "OutgoingEmailRelation",
    "FeedSignal",
    "ActivityHistory",
    "EmailStatus",
    "UserRecordAccess",
    "Name",
    "AggregateResult",
    "OpenActivity",
    "ProcessInstanceHistory",
    "OwnedContentDocument",
    "FolderedContentDocument",
    "FeedTrackedChange",
    "CombinedAttachment",
    "AttachedContentDocument",
    "ContentBody",
    "NoteAndAttachment",
    "LookedUpFromActivity",
    "AttachedContentNote",
    "QuoteTemplateRichTextData",
}


def log_backoff_attempt(details):
    LOGGER.info("ConnectionError detected, triggering backoff: %d try", details.get("tries"))


def raise_for_status(resp):
    """
    Adds additional handling of HTTP Errors.

    `CustomNotAcceptable` is returned during discovery with status code 406.
        This error does not seem to be documented on Salesforce, and possibly
        is not the best error that Salesforce could return. It also appears
        that this error is ephemeral and resolved after retries.
    """
    if resp.status_code != 200:
        err_msg = f"{resp.status_code} Client Error: {resp.reason} for url: {resp.url}"
        LOGGER.warning(err_msg)

    if resp.status_code == 406 and "CustomNotAcceptable" in resp.reason:
        raise SFDCCustomNotAcceptableError(err_msg)
    else:
        resp.raise_for_status()


def field_to_property_schema(field, mdata):  # noqa: C901
    property_schema = {}

    field_name = field["name"]
    sf_type = field["type"]

    if sf_type in STRING_TYPES:
        property_schema["type"] = "string"
    elif sf_type in DATE_TYPES:
        date_type = {"type": "string", "format": "date-time"}
        string_type = {"type": ["string", "null"]}
        property_schema["anyOf"] = [date_type, string_type]
    elif sf_type == "boolean":
        property_schema["type"] = "boolean"
    elif sf_type in NUMBER_TYPES:
        property_schema["type"] = "number"
    elif sf_type == "address":
        property_schema["type"] = "object"
        property_schema["properties"] = {
            "street": {"type": ["null", "string"]},
            "state": {"type": ["null", "string"]},
            "postalCode": {"type": ["null", "string"]},
            "city": {"type": ["null", "string"]},
            "country": {"type": ["null", "string"]},
            "longitude": {"type": ["null", "number"]},
            "latitude": {"type": ["null", "number"]},
            "geocodeAccuracy": {"type": ["null", "string"]},
        }
    elif sf_type in ("int", "long"):
        property_schema["type"] = "integer"
    elif sf_type == "time":
        property_schema["type"] = "string"
    elif sf_type in LOOSE_TYPES:
        return property_schema, mdata  # No type = all types
    elif sf_type in BINARY_TYPES:
        mdata = metadata.write(mdata, ("properties", field_name), "inclusion", "unsupported")
        mdata = metadata.write(mdata, ("properties", field_name), "unsupported-description", "binary data")
        return property_schema, mdata
    elif sf_type == "location":
        # geo coordinates are numbers or objects divided into two fields for lat/long
        property_schema["type"] = ["number", "object", "null"]
        property_schema["properties"] = {
            "longitude": {"type": ["null", "number"]},
            "latitude": {"type": ["null", "number"]},
        }
    elif sf_type == "json":
        property_schema["type"] = "string"
    else:
        raise TapSalesforceExceptionError(f"Found unsupported type: {sf_type}")

    # The nillable field cannot be trusted
    if field_name != "Id" and sf_type != "location" and sf_type not in DATE_TYPES:
        property_schema["type"] = ["null", property_schema["type"]]

    return property_schema, mdata


class Salesforce:
    WINDOWED_OBJECTS = {"Task", "Campaign", "CampaignMember"}

    # pylint: disable=too-many-instance-attributes,too-many-arguments
    def __init__(
        self,
        credentials=None,
        token=None,
        quota_percent_per_run=None,
        quota_percent_total=None,
        is_sandbox=None,
        select_fields_by_default=None,
        default_start_date=None,
        api_type=None,
        api_type_overrides=None,
        windowed_objects=None,
        limit_windowed_objects_month=None,
        pull_config_objects=None,
    ):
        self.api_type = api_type.upper() if api_type else None
        # Optional per-stream api_type overrides, e.g. {"Task": "BULK"} to route a
        # high-volume Activity object through the Bulk API (with PK chunking) while
        # the remaining streams stay on the global api_type.
        self.api_type_overrides = self._normalize_api_type_overrides(api_type_overrides)
        self.session = requests.Session()
        if isinstance(quota_percent_per_run, str) and quota_percent_per_run.strip() == "":
            quota_percent_per_run = None
        if isinstance(quota_percent_total, str) and quota_percent_total.strip() == "":
            quota_percent_total = None

        self.quota_percent_per_run = float(quota_percent_per_run) if quota_percent_per_run is not None else 25
        self.quota_percent_total = float(quota_percent_total) if quota_percent_total is not None else 80
        self.is_sandbox = is_sandbox is True or (isinstance(is_sandbox, str) and is_sandbox.lower() == "true")
        self.select_fields_by_default = select_fields_by_default is True or (
            isinstance(select_fields_by_default, str) and select_fields_by_default.lower() == "true"
        )
        self.rest_requests_attempted = 0
        self.jobs_completed = 0
        self.data_url = "{}/services/data/v60.0/{}"
        self.pk_chunking = False

        # Quota tracking for before/after extraction monitoring
        self._initial_quota_used = None
        self._initial_quota_allotted = None
        self._latest_quota_used = None
        self._latest_quota_allotted = None
        self.windowed_objects = set(windowed_objects) if windowed_objects else self.WINDOWED_OBJECTS
        self.limit_windowed_objects_month = limit_windowed_objects_month
        self.pull_config_objects = pull_config_objects

        self.auth = SalesforceAuth.from_credentials(credentials, is_sandbox=self.is_sandbox)

        # validate start_date
        self.default_start_date = (
            singer_utils.strptime_to_utc(default_start_date)
            if default_start_date
            else (singer_utils.now() - timedelta(weeks=4))
        ).isoformat()

        if default_start_date:
            LOGGER.info(
                "Parsed start date '%s' from value '%s'",
                self.default_start_date,
                default_start_date,
            )

    def _parse_objects_config(self, objects_config: str | list[dict], stream: str) -> list[str]:
        """Parse the OBJECTS configuration string into a list of fields for the given stream."""
        if not objects_config or not stream:
            return []

        try:
            objects_list = json.loads(objects_config) if isinstance(objects_config, str) else objects_config

            for obj in objects_list:
                if isinstance(obj, dict) and obj.get('name', '').lower() == stream.lower():
                    return obj.get('columns', [])
            return []
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            LOGGER.warning(f"Failed to parse OBJECTS configuration: {e}")
            return []

    # pylint: disable=anomalous-backslash-in-string,line-too-long
    def check_rest_quota_usage(self, headers):
        match = re.search(r"^api-usage=(\d+)/(\d+)$", headers.get("Sforce-Limit-Info"))

        if match is None:
            return

        used, allotted = map(int, match.groups())

        LOGGER.warning("Used %s of %s daily REST API quota", used, allotted)

        # Track initial quota snapshot (first API response)
        if self._initial_quota_used is None:
            self._initial_quota_used = used
            self._initial_quota_allotted = allotted
            log_quota_status(self, used, allotted, phase="pre_extract")

        # Always track the latest values
        self._latest_quota_used = used
        self._latest_quota_allotted = allotted

        # Log quota status periodically for monitoring
        if self.rest_requests_attempted > 0 and self.rest_requests_attempted % 1000 == 0:
            log_quota_status(self, used, allotted, phase="current")

        percent_used_from_total = (used / allotted) * 100
        max_requests_for_run = int((self.quota_percent_per_run * allotted) / 100)

        if percent_used_from_total > self.quota_percent_total:
            total_message = (
                "Salesforce has reported {}/{} ({:3.2f}%) total REST quota "
                + "used across all Salesforce Applications. Terminating "
                + "replication to not continue past configured percentage "
                + "of {}% total quota."
            ).format(used, allotted, percent_used_from_total, self.quota_percent_total)
            raise TapSalesforceQuotaExceededError(total_message)
        elif self.rest_requests_attempted > max_requests_for_run:
            partial_message = (
                "This replication job has made {} REST requests ({:3.2f}% of "
                + "total quota). Terminating replication due to allotted "
                + "quota of {}% per replication."
            ).format(
                self.rest_requests_attempted,
                (self.rest_requests_attempted / allotted) * 100,
                self.quota_percent_per_run,
            )
            raise TapSalesforceQuotaExceededError(partial_message)

    def login(self):
        self.auth.login()

    @property
    def instance_url(self):
        return self.auth.instance_url

    def _is_session_expired(self, resp) -> bool:
        """Return True if the 401 indicates a session expiry.

        Returns True when the response body contains INVALID_SESSION_ID, or
        when the body cannot be parsed (treated conservatively as expired).
        """
        try:
            body = resp.json()
            return any(
                err.get("errorCode") == "INVALID_SESSION_ID"
                for err in (body if isinstance(body, list) else [])
            )
        except Exception:
            return True  # treat unparseable 401 as expired session

    def _rebuild_headers_with_new_at(self, headers) -> dict:
        """Return a new headers dict with the current access token injected.

        Callers use either Authorization (REST) or X-SFDC-Session (Bulk).
        """
        new_at = self.auth._access_token
        if "Authorization" in headers:
            return {**headers, "Authorization": f"Bearer {new_at}"}
        if "X-SFDC-Session" in headers:
            return {**headers, "X-SFDC-Session": new_at}
        return headers

    # pylint: disable=too-many-arguments
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.ConnectionError, SFDCCustomNotAcceptableError),
        max_tries=10,
        factor=2,
        on_backoff=log_backoff_attempt,
    )
    def _make_request(self, http_method, url, headers=None, body=None, stream=False, params=None):
        # Capture the request start for duration + per-call observability.
        # Kept as close to the wire call as possible so the timer measures actual
        # network + SFDC latency, not any bookkeeping.
        request_start = singer_utils.now()
        LOGGER.info("Making %s request to %s with params: %s", http_method, url, params or body)
        if http_method == "GET":
            resp = self.session.get(url, headers=headers, stream=stream, params=params)
        elif http_method == "POST":
            resp = self.session.post(url, headers=headers, data=body)
        else:
            raise TapSalesforceExceptionError("Unsupported HTTP method")
        duration_ms = (singer_utils.now() - request_start).total_seconds() * 1000.0

        # 401 = expired AT. Refresh via bongo and retry once.
        if resp.status_code == 401:
            tenant = os.environ.get("TENANT", "unknown")
            if self._is_session_expired(resp) and hasattr(self.auth, "refresh_access_token"):
                LOGGER.warning(
                    "SF data query: 401 INVALID_SESSION_ID — AT expired, refreshing "
                    "event=sf_401_detected tenant=%s url=%s",
                    tenant, url,
                )
                try:
                    self.auth.refresh_access_token()
                    LOGGER.info(
                        "SF data query: AT refreshed, retrying request "
                        "event=sf_at_refresh_done tenant=%s url=%s",
                        tenant, url,
                    )
                    headers = self._rebuild_headers_with_new_at(headers)
                    if http_method == "GET":
                        resp = self.session.get(url, headers=headers, stream=stream, params=params)
                    else:
                        resp = self.session.post(url, headers=headers, data=body)
                    if resp.status_code == 401:
                        LOGGER.error(
                            "SF data query: retry also returned 401 — propagating error "
                            "event=sf_retry_401 tenant=%s url=%s",
                            tenant, url,
                        )
                except Exception as refresh_err:
                    LOGGER.error(
                        "SF data query: AT refresh failed — request will fail "
                        "event=sf_at_refresh_failed tenant=%s url=%s error=%s",
                        tenant, url, refresh_err,
                    )
                    raise
            else:
                LOGGER.warning(
                    "SF data query: 401 but not INVALID_SESSION_ID — not retrying "
                    "event=sf_401_not_session tenant=%s url=%s body=%s",
                    tenant, url, resp.text[:200],
                )

        raise_for_status(resp)

        limit_used: int | None = None
        limit_allotted: int | None = None
        limit_header = resp.headers.get("Sforce-Limit-Info")
        if limit_header is not None:
            self.rest_requests_attempted += 1
            match = re.search(r"^api-usage=(\d+)/(\d+)$", limit_header)
            if match:
                limit_used, limit_allotted = (int(match.group(1)), int(match.group(2)))
            self.check_rest_quota_usage(resp.headers)

        # Per-HTTP-response event so DD can count calls by url_path
        # and track the authoritative SFDC counter across the whole run, not just
        # the pre/post pair. Only fires when Sforce-Limit-Info is present to avoid
        # logging non-quota-bearing calls (auth, streaming chunks) separately.
        if limit_header is not None:
            try:
                response_bytes = (
                    int(resp.headers.get("Content-Length", 0))
                    if resp.headers.get("Content-Length")
                    else None
                )
            except (TypeError, ValueError):
                response_bytes = None
            log_api_call(
                self,
                method=http_method,
                url=url,
                status_code=resp.status_code,
                duration_ms=duration_ms,
                sforce_limit_used=limit_used,
                sforce_limit_allotted=limit_allotted,
                response_bytes=response_bytes,
            )

        return resp

    def describe(self, sobject=None):
        """Describes all objects or a specific object"""
        headers = self.auth.rest_headers
        instance_url = self.auth.instance_url
        body = None
        method = "GET"
        if sobject is None:
            endpoint = "sobjects"
            endpoint_tag = "sobjects"
            url = self.data_url.format(instance_url, endpoint)
        elif isinstance(sobject, list):
            batch_length = len(sobject)
            if batch_length > 25:
                raise TapSalesforceExceptionError(f"Composite limited to 25 sObjects per batch. ({batch_length}).")
            endpoint = "composite/batch"
            endpoint_tag = "CompositeBatch"
            url = self.data_url.format(instance_url, endpoint)
            method = "POST"
            headers["Content-Type"] = "application/json"
            composite_subrequests = []
            for obj in sobject:
                sub_endpoint = f"sobjects/{obj}/describe"
                sub_url = self.data_url.format("", sub_endpoint)
                subrequest = {"method": "GET", "url": sub_url}
                composite_subrequests.append(subrequest)
            body = json.dumps({"batchRequests": composite_subrequests})
        else:
            endpoint = f"sobjects/{sobject}/describe"
            endpoint_tag = sobject
            url = self.data_url.format(instance_url, endpoint)

        # Capture the SFDC-side cost of this describe call separately
        # from the HTTP call count. For /composite/batch the SFDC cost = number of
        # subrequests (up to 25), which is why rest_requests_attempted was under-
        # reporting by ~25× every discovery batch.
        subrequest_count = len(sobject) if isinstance(sobject, list) else 1
        describe_start = singer_utils.now()
        with metrics.http_request_timer("describe") as timer:
            timer.tags["endpoint"] = endpoint_tag
            resp = self._make_request(method, url, headers=headers, body=body)
        describe_duration_ms = (singer_utils.now() - describe_start).total_seconds() * 1000.0

        # Pull the limit state captured by _make_request for this same response.
        # _latest_quota_used is updated inside check_rest_quota_usage above.
        log_describe_call(
            self,
            endpoint_tag=endpoint_tag,
            subrequest_count=subrequest_count,
            duration_ms=describe_duration_ms,
            sforce_limit_used=self._latest_quota_used,
            sforce_limit_allotted=self._latest_quota_allotted,
        )
        # CPF-1874: also emit a UDP dogstatsd counter so the metric reaches DD
        # even when this call happens inside Meltano's discover subprocess (whose
        # stderr is captured by Meltano and never reaches CloudWatch). The log
        # above is preserved for richer fields when stderr IS forwarded (sync phase).
        emit_describe_call_metric(
            endpoint_tag=endpoint_tag,
            subrequest_count=subrequest_count,
        )

        if isinstance(sobject, list):
            return resp.json()["results"]
        else:
            return resp.json()

    # pylint: disable=no-self-use
    def _get_selected_properties(self, catalog_entry):
        mdata = metadata.to_map(catalog_entry["metadata"])
        properties = catalog_entry["schema"].get("properties", {})
        stream = catalog_entry["stream"]
        meltano_selected_fields = [
            k
            for k in properties
            if singer.should_sync_field(
                metadata.get(mdata, ("properties", k), "inclusion"),
                metadata.get(mdata, ("properties", k), "selected"),
                self.select_fields_by_default,
            )
        ]

        pull_config_fields = self._parse_objects_config(self.pull_config_objects, stream)

        # Limit to 500 fields total to prevent header size issues
        max_fields = 500
        if len(pull_config_fields) > max_fields:
            LOGGER.warning(
                f"""Pull config contains more than {max_fields} fields for {stream}.
                Only the first {max_fields} fields will be used."""
            )

        if len(meltano_selected_fields) > max_fields:
            # Limit fields to prevent "Request Header Fields Too Large" error
            # Prioritize essential fields first
            essential_fields = ["Id", "SystemModstamp", "CreatedDate", "LastModifiedDate"]
            priority_fields = [f for f in essential_fields if f in meltano_selected_fields]
            priority_fields.extend([f for f in pull_config_fields if f in meltano_selected_fields])
            priority_fields = list(set(priority_fields))
            mk_fields = [f for f in meltano_selected_fields if "mk_" in f and f not in priority_fields]
            other_fields = [f for f in meltano_selected_fields if f not in priority_fields + mk_fields]

            ingested_fields = priority_fields[:max_fields]
            ingested_fields += mk_fields[:max_fields-len(ingested_fields)]
            ingested_fields += other_fields[:max_fields-len(ingested_fields)]


            LOGGER.warning(
                f"Limiting {stream} fields from {len(meltano_selected_fields)} to {max_fields} "
                "to prevent header size issues"
            )

            LOGGER.info(f"Selected {len(ingested_fields)} fields for {stream}: {ingested_fields}")
            return ingested_fields
        return meltano_selected_fields

    def get_start_date(self, state, catalog_entry):
        """Get the start date for a stream, applying task month limit if configured."""
        catalog_metadata = metadata.to_map(catalog_entry["metadata"])
        replication_key = catalog_metadata.get((), {}).get("replication-key")

        # Get the bookmark date or default start date
        start_date = (
            singer.get_bookmark(state, catalog_entry["tap_stream_id"], replication_key) or self.default_start_date
        )

        # Apply windowed objects month limit if this stream is in windowed_objects and limit is configured
        if (
            catalog_entry["tap_stream_id"] in self.windowed_objects
            and self.limit_windowed_objects_month is not None
            and self.limit_windowed_objects_month > 0
        ):
            now = singer_utils.now()
            month_limit_date = now - timedelta(days=31 * self.limit_windowed_objects_month)
            month_limit_date_str = month_limit_date.isoformat()

            if start_date < month_limit_date_str:
                LOGGER.info(
                    "%s stream limited to %d months. Using start date %s instead of %s",
                    catalog_entry["tap_stream_id"],
                    self.limit_windowed_objects_month,
                    month_limit_date_str,
                    start_date,
                )
                return month_limit_date_str

        return start_date

    def _build_query_string(self, catalog_entry, start_date, end_date=None, order_by_clause=True):
        selected_properties = self._get_selected_properties(catalog_entry)

        query = "SELECT {} FROM {}".format(",".join(selected_properties), catalog_entry["stream"])

        catalog_metadata = metadata.to_map(catalog_entry["metadata"])
        replication_key = catalog_metadata.get((), {}).get("replication-key")

        if replication_key:
            where_clause = f" WHERE {replication_key} >= {start_date} "
            end_date_clause = f" AND {replication_key} < {end_date}" if end_date else ""

            order_by = f" ORDER BY {replication_key} ASC"
            if order_by_clause:
                return query + where_clause + end_date_clause + order_by

            return query + where_clause + end_date_clause
        else:
            return query

    @staticmethod
    def _normalize_api_type_overrides(api_type_overrides):
        """Validate and normalize the per-stream api_type override map.

        Keys are lowercased for case-insensitive stream matching (mirrors the Task
        special-casing in rest.py/bulk.py); values are uppercased and validated
        against the known api_types so a typo fails loudly at init rather than
        silently falling back to the global type.
        """
        normalized_overrides = {}
        for stream, value in (api_type_overrides or {}).items():
            normalized = value.upper() if isinstance(value, str) else value
            if normalized not in (REST_API_TYPE, BULK_API_TYPE, BULK2_API_TYPE):
                raise TapSalesforceExceptionError(
                    f"api_type_overrides[{stream!r}] must be one of "
                    f"{[REST_API_TYPE, BULK_API_TYPE, BULK2_API_TYPE]}, got {value!r}"
                )
            normalized_overrides[stream.lower()] = normalized
        return normalized_overrides

    def effective_api_type(self, stream):
        """Resolve the api_type for a stream, honoring per-stream overrides."""
        return self.api_type_overrides.get(stream.lower(), self.api_type)

    def query(self, catalog_entry, state):
        api_type = self.effective_api_type(catalog_entry["stream"])
        if api_type == BULK_API_TYPE:
            bulk = Bulk(self)
            return bulk.query(catalog_entry, state)
        elif api_type == BULK2_API_TYPE:
            bulk = Bulk2(self)
            return bulk.query(catalog_entry, state)
        elif api_type == REST_API_TYPE:
            rest = Rest(self)
            return rest.query(catalog_entry, state)
        else:
            raise TapSalesforceExceptionError(f"api_type should be REST or BULK was: {api_type}")

    def get_blacklisted_objects(self):
        # Keyed off the global api_type only. Per-stream overrides are supported in
        # the REST->BULK direction (the REST object blacklist is a subset of BULK's,
        # so nothing an override targets gets wrongly excluded from discovery). The
        # reverse (global BULK, override a BULK-unsupported object to REST) is not
        # supported: the object would be filtered out here before the override runs.
        if self.api_type in [BULK_API_TYPE, BULK2_API_TYPE]:
            return UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS.union(QUERY_RESTRICTED_SALESFORCE_OBJECTS).union(
                QUERY_INCOMPATIBLE_SALESFORCE_OBJECTS
            )
        elif self.api_type == REST_API_TYPE:
            return QUERY_RESTRICTED_SALESFORCE_OBJECTS.union(QUERY_INCOMPATIBLE_SALESFORCE_OBJECTS)
        else:
            raise TapSalesforceExceptionError(f"api_type should be REST or BULK was: {self.api_type}")

    # pylint: disable=line-too-long
    def get_blacklisted_fields(self, api_type=None):
        # Accepts an explicit api_type so discovery can pass the per-stream effective
        # type (see effective_api_type); defaults to the global type otherwise.
        api_type = api_type or self.api_type
        if api_type == BULK_API_TYPE or api_type == BULK2_API_TYPE:
            return {
                (
                    "EntityDefinition",
                    "RecordTypesSupported",
                ): "this field is unsupported by the Bulk API."
            }
        elif api_type == REST_API_TYPE:
            return {}
        else:
            raise TapSalesforceExceptionError(f"api_type should be REST or BULK was: {api_type}")

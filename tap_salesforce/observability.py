"""Observability module for structured logging and metrics.

This module provides functions to emit structured log events for Datadog
integration. All logs are emitted in a format compatible with Datadog's
log parsing and faceting capabilities.

Metric events include a 'dd' namespace with metric_name, metric_value,
and metric_type fields for Datadog Log-Based Metric extraction.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import singer

if TYPE_CHECKING:
    from tap_salesforce.salesforce import Salesforce

LOGGER = singer.get_logger()


def get_tenant_id() -> str | None:
    """Get tenant ID from environment variable."""
    return os.environ.get("TENANT")


def _dd_metric(name: str, value: float, metric_type: str = "gauge") -> dict:
    """Build Datadog Log-Based Metric fields.

    Args:
        name: Metric name (e.g. 'mdi.salesforce.api.pre_extract')
        value: Numeric metric value
        metric_type: One of 'gauge', 'count'

    Returns:
        Dict with 'dd' namespace for Datadog extraction.
    """
    return {"dd": {"metric_name": name, "metric_value": value, "metric_type": metric_type}}


def log_sync_start(
    sf: "Salesforce",
    catalog: dict,
    config: dict,
) -> None:
    """Log structured event at the start of a sync operation.

    Args:
        sf: Salesforce client instance
        catalog: The catalog containing streams to sync
        config: The configuration dictionary
    """
    streams = catalog.get("streams", [])
    selected_streams = [s["stream"] for s in streams]

    log_data = {
        "event_type": "salesforce_sync_start",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": get_tenant_id(),
        "api_type": sf.api_type,
        "streams_count": len(selected_streams),
        "streams": selected_streams[:20],  # Limit to first 20 to avoid huge logs
        "quota_percent_total_limit": sf.quota_percent_total,
        "quota_percent_per_run_limit": sf.quota_percent_per_run,
        "max_workers": config.get("max_workers", 8),
        "is_sandbox": sf.is_sandbox,
        "instance_url": sf.instance_url if hasattr(sf, "instance_url") else None,
    }

    # Log as JSON for Datadog parsing
    LOGGER.info("salesforce_sync_start: %s", json.dumps(log_data))


def log_sync_complete(
    sf: "Salesforce",
    config: dict,
    success: bool = True,
    error: Exception | None = None,
    records_synced: int | None = None,
) -> None:
    """Log structured event at the end of a sync operation.

    Args:
        sf: Salesforce client instance
        config: The configuration dictionary
        success: Whether the sync completed successfully
        error: Optional exception if sync failed
        records_synced: Optional count of records synced
    """
    log_data = {
        "event_type": "salesforce_sync_complete",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": get_tenant_id(),
        "success": success,
        "api_type": sf.api_type,
        "rest_requests_attempted": sf.rest_requests_attempted,
        "bulk_jobs_completed": sf.jobs_completed,
        "quota_percent_total_limit": sf.quota_percent_total,
        "quota_percent_per_run_limit": sf.quota_percent_per_run,
        **_dd_metric("mdi.salesforce.api.requests_by_job", sf.rest_requests_attempted, "count"),
    }

    if error:
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)[:500]  # Limit error message length

    if records_synced is not None:
        log_data["records_synced"] = records_synced

    # Log as JSON for Datadog parsing
    LOGGER.info("salesforce_sync_complete: %s", json.dumps(log_data))


def log_quota_status(
    sf: "Salesforce",
    used: int,
    allotted: int,
    phase: str = "current",
) -> None:
    """Log current quota status for monitoring.

    Args:
        sf: Salesforce client instance
        used: Number of API calls used
        allotted: Total API calls allotted
        phase: One of 'pre_extract', 'post_extract', 'current'
    """
    percent_used = (used / allotted * 100) if allotted > 0 else 0

    log_data = {
        "event_type": "salesforce_quota_status",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": get_tenant_id(),
        "api_type": sf.api_type,
        "phase": phase,
        "quota_used": used,
        "quota_allotted": allotted,
        "quota_remaining": allotted - used,
        "quota_percent_used": round(percent_used, 2),
        "quota_percent_total_limit": sf.quota_percent_total,
        "is_near_limit": percent_used >= sf.quota_percent_total,
        **_dd_metric(f"mdi.salesforce.api.{phase}", round(percent_used, 2)),
    }

    LOGGER.info("salesforce_quota_status: %s", json.dumps(log_data))


def log_quota_consumed(
    sf: "Salesforce",
    pre_used: int,
    post_used: int,
    allotted: int,
) -> None:
    """Log the number of API calls consumed by this extraction job.

    Args:
        sf: Salesforce client instance
        pre_used: API calls used before extraction
        post_used: API calls used after extraction
        allotted: Total API calls allotted
    """
    calls_consumed = post_used - pre_used
    percent_consumed = (calls_consumed / allotted * 100) if allotted > 0 else 0

    log_data = {
        "event_type": "salesforce_quota_consumed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": get_tenant_id(),
        "api_type": sf.api_type,
        "calls_consumed": calls_consumed,
        "percent_consumed": round(percent_consumed, 2),
        "pre_used": pre_used,
        "post_used": post_used,
        "allotted": allotted,
        **_dd_metric("mdi.salesforce.api.calls_consumed", calls_consumed),
    }

    LOGGER.info("salesforce_quota_consumed: %s", json.dumps(log_data))


def log_stream_sync_start(
    stream_name: str,
    replication_method: str | None = None,
) -> None:
    """Log when a specific stream sync starts.

    Args:
        stream_name: Name of the stream being synced
        replication_method: INCREMENTAL or FULL_TABLE
    """
    log_data = {
        "event_type": "salesforce_stream_start",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": get_tenant_id(),
        "stream_name": stream_name,
        "replication_method": replication_method,
    }

    LOGGER.info("salesforce_stream_start: %s", json.dumps(log_data))


def log_stream_sync_complete(
    stream_name: str,
    records_count: int | None = None,
    success: bool = True,
) -> None:
    """Log when a specific stream sync completes.

    Args:
        stream_name: Name of the stream that was synced
        records_count: Number of records synced
        success: Whether the sync was successful
    """
    log_data = {
        "event_type": "salesforce_stream_complete",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": get_tenant_id(),
        "stream_name": stream_name,
        "records_count": records_count,
        "success": success,
        **_dd_metric("mdi.salesforce.stream.records", records_count or 0, "count"),
    }

    LOGGER.info("salesforce_stream_complete: %s", json.dumps(log_data))


# The existing `salesforce_quota_consumed` event reports `post_used - pre_used`
# where pre_used is the Sforce-Limit-Info value on the FIRST response (already
# past one call), and increments are tracked per HTTP response — NOT per SFDC
# API call. For the /composite/batch endpoint, one HTTP response corresponds to
# up to 25 SFDC API calls. Result: our Datadog attribution under-reports MK's
# true SFDC quota consumption by 100–500× vs. SFDC's own connected-app report.
#
# These helpers add two low-level events, intentionally one-per-HTTP-response
# and one-per-describe-wrapper, so DD can reconstruct authoritative counts
# without guessing:
#
#   salesforce_api_call       — 1 event per _make_request response
#                               carries endpoint, method, status, duration,
#                               and the SFDC quota header values.
#   salesforce_describe_call  — 1 event per describe() wrapper call
#                               carries composite_subrequest_count so the
#                               SFDC-side cost (sub-requests, up to 25× the
#                               HTTP count) is explicit.

_URL_PATH_CACHE_MAX = 1024


def _url_path(url: str) -> str:
    """Extract path from a full SFDC URL for low-cardinality log tagging.

    Drops query strings and the tenant-specific instance host so Datadog facets
    don't explode. Returns the URL unchanged if it can't be parsed.
    """
    if not url:
        return ""
    try:
        # Cheap split — avoids urllib overhead in the request hot path.
        after_scheme = url.split("://", 1)[-1]
        after_host = after_scheme.split("/", 1)[-1] if "/" in after_scheme else ""
        path = "/" + after_host.split("?", 1)[0]
        return path[:_URL_PATH_CACHE_MAX]
    except Exception:
        return url[:_URL_PATH_CACHE_MAX]


def log_api_call(
    sf: "Salesforce",
    *,
    method: str,
    url: str,
    status_code: int | None,
    duration_ms: float | None,
    sforce_limit_used: int | None,
    sforce_limit_allotted: int | None,
    response_bytes: int | None = None,
) -> None:
    """Emit one structured event per HTTP response through _make_request.

    Intentionally minimal — the hot path runs for every SFDC call. Endpoint
    classification is left to callers that know the semantics (see
    `log_describe_call` for the composite/batch case).
    """
    log_data = {
        "event_type": "salesforce_api_call",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": get_tenant_id(),
        "api_type": sf.api_type,
        "http_method": method,
        "url_path": _url_path(url),
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
        "sforce_limit_used": sforce_limit_used,
        "sforce_limit_allotted": sforce_limit_allotted,
        "sforce_percent_used": (
            round(sforce_limit_used / sforce_limit_allotted * 100, 2)
            if sforce_limit_used is not None and sforce_limit_allotted
            else None
        ),
        "response_bytes": response_bytes,
        **_dd_metric("mdi.salesforce.api.http_call", 1, "count"),
    }
    LOGGER.info("salesforce_api_call: %s", json.dumps(log_data))


def log_describe_call(
    sf: "Salesforce",
    *,
    endpoint_tag: str,
    subrequest_count: int,
    duration_ms: float | None,
    sforce_limit_used: int | None,
    sforce_limit_allotted: int | None,
) -> None:
    """Emit one event per describe() call — critical for closing the composite
    batch 25× undercount.

    `subrequest_count` is the authoritative SFDC API cost of this call:
      - 1  for a global describe (sobjects endpoint) or a single-object describe
      - N  for a /composite/batch with N sub-requests (N ≤ 25)
    """
    log_data = {
        "event_type": "salesforce_describe_call",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": get_tenant_id(),
        "api_type": sf.api_type,
        "endpoint_tag": endpoint_tag,
        "subrequest_count": subrequest_count,
        "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
        "sforce_limit_used": sforce_limit_used,
        "sforce_limit_allotted": sforce_limit_allotted,
        **_dd_metric("mdi.salesforce.api.describe_cost", subrequest_count, "count"),
    }
    LOGGER.info("salesforce_describe_call: %s", json.dumps(log_data))


# ---------------------------------------------------------------------------
# CPF-1874 — Dogstatsd UDP emission for the discover phase
# ---------------------------------------------------------------------------
#
# Discover runs as a Meltano subprocess whose stderr is captured by Meltano,
# not forwarded to the container's stderr → CloudWatch → Datadog Logs pipeline.
# Result: every `LOGGER.info(...)` from `do_discover` and from `describe()`
# during the discover phase is invisible in DD Logs and the dashboard widgets
# built on log-based metrics. This was the entire describe-storm blind spot.
#
# Fix: emit metrics over UDP directly to the DD agent (sidecar in the same
# Fargate task at localhost:8125 by default). UDP packets bypass Meltano's
# pipe capture entirely and reach DD via the agent's standard dogstatsd path.
#
# These helpers are best-effort: we never raise from telemetry. If the socket
# call fails (agent not running locally, port closed, etc.) the tap continues
# normally and we lose the data point — exactly the right trade-off.

import socket as _socket  # noqa: E402
from contextlib import contextmanager  # noqa: E402

# Tracks which tap phase is active so describe-cost metrics can be tagged
# `phase:discover` vs `phase:sync`. Discover and sync may both call
# `Salesforce.describe()`; without this tag the dashboard collapses both into
# one bar and the two distinct waves per Airflow run are indistinguishable.
_current_phase: str = "sync"


def set_phase(phase: str) -> None:
    """Set the active tap phase. Read by `emit_describe_call_metric`."""
    global _current_phase
    _current_phase = phase


def get_phase() -> str:
    return _current_phase


@contextmanager
def phase_context(phase: str):
    previous = _current_phase
    set_phase(phase)
    try:
        yield
    finally:
        set_phase(previous)


def _dogstatsd_endpoint() -> tuple[str, int]:
    """Datadog agent dogstatsd endpoint per Fargate sidecar convention."""
    host = os.environ.get("DD_AGENT_HOST", "localhost")
    try:
        port = int(os.environ.get("DD_DOGSTATSD_PORT", "8125"))
    except (TypeError, ValueError):
        port = 8125
    return host, port


def _dogstatsd_send(line: bytes) -> None:
    """Best-effort UDP send. Swallows every exception — telemetry must not break the tap."""
    try:
        host, port = _dogstatsd_endpoint()
        sock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        try:
            sock.settimeout(0.05)  # 50ms — agent is local; if slower, give up
            sock.sendto(line, (host, port))
        finally:
            sock.close()
    except Exception:  # noqa: BLE001
        pass


def _format_tags(tags: dict[str, str | int | None]) -> str:
    parts = [f"{k}:{v}" for k, v in tags.items() if v is not None and v != ""]
    return ("|#" + ",".join(parts)) if parts else ""


def dogstatsd_count(name: str, value: int | float, tags: dict | None = None) -> None:
    """Emit a counter metric directly to the DD agent over UDP."""
    line = f"{name}:{value}|c{_format_tags(tags or {})}".encode("utf-8")
    _dogstatsd_send(line)


def dogstatsd_gauge(name: str, value: int | float, tags: dict | None = None) -> None:
    """Emit a gauge metric directly to the DD agent over UDP."""
    line = f"{name}:{value}|g{_format_tags(tags or {})}".encode("utf-8")
    _dogstatsd_send(line)


def emit_describe_call_metric(
    *,
    endpoint_tag: str,
    subrequest_count: int,
) -> None:
    """Per-describe-call counter. Fires from inside `Salesforce.describe()`.

    Survives Meltano's discover-subprocess stderr capture because UDP to the
    DD agent is independent of any stdio pipeline.

    Sum `mdi.salesforce.api.describe_calls.cost` for authoritative SFDC
    describe-cost attribution per tenant — matches what SFDC's connected-app
    "API Usage Last 7 Days" report counts.
    """
    tenant_id = get_tenant_id()
    tags = {
        "tenant_id": tenant_id,
        "endpoint_tag": endpoint_tag,
        "phase": get_phase(),
    }
    # Number of describe HTTP responses (1 per wrapper call)
    dogstatsd_count("mdi.salesforce.api.describe_calls.responses", 1, tags)
    # SFDC-billed cost (1 for single, up to 25 for /composite/batch)
    dogstatsd_count("mdi.salesforce.api.describe_calls.cost", subrequest_count, tags)


def emit_discovery_summary_metric(
    *,
    describe_calls_issued: int,
    streams_discovered: int,
) -> None:
    """Per-do_discover() summary metrics. Fires once per discover invocation.

    `describe_calls_issued` counts HTTP responses (composite batches + global).
    Multiply by ~25 for typical full-org discover to estimate SFDC-side cost,
    OR sum `mdi.salesforce.api.describe_calls.cost` from `emit_describe_call_metric`
    for the exact figure.
    """
    tenant_id = get_tenant_id()
    tags = {"tenant_id": tenant_id}
    dogstatsd_count("mdi.salesforce.api.discovery_runs", 1, tags)
    dogstatsd_count("mdi.salesforce.api.discovery_describes", describe_calls_issued, tags)
    dogstatsd_gauge("mdi.salesforce.api.streams_discovered", streams_discovered, tags)

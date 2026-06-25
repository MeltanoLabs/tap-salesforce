import datetime
import logging
import threading

import singer

LOGGER = logging.getLogger(__name__)

_stdout_lock = threading.Lock()

DEFAULT_MAX_FUTURE_SECONDS = 3600  # 1 hour, configurable


def write_record(stream, record, version=None, time_extracted=None):
    msg = singer.RecordMessage(stream=stream, record=record,
                                version=version, time_extracted=time_extracted)
    with _stdout_lock:          # ← only this section is serialised
        singer.write_message(msg)

def write_schema(stream_name, schema, key_properties,
                 replication_key=None, stream_alias=None):
    with _stdout_lock:
        singer.write_schema(stream_name, schema, key_properties,
                            bookmark_properties=replication_key,
                            stream_alias=stream_alias)

def write_state(state):
    with _stdout_lock:
        singer.write_state(state)

def write_message(msg):
    with _stdout_lock:
        singer.write_message(msg)

def safe_bookmark_value(stream_name, replication_key, raw_value,
                        max_future_seconds=DEFAULT_MAX_FUTURE_SECONDS):
    if raw_value is None:
        return raw_value
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        bm_dt = datetime.datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        LOGGER.warning("BOOKMARK_GUARD: Cannot parse '%s' for %s.%s. Passing through.",
                       raw_value, stream_name, replication_key)
        return raw_value
    drift_seconds = (bm_dt - now).total_seconds()
    if drift_seconds > max_future_seconds:
        safe_value = now.isoformat()
        LOGGER.critical(
            "BOOKMARK_GUARD: %s.%s tried to advance to %s (%.0fs in future). "
            "Capping at now() = %s.", stream_name, replication_key,
            raw_value, drift_seconds, safe_value)
        return safe_value
    return raw_value

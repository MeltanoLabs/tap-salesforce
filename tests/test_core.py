"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_tap_test_class

from tap_salesforce.tap import TapSalesforce

SAMPLE_CONFIG = {
    "start_date": "2023-01-01T00:00:00Z",
    "domain": os.environ.get("TAP_SALESFORCE_DOMAIN"),
    "auth": {
        "flow": "password",
        "username": os.environ.get("TAP_SALESFORCE_AUTH_USERNAME"),
        "password": os.environ.get("TAP_SALESFORCE_AUTH_PASSWORD"),
    }
}

# Run standard built-in tap tests from the SDK:
TestTapSalesforce = get_tap_test_class(
    tap_class=TapSalesforce,
    config=SAMPLE_CONFIG,
)

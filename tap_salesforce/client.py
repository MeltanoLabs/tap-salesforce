"""REST client handling, including SalesforceStream base class."""

from __future__ import annotations

from typing import Any, Callable

import requests

from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.streams import RESTStream

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]

class SalesforceStream(RESTStream):
    """salesforce stream class."""
    version = "v58.0"
    records_jsonpath = "$[*]"  # Or override `parse_response`.

    # Set this value or override `get_new_paginator`.
    next_page_token_jsonpath = "$.next_page"  # noqa: S105

    @property
    def url_base(self):
        domain = self.config["domain"]
        return f"https://{domain}.salesforce.com/services/data/{self.version}"

    @property
    def authenticator(self) -> _Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """

        auth_type = self.config["auth"]["flow"]

        if auth_type == "oauth":
            access_token = self.config["auth"]["access_token"]
        else:
            grant_type = "password"
            client_id = self.config["client_id"]
            client_secret = self.config["client_secret"]
            username = self.config["auth"]["username"]
            password = self.config["auth"]["password"]
            url = "https://login.salesforce.com/services/oauth2/token"
            login_response = requests.post(
                url,
                params={
                    "grant_type": grant_type,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "username": username,
                    "password": password,
                },
            )
            access_token = login_response.json().get("access_token")
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=access_token,
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

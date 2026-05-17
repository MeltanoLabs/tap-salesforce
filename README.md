# tap-salesforce

[![CircleCI Build Status](https://circleci.com/gh/singer-io/tap-salesforce.png)](https://circleci.com/gh/singer-io/tap-salesforce.png)


[Singer](https://www.singer.io/) tap that extracts data from a [Salesforce](https://www.salesforce.com/) Account and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This is a forked version of [tap-salesforce (v1.4.24)](https://github.com/singer-io/tap-salesforce) that maintained by the Meltano team.

Main differences from the original version:

- Support for `username/password/security_token` authentication
- Support for OAuth 2.0 JWT Bearer authentication (keypair-based, durable, recommended for unattended use)
- Support for concurrent execution (8 threads by default) when accessing different API endpoints to speed up the extraction process
- Support for much faster discovery

# Quickstart

## Install the tap

This version of `tap-salesforce` is not available on PyPi, so you have to fetch it directly from the Meltano maintained project:

```bash
python3 -m venv venv
source venv/bin/activate
pip install git+https://github.com/MeltanoLabs/tap-salesforce.git
```

## Create a Config file

**Required**
```
{
  "api_type": "BULK2",
  "select_fields_by_default": true,
}
```

**Required for OAuth based authentication**
```
{
  "client_id": "secret_client_id",
  "client_secret": "secret_client_secret",
  "refresh_token": "abc123",
}
```

**Required for username/password based authentication**
```
{
  "username": "Account Email",
  "password": "Account Password",
  "security_token": "Security Token",
}
```

**Required for OAuth 2.0 JWT Bearer based authentication**
```
{
  "jwt_client_id": "Consumer Key of your Connected/External Client App",
  "jwt_username": "Salesforce username to impersonate",
  "jwt_private_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
}
```

`jwt_client_id` is the Consumer Key of a Connected App (or External Client App) configured for JWT bearer flow. `jwt_username` is the Salesforce user whose identity the tap will assume (the JWT `sub` claim) — that user must be pre-authorized for the app. `jwt_private_key` is the RSA private key (PEM) corresponding to the X.509 cert uploaded to the app. The user must have completed an OAuth grant for the app at least once (e.g. via the authorize endpoint) before JWT bearer logins will succeed. See [Salesforce's JWT bearer flow docs](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_jwt_flow.htm) for the full setup.

When multiple credential types are present in the config, the tap chooses in this order: JWT → OAuth refresh-token → username/password.

> **JWT bearer is incompatible with `api_type: BULK`.** Bulk API 1.0 (`/services/async/...`) authenticates via an `X-SFDC-Session` header that requires a SOAP-style session id. The OAuth2 JWT Bearer flow never issues one, so JWT logins succeed but every stream then fails with `InvalidSessionId` at job-create time. Use **`api_type: BULK2`** (Bulk 2.0 uses `Authorization: Bearer`) or `REST` when authenticating with JWT. The tap will refuse to start if it detects this combination.

> **Meltano users:** the [meltano/hub plugin definition](https://github.com/meltano/hub/blob/main/_data/meltano/extractors/tap-salesforce/meltanolabs.yml) added `BULK2` to the `api_type` options some time after this tap began supporting it. If you locked the plugin before that hub update, your local `plugins/extractors/tap-salesforce--meltanolabs.lock` may still list only `REST` and `BULK`, and Meltano will reject `BULK2` at config-validation time with `'BULK2' is not a valid choice for 'api_type'`. Refresh the lockfile with `meltano lock --update --plugin-type extractor tap-salesforce`.

**Optional**
```
{
  "start_date": "2017-11-02T00:00:00Z",
  "state_message_threshold": 1000,
  "max_workers": 8,
  "streams_to_discover": ["Lead", "LeadHistory"]
}
```

The `client_id` and `client_secret` keys are your OAuth Salesforce App secrets. The `refresh_token` is a secret created during the OAuth flow. For more info on the Salesforce OAuth flow, visit the [Salesforce documentation](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_understanding_web_server_oauth_flow.htm).

The `start_date` is used by the tap as a bound on SOQL queries when searching for records.  This should be an [RFC3339](https://www.ietf.org/rfc/rfc3339.txt) formatted date-time, like "2018-01-08T00:00:00Z". For more details, see the [Singer best practices for dates](https://github.com/singer-io/getting-started/blob/master/BEST_PRACTICES.md#dates).

The `api_type` is used to switch the behavior of the tap between using Salesforce's "REST", "BULK" and "BULK 2.0" APIs (each using the `queryAll` operation to include deleted and archived records). When new fields are discovered in Salesforce objects, the `select_fields_by_default` key describes whether or not the tap will select those fields by default.

The `state_message_threshold` is used to throttle how often STATE messages are generated when the tap is using the "REST" API. This is a balance between not slowing down execution due to too many STATE messages produced and how many records must be fetched again if a tap fails unexpectedly. Defaults to 1000 (generate a STATE message every 1000 records).

The `max_workers` value is used to set the maximum number of threads used in order to concurrently extract data for streams. Defaults to 8 (extract data for 8 streams in paralel).

The `streams_to_discover` value may contain a list of Salesforce streams (each ending up in a target table) for which the discovery is handled.
By default, discovery is handled for all existing streams, which can take several minutes. With just several entities which users typically need it is running few seconds.
The disadvantage is that you have to keep this list in sync with the `select` section, where you specify all properties(each ending up in a table column).

## Run Discovery

To run discovery mode, execute the tap with the config file.

```
tap-salesforce --config config.json --discover > properties.json
```

## Sync Data

To sync data, select fields in the `properties.json` output and run the tap.

```
tap-salesforce --config config.json --properties properties.json [--state state.json]
```

Copyright &copy; 2017 Stitch

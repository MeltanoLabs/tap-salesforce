# tap-salesforce

`tap-salesforce` is a Singer tap for tap-salesforce.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Configuration

### Accepted Config Options

| Setting              | Required | Default | Description                                                                                                                                 |
|:---------------------|:--------:|:-------:|:--------------------------------------------------------------------------------------------------------------------------------------------|
| client_id            |   True   |  None   | Client id, used for getting access token if access token is not available                                                                   |
| client_secret        |   True   |  None   | Client secret, used for getting access token if access token is not available                                                               |
| start_date           |  False   |  None   | Earliest record date to sync                                                                                                                |
| end_date             |  False   |  None   | Latest record date to sync                                                                                                                  |
| domain               |   True   |  None   | Website domain for site url, ie., https://{domain}.salesforce.com/services/data/                                                            |
| auth                 |   True   |  None   | Auth type for Salesforce API requires either access_token or username/password                                                              |
| bulk_load            |   True   |  False  | Toggle for using BULK API method |                                                                                                           |
| stream_maps          |  False   |  None   | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). 
| stream_map_config    |  False   |  None   | User-defined config values to be used within map expressions.                                                                               |
| flattening_enabled   |  False   |  None   | 'True' to enable schema flattening and automatically expand nested properties.                                                              |
| flattening_max_depth |  False   |  None   | The max depth to flatten schemas.                                                                                                           |

The auth setting works either with access token or username/password, set by the following configs:

Auth with access token:
```bash
TAP_SALESFORCE_AUTH_FLOW = 'oauth'
TAP_SALESFORCE_AUTH_TOKEN = ''
```

Auth with username/password:
```bash
TAP_SALESFORCE_AUTH_FLOW = 'password'
TAP_SALESFORCE_AUTH_USERNAME = ''
TAP_SALESFORCE_AUTH_PASSWORD = ''
```

A full list of supported settings and capabilities for this tap is available by running:

```bash
tap-salesforce --about
```

## Elastic License 2.0

The licensor grants you a non-exclusive, royalty-free, worldwide, non-sublicensable, non-transferable license to use, copy, distribute, make available, and prepare derivative works of the software.

## Installation

```bash
pipx install git+https://github.com/ryan-miranda-partners/tap-salesforce.git
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

A salesforce access token is required to make API requests. (See [salesforce API](https://developers.salesforce.com/docs/api/working-with-oauth) docs for more info)

## Usage

You can easily run `tap-salesforce` by itself or in a pipeline using [Meltano](https://meltano.com/).

## Stream Inheritance

This project uses parent-child streams. Learn more about them [here](https://gitlab.com/meltano/sdk/-/blob/main/docs/parent_streams.md).

### Executing the Tap Directly

```bash
tap-salesforce --version
tap-salesforce --help
tap-salesforce --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-salesforce` CLI interface directly using `poetry run`:

```bash
poetry run tap-salesforce --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-salesforce
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-salesforce --version
# OR run a test `elt` pipeline:
meltano elt tap-salesforce target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.

## BULK API vs REST API

The `bulk_load` config toggles the use of the BULK API for pulling data. The REST and BULK APIs have a few key differences.

### Data Volume and Batch Processing

**Bulk API** : This API is designed for processing large volumes of data. The connector submits a batch of data for processing, and receives a job ID in response. It then uses that job ID in a query to retrieve the batched data.

**REST API** : The REST API in Salesforce is more suitable for working with individual records or smaller datasets.

### Request and Response Format

**Bulk API** : The Bulk API 2.0 uses a simplified format using CSV files for easier data loading and manipulation. The connector modifies the response CSV into a JSON object.

**REST API** : The REST API primarily uses JSON for requests and responses

### Use Cases

**Bulk API** : It is best suited for scenarios where you need to process large amounts of data, such as data migration, data warehousing, or mass updates to existing records. It's particularly useful when dealing with thousands to millions of records.

**REST API** : The REST API is more suitable for real-time interactions, user interfaces, and integrations that involve smaller data volumes.
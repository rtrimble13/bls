# bls

[![CI](https://github.com/rtrimble13/bls/actions/workflows/ci.yml/badge.svg)](https://github.com/rtrimble13/bls/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

A command-line client (and small Python library) for the
[U.S. Bureau of Labor Statistics Public Data API](https://www.bls.gov/developers/).
It is built for two audiences at once: people doing ad-hoc research in a
terminal, and automations or AI agents that need predictable, scriptable access
to BLS time series.

```console
$ export BLS_API_KEY=...            # free key from https://data.bls.gov/registrationEngine/
$ bls data LNS14000000 CUUR0000SA0 --start 2024-01 --end 2024-03 --format csv
series_id,date,year,period,period_name,frequency,value,footnotes,latest
LNS14000000,2024-01-01,2024,M01,January,monthly,3.7,,false
LNS14000000,2024-02-01,2024,M02,February,monthly,3.9,,false
LNS14000000,2024-03-01,2024,M03,March,monthly,3.8,,false
CUUR0000SA0,2024-01-01,2024,M01,January,monthly,308.417,,false
CUUR0000SA0,2024-02-01,2024,M02,February,monthly,310.326,,false
CUUR0000SA0,2024-03-01,2024,M03,March,monthly,312.332,,false
```

## Features

- **Everything the API v2 offers**: multi-series data requests with
  `catalog`, `calculations`, `annualaverage`, `aspects` and `latest`; the
  survey list and survey detail endpoints; popular series.
- **Limits handled for you**: requests for more than 50 series or more than
  20 years are split into several API calls and merged (25 series / 10 years
  without a key); transient failures are retried with back-off.
- **Filters the API lacks**: inclusive date ranges down to the month
  (`--start 2020-03 --end 2024-Q2`), `--years N`, frequency selection
  (`--frequency monthly|quarterly|semiannual|annual`), latest-only.
- **Output for humans and machines**: `table`, `json`, `jsonl`, `csv`,
  `parquet`; long (tidy) or wide layouts; `--columns` to pick columns;
  `--raw` for the untouched API shape.
- **Discovery with fuzzy search**: `bls search "core cpi"` works offline
  against a curated catalog of ~130 widely used series and the survey list,
  tolerating typos and word order; `bls series list --survey CU --query gasoline`
  searches the *complete* series directory of a survey (BLS flat files);
  `bls popular` and `bls series info` use the live API.
- **Automation friendly**: API key from the environment only, stable exit
  codes, warnings on stderr and data on stdout, `--strict`, `--quiet`,
  `--series-file -` to read ids from stdin, JSON by default when piped.
- **Linux CI, tag-driven releases**: versions are derived from `vX.Y.Z` git
  tags; a one-click workflow bumps, tags and publishes.

## Installation

Requires Python 3.10+.

```bash
# with uv (recommended)
uv tool install git+https://github.com/rtrimble13/bls
# or with pipx
pipx install git+https://github.com/rtrimble13/bls
# or into the current environment
pip install git+https://github.com/rtrimble13/bls
```

For development:

```bash
git clone https://github.com/rtrimble13/bls && cd bls
make install        # uv venv + editable install with dev extras
make check          # ruff, mypy, pytest
```

## Configuration

Set your registration key once; everything else has sensible defaults.

| Variable | Purpose | Default |
| --- | --- | --- |
| `BLS_API_KEY` | Registration key. Without it the API allows 25 requests/day, 25 series and 10 years per request. | unset |
| `BLS_FORMAT` | Default `--format` (`json`, `jsonl`, `csv`, `parquet`, `table`). | `table` on a TTY, `json` otherwise |
| `BLS_CACHE_DIR` | Where survey lists and flat files are cached. | `$XDG_CACHE_HOME/bls` or `~/.cache/bls` |
| `BLS_TIMEOUT` | HTTP timeout in seconds. | `30` |
| `BLS_MAX_RETRIES` | Retries for 429/5xx/network errors. | `3` |
| `BLS_USER_AGENT` | User-Agent header. BLS flat files require a descriptive one. | `bls-cli/<version> (+repo url)` |
| `BLS_API_BASE_URL` | Override the API endpoint (testing, proxies). | `https://api.bls.gov/publicAPI/v2` |
| `NO_COLOR` | Disable colour in table output. | unset |

The key is deliberately **not** accepted as a flag (see
[ADR 0003](docs/adr/0003-api-key-from-environment.md)). `bls config` prints the
effective configuration with the key masked; `bls doctor` additionally checks
connectivity.

## Usage

```text
bls data      Fetch observations for one or more series
bls latest    Newest observation per series (alias for data --latest)
bls search    Fuzzy-search the curated series catalog and the survey list (offline)
bls surveys   List surveys; `surveys show CU` for API metadata
bls popular   Series BLS flags as popular (optionally per survey)
bls series    list --survey XX (complete directory) | info ID... (catalog metadata)
bls config    Effective configuration (key masked)
bls doctor    Configuration + connectivity check
bls cache     info | clear
bls version   Print the version
```

Run `bls <command> --help` for all options. Highlights:

```bash
# Monthly CPI-U and core CPI, 2019 through June 2024, one column per series
bls data CUUR0000SA0 CUUR0000SA0L1E --start 2019 --end 2024-06 --layout wide -f csv -o cpi.csv

# Unemployment rate, last 5 years, with 1/3/6/12-month changes, as Parquet
bls data LNS14000000 --years 5 --calculations -f parquet -o unrate.parquet

# Only quarterly rows of a productivity series, plus annual averages
bls data PRS85006092 --start 2015 --end 2024 --frequency quarterly --frequency annual --annual-average

# Latest nonfarm payrolls with catalog metadata (title, survey, seasonality)
bls latest CES0000000001 --catalog

# Series ids from a file (or stdin with "-"); fail if any series has no data
bls data --series-file ids.txt --years 2 --strict -f jsonl

# Find series without knowing the id
bls search "unemploymnt rate"            # typo-tolerant, offline
bls search jolts --kind all              # series and surveys
bls series list --survey AP --query eggs # exhaustive, from BLS flat files
bls popular --survey CU --catalog        # what others are pulling

# Exactly what the API returned (after client-side filtering)
bls data LNS14000000 --latest --raw
```

### Dates and frequencies

`--start`/`--end` accept `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, `YYYY-Qn` and `YYYY-Hn`.
Both bounds are inclusive. A period is kept when **any part of it overlaps**
the range, so `--start 2020-06` keeps Q2 2020 and the 2020 annual value. The
API only understands whole years, so the CLI fetches whole years and trims
locally ([ADR 0007](docs/adr/0007-client-side-filtering.md)).

BLS period codes map to frequencies as follows: `M01`-`M12` monthly, `Q01`-`Q04`
quarterly, `S01`-`S02` semiannual, `A01` annual, and `M13`/`Q05`/`S03` are
*annual averages* (frequency `annual`, flagged `annual_average=true`, only
returned when you pass `--annual-average`).

### Output

Long layout columns, always in this order:

```
series_id, date, year, period, period_name, frequency, value, footnotes, latest
```

followed by `annual_average` (with `--annual-average`), catalog fields such as
`series_title`, `survey_name`, `seasonality` (with `--catalog`), and
`net_change_{1,3,6,12}` / `pct_change_{1,3,6,12}` (with `--calculations`).
`date` is the first day of the period (ISO 8601 in text formats, `date32` in
Parquet); `value` is a float, `null` when BLS reports `-`.

The wide layout has one row per period and one column per series id. See
[docs/output-formats.md](docs/output-formats.md) for schemas and examples.

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | success |
| 1 | unexpected error |
| 2 | usage error (bad flag, bad date, unknown column) |
| 3 | the API reported a failure or returned an HTTP error |
| 4 | daily request threshold / rate limit exceeded |
| 5 | network problem (DNS, timeout, connection reset) |
| 6 | `--strict` and at least one series returned no data |
| 7 | configuration error |

Warnings (missing series, API notes such as *No Data Available for Series X
Year: 2026*) go to **stderr**; data goes to **stdout**. `--quiet` silences the
warnings.

## Python API

```python
from bls import BLSClient, Settings

with BLSClient.from_settings(Settings.from_env()) as client:  # or BLSClient(api_key="...")
    resp = client.fetch(["LNS14000000", "CUUR0000SA0"], start_year=2015, end_year=2024,
                        calculations=True)
    for series in resp.series:
        for obs in series.data:
            print(series.series_id, obs.date, obs.value)
```

See [docs/python-api.md](docs/python-api.md).

## For agents and automations

`bls` is designed to be called from scripts, cron jobs, GitHub Actions and
agent skills. [docs/agents.md](docs/agents.md) is a compact contract
(commands, flags, output schema, exit codes, request-budget guidance) that a
skill can reference, and [examples/skill/SKILL.md](examples/skill/SKILL.md) is
a ready-made skill. [examples/github-actions/](examples/github-actions/)
contains a scheduled data-pull workflow.

## Documentation

- [docs/usage.md](docs/usage.md) - full command reference
- [docs/configuration.md](docs/configuration.md) - environment variables, limits, caching
- [docs/output-formats.md](docs/output-formats.md) - record schema per format
- [docs/series-ids.md](docs/series-ids.md) - how to find and read BLS series ids
- [docs/agents.md](docs/agents.md) - the contract for agentic workflows
- [docs/python-api.md](docs/python-api.md) - using the library
- [docs/development.md](docs/development.md) - contributing, tests, tooling
- [docs/releasing.md](docs/releasing.md) - versioning and the release workflow
- [docs/adr/](docs/adr/) - architecture decision records
- [CHANGELOG.md](CHANGELOG.md)

## Versioning

Versions are `vMAJOR.MINOR.PATCH` git tags; the package version is derived from
them at build time (hatch-vcs). Releases are produced by the **Bump version**
workflow in the Actions tab (choose patch/minor/major), which updates
`CHANGELOG.md`, tags, builds, verifies, and publishes a GitHub release
([docs/releasing.md](docs/releasing.md)).

## Data notes

- BLS data are public domain; see the
  [BLS API terms of service](https://www.bls.gov/developers/termsOfService.htm).
- Flat-file downloads (`bls series list`) come from `download.bls.gov`, which
  refuses requests without a descriptive `User-Agent`; set `BLS_USER_AGENT`
  with a contact address if you hit HTTP 403.
- The bundled survey list is a snapshot; `bls surveys --refresh` fetches the
  live list and caches it.

## License

MIT - see [LICENSE](LICENSE).

# Development

## Setup

```bash
git clone https://github.com/rtrimble13/bls && cd bls
make install          # creates .venv with uv and installs -e ".[dev]"
source .venv/bin/activate
bls --help
```

Without `make`: `uv venv && uv pip install -e ".[dev]"`.

## Everyday commands

| Command | What it does |
| --- | --- |
| `make check` | ruff lint + format check, mypy (strict), pytest with coverage. Same as CI. |
| `make format` | ruff format + autofix |
| `make test` | pytest |
| `make build` | sdist and wheel into `dist/` |
| `pre-commit install` | optional git hooks (ruff, whitespace, yaml/json checks) |

## Layout

```
src/bls/
  cli/            Typer app: _common (plumbing), data, discover, meta
  client.py       HTTP client: chunking, retries, endpoints
  config.py       Settings from environment variables
  periods.py      Period codes, frequencies, date-spec parsing, range overlap
  models.py       Observation / Series / DataResponse / Survey
  filters.py      Client-side observation filters
  records.py      Flatten to records; wide pivot
  output.py       json / jsonl / csv / parquet / table writers
  search.py       Fuzzy scoring and search
  catalog.py      Bundled data loaders (surveys snapshot, curated series)
  flatfiles.py    download.bls.gov series directories
  cache.py        Small file cache
  errors.py       Exceptions and exit codes
  data/           surveys.json, series_catalog.json
tests/            pytest suite with a fake BLS API (httpx.MockTransport)
docs/             user docs and ADRs
examples/         scripts, a GitHub Actions workflow, an agent skill
scripts/          release helpers (next_version, changelog_*)
```

## Testing philosophy

The BLS API is never called in tests. `tests/conftest.py` contains `FakeBLS`, a
small in-memory implementation of the four endpoints plus the flat-file host,
served through `httpx.MockTransport`. CLI tests inject it via
`State(transport=...)` passed as the Typer context object; client tests pass it
to `BLSClient(transport=...)`. The fake generates deterministic observations so
tests can assert on counts, ordering and request payloads.

To exercise the real API locally:

```bash
export BLS_API_KEY=...
bls doctor
bls latest LNS14000000 -v
```

## Adding a series to the curated catalog

Edit `src/bls/data/series_catalog.json`. Each entry needs `id`, `title`,
`survey` (must equal the first two characters of the id), `frequency`,
`seasonal` (`SA`/`NSA`), `units`, and `tags` (search keywords). Keep national
headline series before regional ones within a survey: ties in search score
keep file order. Verify the id with `bls series info ID` before committing.

Everyday wording goes in one of two places ([ADR 0012](adr/0012-catalog-aliases.md)):

- **`tags`** for single words and established terms (`jobs`, `pay`, `core`,
  `u-6`). Each word of a tag earns credit on its own, so avoid multi-word tags
  whose words could pair with unrelated titles.
- **`aliases`** (optional) for everyday phrases people type whole
  (`grocery prices`, `wage growth`, `cost of living`). An alias matches only
  the entire query, ignoring case, word order, plurals and small words such as
  "of" and "in", and lends no credit to its individual words.

Check a new phrase with `bls search "<phrase>"`, and check that it does not
create matches for unrelated queries.

## Style

- Python 3.10+, `from __future__ import annotations`, type hints everywhere
  (mypy strict).
- Ruff for lint and formatting, line length 100.
- CLI commands live in `src/bls/cli/*.py` and register themselves via
  `register(app)`; shared behaviour goes in `_common.py`.
- Errors raised from library code are `BLSError` subclasses; the CLI maps them
  to exit codes in `handle_errors`.
- Decisions with lasting consequences get an ADR in `docs/adr/`.

# 0004. Tidy records as the canonical shape; JSON, JSONL, CSV, Parquet, table

Date: 2026-10-24
Status: accepted

## Context

The API returns nested JSON (`Results.series[].data[]`) with string-typed
values, period codes instead of dates, newest-first ordering, and optional
`catalog`/`calculations` sub-objects. Consumers want spreadsheets, dataframes,
`jq` pipelines and data lakes.

## Decision

Normalise every observation into a flat **record** with a fixed core column
order (`series_id, date, year, period, period_name, frequency, value,
footnotes, latest`), typed values (`date` as a real date, `value` as float or
null), chronological order, and optional extra columns appended in a defined
order. All formats serialise the same records:

| format | purpose |
| --- | --- |
| `json` | default for pipes; array of objects |
| `jsonl` | streaming / append-friendly |
| `csv` | spreadsheets, pandas |
| `parquet` | typed columnar storage (pyarrow, snappy) |
| `table` | humans; default on a TTY |

A `--layout wide` pivot and a `--raw` escape hatch (API-shaped JSON, after
filtering) are provided; `--columns` projects identically in every format.

## Consequences

- Column names and order are part of the contract; adding columns is a minor
  change, renaming or reordering core columns is major.
- `date` is the *first day* of the period; quarterly/annual consumers must not
  read it as a month-end.
- Catalog columns vary by survey and may be empty; CSV takes the union of keys.

---
name: bls-data
description: Fetch U.S. labor and price statistics (CPI, unemployment, payrolls, PPI, JOLTS, wages) from the Bureau of Labor Statistics with the `bls` CLI. Use when a task needs official BLS time series, the latest reading of an economic indicator, or a CSV/Parquet extract of BLS data.
---

# BLS data via the `bls` CLI

`bls` is a command-line client for the BLS Public Data API. It is installed
(`bls --version` works) and reads the API key from `BLS_API_KEY`.

## Rules

1. Always pass `--format json` (or `jsonl`/`csv`/`parquet` for files). Parse
   **stdout** only; stderr holds warnings.
2. Resolve series ids before fetching data:
   - `bls search "<plain words>" --limit 5 --format json` (offline, free). Use
     the top `id` if its `score` >= 90, otherwise show the user the candidates.
   - For something not in the curated catalog:
     `bls series list --survey <XX> --query "<words>" --limit 10 --format json`
     (`XX` = `CU` consumer prices, `AP` average prices, `LN` labor force,
     `CE` national payrolls, `SM` state payrolls, `LA` state/local unemployment,
     `WP` producer prices, `JT` JOLTS, `CI` employment cost index,
     `PR` productivity). Run `bls surveys --format json` for the full list.
3. Fetch with one call for all ids you need:
   - latest: `bls latest ID1 ID2 --format json --strict`
   - range: `bls data ID1 ID2 --start YYYY-MM --end YYYY-MM --format json`
   - changes: add `--calculations` (adds `pct_change_12`, `net_change_1`, ...)
   - metadata: add `--catalog` (adds `series_title`, `seasonality`, ...)
4. Interpret exit codes: `0` ok; `2` your flags were wrong (read stderr, fix);
   `3` bad id or API error; `4` daily quota exhausted (stop, tell the user);
   `5` network (retry once after a pause); `6` a series had no data.
5. Budget: each `bls data` call costs `ceil(ids/50) * ceil(years/20)` requests
   of a 500/day quota. Do not loop over ids one at a time.

## Output schema

Each JSON row: `series_id, date (YYYY-MM-DD, first day of period), year,
period (M01-M12, Q01-Q04, A01; M13 = annual average), period_name, frequency,
value (number or null), footnotes, latest (bool)`, plus optional
`series_title`, `pct_change_12`, etc.

## Worked example

User: "What's the latest core CPI and how much is it up year over year?"

```bash
bls search "core cpi" --limit 3 --format json          # -> CUSR0000SA0L1E (SA), CUUR0000SA0L1E (NSA)
bls latest CUUR0000SA0L1E --calculations --format json  # value, pct_change_12
```

Report the `period_name`/`year`, `value` and `pct_change_12` from the result.
Prefer not-seasonally-adjusted (`NSA`) series for year-over-year changes and
seasonally adjusted (`SA`) for month-over-month.

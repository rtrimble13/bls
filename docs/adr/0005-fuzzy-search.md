# 0005. Offline fuzzy search over a curated catalog with RapidFuzz

Date: 2026-10-24
Status: accepted

## Context

The API cannot search for series; users must know ids like `CUUR0000SA0`.
BLS publishes complete series directories as large flat files, and a `/popular`
endpoint. Agents in particular need to turn "core inflation" into an id
without spending request quota.

## Decision

Three layers:

1. **`bls search`** - offline, zero-quota fuzzy search over a *curated* JSON
   catalog of ~130 headline series (id, title, survey, frequency, seasonal,
   units, tags) plus the survey list. Scoring is per query token: exact tag =
   1.0, whole word = 0.95, substring = 0.75, fuzzy (RapidFuzz ratio >= 72) =
   0.8 x ratio, averaged and scaled to 0-100; exact id/tag/title = 100. Ties
   keep catalog order so national headline series rank first.
2. **`bls series list --survey XX --query ...`** - exhaustive search over the
   survey's flat-file directory (ADR 0010).
3. **`bls popular` / `bls series info`** - live API.

RapidFuzz was chosen over `difflib` for speed and better partial matching, and
over embedding/vector approaches for zero infrastructure.

## Consequences

- The curated catalog must be maintained by hand; wrong ids are the main risk,
  so contributors verify with `bls series info`.
- Search results are deterministic and explainable (score bands), which suits
  agents.
- Not every BLS series is discoverable offline; the docs make the three layers
  explicit.

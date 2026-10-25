# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/) as `vMAJOR.MINOR.PATCH` git tags.

Releases are cut by the **Bump version** GitHub Actions workflow, which moves the
*Unreleased* section below under the new version heading.

## [Unreleased]
### Added

- `docs/practitioners-guide.md`: what `bls` can answer and how; a research
  workflow, series discovery tactics, analysis recipes (inflation, jobs, real
  wages, state rankings, monitoring), guidance on interpreting BLS data, an
  agent protocol and a question playbook. Linked from the README, the agent
  contract and the example skill.
- `bls search` understands everyday phrasing: single-word synonyms as tags
  (`jobs`, `grocery`, `pay`, `hiring`, `salary`) and a new optional catalog
  field, `aliases`, for whole phrases (`grocery prices`, `rent inflation`,
  `wage growth`, `cost of living`, `chicago inflation`) matched regardless of
  word order, plurals and small words. Aliases lend no credit to their single
  words, so queries for data BLS does not publish (`home prices`) still find
  nothing ([ADR 0012](docs/adr/0012-catalog-aliases.md)).

### Changed

- `bls search` skips small words ("of", "in", "the", "us") when scoring, so
  `unemployment in texas` matches like `texas unemployment`.
- `groceries` now ranks CPI food at home first rather than all food, and the
  average and median duration of unemployment rank ahead of the count of
  long-term unemployed.

## [0.1.0] - 2026-10-24
### Added

- `bls data` / `bls latest`: fetch observations for any number of series with
  automatic request splitting (series and year limits), date-range
  (`--start/--end/--years`), frequency (`--frequency`) and annual-average
  filters, catalog metadata, net/percent-change calculations, long and wide
  layouts, and `--strict` for automations.
- Output formats: `json`, `jsonl`, `csv`, `parquet` and a rich `table`;
  `--columns` to select and order columns; `--output` to write files.
- Discovery: `bls search` (offline fuzzy search over a curated series catalog
  and the survey list), `bls surveys`, `bls popular`, `bls series list`
  (complete per-survey directories from BLS flat files) and `bls series info`.
- Maintenance: `bls config`, `bls doctor`, `bls cache`, `bls version`.
- Python API (`bls.BLSClient`) with retries, chunking and typed models.
- Documentation, ADRs, examples, GitHub Actions CI and tag-driven releases.

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

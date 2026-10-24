# Architecture Decision Records

Decisions that shape `bls` and would be costly to reverse. One file per
decision, numbered in order of acceptance, following the
[MADR](https://adr.github.io/madr/) short form: context, decision, consequences.

| # | Title | Status |
| --- | --- | --- |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | accepted |
| [0002](0002-python-typer-cli.md) | Python package with a Typer CLI over a library core | accepted |
| [0003](0003-api-key-from-environment.md) | API key only from the environment | accepted |
| [0004](0004-tidy-records-and-output-formats.md) | Tidy records as the canonical shape; JSON, JSONL, CSV, Parquet, table | accepted |
| [0005](0005-fuzzy-search.md) | Offline fuzzy search over a curated catalog with RapidFuzz | accepted |
| [0006](0006-version-from-git-tags.md) | Version derived from `vX.Y.Z` git tags; workflow-driven releases | accepted |
| [0007](0007-client-side-filtering.md) | Fetch whole years, filter dates and frequencies client-side | accepted |
| [0008](0008-chunking-and-retries.md) | Transparent chunking and retries in the client | accepted |
| [0009](0009-linux-only-ci.md) | Linux-only GitHub Actions | accepted |
| [0010](0010-flat-file-discovery.md) | Exhaustive series discovery via BLS flat files | accepted |
| [0011](0011-stable-exit-codes-and-streams.md) | Stable exit codes; data on stdout, diagnostics on stderr | accepted |

To add one: copy the template below to `NNNN-short-title.md`, add a row here.

```markdown
# NNNN. Title

Date: YYYY-MM-DD
Status: proposed | accepted | superseded by NNNN

## Context
## Decision
## Consequences
```

# 0002. Python package with a Typer CLI over a library core

Date: 2026-10-24
Status: accepted

## Context

The tool must be easy to install for researchers (who mostly use Python),
callable from shell pipelines and agent skills, and produce Parquet. Options
considered: Python (Typer/Click/argparse), Go, Rust.

## Decision

Implement `bls` as a Python 3.10+ package (`bls-cli` on PyPI, import name
`bls`) with:

- a **library core** (`bls.client`, `bls.models`, `bls.records`, ...) that has
  no CLI concerns and is usable from notebooks and other programs;
- a **Typer** CLI (`bls.cli`) on top, one module per command group, each
  exposing `register(app)`;
- `httpx` for HTTP, `rapidfuzz` for fuzzy matching, `pyarrow` for Parquet,
  `rich` (via Typer) for tables;
- `src/` layout, `hatchling` build backend, `uv` for development.

`pyarrow` is a hard dependency rather than an extra so that `--format parquet`
always works in automations without a second install step.

## Consequences

- Install is `uv tool install` / `pipx install`; startup is ~150 ms, acceptable
  for a network-bound tool.
- Typer vendors Click since 0.27; the code imports only `typer` and raises
  `typer.BadParameter` for usage errors so it works with both old and new
  Typer versions.
- Parquet support costs ~40 MB of wheel on install; judged worth it for
  reliability in pipelines.

# 0003. API key only from the environment

Date: 2026-10-24
Status: accepted

## Context

BLS registration keys are free but rate-limited per key. The tool runs in
shells, cron, CI and agent sandboxes. A `--api-key` flag would leak into shell
history, process listings and agent transcripts, and would tempt people to
hard-code keys in skills.

## Decision

Read the key exclusively from `BLS_API_KEY`. Provide no flag and no config
file. `bls config` and `bls doctor` print it masked (`*******1234`). Operation
without a key is supported with the API's lower limits and a warning when a
key-only feature (`--catalog`) is requested.

Other settings follow the same pattern (`BLS_*` environment variables) so one
mechanism covers every deployment target.

## Consequences

- Secrets management is delegated to the environment (dotenv tools, CI secrets,
  agent sandboxes), where it belongs.
- Users with several keys switch by changing the variable; no per-call key
  selection.
- Tests never need a real key: the client takes `api_key=None`.

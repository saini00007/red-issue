# NOTES — research-agent-osprey-01

## Identity & scope
- Agent name: `research-agent-osprey-01` (unique; no other folder uses it).
- Work location: `improvment-research/research-agent-osprey-01/` only.
- Mode: read-only. No repositories modified; no remote writes; no scan triggered; no request fired at any target. Postgres access was SELECT-only through `docker exec scanner-postgres psql`; container access was `cat`/`ls`/`docker logs` only.

## Source availability at start (all four usable)
- **A — codebase**: local repo `autocan`, branch `feat/alpha-observability`, HEAD `f75608f` (directive cited `1c5551d`; HEAD is 3 commits ahead — recorded as a directive/actual mismatch, code treated as truth).
- **B — competitor research**: `competitor-research/{COMPARISON.md,escape,firecompass,xbow}` (dossiers + captured pages).
- **C — live server**: `ssh abhedi` → `abhedi-cc`, user `admin`. Read-only access worked: per-scan workdir volume `abhedi_red_scanner_data` (mounted in `scanner-cp` at `/var/lib/scanner`), Postgres `tenant_xbow`, `docker logs scanner-cp`, and `/home/admin/research/2026-09-29-deepdive/`.
- **D — public web**: not needed; all public claims were already captured under B and quoted from there.

## Live environment snapshot (read-only)
- Running scan at audit time: `84aea81a-7e43-495c-9974-ca064ddd3552` (VulnerableApp), started 20:08:31Z 2026-09-30; still `running` at 22:48Z (2 h 40 m). Left untouched.
- 12 recent scans in `tenant_xbow.scans` (3 completed multi-hour runs, 3 cancelled, 1 short 6-min run).
- Docker containers up: `scanner-cp`, `scanner-agent-84aea81a7e43`, `zap-…`, `browser-…`, `toolserver-…`, `vulnerableapp`, infra (`postgres`, `redis`, `pgbouncer`, `nginx`, `logging-proxy`).
- Logging-proxy blind spot noted per directive C4: does not apply to this scan (workers ran through OpenRouter `stealth/space-bunny-alpha`; the proxy DB only covers NVIDIA/nemotron scans).

## Method
1. WS-1 code reads (engine wave loop, fleet pool, ledger claim/resolve semantics) + live telemetry (scanner env, worker_runs, ledger states, scan_events, decisions.log, docker logs).
2. WS-3 competitor mechanisms extracted from B with file citations.
3. Gated design workstreams (WS-2/4/5/6) started only after WS-1 produced measured evidence; browser/chain/oracle code claims came from read-only exploration passes whose load-bearing citations were re-read and verified first-hand before publication.
4. Every claim in `REPORT.md` carries an Evidence Ledger row (Section 10) with source type and confidence.

## Gaps / caveats
- `worker_runs` rows for killed scans (e.g. 373bff88) are never closed (`finished_at NULL`), so their durations are inflated — flagged where used.
- Phase rows can remain `running` after scan `completed`; long finalize numbers for 1f5fe7c8 are therefore [INFER]-grade.
- Token/cost columns for the live scan are all zero by code path; a true token total for that scan is not recoverable from the DB.
- No raw prompts from proxy logs are reproduced (none were needed for this scan).

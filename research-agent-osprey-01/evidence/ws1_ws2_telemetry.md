# WS-1 / WS-2 — Raw telemetry (read-only)

All commands ran over `ssh abhedi` (user `admin`) against containers `scanner-cp`, `scanner-postgres`, `scanner-agent-84aea81a7e43`. SELECT-only. Secrets redacted. Capture window: 2026-09-30 22:08–22:55 UTC.

## Live scan identity
- scan_id `84aea81a-7e43-495c-9974-ca064ddd3552`
- tenant `16e69f07-f908-482b-8fc5-492852a61a91` (public.tenants name "XBOW Benchmark", schema `tenant_xbow`)
- target `http://172.17.0.1:9090/VulnerableApp/`
- started 20:08:31 UTC; `running` at 22:48 UTC (2 h 40 m)
- workdir `/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/84aea81a-.../` on volume `abhedi_red_scanner_data`

## Production env (agent container; redacted)
```
WORK_PATH=/var/lib/scanner/16e69f07-.../84aea81a-...
SCANNER_ENGINE_V2=true            SCANNER_ENGINE_FANOUT=4
SCANNER_ENGINE_BATCH_DISPATCH=true  SCANNER_ENGINE_BATCH_BUDGET_S=0
SCANNER_ENGINE_BATCH_MAX_CELLS=8    SCANNER_ENGINE_POOL_HARD_CAP=4
SCANNER_ENGINE_STUCK_WINDOW_S=1200  SCANNER_ENGINE_WORKER_WALL_S=86400
SCANNER_ENGINE_MAX_WAVES=1000       SCANNER_ENGINE_RUNAWAY_WALL_S=86400
SCANNER_LEDGER_LEASE_S=1800         SCANNER_LEDGER_ATTEMPT_CAP=6
SCANNER_ENGINE_SYNC_INTERVAL_S=120  SCANNER_ENGINE_LIVE_CONVERGENCE=true
SCANNER_ENGINE_REPORT_MIN_INTERVAL_S=60  SCANNER_ENGINE_MAX_REPORT_REGENS=50
SCANNER_ENGINE_BOSS=true            SCANNER_ENGINE_SEAT_MODELS=true
SCANNER_ENGINE_CHAIN_FLOOR=1        SCANNER_ENGINE_ESCALATE=1
SCANNER_ENGINE_RECON_EXPANSION_ROUNDS=3  SCANNER_ENGINE_EXPANSION_BUDGET=3
SCANNER_FLOOR_BUDGET_S=1200         SCANNER_EXPLOIT_FLOOR_ENABLED=true
SCANNER_EVIDENCE_GATE=true          SCANNER_LEDGER_MACHINE_CLOSE=true
SCANNER_AUTH_ORACLES_ENABLED=true   SCANNER_DESER_RCE_CONFIRM_ENABLED=true
SCANNER_ZAP_ENABLED=true            SCANNER_BROWSER_ENABLED=true
SCANNER_ENGINE_VERIFY=1             SCANNER_ENGINE_VERIFY_WALL_S=1200
SCANNER_ENGINE_VERIFY_TICK_CONCURRENCY=2
SCANNER_ENGINE_PLAYBOOK=true        SCANNER_ENGINE_DIGEST=1
SCANNER_ENGINE_MAX_RETRIES=8        SCANNER_ENGINE_HTTP_TIMEOUT=300
```
Note: `time_cap_seconds` is empty and `cost_cap_usd=0` on all recent scans → no clock/cost stop; stop is progress-driven.

## Ledger state snapshots (scan 84aea81a)
22:16 UTC
```
attempts:  0 → 6658 | 1 → 2151 | 2 → 418 | 3 → 10
```
22:48 UTC — `state,count`:
```
na 6247 | testing 1701 | tested_clean 943 | untested 321 | confirmed 19 | blocked 6
```
claimed_by × state (22:16):
```
(null) na 6247 | (null) untested 321 | (null) testing 49 | (null) tested_clean 43 | (null) confirmed 15
floor-blind      testing 528 | tested_clean 1 | confirmed 1
floor-access     tested_clean 400 | testing 394
floor-logic      testing 330
floor-clientside testing 196 | confirmed 2
floor-authclass  tested_clean 158
floor-nofamily   tested_clean 149 | testing 40 | confirmed 1
floor-ratelimit  tested_clean 87 | testing 34
floor-upload     testing 71
floor-config     tested_clean 60
floor-hygiene    tested_clean 34 | testing 13
floor-injection  testing 16 | tested_clean 5
wave1            testing 33
```

## Worker timeline (worker_runs; 41 rows at 22:48; 38 finished / 3 running)
| worker | status | duration | findings_count |
|---|---|---|---|
| batch1-b-7-bunny | ok | 2961 s | 67 |
| batch1-b-11-bunny | running | 1745 s+ | 0 |
| batch1-b-9-bunny | ok | 1663 s | 63 |
| batch1-b-10-bunny | ok | 1476 s | 65 |
| batch0-b-0-bunny | ok | 1223 s | 32 |
| s2w100-access-bunny | ok | 1167 s | 39 |
| batch1-b-6-bunny | ok | 1055 s | 62 |
| batch0-b-5-bunny | ok | 881 s | 31 |
| batch1-b-13-bunny | ok | 787 s | 70 |
| batch1-b-12-bunny | ok | 745 s | 68 |
| … 31 more (avg ≈ 594 s) | | | |

Phase joins: wave0 20:13:13→20:40:50 (11 batches); authed-recrawl 20:40:51→20:43:01; escalation 20:43:02→21:02:29 (4 workers); wave1 21:02:54→ongoing (24 batches at capture). 3 workers running at 22:48 (b-11, b-15, b-17→b-18 spawned 22:18; later b-21..b-23 turn1 in log).

## Event aggregates (scan_events, 84aea81a)
```
tool.started 3111 | tool.done 3110 | floor.tick 151 | finding.recorded 63
worker.started 35→41 | worker.finished 32→38 | component.health 4
phase.started 2 | phase.finished 1 | governor.decision 2 | expansion.approved 1
engine.level_resolved 1
plan.revised 0
```
Governor decisions:
```
20:13:12 continue  plateau=false unresolved=770  invocations=46   elapsed=48.6s
21:02:54 continue  plateau=false unresolved=2537 invocations=1395 elapsed=3029.9s
```
(No third decision: the loop is inside wave 1.)

Floor ticks (first and last):
```
20:13:16 upload batch=11 cells=0    fired=14   signals=14  findings=0
21:16:20 access batch=11 cells=1173 fired=2125 signals=930 findings=4
```
Floor sweep summary for wave 1: 1,173 cells swept → 930 signals → 4 findings (≈79% signal rate).

## Workdir artifacts (sizes / line counts)
```
decisions.log                 86 lines (all max_turns_exceeded in sampled head/tail; 73/73 at first capture)
findings.jsonl                71 lines; 64 contain "verified": true; DB rows 42 (39 verified)
ledger_updates.jsonl          1968 lines: state testing 1816, tested_clean 144, blocked 8
exploit_floor_signals.jsonl   1157 lines: blind 502, access 344, clientside 175, upload 112, injection 13, chain 7, zap 4
oob_interactions.jsonl        317 lines
oob_registry.jsonl            740 lines
report.md 1,521,104 B · report.json 1,988,655 B · report.html 97,669 B
scan_brief.md 18,100 B (single `#` heading; prose sections)
tool_outputs/                 28 subdirs, 77,824 B dirent
evidence/                     verification reports + artifacts (e.g. INDEP_VERIFY_*, VERIFICATION_REPORT.md)
```
No `plan.json`, no `coverage_quality.json` at capture.

## Agent log counters (docker logs scanner-agent-84aea81a7e43)
```
ledger.resolve.update_unmatched   522
ledger.resolve.finding_unmatched  362
verification.failed               146   (all "Max turns (12) exceeded")
verification.reproduced             0   (no such log line observed)
father.boss_tick_failed             0   (boss failure is silent by design)
father.sync_moat_failed             0
```
Also observed: `tool.blocked.exploit_forbidden` (a worker port-scan attempt correctly blocked), `verification.spawned` lines during the live tick.

## agent_messages (84aea81a)
```
role = assistant for all 74 rows (later 86 by capture)
turn_index histogram: 1→33, 2→18, 3→10, 4→4, 5→4, 6→3, 7→2
tokens_in = 0, tokens_out = 0, cost_usd = 0 on every row
```
Cause [CODE]: the MaxTurnsExceeded path records a marker with zeros (`agents_runtime.py:440-445`).

## Completed-scan comparison
| scan | target | wall | states (na / tested_clean / attempted / confirmed / blocked / testing) | workers |
|---|---|---|---|---|
| 68a58881 | duck-store.escape.tech | 17 h 53 m | 4859 / 1388 / 1303 / 65 / 5 / 12 | 172, avg 2275 s |
| 1f5fe7c8 | infinitycapital.bh | 15 h 15 m | 3180 / 1253 / 853 / 24 / 26 / 1 | 321, avg 419 s |
| 373bff88 | duck-store.escape.tech | 47 m 58 s | 4311 / 348 / 1516 / 49 / 10 / 6 | 12 (rows unclosed: avg inflated) |
| 7ec54a2f | vulnerableapp | 6 m 0 s | 130 / 0 / 0 / 0 / 0 / 41 | 8, avg 71 s |
Note: `exploitation`/`finalize` phase rows are sometimes left `running` after `completed` status (68a58881, 373bff88, 1f5fe7c8), so phase durations for those are unreliable [INFER].

## Key read-only commands used
```
ssh abhedi 'docker inspect scanner-agent-84aea81a7e43 --format "{{json .Config.Env}}"'
ssh abhedi 'docker exec scanner-postgres psql -U scanner -d scanner -tAc "SELECT ..."'
ssh abhedi 'docker exec scanner-cp cat /var/lib/scanner/<tenant>/<scan>/decisions.log'
ssh abhedi 'docker logs scanner-agent-84aea81a7e43 | grep -c "update_unmatched"'
```
No writes, no inserts, no container stops, no request fired at the target.

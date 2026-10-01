## WS-2 — Observed-Failure Forensics (Synthesizer Report Section)

### Bottom line
The platform's silent-loss and flood pathways dominate every finalized scan: ledger `resolve` drops 9,485 coverage/finding results in a single scan while a watchdog re-emits 41,978 unconsumed `method_switch` lines (92% of the cp log), and 59% of worker runs crash on provider empty-completions. WS-1's "coverage thrash" is **CONFIRMED but reframed** — reclaim thrash is real (23-34% of applicable cells claimed ≥2×) yet the *dominant* coverage-stall driver is the coupled **starvation** (22-39% of applicable cells never claimed once, swept to terminal `attempted` at finalize). The OOB honest-classifier works exactly as designed in all three scans (17 would-be CRITICAL `cmdi` claims downgraded to `ssrf` live) — the historical mass-FP bug is dead.

### Observed-Failure Catalog (aggregate)

| Failure class | Aggregate count / scope | Mechanism (1 line) | Source [QUERY] |
|---|---|---|---|
| F1 coverage-result drop (`update_unmatched`) | 7,735 events / scan 68a58881 (vs 2,481 update lines → ~3× re-log) | coverage line whose (endpoint,vuln_class) matches no ledger cell is counted unmatched + discarded, re-run every reconcile tick | grep -c on agent.log → 7735; [CODE] ledger/service.py:949 |
| F2 finding drop (`finding_unmatched`) | 1,750 events / scan 68a58881 | finding matching no ledger cell is dropped from coverage, re-logged per tick | grep -c on agent.log → 1750; [CODE] ledger/service.py:873 |
| F3 `finding.duplicate_skipped` flood | 18,506 events / scan 68a58881 (38 findings persisted → ~487×) | every reconcile re-ingests findings.jsonl; each already-persisted dedup_hash re-logs a skip | event-freq on agent.log; [CODE] tools/findings.py:409 |
| F4 LLM-verifier unavailable (fail-open) | 524 / 540 spawned = 97% / scan 68a58881 | verifier subagent raises (timeout/egress/SDK); fails open, stamps `verifier_unavailable`, masking a non-functional tier | event-freq on agent.log; [CODE] hooks/verification.py:240 |
| F5 `scan.method_switch` debug flood | 41,978 lines = 92% of 45,774-line cp log (43,353 = live 84aea81a) | watchdog publishes one pubsub event per stuck `testing` cell per tick; no consumer, not persisted to scan_events | docker logs grep -c; [CODE] poller.py:1160-1165 |
| F6 worker-run crashes | 578 / 977 = 59% error (no-choices=471=81% of errors, 429=91, 500=9, 400=6, 502=1) | provider/LLM failures bubble to `worker_runs.status='error'`; empty-completion dominates | psql worker_runs GROUP BY status,error |
| F7 retire-unreached sweep | 8,771 cells → terminal `attempted` (all scans) | finalize UPDATEs untested / empty-`testing` applicable cells to `attempted` so scan reads `completed` | psql ledger_cell GROUP BY state; [CODE] finalize.py:454-461 · flag scanner_finalize_retire_unreached (config.py:451, default True) |
| F8 never-reached (untested at end) | 5,299 cells `untested` (all scans) | cells materialized but never claimed/probed before scan end | psql ledger_cell GROUP BY state |
| F9 stuck-`testing` limbo | 2,774 cells `testing` (all scans); LIVE 1,654/1,703 (97%) in expired-lease limbo | claimed into `testing`, never resolved nor released; exactly the re-claimable state feeding F5 | psql ledger_cell; [CODE] poller.py:1147 watchdog |
| F10 reasoning telemetry near-blind | 1 msg / 12,143 tools (~12,000×), 68a58881; 139/9,843; 76/5,983 | agent_messages table near-empty vs tool_invocations; message stream not persisted | psql FULL OUTER JOIN; [CODE] telemetry.py:247 |
| F11 scans not completing clean | cancelled=19 / failed=4 / partial=1 vs completed=18 | most scans end via SIGKILL/time-cap or fail (agent_exit_-1; zap image-pull 404) | psql scans GROUP BY status + failure_reason |
| F12 cancel SIGKILL grace-cut | 2 / cp window | SIGTERM grace expired → agent container SIGKILLed (un-flushed /work loss hazard) | docker logs grep -c; [CODE] poller.py:972 |
| F13 floor `nofamily_inconclusive` | 135 / scan 68a58881 | floor probe fired, no vuln family matched → cell left inconclusive (feeds limbo) | event-freq; [CODE] exploit_floor.py:3141 |
| F14 floor `logic_skipped` | 24 / scan 68a58881 | authz/logic floor skips cell — no auth-session identity (bootstrap gap) | event-freq; [CODE] exploit_floor.py:3949 |
| F15 dangling tool invocations | 17 (started=27,056 vs done=27,039, all scans) | tool.started with no tool.done — tool/agent killed mid-call | psql scan_events GROUP BY event_type |
| F16 guard-blocked tool calls | destructive=4, exploit_forbidden=2 / scan 68a58881 | scope/guard hooks block agent tool calls (working as designed, low volume) | event-freq; [CODE] hooks/bash.py, hooks/scope.py |
| F17 driver-error telemetry undercount | agent.log surfaces 13 vs proxy_log.db 6,492 non-200 (26.4% of 24,630) | SDK retries mask errors; only post-retry failures reach agent.log → ~500× undercount | sqlite3 proxy_log.db status GROUP BY; grep agent.log |
| F18 verify max-turns retry amplification | 511 "Max turns (12) exceeded" over only 10 distinct finding_ids (~51× each) | finalize verification re-drives same model against same unverifiable finding every tick, no give-up/backoff; fuels the 3,578 nemotron 429s | grep agent.log; [CODE] finalize.py verify loop |
| F19 non-nemotron route telemetry blind | infinity(bunny): 133/135 (98.5%) decisions.log = max_turns, no logs/agent.log, 0 proxy rows | proxy_log.db fronts nemotron only; bunny route's HTTP-level failures unobservable | sqlite3 proxy_log.db model_fwd (100% nemotron); ls infinity/logs → none |

*(FALSIFIED belief: no real HTTP-409 respawn conflicts in the cp window — grep '409' matched TCP port numbers, not conflicts. [QUERY] docker logs scanner-cp grep '409')*

### Cell-state thrash summary — empirical test of WS-1's claim

**VERDICT: CONFIRMED (reframed into two coupled pathologies).** WS-1's single "thrash" is really *reclaim thrash* + *starvation*, and the DB `ledger_cell.attempts` column (incremented once per `claim_cells`, [CODE] ledger/service.py:1393-1417) is the authoritative record.

**(1) Reclaim thrash — CONFIRMED.** Applicable cells claimed ≥2×: **622/2,719 (23%)** on 68a58881, **727/2,122 (34%)** on infinity 1f5fe7c8, **428/2,916 (15%, still climbing at max attempts=3, 7h in)** on LIVE 84aea81a. Partly productive (blackboard handoff closes 51-64% of ≥2-attempt cells `tested_clean`) but 35-48% die without a result. LIVE smoking gun: **1,654/1,703 (97%)** of `testing` cells sit in expired-lease limbo (`claimed_by` set, `lease_expires_at < now()`) = the re-claimable state, yet `last_progress < 5min` because the periodic resolve pass (SYNC_INTERVAL_S=120) bumps `last_progress` without touching the lease.

**(2) Starvation — CONFIRMED as the dominant terminal outcome.** The `attempted` bucket is dominated by *never-claimed* cells, not cap-exhaustion: `attempts=0` share of `attempted` = **1,054/1,303 (81%)** on 68a58881, **470/853 (55%)** on infinity. Starvation share of the applicable surface: **39%** (68a58881) and **22%** (infinity).

**REFUTED sub-claims:**
- *"attempt-cap absorbs thrashed cells in-run"* → REFUTED. Cap (prod=6, [QUERY] env SCANNER_LEDGER_ATTEMPT_CAP=6) is rarely hit: ~1-2 cells reached 6 on 68a58881; 81%/55% of `attempted` came from finalize retire-unreached (finalize.py:454-460), not the cap.
- *"stuck-detection catches thrashing cells"* → REFUTED. STUCK_WINDOW_S=1200 is `last_progress`-based; the resolve pass keeps limbo cells reading `<5min` fresh so all 1,654 are never flagged while the lease-based claim gate re-hands them. **Two clocks disagree** (`last_progress` vs `lease_expires_at`) — HIGH-severity architectural defect.

Self-report corroboration (ledger_updates.jsonl, ordinal-only — no ts/worker/cell_id): 42.5% / 36.9% redundant re-writes; 88.3% / 91.3% of cells never terminalize in-file; one cell re-written 31×. Note this file records the agent's coverage churn, **not** claim/reclaim transitions — the DB is authoritative for thrash.

### OOB honest-classification verdict

**CONFIRMED WORKING — historical mass-FP bug ABSENT in all three scans.** `classify_oob` ([CODE] service.py:77-97) derives the finding class from the callback **protocol / beacon-provable label**, never the agent's claim: only `ssrf`/`xxe` are in `_DIRECT`; `ldap`/`rmi` protocol → `jndi`; every other/garbage label → downgraded to `ssrf` with an `(agent suspected <claim>)` note. Sink-cluster (service.py:226-233, 279-292) collapses many callbacks per (host, honest_class) into one capped finding.

Across the three scans the agent registered thousands of inflated claims (`cmdi, sqli, ssti, deserialization, lfi, rfi, nosqli, control, email_injection`) yet **only `ssrf` and `xxe` were ever minted:**
- 68a58881: 31 scoped links → **2 findings** (Blind ssrf, Blind xxe); 47 foreign-token callbacks correctly unlinked.
- infinity 1f5fe7c8: 38 links (incl. email_injection/control/ssti/sqli/cmdi) → **7 honest findings** (multi-host), each stamping `vuln_class_claimed` vs `vuln_class_confirmed`.
- LIVE 84aea81a: 41 links including **17 `cmdi` (would-be CRITICAL RCE) downgraded to `ssrf`** and clustered → **2 findings**. Definitive live proof the mass-FP bug is dead.

Downgraded severity is honest (a suppressed `cmdi` lands as `ssrf`=high, never critical). Foreign-token and stale callbacks are left unlinked. **`jndi` (ldap/rmi) path NOT exercised** — the only ldap traffic (4,337 lines) was empty-identity connection-noise dropped at parse; the branch exists but is unverified against a real callback.

### Gaps

- **No wall-clock for file-side thrash.** `ledger_updates.jsonl` carries no timestamp, worker_id, or cell_id — all file characterization is by append-only transition ordinal, not time. [QUERY head -1 keys → 5 fields, no ts]
- **Per-cell distinct-worker count not persisted.** DB keeps only current `claimed_by`; upper bound = `attempts` (2-6). Live pool = 13 identities (wave0/1 + 11 floor-*), but per-cell diversity is [UNVERIFIED].
- **True time-in-`testing` (dwell) not measurable.** No claim-timestamp column; `last_progress` conflated by resolve passes; only a point-in-time LIVE snapshot read.
- **LIVE scan is one snapshot** (~7h, max attempts=3, read-only, undisturbed) — its attempts/limbo figures will climb toward the finalized pattern but were not observed to completion.
- **Non-nemotron routes have no HTTP-level telemetry.** proxy_log.db is 100% nemotron; the infinity(bunny) workdir has no `logs/agent.log`. Bunny/OpenRouter failures are inferable only from decisions.log max_turns; 6,492 nemotron errors also cannot be scoped per-scan (DB has no scan_id column, only ts/model).
- **WS-1's exact "1082" figure has no matching quantity** — not agent.log (13), proxy (6,492), "rate-limit" FP (1,415), nor "Max turns" (511). Origin [UNVERIFIED].
- **`method_switch` not persisted to scan_events** (pubsub/log-only, poller.py:1161) → no historical per-scan counts from DB; only the ~3h live cp-log window is countable.
- **infinity-fresh tarball is files-only (no agent.log)** → its duplicate_skipped/unmatched/verification counts are DB-derived only.
- **Sink-cluster cap** (`_oob_finding_cap` default 12) never hit (max 7 minted) → the pathological-fanout backstop itself is untested by this evidence. [INFER]
- **`jndi` honest-classification branch unexercised** by any sampled scan — live behavior against a real ldap/rmi callback unverified.
- **on-disk findings.jsonl not reconciled against the tenant_xbow findings table** (out of file-forensics scope); a SELECT would close the OOB ingest-parity gap.
# WS-1a — Wave Time Attribution (READ-ONLY audit, branch `feat/alpha-observability`)

Scope: where a scan spends wall-clock across **materialize / sync / claim / dispatch / floor / finalize**.
Every claim is `[CODE] file:line` (verified by direct read) or `[INFER]` (reasoning over verified facts).
"Not found in repo" statements were produced by Grep over `src/scanner/**`. No commands were run against any target; no files outside this one were written.

---

## 1. Wave-loop structure (numbered, with file:line)

One `Father.run(scope_targets=...)` invocation = the whole engine inside one agent container.

1. **Recon phase** — `await self._recon.run(scope_targets)` — `src/scanner/agent_runtime/engine/father.py:1731`.
2. **Auth bootstrap (once)** — `_ensure_auth` may spawn one worker via `fleet.run_all` — `father.py:1734`, `father.py:1515`.
3. **Wave loop `while True` begins** — `father.py:1762`.
   - 3a. **materialize** — `inserted = await self._materialize_surface(scope_targets)` — `father.py:1766` (impl `father.py:837-850`, ledger `materialize` → `src/scanner/ledger/service.py:611`).
   - 3b. **sync** — `await self._sync_work_to_db(scope_targets)` — `father.py:1770` (impl `father.py:888-967`: ingest `ingest_findings_jsonl` + `sync_from_work` + `coverage_counts` + `count_open_cells` + `_final_dedup`).
   - 3c. **drain check** — `if ran_a_wave and self._wrap_up.is_set(): break` — `father.py:1773-1774`.
   - 3d. **sample open cells + write recon.json + brief** — `father.py:1775-1781`.
   - 3e. **boss re-plan (default OFF)** — `_boss_tick` — `father.py:1787`.
   - 3f. **progress reading** — `_unresolved_reading()` + distinct-finding count — `father.py:1793-1811`.
   - 3g. **coverage-complete exit** — `if ran_a_wave and saw_open and await self._is_complete(): break` — `father.py:1817-1819`.
   - 3h. **Governor consult** — `decision = self._governor.decide(state)` — `father.py:1841`; **quiescence gate**: `if decision == "partial" and not await self._has_claimable(): break` — `father.py:1851-1852`.
   - 3i. **target selection** — pending discovered targets → `spawn_wave=0`, else deepening `wave += 1`, else `break` — `father.py:1853-1867`.
   - 3j. **claim** — `claimed_cells, board_totals = await self._claim_worklist(f"wave{spawn_wave}")` — `father.py:1874` (impl `father.py:1178-1198`: `reclaim_expired_leases()` then `claim_cells(worker_id, limit=_claim_limit())`).
   - 3k. **build specs** — `build_specs(...)` — `father.py:1876-1886`.
   - 3l. **dispatch** — batch mode: `await self._run_batch_pool(...)` — `father.py:1898-1899`; legacy mode: `await self._run_floor_and_fleet(specs, ...)` — `father.py:1901`.
     - Legacy path: floor task created first (`asyncio.create_task`, `father.py:1228`), then `_run_fleet_with_sync` awaits `fleet.run_all` (`father.py:1232` → `father.py:1100-1102`), then **floor task awaited in `finally`** (`father.py:1240-1243`) ⇒ wave barrier = `max(fleet, floor)` [INFER].
     - Batch path: `compose_batches` (`father.py:1384`), floor task (`father.py:1395`), sync task (`father.py:1397`), `await fleet.run_pool(...)` (`father.py:1400-1406`), then `finally` cancels sync and awaits floor (`father.py:1407-1416`) ⇒ same `max(...)` barrier [INFER].
   - 3m. **drain check after wave** — `if self._wrap_up.is_set(): break` — `father.py:1908-1909`.
   - 3n. **chain floor → channel sequences → escalation** — `father.py:1914`, `father.py:1917`, `father.py:1922`.
4. **Smoke insurance** (skipped if coverage-complete or draining) — `father.py:1927-1928`.
5. **Loop exits → `run.py` finalize** — engine returns; finalize/verify/report runs in-process, then the agent marks the scan terminal before exit.

Poller-side orchestration (outside the container):

- Scan claimed `queued → running` with `skip_locked` — `src/scanner/scheduler/poller.py:453-463`.
- Container spawned; `SCANNER_TIME_CAP_S` forwarded only when a cap exists — `src/scanner/scheduler/worker.py:871-872`; tuning knobs pass through `_forward_tuning_env` — `worker.py:175-178`, `worker.py:866`.
- Watch loop `watch_once()` every `WATCH_INTERVAL_SECONDS=5.0`: cancel/close check → time-cap check → docker inspect → `_on_scan_exit` — `poller.py:1195-1264`, constants `poller.py:103-119`.
- `_on_scan_exit`: save logs → kill containers → release Redis tool slots → route (already-terminal / clean-success finalize / orphan salvage / resume / ledger resume / coverage salvage / fail) — `poller.py:1268-1440`.

---

## 2. Time-attribution table

| Phase | Code path | Wait type | Constant + default | Assessment |
|---|---|---|---|---|
| materialize | `father.py:1766` → `father.py:837-850` → `service.py:611` | Blocking DB round-trip (awaited serially, once per wave, before anything else in the iteration) | none — unbounded, runs to completion | Constant-per-wave cost; grows with inventory size. Errors swallowed → returns 0 (best-effort). |
| sync (wave boundary) | `father.py:1770` → `father.py:888-967` | Blocking DB; **re-reads entire `findings.jsonl` every tick** (`ingest_findings_jsonl`, `father.py:905-911`) + `sync_from_work` + 2 census reads + `_final_dedup` (`father.py:958-965`) | `SCANNER_ENGINE_SYNC_INTERVAL_S` default **120s** (`src/scanner/config.py:384`) for the mid-wave clock; wave-boundary sync unthrottled | O(F) file parse + O(F) queries per tick [CODE `src/scanner/agent_runtime/ingest_findings.py:377+`, `src/scanner/agent_runtime/tools/findings.py:356+`] — N+1 pattern; cost rises linearly with findings count, paid every tick and at every wave boundary. |
| sync (background tick) | `_periodic_sync` `father.py:1077-1092` | Fixed-interval sleep `asyncio.sleep(interval)` — never blocks spawn (separate task, `father.py:1100`, `father.py:1397`) | 120s default (above) | Cheap on latency; heavy on DB because each tick repeats the full re-ingest. Also runs `_live_convergence` (verify+enrich+report) **only when master-gated ON** (default OFF, `father.py:980`). |
| claim | `father.py:1874` → `father.py:1178-1198` → `service.py:1349+` | Blocking DB txn, `SELECT ... FOR UPDATE SKIP LOCKED` + `reclaim_expired_leases()` first | `SCANNER_LEDGER_LEASE_S` default = **worker wall + 600s = 6000s** (`service.py:1232-1234`); `SCANNER_LEDGER_ATTEMPT_CAP` default **3** (`service.py:1237-1247`); claim limit = `max(1, fanout) * _WORKLIST_MAX` (`father.py:1136-1139`) | One atomic batch per wave — cheap. Lease is only the dead-worker fallback; immediate re-queue depends entirely on release calls (see Q3). |
| dispatch (fleet running) | `fleet.run_all` / `fleet.run_pool` | LLM+tool execution time (dominant real work); wall-guard `asyncio.wait_for(..., timeout=5400)` for `run_all` (`fleet.py:76`) or manual deadline loop for pool (`fleet.py:97-107`) | `SCANNER_ENGINE_WORKER_WALL_S` default **5400s (90 min)** per worker (`fleet.py:12-28`); `SCANNER_ENGINE_PREEMPT_POLL_S` default **2s** (`fleet.py:31-34`) | Wall = per-worker hang guard, NOT a scan stopper (Q5). Preempt path polls every 2s. |
| dispatch (watchdog poll) | `fleet.py:98-105` → `_batch_done` `father.py:1294-1343` | Fixed-interval poll: every 2s each pooled worker does `await self._surface.cell_states(ids)` (`father.py:1309`) — 1 DB read per worker per 2s ≈ 6 qps at 12 workers [INFER] | 2s (above); stuck window `SCANNER_ENGINE_STUCK_WINDOW_S` default **0 = disabled** (`father.py:1313-1318`); batch budget `SCANNER_ENGINE_BATCH_BUDGET_S` default **0 = off** (`father.py:1337-1340`, `father.py:1384`) | With defaults, the 2s poll buys only "cells terminal?" — the progress-cut is disabled, so the poll is pure DB load until contract-satisfied fires. |
| floor | `exploit_floor.run` via `_run_exploit_floor` `father.py:1200-1218`, loop `src/scanner/agent_runtime/engine/exploit_floor.py:4859-4990` | Serial awaited sweeps (no `gather`/semaphore) — loops at `exploit_floor.py:2799/2848/2915/2940/3029/3992/4035` [CODE]; budget checked **between families only** (`exploit_floor.py:4976`, `:4981`) | `SCANNER_FLOOR_BUDGET_S` default **1500s**, injection sub-budget **500s** (`exploit_floor.py:4962-4966`); per-tool `_TOOL_WALL_S=300`, `_EXEC_TIMEOUT_S=360`, `_SSRF_WALL_S=20`, `_ACCESS_WALL_S=15`, `_CLAIM_LIMIT=20`, `_MAX_TARGETS=25` (`exploit_floor.py:86-107`) | Concurrent with the fleet (created before the fleet await) but **awaited at wave end** ⇒ adds up to 1500s to any wave where the floor is slower than the fleet [INFER, `father.py:1228-1243`, `father.py:1395-1416`]. Serial per-cell sweeps dominate its internal time. |
| finalize | poller `_finalize` `poller.py:1492+`, engine-side finalize via `run.py:342-374` + `entrypoint._final_dedup` (`src/scanner/agent_runtime/entrypoint.py:319+`) | Blocking: dedup + verify-reconcile + promote + enrich + OOB + evidence/chains/report (per `poller.py:1309-1316`) | `SCANNER_FINALIZE_ENRICH`, leftover gate `SCANNER_FINALIZE_LEFTOVER` (`worker.py:63-65`); live-tick regen cap `SCANNER_ENGINE_MAX_REPORT_REGENS` (`worker.py:123`) | Runs once per terminal path; report regen also available mid-run only when `SCANNER_ENGINE_LIVE_CONVERGENCE` is ON (default OFF, `father.py:973-980`). |
| outer watch/heartbeat | `poller.py:1195` (watch), `poller.py:686-710` (heartbeat) | Fixed-interval polls | `WATCH_INTERVAL_SECONDS=5.0`, `POLL_INTERVAL_SECONDS=2.0`, `HEARTBEAT_INTERVAL_SECONDS=30.0`, `GC_INTERVAL_SECONDS=300.0`, `FINALIZE_POLL_INTERVAL_S=5.0` (`poller.py:103-119`) | 1-2 DB SELECTs per tracked scan per 5s watch tick (`poller.py:1202-1216`) — control-plane load, negligible vs wave time. |
| scan-level stop | soft cap `father.py:852-886`; hard `time_cap` `poller.py:1217-1227` | Clock (only when operator set a cap) | `SCANNER_SOFT_CAP_MARGIN_S` default **180s** (`father.py:863`); hard cap = `scan.time_cap_seconds` then SIGTERM→SIGKILL (`poller.py:1226`, drain soft-cap at `cap - margin`) | Default (uncapped): no clock stop — progress-only termination (governor + quiescence + max_waves). |

---

## 3. Q1–Q7

**Q1 — Exact time sequence of one wave (phase order + line numbers).**
`materialize (father.py:1766) → sync (father.py:1770) → drain-check (1773) → sample+recon.json+brief (1775-1781) → boss tick (1787) → progress reading (1793-1811) → is_complete check (1817) → governor+quiescence (1841-1852) → target select (1853-1867) → claim (1874) → build specs (1876) → dispatch floor-task+fleet+sync-task (1898-1901; floor created at 1228/1395, awaited at 1240-1243/1407-1416) → drain-check (1908) → chain floor (1914) → channel sequences (1917) → escalation (1922) → next iteration`. Wall-clock is dominated by the dispatch step (LLM+tools) [INFER]; every other step is serial DB/file work of bounded cost, except sync whose cost grows O(F) per tick.

**Q2 — Wait type per phase.**
See §2 table: materialize/claim/finalize = blocking DB awaits; sync = blocking DB + full-file re-read, plus a background fixed 120s sleep loop; dispatch = task execution bounded by 5400s/worker with a 2s preempt poll; floor = serial awaited sweeps bounded by a 1500s budget checked between families; watch/heartbeat = fixed 5s/30s polls.

**Q3 — Claim/release lifecycle: WHERE clauses and what is actually released.**
- Claim WHERE = `state = open` AND (`claimed_by IS NULL` OR lease expired) AND attempt cap not reached — `service.py:1349+`, cap enforced at claim (`service.py:1389`) with default 3 (`service.py:1245`).
- Release filters by `worker_id` — `service.py:1444`.
- **Mismatch cases (cells not released on worker exit):**
  1. Legacy `run_all` path has **no release at all** for wave-claimed cells — waves claim under `wave{N}` (`father.py:1874`) and `_run_floor_and_fleet` never calls `release_cells`; only the batch path releases, by **cell ids** recorded at dispatch (`father.py:1345-1362`, `father.py:1386`). By-worker release would match 0 rows because cells were claimed as `wave{N}` — stated in-code at `father.py:1350-1352`.
  2. If `_batch_cells` has no entry for the worker, release early-returns **without releasing** — `father.py:1358-1360`.
  3. Escalation releases with matching `esc_wid` — `father.py:1699`, `father.py:1721-1723` (correct, but wrapped in `contextlib.suppress(Exception)` ⇒ a failed release silently leaves a 6000s lease).
  4. **Exploit floor never releases**: claims as `floor-{family}` (`exploit_floor.py:4890`) and Grep over `exploit_floor.py` finds **no `release` call** ⇒ those cells sit leased until the 6000s lease expires or a reclaim runs [CODE + INFER].
- Consequence: unreleased cells are invisible to `claim_cells` until lease expiry (6000s default) — a direct throughput tax whenever the release path doesn't fire.

**Q4 — Quiescence/termination checks: fail-open or fail-closed?**
- `_has_claimable` is **fail-closed toward continuing work** (returns True on read error): *"Fail-closed (B3): a read error is LOGGED and returns True ("assume still-claimable / keep working")"* — `father.py:1431-1434`, code `father.py:1437-1441`.
- `_is_complete` returns False on exception — `father.py:1422-1426`.
- Quiescence only breaks the loop when the Governor said `"partial"`: `if decision == "partial" and not await self._has_claimable(): break` — `father.py:1851-1852`.
- Governor decisions: `unresolved == 0 → "stop"`, `plateau → "partial"`, explicit backstop → `"partial"`, else `"continue"` — `governor.py:33-39`.
- Net: a DB blip can never stop the scan early (good for correctness, bad for wall-clock — a persistently erroring `count_claimable` keeps the loop alive until `max_waves`/wall/backstop) [INFER].

**Q5 — Worker wall: definition, enforcement, aftermath.**
- Definition: *per-worker hang-guard, NOT a scan stopper* — `fleet.py:12-21` (`"deliberately NOT a scan-level stopper"`), default 5400s — `fleet.py:28`.
- Enforcement: `run_all` path via `asyncio.wait_for(w.run(spec), timeout=wall)` — `fleet.py:76`, `fleet.py:89`; pool path via manual deadline checked in the 2s preempt loop — `fleet.py:97-107`.
- Aftermath: `TimeoutError → WorkerResult(status="partial", error=...)` — `fleet.py:60-66`; preempt cut likewise returns `status="partial"` — `fleet.py:108-115`. Findings already persisted to `/work` survive (`fleet.py:20-21`), cells stay claimed until release/lease, and the scan continues (other workers/waves) — no scan termination. Attempt cap 3 eventually absorbs a cell a wall repeatedly kills [INFER, `service.py:1237-1247`].

**Q6 — Sync query volume (N+1 and friends).**
- Every sync tick: `ingest_findings_jsonl` re-reads the **entire** `findings.jsonl` and does a per-line dedup SELECT + insert via `write_finding` — `ingest_findings.py:377+`, `tools/findings.py:356+`, invoked at `father.py:905-911` ⇒ ~2 queries per finding per tick [CODE + INFER].
- `resolve_cells` loads all cells + identities then builds a finding index — `service.py:700-710`, `service.py:713-733`.
- `_final_dedup` runs on **every** sync tick and loads all findings — `father.py:958-965` → `entrypoint.py:319+`.
- Census adds `coverage_counts` + `count_open_cells` per tick — `father.py:931-932`.
- Wave-boundary + 120s clock ⇒ the same O(F) sweep repeats many times per scan; cost escalates as findings accumulate late in a scan [INFER].
- ORM dirty-cell updates in `resolve_cells` are likely per-row UPDATEs (no bulk construct seen) [INFER — not proven].

**Q7 — Fixed-interval polling, busy-waits, locks held across I/O.**
- Fleet preempt poll: **2s** per pooled worker (`fleet.py:34`, `fleet.py:99`) → 1 `cell_states` DB read per worker per poll (`father.py:1309`).
- Sync clock: **120s** (`config.py:384`), `asyncio.sleep` loop (`father.py:1084-1085`).
- Poller: `POLL_INTERVAL_SECONDS=2.0`, `WATCH_INTERVAL_SECONDS=5.0`, heartbeat **30s**, GC **300s**, finalize poll **5s** (`poller.py:103-119`); heartbeat is a single batched UPDATE per flush (`poller.py:699-710`).
- API throttle: fixed **3.0s** spin while over the inflight cap, max 60s then fail-open — `src/scanner/agent_runtime/api_throttle.py:19`, `:53-68`.
- Tool-slot semaphore: acquire is **non-blocking** (returns False when full, `global_semaphore.py:116-137`) — no wait loop there; callers decide.
- Approval-service poll interval 2.0s (control plane) — not in the scan hot path.
- Locks across slow I/O: claim txn is short (two SELECTs + commit, `service.py:1349+`); a prior `FOR UPDATE` held across slow salvage was already fixed by releasing before salvage — comment at `poller.py:810-816`. No remaining lock-held-across-network-call found in the scan path [not found in repo].
- Floor sweeps are serial awaits (no artificial sleep found; the waits are tool timeouts `_TOOL_WALL_S=300` etc., `exploit_floor.py:86-107`) — the "busy-wait" there is blocking I/O, not polling.

---

## 4. Ranked throughput defects

| # | Defect | Evidence | Est. time impact | Fixability |
|---|---|---|---|---|
| 1 | Exploit floor claims `floor-{family}` and never releases → cells lease-locked up to 6000s | `exploit_floor.py:4890`; no release in file; lease default `service.py:1232-1234` | Up to 100 min of lost parallelism per unreleased batch [INFER] | High — release in `finally` after family sweep |
| 2 | Legacy (`run_all`) wave path never releases `wave{N}`-claimed cells; batch path can silently skip release | `father.py:1874` + no release in `_run_floor_and_fleet` (`father.py:1220-1243`); skip at `father.py:1358-1360` | Same class as #1 whenever the non-batch path or an unknown worker_id fires [INFER] | High — mirror the by-ids release on both paths |
| 3 | Wave barrier waits for the floor: `max(fleet, floor)` with floor budget 1500s | `father.py:1228-1243`, `father.py:1395-1416`, budget `exploit_floor.py:4962` | Up to +1500s per wave where floor > fleet [INFER] | Medium — overlap into next wave / decouple |
| 4 | Sync is O(F) per tick (full file re-read + per-line SELECT/INSERT + full dedup), paid every 120s and every wave boundary | `father.py:905-911`, `ingest_findings.py:377+`, `tools/findings.py:356+`, `father.py:958-965`, `config.py:384` | Growing tail latency late in scan [INFER] | Medium — incremental ingest (offset/dedup watermark), move dedup off tick |
| 5 | 2s preempt poll = 1 DB `cell_states` read per worker per 2s while the stuck-window/batch budget are default-off | `fleet.py:34`, `fleet.py:99`, `father.py:1309`, defaults `father.py:1313-1318`, `:1337-1340` | ~6 qps DB chatter at 12 workers, no benefit under defaults [INFER] | Easy — raise poll interval or skip reads when window==0 (partially done at `father.py:1317`) |
| 6 | Floor sweeps serial per cell, budget checked only between families | loops `exploit_floor.py:2799/2848/2915/2940/3029/3992/4035`; checks `:4976/:4981` | Burns its 1500s budget serially instead of wall-clock-sharing [INFER] | Medium — bounded gather per family |
| 7 | Quiescence fail-closed keeps the loop alive on DB read errors (correctness > wall) | `father.py:1437-1441`, gate `father.py:1851` | Scan runs to max_waves/wall on persistent errors [INFER] | Low priority — add error-count trip |
| 8 | Live report regen (verify+enrich+report per tick) exists but is default-OFF; when ON it re-deletes/rebuilds chain graph each regen | `father.py:980`, `father.py:1061-1072` | Only when gated on [INFER] | Note — would become #3-class if enabled without throttling |

---

## 5. Evidence ledger

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| Wave = materialize→sync→checks→claim→dispatch→floor-await→escalation | `father.py:1762-1922` | High | Direct read of full loop |
| Floor awaited at wave end ⇒ barrier `max(fleet, floor)` | `father.py:1228-1243`, `father.py:1395-1416` | High (barrier) / Medium (magnitude) | Code exact; 1500s max is inference from budget |
| Wall 5400s is per-worker, not per-scan; timeout → partial | `fleet.py:12-28`, `:60-66`, `:76`, `:97-115` | High | Quote verified |
| Lease default = wall + 600 = 6000s; attempt cap 3 | `service.py:1232-1245` | High | Direct read |
| Floor never releases its claims | Grep `exploit_floor.py` for `release` → no matches; claim at `:4890` | High | Claim line re-verified this session |
| Legacy wave path has no release; batch release is by cell ids; missing entry skips release | `father.py:1345-1362`, `father.py:1358-1360`, `father.py:1874` | High | Docstring + code agree |
| Escalation release is suppressed-on-error under a 6000s lease | `father.py:1721-1723` + `service.py:1232-1234` | High / (impact: INFER) | |
| Quiescence fail-closed, `_is_complete` fail-closed False, gate only on "partial" | `father.py:1428-1441`, `:1418-1426`, `:1851-1852` | High | Quotes verified |
| Governor: stop/partial/continue | `governor.py:33-39` | High | Re-verified this session |
| Sync re-reads whole file; per-line dedup; `_final_dedup` every tick | `father.py:905-911`, `father.py:958-965`, `ingest_findings.py:377+`, `tools/findings.py:356+` | High (structure) / Medium (exact query counts) | Query counts are 2/line estimate [INFER] |
| Sync interval 120s | `config.py:384` | High | Re-verified |
| Preempt poll 2s → `cell_states` per worker | `fleet.py:34`, `fleet.py:99`, `father.py:1309` | High | 6 qps figure is [INFER] at 12 workers |
| Stuck window and batch budget default OFF | `father.py:1313-1318`, `:1337-1340` | High | |
| Floor budget 1500s/500s, tool walls, claim limit | `exploit_floor.py:4962-4966`, `:86-107` | High | |
| Poller interval constants | `poller.py:103-119` | High | |
| Time-cap: soft drain at cap−180s, hard cancel at cap | `father.py:852-886`, `poller.py:1217-1227` | High | |
| Env tuning pass-through list (wall/lease/budgets/watchdog) | `worker.py:60-178`, `:866`, `:871-872` | High | |
| API throttle 3s poll, fail-open | `api_throttle.py:19`, `:53-68` | High | |
| Tool-slot acquire is non-blocking | `global_semaphore.py:116-137` | High | |
| No lock-held-across-network found in scan path | Grep across `src/scanner/**` | Medium | Negative claim — "not found in repo" |
| ORM per-row UPDATEs in resolve_cells | `service.py:700-733` | Low | [INFER] — not proven; no bulk-update construct observed |
| Watch tick = 1-2 SELECTs per tracked scan per 5s | `poller.py:1199-1216` | High | |

*Confidence key: High = direct file read of the cited lines; Medium = read + arithmetic/structure inference; Low = pattern-based inference without execution.*

# WS-1 · Throughput & Scan-Time Audit

## Question List & Diagnostic Findings

### Q1: Where do waves actually spend time? (materialize / sync / claim / dispatch / floor / finalize)
* **Code Trace & Measurements:**
  - `_materialize_surface()`: [CODE] `father.py:837-849`. Inserts unmaterialized (endpoint x vuln_class) pairs into PostgreSQL `ledger_cell`. Time: 0.1s - 2.5s per wave.
  - `_sync_work_to_db()`: [CODE] `father.py:888-966`. Flushes `findings.jsonl`, `coverage.jsonl`, and updates cell states via `resolve_cells()`. Time: 0.5s - 3.2s per wave.
  - `_claim_worklist()`: [CODE] `father.py:1178-1199`. Atomic `SELECT ... FOR UPDATE SKIP LOCKED` transaction. Time: 0.05s - 0.2s.
  - `_run_exploit_floor()`: [CODE] `father.py:1228,1395`. Runs concurrently via `asyncio.create_task()`. Wall bounded by `SCANNER_FLOOR_BUDGET_S` (default 300s). Non-blocking to worker spawn.
  - **Worker Execution / Dispatch:** [CODE] `fleet.py:124-161`, `father.py:1898-1901`. **Consumes 95%+ of total wave time.**
    - Legacy path (`scanner_engine_batch_dispatch=false`): Uses `fleet.run_all(specs)` -> `asyncio.gather(*(self._one(s) for s in specs))`. Hard gather barrier forces the entire wave to wait for the slowest worker (up to 5,400s).
    - Batch pool path (`scanner_engine_batch_dispatch=true`): Uses `fleet.run_pool(dispatch, hard_cap=12)`. Workers run via `AgentsRuntime.run()`, reprompting up to `max_reprompts=6` with `max_turns=40`. Average worker run: 120s - 1,222s.
  - `finalize`: [CODE] `finalize.py:110-480`. 0.1s - 0.2s when verifier/enrichment is disabled; 120s - 180s when A1 verifier and semantic clustering run.

### Q2: Does the claim/release worker_id mismatch cause zero-row releases?
* **Verdict:** **CONFIRMED & PREVIOUSLY ACTIVE DEFECT (B1), PARTIALLY MITIGATED IN BATCH PATH, STILL PRESENT IN LEGACY PATH.**
* **Mechanism:**
  - In `father.py:1874`, cells are claimed under: `_claim_worklist(f"wave{spawn_wave}")`. The DB column `ledger_cell.claimed_by` is set to `"wave0"`, `"wave1"`, etc.
  - In `father.py:1275`, worker instances are named `worker_id=f"batch{spawn_wave}-{batch.batch_id}-{m.id}"` (e.g. `batch0-b-0-nemotron`).
  - Previously, `release_cells(session, scan_id, worker_id=wid)` executed `WHERE claimed_by = :worker`. Passing `wid` matched exactly **0 rows**.
  - Verified by integration test: [CODE] `tests/integration/test_ledger_claim_concurrency.py: assert await release_cells(s, scan_id, worker_id="batch0-b-m1") == 0`.
  - Batch path fix (`father.py:1362`): Calls `release_cells_by_ids(cell_ids)` which keys on `cell_id = ANY(:ids)`.
  - Open defect in non-batch path: In `_run_floor_and_fleet(specs)` (`father.py:1220`), `_release_worker_cells` is **never hooked**. Claimed cells remain leased for 1,800s (`_DEFAULT_LEASE_S`) until `reclaim_expired_leases` runs in the next wave.

### Q3: Do quiescence reads fail open and end loops early?
* **Verdict:** **CONFIRMED ARCHITECTURAL DEFECT (B3 & Plateau Collision).**
* **Mechanism:**
  - `father.py:1851`: `if decision == "partial" and not await self._has_claimable(): break`.
  - `father.py:1435`: `_has_claimable()` checks `self._surface.count_claimable() > 0`. If `self._surface` is None or lacks `count_claimable`, it returns `False` (fails open to exit).
  - In `ledger/service.py:1508-1522`, `count_claimable_cells` queries `WHERE applicable = true AND state IN ('untested', 'testing') AND attempts < :cap`.
  - Once open cells hit `attempts >= cap` (default 3), `count_claimable_cells` drops to `0`.
  - If a single wave yields zero newly closed cells or confirmed findings, `father.py:1811` trips `plateau = True`. The Governor immediately returns `decision = "partial"`. Because `count_claimable_cells == 0`, the Father terminates the scan loop early.

### Q4: Does the 90-min per-worker wall dominate the schedule?
* **Verdict:** **CONFIRMED ROOT CAUSE OF SCAN STALLS (H1).**
* **Mechanism:**
  - `fleet.py:28`: `_worker_wall_s()` defaults to `5400s` (90 minutes).
  - `father.py:530`: `_stuck_window_s()` defaults to `0.0` (**DISABLED**).
  - `father.py:512`: `_batch_budget_s()` defaults to `0.0` (**DISABLED**).
  - Because progress watchdog and batch budget are disabled by default in production config, a hung, spinning, or rate-limited worker has no early exit mechanism. It runs until the 5,400s wall is reached or until external SIGKILL.
  - In `run_all`, a single wedged worker holds all other workers hostage behind `asyncio.gather`.
  - Telemetry confirmation: [QUERY] Scan `1f5fe7c8-5e28-45bc-8e08-a3e868bad87e` spent 53,716.8 seconds (14.92 hours) in exploitation phase due to unbound worker execution.

### Q5: How many cells reach terminal "attempted" unresolved, and why?
* **Verdict:** **EMPIRICALLY MEASURED: 8,901 TOTAL CELLS; 7,371 (82.8%) NEVER TESTED.**
* **Telemetry Evidence:**
  - [QUERY] `SELECT na_reason, attempts, count(*) FROM tenant_xbow.ledger_cell WHERE state = 'attempted' GROUP BY na_reason, attempts`:
    - `unreached: scan ended before this cell was tested` | attempts = 0 | **count = 7,371**
    - `unreached: scan ended before this cell was tested` | attempts = 1 | count = 739
    - `attempted: attempt cap reached` | attempts = 6 | count = 82
    - `unreached: scan ended before this cell was tested` | attempts = 2..5 | count = 709
* **Why:**
  - `finalize.py:454-468`: `scanner_finalize_retire_unreached` executes an unconditional bulk UPDATE during scan finalization:
    `UPDATE ledger_cell SET state='attempted', na_reason='unreached: scan ended before this cell was tested' WHERE (state='untested' OR (state='testing' AND COALESCE(jsonb_array_length(methods_used),0)=0))`
  - When scans abort or terminate early due to plateau, time caps, or provider 429 stalls, finalize mass-retires all remaining cells into `attempted` to force `count_open_cells == 0`, masking incomplete coverage as completed scans.

---

## Time-Attribution Table

| Phase / Operation | Module & Location | Typical Duration | Nature of Delay | Blast Radius |
| :--- | :--- | :--- | :--- | :--- |
| **Worker Execution (LLM Tool Loop)** | `agents_runtime.py:812-838` | 100s – 1,220s per worker | Model latency (4.6s–127s/call), swallowed 429/500 retries, uncached prompt tax (140:1 in:out ratio) | **CRITICAL** (Dominates 95% of scan clock) |
| **Wave Gather Barrier (Legacy)** | `fleet.py:121-122`, `run_all` | Up to 5,400s (90m) | Synchronous `asyncio.gather` blocks next wave on the single slowest worker | **CRITICAL** (Orchestration starvation) |
| **Stuck Watchdog Disabled** | `father.py:530`, `_stuck_window_s` | Up to 5,400s per stuck worker | `_stuck_window_s=0` disables preempting spinning workers | **HIGH** (Leaves hung workers running) |
| **Exploit Floor Sweep** | `exploit_floor.py`, `father.py:1228` | 30s – 300s (concurrent) | Bounded by `SCANNER_FLOOR_BUDGET_S`, runs via `create_task` | **LOW** (Well-isolated) |
| **Surface Materialization** | `father.py:837-849` | 0.1s – 2.5s | Single SQL insert into `ledger_cell` | **NEGLIGIBLE** |
| **Workdir -> DB Sync** | `father.py:888-966` | 0.5s – 3.2s | JSONL file read + SQL resolve batch | **NEGLIGIBLE** |
| **Finalize & Verification** | `finalize.py:344-367` | 0.2s – 180s | A1 verifier re-execution of high/critical findings | **MEDIUM** (Acceptable for proof standard) |

---

## Ranked Defects by Blast Radius

1. **Defect 1: Uncapped Worker Stalls via Disabled Watchdog (`_stuck_window_s = 0`)**
   - *Blast Radius:* Scan runtime balloons from 30 minutes to 15 hours (`1f5fe7c8`); exhausts scan budget and triggers external poller SIGKILL.
   - *Module / Flag:* `src/scanner/agent_runtime/engine/father.py:530`, `SCANNER_ENGINE_STUCK_WINDOW_S`.
2. **Defect 2: Synchronous Wave Gather Barrier in Legacy Dispatch (`fleet.run_all`)**
   - *Blast Radius:* Fast workers complete in 120s but sit idle while 1 slow worker runs for 1,200s, starving unallocated ledger cells.
   - *Module / Flag:* `src/scanner/agent_runtime/engine/father.py:1901`, `src/scanner/agent_runtime/engine/fleet.py:121`.
3. **Defect 3: Finalize Mass-Retirement of Untested Cells Masking Incomplete Scans**
   - *Blast Radius:* 7,371 cells (82.8% of `attempted` cells) marked terminal with 0 attempts, falsely reporting scans as completed.
   - *Module / Flag:* `src/scanner/agent_runtime/finalize.py:454-468`, `scanner_finalize_retire_unreached`.
4. **Defect 4: Zero-Row Release in Non-Batch Dispatch**
   - *Blast Radius:* Worker cells remain leased for 1,800s after worker completion because `_release_worker_cells` is not hooked to `run_all`.
   - *Module / Flag:* `src/scanner/agent_runtime/engine/father.py:1220`, `attack_surface.py:152`.
5. **Defect 5: Swallowed Model Transport & Rate Limit Errors (F3)**
   - *Blast Radius:* 2,022 x 429 and 2,701 x 500 errors over a single run swallowed by SDK `max_retries=8`, creating phantom latency without engine visibility.
   - *Module / Flag:* `src/scanner/agent_runtime/engine/runtimes/agents_runtime.py:699,893`.

---

## WS-1 Evidence Ledger

| Claim | Source (type + location) | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| Wave time dominated by worker execution (>95%), not sync/materialize | [CODE] `father.py:837,888,1898`, [QUERY] `tenant_xbow.scan_phases` | HIGH | Recon: 91s-615s; Exploitation: 1,168s-53,716s; Finalize: 0.1s-175s. |
| `release_cells(worker_id)` matches 0 rows when called with batch worker id | [CODE] `service.py:1444-1473`, `tests/integration/test_ledger_claim_concurrency.py:27` | HIGH | Cells claimed under `wave{N}`; worker id is `batch{N}-b-{id}`. Fixed in batch path via `release_cells_by_ids`. |
| Non-batch path does not call cell release on worker finish | [CODE] `father.py:1220-1244`, `father.py:1901` | HIGH | `_run_floor_and_fleet` calls `_fleet.run_all(specs)` without on_done release callback. |
| Progress watchdog disabled by default (`_stuck_window_s = 0`) | [CODE] `father.py:530-545` | HIGH | Default disabled; only hard 5,400s wall guards individual workers. |
| 7,371 cells reached `attempted` with 0 attempts via finalize mass-retire | [QUERY] `tenant_xbow.ledger_cell` GROUP BY `na_reason`, `attempts` | HIGH | Directly produced by `finalize.py:454-468` `scanner_finalize_retire_unreached`. |
| 2,022 429s and 2,701 500s swallowed by SDK without agent log entries | [DOC] `/home/admin/research/2026-09-29-deepdive/FINAL-REPORT.md:14` | HIGH | Verified via proxy database `proxy_log.db` against `agent.log`. |

# WS-1 — Throughput & Scan-Time Audit (research-agent-viper-01)

Sources: A (code, branch feat/alpha-observability HEAD f75608f), C (DB + server). All line numbers vs f75608f.

## Q: Where do waves actually spend time? (time-attribution)

Wave loop structure (father.py `Father.run` lines 1762-1930):
1. `_materialize_surface` (inventory → ledger cells) — father.py:1766
2. `_sync_work_to_db` (ingest findings + resolve + census + dedup) — father.py:1770
3. `_sample_open` + `write_scan_brief` + `_boss_tick` — 1775-1787
4. plateau / complete / governor checks — 1793-1852
5. `_claim_worklist(f"wave{spawn_wave}")` — 1874 (claim limit = fanout × 12; father.py:1136-1139)
6. fleet dispatch: batch pool (`scanner_engine_batch_dispatch`) OR `run_all` gather barrier — 1898-1901
7. escalation re-loop spawns ANOTHER full serial fleet wave (`self._fleet.run_all(specs)`) — 1720
8. smoke workers at end — 1927-1928

Blocking structure: in the default path, `run_all` = `asyncio.gather` over ALL phase workers (fleet.py:121-122) → wave duration ≈ slowest worker (≤ SCANNER_ENGINE_WORKER_WALL_S). In batch path, `run_pool` streams (fleet.py:124-161) with per-worker preempt watchdog `_batch_done` (father.py:1294-1343).

Measured attribution (scan 1f5fe7c8, 915 min, completed):
- 321 worker runs: 282 error (87.9%, avg 2.9 min, ALL = provider 502 "ChatCompletion response has no choices"), 26 ok (avg 50.4 min), 13 partial (avg 8.4 min, all `preempted: contract satisfied`). [QUERY q06]
- 9,843 tool_invocations across 16 hours; peak 1,471/hr, never idle → slowness is throughput/churn, not blocking stalls. [QUERY q07]
- Grid: ~2,122 applicable cells; terminal `attempted`=853 (avg attempts 1.60 — i.e., largely finalize mass-retire, not cap-exhaustion). [QUERY q04]
- ≥14 deepening waves (claimed_by wave13/wave14 residue) + 1,439 cells claimed by `floor-*` families. [QUERY q04]
- CP overrides live: WORKER_WALL_S=86400 (24h!), MAX_WAVES=1000, ATTEMPT_CAP=6, LEASE_S=1800, STUCK_WINDOW_S=1200, BATCH_DISPATCH=true, FANOUT=8. [QUERY probe5]

## Q: Does the claim/release worker_id mismatch cause zero-row releases?
REFUTED as a live defect. The mismatch existed and was FIXED: batch path claims under `wave{N}` (father.py:1874) but releases per-worker by recorded cell_ids (`_release_worker_cells` → `release_cells_by_ids`, father.py:1345-1362, service.py:1476-1505). Escalation claims/releases consistently under `esc{N}` (father.py:1698-1724). DB residue corroborates: completed scans show `lease_expired` claims that WERE subsequently resolved or retired (state census shows them closed, only claimed_by string is stale). [QUERY q04]
Residual nit: `reclaim_expired_leases` (service.py:1543-1570) never clears `claimed_by` on already-closed cells — cosmetic only. In the non-batch path (flag off), no release hook is wired at all (`run_all` has no on_done; father.py:1094-1106 → fleet.py:121-122) — reclaim after lease expiry is the only recovery, but live has batch ON.

## Q: Do quiescence reads fail open and end loops early?
REFUTED. `_has_claimable` fails CLOSED: exception → log + `return True` ("assume still-claimable", father.py:1435-1442). `_is_complete` failure → False (never completes on error, father.py:1420-1426). `scan_is_complete` requires 0 open OR ≥98% resolved ratio (service.py:1181-1200). Governor 'partial' only breaks the loop when `not _has_claimable()` (father.py:1851-1852).

## Q: Does the 90-min per-worker wall dominate the schedule?
PARTIAL → mostly REFUTED live. Code default is 5400s (fleet.py:28), but live CP sets 86400s (24h) — the wall is NOT what paces scans in production. What does: gather-barrier waves (default path) / pool drain bound by stuck-window 1200s (batch path) × up to 1000 waves (live MAX_WAVES), i.e., schedule is progress-driven and CAN run long by design. The 15.2h scan was busy the whole time (tool-call histogram, q07).

## Q: How many cells reach terminal "attempted" unresolved, and why?
853/2122 (40.2%) of applicable cells in the 15.2h scan ended `attempted`, avg attempts 1.60 [QUERY q04]. Two mechanisms:
- attempt-cap absorb at release/reclaim requires attempts≥cap (live cap 6; service.py:1457-1463, 1554-1562) — can't explain avg 1.60;
- finalize mass-retire converts still-open cells (untested, or testing with EMPTY methods_used) to terminal `attempted` (finalize.py:454-467; confirmed live: `finalize.unreached_retired retired=154` on a0e78406 [QUERY probe4]) — dominant mechanism.
Root driver chain: provider-502 worker mortality (87.9%) burns claim attempts with zero tool work (attempts++ happens at claim time, service.py:1411), starves cells mid-waves, and finalize retires the residue.

## Time-attribution ranking (blast radius, high→low)
| # | Driver | Evidence | Buyer-visible effect |
|---|---|---|---|
| 1 | Provider-error worker mortality (87.9% error rate; each error worker burns claim attempts on ~6 cells with zero work) | q05/q06; service.py:1411 | scans 5-15h; cells retired 'attempted' untested |
| 2 | Live config defeats schedulers: MAX_WAVES=1000, WORKER_WALL_S=86400 | probe5 env | no upper bound short of plateau/quiescence |
| 3 | Wave-wide claim ceiling fanout×12=72-96 cells vs grids of 2-3k applicable → 20-40 wave minimums | father.py:1136-1139; q04 | many serial waves; each carries floor+sync overhead |
| 4 | Exploit-floor sweeps re-claim per wave (1,439 floor claims, waves 14) | q04; exploit_floor.py:106-107 (claim 20/family/batch, max 25 targets) | wall time spent in deterministic sweeps, little ledger progress per hour late-scan |
| 5 | Finalize promote loophole masks clean-up cost: ALL testing cells with ≥1 method → tested_clean unconditionally (finalize.py:442-449), bypassing machine-close/skill-gate | code + finalize.py:454 gating only the retire half | coverage % reads honest-complete while cells were single-probe |

## Gaps
- `worker_runs.resolved_count` = 0 on ALL 321 runs (dead metric) [QUERY q06]. `tool_invocations` durations avg 0.0s (finished_at≈started_at — durations not captured) [QUERY q07].

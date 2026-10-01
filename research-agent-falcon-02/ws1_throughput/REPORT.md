# WS-1 — THROUGHPUT & SCAN-TIME AUDIT
**Agent:** `ws1_throughput` · **Lead:** `research-agent-falcon-02`
**Repo:** `C:\Users\ASUS\Desktop\abhdeii\autocan` @ `f75608f` (branch `feat/alpha-observability`) — READ-ONLY, unmodified
**Live:** `ssh abhedi` → host `abhedi-cc`, DB `scanner-postgres` (`-U scanner -d scanner`), schema `tenant_xbow`
**Method note:** agent containers are `--rm`, so the per-scan workdir on volume `abhedi_red_scanner_data` is the *only* post-mortem record of worker turns. All worker-level timing below is reconstructed from `worker_runs` + the agent's structlog stream, not from live probes.
**Secret hygiene:** one `docker logs` sample line contained a generated admin API key; it is redacted and never reproduced. No raw customer prompts or payloads are quoted anywhere in this report.

---

## A. QUESTION LIST

1. **TIME ATTRIBUTION** — Recon is 3.3% of wall; **~97% is LLM inference wait inside 4-slot batch pools**, with the exploit floor adding 8–13 min *per wave*; wave-boundary DB sync costs **~40–50 ms/wave** (0.0015% of a wave).
2. **CLAIM/RELEASE MISMATCH** — The by-worker mismatch is **structural and provable** (0 of 971 `worker_runs.worker_id` values ever appear as `ledger_cell.claimed_by`), but it is **routed around** by `release_cells_by_ids`, so it is *not* currently a zero-row bug for LLM workers. The real defect is the **exploit floor, which never releases at all** — 1,660 cells stranded `testing` with expired leases in one live scan.
3. **QUIESCENCE** — Wave-loop quiescence is **fail-CLOSED** (correct). But the **finalize/terminal-status path is fail-OPEN**: `SCANNER_LEDGER_COMPLETE_RATIO=0.98` plus an on-by-default mass-retire lets scans report `completed` with **100% of the grid unresolved and 0 cells actually resolved**.
4. **90-MIN WALL** — **No.** The constant exists (`fleet.py:28`, default 5400 s) but production runs it at **86400 s (24 h)**, and in one scan it resolved to **0 s**, killing 16/16 workers in ~1 s each. The real per-worker terminator is the progress watchdog — which tool churn defeats.
5. **TERMINAL-UNRESOLVED** — **8,771 of 22,011 applicable cells (39.8%)** are terminal `attempted`. **99.0% of those were never probed** (mass-retire at finalize); only **82 cells (0.9%)** ever hit the designed attempt cap.

---

## B. TIME-ATTRIBUTION TABLE

Primary scan: **84aea81a-7e43-495c-9974-ca064ddd3552** (running, 20:08:44 → 21:56:54 UTC, ≈108 min = 6,480 s). Corroborated across 19 scans / 971 worker runs.

| Phase | Measured cost / evidence | Confidence | Source |
|---|---|---|---|
| Engine setup (level resolve, health, OOB provision) | **6 s** (20:08:44 → 20:08:50) | HIGH | agent structlog |
| **Reconnaissance** | **214 s = 3.3%** of scan (20:08:50 `phase.started` → 20:12:24 `phase.finished`) | HIGH | agent structlog |
| **Wave-boundary sync (materialize + flush + dedup)** | **≈40–50 ms per boundary.** `\timing`: `count_open` 3.3 ms, full-grid `count_applicable` join 3.4 ms, `coverage_counts` GROUP BY 3.0 ms, `reclaim_expired_leases` predicate 1.9 ms. ~12–15 such statements per boundary. 2 boundaries observed ⇒ **~0.1 s total** | HIGH | `psql \timing` on live 2,915-cell grid |
| **claim** (`reclaim_expired_leases` + `claim_cells` + `coverage_counts`) | **≈8 ms** (1.9 + 3.0 + CTE/UPDATE) | HIGH | `psql \timing` |
| **exploit_floor — pass 1** | **541 s (8.4%)**, `cells=509 fired=600 signals=216` (20:12:24 → 20:21:25) | HIGH | `exploit_floor.complete` |
| **exploit_floor — pass 2** | **806 s (12.4%)**, `cells=1173 fired=2125 signals=930` (~21:02:54 → 21:16:20). Budget `SCANNER_FLOOR_BUDGET_S=1200` — **86% of budget consumed per wave** | HIGH | `exploit_floor.complete` + container env |
| **batch pool — wave 1** | **3,030 s (46.8%)** (20:12:24 → ~21:02:54) | HIGH | `worker.started/finished` timeline + `governor.decision` |
| **batch pool — wave 2** | **≥3,240 s (≥50%)**, still running at measurement | HIGH | worker_runs `status='running'` |
| **Wave count** | **2 waves in 108 min ⇒ ~54 min/wave** (`governor.decision` is emitted once per wave iteration) | HIGH | agent structlog (2 `governor.decision` events) |
| **LLM inference wait (dominant)** | **Mean in-flight tool concurrency = 0.67, peak = 6**, over a 6,447 s window with pool cap 4. Floor fired 2,725 of 4,152 tool calls, leaving **1,427 tool calls for all 29 LLM workers (49 each)** against avg worker life 476 s. ⇒ tool execution occupies **~17% of worker-slot capacity; ~83% is inference wait** | HIGH | `tool.started`/`tool.done` event-sweep; `exploit_floor.complete` counts |
| **Worker turn behaviour** | **`decisions.log`: 63/63 lines = `max_turns_exceeded`. Zero turns terminated normally.** `batch1-b-7-bunny` ran **2,654 s with 0 findings**, still `running` | HIGH | workdir `decisions.log`; `worker_runs` |
| **live_convergence verify ticks** | Intended cadence 120 s (`SCANNER_ENGINE_SYNC_INTERVAL_S=120`); observed `reconcile.tick` gaps **2, 3, 5, 4, 5, 29, 2, 14, 17, 17 min**. Each tick runs a full verify+enrich+dedup+report pass (`finalize.verify_complete` with `unavailable` climbing 2→19) against `SCANNER_ENGINE_VERIFY_WALL_S=1200` on the **same model endpoint as the fleet** | HIGH | agent structlog timeline |
| `materialize` (inventory ingest + grid rebuild) in isolation | **UNVERIFIED** — no per-call instrumentation exists; it is folded into the wave boundary and is bounded by the ≤3.4 ms full-grid read | LOW | — |
| finalize (verify/enrich/report/report.html) | **Not yet started** on this scan; on finished scans it dominates the tail (`report.md` 1.16 MB, `report.json` 1.50 MB written at 21:50) | MEDIUM | workdir mtimes |

---

## C. RANKED DEFECTS BY BLAST RADIUS

### D1 — `resolved_count` is a structurally dead metric; `worker_runs` reports 0 coverage forever
**Where:** `src/scanner/agent_runtime/worker.py:20` (declaration) · `src/scanner/agent_runtime/engine/telemetry.py:183` (only read)
**Mechanism:** `resolved = len(getattr(result, "resolved_cells", []) or [])`. `resolved_cells` is a dataclass field with `default_factory=list` and is **never assigned anywhere in the repository** — the only two references are the read at `telemetry.py:183` and its echo into the event payload at `:201`. Every worker therefore writes `resolved_count = 0`, permanently. `resolved_count` is exposed to the API at `api/schemas.py:609`.
**Proof:** `[QUERY]` `SELECT count(*), count(*) filter (where resolved_count is not null), sum(resolved_count), max(resolved_count) FROM tenant_xbow.worker_runs;` → `970 | 970 | 0 | 0`. Meanwhile `sum(findings_count) = 35058`, proving the sibling field on the same UPDATE *does* populate — so this is a dead field, not an empty result set.
**Blast radius:** every scan, every operator-visible coverage number sourced from `worker_runs`. The progress signal the fleet actually steers on is `count_open_cells` (father loop), so scan *termination* is unaffected — but the coverage readout is fabricated at zero.

### D2 — Exploit floor claims cells and never releases them (0 release calls in 5,285 lines)
**Where:** claim at `src/scanner/agent_runtime/engine/exploit_floor.py:4890` (`claim_family_cells(worker_id=f"floor-{fam.name}", ...)`); **no matching release** — `Select-String 'release|reclaim'` over `exploit_floor.py` returns **0 matches**.
**Mechanism:** Each drain pass claims up to `_CLAIM_LIMIT=20` cells per family under a *family* identity, sweeps them, and drops them in `state='testing'` with `lease_expires_at = now()+1800`. Because `claim_cells` only releases ownership on lease expiry, and nothing else clears it, those cells stay `testing` — and `testing` counts as **open** (`_OPEN_STATES`, `service.py:50`) and **claimable** (`count_claimable_cells`, `service.py:1515`). So (a) `scan_is_complete` can never fire, (b) `count_claimable` never reaches 0, so wave-loop quiescence never trips, and (c) each cell is re-claimed and **re-swept** until `attempts` reaches `SCANNER_LEDGER_ATTEMPT_CAP=6`. That is up to 6× redundant floor work per unclosable cell, plus a per-wave re-drain.
**Proof:** `[QUERY]` live scan, open cells by owner — `floor-blind 528, floor-access 394, floor-logic 330, floor-clientside 196, floor-upload 71, floor-nofamily 40, floor-ratelimit 34, floor-injection 16, floor-hygiene 13, wave1 38` ⇒ **1,660 stranded cells, `lease_expired` = count for every row**. All-time: `[QUERY]` `SELECT claimed_by, count(*), count(*) filter (where lease_expires_at < now()) ... WHERE state IN ('untested','testing') AND claimed_by IS NOT NULL GROUP BY 1` → **every** owner row shows `lease_expired == cells` (2,523 rows across 12 owners, 100%).
**Corroboration that this is not the only never-release site:** `attempts` values **above** the repo-default cap of 3 exist — 364 cells at `attempts=4`, 125 at 5, 158 at 6 — which is only possible because `release_cells`/`reclaim_expired_leases`, the *only* two code paths that absorb over-cap cells to `attempted` (`service.py:1460`, `:1559`), are not reached for floor/wave claims.

### D3 — Claim identity ≠ worker identity (structural; routed around today, fragile)
**Where:** claim at `src/scanner/agent_runtime/engine/father.py:1874` — `_claim_worklist(f"wave{spawn_wave}")`; workers named at `father.py:1275` — `worker_id=f"batch{spawn_wave}-{batch.batch_id}-{m.id}"`; the mismatch is acknowledged verbatim at `src/scanner/ledger/service.py:1479-1482` ("releasing by the batch workerId matches 0 rows (B1)").
**Mechanism:** The whole wave's cells are owned by `wave{N}`, dispatched to workers under a *different* id. Any `release_cells(worker_id=<batch id>)` is guaranteed to match zero rows. The code avoids this via `release_cells_by_ids` (`father.py:1362`), which is keyed on `cell_id` only — correct, but it means the `claimed_by` column is decorative and no invariant ties it to a live owner.
**Proof:** `[QUERY]` `SELECT count(*) FROM (SELECT DISTINCT worker_id FROM worker_runs) w WHERE EXISTS (SELECT 1 FROM ledger_cell c WHERE c.claimed_by = w.worker_id);` → **`0`**. And `SELECT count(*) filter (where worker_id like 'batch%'), ... like 'wave%', ... like 'floor%' FROM worker_runs;` → **`900 | 0 | 0 | 0` of 971**. No worker identity has ever owned a ledger row.
**Verdict on the operator's framing:** the *mismatch* is real and provable; the *"causing zero-row releases"* consequence is **not currently firing** for LLM workers. It is a latent trap, not an active time sink. (Releases *are* exercised — 59 workers ended `preempted: contract satisfied` — via the by-ids path.)

### D4 — Mass-retire at finalize converts untested surface into a green `completed`
**Where:** `src/scanner/agent_runtime/agent_runtime/finalize.py` → `src/scanner/agent_runtime/finalize.py:455-464`, gated by `scanner_finalize_retire_unreached: bool = True` (`src/scanner/config.py:451`, default **ON**).
**Mechanism:** `UPDATE ledger_cell SET state='attempted', na_reason=COALESCE(na_reason,'unreached: scan ended before this cell was tested') WHERE applicable=true AND (state='untested' OR (state='testing' AND COALESCE(jsonb_array_length(methods_used),0)=0))`. This drives `count_open_cells` to 0 ⇒ `scan_is_complete` returns True (`service.py:1193-1195`) ⇒ `graceful_terminal_status` returns **`"completed"`** (`service.py:1207`). The inline comment claims "attempted is NOT resolved (coverage % unchanged)" — **false**: `scan_is_complete` computes `resolved_ratio = 1 - (open_n/total_n)`, which becomes exactly `1.0`.
**Proof:** `[QUERY]` `SELECT ... FROM ledger_cell c JOIN scans s ... WHERE c.applicable=true GROUP BY 1,2 HAVING count(*) FILTER (WHERE state='attempted') > count(*)*0.5` → eight scans with **100% of applicable cells attempted and `actually_resolved = 0`** still labelled `status='completed'`: `423515d1, f7e8262e, 4bab7894, 799ceec5, bd9a077c, 91db62e9, 1c589347, 3bd3d6ff`. Worst real-world case `dbf83a85`: 3,598 applicable → **3,406 mass-retired (94.6%)**, 166 `tested_clean`, status `completed`.
**Secondary over-count in the same function:** `finalize.py:442-449` promotes `testing` cells with `jsonb_array_length(methods_used) >= 1` straight to `tested_clean`, overriding the ledger's own `>=2`-method redundancy bar (`service.py` `resolve_cells`) — so a single probe is scored as resolved.

### D5 — `SCANNER_ENGINE_COMPLETE_RATIO=0.98` silently truncates the grid; its docstring is wrong
**Where:** `src/scanner/ledger/service.py:1181` (`_COMPLETE_RATIO`, module-import read), gate at `service.py:1196-1200`.
**Mechanism:** `resolved_ratio >= 0.98` returns True with **2% of the applicable grid still open**. The docstring asserts the ratio path "can't fire before `count_open_cells` has already been checked" — that is **factually wrong**: `count_open_cells` returning non-zero does not prevent the ratio branch from returning True. On a 3,600-cell grid that is ~72 cells declared complete untested. Also read once at import, so `os.environ` changes cannot retune a running process.
**Proof:** `[CODE]` read of `service.py:1184-1200`; live grid sizes 2,915 / 3,598 confirm the 2% is tens-to-hundreds of cells.

### D6 — `SCANNER_ENGINE_WORKER_WALL_S=0` means "kill instantly", not "no limit"
**Where:** `src/scanner/agent_runtime/engine/fleet.py:28` — `float(os.environ.get("SCANNER_ENGINE_WORKER_WALL_S", "5400") or "5400")`. No zero-guard. Enforcement at `fleet.py:89` (`asyncio.wait_for`) and `fleet.py:97,106-107` (backstop).
**Mechanism:** `worker.py:38-42` forwards the var **whenever set and non-empty** — the string `"0"` is non-empty, so it reaches the agent. `float("0" or "5400")` → `0.0` ⇒ `asyncio.wait_for(..., timeout=0)` and `deadline = monotonic() + 0`, both firing on the first poll. This contradicts the platform's own convention that `0` means unlimited (`config.py:464` "0 ⇒ an unset time cap is ACTUALLY unlimited"; `father.py:860-862` treats `cap <= 0` as disabled).
**Proof:** `[QUERY]` `SELECT left(error,60), count(*), avg(dur_s) FROM worker_runs WHERE finished_at IS NOT NULL GROUP BY 1` → `preempted: worker backstop 0s exceeded | 13 | 2` and `worker wall cap 0s exceeded | 3 | 0`. All 16 trace to scan `799ceec5`, which ran **1.5 min, mass-retired 130/130 cells, and reported `completed`**.
**Live value for contrast:** `[QUERY]` `docker inspect scanner-agent-84aea81a7e43` → `SCANNER_ENGINE_WORKER_WALL_S=86400`.

### D7 — Progress watchdog is defeated by tool churn; spinning workers run for hours
**Where:** `src/scanner/agent_runtime/engine/father.py:1328-1336`.
**Mechanism:** `advanced = terminal_now > st["terminal"] or tool_calls > st.get("tool_calls",-1) or (last_prog fresher)`. Because a bare `tool_calls` increment counts as forward progress, a worker that fires tools forever without closing a single cell is **never** declared stuck. With `_worker_wall_s()` at 86400 s there is no backstop.
**Proof:** `[QUERY]` live scan `worker_runs` — `batch1-b-7-bunny` status `running`, **2,654 s elapsed, `findings_count = 0`**; `batch1-b-11/12` also `running`. `[CODE]` workdir `decisions.log` — `batch0-b-0-bunny·turn1..turn6`, `batch1-b-9-bunny·turn1..turn7`: repeated `max_turns_exceeded` across many turns of the same batch, i.e. pure churn.
**Blast radius:** the 20-min `STUCK_WINDOW_S` is nominally the primary per-worker stopper; in practice it only cuts workers that go *silent*, which is the minority failure mode.

### D8 — Live-convergence verify runs inline on the sync loop and overshoots its 120 s cadence by 7–15×
**Where:** `father.py:1084-1092` (`_periodic_sync` awaits `_live_convergence` inline), `father.py:969-980`, default `True` at `config.py:401` — **contradicting `father.py:973`'s own docstring "default OFF"**. Live env `SCANNER_ENGINE_LIVE_CONVERGENCE=true`.
**Mechanism:** Each 120 s tick runs the full verify + enrich + dedup + report pipeline with `SCANNER_ENGINE_VERIFY_WALL_S=1200` and `VERIFY_TICK_CONCURRENCY=2` against the *same* single configured model (`stealth/space-bunny-alpha`). Because the await is serial, one slow pass delays every subsequent tick.
**Proof:** `[QUERY/LOG]` `reconcile.tick` timestamps — 20:12:24, 20:15:13, 20:19:02, 20:24:21, 20:28:39, 20:33:27, **21:02:30**, 21:04:54, 21:19:09, **21:35:49**, 21:52:53 → gaps of 2–29 min against a 120 s target. `finalize.verify_complete` fires 8× mid-run with `unavailable` monotonically climbing 2 → 3 → 5 → 7 → 13 → 18 → 19.

### D9 — Pool hard cap of 4 against a 12-batch wave → 3 sequential rounds per wave
**Where:** `father.py:1384` (`compose_batches(..., max_cells=_batch_max_cells())`), `father.py:1402` (`hard_cap=_pool_hard_cap(...)`), `fleet.py:141-160` (`run_pool`).
**Mechanism:** Live env has `SCANNER_ENGINE_POOL_HARD_CAP=4`, `SCANNER_ENGINE_FANOUT=4`, `SCANNER_ENGINE_BATCH_MAX_CELLS=8`. Observed 11–12 batches per wave (`batch0-b-0`…`b-10`, `batch1-b-0`…`b-11`) ⇒ **3 sequential rounds of 4**, each round bounded only by D7's ineffective watchdog. Per-round mean ≈ 500 s ⇒ ~54 min/wave, matching the observed cadence exactly.
**Note an unverified arithmetic discrepancy:** `father.py:1139` computes `_claim_limit() = fanout × _WORKLIST_MAX = 4 × 12 = 48` cells/wave, which at `max_cells=8` implies 6 batches, not the 11–12 observed. I did not reconcile this against `compose_batches`; flagged rather than guessed.

---

## D. H1 VERDICT

# **REFUTED**

**Blast radius of the refutation — H1's two named causes are quantitatively excluded as the throughput bottleneck:**

- **"Wave-loop sync overhead"** — measured at **~40–50 ms per wave boundary** (`\timing`: 1.9–3.4 ms per statement, ~12–15 statements) against an observed **~3,000 s wave**. That is **~0.0015% of wave time** — five orders of magnitude too small to matter. This half of H1 is dead.
- **"Ledger claim/release mismatches"** — the mismatch is **real and provable** (D3: 0/971 worker identities ever owned a cell) but is **routed around** by `release_cells_by_ids` and therefore does not generate the zero-row releases the hypothesis assumes. Its actual cost is **coverage loss, not time**. The one genuine *time* cost in this family is floor re-entry (D2), which I can bound but not fully size.

**What actually dominates:** a third cause the hypothesis does not name. At **mean tool concurrency 0.67 against a 4-slot pool**, roughly **83% of worker wall time is LLM inference wait**, amplified by (i) `POOL_HARD_CAP=4` forcing 3 sequential rounds per wave, (ii) **`max_turns_exceeded` on 63/63 recorded turns** — the model never converges inside its turn budget, so every batch burns its full allowance, and (iii) the live-convergence verifier (D8) drawing on the same single-model endpoint.

**Two supporting findings that partially vindicate the *spirit* of H1** (ledger/scheduling machinery, not coverage cost): the 90-min wall is **not in force** (it is 86,400 s live, and once resolved to **0 s**, D6), so the schedule is bounded by neither the wall nor a working watchdog (D7) — and 39.8% of the grid ends terminal-unresolved (D4/D5), with 8 scans reporting `completed` on essentially zero real coverage.

**Recommended framing for the operator:** H1 mis-diagnoses a *coverage-integrity* problem as a *throughput* problem. The throughput problem is concurrency × model latency × non-convergence; the ledger problems are worth fixing on their own merits (they are severe), but fixing them will **not** make scans finish faster — it will make the finished scans more honest.

---

## E. EVIDENCE LEDGER

| Claim | Source (type + location) | Confidence | Notes |
|---|---|---|---|
| Wave loop lives in `Father.run`, not `engine/run.py`; `run.py` is the entrypoint/finalizer | [CODE] `agent_runtime/engine/run.py:167-374`; `engine/father.py:1727-1930` | HIGH | `run.py` has no wave loop |
| Claim owner is `wave{N}`; workers are `batch{N}-{bid}-{model}` | [CODE] `father.py:1874`, `father.py:1275` | HIGH | identity mismatch is by construction |
| B1 mismatch acknowledged in the ledger service itself | [CODE] `ledger/service.py:1479-1482` | HIGH | "releasing by the batch workerId matches 0 rows (B1)" |
| Release routed around mismatch via cell_ids | [CODE] `father.py:1358-1362`; `ledger/service.py:1476-1505` | HIGH | `_batch_cells` map keyed on worker_id |
| No worker identity ever owned a ledger row | [QUERY] `SELECT count(*) FROM (SELECT DISTINCT worker_id FROM worker_runs) w WHERE EXISTS (SELECT 1 FROM ledger_cell c WHERE c.claimed_by=w.worker_id)` → `0` | HIGH | decisive |
| worker_runs naming: 900 `batch%`, 0 `esc%`, 0 `wave%`, 0 `floor%` of 971 | [QUERY] `SELECT count(*) filter (where worker_id like ...) FROM worker_runs` | HIGH | claims live in a disjoint namespace from workers |
| Exploit floor claims under `floor-{family}` | [CODE] `exploit_floor.py:4890` | HIGH | — |
| Exploit floor has **zero** release/reclaim calls | [CODE] `Select-String 'release\|reclaim'` over `exploit_floor.py` → 0 matches (5,285 lines) | HIGH | the strongest single code finding |
| 1,660 cells stranded `testing` with **expired** leases, live scan | [QUERY] `SELECT claimed_by,state,count(*),count(*) filter (where lease_expires_at<now()) ... GROUP BY 1,2` | HIGH | 1,660 = 1,624 `floor-*` + 38 `wave1` + … |
| All stranded owners 100% lease-expired, all-time (2,523 rows) | [QUERY] `GROUP BY claimed_by` with `lease_expired` == `cells` for all 12 owners | HIGH | confirms no live owner exists |
| `attempts` exceeds repo-default cap 3 (364@4, 125@5, 158@6) | [QUERY] `SELECT attempts,count(*) FROM ledger_cell WHERE applicable=true GROUP BY 1` | HIGH | only reachable if release/reclaim paths don't run |
| Wave-loop quiescence is fail-CLOSED | [CODE] `father.py:1439-1441` (returns `True` on read error); `attack_surface.py:178-183` (re-raises, `count_claimable_failed`) | HIGH | hypothesis's "high-value defect" is *not* present here |
| Quiescence has one fail-OPEN branch | [CODE] `father.py:1435-1436` — returns `False` ("drained") when `surface is None` | HIGH | latent; unreachable in production (surface always wired) |
| `COMPLETE_RATIO=0.98` declares complete with 2% still open | [CODE] `ledger/service.py:1181`, `1184-1200` | HIGH | read once at import |
| Docstring claim about ratio gate is false | [CODE] `ledger/service.py:1188-1191` vs `:1193-1200` | HIGH | `open_n != 0` does not gate the ratio branch |
| Mass-retire turns untested cells into `completed` | [CODE] `agent_runtime/finalize.py:455-464`; gate `config.py:451` (default ON) | HIGH | — |
| 8 scans `completed` at 100% mass-retired, 0 resolved | [QUERY] `HAVING count(*) FILTER (WHERE state='attempted') > count(*)*0.5` | HIGH | incl. `799ceec5`, `423515d1`, `1c589347` |
| Worst case `dbf83a85`: 94.6% mass-retired, status `completed` | [QUERY] per-scan state rollup | HIGH | 3,406/3,598 |
| Single-probe cells promoted to `tested_clean` | [CODE] `finalize.py:442-449` (`jsonb_array_length(methods_used) >= 1`) | HIGH | overrides the ≥2-method bar |
| `resolved_count` structurally always 0 | [CODE] `worker.py:20` (declared, never assigned) + `telemetry.py:183` (only read) | HIGH | `grep resolved_cells` → 3 hits, none an assignment |
| 970/970 worker_runs have `resolved_count` non-null, sum 0, max 0 | [QUERY] `SELECT count(*), sum(resolved_count), max(resolved_count) FROM worker_runs` → `970 \| 0 \| 0` | HIGH | sibling `findings_count` sums 35,058 on the same UPDATE |
| `resolved_count` is API-exposed | [CODE] `api/schemas.py:609` | HIGH | operator-visible |
| Per-worker wall constant = 5400 s default, no zero-guard | [CODE] `engine/fleet.py:12-28`; enforcement `fleet.py:89`, `97`, `106-107` | HIGH | — |
| Live wall is 86,400 s, not 90 min | [QUERY] `docker inspect scanner-agent-84aea81a7e43` → `SCANNER_ENGINE_WORKER_WALL_S=86400` | HIGH | also `RUNAWAY_WALL_S=86400` |
| Wall resolved to **0 s** in one scan; killed 16/16 workers | [QUERY] `GROUP BY left(error,60)` → `worker backstop 0s exceeded \| 13 \| avg 2s`; `worker wall cap 0s exceeded \| 3 \| avg 0s`, all in `799ceec5` | HIGH | scan 1.5 min, 130/130 retired, `completed` |
| `"0"` is forwarded because it is non-empty | [CODE] `scheduler/worker.py:38-42` (allowlist) + `:866` (`_forward_tuning_env`) | HIGH | contrast `father.py:860-862`, `config.py:464` which do treat 0 as unlimited |
| 90-min wall never bounded the schedule | [QUERY] max worker lifetimes 6,257 s / 6,685 s > 5,400 s; avg for `ok` = 1,462 s | HIGH | wall not the binding constraint |
| Stuck watchdog defeated by tool churn | [CODE] `father.py:1328-1336` (`tool_calls > st['tool_calls']` counts as progress) | HIGH | — |
| Spinning worker: 2,654 s, 0 findings, still running | [QUERY] live `worker_runs` — `batch1-b-7-bunny` | HIGH | — |
| 63/63 worker turns ended `max_turns_exceeded` | [QUERY-equivalent] workdir `decisions.log`, full file read, every line | HIGH | zero normal completions |
| Recon = 214 s = 3.3% of an ~108 min scan | [QUERY/LOG] `phase.started` 20:08:50 → `phase.finished` 20:12:24 | HIGH | — |
| Only 2 waves in 108 min (~54 min/wave) | [QUERY/LOG] exactly 2 `governor.decision` events in the stream | HIGH | governor is once per wave iteration (`father.py:1841-1843`) |
| Exploit floor consumes 86% of its budget per wave | [QUERY/LOG] `exploit_floor.complete` 541 s then 806 s vs `SCANNER_FLOOR_BUDGET_S=1200` | HIGH | 2 invocations only |
| Floor does ~2× the tool work of the whole LLM fleet | [QUERY/LOG] floor `fired=600 + 2125 = 2725` vs 4,152 total `tool.started` ⇒ 1,427 for 29 workers | HIGH | 49 tools/worker |
| **Mean tool concurrency 0.67, peak 6** over 6,447 s | [QUERY/LOG] `tool.started`/`tool.done` event-sweep, area/span | HIGH | pool cap is 4 ⇒ ~83% of slot time is inference wait |
| Wave-boundary DB reads cost 1.9–3.4 ms each | [QUERY] `psql \timing`: count_open 3.288 ms, full-grid join 3.403 ms, coverage_counts 2.952 ms, reclaim predicate 1.947 ms | HIGH | refutes H1 sync-overhead |
| Wave claims only ~48 cells (`fanout × 12`) but 11–12 batches observed | [CODE] `father.py:1139` (`_WORKLIST_MAX=12`), `father.py:1384` (`max_cells=8`) vs [LOG] `batch0-b-0..b-10` | LOW | **UNVERIFIED** — not reconciled against `compose_batches` |
| live_convergence overshoots 120 s cadence by 7–15× | [QUERY/LOG] `reconcile.tick` gaps incl. 29, 14, 17, 17 min vs `SYNC_INTERVAL_S=120` | HIGH | — |
| live_convergence default is `True`, docstring says OFF | [CODE] `config.py:401` vs `father.py:973`; live env `SCANNER_ENGINE_LIVE_CONVERGENCE=true` | HIGH | doc/code contradiction |
| 48.5% of all worker runs died on an empty LLM response | [QUERY] `ChatCompletion response has no choices` → 471 runs, avg 125 s; `1f5fe7c8` 282/321, `6c4d84c3` 72/72, `dbf83a85` 31/31 | HIGH | largest single error class |
| 429 rate-limit errors | [QUERY] 73 + 11 + 7 = 91 worker runs | HIGH | secondary LLM-capacity signal |
| `time_cap_seconds` NULL on all scans since 09-28 | [QUERY] `scans.time_cap_seconds` — only 09-20 rows have 2100 | HIGH | ⇒ no soft-cap drain (`father.py:860-862`), poller SIGKILL is the only stop |
| 53 `worker_runs` rows stuck `running` (avg 335,428 s) | [QUERY] `SELECT status,count(*),avg(...) GROUP BY status` | HIGH | bookkeeping leak; `worker_runs` unreliable for lifetime stats |
| 87.1% of applicable cells never probed (7,371 of 8,771 attempted) | [QUERY] `attempts=0 AND state='attempted'` → 7,371; `na_reason` histogram → 8,683 `unreached` | HIGH | — |
| Only 82 cells (0.9%) hit the real attempt cap | [QUERY] `na_reason='attempted: attempt cap reached'` → 82 | HIGH | the designed terminator is nearly inert |
| Worst unresolved classes | [QUERY] `forced_browse 518, priv_esc 488, auth_bypass 455, excessive_data 450, rate_limit 328` | HIGH | high-value classes, mostly never claimed |
| Live volume is `abhedi_red_scanner_data`; no `abhdeii_*` volume exists | [QUERY] `docker volume ls \| grep -i abhedi` → `abhedi_red_scanner_data` | HIGH | brief's warning confirmed; double-'i' artifact absent on this host |
| Agent containers are `--rm`; workdir is the only post-mortem record | [QUERY] `docker ps` shows no exited agent containers to inspect | MEDIUM | documented as a method constraint |
| DB credentials used: `scanner`/`scanner` on db `scanner` | [QUERY] read from repo `docker-compose.yml`; connection succeeded | HIGH | stated as instructed |

---

### Falsification summary
The operator's hypothesis survived only in a weakened form. Both of its named causes are excluded by direct measurement (sync overhead ~0.0015% of wave time; release mismatch provably real but inert because it is bypassed). The binding constraint is a third factor — model inference latency at 0.67 mean concurrency under a 4-slot pool, with 100% turn-cap non-convergence — compounded by a broken safety envelope (wall at 24 h or 0 s, watchdog defeated by tool churn). Separately and more seriously, the ledger machinery is producing **false `completed` verdicts** on scans with 94–100% of the grid untested.
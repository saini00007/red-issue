# WS-1b — Terminal-cell & scan-throughput forensics (server-observed)

**Research agent:** nova-02 · **Mode:** READ-ONLY systems audit (sources: local code + `ssh abhedi`)
**Snapshot time:** 2026-09-30 21:47–22:00 UTC (live DB — counters moved while auditing; all counts "as of" that window)
**Targets:** container `scanner-postgres`, db/user `scanner`, schema `tenant_xbow`; volume `abhedi_red_scanner_data` (`/var/lib/scanner/<hash>/<scan_id>/`); container `scanner-cp`.
**Write scope honored:** only this file + `scripts/*.sql`. No DB writes, no container lifecycle actions, no target HTTP.

### Step 1 — Schema recon (real names)

[QUERY] `information_schema.tables where table_schema='tenant_xbow'` → 19 tables:
`agent_messages, audit_log, chain_edge, chain_node, checkpoints, coverage_ledger, evidence_object, findings, inventory_element, ledger_cell, oob_token, recon_targets, scan_approvals, scan_events, scan_phases, scan_schedule, scans, tool_invocations, worker_runs`
**There is no table named `evidence` or `chains`** — the real ones are `evidence_object` and `chain_node`/`chain_edge`.

Key columns (`scripts/01_columns.sql`, `02_columns2.sql`):
- `scans(status text, mode, current_phase, created_at, started_at, completed_at, failure_reason, time_cap_seconds, cost_cap_usd, cost_spent_usd)`
- `ledger_cell(cell_id, scan_id, vuln_class, applicable bool, state text, attempts int, methods_used jsonb, evidence_ids jsonb, finding_id, na_reason, last_progress, updated_at)`
- `findings(..., verified bool, verification_method, evidence_paths jsonb, dedup_hash, severity, created_at)`
- `evidence_object(evidence_id, scan_id, cell_id, finding_id, kind, method, confidence, rejection_reason)`
- `agent_messages(scan_id, turn_index, role, model, tokens_in/out, cost_usd, occurred_at)`
- `chain_node(node_id, scan_id, finding_id, capability)`, `chain_edge(from_node, to_node, rationale)`
- `worker_runs(phase, status, findings_count, resolved_count, error, started_at, finished_at)` · `tool_invocations(tool_name, status, exit_code, started_at, finished_at)`

**State vocabulary is plain `text`, not a PG enum.** Observed values + code meaning:

| State | count | % of all 70,781 | % of applicable 22,011 | meaning (code) |
|---|---|---|---|---|
| `na` | 48,323 | 68.3 | — (applicable=false) | cell can't apply to this surface; excluded from coverage denominator `[CODE] reporting/service.py:115-117` |
| `attempted` | 8,771 | 12.4 | **39.8** | **TERMINAL, NOT RESOLVED** — attempt-cap/finalize retire of never-closed work `[CODE] reporting/service.py:123`, `finalize.py:450-467`, `ledger/service.py:1237-1247` |
| `untested` | 5,299 | 7.5 | 24.1 | open (never touched) `[CODE] ledger/service.py:50` `_OPEN_STATES=("untested","testing")` |
| `tested_clean` | 4,862 | 6.9 | 21.2 (4,671 applicable) | resolved — probed & closed clean `[CODE] reporting/service.py:121` |
| `testing` | 2,775 | 3.9 | 12.1 | open/in-flight (weapon fired, not closed) `[CODE] ledger/service.py:765-766` |
| `blocked` | 454 | 0.6 | 1.4 | resolved-with-reason `[CODE] reporting/service.py:121` |
| `confirmed` | 297 | 0.4 | 1.3 | resolved — proven vuln `[CODE] reporting/service.py:121` |

Terminal set = `{confirmed, tested_clean, blocked, na, attempted}` `[CODE] engine/batch.py:18`; resolved set = `{confirmed, tested_clean, blocked}` `[CODE] reporting/regression.py:37`, `engine/coverage_qa.py:30`.
States referenced in code but **0 rows in DB**: `pending_oracle`, `pending_human` `[CODE] ledger/service.py:970`; agent-written `tested_vulnerable` occurs in a workdir file but **not in src at all** (see Q3/forensics).

---

## 1. Per-question findings (Q1–Q6)

### Q1 — Scans by status; duration min/median/max

[QUERY] `scripts/03_q1_status.sql` → `cancelled|19`, `completed|18`, `failed|4`, `partial|1`, `running|1` (43 total); mode `thorough|43`.
[QUERY] same file → current_phase: `finalize|18`, `exploitation|17`, `reconnaissance|4`, `<null>|4`.
[QUERY] `scripts/04_q1_dur.sql` → `dur_s_min_med_max|42|92|664|64618` → **n=42, min 92 s, median 664 s (11.1 min), max 64,618 s (17.9 h)** (created→completed_at).
[QUERY] `04_q1_dur.sql` → `cancelled|150/741/2192`, `completed|92/495/64618`, `failed|259/599/945`, `partial|2226/2226/2226` (min/median/max s).
[QUERY] `04_q1_dur.sql` → `running_age_s|5848` (scan `84aea81a…` still live at query time).
[QUERY] `scripts/16_caps.sql` → time caps `2100|22`, `900|1`, `<null>|20`; **`cost_cap_usd = 0.00` for all 43 and `avg(cost_spent_usd)=0.000`** → cost metering reports zero spend on every scan.
[QUERY] `16_caps.sql` → failure_reason: `<null>|39`, `agent_exit_-1_after_0_attempts|3`, `spawn_error: …scanner/zap image pull 404…|1`.
[QUERY] `scripts/21_events.sql` → `scan.created|43, scan.started|40, scan.kill|21, scan.cancelled|20, scan.completed|14, scan.close|4, scan.closed|4, scan.failed.crash|3, scan.failed.spawn|1` — event stream shows 14 completion events vs 18 scans in `completed` state.
[CODE] time-cap cancellation path: `scheduler/poller.py:1217-1227`; failure strings: `poller.py:594` (spawn_error), `poller.py:1425` (`agent_exit_{code}_after_{n}_attempts`).
[UNVERIFIED] 19 cancelled scans have median duration 741 s vs a 2,100 s cap — most cancellations are **not** explained by the time cap (manual/API kill vs. other triggers not proven).

### Q2 — Ledger cells total, by state; terminal-but-unresolved

[QUERY] `scripts/05_q2_state.sql` → `cells_per_scan_total|70781|40` (43 scans exist; **3 failed scans have 0 cells**).
[QUERY] `05_q2_state.sql` → `cell_applicable false|48770`, `true|22011`.
[QUERY] `scripts/06_q2b_terminal.sql` → applicable states: `attempted|8771|39.8`, `untested|5299|24.1`, `tested_clean|4671|21.2`, `testing|2658|12.1`, `blocked|315|1.4`, `confirmed|297|1.3`.
[QUERY] `06_q2b_terminal.sql` → `resolved|5283`, `open|7957`, `terminal_unresolved_attempted|8771`, `pct_terminal_unresolved|39.8`.
**Result: 8,771 applicable cells (39.8% of all applicable cells; 62.4% = 8,771/14,054 of all *terminal* applicable cells) reached a terminal state while never being proven or disproven.**
[CODE] why `attempted` is terminal-but-unresolved: `reporting/service.py:123` "terminal (attempt-cap exhausted), not open, not resolved"; finalize retires never-probed cells: `agent_runtime/finalize.py:450-467` (SQL `SET state='attempted'`); attempt cap default 3: `ledger/service.py:1237-1247`.
[QUERY] `scripts/17_attempts.sql` → attempts>3 on 647 cells (0.91%) despite cap default 3 → cap env/override or post-cap increments `[UNVERIFIED which]`.

### Q3 — Per-scan cells vs actually proven (honest-coverage gap)

[QUERY] `scripts/20_q3_ratio.sql` → `avg per-scan resolved/applicable = 0.155`, **median = 0.000**, max = 1.000, n=40 scans.
[QUERY] `20_q3_ratio.sql` → overall `5283 / 22011 = 24.0%` applicable cells resolved; **22 of 40 scans resolved ZERO applicable cells**.
[QUERY] `scripts/16_caps.sql` (findings) + `20_q3_ratio.sql` → **11 of 18 `completed` scans have zero resolved cells**.
[QUERY] `scripts/07_q3_perscan.sql` (top rows, total|applicable|resolved|attempted|open|resolved%):
`dbf83a85 completed|9420|3598|192|3406|0|5.3` · `68a58881 completed|7632|2719|1416|1303|0|52.1` · `1f5fe7c8 completed|5337|2122|1269|853|0|59.8` · `373bff88 completed|6240|1904|388|1516|0|20.4` · `6c4d84c3 cancelled|6057|1812|202|0|1610|11.1` · `799ceec5 completed|513|130|0|130|0|0.0` · `84aea81a running|9237|2915|930|0|1985|31.9`.
[QUERY] `07_q3_perscan.sql` → every **cancelled** big scan has `open_cells > 0` (e.g. 1,610 / 1,572 / 1,298 / 1,471) — cancellation leaves the grid wide open (no finalize retire runs).
[QUERY] `scripts/18_q6_lag.sql` → `all_cells_state_pct`: `na 68.3, attempted 12.4, untested 7.5, tested_clean 6.9, testing 3.9, blocked 0.6, confirmed 0.4`.
[CODE] the report itself computes the same "honest" number: `reporting/service.py:110-134`; workdir JSON for `dbf83a85` matches DB (`coverage.applicable 3598, resolved 192, resolved_pct 5.3, attempted 3406, open 0`).

### Q4 — findings with evidence vs without; chains populated?

[QUERY] `scripts/08_q4_evid.sql` → `findings_total|254`, `findings_with_evidence_row|19`, `findings_verified true|201 / false|53`.
[QUERY] `scripts/19_chains.sql` → verified × evidence: `true|false|183`, `true|true|19`, `false|false|53` → **183 of 201 verified findings (90.6%) have no `evidence_object` row**.
[QUERY] `19_chains.sql` → `evidence_object` total `325`: `cell_id only|18`, `finding_id only|19`, **neither|288** (orphan evidence rows).
[QUERY] `08_q4_evid.sql` → `evidence_total|316` (snapshot ~10 min earlier; table is growing live), `coverage_ledger|0`, `tool_invocations|35700` (`success|32226`, `failed|3533` = 9.9% fail), `scan_events|57360`, `oob_token|276`.
[QUERY] `08_q4_evid.sql` → **chains ARE populated**: `chain_node|188`, `chain_edge|449`.
[QUERY] `scripts/19_chains.sql` → nodes/edges per scan (top): `84aea81a 37/46`, `68a58881 29/118`, `0ebea923 23/66`, `373bff88 21/66`, `1f5fe7c8 18/78`.
[QUERY] `report.json` (workdir, parsed locally) → `dbf83a85: chains=0, executed_chains=0`; `68a58881: chains=118, executed_chains=0` → **graph is built, chain execution never fires**.
[CODE] executed_chains only fills for verified executed-chain findings: `reporting/service.py:298-318`; chain node/edge synthesis: `agent_runtime/chain/service.py:124-181`; `coverage_ledger` is a deliberately retired phantom table (explains 0 rows): `engine/context.py:15,154`, `db/provisioning.py:60-63`.
[CODE] `verified=True` is stamped by several paths independent of evidence rows (finalize re-verify `agent_runtime/finalize.py:919`, OOB autofind `oob/service.py:355,489`, inventory ingest `inventory_ingest.py:918`).

### Q5 — agent turns per scan (did the model drive many turns or die early?)

[QUERY] `scripts/10_q5_turns.sql` → `turns_per_scan|17|18.4|139|1` → **only 17 of 43 scans have any `agent_messages` row; avg 18.4 assistant turns, max 139, min 1** (313 rows total, all `role=assistant`).
[QUERY] `10_q5_turns.sql` → `distinct_scans_with_msgs|17`; `msgs_with_null_turn|0`.
[QUERY] `scripts/12_q5b.sql` → top max-turn scans `7,7,7,7,4,4,3,2`; **10 of 17 scans never exceeded turn index 2** (`turns_lt3|10`).
[QUERY] `12_q5b.sql` → scans with messages by status: `cancelled|8, completed|7, failed|0, partial|1, running|1` → 26 scans have no message telemetry at all.
[QUERY] `scripts/23_workers.sql` + inline query → `worker_runs` 972 rows: **`error|578 (59.5%)`, `ok|266`, `partial|75`, `running|53`**; avg 24.9 runs/scan, max 321; by phase `exploit|error 561` vs `exploit|ok 245`.
[QUERY] worker error signatures (top): `ChatCompletion response has no choices (possible provider error payload)…|471` (81.5% of errors), `429 Too Many Requests|73`, `429 provider|11`, `500|9`, `429 free-models…|7`, `400|6`, `502|1`.
[CODE] one `agent_messages` row per Runner turn: `engine/runtimes/agents_runtime.py:430`, INSERT `engine/telemetry.py:226`; known "messages left empty" path acknowledged in `planner/contract.py:40`, `planner/coordinator.py:141`.
[CODE] failure strings originate from the OpenAI-compatible client/provider, not repo code → **[UNVERIFIED] exact raising site** (no match for `no choices` in `src/`).

### Q6 — Phase-revealing timestamps: created vs first/last ledger update

[QUERY] `scripts/13_q6_phase.sql` → 43 scans listed with `created_epoch / first_cell_upd / last_cell_upd / last_progress`; **3 `failed` scans have `cells_touched = 0`** (`ab8cf1e8`, `f8500a4b`, `2759dbc2`) — they never wrote a single ledger row.
[QUERY] `scripts/18_q6_lag.sql` → `first_ledger_lag_s_min_med_max|18|336|1271` → **median 5.6 min between scan creation and the first ledger write**.
[QUERY] `18_q6_lag.sql` → `active_window_s_min_med_max|0|0|63660` → median cell activity window = **0 s** (grid cells are bulk-materialized in one flush; only a few scans ever re-touch cells — max 17.7 h).
[QUERY] `13_q6_phase.sql` → representative lags (s): `dbf83a85 created 1790633156 → first 1790633531 (375) → last 1790634333 (1177)`; `68a58881 1790636693 → 1790637518 (825) → 1790701177 (64,484)`; `4bab7894 1789910800 → 1789910886 (86) → 1789910886 (86)`.
[QUERY] `scripts/15_inv_phases.sql` → phases rows: `reconnaissance completed|37`, `exploitation completed|19 / running|18`, `finalize completed|16 / running|2`, `reconnaissance running|4` — i.e. **19 of 43 scans never reached a completed finalize**.
[QUERY] `15_inv_phases.sql` → tool invocations by tool (top): `curl 14768, upload 3946, oob 3035, python3 2301, sqlmap 2082, cat 2042, ls 1954, grep 1186, dalfox 609`.
[QUERY] `08_q4_evid.sql` + throughput file → resolved-cells/hour: `68a58881 81`, `1f5fe7c8 85`, `4ebd576b 82` for long scans vs `dbf83a85 597` (fast, low-resolve) — wall-clock throughput is dominated by scan length, not by resolution rate.

---

## 2. Step 3 — Workdir forensics (3 representative scans, read-only)

Read method: `docker exec scanner-cp cat <path>` and `docker run --rm -v abhedi_red_scanner_data:/mnt alpine …` (throwaway, read-only), parsed/aggregated in-memory locally. **No raw prompts or request bodies reproduced.**

| Artifact | `dbf83a85` (completed) | `68a58881` (completed) | `84aea81a` (running) |
|---|---|---|---|
| `decisions.log` | 10 lines, **no timestamps** (format: `[worker·turnN] Session Summary`) | 8 lines, same format | n/a (not listed) |
| `ledger_updates.jsonl` | 124 lines: `testing 117, tested_clean 7`; 68 distinct endpoints, **29 endpoints updated >1× (max 7)** | 2,481 lines: `testing 1845, tested_clean 618, blocked 17, tested_vulnerable 1`; 221 endpoints, **185 updated >1× (max 63 for a single endpoint)** | — |
| `findings.jsonl` | 23 lines | (280 KB) | — |
| `oob_interactions.jsonl` | 4,271 lines: `ldap 4266, dns 4, http 1`, **distinct interaction ids = 2**, first ts `2026-08-29` (a month before scan start) | 4,603 lines: `ldap 4337, dns 219, http 47`, distinct ids = 2, first ts `2026-08-29` | 220 lines: `dns 138, http 82`, distinct ids = 1 |
| `coverage_quality.json` | families: `access 1163 applicable / 0 exercised / 101 resolved`, `clientside 506/0/4`, `injection 760/63/7`, `logic 655/183/21`, `config 514/74/59`, `oob applicable 508 / minted 1 / fired 1` | present (not dumped) | present |
| `report.json` (aggregate) | `status closing`, findings 13, unconfirmed 1, **chains 0, executed_chains 0**, coverage `3598/192/5.3%, open 0, attempted 3406` | `status closing`, findings 36, unconfirmed 9, **chains 118, executed_chains 0**, coverage `2719/1416/52.1%, attempted 1303` | — |
| `report.json effort` | 534 tool calls, 31 workers, 436,951 tokens, tools incl. `oob 21 calls / 20 errors` | 12,143 tool calls, 172 workers, 1,024,924 tokens; `sqlmap 1703/343 err`, `oob 898/180 err`, `upload 1251/181 err` | — |
| `logs/` | `agent.log 821 lines`, `toolserver.log 665` | `agent.log 60,672 lines`, `toolserver.log 20,551` | — |

Observations:
- **Thrash (aggregate only):** in `68a58881`, 185 of 221 endpoints received repeated ledger updates, one endpoint **63 times** — repeated `testing` writes without convergence. [QUERY] in-memory group of `ledger_updates.jsonl`.
- **Invalid state emitted:** `tested_vulnerable` appears once and exists **nowhere in `src/`** → agent-authored state the resolver does not know; ledger skips unknowns ("Unmatched rows are logged and skipped") `[CODE] ledger/service.py:767,801-803`.
- **`decisions.log` carries no timestamps** → cannot be used for phase timing (contradicts the intended "one line per phase decision" contract `[CODE] agent_runtime/orchestrator.py:44`).
- **`oob_interactions.jsonl` is a mirrored full stream**, including entries predating the scan by a month (`interactsh.py:11` streams interactions to the work path; `scheduler/poller.py:1490`, `entrypoint.py:810,992` re-mirror it) → per-scan OOB counts are not scan-scoped.
- `coverage_quality.json` for `dbf83a85` reports **2 tool families with 0 executions over 1,669 applicable cells** (access/clientside) while the scan still ended `completed` with `open 0`.

## 3. Step 4 — `docker logs scanner-cp --tail 500` (aggregate only)

[QUERY] `docker logs scanner-cp --tail 500 2>&1` parsed in-memory → **500 lines: `event.published 494`, `egress_healthy 6`; levels `debug 494 / info 6`; error/warning 0**; time span `21:54:12 → 21:55:43` (91 s).
[QUERY] `docker logs scanner-cp --tail 5000` → 5,000 lines spanning `21:47:43 → 21:56:13` (8.5 min): **`event_type=scan.method_switch 4,953 (99.1%)`**, `egress_healthy 31`, `ledger.resolve.finding_unmatched 8`, `evidence.written 8`; error/warning lines = 8.
[QUERY] same window keyword counts: `poll=0, finali=0, spawn=0, worker=0, heartbeat=0, lease=0, reclaim=0, cancel=0` → poller/finalize/spawn events are **not visible in this container's recent log window** (they are logged elsewhere/at other levels) [UNVERIFIED location].
[QUERY] aggregate of the 8 warnings → `ledger.resolve.finding_unmatched` on 6 distinct endpoints, all with `vuln_class=ssrf` mismatched against non-SSRF endpoints (CommandInjection/RFI/SSRFVuln classes) — i.e. **findings whose (endpoint, vuln_class) key matches no ledger cell**.
[CODE] one `scan.method_switch` event **per stale `testing` cell** each watchdog pass (`WATCHDOG_STALE_SECONDS = 180`, `scheduler/poller.py:111`, publish loop `poller.py:1158-1165`) → explains the ~5.4 events/s flood (4,953 in 8.5 min).
[CODE] unmatched-finding warning: `ledger/service.py:873`.

---

## 4. Observed-failure catalog

| # | Failure mode | Aggregate metric | Evidence |
|---|---|---|---|
| F1 | Cells closed as terminal without proof ("attempted" retirement) | **8,771 cells = 39.8% of applicable = 62.4% of terminal applicable cells** | [QUERY] `06_q2b_terminal.sql`; [CODE] `finalize.py:450-467`, `reporting/service.py:123` |
| F2 | Honest-coverage gap: scans end with almost nothing resolved | median per-scan resolved/applicable = **0.000**; overall **24.0%**; **11/18 completed scans = 0 resolved**; `dbf83a85` 5.3% | [QUERY] `20_q3_ratio.sql`, `07_q3_perscan.sql`; [CODE] `reporting/service.py:110-134` |
| F3 | LLM/provider failures kill workers | **578/972 worker_runs error (59.5%)**; 471 "no choices", 73× HTTP 429; exploit phase 561 err vs 245 ok | [QUERY] `23_workers.sql` + inline error grouping; [CODE for meaning] `worker_runs` written by scheduler [UNVERIFIED raise site] |
| F4 | Model dies early / telemetry missing | only **17/43 scans** have `agent_messages`; **10/17 never pass turn 2**; avg 18.4 turns, max 139 | [QUERY] `10_q5_turns.sql`, `12_q5b.sql`; [CODE] `agents_runtime.py:430`, `planner/coordinator.py:141` |
| F5 | Watchdog event flood drowning control-plane logs | **4,953/5,000 log lines (99.1%) = `scan.method_switch`** in 8.5 min (~5.4/s) | [QUERY] `docker logs --tail 5000` aggregate; [CODE] `poller.py:111,1158-1165` |
| F6 | Findings recorded without evidence rows | **183/201 verified findings (90.6%) have 0 `evidence_object` rows**; 288/325 evidence rows are orphans (no cell, no finding) | [QUERY] `19_chains.sql`, `08_q4_evid.sql`; [CODE] multi-path `verified=True`: `finalize.py:919`, `oob/service.py:355,489` |
| F7 | Chaining built but never executed | `chain_node 188 / chain_edge 449` populated; **`executed_chains = 0`** in both sampled reports | [QUERY] `08_q4_evid.sql`, `19_chains.sql`, workdir `report.json`; [CODE] `reporting/service.py:298-318` |
| F8 | Endpoint-level ledger churn (thrash) | `68a58881`: **2,481 updates, 185/221 endpoints repeated, one endpoint 63×** | [QUERY] in-memory aggregate of `ledger_updates.jsonl`; [CODE] resolver re-runnable by design `ledger/service.py:965` |
| F9 | Tool-level failure inside "successful" scans | `oob` tool 20/21 errors (`dbf83a85`), 180/898 (`68a58881`); `sqlmap` 343/1703 errors; global `tool_invocations` 3,533/35,700 failed (9.9%) | [QUERY] `report.json.effort`, `08_q4_evid.sql` |
| F10 | OOB proof base is not scan-scoped | per-scan OOB file contains **ldap floods (4,266/4,271) with only 2 distinct interaction ids**, first timestamp a month before scan creation | [QUERY] in-memory aggregate; [CODE] `interactsh.py:11`, `poller.py:1490` |
| F11 | Coverage/QA self-report shows unfired tool families yet scan completes | `access 1163 applicable/0 exercised`, `clientside 506/0` in `coverage_quality.json` while scan status `completed`, `open 0` | [QUERY] workdir `coverage_quality.json`; [CODE] writer `engine/coverage_qa.py:123-136` |
| F12 | Finding→cell key mismatch | 8× `ledger.resolve.finding_unmatched` (e.g. `vuln_class=ssrf` vs CommandInjection/RFI endpoints) in one 8.5-min window | [QUERY] `docker logs --tail 5000`; [CODE] `ledger/service.py:873` |
| F13 | Failed scans leave zero forensic state | 3 scans `failure_reason=agent_exit_-1_after_0_attempts` + **0 ledger cells**; 1 scan spawn-killed by missing `scanner/zap` image | [QUERY] `16_caps.sql`, `13_q6_phase.sql`; [CODE] `poller.py:594,1425` |
| F14 | Cancelled scans skip finalize → open grid persists | **all 5 big cancelled scans have open_cells 1,298–1,610**; overall 7,957 open applicable cells | [QUERY] `07_q3_perscan.sql`; [UNVERIFIED] exact code reason finalize doesn't run on cancel path |
| F15 | Cost telemetry flat-liners | `cost_cap_usd = 0.00` and `avg(cost_spent_usd) = 0.000` on all 43 scans despite 1.02M+ token runs | [QUERY] `16_caps.sql`; [UNVERIFIED] whether $0 is intentional for local/self-hosted models |
| F16 | Attempt-cap exceeded cells exist | 647 cells with `attempts > 3` (cap default 3) | [QUERY] `17_attempts.sql`; [CODE] `ledger/service.py:1237-1247` |
| F17 | `decisions.log` not machine-timable | 10 and 8 lines, zero timestamps; content is free-form session summaries | [QUERY] workdir `decisions.log`; [CODE contract] `orchestrator.py:44` |
| F18 | `coverage_ledger` / `checkpoints` / `scan_approvals` dead tables | 0, 0, 0 rows | [QUERY] `08_q4_evid.sql`, `22_misc.sql`; [CODE] retired phantom `engine/context.py:15,154` |

---

## 5. Evidence Ledger

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| 43 scans: 19 cancelled / 18 completed / 4 failed / 1 partial / 1 running | [QUERY] `scripts/03_q1_status.sql` → 5 rows | High | live DB |
| Duration median 664 s, max 64,618 s | [QUERY] `scripts/04_q1_dur.sql` | High | `completed_at - created_at` |
| 70,781 ledger cells, 22,011 applicable, 40 scans with cells | [QUERY] `05_q2_state.sql` | High | 3 failed scans have none |
| 8,771 applicable cells terminal-unresolved (`attempted`) = 39.8% | [QUERY] `06_q2b_terminal.sql` | High | = 62.4% of terminal applicable cells |
| `attempted` is terminal-but-unresolved by design | [CODE] `reporting/service.py:123`, `finalize.py:450-467` | High | direct comment + SQL |
| Overall resolved 5,283/22,011 = 24.0%; median per-scan 0.000 | [QUERY] `20_q3_ratio.sql` | High | |
| 11/18 completed scans resolved nothing | [QUERY] `20_q3_ratio.sql` | High | |
| 201 findings verified, only 19 with evidence rows | [QUERY] `08_q4_evid.sql`, `19_chains.sql` | High | counts drift ±few while running scan writes |
| 288/325 evidence rows link to neither cell nor finding | [QUERY] `19_chains.sql` | Medium | snapshot; interpretation of "orphan" is mine |
| chains populated (188 nodes/449 edges) but `executed_chains=0` | [QUERY] `08_q4_evid.sql`, `19_chains.sql`, workdir `report.json` | High | report JSON read from 2 scans only |
| 313 agent messages over 17 scans, avg 18.4 turns, 10/17 ≤ turn 2 | [QUERY] `10_q5_turns.sql`, `12_q5b.sql` | High | |
| worker_runs 59.5% error, 471 "no choices", 73× 429 | [QUERY] inline `worker_runs.error` grouping | High | raise site in repo **[UNVERIFIED]** |
| 99.1% of recent scanner-cp logs are `scan.method_switch` | [QUERY] `docker logs scanner-cp --tail 5000` aggregate | High | 8.5-min window while one scan ran |
| method_switch published per stale testing cell every 180 s | [CODE] `scheduler/poller.py:111,1158-1165` | High | explains flood magnitude |
| 8× `finding_unmatched` warnings with class mismatch | [QUERY] log aggregate; [CODE] `ledger/service.py:873` | High | |
| Median 336 s creation→first ledger write; median activity window 0 s | [QUERY] `18_q6_lag.sql` | High | 0 s ⇒ bulk materialization |
| `coverage_ledger` empty because it is a retired phantom | [QUERY] `08_q4_evid.sql` (0 rows); [CODE] `engine/context.py:15,154` | High | |
| Thrash: 185/221 endpoints re-updated, max 63× (one scan) | [QUERY] in-memory aggregate of `ledger_updates.jsonl` | High | counts only, no content emitted |
| `tested_vulnerable` state emitted by agent, absent from `src/` | [QUERY] workdir aggregate; [Grep] `tested_vulnerable` → no matches | High | resolver skips unknown states `ledger/service.py:767` |
| OOB interaction files are not scan-scoped (pre-scan timestamps, 2 distinct ids) | [QUERY] in-memory aggregate; [CODE] `interactsh.py:11`, `poller.py:1490` | Medium | mirrors whole stream each pass |
| `decisions.log` has no timestamps | [QUERY] in-memory regex over both sampled files | High | 10 & 8 lines |
| cost fields all zero across 43 scans | [QUERY] `16_caps.sql` | High | intent **[UNVERIFIED]** |
| Cancelled big scans keep 1,298–1,610 open cells | [QUERY] `07_q3_perscan.sql` | High | cause **[UNVERIFIED]** |
| Watchdog/spawn/finalize log lines absent from recent scanner-cp window | [QUERY] keyword counts = 0 in 5,000 lines | Medium | they may log to another stream/level |
| Volume name `abhedi_red_scanner_data` holds all 43 workdirs under `<hash>/` | [QUERY] `docker inspect scanner-cp` + `alpine ls` | High | brief's path pattern confirmed |

---

## 6. Reproduction index (local query files)

`scripts/00_schema.sql` … `24_spot.sql` — each file was run via
`Get-Content <file> -Raw | ssh -o BatchMode=yes abhedi 'docker exec -i scanner-postgres psql -U scanner -d scanner -At'`.
Files that intentionally failed on identifier quirks were corrected in place (`07`, `12`, `16`, `19`, `20`); all results quoted above come from the corrected versions.

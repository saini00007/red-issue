# WS-2 — Telemetry forensics: ledger thrash, OOB honesty, model errors, model-driven evidence, feedback loops

**Research agent:** nova-02 · **Mode:** READ-ONLY forensics (local code + `ssh abhedi` SELECT-only SQL + read-only container/file inspection)
**Snapshot:** 2026-10-01 (live DB — counters drift while the running scan writes; all counts "as of" this session)
**Sources:** container `scanner-postgres` (db/user `scanner`, schema `tenant_xbow`, 19 tables, 43 scans), volume `abhedi_red_scanner_data` (`/var/lib/scanner/<hash>/<scan_id>/`), container `scanner-cp` (read-only greps of site-packages + `docker inspect` env), local `src/`.
**Write scope honored:** only this file + NEW `scripts/*.sql` (files 40–54; existing 00–31 untouched). No DB writes, no container lifecycle actions, no target HTTP, no secrets reproduced (the `SCANNER_OOB_TOKEN` / API keys seen in env are NOT copied here).
**Peer dedup:** WS-1b (terminal-cell & throughput forensics) already covers scan/cell state counts, `worker_runs` error classes, message/turn counts, log floods, and the thrash *headline*. Where WS-2 touches that ground it cites the peer's F1–F18 instead of re-deriving, and adds only new mechanism/evidence. New catalog items are F19–F28 in §2.

### Step 0 — method & environment facts

- SQL pattern: write `.sql`, then `Get-Content <file> -Raw | ssh -o BatchMode=yes abhedi 'docker exec -i scanner-postgres psql -U scanner -d scanner -At'`.
- Volume forensics pattern (read-only, throwaway): write LF shell script to `%TEMP%\opencode\ws2\*.sh`, then `Get-Content <f> -Raw | ssh abhedi "tr -d '\r' | docker run --rm -i -v abhedi_red_scanner_data:/d alpine sh -s"` (awk/grep/wc over `ledger_updates.jsonl`, `decisions.log`, `logs/agent.log`, `oob_*.jsonl`).
- Container code/site-packages greps: `tr -d '\r' | docker exec -i scanner-cp sh -s`.
- **Runtime env observed** (`docker inspect scanner-cp`, secrets elided): `SCANNER_ORCHESTRATOR=planner`, `SCANNER_ENGINE_MAX_RETRIES=8` (code default 3 `agents_runtime.py:781`), `SCANNER_ENGINE_VERIFY_WALL_S=1200` (code default 180 `verify.py:67`), `SCANNER_EVIDENCE_GATE=true`, `SCANNER_LEDGER_MACHINE_CLOSE=true`, `SCANNER_LEDGER_STOP_ON_PROBE=0`, `SCANNER_LEDGER_LEASE_S=1800`, `SCANNER_ENGINE_SEAT_MODELS=true`, `SCANNER_ENGINE_FANOUT=8`, `SCANNER_OOB_SERVER=https://oast.abhedi.co.in`. **Absent** (→ code defaults): `SCANNER_LEDGER_ATTEMPT_CAP` → 3, `SCANNER_ENGINE_MAX_TURNS` → 40, `SCANNER_ENGINE_MAX_REPROMPTS` → 6, `SCANNER_ENGINE_RECONNECT_TRIES/SLEEP_S` → 5 × 20 s. (38 matching env lines returned, not truncated.)
- Logger note: structlog events land in each workdir `logs/agent.log` (e.g. `verification.spawned` is visible there), so "0 occurrences" below is a real absence, not a stream artifact.

---

## 1. Per-question findings

### Q1 — Cell-state thrash: does the ledger churn states, and why?

**Data — every `ledger_updates.jsonl` in the volume (19 files, 9,105 lines total), awk grouped by endpoint** (`[QUERY]` temp script `q1_full2.sh`; JSON has `"state": "x"` with a space — an earlier space-less regex read all-zero, corrected):

| scan | lines | eps | %eps written >1× | %eps ≥11 writes | max writes/endpoint | last-write resolved% / testing% | `tested_clean` lines |
|---|---|---|---|---|---|---|---|
| 1f5fe7c8 | 2,032 | 114 | 82.5 | 39.5 | **80** | 29.8 / 70.2 | 149 |
| 68a58881 | 2,481 | 222 | **83.8** | 29.3 | 63 | 40.5 / 59.5 | 618 |
| 84aea81a | 2,041 | 297 | 73.1 | 18.2 | 43 | 40.4 / 59.6 | 210 |
| 0ebea923 | 326 | 101 | 61.4 | 0 | 10 | 8.9 / 91.1 | 29 |
| 373bff88 | 421 | 95 | 57.9 | 11.6 | 21 | 17.9 / 82.1 | 74 |
| 4ebd576b | 493 | 217 | 16.1 | 4.1 | 46 | 100 / 0 | 263 |
| 6c4d84c3 (cancelled) | 325 | 116 | 69.0 | 0 | 10 | **0 / 100** | 1 |
| 947b04f7 | 335 | 107 | 66.4 | 0.9 | 12 | **0 / 100** | 1 |
| dbf83a85 | 124 | 68 | 42.6 | 0 | 7 | 4.4 / 95.6 | 7 |
| others (9 files, ≤115 lines) | 991 | 1–72 | 0–100 | 0–66.7 | 6–47 | mixed | 40 |

- **Agents never author terminal states:** `"state":"attempted"` = **0** and `"state":"na"` = **0** across all 9,105 lines. Terminal states (`attempted`/`na`) are written only by SQL paths (`release_cells`, `reclaim_expired_leases`, finalize retire) — yet they are *not* protected from being reopened (below).
- Overall only **1,391 / 9,105 (15.3%)** update lines carry a resolving state (`tested_clean`); the rest are `testing` re-assertions.
- Cancelled/partial scans (`6c4d84c3`, `947b04f7`) end with **0%** of endpoints last-written as resolved → every endpoint's final self-report is still `testing` (peer F14: cancellation leaves the grid open).

**Mechanism — the reopen loop** (`[CODE] src/scanner/ledger/service.py`):

1. `sync_from_work` (:1034) re-reads **the whole** `ledger_updates.jsonl` on every call; call sites: `entrypoint.py:787` (each reprompt iteration — its own comment: "runs each reprompt iteration"), `finalize.py:252`, `engine/father.py:929` (each wave), `planner/coordinator.py:138` (each planner round), `hooks/stop_gate.py:144` (each Stop, if wired — see Q5).
2. The idempotency guard (:970) skips only `confirmed/tested_clean/blocked/pending_oracle/pending_human` — **not `attempted`, not `na`**. Everything else falls into the sinks at :1004 / :1018 / **:1023** (`cell.state = "testing"`) with `cell.last_progress = now` (:1028).
3. The loader `_load_cells_with_identity` (:700-710) has **no `applicable`/state filter**, and the ledger-update loop (:930-1028) has **no `applicable` check** — so a matched cell in *any* other state is rewritten.
4. A cell flipped `attempted → testing` becomes claimable again (`claim_cells` requires `state IN ('untested','testing') AND applicable AND attempts < cap`, :1399-1404, :1392) → `attempts+1` (:1411) → cap 3 re-absorbs it on release/reclaim (:1460, :1559) → next matching update flips it again. The attempt cap bounds (does not prevent) the cycle.

**Live proof of the sink firing outside its guard:**
- `[QUERY] scripts/49_q1_sink.sql` → cells with `applicable = false` by state: `na 48,322`, **`testing 117`**, **`blocked 139`**, **`tested_clean 191`**. Materialize seeds inapplicable cells **only** as `na` (`state="untested" if applicable else "na"` :688) and `reopen_cells_for_classes` only ever produces `untested` from `tested_clean` (:1112-1113) → the 117 `testing` (and the `blocked`/`tested_clean`) rows on inapplicable cells can only come from the resolve sinks. Same code path that silently reopens `attempted` (state not in the guard tuple).
- `[QUERY] scripts/45_q1_state_attempts.sql` → applicable cells: `attempted 8,771` (532 with `attempts>=3`), `tested_clean 4,674` (511 ≥3), **`testing 2,651` (42 with `attempts>=3`, all `claimed_by NOT NULL`)**, `untested 5,299` (0 ≥3). The 42 over-cap `testing` cells are mid-lease and will absorb to `attempted` at lease expiry (`reclaim_expired_leases` :1554-1565, `release_cells` :1454-1463) — consistent with cap=3 doing its job *when the cell is claimed*; the un-claimable reopen risk comes from the sink (step 2-4), not from claims.
- **Unmatched amplification:** every sync re-logs rows whose `(endpoint, class)` matches no cell (`ledger.resolve.update_unmatched` :949, `finding_unmatched` :873). `[QUERY]` temp `q3_matrix.sh` over 27 `agent.log` files → **12,734** such warning lines total; `68a58881` alone: **9,485** lines (≈7,735 update + 1,750 finding) for only 2,481 source updates ≈ **3.1× re-processing** (≥3 full-file sync passes). `1f5fe7c8` 1,620; `4ebd576b` 1,567.
- DB-side symptom of stale `testing` cells (method_switch event flood, 180 s watchdog) is peer F5 — cited, not re-derived.

**Q1 verdict:** thrash is real and endpoint-level (peer F8 for one scan; table above shows it fleet-wide: 61–84% of endpoints re-written on the four big scans, one endpoint written 80×), *and* there is a state-machine hole: the re-sync path can move terminal-but-unresolved (`attempted`) and `na` cells back to `testing` because the guard list at :970 omits them and nothing checks `applicable`. Net effect: `last_progress` churn, ~3× unmatched-warning amplification, and reopened cells competing for attempt budget.

---

### Q2 — OOB honest classification: is it honest, and does one callback hit deterministically confirm?

**Code chain** (`[CODE] src/scanner/agent_runtime/oob/service.py`, `registry.py`):

- `sync_oob` (:199-301) parses `oob_registry.jsonl` + `oob_interactions.jsonl`, then gates with `correlate(..., since=_registration_floor(wd))` (:218). `_registration_floor` (:151-159) reads **`oob_health.json` → `checked_at`** (written at provisioning ≈ token-registration start); missing file/blank ⇒ `None` ⇒ "identity gate only" (comment :217).
- Dedup: in-memory `_PROCESSED` (:128, checked :236) + DB `OobToken` fired set (:219/:236).
- **Evidence-first:** `_safe_evidence(...)` for every match (:240-257); `if not ok: continue` (:258-261) — a callback whose evidence row can't be written is **not** persisted and **not** confirmed (retried next tick).
- **Unlinked** callbacks (`reg is None` → matched a token but not provably this scan's, `registry.py:193`) get evidence only (:240-247) and are counted `unlinked` (:264-265) — **never appended to `oob_findings`, never confirm anything**.
- **Honest class:** `classify_oob(reg.vuln_class, m.interaction.protocol)` (:77, called :269) derives the vuln class **from the callback protocol, not the agent's label** ("a URL-fetch beacon must confirm ssrf, not the agent's claimed sqli/cmdi cell", comment :271-273). Endpoint comes from the registration (`reg.endpoint`, required at :267).
- Linked matches build `oob_findings` (:274) → one sink-clustered `verified=True` Finding per (scan, host, class), capped (:279-292, write at :489) → `resolve_cells(findings=…, ledger_updates=[])` (:296, and :378 in `sync_deferred`; second `verified=True` at :355).

**So: does one callback hit deterministically flip a cell to `confirmed`?** *Conditionally yes* — and the conditions are exactly the honesty gates. Deterministic iff **all** of: registration exists (else evidence-only) ∧ interaction ≥ `_registration_floor` (else dropped by `correlate`) ∧ token not already fired/processed ∧ evidence write succeeds ∧ the `(reg.endpoint, honest class)` key matches a ledger cell (else `finding_unmatched` `:873`, logged & skipped). Failure of any gate ⇒ no confirm, by design.

**Data:**
- `[QUERY] scripts/50_q2_oob_tokens.sql` → `oob_token` **302 rows, 302 fired (`fired_at NOT NULL`), 0 unfired**; **18 carry `cell_id` (6.0%)**; **141 carry `endpoint` (46.7%)**. Per scan (fired / with cell_id): `1f5fe7c8 156/11`, `84aea81a 52/5`, `68a58881 32/1`, `4ebd576b 13/0`, `947b04f7 6`, `373bff88 4`, `6c4d84c3 4`, then 29 scans ×1.
  - Interpretation: only ~47% of persisted firings even have an endpoint to key a cell on, and only 6% were cell-bound at mint time (`_persist_token` stores `cell_id = reg.cell_id or None` :544). Confirmation is keyed by (endpoint, class) match, not by `cell_id`, so the practical ceiling on confirm-capable firings is **141/302**.
- `[QUERY] scripts/40_q2_oob_window.sql` → across all 43 scans: **`pre_pct = 0.0` of 302 persisted interactions** (every persisted callback ≥ scan `created_at`); first persisted callback lands **12.4–16.9 s** after creation (median ~15 s = provisioning/registration lag), last as late as **+16 h 47 m** (`68a58881`). The floor works on what reaches the DB.
- **But the raw file stream is not scan-scoped** (peer F10, quantified here) — awk over `oob_interactions.jsonl`: `dbf83a85` 4,271 lines / **99.9% pre-scan** / 1 distinct full-id; `68a58881` 4,603 / 92.7% pre / 244 ids; `4ebd576b` 4,381 / 96.0% pre / 132 ids; `1f5fe7c8` 1,089 / 0% pre / 626 ids; `84aea81a` 335 / 0% pre / 48 ids. The pre-scan rows are overwhelmingly empty-id LDAP noise from the shared oracle; the floor (`registry.py correlate since=`) is what keeps them out of the DB.
- **Minted vs fired** (`oob_registry.jsonl` lines vs `oob_token` rows): `dbf83a85` 25/1 (4%), `68a58881` 962/32 (3.3%), `1f5fe7c8` 1,413/156 (11.0%), `4ebd576b` 46/13 (28.3%), `84aea81a` 753/52 (6.9%). Firing rate on registered tokens is single-digit percent except `4ebd576b`.
- **Floor file present?** Temp `q2_health.sh` → `oob_health.json` with `checked_at` exists in **40/44 workdirs** (4 have no file ⇒ floor `None` ⇒ identity-gate-only for those scans, per code comment :217). No `scan_started_at` key is stored (floor compares against `created_at` upstream in `correlate`).
- Only **8 findings** have `detected_by_tool='oob'` (of 259, `[QUERY] scripts/46_q4_model_evidence.sql`) — OOB contributes a small number of *findings*, while the confirm-path work is mostly cell resolution.

**Q2 verdict:** classification is honest by construction (protocol-derived class, registration-identity gate, time floor, evidence-first, unlinked ⇒ never confirms). The honesty *gap* is coverage, not correctness: 94% of fired tokens carry no `cell_id`, ~53% have no endpoint at all, and single-digit percentages of minted tokens ever fire — so the deterministic confirm path, while sound, is exercised by a small minority of callbacks. `[UNVERIFIED]` why ~470 of 626 in-window distinct ids in `1f5fe7c8` never became rows (floor vs `created_at` gap, cross-scan registrations in the shared stream, or evidence-write failures — not separated).

---

### Q3 — Model-driver errors: classified, and are they retried or fatal?

**Per-log error matrix** (`[QUERY]` temp `q3_matrix.sh`, 27 `agent.log` files; `84aea81a` has no `logs/` yet):

| signal | total | where |
|---|---|---|
| `engine.model_http_error` (httpx hook, ≥400) | **1,082** | `1397908a` 976 (**969×429**, 3×500, 4×502), `373bff88` 105 (86×500, 19×429), `1f5fe7c8` 1×502 |
| literal `Too Many Requests` | 5 | `68a58881` |
| `rate limit` (message text) | 927 | `1f5fe7c8` |
| empty response (`empty response`/`no choices`) | **56** | `1f5fe7c8` 52, `dbf83a85` 4 |
| `verification.spawned` / `verification.failed` | **1,055 / 1,016 (96.3% fail)** | `68a58881` 524, `1f5fe7c8` 438, `4ebd576b` 47, `373bff88` 4, `dbf83a85` 3 |
| `Max turns (…) exceeded` | 949 (of the 1,016) | 511+387+47+4 per scan above |
| `ledger.resolve.*unmatched` | 12,734 | see Q1 |
| context overflow / timeout / connection error | **0 / 0 / 0** | — |
| `agent.rate_limited`, `agent.context_reset`, `worker.reconnect` in logs | **0 / 0 / 0** | `worker.reconnect` = **1 ever** in `scan_events` (`[QUERY] scripts/51_q3_events.sql`) |
| error-level lines | 1,015 | `68a58881` 524, `1f5fe7c8` 439, `4ebd576b` 47, others ≤4 |
| `decisions.log`: turn lines / `max_turns_exceeded` / `Session Summary` | 367 / **237** / **1** | mte: `1f5fe7c8` 135, `84aea81a` 90, others ≤4; the single `Session Summary` is `dbf83a85` |

**Classification vs retry semantics** (`[CODE]`):

1. **HTTP 429/5xx — retried, but storms still starve scans.** Logged by the httpx response hook `_log_model_http_error` (`agents_runtime.py:70-79`, attached :764-768); retried inside the OpenAI client `max_retries` (jittered backoff; code default 3 :769-783, **effective 8 via env**); legacy path additionally backs off 429-only ×4 in `_receive_with_retry` (`entrypoint.py:470-483`, logs `agent.rate_limited` — never seen in logs). Evidence the retry budget is insufficient: **scan `1397908a` = 969×429 + 86×500-class errors inside a 2,034-line log, 4 messages, 0 findings** — rate-limit-saturated to zero output.
2. **Connection drops — retried hard, but almost never happen.** `_is_connection_error` (:82-89) → outer loop `_run_with_reconnect` ≤5 × 20 s (:892-915, emits `worker.reconnect`). Observed **once ever** → not the failure mode.
3. **HTTP-200-with-empty-choices — bypasses every retry layer, fatal.** Raise site found in the deployed SDK (read-only grep of `scanner-cp` site-packages): **`agents/models/openai_chatcompletions.py:261`** raises `ModelBehaviorError("ChatCompletion response has no choices (possible provider error payload)…")` *after* the OpenAI client returned success ⇒ the client's `max_retries` never engages; the exception propagates to `AgentsRuntime.run` → generic handler returns `WorkerResult(status="error")` (:823-830) — **no retry, worker dead**. This supplies the missing raise site for peer F3 (471 `worker_runs` errors of this string). In `agent.log` it surfaces only where callers catch it: `verification.failed` (56) and `close_sweep.failed`.
4. **MaxTurns — soft-stop for workers, fatal-for-verifier for checks.** `MaxTurnsExceeded` is caught and reprompted for workers (:816-822; cap `SCANNER_ENGINE_MAX_REPROMPTS` → 6, :809; `decisions.log` gets a `max_turns_exceeded` line via `_record_turn` :442-445, 237 observed). But the **independent verifier** runs with `max_turns = 12` (`verify.py:68`) and wall 1200 s (`verify.py:67`, env), and `execute_fn` (`verify.py:99`) lets the exception propagate to `spawn_verification` which **fails open**: log `verification.failed` + return `verifier_unavailable`, never retried, never blocks finalize (`hooks/verification.py:234-241`). **949 of 1,016 verification failures are "Max turns (12) exceeded" ⇒ 96.3% of spawned verifications produced no verdict** (`verification.spawned` 1,055 vs `failed` 1,016).
5. **Tool errors — soft.** `tool_not_found_behavior: return_error_to_model` (:887-889): tool failures are handed back to the model, not fatal (tool-level rates are peer F9).
6. **Context/429 resilience features never observed:** `agent.rate_limited` (0), `agent.context_reset` (0; feature exists at `entrypoint.py:129-152`, threshold 150k tokens) — these live on the legacy claude-SDK path; the observed fleet runs the agents/planner path.

**Q3 verdict:** the fleet's real killers are provider payload/HTTP errors, which come in two species — 429/5xx (retried, but 969-hit storms still zero out a scan) and 200-empty-choices (structurally un-retried → fatal worker error). Verification, the honesty backstop, fails closed-quietly 96% of the time on its own turn cap while the code treats it as fail-open. Connection resets — the thing the retry machinery was built for — happen once.

---

### Q4 — Model-driven evidence: how much of the evidence is actually model-driven?

**Model activity** (`[QUERY] scripts/43_q4_models.sql`, `48_q4_msgshape.sql`, `53_q4_perscan_msgs.sql`):
- `agent_messages` = **~348–352 rows, all `role=assistant`, only 17 of 43 scans have any** (peer F4 territory; here used for correlation, not re-counted).
- Model mix (rows / distinct scans / tokens_in): **`stealth/space-bunny-alpha` 304 / 8 / 43.5M**, `gpt-5.6-luna` 22 / 1 / 0.96M, `nvidia/nemotron-3-ultra-550b-a55b` 7 / 2 / 2.6M, `dots-studio/dots-3-note-preview:free` 5 / 1 / 2.56M (120k out), `nemotron-3-super-120b` 5 / 2 / 0 tokens recorded, `z-ai/glm-5.3` 1, `nemotron-3-ultra-550b:free` 1, `deepseek/deepseek-v4.1-flash` 1. `[UNVERIFIED]` how `space-bunny-alpha` wins seats when `SCANNER_ENGINE_MODELS` lists only the nemotron seat (seat-binding logic elsewhere).
- Per-scan messages (top): `1f5fe7c8` 139 (55 distinct agent ids), `84aea81a` 97, `4ebd576b` 55, `218770b1` 22 … down to 7 scans with exactly **1** row (incl. `68a58881`, `dbf83a85` — scans with 38/13 findings but a single model-telemetry row). `max(turn_index)` = **7 fleet-wide** → ≤8 `Runner.run`s per worker (1 initial + ≤6 reprompts + …; `_turn_index` is a per-runtime counter, `agents_runtime.py:459`), each run internally capped at 40 model turns (:798).
- Tokens: avg **149,991 in / 2,479 out**, max **1,858,256 in / 95,629 out**; **`sum(cost_usd) = 0.0000`** → message-level cost metering is dead too (extends peer F15).

**Turns vs findings** (`[QUERY] scripts/44_q4_corr.sql`, `47_q4_turns_findings.sql`):
- **corr(turns, findings) = 0.224 (n=17)** — positive but weak.
- 8-run scans: `84aea81a` 45 findings, `1f5fe7c8` 25, `4ebd576b` 15, `218770b1` 0. 2-run scans: `68a58881` **38**, `373bff88` 26, `0ebea923` 26, `dbf83a85` 13. **A 2-run scan out-finds three 8-run scans** → finding output is driven by the deterministic floor/tools and cell inventory, not by how long the model ran.
- 3 of the 26 zero-telemetry scans have findings anyway (findings exist with no model-turn record).

**Evidence provenance** (`[QUERY] scripts/46_q4_model_evidence.sql`, 259 findings live):
- `detected_by_agent`: **`orchestrator` 241, NULL 18** — a single constant label; there is **no per-model/per-worker attribution** in the findings table.
- `detected_by_tool` (complete list): `(none) 105`, **`curl 59`**, `rate-limit 57`, `zap 13`, `hygiene 10`, `oob 8`, `sqli-boolean 3`, `dalfox 2`, `nofamily 1`, and **1 free-text row**: `"live OOB callback; persisted via manual append because write_finding() failed with Errno 13 Permission denied on /work/findings.jsonl"` → (a) free prose is accepted into a tool-name column, (b) first-hand evidence of a **`write_finding` Permission-denied** failure mode (NEW F26).
- `evidence_paths`: **205/259 non-empty (79.2%)**; verified × evidence: `true+has 155`, **`true+no evidence 51 (24.8% of the 206 verified)`**, `false+has 50`, `false+no 3`.
- Tool phase attribution: `tool_invocations` = **37,190 rows, `phase_id` NULL on 37,190/37,190 (100%)** (`[QUERY] scripts/41/54`), success 33,539 / failed 3,651 (9.8%). Time-window join to `scan_phases` (`scripts/42_q4_phasejoin.sql`): exploitation owns virtually everything (curl 15,255 succ, upload 3,481/614 fail, oob 2,520/607, sqlmap 1,728/417, python3 2,233) vs reconnaissance's entire visible top-6 = 474 rows (curl 154, cat 85, ls 78, grep 72, find 49, python3 36). Caveat: the join fans out overlapping windows — exploitation `curl` 15,255 > global 14,932 ⇒ **~2–4% double-count**, use ratios not absolutes.

**Q4 verdict:** evidence is only weakly model-driven in the measurable senses: turn count explains ~5% of finding variance (r=0.224), attribution is one constant string (`orchestrator`), phase linkage for tool evidence is null by column (time-join required), 24.8% of verified findings carry no evidence path, and cost is reported as $0 over ~52M input tokens. The heavy lifting is the deterministic floor/exploit tooling (exploitation-phase concentration above), with the model acting as orchestrator + probe author.

---

### Q5 — Feedback loop: what loops actually exist, and is one broken?

**Loops that exist (all within a single scan):**

| # | Loop | Code |
|---|---|---|
| L1 | **Blackboard handoff across workers:** `claim_cells` returns `prior_methods` + `attempt` for re-claimed cells ("the last worker's effort carried forward") | `ledger/service.py:1429-1441`; rendered into the next task as *"[attempt N; prior workers tried: … — go DEEPER or a DIFFERENT technique]"* `engine/father.py:360-367` |
| L2 | **Ledger → wave brief → task:** coverage board + open-cell worklist + plan digest prepended each wave; brief rebuilt from live `/work` every wave (caps `_MAX_ENDPOINTS=30` etc.) | `father.py:382-406` (`_render_board_totals`), `:351-372` (`_worklist_text`), `:597` (`_task_for`), `scan_brief.py:1-12,30-34,249`; call sites `father.py:1266,1504,1558,1709,1781` |
| L3 | **Ledger sync per wave/round/reprompt:** `sync_from_work` re-ingests findings + updates | `father.py:929`, `planner/coordinator.py:138` (planner round; also persists specialist turns :139-154 — the fix that made `agent_messages` non-empty), `finalize.py:252`, `entrypoint.py:787` (each reprompt iteration) |
| L4 | **Stateful reprompt:** transcript replay (capped) + scope re-assert + live progress digest re-read from `findings.jsonl`/`ledger_updates.jsonl` every reprompt | `agents_runtime.py:962-994` (`_reprompt`, replay :988-991, cap :212-222), `:996-1008` (`_scope_block`), `:1010-1021` (`_progress_digest`), stop decision `:942-960` (`_offensive_gate`) |
| L5 | **Exploit-floor signal triage:** pending floor signals block weapon-swept closes and inject a triage directive | `ledger/service.py:984-987`, `father.py:327-348` (`_signal_triage_directive`) |
| L6 | **Plan feedback:** boss proposes, gate validates, prior plan stands on failure; objectives carry forward | `plan_gate.py:32-47`, `plan.py:56-95`, `father.py:1160-1166` |
| L7 | **Attempt-budget feedback:** attempts+1 on claim, cap 3 retires to `attempted`, `prior_methods`/attempt surface to the next claimer | `service.py:1399-1415`, `:1454-1463`, `:1554-1565`, `:1237-1247` |

**Loops that are broken / absent:**

- **B1 — the Stop-gate (ledger → "stop only when covered") never fires.** `[QUERY]` temp `q5_events.sh` + `q5_stopgate2.sh` over 27 logs: `stop_gate.block` **0**, `stop_gate.allow_complete` **0**, `stop_gate.partial_guardrail` **0**, `stop_gate.ledger_read_failed` **0**. The Stop hook is built only in the claude-SDK options builder (`entrypoint.py:687-713`, registered at :713); the claude runtime registers only Pre/PostToolUse hooks (`engine/runtimes/claude_sdk.py:146-149`) and the agents runtime registers none — so `hooks/stop_gate.py:141-157` (sync-on-Stop + block-while-open) has no registration point on the observed fleet. Termination instead comes from `_offensive_gate` + reprompt cap + finalize. `[UNVERIFIED]` whether this is deliberate for the planner orchestrator.
- **B2 — no cross-scan learning whatsoever.** `engine/context_memory.py` defines `MemoryStore` + `engine_memory` pgvector table (:11, :35, :44) but a repo-wide grep finds **zero instantiations/imports** — dead code. `scan_brief` is rebuilt only from the current scan's live `/work` (`scan_brief.py:1-12`). Every scan starts cognitively blank.
- **B3 — the unmatched-key feedback channel is one-way (server log only).** Agents author ledger keys that match no cell; the resolver logs `update_unmatched`/`finding_unmatched` and skips (`service.py:767` docstring, :873, :949) — **12,734 warning lines** (Q1) — but nothing surfaces "your key matched nothing" back into the model's next task beyond the coarse board/worklist at the next wave. Result: same unmatched keys re-emitted across ≥3 sync passes (~3.1× amplification on `68a58881`).
- **B4 — verification feedback is fail-open noise.** 96.3% of verifications die on their own turn cap (Q3) and return `verifier_unavailable`; the finding keeps whatever `verified` flag it already carries (`hooks/verification.py:236-241`), so the "independent check" loop mostly transmits nothing.
- **B5 — cost/budget feedback is inert.** `cost_usd` sums to 0.0000 in `agent_messages` and `cost_spent_usd=0` fleet-wide (peer F15), so any budget-based stop (`_guard.budget_remaining` checked at `agents_runtime.py:836`) has no real signal behind it; `SCANNER_ENGINE_BATCH_BUDGET_S=0` (unbounded) as well.

**Q5 verdict:** within-scan feedback is richly engineered (L1–L7: blackboard handoff, briefs, stateful reprompts, plan gate, attempt budget) and demonstrably active. The *control* loops — stop-gate (B1), independent verification (B4), cost/budget (B5) — never engage, and the *learning* loop across scans (B2) does not exist. The one feedback channel that fires constantly (unmatched warnings, B3) is written only where the model cannot see it.

---

## 2. Observed-failure catalog — additions to peer F1–F18

| # | Failure mode | Aggregate metric | Evidence | Relation |
|---|---|---|---|---|
| **F19** | Stop-gate coverage feedback inert on the running fleet | 0 `stop_gate.*` events across 27 `agent.log`; hook only registered in claude-SDK options builder | [QUERY] temp `q5_events.sh`/`q5_stopgate2.sh`; [CODE] `entrypoint.py:687-713`, `claude_sdk.py:146-149`, `hooks/stop_gate.py:141-183` | NEW |
| **F20** | Independent verification fails open ~96% of the time | **1,016 / 1,055 spawned verifications failed; 949 = "Max turns (12) exceeded"** | [QUERY] temp `q3_matrix.sh`; [CODE] `verify.py:67-68,99`, `hooks/verification.py:234-241` | NEW (peer F6 shows multi-path `verified=True`; this is the verifier itself) |
| **F21** | HTTP-200-empty-choices bypasses all retry layers → fatal worker error | raise site `agents/models/openai_chatcompletions.py:261` (`ModelBehaviorError`); 471 such `worker_runs` errors (peer), 56 caught in `agent.log` | [QUERY] read-only grep in `scanner-cp` site-packages; [CODE] `agents_runtime.py:823-830` | supplies raise site for peer **F3** |
| **F22** | Resolve sinks rewrite terminal `attempted`/`na` cells back to `testing` (guard omits them; no `applicable` check) | **117 inapplicable cells live in `testing`** (+139 `blocked`, +191 `tested_clean` on `applicable=false`); `attempted`/`na` appear 0× in 9,105 agent updates | [QUERY] `scripts/49_q1_sink.sql`, temp `q1_full2.sh`; [CODE] `service.py:970`, `:700-710`, `:930-1028`, `:688` | mechanism behind peer **F8** thrash, extends peer **F1** |
| **F23** | Unmatched-key amplification: full-file re-sync re-logs unmatched rows every pass, model never sees it | **12,734** unmatched warning lines; `68a58881` 9,485 vs 2,481 source updates ≈ 3.1× | [QUERY] temp `q3_matrix.sh`; [CODE] `service.py:873,949`; sync sites `entrypoint.py:787`, `father.py:929`, `coordinator.py:138`, `finalize.py:252` | NEW |
| **F24** | Provider 429/5xx storms starve a whole scan despite retries | `engine.model_http_error` **1,082 lines**; `1397908a` = **969×429** in 2,034 log lines → 4 msgs, 0 findings | [QUERY] temp `q3_matrix.sh`; [CODE] `agents_runtime.py:70-79,769-783` | log-level complement to peer **F3** |
| **F25** | Message-level cost telemetry flat-lines | `sum(agent_messages.cost_usd) = 0.0000` over ~52M tokens_in | [QUERY] `scripts/43_q4_models.sql`, `25_q4_agent.sql` | extends peer **F15** |
| **F26** | Free-text into `detected_by_tool` + `write_finding` Permission-denied | 1 finding row carrying prose `"...write_finding() failed with Errno 13 Permission denied on /work/findings.jsonl"`; `rate-limit` (57) / `curl` (59) as "tools" | [QUERY] `scripts/46_q4_model_evidence.sql` | NEW |
| **F27** | Resilience features unobservable/unused: `agent.rate_limited`, `agent.context_reset` = 0/27 logs; `worker.reconnect` = 1 ever | 0, 0, 1 | [QUERY] temp `q3_matrix.sh`, `scripts/51_q3_events.sql`; [CODE] `entrypoint.py:470-483,129-152`, `agents_runtime.py:892-915` | NEW |
| **F28** | OOB confirm path is sound but narrow: 94% of fired tokens carry no `cell_id`, ~53% no endpoint; mint fire-rate 3–28% | `oob_token` 302: cell_id 18, endpoint 141; minted/fired `1413/156`, `962/32`, `753/52`, `25/1`, `46/13` | [QUERY] `scripts/50_q2_oob_tokens.sql`, `40_q2_oob_window.sql`; [CODE] `oob/service.py:199-301,544` | quantifies/extends peer **F10** |

Also new but reported in Q4 rather than the catalog: `phase_id` NULL on 100% of `tool_invocations` (37,190/37,190) → phase attribution requires a lossy time-join (NEW, informational); `corr(turns,findings)=0.224` and 3 findings-only scans with zero model telemetry (extends peer **F4**).

---

## 3. Evidence Ledger

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| 9,105 ledger-update lines across 19 workdirs; endpoint repeat rates 61–84% on big scans; max 80 writes/endpoint | [QUERY] awk (temp `q1_full2.sh`) over volume `ledger_updates.jsonl` | High | JSON `"state": "x"` spacing matters — earlier space-less regex read 0 |
| Agents author 0 `attempted` and 0 `na` states | [QUERY] same awk (`attempted`=0, `na`=0 all files) | High | terminal states come only from SQL paths |
| Guard at `service.py:970` omits `attempted`/`na`; update loop has no `applicable` check; loader loads all cells | [CODE] `service.py:970`, `:930-1028`, `:700-710` | High | direct read |
| 117 inapplicable cells sit in `testing` (+139 blocked, +191 tested_clean) — impossible from materialize/reopen alone | [QUERY] `scripts/49_q1_sink.sql`; [CODE] seeds at `:688`, reopen `:1112-1113` | High | inference from exclusive write paths, stated |
| 42 applicable over-cap (`attempts>=3`) cells in `testing`, all claimed (in-flight absorption) | [QUERY] `scripts/45_q1_sink.sql` | High | live snapshot |
| ~3.1× re-processing of updates (9,485 unmatched log lines vs 2,481 source lines, `68a58881`); 12,734 fleet-wide | [QUERY] temp `q3_matrix.sh` | Medium-High | ratio is inferred from line counts (findings lines also logged per pass) |
| OOB confirm chain: floor (`oob_health.checked_at`) → dedup → evidence-first → unlinked⇒no-confirm → protocol-honest class → `resolve_cells(findings…)` | [CODE] `oob/service.py:151-159,218,236,240-265,269-296,378` | High | direct read |
| 302 `oob_token` rows, all fired, 18 cell_id (6.0%), 141 endpoint (46.7%) | [QUERY] `scripts/50_q2_oob_tokens.sql` | High | live; counts drift +4 rows vs earlier snapshot same session |
| 0% of persisted OOB interactions pre-date scan `created_at` (n=302); first callback +12–17 s | [QUERY] `scripts/40_q2_oob_window.sql` | High | vs raw files 92–99.9% pre-scan for 3 older scans |
| `oob_health.json` with `checked_at` present in 40/44 workdirs | [QUERY] temp `q2_health.sh` | High | 4 workdirs ⇒ floor `None` |
| Minted/fired rates: 4%, 3.3%, 11.0%, 28.3%, 6.9% (5 sampled scans) | [QUERY] `oob_registry.jsonl` line counts vs `oob_token` | Medium | two snapshots at slightly different times |
| Empty-choices raise site = Agents SDK `ModelBehaviorError` (post-200 check) → retries never engage → fatal | [QUERY] read-only grep `scanner-cp` site-packages; [CODE] `agents_runtime.py:823-830` | High | fixes peer F3's `[UNVERIFIED raise site]` |
| 1,016/1,055 verifications failed (96.3%); 949 = MaxTurns(12) | [QUERY] temp `q3_matrix.sh` | High | counts per scan sum exactly |
| `1397908a`: 969×429 + 3×500 + 4×502 in 2,034 lines, 4 messages, 0 findings | [QUERY] temp `q3_matrix.sh` + `scripts/47`/`53` | High | strong circumstantial: rate-limit → no output |
| `worker.reconnect` fired exactly once ever; `agent.rate_limited`/`agent.context_reset` never | [QUERY] `scripts/51_q3_events.sql` + 27 logs | High | |
| Stop-gate never logged any of its 4 events | [QUERY] temp `q5_events.sh`/`q5_stopgate2.sh` | High | logger proven to reach `agent.log` via `verification.spawned` |
| Stop hook registered only in claude-SDK options builder; agents runtime has no Stop hook | [CODE] `entrypoint.py:687-713`, `claude_sdk.py:146-149`, `agents_runtime` (none) | High | |
| `MemoryStore` dead (zero instantiations) | [Grep] `src/` for `MemoryStore(`/`context_memory` → only self-references | High | cross-scan loop absent |
| corr(turns,findings) = 0.224 (n=17); 8-run scans 0–45 findings vs 2-run scans 0–38 | [QUERY] `scripts/44_q4_corr.sql`, `47_q4_turns_findings.sql` | High | only 17/43 scans have turns |
| `detected_by_agent` constant `orchestrator` (241/259); tool list complete incl. 1 prose row | [QUERY] `scripts/46_q4_model_evidence.sql` | High | 10 distinct tool values summing to 259 ⇒ complete |
| 205/259 findings have `evidence_paths`; 51 verified findings have none (24.8%) | [QUERY] `scripts/46_q4_model_evidence.sql` | High | differs from peer's `evidence_object` count (19) — different column |
| `phase_id` NULL on 37,190/37,190 tool invocations; success 33,539 / failed 3,651 (9.8%) | [QUERY] `scripts/41/54` | High | live |
| Phase time-join inflates counts ~2–4% (curl 15,255 joined vs 14,932 total) | [QUERY] `scripts/42` vs `41/54` | High | use ratios from join, not absolutes |
| `sum(agent_messages.cost_usd)=0` over ~52M tokens_in | [QUERY] `scripts/43_q4_models.sql` | High | intent `[UNVERIFIED]` (peer F15 note) |
| Env: `SCANNER_ORCHESTRATOR=planner`, `MAX_RETRIES=8`, `VERIFY_WALL_S=1200`; attempt cap / max turns / reprompts unset → 3/40/6 | [QUERY] `docker inspect scanner-cp` env (38 matching lines, not truncated; secrets elided) | High | |
| `max(turn_index)=7` fleet-wide → ≤8 Runner.runs per worker | [QUERY] `scripts/48_q4_msgshape.sql` | High | `_turn_index` is per-runtime counter (`agents_runtime.py:459`) |
| Why ~470 of 626 in-window distinct OOB ids (`1f5fe7c8`) never persisted | — | — | `[UNVERIFIED]` — floor-vs-created_at, cross-scan stream, or evidence-write failures not separated |
| Why `space-bunny-alpha` holds 304/352 message rows while `SCANNER_ENGINE_MODELS` lists only nemotron | — | — | `[UNVERIFIED]` seat-binding logic not located this session |
| Whether Stop-gate absence is intentional under the planner orchestrator | — | — | `[UNVERIFIED]` |

---

## 4. Reproduction index

**New SQL files (this WS; run via `Get-Content <file> -Raw | ssh -o BatchMode=yes abhedi 'docker exec -i scanner-postgres psql -U scanner -d scanner -At'`):**

- `scripts/40_q2_oob_window.sql` — persisted OOB interactions vs scan `created_at` (pre-scan %, offsets)
- `scripts/41_q4_toolphase.sql` — tool × status top-N + `phase_id` null count + sample `scan_phases` windows
- `scripts/42_q4_phasejoin.sql` — tool × status by phase via time-window join (fan-out caveat)
- `scripts/43_q4_models.sql` — messages by model, findings `evidence_paths` empty/nonempty, verified × evidence
- `scripts/44_q4_corr.sql` — corr(turns, findings), scans-with-turns vs total
- `scripts/45_q1_state_attempts.sql` — applicable cells by state × `attempts>=3`
- `scripts/46_q4_model_evidence.sql` — `detected_by_agent`, complete `detected_by_tool` list, evidence/verified matrix
- `scripts/47_q4_turns_findings.sql` — per-scan turns vs findings (self-contained CTE)
- `scripts/48_q4_msgshape.sql` — msgs / max(turn_index) / agents per scan, totals
- `scripts/49_q1_sink.sql` — inapplicable cells by state; over-cap `testing` split by claim
- `scripts/50_q2_oob_tokens.sql` — `oob_token` totals, cell_id/endpoint coverage, per scan
- `scripts/51_q3_events.sql` — `scan_events` by type (incl. `worker.reconnect`)
- `scripts/52_q5_events.sql` — stop/verification event types in `scan_events`
- `scripts/53_q4_perscan_msgs.sql` — per-scan message counts
- `scripts/54_q4_toottot.sql` — tool status totals + `phase_id` null count

**Read-only shell passes (temp scripts, `%TEMP%\opencode\ws2\`, piped to the throwaway alpine container):**

- `q1_full2.sh` — per-scan endpoint repeat/thrash table over every `ledger_updates.jsonl` (Q1)
- `q3_matrix.sh` — per-log error matrix over 27 `agent.log` files (Q3)
- `q3_precise.sh`, `q3_events.sh`, `q3_decisions.sh`, `q3_decs2.sh` — targeted retry/context/decision counters
- `q2_health.sh` — `oob_health.json checked_at` presence (Q2)
- `q5_events.sh`, `q5_stopgate2.sh` — stop-gate & verification counters (Q5)
- `grep_openai*.sh`, `grep_payload.sh`, `grep_ctx.sh`, `find_openai.sh` — `docker exec scanner-cp sh -s` greps that located the empty-choices raise site and `MaxTurnsExceeded` message
- Env: `docker inspect scanner-cp --format '{{range .Config.Env}}{{println .}}{{end}}' | grep …` (secrets not reproduced)

**Prior WS files read (never modified):** `ws1/WS-1b-terminal-cells-server.md` (peer F1–F18 cited), `notes/NOTES.md`.

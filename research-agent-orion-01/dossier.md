# Engine-v2 Telemetry ↔ Code Correlation Report
**Agent:** research-agent-orion-01 · **Date:** 2026-10-01 · **Mode:** read-only code correlation against provided live-telemetry summary (no live queries run)

Scope note: I did not modify any file, run docker/db commands, or execute payloads. All claims below are either `[CODE file:line]`, `[QUERY]` (using only the numbers supplied in the task, never re-queried), `[INFER]` (explicitly labeled), or "not found in repo."

---

## Q1 — The zombie-scan pattern

**Claim, falsified: this is not evidence the DB row "was never moved to a terminal status."** `'partial'` is a first-class *terminal* status in this codebase, not a stuck/running state:

- `graceful_terminal_status()` returns only `"completed"` or `"partial"` as the scan's final verdict `[CODE src/scanner/ledger/service.py:1207]`.
- `finalize.py`'s own status-reconcile function treats `partial` as terminal output, alongside `completed` — only `failed` rows are eligible for promotion `[CODE src/scanner/agent_runtime/finalize.py:516-546]`.
- The public API groups it with the other two genuinely-dead states: `_RESUMABLE_STATES = ("failed", "partial", "cancelled")` `[CODE src/scanner/api/routes/scans.py:420]`.
- Every single code path in the poller that can produce `status="partial"` (clean exit, "orphan-finalize-from-disk", ledger-resume-exhausted, and "coverage salvage" after exit 137) **also** sets `scan.completed_at = datetime.now(UTC)`, pops the scan out of `self._tracked`, and calls `await self.concurrency.release(tracked.mode)` in the same transaction `[CODE src/scanner/scheduler/poller.py:1309-1329 (clean), :1332-1355 (orphan-finalize), :1391-1422 (salvage), :1424-1440 (failed)]`.

So a `partial` scan with a long-gone container and a heartbeat frozen 10 days ago is the *expected residual shape* of a scan that finished (in the degraded sense) 10 days ago and was correctly torn down and untracked at that time — not a live defect, assuming `completed_at` on that row is in fact ~10 days old (I could not verify this — see Evidence Ledger; the raw telemetry didn't include `completed_at`, only heartbeat staleness).

**What the liveness/heartbeat machinery is actually *for*.** Two independent mechanisms exist, and neither is "detect my own dead agent container while I'm still healthy":

1. **Node-death failover**, not container-death detection: `_recover_dead_node_scans()` re-queues a `status='running'` row only when `node_id IS NOT NULL AND node_id != :my_node AND last_heartbeat_at < now-5min`, or the legacy `node_id IS NULL AND started_at < now-2h` orphan case `[CODE src/scanner/scheduler/poller.py:718-745]`. On this platform's actual deployment — "Docker-composed on single VM" `[DOC CLAUDE.md "Project"]` — every scan's `node_id` equals the one node's own id, so the `node_id != my_node` branch can *structurally never fire* here; this sweep exists for a multi-node future, not this deployment.
2. **Live-node container-death detection** is `watch_once()`'s per-tick Docker inspect of `self._tracked`: `docker.errors.NotFound` (container removed) is explicitly handled and routed to `_on_scan_exit(success=False, exit_code=-1)` with the comment "treat as a crashed agent so it's routed to resume-or-fail instead of being left stuck 'running' forever" `[CODE src/scanner/scheduler/poller.py:1231-1247]`. This *is* the real "my own agent died" detector — but it only inspects scans present in `self._tracked`, which is populated only for `status IN ("running","cancelling","closing","killing")` at boot (`_reconcile_on_boot`, `[CODE poller.py:213-287, filter at :241]`) or at spawn time. Once a scan reaches `partial`/`completed`/`failed` it is deliberately dropped from `_tracked` and stops being watched or heartbeated — again, by design, not a gap.

**The real, narrower gap** (already flagged in this repo's own tracked issues, and confirmed by my own reading, not new): if a scan is *still* `status='running'` on the *same* node when scanner-cp restarts, `_reconcile_on_boot` should re-adopt it (its filter includes `"running"`). If it is somehow NOT re-adopted (e.g. status drifted to something outside that filter list without going through `_on_scan_exit`), the same-node dead-node reaper above can never rescue it, because of the `node_id != my_node` guard. That is a real, distinct residual risk — but it is a **different** failure shape (a scan permanently stuck at `status='running'`) than the one in the telemetry (`status='partial'`), so it does not explain this specific "zombie."

**Verdict on Q1:** REFUTED as literally framed. `partial` is terminal-by-design; the observed row is consistent with a normal (if coverage-degraded) completion, not a live defect. [CONFIDENCE: high on the terminality claim (multiple independent code sites agree); medium on "this specific row is benign," since I could not check its `completed_at`/`node_id` values.]

---

## Q2 — Does a pure upstream-provider failure inflate the attempts counter? **Yes, confirmed.**

`attempts` is incremented **at claim time**, before the worker does any work at all:

```
UPDATE ledger_cell u SET ... attempts = u.attempts + 1 ...
```
`[CODE src/scanner/ledger/service.py:1393-1416, increment at :1411]`

The default attempt cap is only **3** claims before a cell is permanently retired into the terminal `'attempted'` state (`_attempt_cap()`, default `SCANNER_LEDGER_ATTEMPT_CAP=3`) `[CODE src/scanner/ledger/service.py:1237-1247]`, and this absorption happens in `release_cells`/`release_cells_by_ids`, run from the fleet's `on_done` hook on **every** worker exit — `ok`, `partial`, `error`, or `preempt` alike `[CODE src/scanner/agent_runtime/engine/father.py:1345-1362 ("the instant a worker finishes (ok/partial/error/preempt)"), src/scanner/ledger/service.py:1444-1473]`.

Now trace what happens on the specific upstream failure named in the telemetry, `"ChatCompletion response has no choices (possible provider error payload)"`:

- The reconnect wrapper only retries **connection**-class errors: `_is_connection_error()` matches only `"connection error"`, `"connection reset"`, `"connection aborted"`, `"timed out"`/`"timeout"` substrings `[CODE src/scanner/agent_runtime/engine/runtimes/agents_runtime.py:82-89]`. A "no choices" message matches none of these, so `_run_with_reconnect` does **not** retry it — it propagates straight up `[CODE agents_runtime.py:892-915, "MaxTurnsExceeded and non-connection errors propagate untouched"]`.
- In the outer reprompt loop, any non-`MaxTurnsExceeded` exception is caught and turned into `WorkerResult(status="error", ...)` **immediately** — before `attempts += 1`'s sibling bookkeeping, before `_record_turn`, before any tool call, before any actual probe of the target `[CODE agents_runtime.py:812-830]`.
- That `WorkerResult` still flows to the fleet's `on_done` → `_release_worker_cells`, which releases the worker's claimed cells and, because `_attempt_cap()>0`, converts any cell that has now hit the cap straight to `state='attempted'` `[CODE father.py:1345-1362; ledger/service.py:1459-1463]`.

So: a worker that died on turn 0 with zero real HTTP requests against the target consumes exactly one "attempt" per cell it had claimed, indistinguishable in the ledger from a worker that spent 40 real turns genuinely probing and found nothing. With cap=3, **three consecutive provider garbage-payload crashes are enough to permanently retire a cell as `'attempted'` having never been tested once.**

This directly explains the shape of the numbers given: `attempted(capped)=8771` exceeding `confirmed+tested_clean=5159` combined, and specific classes (`ssi`, `quota_abuse`, `workflow_abuse`) showing hundreds of attempt-capped cells with **zero** `tested_clean` and **zero** `confirmed` — a pattern fully consistent with cells being exhausted by claim-churn against a provider that was failing ~53% of the time (`worker_runs: error=578`, dominated by this one message, itself concentrated on one model: `openrouter/stealth/space-bunny-alpha` used in 594/~970 runs). [INFER — I did not query per-cell `attempts` history for these specific classes; the telemetry's own alternate explanation ("no negative/clean oracle exists for these classes") is equally consistent with the same numbers and is not mutually exclusive — both can be true simultaneously.]

**Verdict on Q2:** CONFIRMED. This is a real, code-verified defect: the ledger's "attempt" accounting has no distinction between "a worker genuinely tried and failed" and "a worker's LLM call crashed with zero effort" — both cost the cell one of its 3 lives.

---

## Q3 — What writes `decisions.log`, and is `max_turns_exceeded` the only category?

There are **two different files** named `decisions.log` in this codebase — worth flagging because it's easy to conflate them:

1. `/work/guard/decisions.log` — a JSONL audit trail of every `guard_tool_call` allow/deny verdict, gated behind `SCANNER_ENGINE_GUARD_LOG` (not shown as default-on anywhere I found) `[CODE src/scanner/agent_runtime/engine/guardrails.py:69-93]`. Not the file the telemetry is reading (different path, different format).
2. `/work/decisions.log` (root work dir) — a plain-text human-readable log, tailed by `GET /scans/{id}/activity` `[CODE src/scanner/agent_runtime/engine/runtimes/agents_runtime.py:471-473 comment]`. **This is the sole writer**, `_record_turn()`, called once per completed `Runner.run()` attempt `[CODE agents_runtime.py:427-481, call site :835]`.

`_record_turn`'s content is **exactly one of two shapes**, never a third:
- `text = str(result.final_output)` (truncated to 600 chars) when a turn completed normally (`result is not None`) `[CODE agents_runtime.py:442-458, :479]`.
- the literal string `"max_turns_exceeded"` when `Runner.run()` raised `MaxTurnsExceeded` (`result is None`, `max_turns_exceeded=True`) `[CODE agents_runtime.py:444, call site :813-822,835]`.

**There is no code path today that writes any other decision category** ("finding written," "hypothesis abandoned," etc.) to this file. The docstring at line 437 even says the *previous* behavior silently dropped the max-turns case entirely from both `agent_messages` and `decisions.log` — this file writes a marker specifically to *avoid* going blank, not to enumerate decision types. So: **this is intentional current behavior, not a bug** — the orchestrator prompts (`orchestrator.py`, `enrichment.py`) *tell the model* to log free-text lines like `"blocked: no credentials"` into `decisions.log` itself via its own `write_file`/shell tool calls, but that is model-authored content that would show up as the `final_output` text of a normal turn, not a separate logging category in code.

Given that, the observed **59/59 lines being literally `"max_turns_exceeded"` is a real and significant finding in its own right**: it means every single turn that was ever recorded for this scan hit the internal per-run cap (`SCANNER_ENGINE_MAX_TURNS`, default 40 `[CODE agents_runtime.py:326-331]`) — not one worker turn in the whole scan ever finished with a clean model-authored final answer. Two contributing/compounding factors, both code-verified:
- `tool_choice="required"` is only forced by default and is reset after the first tool call because `Agent.reset_tool_choice` defaults to `True` in the installed SDK `[CODE .venv/Lib/site-packages/agents/agent.py:395-397]` and is never overridden in `agents_runtime.py`'s `Agent(...)` construction `[CODE agents_runtime.py:785-797]` — so I can **rule out** "tool_choice=required for the whole run forces infinite tool use" as the mechanism (checked and refuted against the actual installed SDK, not assumed).
- Each reprompt (`max_reprompts=6` by default) re-invokes `Runner.run()` with a **fresh 40-turn budget** `[CODE agents_runtime.py:809,812-838]`; hitting max-turns on every attempt means a worker plausibly burns up to 6×40 = 240 internal turns without ever cleanly stopping, which is consistent with the reported `worker_runs` p90 duration of 1786s.
- Separately, any worker that instead died via the "no choices" crash (Q2) **never reaches `_record_turn` at all** (the exception returns `WorkerResult` before line 835), so those failures are invisible in `decisions.log` — the 59 lines are only the subset of turns that survived long enough to exhaust their turn budget, not the full picture of what killed this scan's workers.

**Verdict on Q3:** `max_turns_exceeded` is not an arbitrary category needing a "should other types appear" fix — it is one of exactly two possible line shapes by design. The anomaly is that the *other* shape (a real completed-turn transcript) never appears in this scan at all, which is itself worth investigating as either a model-fit problem (this specific model never produces a clean stop) or a symptom of the same provider instability making genuinely-completed runs rare.

---

## Q4 — Where does the honest OOB classification verdict actually persist?

Not in `oob_interactions.jsonl` — that file is confirmed to be the **raw, pre-classification** interactsh mirror only: `mirror_interactions()` streams raw callback records to it from inside the agent/toolserver container and the poller `[CODE src/scanner/agent_runtime/interactsh.py:11,50; src/scanner/agent_runtime/entrypoint.py:810,992; src/scanner/scheduler/poller.py:1490]`. It is never rewritten with a verdict field — the "no classification field" observation in the telemetry is expected, not a bug.

`classify_oob(reg_class, protocol)` `[CODE src/scanner/agent_runtime/oob/service.py:77-97]` is invoked **at read/sync time**, inside `sync_oob()`, against the raw `oob_interactions.jsonl` + `oob_registry.jsonl` files `[CODE oob/service.py:199-230]`. Its `(honest_class, note)` verdict is persisted in exactly two places, both downstream of the raw file:
1. An auto-minted **`findings`** row's `category` field — the honest class, explicitly *not* the agent's original claimed class (`"Resolve the ledger cell under the HONEST class"`) — via `_upsert_oob_finding` `[CODE oob/service.py:267-284]`.
2. An evidence record tying the `oob_token` to the (cell, scan) via `_safe_evidence`/`_upsert_oob_finding`'s evidence-write path `[CODE oob/service.py:240-284]`, and the resolved ledger cell itself is updated to the honest `vuln_class`.

So: the classification verdict lives in `findings.category` + evidence, not in any dedicated "oob_classifications" table or back into the jsonl — the raw interaction log and the classified result are, by design, two different artifacts at two different pipeline stages.

**Verdict on Q4:** Not a gap — the file the telemetry inspected was never meant to carry the verdict.

---

## Q5 / H1 — Ranking the explanations for observed failure volume

Given the specific candidate causes named in the task (ledger claim/release defect vs. upstream-provider unreliability vs. zombie/reconcile gap vs. some combination), ranked by how much of the observed volume each explains, using only the evidence above:

1. **Upstream-provider unreliability — primary, largest single driver.** `"ChatCompletion response has no choices"` is ~53% of *all* worker_runs (471/~970) and is structurally un-retried (Q2: doesn't match `_is_connection_error`), so each occurrence kills a worker outright on first contact with the model, at zero probing effort, concentrated on one model (`space-bunny-alpha`, 594/~970 runs — a free/"stealth" OpenRouter route). This is the dominant volume source by a wide margin over anything else measured.
2. **Ledger claim/release "attempt" accounting defect — confirmed, and it is the mechanism that *converts* problem #1 into corrupted-looking coverage data.** It is not itself a race/concurrency bug in the claim/release SQL (that machinery — `FOR UPDATE SKIP LOCKED`, work-stealing release-by-cell-id — reads as correctly implemented and this repo's own tracked issues already record its concurrency tests as fixed). The defect is narrower and specific: **`attempts` counts a claim, not a genuine probe**, and cap=3 is a low bar that a 53%-failure-rate upstream can exhaust in a handful of unlucky draws with zero real testing. This is what produces the headline number (`attempted 8771` > `confirmed+tested_clean 5159`) and the zero-clean/zero-confirmed vuln classes.
3. **Turn-cap/reprompt inefficiency — secondary, a cost/latency amplifier, not a correctness bug.** 100% `max_turns_exceeded` in `decisions.log` for this scan shows workers that *did* survive contact with the model still never stopped cleanly, burning up to 6×40 turns per worker (matches the long p90 duration), but `MaxTurnsExceeded` is a soft-stop (worker continues to reprompt, `WorkerResult` isn't `status=error`), so it inflates cost/time, not the ledger's attempt-cap bucket the way #1/#2 do.
4. **Zombie/reconcile gap — REFUTED as an explanation for this scan.** `partial` is terminal-by-design and every path that sets it also correctly releases resources (Q1). The one genuine, narrower gap in this area (same-node `status='running'` scan surviving a scanner-cp restart without being re-adopted) is a different failure shape than what's observed here and isn't implicated by any of the given numbers.

**VERDICT: PARTIAL.** The dominant explanation is upstream-provider unreliability (not a ledger defect and not the zombie/reconcile gap), but the ledger's claim-time attempt accounting is a real, separate, code-confirmed defect that amplifies #1 into the specific "attempt-capped exceeds resolved" and "zero-clean-zero-confirmed classes" symptoms. Neither is well described as "primarily a ledger claim/release defect" (the claim/release *mechanics* are sound; only the *counting semantics* are wrong) nor as "primarily the zombie/reconcile gap" (refuted for this scan).

---

## Blast radius

| Defect | Blast radius |
|---|---|
| Upstream "no choices" crash uncounted as connection error, no retry | Every scan run against a flaky/free-tier OpenRouter model; ~53% of worker_runs fleet-wide per the telemetry sample — the single largest efficiency/cost loss in the fleet today. |
| `attempts` incremented at claim time, not at proven-effort time | Any scan where provider failures coincide with a low attempt cap (default 3); corrupts per-class coverage honesty (a class can look "exhaustively tested and clean" or "exhaustively tested and retired" while having had zero genuine probes) — directly undermines the "honest coverage" goal this engine is built around. |
| `decisions.log` only ever shows two shapes, and crashed-before-first-turn workers never appear in it at all | Operators/monitoring reading `decisions.log` (or the `/activity` UI it feeds) for this scan see a misleadingly uniform "max_turns_exceeded" picture and are blind to the much larger population of workers that died before turn 1 — undercuts incident diagnosis exactly like this task's own investigation had to route around it. |
| Same-node dead-`running`-scan gap (Q1, narrower) | Only manifests across a scanner-cp process restart while a scan is still actively `running` on the *same* single node; does not explain the `partial` row investigated here, but remains a real latent risk this repo's own CLAUDE.md already tracks. |

---

## Evidence Ledger

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| `partial` is a terminal status, grouped with `failed`/`cancelled` | [CODE src/scanner/api/routes/scans.py:420] | High | `_RESUMABLE_STATES` tuple |
| Every code path producing `status='partial'` also sets `completed_at` and releases the concurrency slot | [CODE src/scanner/scheduler/poller.py:1309-1440] | High | 4 distinct branches checked (clean/orphan-finalize/ledger-resume-exhausted/salvage) |
| Dead-node reaper only fires for `node_id != my_node` (or legacy NULL) | [CODE src/scanner/scheduler/poller.py:718-745] | High | Structurally can't fire on a single-VM deployment for same-node scans |
| `_reconcile_on_boot` only re-tracks `running/cancelling/closing/killing` | [CODE src/scanner/scheduler/poller.py:213-287, filter :241] | High | `partial` correctly excluded — not a gap for this scan's status |
| `watch_once` container-`NotFound` → `_on_scan_exit(success=False)` | [CODE src/scanner/scheduler/poller.py:1231-1247] | High | Real live-node container-death detector, scoped to `_tracked` only |
| `attempts = u.attempts + 1` happens at claim time, before any work | [CODE src/scanner/ledger/service.py:1393-1416] | High | Direct SQL read |
| Attempt cap defaults to 3 | [CODE src/scanner/ledger/service.py:1237-1247] | High | `SCANNER_LEDGER_ATTEMPT_CAP` |
| Cap-exhausted cells absorbed to `'attempted'` on every worker exit type (ok/partial/error/preempt) | [CODE src/scanner/agent_runtime/engine/father.py:1345-1362; src/scanner/ledger/service.py:1444-1473] | High | `on_done` hook wiring confirmed |
| `"no choices"` does not match the reconnect predicate → not retried | [CODE src/scanner/agent_runtime/engine/runtimes/agents_runtime.py:82-89] | High | Substring check enumerated in code |
| Non-`MaxTurnsExceeded` exceptions return `WorkerResult(status="error")` before any `_record_turn`/attempts bookkeeping in that function | [CODE agents_runtime.py:812-830] | High | Direct control-flow read |
| `/work/decisions.log`'s sole writer is `_record_turn`; content is `final_output[:600]` or literal `"max_turns_exceeded"`, nothing else | [CODE agents_runtime.py:427-481] | High | No other write site found repo-wide for this exact path |
| `/work/guard/decisions.log` is a separate, JSON, gated-by-flag file — not the one the telemetry read | [CODE src/scanner/agent_runtime/engine/guardrails.py:69-93] | High | Different path, different format |
| `reset_tool_choice` defaults `True` in the installed SDK, ruling out permanent forced-tool-choice as the max-turns cause | [CODE .venv/Lib/site-packages/agents/agent.py:395-397] | High | Verified against actually-installed package, not assumed |
| `oob_interactions.jsonl` is raw/pre-classification; `classify_oob`'s verdict lands in `findings.category` + evidence, not the jsonl | [CODE src/scanner/agent_runtime/oob/service.py:77-97, 199-284; src/scanner/agent_runtime/interactsh.py:11,50] | High | Read/write sites for both files enumerated |
| Governor returns `"partial"` on plateau (a full wave with 0 closed cells / 0 new surface / 0 new findings), and the wave loop only stops once the ledger is fully drained (no claimable cells left) | [CODE src/scanner/agent_runtime/engine/governor.py:18-39; src/scanner/agent_runtime/engine/father.py:1750-1852] | High | Ties Q1's terminal-`partial` finding to Q2's attempt-cap-drives-drain mechanism |
| Specific vuln classes (ssi/quota_abuse/workflow_abuse) hit hundreds of attempt-capped cells with zero clean/confirmed purely because no negative oracle exists for them | [INFER] | Low | Telemetry's own explanation; equally consistent with, and not distinguished from, the claim-time-attempt-inflation mechanism in Q2 without a per-cell attempts/error-type query I did not run |
| This specific zombie row's `completed_at`/`node_id` values are consistent with a benign 10-day-old completion | [INFER] | Medium | Not directly queryable in this read-only pass; inferred from the code paths that produce `partial`, all of which set `completed_at` |
| A hop's proof/evidence is threaded into the next hop's worker input (vs. only linked after-the-fact) | Not found in repo (out of the 8 files read for this task) | — | Flagged in the task as needing a code check; would require reading the chain-writer/worker-dispatch code, which was not in the assigned file set — not answered here to avoid guessing |

---
---

# WS2 — Boss / Policy / PlanGate: Ground Truth + Bounded Per-Tick Planner Design
**Agent:** research-agent-orion-01 · **Date:** 2026-10-01 · **Mode:** read-only design task against `boss.py`, `policy.py`, `plan_gate.py`, `plan.py` (+ their real call sites in `father.py`/`run.py`/`scan_brief.py`/`context.py`/`config.py`/`ledger/service.py`/`hooks/scope.py`)

## Ground truth first, as instructed: is this live per-tick, or one-shot-at-scan-start?

**FALSIFIED: it is neither a design proposal nor a one-shot plan — a bounded, per-wave-tick planner is already built and wired end-to-end in code today.** It ships OFF by default, but "off" is a flag value, not an architecture gap.

- The engine-v2 wave loop is a `while True:` in `Father.run()`. Each iteration: refresh surface → sync to DB → sample open cells → write `recon.json` → **`brief = write_scan_brief(...)`** → **`await self._boss_tick(brief)`** → plateau/governor/quiescence checks → claim+dispatch this wave's workers `[CODE src/scanner/agent_runtime/engine/father.py:1762-1787]`. The boss call sits *inside* the per-wave loop, not before it — this is definitionally per-tick, not once at intake.
- `_boss_tick` itself: gated on `self._boss_fn is not None and settings.scanner_engine_boss` `[CODE father.py:1156]`; calls the boss, validates+merges via `PlanGate.validate_plan` against **that wave's live open-cell sample and scope**, persists `plan.json` atomically, and updates the in-memory claim-bias (`self._plan`, `self._plan_digest`) — all fresh, every wave `[CODE father.py:1145-1176]`.
- The claim-order bias it produces is consumed on the very next line of the same wave: `surf.claim_cells(worker_id=..., limit=..., priority_classes=self._plan_priority_classes())` `[CODE father.py:1191-1193]` — i.e. a re-plan this wave can steer worker claims *this same wave*, not just a future one.
- **Minor doc-vs-code nuance (code wins):** `config.py`'s own comment on the flag says "Default OFF => no plan **at scan start**" `[CODE src/scanner/config.py:415-416]`. Read literally that undersells the mechanism — the plan isn't just missing at t=0, it is actively rebuilt every wave for the life of the scan. Not wrong, just incomplete next to what the code actually does.

**Verdict:** treat the "is it live-per-tick or one-shot" question as closed — it's per-tick, already shipped, gated by `scanner_engine_boss: bool = False` `[CODE config.py:417]`. The open design work is *not* "build a per-tick planner" — it's **closing two real gaps between what the existing contract promises and what it currently delivers**, and **making operator playbooks obey the same validated path an LLM objective does**. Detailed below, each falsified/confirmed against the actual wiring, not assumed from the module docstrings.

## The contract as it exists today, per layer (for reference — all three files already implement exactly the 3-layer split the task asked to design)

| Layer | File | Contract |
|---|---|---|
| Propose (LLM, advisory) | `boss.py` | `propose_plan(execute_fn, brief, board_totals, coverage_qa, current_plan, policy) -> dict\|None`. Bounded: `max_turns=8`, `wall=180s` (env-overridable) `[CODE boss.py:46-51]`. Tool surface is **read-only**: only `read_file`/`grep`/`glob` over `/work`, explicitly NOT `run_shell`/`write_file`/`browse` `[CODE boss.py:76]`. `tool_choice=None`, not `"required"` — the boss may answer from the prompt alone `[CODE boss.py:90]`. No SDK / no `OPENROUTER_API_KEY`/`CAI_API_KEY` / any exception / empty-or-malformed JSON ⇒ `None` ⇒ caller treats as "prior stands" `[CODE boss.py:67-71, 133-146, 171-175]`. **Never raises** — `propose_plan` wraps the call in `try/except Exception` `[CODE boss.py:171-174]`. |
| Gate (deterministic, mandatory) | `plan_gate.py` | `validate_plan(candidate, prior, open_cells, scope, max_active=10) -> dict`, **never raises** (outer `try/except Exception → logger.warning + prior/_empty_plan fallback`) `[CODE plan_gate.py:30-47]`. Merge-not-replace by objective `id`, only fields the boss *actually resent* overwrite the prior objective's fields `[CODE plan_gate.py:68-90]`. Per-objective rules re-evaluated every tick over the **live** surface: Rule 4 (must resolve to ≥1 known taxonomy class via `taxonomy.normalize`, else `rejected:"no_valid_class"`) `[CODE plan_gate.py:158-164, 219-221]`; Rule 3 (a *concrete* host named in `endpoint_glob` must be `in_scope()`, else `rejected:"out_of_scope"`) `[CODE plan_gate.py:173-186, 222-225, using scanner.agent_runtime.hooks.scope.in_scope/ScopeConfig]`; Rule 2 (must count ≥1 matching **open** cell in the sampled surface, else `rejected:"no_surface"` if new, or auto-`"retired"` if it previously had backing and drained) `[CODE plan_gate.py:203-234]`; Rule 1 (active-objective count capped at `max_active`, overflow demoted to `"queued"` not dropped) `[CODE plan_gate.py:95-104]`; Rule 5 (every free-text field length-capped — rationale 200 chars, `target_profile.notes` 400, etc.) `[CODE plan_gate.py:22, 107-118, 142]`; Rule 6 is the fail-safe already covered above. |
| Persist/consume (pure I/O + projection, mandatory) | `plan.py` | `write_plan`/`read_plan`: atomic temp-file + `os.replace` (the same pattern as `auth_bootstrap.py:105-118`), best-effort, never raises `[CODE plan.py:22-44]`. `render_plan_digest`: ≤1500-char string of *active* objectives, priority-sorted, fed into both the brief's PLAN section and the per-worker task prefix `[CODE plan.py:19, 84-94; father.py:297-300, 605-614]`. `plan_priority_classes`: ordered de-duped class list from active objectives, **biases, never restricts**, the ledger claim order — `[]` on an empty plan falls back to the ledger's own deterministic `_CLASS_PRIORITY` default `[CODE plan.py:97-108]`. |

## Gap 1 (confirmed): the live boss prompt is narrower than the boss's own module docstring promises

`boss.py`'s module docstring says the Boss "inspects the bounded scan state (**scan_brief + coverage board + digests + coverage_qa + prior plan + policy**)" `[CODE boss.py:3-4]`, and `build_boss_prompt(brief, board_totals, coverage_qa, current_plan, policy)` genuinely renders all five sections when given them `[CODE boss.py:108-130]`. But the **only** production call site wires just two:

```python
async def _boss_fn(brief: str, prior: dict[str, Any]) -> dict[str, Any] | None:
    return await propose_plan(_boss_execute, brief=brief, current_plan=json.dumps(prior) if prior else "")
```
`[CODE src/scanner/agent_runtime/engine/run.py:260-261]`

`board_totals`, `coverage_qa`, and `policy` are never passed — they silently default to `""` inside `build_boss_prompt` (`"(none)"` rendered) `[CODE boss.py:121-129]`. Concretely, with `scanner_engine_boss=true` **today**, the boss plans blind to:
- **The coverage board** — even though it's computed fresh every wave anyway, just one call earlier in the same tick: `board = _render_board_totals(await surf.coverage_counts())`, returned from `_claim_worklist()` `[CODE father.py:1194, 1874]`. `_boss_tick(brief)` runs *before* `_claim_worklist()` in the loop `[CODE father.py:1787 vs 1874]`, so the current wave's board isn't computed yet at boss-tick time — but the **previous** wave's board is sitting unused (nothing caches it on `self`).
- **`policy.md`** — assembled once, unconditionally, at intake by `write_policy_file(self._work_dir)`, whose return value (the `md` string) is discarded at the call site `[CODE src/scanner/agent_runtime/engine/context.py:202-204]`. Because policy is built once from `SCAN_SCOPE`/`TENANT_BLOCKLIST`/`SCAN_INSTRUCTION`/`PLAYBOOK_NAME` — none of which change mid-scan — it is safe to read once, not per-tick.
- **`coverage_qa`** — this is a *different, heavier* pipeline than the board: `coverage_quality_summary(session_factory, scan_id, work_dir)` does real DB round-trips (`_load_rows`, 3 queries) `[CODE coverage_qa.py:100, 122]` and today is invoked **exactly once, at finalize**, purely to emit a `"coverage.quality"` telemetry event `[CODE run.py:141-143]`. It is not — and per its current shape, should not casually become — a per-wave call; wiring it into every boss tick would add real DB load per wave for a summary designed as an end-of-scan audit.

**This is a real, code-verified completeness gap, not a hypothesis.** [CONFIDENCE: high — both the promised signature and the actual call site are read directly, not inferred.]

## Gap 2 (confirmed, and self-documented in the code as a known ceiling): PlanGate's backing check is a sample, not a count

`_count_backing()` checks an objective's classes/glob against `open_cells`, which is `Father._sample_open()` → `AttackSurface.sample_open_cells()` `[CODE father.py:1125-1134]` → `sample_open_cells(session, scan_id, n=15)` — **default cap of 15 rows** `[CODE src/scanner/ledger/service.py:1210]`. `plan_gate.py` already flags this itself:

> "ponytail: sample-window fact check (n cells). Ceiling = the sample size; upgrade to a filtered COUNT(\*) (mirror ledger.count_claimable_cells) only if a large frozen grid starves valid objectives past the window." `[CODE plan_gate.py:206-208]`

Concretely: on a scan with a large ledger grid (the codebase's own tracked coverage-grid-inflation issue — ULID/param-cohort fold notwithstanding — routinely produces thousands of cells `[DOC CLAUDE.md "Coverage grid fix 2026-09-18"]`), a genuinely-open, in-scope, correctly-classed objective can be `rejected:"no_surface"` purely because its matching cells didn't land in that wave's 15-row sample — not because no such cells exist. `count_claimable_cells(session, scan_id)` already exists as the exact COUNT(*) primitive this would need `[CODE ledger/service.py:1508]`, just not wired to `_count_backing`.

## Gap 3 (confirmed): operator playbooks reach the engine as prose today, never as a validated, ledger-checked directive

Two real, independent wiring paths for playbooks exist, and **both stop at free text**:
1. `scan_brief.py`: when `playbook_consume_enabled()` is true, the brief gets a `"PLAYBOOK PHASES"` section listing phase names as a "methodology directive" `[CODE scan_brief.py:132, 278-280]` — this reaches every worker's prompt (not boss-specific), as advisory text a worker LLM may or may not follow.
2. `policy.py`: `_playbook_section()` renders the playbook's name/aggression/phases/restrictions/`skip_tools` into `/work/policy.md`'s Playbook section, explicitly marked `"(ADVISORY — hard limits stay code)"` and `"(documented-only — NOT code-enforced)"` for `skip_tools` `[CODE policy.py:70-82]`.

`playbook_consume_enabled()` is gated by `scanner_engine_playbook OR scanner_engine_boss` `[CODE policy.py:124-132]` — so flipping `scanner_engine_boss` on today (once Gap 1 above is fixed) *would* get playbook text into the boss's `policy` section — but only as prose for the LLM to interpret, with zero guarantee it maps to real open/in-scope cells, and zero enforcement if the model ignores it. There is **no code path today that turns a playbook's declared phases into `plan.json` objectives** that `PlanGate` validates the same way it validates a boss-authored objective. This is the one piece of the task's ask ("how operator playbooks become directives the engine actually obeys") that has no code today, confirmed by grep across `src/scanner` for any playbook→objective/plan.json projection — none found.

---

## Design: bounded per-tick planner — completing the existing contract, not replacing it

Ponytail framing: two of the three things asked for as "design" are gap-closures on an already-correct architecture (rungs 2–3 of the ladder — reuse what's built), and the third (playbooks as real directives) is genuinely new but small, expressed as a pure function feeding the exact same validated path everything else already goes through. No new module, no new abstraction layer, no interface-for-one-implementation.

### D1 — Input = ledger state + progress (fixes Gap 1; no new flag)

This isn't a new capability — it's finishing what `scanner_engine_boss`'s own contract already claims. No new flag; ships under `scanner_engine_boss` exactly as documented.

- **`policy`**: capture `write_policy_file()`'s return value at its one call site `[CODE context.py:204]` — e.g. stash it on `scan_ctx` (or re-`read_plan`-style read `/work/policy.md` once, at the same point `run.py` already builds `_boss_execute` `[CODE run.py:254-258]` — smaller diff, since it needs no new field threaded through `ScanContext`). Pass it as `policy=` into the existing `_boss_fn` closure. Zero added per-tick I/O (read once, close over the string).
- **`board_totals`**: cache the previous wave's already-computed string — `self._last_board_totals` set right after `_claim_worklist()` returns it `[CODE father.py:1874]` — and pass `self._last_board_totals` into `_boss_tick`'s call to `self._boss_fn(brief, self._plan, board_totals=self._last_board_totals)`. Costs nothing new to compute; it already exists in memory for one wave's lifetime today and is simply not retained.
- **`coverage_qa`**: **do not** wire the finalize-time `coverage_quality_summary()` into every wave — it's a 3-query DB audit built for an end-of-scan report, not a per-tick signal, and forcing it per-wave adds real DB load for every scan that flips `scanner_engine_boss` on, defeating the "byte-identical unless opted in, and cheap when opted in" ethos the rest of this codebase holds to. If a cheap per-tick quality signal is wanted, it should be a **new, cheap aggregate** (e.g. attempted-vs-confirmed ratio per class, already computable from the same `coverage_counts()` rows `_render_board_totals` already consumes `[CODE father.py:382, 1194]`) — not the existing heavy summary. Left as `""` (today's behavior) until that cheap signal is designed; the module's own docstring should be corrected to stop promising the heavy one per-tick. [INFER — this is a judgment call on cost/benefit, not a claim about existing code.]

### D2 — Deterministic plan gate already maps objectives to real ledger cells; fix the sample ceiling it already flags on itself (fixes Gap 2; no new flag)

Swap (or supplement) `_count_backing`'s sampled-`open_cells` check with the existing `count_claimable_cells(session, scan_id, vuln_class=..., endpoint=...)`-shaped COUNT(*) `[CODE ledger/service.py:1508]` filtered by the objective's `classes`/`endpoint_glob`, exactly as `plan_gate.py`'s own comment already prescribes `[CODE plan_gate.py:206-208]`. Mechanism: `validate_plan` already takes `open_cells: Sequence[Mapping[str,str]]` as a plain in-memory sequence with no DB handle `[CODE plan_gate.py:30-35]` — the smallest-diff path is to make `Father._sample_open()` widen its sample size only when the gate is about to reject-for-`no_surface` (a targeted re-check), rather than turning `plan_gate.py` itself into an async/DB-aware module (which would break its "pure, no DB" contract stated in its own docstring `[CODE plan_gate.py:1-4]` and its unit-testability). Concretely: on a `no_surface` rejection, `Father` can do one more `count_claimable_cells`-shaped query scoped to that objective's class+glob before finalizing the rejection, and only reject if that returns 0 too. This keeps `plan_gate.validate_plan` synchronous/pure and pushes the one extra DB round-trip to the (already-async) caller, only on the rejection path — not every tick, every objective.

### D3 — Operator playbooks become directives the engine actually obeys (fixes Gap 3; new flag)

**New flag, following `config.py`'s convention: `scanner_engine_playbook_objectives: bool = False`** (placed beside `scanner_engine_playbook`/`scanner_engine_boss` at `config.py:410-417`; comment pattern: *"Default OFF => playbook phases stay brief-only prose (today's behavior); ON => phases also seed validated plan.json objectives, so an operator directive gets the exact same real-open-cell + in-scope check a boss-authored objective gets."*).

Mechanism — reuses every existing primitive, adds one pure projector function:
1. **`policy.playbook_policy_view(playbook)`** already exists and already returns `{"name", "phases": [str,...], "aggression", "restrictions": [...], "skip_tools": [...]}` `[CODE policy.py:103-121]` — the phase *names* are already deterministic strings (e.g. `"auth"`, `"idor"`, `"injection"` per whatever the shipped YAML under `playbooks/definitions/*.yaml` names them).
2. New pure function (same file family as `plan.py`/`plan_gate.py`, no new module needed — could live in `plan.py` next to `merge_plan`): `seed_objectives_from_playbook(view: dict) -> list[dict]` maps each phase name through `taxonomy.normalize()` (the **same** normalizer `plan_gate._norm_classes` already calls `[CODE plan_gate.py:158-164]`) to a `classes` list, synthesizes `id=f"playbook:{phase}"`, `kind="exploit"`, `priority=<phase index>`, `rationale=f"operator playbook: {view['name']}"`. Phase names that don't normalize to any known taxonomy class are simply dropped (same silent-drop behavior `_sanitize_objective` already has for an objective with no id `[CODE plan_gate.py:127-129]` — consistent, not novel).
3. Feed the result through the **existing, unmodified** `validate_plan(candidate={"objectives": seeded}, prior=None, open_cells=..., scope=...)` at the first wave of `Father.run()`, gated on `scanner_engine_playbook_objectives`. This is not a new code path through the ledger/scope layer — it's the *same* `_apply_rules` (Rule 2/3/4 above) a boss objective already goes through, so a playbook phase with zero matching open cells is **auto-`"retired"`/`"no_surface"`-rejected exactly like a bad LLM objective would be** — no separate enforcement logic to write or get wrong.
4. On later ticks, if `scanner_engine_boss` is also on, the boss's own candidate merges with this seeded set by the **existing** merge-not-replace-by-`id` rule `[CODE plan_gate.py:56-92]` — the boss can reprioritize/retire a playbook-seeded objective (its `id` is a normal string, no special-casing needed), but can never resurrect one PlanGate already rejected for having no real backing, and can never invent scope it doesn't have.
5. If `scanner_engine_boss` is OFF but `scanner_engine_playbook_objectives` is ON: the seeded plan still persists via the **existing** `write_plan`/`render_plan_digest`/`plan_priority_classes` `[CODE plan.py]`, so playbook phases bias claim order deterministically with **no LLM involved at all** — a genuinely new, cheap, LLM-independent capability the current architecture doesn't offer today (today, playbook enforcement without the boss is 100%-advisory prose only).

### Failure semantics — preserved by construction, not by a new safeguard

All three design pieces sit *behind existing fail-safe boundaries* rather than adding new ones:
- D1's extra `policy`/`board_totals` params are just additional (possibly-empty) strings into `build_boss_prompt`, which already renders `"(none)"` for any empty section `[CODE boss.py:121-129]` — a missing/failed read degrades to today's blanker prompt, never an error.
- D2's extra COUNT(*) call is wrapped the same way every other `Father` DB call already is — `try/except Exception: logger.awarning(...)` fallback to the sampled-only verdict `[pattern CODE father.py:1132-1134, matches existing `_sample_open` error handling]` — a DB hiccup just falls back to today's sample-only check, never blocks the tick.
- D3's seeding call is a **pure function** (no I/O, no LLM, cannot time out) feeding the **already-never-raises** `validate_plan` `[CODE plan_gate.py:30-47]`; with the flag off, it's simply never called, so `self._plan` stays exactly whatever the boss (or nothing) produced — byte-identical to today.

In every case: **planner down ⇒ prior plan stands**, exactly as `plan_gate.py`'s own Rule 6 already states and `boss.py`'s docstring already promises `[CODE boss.py:13; plan_gate.py:38-42]` — the design adds inputs and one new deterministic seed path *into* that existing fail-safe funnel, it does not add a new one.

### Flag summary

| Flag | Default | Gates |
|---|---|---|
| `scanner_engine_boss` (existing) | `False` `[CODE config.py:417]` | The LLM propose step + D1's input completeness fix (no new flag needed for D1 — it's inside this flag's existing contract) |
| `scanner_engine_playbook` (existing) | `False` `[CODE config.py:413]` | Brief PHASES prose injection (unchanged by this design) |
| `scanner_engine_playbook_objectives` (**new**) | `False` | D3 — playbook phases seeded as `PlanGate`-validated `plan.json` objectives; independent of `scanner_engine_boss` |

---

## Evidence Ledger (WS2)

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| The boss tick runs once per wave, inside `Father.run()`'s `while True:` loop, not once at scan start | [CODE src/scanner/agent_runtime/engine/father.py:1762-1787] | High | Direct control-flow read; `_boss_tick` call sits between brief-refresh and plateau/governor checks every iteration |
| `_boss_tick` is gated by `boss_fn is not None` AND `settings.scanner_engine_boss` | [CODE father.py:1156] | High | Direct read |
| `scanner_engine_boss` defaults `False`; comment says "no plan at scan start" (imprecise — it's rebuilt every wave, not just absent at t=0) | [CODE src/scanner/config.py:415-417] | High | Code (the flag/gate) is unambiguous; only the inline comment's phrasing is loose |
| The plan's claim-order bias is consumed the same wave it's produced (`claim_cells(..., priority_classes=self._plan_priority_classes())`) | [CODE father.py:1191-1193] | High | Same-wave read-after-write confirmed |
| `build_boss_prompt` accepts `board_totals`/`coverage_qa`/`policy`, and renders all five sections | [CODE src/scanner/agent_runtime/engine/boss.py:108-130] | High | Direct read |
| The only production call site (`run.py`'s `_boss_fn`) passes only `brief`/`current_plan` | [CODE src/scanner/agent_runtime/engine/run.py:260-261] | High | Grepped for every call to `propose_plan`/`build_boss_prompt` repo-wide; this is the sole live wiring |
| `board_totals` is computed once per wave already, one call after `_boss_tick`, and discarded (not cached across waves) | [CODE father.py:1194, 1874] | High | `_claim_worklist` runs after `_boss_tick` in loop order |
| `write_policy_file`'s return value is discarded at its only call site | [CODE src/scanner/agent_runtime/engine/context.py:202-204] | High | Direct read |
| `coverage_quality_summary` does DB round-trips and is invoked exactly once, at finalize, for a telemetry emit only | [CODE src/scanner/agent_runtime/engine/run.py:138-145; coverage_qa.py:100,122] | High | Grepped every call site of `coverage_quality_summary` repo-wide (1 hit) |
| `_count_backing` checks against a ≤15-row sample (`sample_open_cells(..., n=15)`), not a full count; the code itself flags this as a known ceiling | [CODE src/scanner/agent_runtime/engine/plan_gate.py:203-211, comment 206-208; src/scanner/ledger/service.py:1210] | High | Default-arg read + the module's own inline "ponytail" comment |
| `count_claimable_cells` already exists as the COUNT(*) primitive the fix would use | [CODE src/scanner/ledger/service.py:1508] | High | Signature confirmed; not currently called from `plan_gate.py`/`father._sample_open` |
| `playbook_consume_enabled()` gates the brief's "PLAYBOOK PHASES" prose injection, keyed on `scanner_engine_playbook OR scanner_engine_boss` | [CODE src/scanner/agent_runtime/engine/policy.py:124-132; scan_brief.py:278-280] | High | Both sides of the wiring read directly |
| `policy.py`'s playbook section explicitly marks `skip_tools`/aggression as advisory/"NOT code-enforced" | [CODE policy.py:70-82] | High | Direct read of the rendered markdown builder |
| No code path today projects a playbook's phases into `plan.json` objectives / anything `PlanGate` validates | Not found in repo | Medium | Grepped `src/scanner` for a playbook→objective/plan projection; absence is the finding, not a positive proof of non-existence beyond grep coverage |
| `PlanGate.validate_plan`/`_validate` never raises (outer `try/except Exception` with logger fallback) | [CODE plan_gate.py:30-47] | High | Direct read |
| `plan_gate._norm_classes` reuses `taxonomy.normalize` for alias resolution — the same primitive proposed for playbook-phase→class mapping in D3 | [CODE plan_gate.py:16, 158-164] | High | Confirms D3 reuses an existing normalizer rather than inventing one |
| `merge_plan`'s (and PlanGate's live equivalent) merge-not-replace-by-id would let a boss candidate coexist with playbook-seeded objectives without special-casing | [CODE plan.py:56-81; plan_gate.py:68-92] | High | Both merge implementations key purely on `id`, no type/origin distinction needed |

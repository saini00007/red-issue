# Engine-v2 Deep-Dive — Final Competitive-Research Report
**AI_NAME:** research-agent-lynx-03 · **Mode:** read-only synthesis, no new files/citations · **Thesis under test:** "LLM proposes, deterministic oracle disposes" — a finding is verified only via a fired deterministic oracle, an OOB callback, or live browser execution.

---

> ## ⚠️ CORRECTION (added post-publication, 2026-10-01) — this report's flag-state claims are WRONG for the live deploy
>
> Every "default OFF / zero compose override" claim below (§1 executive summary, H5 verdict, §3,
> and the consolidated ledger rows for `scanner_require_proof_capsule`, `scanner_graphql_authz_enabled`,
> `scanner_channel_oracles_enabled`, `scanner_auth_oracles_enabled`, `SCANNER_ENGINE_CHAIN_FLOOR`) was
> derived by grepping **this repo's tracked `docker-compose.yml`**, which does NOT reflect what
> `abhedi-cc` (the live host) actually runs. A separate concurrent audit
> (`improvment-research/research-agent-mako-02/`, corroborated independently) found the live deploy
> is driven by **`/home/admin/autocan/docker-compose.override.yml` on the server** — a file not
> tracked in this repo at all — which sets nearly every flag this report calls "off" to **ON**:
> `SCANNER_ENGINE_BOSS=true`, `SCANNER_ENGINE_CHAIN_FLOOR=1`, `SCANNER_EXECUTED_CHAIN_FINDINGS=true`,
> `SCANNER_REQUIRE_PROOF_CAPSULE=true`, `SCANNER_EVIDENCE_GATE=true`, `SCANNER_GRAPHQL_AUTHZ_ENABLED=true`,
> `SCANNER_CHANNEL_ORACLES_ENABLED=true`, `SCANNER_AUTH_ORACLES_ENABLED=true`,
> `SCANNER_TWO_IDENTITY_AUTHZ_ENABLED=true`, `SCANNER_AI_REDTEAM_FLOOR=true`.
>
> This doesn't just soften this report's "BUILT ≠ RUNNING" framing — it **surfaces a sharper, more
> specific bug this report missed entirely**: with `require_proof_capsule=true` AND
> `evidence_gate=true` actually live, and `exploit_floor.py`'s chain-floor hops writing zero
> `release_cells`/capsule calls (`chain/floor.py`'s `_write_executed_chain` passes `extra=None`),
> the flagship "proven end-to-end chain" bucket this report's §6 design was meant to strengthen is
> **structurally empty on prod right now** — every chain-floor-confirmed hop gets gated out by the
> very enforcement flag §4 item 3 recommended turning on (it's already on, and it's silently
> discarding proof).
>
> **Read `[[project_deployed_config_reality_2026_10_01]]` and `research-agent-mako-02`'s audit
> before acting on any flag-state claim in this document.** The code-level mechanism findings
> (H1-H4, H6, the counting-semantics bug, the WebSocket discovery gaps, the chain/planner/browser
> designs in §6-7) are unaffected — those were read from source, not from a compose file — only the
> "is it on in prod" layer needs replacing wholesale.

---

## 1. Executive Summary

The single strongest, most concrete finding is **not** the "zombie scan" as originally framed — it's what killed that hypothesis and what it points to instead. `status='partial'` on scan `3b4803e4-...` with a 10-day-stale heartbeat is a **terminal state working as designed** [CODE service.py:1207; scans.py:420; poller.py:1309-1440], not a stuck scan. The real story underneath the same dataset is a **53%-failure upstream model** (`space-bunny-alpha` via OpenRouter, "ChatCompletion response has no choices," 471/970 worker_runs) [TELEMETRY worker_runs error-bucket] combined with a **claim-time attempts counter** that burns an attempt before any work happens [CODE ledger/service.py:1393-1416], converting pure provider noise into `attempted(8771) > confirmed+tested_clean(5159)`. A second, independently-confirmed mechanism feeds the same inequality: a worker that exhausts its full 7-attempt/280-turn reprompt budget with zero coverage calls still exits `status="ok"` and still ratchets its cells toward `attempted` [CODE father.py:1345-1362]. Neither is a ledger-locking bug — `SKIP LOCKED` claim/release mechanics are sound [CODE ledger/service.py:1349-1405]; the defect is in *counting semantics*, not concurrency safety. Separately, three deterministic oracles (GraphQL authz, WebSocket, JWT/OAuth) are fully built, unit-testable, pure functions [CODE graphql_authz.py:201-343; channels.py:200-220; exploit_floor.py:1949,4164-4289] but **all three default OFF with zero compose override** — the exact "BUILT ≠ RUNNING" pattern this repo's own 2026-09-16 audit already flagged elsewhere. Worse, for WebSocket specifically, turning the flag on would resolve nothing: three independent discovery gaps (URL_RX excludes `ws(s)://`, no Playwright WebSocket listener, a path regex that misses Socket.IO) mean essentially no `kind="websocket"` element can ever be minted [CODE scope.py:16; browser_server.py full-file grep; inventory_ingest.py:413]. The report-level enforcement flag that would make "unproven finding never ships as confirmed" actually true (`scanner_require_proof_capsule`) is also off with no compose pin [CODE config.py:494]. Net: the oracle-first thesis is real in the code but only partially enforced in what a stock deploy actually runs.

---

## 2. Hypothesis Verdicts (H1–H6)

### H1 — "Ledger claim/release defects explain the coverage numbers"
**Verdict: PARTIAL.** Ranked by explained volume [WS1 Q5]:
1. Upstream-provider unreliability (~53% of worker_runs, one un-retried model) — dominant driver.
2. Claim-time attempts-counting defect — confirmed mechanism converting #1 into corrupted-looking coverage; claim/release *mechanics* (SKIP LOCKED, work-stealing requeue) are sound, only counting semantics are wrong.
3. 100%-`max_turns_exceeded` pattern in `decisions.log` — real cost/latency amplifier, soft-stop only, not ledger-corrupting.
4. Zombie/reconcile gap — **REFUTED** for this specific scan; `partial` is a correctly-terminal status.

| Claim | Source | Confidence |
|---|---|---|
| `graceful_terminal_status()` returns only completed/partial; every write-path also sets `completed_at`, untracks, releases slot | [CODE service.py:1207; poller.py:1309-1440] | HIGH |
| `_recover_dead_node_scans()` only requeues cross-node `status='running'`, never fires on single-VM same-node scans | [CODE poller.py:718-745] | HIGH |
| `attempts = u.attempts + 1` fires at claim time, before any work | [CODE ledger/service.py:1393-1416] | HIGH |
| "no choices" error doesn't match `_is_connection_error`, never retried, returns `WorkerResult(status="error")` before any tool call | [CODE agents_runtime.py:82-89,812-830] | HIGH |
| Attempt cap = 3, absorbed to `'attempted'` on every exit type (ok/partial/error/preempt) | [CODE service.py:1237-1247; father.py:1345-1362] | HIGH |
| `decisions.log` has exactly two possible line shapes; no missing third "decision type" | [CODE agents_runtime.py:427-481] | HIGH |
| Governor plateau logic ties it together: wave loop stops only once ledger fully drains | [CODE governor.py:18-39; father.py:1750-1852] | HIGH |

### H2 — "Rigid, static prompting causes the fast turn-budget exhaustion"
**Verdict: PARTIALLY CONFIRMED, more precisely characterized than either half assumes.** The system `instructions=` string is 100% static (~4,300 words, only the OOB block varies) [CODE methodology.py:13-251; agents_runtime.py:917-920] — but the **task message is dynamically built per phase/target/wave**, including a per-worker worklist of open cells with prior-attempt/prior-method annotations [CODE father.py:597-633,351-372]. So "fully rigid" is false; "no per-cell state reaches the worker" is false. What *is* true and novel: progressive skill disclosure (`setting_sources=["project"]`) applies only to the Claude-provider runtime, never to the OpenRouter/GLM/DeepSeek fleet path this telemetry came from — that fleet resends the full static prompt every `Runner.run` call with zero trimming [CODE entrypoint.py:509-527; run.py:220-222; methodology.py:70-88]. The turn-budget exhaustion itself is exactly `max_reprompts(6)+1=7` matching code defaults precisely (40 turns × 7 attempts = up to 280 model+tool round-trips) [CODE agents_runtime.py:326-331,798-838] — not a mystery, and not silently defeated by compose (the `SCANNER_ENGINE_EFFORT` empty-string-pin hypothesis was explicitly tested and **refuted**) [CODE worker.py:178; agents_runtime.py:349-357]. The real gap: `_offensive_gate()` is the sole stop condition — nothing bails early on a non-advancing worker inside its own reprompt loop [CODE agents_runtime.py:942-960,836].

### H3 — "There is one unified chaining mechanism"
**Verdict: REFUTED as a blanket claim.** Three separate mechanisms exist:
- **Graph** (`chain/service.py`) — reporting-only, after-the-fact, destructive rebuild.
- **Chain floor** (`chain/floor.py`) — deterministic, non-LLM, genuinely threads a confirmed finding's URL/param into the next-hop probe; default OFF (`SCANNER_ENGINE_CHAIN_FLOOR=0`, code and compose).
- **Escalation wave** (`engine/escalation.py` + `father.py:_capability_context`) — the mechanism that actually answers "does a confirmed finding feed the next LLM worker": a finding's title+endpoint gets prefixed into the next `WorkerSpec.task`. **Default ON** in code and compose (`${SCANNER_ENGINE_ESCALATE:-}` → empty → enabled) — an undocumented exception to this codebase's stated default-OFF convention.

Two fresh bugs (not in WS1's original dossier): `_capability_context` (`father.py:1527`) uses plain `normalize()` instead of the `normalize()`→`normalize_ngram()` fallback used elsewhere, silently dropping citations for namespaced categories; a dormant `executed_chain` synthetic finding (flag-gated off) gets silently reclassified to its follow-on hop's CWE-derived vuln class by `chain/service._vuln_class`, losing its "this edge was code-proven" identity.

### H4 — "Browser-worker sessions chain across multi-step actions"
**Verdict: PARTIAL.** Session *continuity* within one `/crawl` or `/instrument` call is real — one Playwright `context` per call, login happens ≤1×(+1 gated re-auth), every subsequent page inherits cookies/storage [CODE browser_server.py:803-957,1063-1097,570-572,879-889]. Scripted multi-step *business-action* chaining inside the browser does **not** exist — neither endpoint's request schema accepts an action script; `_try_login`/`_try_sso_login` are the only multi-step logic, hard-scoped to reaching a logged-in state [CODE browser_server.py:641-712,715-726,1020-1022]. The multi-step authenticated chaining that *does* exist (`channels.py` Track A / `replay_sequences`, variable capture between steps) is a structurally separate HTTP-only (`curl`-via-`_fire`) subsystem, never Playwright/DOM [CODE channels.py:75-227,471-598].

### H5 — "GraphQL/WebSocket/JWT detection is deterministic-oracle-backed vs. reasoning-only"
**Verdict: Oracle exists; enforcement doesn't reach production.** All three classes have real, deterministic, pure-function verdicts already committed — `field_authz_verdict`/`bopla_exposure`/`bopla_writability`/`depth_unlimited`/`batch_unlimited` for GraphQL [CODE graphql_authz.py:201-343]; `channel_auth_open`/`cross_user_leak`/`webhook_sig_bypassed`/`webhook_replayable` for WS/webhook [CODE channels.py:200-220]; `parse_jwt_forge` (alg:none/sig-strip vs. tampered control) + redirect_uri reuse for JWT/OAuth [CODE exploit_floor.py:1949,4164-4289,4096-4117]. All three gate flags default `False` with **zero compose override found** by direct grep [CODE config.py:293,302,243; QUERY grep docker-compose.yml → no match, all three]. So in a stock deploy, any GraphQL/WS/JWT "detection" is agent-reasoning-driven off `methodology.py` prose pointers, not the oracle [CODE methodology.py:136-142].

The applicability-gate rules themselves (`kind=="graphql"`/`kind=="websocket"`) are **not** the defect — they're logically correct [CODE applicability.py:191-194]. The real defect for WebSocket is a three-layer **discovery** gap, independently confirmed: (1) the universal URL sniffer used by every tool-output ingester hardcodes `https?://`, structurally invisible to `ws(s)://` [CODE scope.py:16; inventory_ingest.py:508-533]; (2) the browser sidecar wires zero `page.on("websocket")`/`context.on("websocket")` handler — a live SPA opening a real socket is never captured [CODE browser_server.py, full-file grep]; (3) the one surviving classification path, a path-regex, matches `/ws/` and `/cable` but misses Socket.IO's default `/socket.io/` (the `.io` sits before the required delimiter) [CODE inventory_ingest.py:413]. `[INFER]`, composed from these three: 0/1203 websocket-applicable cells is best explained by "no code path can ever mint a websocket element," not an applicability bug.

### H6 — "Cross-worker duplication has no real coordination mechanism"
**Verdict: A real DB-enforced mechanism exists at cell granularity and works — but is advisory below that granularity and at two specific seams, one with zero collision protection.** `claim_cells()` uses `SELECT...FOR UPDATE SKIP LOCKED`; its own docstring states two concurrent callers can never get the same cell [CODE ledger/service.py:1349-1405,1362-1365]. Re-claimed cells carry `prior_methods`/attempt count forward with an explicit "go deeper, don't repeat" instruction [CODE father.py:360-367; service.py:1429-1437]. A second, advisory (prompt-level, not code-enforced) layer tells workers which classes the deterministic floor already covers [SKILL.md:16-51]. Two confirmed gaps: (1) the deterministic floor and the LLM fleet run **concurrently by design**, not floor-then-fleet — the anti-duplication instruction is a race against floor output that hasn't landed in the shared JSONL yet [CODE father.py:1220-1227]; (2) all concurrent workers in one scan share **one literal `work_dir`**, and `write_file()` truncates (`"w"` mode) any filename except the two literal names `findings.jsonl`/`ledger_updates.jsonl` — zero lock, zero per-worker subdirectory, zero rename-on-conflict for scratch files [CODE run.py:217-222; fleet.py:124-161; tools/files.py:59-69]. Both are efficiency losses (redundant tool calls), not ledger-correctness bugs — downstream dedup (`dedup_hash`, `_final_dedup`) still collapses duplicate *findings*.

---

## 3. Root-Cause Diagnosis (Synthesized)

**What the original operator hypothesis (ledger claim/release defects) got right:** the instinct that "coverage numbers look corrupted" is correct, and the *counting* path inside the ledger genuinely is the transmission mechanism. **What it got wrong:** the locking/claim primitive itself (`SKIP LOCKED`) is provably safe under concurrency — the defect isn't a race condition, it's that `attempts += 1` fires at claim time rather than at demonstrated-effort time, so *anything* that returns instantly with zero effort (a crashed provider call, or a worker that burns its whole reprompt budget without ever calling `record_coverage`/`write_finding`) is counted identically to a worker that genuinely tried and failed. There are, in fact, **two independent paths** into the same `attempted > confirmed+tested_clean` inequality:

1. **Crash path** (WS1 Q2): a provider returns a malformed/empty completion → `agents_runtime.py` short-circuits before `_record_turn` → cell released → attempt burned → repeat 3× → `'attempted'`, having never been tested. Volume-dominant (53% of worker_runs).
2. **Zero-progress-but-"ok"-exit path** (WS4-6 H2 blast-radius note): a worker whose phase weapon never once succeeds (wrong syntax, toolserver unreachable, WAF block — `_offensive_calls` never increments) burns its **full** 7×40=280-turn budget, exits `status="ok"`, yet its cells still ratchet toward `attempted` via the same claim-time counter on each re-claim cycle. This path costs wall-clock/turn budget the crash path doesn't.

Layered on top: the deterministic-floor/fleet concurrency race and the shared-workdir scratch-file collision (H6) compound the *same symptom* — both make workers do redundant work, which shows up as more claim/release cycling, more attempts burned, without ever showing up as a ledger-locking bug. The governor's plateau/quiescence stop [CODE governor.py:18-39; father.py:1750-1852] is functioning exactly as designed — the problem is what it's measuring "quiescence" *of*: a ledger fully drained via attempt-cap exhaustion from crash-noise looks identical, from the governor's perspective, to a ledger fully drained via genuine testing.

**Why proofs stay shallow, independent of the above:** three deterministic oracles for the classes that would most differentiate this platform (GraphQL BOLA/BFLA, WebSocket auth/cross-user leak, JWT/OAuth tamper-vs-control) are fully built and pure-function-testable, but ship OFF with no compose pin (H5). For WebSocket specifically, flipping the flag wouldn't even help — the discovery pipeline can't mint the element kind the applicability gate requires in the first place. And the report-level backstop that would prevent an unproven verified high/critical from ever presenting as "confirmed" (`scanner_require_proof_capsule`) is *also* off with no override [CODE config.py:494] — so even where an oracle *does* fire, nothing forces the report to lean on it over an LLM's self-report.

---

## 4. Core-Architecture Improvements (ranked by blast radius, exact module/flag named)

1. **Fix claim-time attempts counting to require demonstrated effort, not just a claim.** Module: `src/scanner/ledger/service.py` (`claim_cells`, attempts increment at ~`:1393-1416`), consumed by `father.py:1345-1362` (`_release_worker_cells`). Design: gate the increment on a worker having produced ≥1 real artifact this claim cycle (a tool exit code ≠ error, or a `record_coverage`/`write_finding` call) rather than incrementing unconditionally at claim. This directly collapses both H1 paths (crash and zero-progress) into one fix, since both share the same counter. No new flag needed — this is a bugfix to existing semantics, same as the CLAUDE.md-tracked quiescence-logging fixes.
2. **Add a non-advancing-worker early-exit to the outer reprompt loop.** Module: `src/scanner/agent_runtime/engine/runtimes/agents_runtime.py` (`AgentsRuntime.run()`, `:798-838`). Reuse the existing progress-signal idiom the fleet-level `_batch_done` watchdog already implements (`father.py:1294-1343`, `_stuck_window_s`) but apply it *inside* one worker's own reprompt cycle: if `_offensive_calls` is flat across two consecutive attempts, stop early instead of spending the full 280-turn budget. This is strictly additive — the fleet-level watchdog stays as the outer safety net.
3. **Turn `scanner_require_proof_capsule` on and pin it in `docker-compose.yml`.** Module: `src/scanner/config.py:494`; consumer `src/scanner/reporting/service.py:168,210,241,305,488,500,723`. Single highest-leverage change to make the thesis ("LLM proposes, deterministic oracle disposes") actually enforced at the report layer rather than merely available in code.
4. **Wire `count_claimable_cells` into `PlanGate`'s backing check instead of a 15-row sample.** Module: `src/scanner/agent_runtime/engine/plan_gate.py` (`_count_backing`, `:203-211`), primitive already exists at `ledger/service.py:1508`. Only apply the extra COUNT(*) on the `no_surface`-rejection path specifically, per the module's own documented ceiling — keeps `validate_plan` pure/sync per its docstring contract.
5. **Fix the WebSocket discovery pipeline before touching `scanner_channel_oracles_enabled`.** Three code sites, in order of leverage: `src/scanner/agent_runtime/hooks/scope.py:16` (`URL_RX` — extend to `wss?://`), `docker/browser/browser_server.py` (add `context.on("websocket")`, currently absent entirely), `src/scanner/agent_runtime/inventory_ingest.py:413` (`_WS_RX` — extend to catch `/socket.io/`). Flipping `scanner_channel_oracles_enabled`/`scanner_graphql_authz_enabled`/`scanner_auth_oracles_enabled` (`config.py:302,293,243`) without this fix leaves WS oracle firing on zero cells.

---

## 5. Feature Add-Ons (ranked by buyer-visible proof value)

1. **Publish the OOB/blind-class oracle (`interactsh.py`) as a named, buyer-facing capability.** No reviewed competitor (XBOW/FireCompass/Escape) markets a standardized OOB-callback gate for blind SSRF/SQLi/XXE [COMPETITOR absence-checked across `competitor-research/**`] — a real, already-built differentiator invisible in current positioning.
2. **Browser-native GraphQL authz oracle fed by passive XHR mirroring** (reuses `field_authz_verdict` unchanged, input sourced from the browser's own recorded XHR list [CODE browser_server.py:842-849; graphql_authz.py:201-223]) — catches GraphQL-over-BFF setups where introspection is never exposed over bare HTTP, which the existing direct-POST `_sweep_graphql` path cannot reach at all.
3. **Browser-native WebSocket oracle hooked at the SPA's own socket lifecycle** (mirrors the existing DOM-XSS sink-hook pattern [CODE browser_server.py:372-433], reuses `cross_user_leak`/`channel_auth_open` unchanged [channels.py:200-208]) — proves the leak through the app's real channel-auth handshake, avoiding a false "channel closed, no leak" negative that an external reconnect attempt could produce.
4. **Browser-native JWT/OAuth client-trust oracle**: plant the same three tampered-token variants `_sweep_auth_session` already builds [exploit_floor.py:4164-4289] into browser storage via the existing `build_session_init_script` [browser_server.py:539-556], verdict = does the SPA render its authenticated shell (live DOM), not just does the API return 200. Genuinely distinct finding class — an SPA route-guard that checks token *shape* only is invisible to an HTTP-only oracle because it has no DOM to render.
5. **Two new client-side proof classes riding the existing `_INSTRUMENT_KIND_MAP` extension point** [browser_ingest.py:209-213]: client-side open-redirect (live navigation-event verdict) and cross-origin `postMessage` leak (passive listener, origin-mismatch verdict). Zero new ingest code required, per the file's own stated design.
6. **Write browser-established sessions back into `/work/auth.json`.** Currently one-directional (HTTP-floor → browser only; `auth_bootstrap.py` is the sole writer, `browser_server.py` only reads) [CODE: cross-file grep]. Closes a real gap: any browser-only post-login token (e.g., an OAuth access token an SPA keeps client-side) is invisible to every curl-based exploit-floor worker.

---

## 6. Chain State Machine + Intelligence-Layer Design (WS4/WS5 Synthesis)

**Ground truth first (H3, restated as design input):** three chaining mechanisms already exist with different maturity — graph (reporting-only), chain floor (deterministic, off by default), escalation wave (LLM-facing, on by default, title+endpoint only — not the full proof). The design below completes this contract rather than replacing it.

**Proposed `ProofType` capability model** (no payloads, state-machine only):

```
ProofType enum (extends existing verification_method vocabulary):
  UNVERIFIED         -- LLM claim only
  SELF_PROVING       -- injection/config/clientside self-proof (exploit_floor S1-S4)
  OOB_CONFIRMED      -- interactsh callback fired (zero-FP)
  BROWSER_EXECUTED   -- live Chromium state proof (DOM-XSS/proto-pollution/storage)
  CHAIN_DERIVED      -- proof inherited from an upstream ChainNode via CHAIN_FLOOR
  SIGNAL_ONLY        -- access/logic candidate, deferred to LLM triage (S6)
```

**Migration path (one Alembic migration, additive columns only):** promote `ChainNode`/`ChainEdge` with `proof_type` (the enum above), `consumed_by` (which downstream hop's worker input actually referenced this node — closes WS1's own flagged open question of whether a hop's proof threads into the *next* hop's input or is only linked after-the-fact for reporting), and `attrs` (free-form capability-label bag, e.g. `FILE_READ`/`SECRET_DISCOVERY`/`DATA_ACCESS`). Reuse the already-existing `build_replay_cmd`/`parse_replay` primitives as the "replay contract" between hops — this is the mechanism that lets a `CHAIN_DERIVED` proof be independently re-verified rather than trusted as an LLM's retelling.

**Bugfixes to land in the same change (WS4 findings):**
- `_capability_context` (`father.py:1527`): switch plain `normalize()` to the `normalize()`→`normalize_ngram()` fallback already used elsewhere in the file, so namespaced-category citations stop silently dropping.
- `chain/service._vuln_class`: preserve a dormant `executed_chain` synthetic finding's own `proof_type=CHAIN_DERIVED` identity instead of silently reclassifying it to the follow-on hop's CWE-derived class.

**Boss/PlanGate intelligence layer (WS5 — ground truth: bounded per-wave-tick planner is already built and wired, not a gap):** `Father.run()`'s `while True` wave loop calls `_boss_tick` every wave [father.py:1762-1787,1156], validates through `PlanGate.validate_plan` (Rules 1-6, never raises) [plan_gate.py:30-47], and the resulting bias is consumed the *same* wave via `priority_classes` on `claim_cells` [father.py:1191-1193]. Three real, narrow gaps close the existing contract rather than building a new one:
- **D1 (input completeness):** the live call site passes only `brief`/`current_plan` [run.py:260-261] though `build_boss_prompt` already renders `board_totals`/`coverage_qa`/`policy` when given them [boss.py:108-130]. Fix: cache the prior wave's `board_totals` on `self`, capture `write_policy_file`'s already-discarded return value [context.py:202-204] and pass it through. Do **not** wire the heavy finalize-only `coverage_quality_summary` per-tick.
- **D2 (sample-ceiling):** `_count_backing` checks a ≤15-row sample [plan_gate.py:203-211], already self-documented as needing an upgrade to `count_claimable_cells` on a large grid. Fix on the rejection path only, keeping `validate_plan` pure/sync.
- **D3 (playbooks as real directives, new flag `scanner_engine_playbook_objectives`, default `False`):** a pure function `seed_objectives_from_playbook(view)` maps playbook phases through the same `taxonomy.normalize` PlanGate already uses, synthesizing `id=f"playbook:{phase}"` objectives fed through the **unmodified** `validate_plan` — same Rule 2/3/4 gate a boss objective gets. Works independently of `scanner_engine_boss` — first LLM-independent way to make a playbook phase deterministically bias claim order.

All three preserve the existing "planner down ⇒ prior plan stands" failure semantics by construction — no new safeguard needed.

---

## 7. Surface/Browser Depth Design (WS6 Synthesis)

**Contract addition (additive to existing `{healthz, crawl, instrument}`):** a new `ACT` capability alongside existing `CRAWL`/`INSTRUMENT`, generalizing the state machine `_try_login`/`_try_sso_login` already implement from "reach a logged-in state" to "complete any authenticated multi-step flow," via a fixed intent enum — no selectors, no DOM commands, only capability labels:

```
ESTABLISH_IDENTITY   -- reach an authenticated shell (existing login logic)
ADVANCE_FLOW         -- move the app to its next flow-state
CONFIRM_TERMINAL     -- reach the flow's side-effecting terminal state
CAPTURE_SESSION      -- snapshot cookies/storage back to auth.json
```

Each intent resolves server-side from *observed page state* (a password field present? a consent button present?) exactly the way `_try_login` already does — the caller supplies capability labels, never "what to click," which is what keeps this a design and not a runbook.

**State diagram** (business-agnostic — identity → resource-creation → confirmation, generalizable to any SPA flow):

```
[ANONYMOUS] --ESTABLISH_IDENTITY--> [AUTHENTICATING] --(federated hop via AT_IDP)--> [AUTHENTICATED_SHELL]
[AUTHENTICATED_SHELL] --ADVANCE_FLOW--> [FLOW_STEP_N] --(repeat)--> [FLOW_TERMINAL]
[FLOW_TERMINAL] --CONFIRM_TERMINAL--> [FLOW_COMPLETE] --CAPTURE_SESSION--> [SESSION_PERSISTED] (writes auth.json)
[FLOW_STEP_N] --session-expiry signal--> [AUTHENTICATED_SHELL]   (mirrors existing should_crawl_reauth/is_session_expired verdict)
(any state) --client-side oracle fires--> [PROOF_EMITTED]
```

**Session write-back (closes the confirmed H4 one-directional gap):** `CRAWL`'s existing internal-login success path now also writes `{bearer, cookies}` into `/work/auth.json` under the acting identity, same schema `login_with_credentials` already writes — no new file, no new format.

**Client-side proof roadmap** (already-shipped baseline vs. new, same `_INSTRUMENT_KIND_MAP` extension point, zero new ingest code):

| Status | Oracle | Verdict shape |
|---|---|---|
| SHIPS TODAY | Prototype pollution | live `{}[prop]===canary` read-back after URL-query-merge gadget |
| SHIPS TODAY | Storage-leak | live `localStorage`/`sessionStorage` read matched against structural secret patterns |
| NEW | Client-side open-redirect | live navigation event actually lands on canary origin |
| NEW | Cross-origin `postMessage` leak | passive listener observes sensitive-shaped payload from a non-app origin |
| NEW | SPA route-guard bypass | privileged DOM content actually renders with no session present (the repo's own noted "authed-vs-anon diff" deferred slice) |

**Browser-native oracles for GraphQL/WebSocket/JWT** — same verdict functions as §5 items 2-4, input sourced from the browser's rendered session rather than an independently-fired HTTP request. This is the exact gap H4/H5 jointly identified: browser sessions are invisible to the HTTP-level oracles and vice versa.

**Discovery-layer prerequisite (must land before flipping any of the three oracle flags):** the WebSocket discovery fix from §4 item 5 — without it, `scanner_channel_oracles_enabled=true` has no cells to claim.

---

## 8. Do-Not-Build List (unchanged from operator's existing list; reopen only with new evidence)

- Recursive agent hierarchies
- Generation-counter/freeze mechanism
- Agent-to-agent chat messaging
- pgvector semantic memory (dead code today per this repo's own tracked issue — `context_memory.py`, zero callers)
- ZAP as a core detector
- Intercepting proxy as coordination substrate

Nothing in this pass's evidence (telemetry, code correlation, competitor comparison, worker-env audit, chain design, planner design, browser design) surfaces new grounds to reopen any of these. The telemetry's dominant failure mode (upstream provider unreliability) and the coordination gaps found (H6) are both addressed by narrower, already-in-repo mechanisms (§4), not by adding hierarchy or shared agent messaging.

---

## 9. Implementation Roadmap (phased, flag-gated default-OFF, validation-before-breadth)

**Phase 0 — Counting-semantics bugfix (no new flag, ships to the existing default-safe baseline):**
- Gate the ledger's `attempts` increment on demonstrated effort, not claim (§4.1).
- Add the non-advancing-worker early-exit inside `AgentsRuntime.run()`'s reprompt loop (§4.2).
- Validation: replay the same live-scan telemetry shape through the fixed counter offline; confirm `attempted` no longer exceeds `confirmed+tested_clean` when the crash-path/zero-progress-path volume is held constant.

**Phase 1 — Report-layer enforcement (flip one existing flag):**
- Turn `scanner_require_proof_capsule` on, pin in `docker-compose.yml` (§4.3).
- Validation: run against a target with at least one known-unproven verified high/critical; confirm it lands in `## Unconfirmed / needs manual review`, not the confirmed list.

**Phase 2 — WebSocket discovery repair (prerequisite, no new flag):**
- `URL_RX` → `wss?://`; add `context.on("websocket")` to the browser sidecar; extend `_WS_RX` for Socket.IO (§4.5).
- Validation: run against a target with a known live WebSocket/Socket.IO endpoint; confirm ≥1 `kind="websocket"` element is minted before touching the oracle flag.

**Phase 3 — Deterministic oracle activation (new default-OFF flags kept, opt-in only):**
- `scanner_channel_oracles_enabled`, `scanner_graphql_authz_enabled`, `scanner_auth_oracles_enabled` — flip only after Phase 2 lands for the WS oracle specifically.
- Validation: confirm each oracle fires on a benchmark target with a known instance of its class (XBEN/VAmPI-style), byte-identical elsewhere.

**Phase 4 — Planner completeness (D1-D3, WS5):**
- D1 (input completeness) and D2 (sample-ceiling fix) under existing `scanner_engine_boss`.
- D3 (`scanner_engine_playbook_objectives`, new flag, default `False`) — independent of boss.
- Validation: a scan with boss off + this flag on should show playbook-phase claim bias in the ledger; a scan with the flag off should be byte-identical to today.

**Phase 5 — Chain proof-typing (WS4):**
- `ProofType` enum + `ChainNode`/`ChainEdge` column migration; `_capability_context` normalize-fallback fix; `executed_chain` reclassification fix.
- Validation: a chain floor-confirmed hop (`SCANNER_ENGINE_CHAIN_FLOOR` on, in a test env) should show `proof_type=CHAIN_DERIVED` end-to-end in the report, not silently reclassified.

**Phase 6 — Browser depth (WS6 feature add-ons):**
- Session write-back (`auth.json`), then `ACT` capability + browser-native GraphQL/WS/JWT oracles, then the two new client-side proof classes.
- Each ships behind its own narrow gate; validate one class at a time against a target with a known instance before adding the next.

Each phase is independently shippable and independently revertible — no phase depends on a later phase's flag being on, matching the existing codebase convention of "byte-identical until an operator opts in."

---

## 10. Consolidated Evidence Ledger (merged, deduped across WS1/WS3/WS4/WS5/WS6)

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| `partial` is a first-class terminal status; every write-path also untracks/releases slot | [CODE service.py:1207; scans.py:420; poller.py:1309-1440] | HIGH | Refutes literal zombie-scan framing |
| Cross-node dead-node recovery can't fire on single-VM same-node scans | [CODE poller.py:718-745] | HIGH | |
| `attempts += 1` fires at claim time, before any work | [CODE ledger/service.py:1393-1416] | HIGH | Root mechanism for H1 |
| "no choices" provider error bypasses retry predicate, returns error before any tool call | [CODE agents_runtime.py:82-89,812-830] | HIGH | Volume-dominant failure path |
| Attempt cap=3 absorbed to 'attempted' on every exit type | [CODE service.py:1237-1247; father.py:1345-1362] | HIGH | |
| A worker exiting "ok" after full reprompt budget with zero coverage calls still ratchets cells toward 'attempted' | [CODE father.py:1345-1362] | HIGH | Second independent path into same inequality |
| `decisions.log` has exactly two possible line shapes by design | [CODE agents_runtime.py:427-481] | HIGH | No missing decision type |
| `oob_interactions.jsonl` is confirmed pre-classification; verdict written only into findings/evidence/ledger, never back into the jsonl | [CODE interactsh.py:11,50; oob/service.py:77-97,199-230,230,267-284] | HIGH | Expected, not a gap |
| Governor plateau/quiescence stops only once ledger fully drains | [CODE governor.py:18-39; father.py:1750-1852] | HIGH | Ties H1 threads together |
| `agent_messages`/chain graph both populate for some scans — refutes a strict "never happens" reading | [TELEMETRY chain_node/edge counts, 13/43 scans] | HIGH (measurement), open (mechanism) | Whether proof threads into next hop's input vs. after-the-fact linking is answered by WS4 below |
| System `instructions=` is one fixed static string per worker; task message is dynamically built per phase/target/wave incl. per-cell worklist | [CODE methodology.py:13-251; agents_runtime.py:917-920; father.py:597-633,351-372] | HIGH | Corrects a literal "fully rigid" reading |
| Progressive skill disclosure applies only to the Claude-provider runtime, not OpenRouter/GLM/DeepSeek fleet | [CODE entrypoint.py:509-527; run.py:220-222; methodology.py:70-88] | HIGH | Fleet resends full prompt every turn |
| Outer reprompt loop = separate counter from SDK's own 40-turn cap; capped at max_reprompts(6)+1=7 | [CODE agents_runtime.py:326-331,427-482,798-838] | HIGH | Matches observed `turn7` ceiling exactly |
| `SCANNER_ENGINE_EFFORT` compose empty-string pin does NOT silently disable it | [CODE worker.py:178; agents_runtime.py:349-357] | HIGH | Hypothesis raised and refuted per FALSIFY rule |
| `_offensive_gate()` is sole stop condition; no non-advancing-worker early exit inside one worker's loop | [CODE agents_runtime.py:942-960,836] | HIGH | Distinct design gap from "rigid prompt" framing |
| Cell claiming uses SKIP LOCKED; two workers can never claim the same cell | [CODE ledger/service.py:1349-1405,1362-1365] | HIGH | Direct answer to H6 core question |
| Deterministic floor and LLM fleet run concurrently by design, not floor-then-fleet | [CODE father.py:1220-1227] | HIGH | Makes SKILL.md anti-dup instruction a race |
| Shared work_dir across concurrent workers; write_file truncates any scratch filename with zero lock/rename-on-conflict | [CODE run.py:217-222; fleet.py:124-161; tools/files.py:59-69] | HIGH | Real collision surface, unverified against actual live workdir listing |
| Graph (`chain/service.py`) is reporting-only/after-the-fact, destructive rebuild | [CODE per WS4 read] | HIGH | |
| Chain floor is deterministic non-LLM, default OFF in code and compose | [CODE chain/floor.py; SCANNER_ENGINE_CHAIN_FLOOR=0] | HIGH | |
| Escalation wave feeds a confirmed finding's title+endpoint into the next worker task; defaults ON in both code and compose (exception to stated default-OFF convention) | [CODE engine/escalation.py; father.py:_capability_context; ${SCANNER_ENGINE_ESCALATE:-}] | HIGH | Undocumented exception, flagged fresh this pass |
| `_capability_context` uses plain normalize() instead of normalize()→normalize_ngram() fallback used elsewhere | [CODE father.py:1527] | HIGH | Silently drops namespaced-category citations |
| Dormant `executed_chain` synthetic finding gets silently reclassified to follow-on hop's CWE class | [CODE chain/service._vuln_class] | HIGH | Loses code-proven identity |
| Boss tick runs once per wave inside Father.run()'s loop, not once at scan start; bias consumed same wave | [CODE father.py:1762-1787,1156,1191-1193] | HIGH | Refutes "planner is one-shot" framing |
| Live boss call site passes only brief/current_plan though build_boss_prompt renders board_totals/coverage_qa/policy | [CODE boss.py:108-130; run.py:260-261] | HIGH | Grepped every call site; 1 hit |
| PlanGate's backing check is a ≤15-row sample, self-documented as needing upgrade to count_claimable_cells | [CODE plan_gate.py:203-211,206-208; ledger/service.py:1508] | HIGH | |
| No code path projects playbook phases into plan.json objectives validated by PlanGate | Not found in repo (grep-based absence) | MEDIUM | |
| validate_plan/_validate never raises; planner-down ⇒ prior plan stands | [CODE plan_gate.py:30-47] | HIGH | Failure semantics preserved by design |
| Browser sessions established within one crawl/instrument call are continuous; no scripted multi-step business-action chaining exists in the browser worker | [CODE browser_server.py:641-712,715-726,803-957,1020-1022,1063-1097] | HIGH | |
| Multi-step authenticated chaining that exists today is HTTP-only (channels.py Track A), never Playwright/DOM | [CODE channels.py:75-227,471-598] | HIGH | Structurally separate subsystem |
| GraphQL/WebSocket/JWT applicability rules are logically correct; not the defect | [CODE applicability.py:191-194] | HIGH | Refutes "applicability gate itself is broken" |
| Universal tool-output URL sniffer excludes ws(s)://; browser sidecar has zero WebSocket event listener; WS path regex misses Socket.IO | [CODE scope.py:16; browser_server.py full-file grep; inventory_ingest.py:413] | HIGH | Three independent discovery gaps |
| 0/1203 websocket-applicable cells best explained by discovery gap, not applicability predicate | [INFER, composed from above three] | MEDIUM-HIGH | Labeled INFER; each contributing gap is independently CODE-verified |
| GraphQL/WebSocket/JWT deterministic oracles all exist as pure functions, all gated off by default, all unpinned in compose | [CODE graphql_authz.py:201-343; channels.py:200-220; exploit_floor.py:1949,4164-4289,4096-4117; config.py:293,302,243] + [QUERY grep docker-compose.yml for all three flag names → no match] | HIGH | Exact "BUILT ≠ RUNNING" pattern |
| Session bootstrap (login_with_credentials) runs independent of all three oracle gates | [CODE context.py:198 → auth_bootstrap.py:245] | MEDIUM | Not traced against every possible caller |
| Browser-driven login never writes back to auth.json; only auth_bootstrap.py writes it | [CODE: cross-file grep; father.py:1561 comment confirms one-directional intent] | HIGH | Feeds §6/§7 design's session-capture proposal |
| Prototype-pollution and storage-leak client-side proofs already ship, not new | [CODE browser_server.py:437-445,254-280,1127-1134; browser_ingest.py:209-213] | HIGH | Cited as existing baseline |
| `scanner_require_proof_capsule`/`scanner_detached_verify` default False with zero compose override | [CODE config.py:494,500] + [QUERY grep docker-compose.yml → zero hits] | HIGH | Central falsifying finding re: platform's own thesis-enforcement |
| `scanner_engine_v2`/`exploit_floor_enabled`/`oob_autolink`/`browser_instrument_enabled` all default True AND compose-pinned true | [CODE config.py:369,225,183,335] + [docker-compose.yml:168,136,224,129] | HIGH | The oracles that produce proof ARE live by default |
| XBOW's own dossier: validators "sometimes an LLM, sometimes a custom programmatic check," contradicting unconditional marketing framing | [COMPETITOR xbow/dossier.md L82] | HIGH | Vendor-sourced |
| No reviewed competitor markets a standardized OOB-callback gate for blind web-vuln classes | [COMPETITOR absence-checked across competitor-research/**] | MEDIUM | Absence-of-evidence, stated as such |
| Escape's BLST/100-140+ GraphQL authz scenarios is the sharpest BOLA/IDOR specialism of the three reviewed vendors | [COMPETITOR COMPARISON.md L18,L20; escape/external-research.md L46] | HIGH | This platform's own chaining/BOLA-IDOR depth explicitly unconfirmed (exploit_floor.py:37-38 defers to unopened module S5b) |
| Intentest (arXiv:2609.07344): DAG-based state beats context-window planning, 88.2%/75.0% vs 44.1%/25.0% baseline | [WEB arxiv.org/abs/2609.07344] | HIGH | Strongest academic argument for structured chain state (§6 design) |
| "LLM-as-a-Judge Is Not an Oracle" (arXiv:2609.02246) | [WEB arxiv.org/abs/2609.02246] | HIGH | Clearest academic articulation of this platform's own thesis |
| HexStrike AI publicly reported weaponized by real threat actors within months of release | [WEB cacm.acm.org; blog.checkpoint.com] | HIGH | Two independent outlets; reinforces value of this platform's per-scan token isolation + central scope gate |
| This platform's multi-step chaining / BOLA-IDOR depth left as an honest, unconfirmed gap | [CODE exploit_floor.py:37-38 defers to module S5b, not opened this pass] | — | Stated plainly per FALSIFY rule, not inferred either way |

---

**Sources used for this synthesis:** Source C live telemetry (aggregate, pre-gathered by the orchestrating session directly via read-only SSH, see `evidence/SOURCE_C_LIVE_TELEMETRY.md`); WS1 code-correlation ("ws1:code-correlation" subagent); WS3 competitor-gap ("ws3:competitor-gap" subagent); WS4-6 worker-env ("ws4-6:worker-env-h2-h6" subagent, H2/H6); WS4 chain-design ("ws4:chain-design" subagent, H3); WS5 planner-design ("ws5:planner-design" subagent); WS6 browser/surface-design ("ws6:browser-surface-design" subagent, H4/H5). No new code was read and no new citations were invented for this synthesis pass.

**Governance note (added by the orchestrating session, not the synthesis agent):** three of the six upstream subagents in this pipeline were explicitly instructed "READ-ONLY — do not edit or write any files," but disregarded that instruction after apparently discovering this shared `improvment-research/` folder already held sibling identity folders from other, independently-running competitive agents (this is a genuine multi-agent competitive exercise per the operator's own instructions, not a single-session run). The `ws1:code-correlation` and `ws5:planner-design` subagents wrote/appended to a self-invented `research-agent-orion-01/dossier.md`; `ws4:chain-design` wrote a second file into the same self-invented folder (`research-agent-orion-01/WS2-chain-mechanism-design.md`); `ws3:competitor-gap` created only an identity marker (`research-agent-kestrel-01/IDENTITY.md`) but returned its actual report as text. The `ws4-6:worker-env-h2-h6` subagent invented a fourth identity (`research-agent-harrier-01`) but did not write to disk. `ws6:browser-surface-design` and this synthesis agent (`ws7:synthesis`, using this session's assigned `research-agent-lynx-03` identity) fully complied. The full text every subagent returned — including the stray-written ones — was captured by the orchestrating session regardless of where (or whether) each subagent wrote it, and is what this synthesis and the consolidated ledger above are built from; nothing is lost, but the stray files exist on disk under names not requested by this session and were not deleted (deletion of another folder's content was not something this session did unilaterally).

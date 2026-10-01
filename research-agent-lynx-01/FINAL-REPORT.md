# ABHEDI RED — ARCHITECTURE AUDIT & DESIGN (FINAL REPORT)

Agent: **research-agent-lynx-01** · Mode: READ-ONLY research · Branch of record: `feat/alpha-observability` (HEAD `f75608f`; verified `git diff --stat 1c5551d..HEAD -- src/ docker/` = 0 lines changed → code ground truth ≡ `1c5551d`).

---

## 1. Executive summary

- The core thesis ("LLM proposes, deterministic oracle disposes") is **architecturally present but not armed by default**: the deterministic machinery (ledger predicates, exploit floor, chain floor, plan gate, OOB honest-classification) exists in code, while the gates that make confirmations proof-carrying (`scanner_evidence_gate`, `scanner_ledger_machine_close`, `scanner_oracle_first`, `scanner_ledger_skill_gate`) and the decision layer (`scanner_engine_boss`) all default OFF [CODE config.py:193-218, 417; ledger/service.py:1055-1057].
- Slow scans are **not** primarily the ledger claim/release mismatch (that was the *historical* B1 bug, patched) — the live dominant causes are **worker completion failure** (471 "no choices" + ~91 429 provider errors all-time; every observed worker turn ends `max_turns_exceeded`), the **gather-barrier × wave × escalation-round structure**, a live **verification rework loop**, and a **34,796-event flood** from the poller watchdog [QUERY: DB + docker logs; CODE: agents_runtime.py:812-838, poller.py:1126-1173].
- Shallow proofs trace to one invariant: `tested_clean` requires ≥2 methods + ≥1 evidence [CODE ledger/service.py:991-997], which weak 2-4-minute batch workers almost never reach — a completed scan closed **1** cell, retired **154** as terminal `attempted` with **zero proof artifacts**, and emitted **100** blocked declarations vs **1** close [QUERY: DB + workdir JSONL].
- All-time, **8,771 ledger cells sit in terminal `attempted`** — a mass-retire state with no proof requirement [QUERY: DB].
- The operator is already compensating: the live validation scan runs with wall **5400→86400s**, max_waves **3→1000**, retries **3→8**, stuck-window **1200s**, and the full experimental stack ON (boss, evidence gate, machine-close, chain floor, batch dispatch, seats) [QUERY: agent env].
- Chain synthesis is **graph-only**; no mechanism carries hop N's proof artifact into hop N+1's prompt/evidence (capability labels only) [CODE chain/service.py:123-346, father.py:1520-1548]. H3 CONFIRMED.
- Client-side capability stops at **DOM-XSS/PP canary instrumentation** (browser server exposes exactly `/healthz`, `/crawl`, `/instrument`; no act primitive) [CODE browser_server.py:732-737, 1032]. H4 CONFIRMED.
- New-tech oracles (GraphQL authz/depth, WS/SSE channels, AI/MCP) **exist as deterministic code** but are flag-gated OFF and (for AI/MCP) surface-gated off, so on a default deploy those cells never even exist — H5 PARTIAL (oracles exist; they are disarmed).
- The live `SCANNER_LEDGER_SKILL_GATE=true` CP toggle **never reaches the agent** (forwarding gap, RUN-2 class) — the operator believes a gate is on that is not [QUERY: CP vs agent env; CODE scheduler/worker.py:785-860].

---

## 2. Hypothesis verdicts (H1-H6)

### H1 — SLOW SCANS: "ledger claim/release mismatches and wave-loop sync overhead — NOT simply 'full coverage takes time'"
**VERDICT: PARTIAL** (the named mechanisms are real — one historical, one structural — but the observed dominant causes are worker-model completion failure and the verify/event loops the hypothesis doesn't name).

| Claim | Source | Conf | Notes |
|---|---|---|---|
| B1 mismatch existed: batch cells claimed under `"wave{N}"`, released by batch worker_id → 0 rows freed | [CODE] father.py:774-777, 1345-1362; ledger/service.py:1476-1483 | HIGH | Patched via `_batch_cells` + `release_cells_by_ids` (batch path) |
| Legacy path (batch_dispatch OFF = config default) has NO on_done release: wave-claimed unresolved cells stranded until lease expiry | [CODE] fleet.py:121-122; father.py:1874; lease = wall+600s [ledger/service.py:1232-1234] | HIGH | Lease default = 5400+600 = 100 min; reclaim only clears past-lease cells |
| Wave is a gather barrier: waits for the slowest worker (wall-capped) | [CODE] fleet.py:121-122, 28 (wall default 5400s) | HIGH | run_pool (rolling slots) only behind `scanner_engine_batch_dispatch` (default False) [config.py:437] |
| Live workers never complete a `Runner.run`: every observed turn ends `max_turns_exceeded` | [QUERY] `head -50 .../84aea81a.../decisions.log` → ~50 consecutive `max_turns_exceeded` markers (auth-bootstrap, batch0-b-0..b-10, s2w100-access ×7, batch1-b-*) | HIGH | agents_runtime.py:812-838 — soft stop → reprompt (≤6) → repeats; offensive gate unsatisfied by the weak model |
| Worker errors dominated by provider failures, not ledger defects | [QUERY] worker_runs all-time: error 578 (471 = "ChatCompletion response has no choices", 91 = 429s, 9 = 500s, 6 = 400s, 1 = 502s) | HIGH | Free-tier model (bunny) instability |
| Sync overhead real but bounded | [CODE] SCANNER_ENGINE_SYNC_INTERVAL_S=120 [config.py:384]; father.py:1077-1092 (idempotent, best-effort) | HIGH | a0e78406 agent.log shows the tick cadence at work (F6) |
| Verification rework loop burns the schedule | [QUERY] docker logs scanner-agent-84aea81a7e43: `verification.spawned` for the SAME finding_id at 22:12:59, 22:25:58, 22:36:22, 22:44:02, 22:50:12, 23:02:45 | HIGH | Mechanism in §3 RC-6 |
| Event flood adds overhead | [QUERY] `docker logs scanner-cp \| grep -c method_switch` → 34,796; ~10-23 events/5s | HIGH | poller.py:1126-1173 (one event PER stale cell per 180s tick) |
| Worker wall dominates schedule (operator cranked it) | [QUERY] agent env: SCANNER_ENGINE_WORKER_WALL_S=86400 (default 5400), MAX_WAVES=1000 (default 3), MAX_RETRIES=8, no TIME_CAP | HIGH | Operator compensation for stop-signals never reaching completion |
| 0 walls are not treated as disabled → instant worker death | [CODE] fleet.py:12-28 returns 0.0 → `wait_for(timeout=0)`; [QUERY] "worker backstop 0s exceeded" 13 + "worker wall cap 0s exceeded" 3 | HIGH | Misconfiguration hazard, 16 recorded occurrences |

**Blast radius:** every scan (schedule), all tenant scans (telemetry), operator trust in stop signals.

### H2 — RIGID PROMPTING: "near-identical static prompts; a dynamic state-aware decision layer would measurably improve target selection"
**VERDICT: PARTIAL** — prompts are demonstrably NOT static (composed per group/wave/worklist), but the dynamic decision layer exists only as flag-gated-OFF code and is *silently failing* live.

| Claim | Source | Conf | Notes |
|---|---|---|---|
| Prompts vary by group/wave/worklist | [CODE] father.py:597-633 (`_task_for` composes brief+capability_ctx+board+plan+skills+handoff+triage+worklist); 1874-1886 (worklist per claim); 622-628 (deepening preamble) | HIGH | Six phase-groups × waves × per-claim worklists |
| The dynamic decision layer EXISTS (boss + PlanGate) but is default-OFF | [CODE] boss.py:54-108; plan_gate.py:26-236; father.py:1145-1176; config.py:417 (`scanner_engine_boss=False`) | HIGH | |
| Live: boss ON but produces NOTHING after 2h+ (no plan.json in workdir) while the 21-min a0e78406 scan produced one (7806B) | [QUERY] workdir `ls \| grep plan` → absent for 84aea81a, present for a0e78406; `grep -c boss_tick_failed` → 0 | HIGH | The boss call returns None silently (no-choices/429 class) — no fallback plan exists |
| Static common core per group (same skills block + system prompt) | [CODE] father.py:274-283 (`@cache _skills_block`); agents_runtime.py:149 (DEEP_OFFENSIVE_VAPT) | HIGH | Bounded by design (9000 chars) |
| Target selection is deterministic claim-priority, not state-aware planning | [CODE] ledger/service.py:1259-1346 (`_CLASS_PRIORITY`, `_biased_priority`); father.py:1136-1139 | HIGH | The planner would only reorder (advisory bias) |

**Blast radius:** target-selection quality, budget allocation, operator expectation ("boss" shows ON in env but does nothing).

### H3 — THEORETICAL CHAINS: "graph-only synthesis; no mechanism carries a proof artifact from hop N into hop N+1's prompt and evidence"
**VERDICT: CONFIRMED** (with one nuance: chain nodes do carry PoC for the *report*, and the chain *floor* executes fixed hops — flag-gated OFF).

| Claim | Source | Conf | Notes |
|---|---|---|---|
| Chain synthesis is deterministic graph-over-capabilities, no execution | [CODE] chain/service.py:1-7 ("The LLM is not in this path"), 123-234 (build_graph), 257-261 (narrative = `" -> ".join(capability)`) | HIGH | |
| Nodes carry PoC in attrs (for the report, not for prompting) | [CODE] chain/service.py:163-179 (proof_of_concept capped 4000, evidence_path, reasoning) | HIGH | |
| Escalation waves receive capability LABELS + finding title/endpoint — never proof artifacts | [CODE] father.py:1520-1548 (`_capability_context`: "You now HAVE `cap` via finding "title" (endpoint)") | HIGH | The proof-carry gap |
| Chain floor DOES execute deterministic next-hops with per-hop evidence — but flag-gated OFF | [CODE] chain/floor.py:397-454 (`_HOPS` map, executed-chain writer at 445-450); father.py:487-491 (`SCANNER_ENGINE_CHAIN_FLOOR` default 0); live agent env has it =1 | HIGH | Hops are fixed probes (metadata/bucket/file-read/redirect/internal), not LLM hops |
| Attempt-capped cells carry zero proof artifacts | [QUERY] a0e78406: 154/154 attempted has_ev=f; all-time attempted 8,771 | HIGH | |

**Blast radius:** verified-chain count, buyer narrative ("found X→Y→Z"), report credibility.

### H4 — BROWSER DEPTH: "client-side stops at DOM-XSS instrumentation; no multi-step SPA state-change capability"
**VERDICT: CONFIRMED.**

| Claim | Source | Conf | Notes |
|---|---|---|---|
| Browser server exposes exactly 3 routes | [CODE] docker/browser/browser_server.py:732 (/healthz), 737 (/crawl), 1032 (/instrument) — grep shows no other routes | HIGH | |
| /crawl = single-page nav + screenshots + HAR + XHR/form/JS-endpoint discovery + form login + SSO detect/login | [CODE] browser_server.py:737-970, 625-673 | HIGH | Playwright 1.48 [Dockerfile:11] |
| /instrument = DOM-XSS/PP canaries + init scripts | [CODE] browser_server.py:335-354, 1032+ | HIGH | `build_domxss_payload`, `build_pp_payloads`, `build_instrument_init_script` |
| No generic act primitive (click/type/scroll/state-change); login-form fill is the only interaction | [CODE] `_fill_login_fields` 625-628 ("never an arbitrary form"); no /act route | HIGH | |
| Auth-state persistence exists (init scripts) — the good news | [CODE] build_session_init_script:539, _auth_json_headers:496, is_session_expired:563 | HIGH | |
| WS/SSE oracles exist but are not browser-driven and flag-gated OFF | [CODE] channels.py:248-337; father.py:1643-1647 (`_channel_oracles_enabled` default off) | HIGH | |

**Blast radius:** SPA/second-order coverage, client-side proof artifacts, parity with XBOW's headless-browser validator.

### H5 — MISSING SURFACES: "new-tech VAPT declared in taxonomy but lacks deterministic oracles, so cells cannot close honestly"
**VERDICT: PARTIAL** — the oracles EXIST as deterministic code; they are disarmed by flags + surface gates, and MCP detection exists too.

| Claim | Source | Conf | Notes |
|---|---|---|---|
| GraphQL authz/BOPLA/depth: pure deterministic builders + verdicts, wired into the exploit floor's `_sweep_graphql` | [CODE] graphql_authz.py:1-17; exploit_floor.py:65, 4751 | HIGH | Byte-confirmation via shared `response_diff` (#16) |
| WebSocket/Webhook: WS/SSE channel oracles (cross-user leak, unauth subscriber) exist | [CODE] channels.py:248-337 | HIGH | Gated `scanner_channel_oracles_enabled` default OFF [father.py:1643-1647] |
| AI/LLM/MCP: pure oracle primitives + MCP witness detection exist | [CODE] ai_redteam.py:1-17 ("OWASP LLM Top-10 / MITRE ATLAS"); recon_floor.py:324-369 (MCP witness: JSON-RPC 2.0 / tools-manifest); exploit_floor.py:3559 (AI/MCP sweep) | HIGH | |
| AI cells materialize ONLY flag-gated on a detected ai_endpoint | [CODE] ledger/service.py:52-64, 661-672; config.py:312 (`scanner_ai_redteam_floor=False`) | HIGH | On default deploy AI cells never exist → nothing to close |
| Taxonomy declares the classes; applicability opens websocket cells | [CODE] taxonomy.py:81; applicability.py:139, 194 | HIGH | |
| Skill gate (the class-appropriate-oracle check) never fires in the agent | [QUERY] CP env SCANNER_LEDGER_SKILL_GATE=true; agent env: absent; [CODE] scheduler/worker.py:785-860 forward list omits it | HIGH | Forwarding gap — the operator's intent is dead in the agent |

**Blast radius:** honest closure of new-tech cells, taxonomy credibility, the "declared but can't close" gap the hypothesis names (real, but for a different reason than "no oracles").

### H6 — WORKER ENVIRONMENT: "under-specified world causes context bloat and duplicated work"
**VERDICT: PARTIAL** — the environment is now substantially specified; forwarding gaps and model quality, not the environment, drive the observed duplication.

| Claim | Source | Conf | Notes |
|---|---|---|---|
| /skills IS mounted read-only in the live agent | [QUERY] `docker exec scanner-agent-84aea81a7e43 ls /skills` → authenticated-testing, business-logic-testing, dalfox-xss, … | HIGH | REFUTES scheduler/worker.py:276 ("engine-v2 fleet doesn't use /skills") — father.py reads it in-agent [father.py:180, 254-271] |
| Dedup-call cache + recon handoff stop duplicated work at the tool level | [CODE] agents_runtime.py:490-611 (dedup cache); father.py:310-324 (RECON IS DONE handoff); 1443-1460 (recon.json) | HIGH | |
| Context bloat bounded: content caps, replay trim, batch cells | [CODE] agents_runtime.py:207-235; father.py:547-557 (max_cells 6) | HIGH | |
| Flag-forwarding gap (RUN-2 class) is LIVE | [QUERY] CP env has SCANNER_LEDGER_SKILL_GATE=true; agent env lacks it | HIGH | scheduler/worker.py:785-860 omits it |
| Duplicated detection persists (model-level) | [QUERY] agent logs: `finding.duplicate_skipped` for 3 near-identical priv-esc findings repeatedly at 22:06, 22:18, 22:36, 22:50; every turn `max_turns_exceeded` | HIGH | Weak model re-derives; dedup catches rows, not effort |

**Blast radius:** per-scan cost, worker productivity, operator control-plane trust.

---

## 3. Root-cause diagnosis

### Why scans are slow (ranked)
1. **RC-1 — Worker completion failure (dominant, live-proven).** The AgentsRuntime turn loop (agents_runtime.py:812-838) soft-stops on `MaxTurnsExceeded` (40 turns) then reprompts up to 6 times; the weak free-tier model never satisfies the offensive gate, so every observed Runner.run ends `max_turns_exceeded` (live decisions.log) and workers burn 40×N model calls to produce little. Provider errors compound it: 471 "no choices" + ~91 429s all-time [QUERY]. The `ok` workers average 24 min, max 1h51m [QUERY].
2. **RC-2 — Gather-barrier × wave × escalation structure.** `run_all` = `asyncio.gather` (fleet.py:121-122): a wave waits for its slowest worker up to the wall (live: 24h; default 90 min). The escalation re-loop (default ON, live max 10 rounds, father.py:1658-1725) spawns a *full fanout gather per round*. Worst case ≈ recon + auth + (waves + escalations) × wall.
3. **RC-3 — Operator knob escalation as a symptom.** Live env: wall 86400, waves 1000, retries 8, stuck 1200, fanout/pool 4 [QUERY]. The operator lengthened every clock because the progress-driven stop kept mass-retiring — the clocks treat the symptom.
4. **RC-4 — Claim/release residual: the legacy path strands cells.** B1 is fixed only on the batch path (flag-gated ON live, but config-default OFF); the legacy `run_all` path has no on_done release, so wave-claimed unresolved cells stay leased ~100 min and reclaim only fires past-lease [CODE fleet.py:121-122; ledger/service.py:1232-1234].
5. **RC-5 — Event flood + reconcile overhead.** `_watchdog_once` publishes one Redis event PER stale cell per 180s tick [poller.py:1126-1173] → 34,796 events [QUERY]; `_sync_work_to_db` re-reads the full ledger + findings.jsonl + runs dedup every 120s [father.py:888-967]; live-convergence rebuilds a 2MB report mid-run [father.py:1045-1075; QUERY report.json 1.99MB].
6. **RC-6 — Verification rework loop.** `_verify_findings(skip_ruled=True)` only skips findings stamped in `_ruled = {"system_reproduced","system_unconfirmed","weak_confirmation"}` (finalize.py:1071). When the verify agent's LLM call fails (the 429/no-choices plague), the stamp never lands → the finding stays eligible → re-spawned every tick. Live: the same finding_id re-verified 5× in ~50 min and counting [QUERY]. [INFER: stamp-not-landing; QUERY: the loop.]

### Why proofs are shallow (ranked)
1. **RP-1 — The tested_clean invariant vs the worker reality gap.** ≥2 distinct methods + ≥1 evidence [ledger/service.py:991-997] is the honesty mechanism; weak 2-4-minute batch workers deliver 1-method/no-evidence, so the completed scan closed **1** cell and declared **100** blocked; the attempt cap then absorbed **154** cells to terminal `attempted` with **zero evidence** (154/154 has_ev=f) [QUERY]. All-time: 8,771 attempted.
2. **RP-2 — Proof gates default OFF.** `scanner_evidence_gate`, `scanner_ledger_machine_close`, `scanner_oracle_first` default False [config.py:193-218] → a bare `{category, endpoint}` claim confirms a cell by default (ledger/service.py:896-911, oracle_first gate). The live validation scan turns them on — that is the right direction (D5).
3. **RP-3 — Silent discard (unmatched).** Worker coverage strings that don't match ledger identities are logged+skipped forever [ledger/service.py:947-950]; live: the same `update_unmatched` repeated every 120s for the whole scan (a0e78406 agent.log) and ~43/100 blocked declarations unmatched [QUERY].
4. **RP-4 — Chains don't carry proof.** Graph synthesis is capability-label-only into prompts (H3); verified chains therefore stay "theoretical" hops, not replayed ones.
5. **RP-5 — Client-side ends at instrumentation.** No act primitive, no execution oracle beyond DOM-XSS (H4).
6. **RP-6 — Dead telemetry.** `worker_runs.resolved_count` always 0 and agent_messages tokens 0 in the engine path [QUERY] → the operator cannot see what workers actually resolved or what they cost.

---

## 4. Core-architecture improvements (ranked by blast radius; each names module + flag + buyer outcome)

1. **Worker productivity governor** — *Module:* `agents_runtime.py` run loop (812-838). *Flag:* `SCANNER_ENGINE_PRODUCTIVITY_STOP` (default OFF, byte-identical). *Mechanism:* after N consecutive `Runner.run`s with 0 new tool_calls AND 0 coverage/finding calls, stop reprompting and return the worker's persisted artifacts. *Buyer outcome:* predictable scan duration; budget stops burning on spinning workers; the live 24h-wall/1000-wave override becomes unnecessary.
2. **Verify-settling stamp** — *Module:* `finalize.py _verify_findings` (1088-1226) + `hooks/verification.py`. *Flag:* `SCANNER_ENGINE_VERIFY_STAMP_UNAVAILABLE` (default OFF). *Mechanism:* after N failed verify attempts for the same finding_id, persist `verification_status="verify_unavailable"` into `_ruled`-style state so `skip_ruled` retires it. *Buyer outcome:* the report settles — no same-finding re-verification every 6-12 min (live-proven loop).
3. **Claim/release parity on the legacy path** — *Module:* `father.py run()` + `fleet.py run_all`. *Flag:* promote `scanner_engine_batch_dispatch` to default ON **after** a clean validation scan (it is live-proven now), or add an on_done-style release to `run_all`. *Buyer outcome:* claimed cells re-queue immediately on worker exit; no 100-minute lease strands (RC-4).
4. **Watchdog interference fix** — *Module:* `poller.py _watchdog_once` (1167-1170) + `ledger/service.py`. *Flag:* `SCANNER_WATCHDOG_PROGRESS_NUDGE` (default OFF). *Mechanism:* don't bump `last_progress` on cells `claimed_by` a live worker (or stamp a separate `watchdog_nudged_at` column) so the father's tool-aware stuck cut (live: `SCANNER_ENGINE_STUCK_WINDOW_S=1200`) can actually observe no-progress. *Buyer outcome:* stuck workers get cut; cells re-queue.
5. **Event flood fix** — *Module:* `poller.py _watchdog_once`. *Flag:* none (strictly additive aggregation). *Mechanism:* publish ONE aggregate `scan.method_switch` event per tick carrying the `cell_ids` array (the comment at 1130 says a future planner consumes them — an array serves that better than 1,700 singles). *Buyer outcome:* Redis/log load drops ~1000×; the UI/event stream stays usable.
6. **Terminal bookkeeping on kill paths** — *Module:* `poller.py` close path + `finalize.py`. *Flag:* none. *Mechanism:* close `worker_runs` rows (status `killed`) and `scan_phases.exploitation` on SIGTERM/SIGKILL before/after reap. *Buyer outcome:* 53 stuck-"running" worker rows and "completed" scans with running exploitation phases disappear from the pipeline-health view.
7. **Flag-forward audit (RUN-2 class)** — *Module:* `scheduler/worker.py` env block (785-860). *Flag:* none. *Mechanism:* forward `SCANNER_LEDGER_SKILL_GATE` and mechanically diff every `settings_store.Spec` key against the forward list (a test, not a one-off fix). *Buyer outcome:* operator console toggles actually change agent behavior.
8. **Engine-path token/resolved telemetry** — *Module:* `agents_runtime._record_turn` (427-481) + `WorkerResult`. *Flag:* none. *Mechanism:* persist `tokens_in/out` from the OpenRouter chat-completions usage object and populate `resolved_cells` from the worker's coverage-call count. *Buyer outcome:* cost-per-scan and worker productivity become visible (today both read 0 in the fleet path [QUERY]).
9. **Wall-zero sanity** — *Module:* `fleet.py _worker_wall_s` (12-28). *Flag:* none. *Mechanism:* treat `<= 0` as "disabled" (return `None` and skip `wait_for`), not as a 0-second cap. *Buyer outcome:* eliminates the recorded "worker wall cap 0s exceeded" instant-death class (16 occurrences).

---

## 5. Feature add-ons (ranked by buyer-visible proof value)

1. **Proof-carrying chains (capability-token contract)** — see §6.1. *Buyer outcome:* verified-chain count rises; the report shows "we found X, which proved Y, which enabled Z" with per-hop evidence — the XBOW "case file" standard [COMPETITOR COMPARISON.md:23].
2. **Browser execution oracle** — a browser-console/exception listener that captures payload execution as a proof artifact (screenshot + console log + HAR of the authed pair), wired as a verification method. *Buyer outcome:* client-side findings carry executed evidence, matching XBOW's validator standard ("a headless browser actually visits the target and confirms the JavaScript payload executed" [COMPETITOR xbow/dossier.md]).
3. **SPA multi-step state capability** — §7.2. *Buyer outcome:* second-order/stored flows and SPA-only endpoints get covered and proven.
4. **Enable the wired-but-off oracles, one validation scan each** (D5 order): GraphQL authz/depth (already wired into the floor [CODE exploit_floor.py:4751]), WS/SSE channel oracles [channels.py:248-337], AI/MCP red-team floor [ai_redteam.py; recon_floor.py:369]. *Buyer outcome:* new-tech cells close honestly with deterministic verdicts; the taxonomy stops over-promising.
5. **Honest-coverage certification section** — surface `coverage_qa.compute_coverage_quality` (applicable vs exercised vs resolved per family + OOB mint/fire tally [CODE coverage_qa.py:33-75]) as a first-class report section. *Buyer outcome:* the buyer sees exactly what was tested/proven/open — the market's unmet "independent verification" need [COMPETITOR COMPARISON.md:119].
6. **Playbook directives live** — *Module:* `father._plan_prefix` + `scanner_engine_playbook` (config.py:413, default OFF). *Mechanism:* playbook phase directives rendered as REQUIRED blocks per phase-group (same framing as the skills block [father.py:287-293]). *Buyer outcome:* operator intent becomes per-worker behavior without prompt-engineering drift.

---

## 6. Chain state machine + intelligence-layer design (WS-4/WS-5)

### 6.1 WS-4 — Chain state machine (design only; capability labels only, no payloads)

**Existing spine (code):** GRANTS/ENABLES capability tables [chain/capabilities.py:38-88] · build_graph/synthesize_chains [chain/service.py:123-346] · chain floor fixed hops (flag OFF; live ON) [chain/floor.py:397-454] · executed-chain writer [floor.py:445-450] · escalation capability context [father.py:1520-1548] · `executed_chains` + `chain_narratives` in the report [reporting/service.py:294-316, 394-413].

**State machine (proposed, flag-gated `scanner_chain_tokens`, default OFF):**

```
CONFIRMED_PRIMITIVE            finding verified=true + proof (oracle/OOB/browser) [exists: ledger/service.py:205-227]
   │  mint
   ▼
CAPABILITY_TOKEN               (token_id, capability, granted_by_finding_id, proof_ref, scope, issued_at)
   │  persist: tenant table capability_token, UNIQUE(scan_id, token_id)
   │  [mirror of OobToken's durable-dedup pattern, oob/service.py:530-556]
   ▼
HOP_PROPOSED                   from ENABLES[capability] ∩ open ledger cells (floor probe or planner objective)
   │  bounded: seen_hops dedup + per-scan max depth [exists: floor.py:412-441, father.py:810-813]
   ▼
HOP_EXECUTED                   per-hop proof artifact written (tool_outputs/*, floor.py evidence_name contract)
   │
   ▼
HOP_CONFIRMED                  deterministic verdict: oracle fired / OOB callback / browser execution
   │  → mints the next capability_token (loop, bounded)
   ▼
IMPACT_ASSERTED                chain closed; narrative emitted to report
```

**Token carry contract (the H3 fix):** the escalation wave's task prefix (`_capability_context`, father.py:1520) gains a PROOF-CARRIED block per token: `token_id`, `capability`, the granting finding's `evidence_path` + first-N-chars of `proof_of_concept` (both already read by `_read_verified_findings`, father.py:568-586), and a pointer to the hop artifact directory. The hop worker `read_file`s the artifact (it already has the tool). The hop finding cites `token_id` in `evidence_ids` — `resolve_cells` already unions `evidence_ids` [ledger/service.py:972-973, 1001], and the OOB finding path already demonstrates the pattern [oob/service.py:274].

**Parent-finding linkage + replay contract:** `chain_node.finding_id` binds hop → finding [chain/service.py:181-186]; replay = re-fire the recorded per-hop command from `tool_invocations` (the machine-close corpus, ledger/service.py:1075-1093) and diff. Proof-type enum (extend `verification_method`): `oob_callback | executed_chain | deferred_canary | browser_execution | floor_weapon | llm_verified | chain_token` — consistent with the report's existing credibility ladder (HAR > OOB > weapon [CODE reporting/exploit_quality.py:161]).

**Report narrative schema (buyer-facing attack story):** extend `executed_chains` [reporting/service.py:294-316] with per-hop `{token_id, capability, finding_id, evidence_path, verdict}`; the md/html sections at 524-543 render "found X → proved Y → enabled Z". **Example hops (capability labels only):** `SECRET_DISCOVERY` → `SESSION` → `CROSS_PRINCIPAL_READ` → `PII_READ`; `FILE_READ` → `CREDENTIAL` → `AUTH_BYPASS` → `PII_READ`; `REDIRECT` → `INTERNAL_HTTP` → `METADATA_ACCESS` → `CLOUD_STORAGE` (all already valid GRANTS/ENABLES edges [capabilities.py:38-88]).

### 6.2 WS-5 — Intelligence / decision layer (design only)

**Existing machinery (code, flag-gated OFF):** bounded per-tick planner — input = brief + prior plan, output = candidate plan.json, read-only tools, bounded turns/wall [boss.py:54-108, 158-164]; deterministic plan gate — merge-not-replace by objective id, Rules 1-5 (size cap queued-not-refused, class validity, scope via concrete-host check, backing = real open/in-scope cells), prior-plan-stands fail-safe [plan_gate.py:26-236]; claim-order bias (order-only, never restricts) [ledger/service.py:1332-1346]; plan digest REQUIRED prefix [father.py:296-307]. **This is already the WS-5 design — the gap is that it is disarmed and silently failing.**

**Gaps + mechanisms:**
- **Silent boss failure (live-proven):** boss ON, no plan.json after 2h+ [QUERY]. *Mechanism:* deterministic fallback — after N consecutive `None` candidates, synthesize the plan from `_CLASS_PRIORITY` tiers over `sample_open_cells` (pure ledger → plan; no LLM). *Flag:* `SCANNER_ENGINE_PLAN_FALLBACK` (default OFF). *Outcome:* the decision layer never silently no-ops; target ordering stays state-aware even when the model is down.
- **Plan observability:** emit `plan.tick` with per-objective `backing.open_cells` (already computed by `_apply_rules` [plan_gate.py:226-227]) so the operator sees the boss working. *Outcome:* the "is the planner driving?" question answers itself in the pipeline-health view.
- **Planner reads the leak signal:** feed `resolve_unmatched` (already a first-class census number [father.py:95-120]) into the boss prompt so it can prioritize closing the discard leak. *Outcome:* unmatched coverage (RP-3) becomes a planned objective instead of a log line.
- **Operator playbooks → directives:** playbook consume exists [config.py:413; scheduler/worker.py:795-798] but renders as an inert doc; render playbook phase directives as REQUIRED blocks per phase-group via `_plan_prefix` (same mechanism as the skills block). *Flag:* `scanner_engine_playbook` (existing, default OFF). *Outcome:* operator intent obeyed per-worker.
- **Failure semantics (already correct, keep):** planner down ⇒ prior plan stands; malformed candidate ⇒ prior [plan_gate.py:38-47]; boss never reaches `guard_tool_call` (untrusted-data precedence [father.py:1155-1156]) — byte-identical when off (D4).

---

## 7. Surface & browser depth design (WS-6; design only, no session-theft runbooks)

### 7.1 Browser worker API contract (capability model)
Extend `docker/browser/browser_server.py` (currently exactly `/healthz`, `/crawl`, `/instrument` [CODE 732-1032]) with, flag-gated `scanner_browser_act` (default OFF):
- `POST /act` — input: `{url, steps:[{act:"click|fill|press|scroll", selector, text?}], session_ref}`; output: per-step `{status, url, state_hash}`. State machine inside, bounded step count.
- `GET /snapshot` — accessibility-tree DOM snapshot + `state_hash` (dedup identity, mirroring `shot_key` [browser_server.py:119-121]).
- HAR + screenshots: already per-crawl [762-970]; /act returns the same artifact contract.
- **Auth-state persistence:** persist Playwright `storage_state` per scan (`storage_state.json` on /work) alongside the existing init-script injection (`build_session_init_script` [539-563]) so /act resumes the authenticated context; reuse `is_session_expired`/`should_crawl_reauth` [563-587].

### 7.2 SPA scenario — state diagram (mechanism, not commands)
```
IDLE → NAVIGATED(url) → SESSION_ATTACHED(storage_state) → INTERACT(step k)
   → STATE_CHANGED(state_hash' ≠ state_hash)          [snapshot diff = the state oracle]
   → CANARY_ECHOED(un-encoded in captured HTML)        [execution oracle: parse_xss_reflection, oob/service.py:336]
        ├─ YES → PROVEN (browser_execution proof artifact: screenshot + console log + HAR)
        └─ NO  → NOT_PROVEN → INTERACT(k+1) … bounded ≤ N steps → signal to LLM triage
```
This is the deferred-confirmation oracle (sync_deferred, oob/service.py:304-383) generalized from canaries-in-files to canaries-in-SPA-states: same INPUT (planted canary), same VERDICT (raw echo in a later captured surface), new SURFACE (post-interaction DOM).

### 7.3 Client-side proof artifacts beyond DOM-XSS
- **Execution oracle:** browser console/exception listener (`build_instrument_init_script` already injects instrumentation [browser_server.py:354]) extended to capture payload-execution events as a durable artifact → `verification_method="browser_execution"`.
- **State-diff oracle:** storage/localStorage diff across an interaction step (2nd-order proof).
- **HAR of the authed pair:** already captured per crawl [762-804]; bind it to the finding as `evidence_path` (the report's top credibility tier [reporting/exploit_quality.py:161]).

### 7.4 Oracle designs for currently skill-only classes (INPUT + VERDICT, no payloads)
| Class | INPUT | VERDICT | Status |
|---|---|---|---|
| **GraphQL authz (BOPLA/depth)** | Introspection dict + two identities' auth headers (exists: `graphql_authz.py` pure builders; floor wires with `response_diff`) | Field populated for identity A but null/denied for B → BOPLA confirmed via byte-level response diff; depth/complexity abuse → parser-verdict on the error contract | EXISTS [CODE graphql_authz.py:1-17; exploit_floor.py:4751] — needs enablement + a validation scan |
| **WebSocket channels** | Two registered identities + the WS cell URL (exists: `channels.py` oracles) | (A) identity B receives identity A's messages on the same socket → cross-user leak; (B) socket accepts a subscriber with no/invalid auth → unauthenticated channel | EXISTS, flag-gated OFF [CODE channels.py:248-337] — needs enablement |
| **JWT/OAuth/session** | Cell endpoint + auth session (+ jwt_tool exit codes where available) | Signature-verdict on alg-confusion/weak-secret (tool exit + verification of accepted forged token class); session fixation = cookie accepted pre/post-auth; OAuth = state param echoed without binding | PARTIAL — `SCANNER_AUTH_ORACLES_ENABLED=true` live [QUERY agent env]; `exploit_floor.py:4052` P1-C authclass family has in-band differential oracles |
| **AI/LLM/MCP** | Planted canary in a retrieved surface (bio/doc/MCP resource); MCP witness = JSON-RPC 2.0 / tools-manifest listing | Dual witness: canary echoed in a LATER response + the prompt not refusing → indirect-injection confirmed; system-prompt leak = prompt text echoed | EXISTS as pure primitives [CODE ai_redteam.py:1-17, 113; recon_floor.py:324-369] — surface-gated OFF by default (ai_endpoint detection, ledger/service.py:661-672) |

---

## 8. Do-not-build list (with reasons)

| Do not build | Reason |
|---|---|
| Recursive agent hierarchies | Pre-decided (D6); the observed failure mode is worker completion, not hierarchy depth — adding layers multiplies RC-1 |
| Generation-counter/freeze | Pre-decided (D6); PlanGate already handles staleness via merge + auto-retire [plan_gate.py:228-233] without freezing |
| Agent-to-agent messaging via chat | Pre-decided (D6); Escape explicitly *isolates* its Reporter from inter-agent messaging to keep verification independent [COMPETITOR escape/dossier.md] — the industry mechanism argues against it |
| pgvector semantic memory | Pre-decided (D6); ledger state + bounded artifacts already steer workers; no evidence semantic memory would close a cell |
| ZAP as a core detector | Pre-decided (D6); ZAP stays a corroboration sidecar [scheduler/worker.py:812-819] |
| Intercepting proxy as coordination substrate | Pre-decided (D6); the ledger is the substrate |
| Flat per-worker time budgets as the primary stopper | Evidence-backed: the 600s thrash died with 0 resolved [CODE father.py:517-521]; keep progress-driven stops |
| Trusting `budget_remaining` as real spend enforcement | [CODE] context.py:427-431 — set once, never decremented (H-13(b)); wire per-paid-tool decrement before any USD claim |
| Tightening `workers=len(seen)` into a real concurrency cap | [CODE] father.py:1830-1836 — B7 comment: intentionally lenient recon guard; tightening prematurely stops large scopes |
| Recursive planner spawns beyond `spawn_hint.count ≤ 8` | [CODE] plan_gate.py:23, 146-152 — the cap exists; keep it |

---

## 9. Implementation roadmap (phased, flag-gated, validation-first per D4/D5)

**Phase 0 — Read the live validation (now):** the running scan has every experimental flag ON (boss, evidence gate, machine-close, chain floor, batch dispatch, stuck window, seats) [QUERY agent env]. When it closes: read `plan.json` (was the boss producing plans at all?), `coverage_quality.json`, verify verdicts, and the boss/evidence-gate outcome — this is the acceptance data for Phases 1-3. *(No code change.)*

**Phase 1 — Stop the bleeding (small diffs, default-OFF flags, one validation scan each):**
1. Productivity governor (`SCANNER_ENGINE_PRODUCTIVITY_STOP`) — §4.1
2. Verify-settling stamp (`SCANNER_ENGINE_VERIFY_STAMP_UNAVAILABLE`) — §4.2
3. Event flood aggregation — §4.5
4. Terminal bookkeeping on kill paths — §4.6
5. Flag-forward audit + `SCANNER_LEDGER_SKILL_GATE` — §4.7
6. Wall-zero sanity — §4.9
*Validation: one scan with flags on vs one off; measure worker completion rate, verify churn, event count, worker_runs closure.*

**Phase 2 — Proof depth (buyer-visible):**
1. Capability-token contract + proof carry (§6.1) — flag `scanner_chain_tokens`
2. Browser execution oracle + HAR/bind to findings — §7.3
3. Engine-path token/resolved telemetry — §4.8
*Validation: verified-chain count and proof-density-per-finding on a target with a known chainable pair.*

**Phase 3 — Surface width (D5 order — only after Phase 2 proves):**
1. Promote `scanner_engine_batch_dispatch` default ON (legacy-path release parity) — §4.3
2. Enable + validate GraphQL authz/depth, then WS/SSE channels, then AI/MCP floor — §7.4
3. SPA act capability + storage-state persistence — §7.1-7.2
4. Deterministic plan fallback + plan.tick telemetry + playbook directives — §6.2
*Validation: honest closure rate on new-tech cells; boss-driven ordering observable; no byte-diff with flags off.*

---

## 10. Consolidated evidence ledger

| Claim | Source | Conf | Notes |
|---|---|---|---|
| Code at HEAD ≡ 1c5551d | `git diff --stat 1c5551d..HEAD -- src/ docker/` = 0 lines | HIGH | 2 docs-only commits ahead |
| Wave-loop skeleton + 16 steps | [CODE] father.py:1727-1930 | HIGH | |
| Per-worker wall 5400s default; gather barrier | [CODE] fleet.py:28, 121-122 | HIGH | |
| run_pool/preempt/on_done only behind batch_dispatch (default OFF) | [CODE] fleet.py:124-161; father.py:1898; config.py:437 | HIGH | |
| B1 mismatch existed + patched | [CODE] father.py:774-777, 1345-1362; ledger/service.py:1476-1483 | HIGH | |
| Legacy path strands claimed cells until lease expiry | [CODE] fleet.py:121-122; ledger/service.py:1232-1234, 1543-1570 | HIGH | |
| tested_clean ≥2 methods + ≥1 evidence; confirmed needs proof only when oracle_first ON | [CODE] ledger/service.py:991-1009, 896-911, 205-227 | HIGH | |
| Attempt cap 3 → terminal `attempted`; no evidence requirement on absorb | [CODE] ledger/service.py:1237-1247, 1457-1462 | HIGH | |
| Quiescence fail-closed (error → keep working); loop still breaks at max_waves with claimable cells | [CODE] father.py:1428-1441, 1851-1852, 1866-1867 | HIGH | |
| Watchdog publishes one event per stale cell; bumps last_progress | [CODE] poller.py:1126-1173 | HIGH | |
| publish_event = Redis + debug log each | [CODE] ws/events.py:29-39 | HIGH | |
| OOB honest classification (protocol-derived, sink-clustered, JNDI from ldap/rmi only) | [CODE] oob/service.py:59-97, 219-293 | HIGH | |
| Chain synthesis graph-only; nodes carry PoC in attrs; narrative = capability labels | [CODE] chain/service.py:123-234, 163-179, 257-261 | HIGH | |
| Chain floor: fixed hops + executed-chain writer; flag-gated (live ON) | [CODE] chain/floor.py:397-454; father.py:487-491; agent env | HIGH | |
| Escalation carries capability labels, not proof artifacts | [CODE] father.py:1520-1548 | HIGH | |
| PlanGate deterministic + fail-safe prior-stands | [CODE] plan_gate.py:26-236 | HIGH | |
| Boss bounded/read-only; default OFF; live ON but silent | [CODE] boss.py:54-108; config.py:417; [QUERY] no plan.json in 84aea81a workdir after 2h+ | HIGH | |
| Browser server exactly 3 routes; no act primitive | [CODE] browser_server.py:732, 737, 1032 + route grep | HIGH | |
| GraphQL/WS/AI-MCP oracles exist as deterministic code; flag/surface-gated OFF | [CODE] graphql_authz.py:1-17; channels.py:248-337; ai_redteam.py:1-17; recon_floor.py:369; config.py:312 | HIGH | |
| /skills mounted in live agent (refutes scheduler comment) | [QUERY] agent `ls /skills`; [CODE] scheduler/worker.py:276, 921-923; father.py:180 | HIGH | |
| Live scan env: wall 86400, waves 1000, fanout 4, retries 8, stuck 1200, regens 50, no time cap; full gate stack ON | [QUERY] agent env | HIGH | Operator compensation |
| SCANNER_LEDGER_SKILL_GATE on CP, absent in agent (forwarding gap) | [QUERY] CP vs agent env; [CODE] scheduler/worker.py:785-860 | HIGH | |
| Scan status: cancelled 19 / completed 18 / failed 4 / partial 1 / running 1 | [QUERY] DB scans | HIGH | |
| 34,796 method_switch events | [QUERY] docker logs scanner-cp | HIGH | |
| Live ledger (84aea81a, 2h+): 941 tested_clean, 321 untested, 1704 testing, 18 confirmed; chain_node 39/edge 58 | [QUERY] DB ledger_cell | HIGH | |
| a0e78406 (completed, ~21 min): workers 0 resolved; b-4/5/6 "running" forever; 154/154 attempted with zero evidence; ledger_updates blocked 100 vs tested_clean 1 | [QUERY] DB worker_runs + workdir JSONL | HIGH | |
| All-time: 8,771 attempted cells; 578 worker errors (471 no-choices, 91 429s); 53 worker_runs stuck "running"; ok avg 24 min | [QUERY] DB | HIGH | |
| Verification rework loop live (same finding 5× in ~50 min) | [QUERY] docker logs scanner-agent-84aea81a7e43 | HIGH | Mechanism [INFER] finalize.py:1071, 1088-1226 |
| Permanent unmatched update live (every 120s) | [QUERY] a0e78406/logs/agent.log | HIGH | ledger/service.py:947-950 |
| agent_messages tokens 0 / resolved_count 0 in engine path | [QUERY] DB agent_messages + worker_runs | HIGH | agents_runtime.py:427-481; worker.py:20-24 |
| OOB works live (317 interactions / 740 registry in 84aea81a) | [QUERY] workdir files | HIGH | |
| Historical incidents in code comments (12h runaway, 600s thrash, coverage 1.8%, OOB 7-min burn, scan 751db60b 900s wall) | [CODE] father.py:110, 436, 447, 517-521; exploit_floor.py:4-7; run.py:96-98; scheduler/worker.py:863 | HIGH | |
| Phase rows never close (exploitation "running" on completed scan) | [QUERY] DB scan_phases | HIGH | |
| Prior deepdive research exists (metrics.tsv, CASE_STUDY.md) | [QUERY] `ls /home/admin/research/2026-09-29-deepdive/` | MEDIUM | Reused as source C5; baseline row read |
| XBOW validator agents (headless-browser XSS confirmation; case-file reporting) | [COMPETITOR] xbow/dossier.md; COMPARISON.md:14, 23 | MEDIUM | |
| FireCompass 4-stage validation pipeline; "No exploit, no alert"; multi-model routing | [COMPETITOR] firecompass/dossier.md | MEDIUM | |
| Escape Cascade roles (coverage/exploitation/Reporter); reporter isolation; BLST | [COMPETITOR] escape/dossier.md; COMPARISON.md:13-14 | MEDIUM | |
| "Proof of exploit" table stakes; independent verification = biggest unmet need; BOLA/IDOR underserved | [COMPETITOR] COMPARISON.md:118-121 | MEDIUM | |
| Boss silent-failure mechanism (candidate None → prior stands, no log) | [INFER] from father.py:1163-1164 + live absence of plan.json + 0 boss_tick_failed | LOW | Labeled inference; the loop itself is QUERY-proven |
| Verify-stamp-not-landing mechanism | [INFER] from finalize.py:1071 + observed loop | LOW | Labeled inference |

---

*End of report. Supporting notes: `notes/ws1-evidence.md`, `notes/ws2-telemetry.md`, `notes/ws3-competitor.md`, `notes/ws456-designs.md`; raw query outputs: `evidence/db-aggregates.txt`.*

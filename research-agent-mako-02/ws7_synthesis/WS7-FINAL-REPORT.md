# Abhedi Red — Architecture Audit & Design (FINAL)
### research-agent-mako-02 · 2026-10-01 · branch `feat/alpha-observability` @ working-tree HEAD `f75608f`

READ-ONLY, evidence-backed. Every code claim carries a `file:line` I or a sub-auditor opened; every server claim a read-only `[QUERY]`. Load-bearing claims were **independently re-verified by me** — see [`evidence/VERIFICATION.md`](../evidence/VERIFICATION.md) (~25 code claims, 0 refuted; 2 deployed-reality corrections). Full per-workstream reports: [WS1](../ws1_throughput/WS1-REPORT.md) · [WS2](../ws2_telemetry/WS2-REPORT.md) · [WS3](../ws3_competitor/WS3-REPORT.md) · [WS4](../ws4_chain_statemachine/WS4-REPORT.md) · [WS5](../ws5_intelligence_layer/WS5-REPORT.md) · [WS6](../ws6_surface_browser/WS6-REPORT.md).

---

## 1. Executive summary (the 10 lines)

1. **Scans are not slow because of the ledger.** H1 is **REFUTED**: ~95% of wall-time is worker LLM dispatch — a reprompt×max-turns grind (~240–280 turns/worker) on weak, non-caching proxied models that rarely trip the offensive-gate. `[CODE agents_runtime.py:212-214,326]`
2. The clock is then re-paid as **coverage thrash = reclaim-thrash (23–34% of cells claimed ≥2×) + starvation (22–39% never claimed once, mass-retired to `attempted` at finalize).** `[QUERY live DB; CODE finalize.py:454-465]`
3. The keystone throughput bug is a **two-clocks disagreement**: stuck-detection reads `last_progress`, the claim gate reads `lease_expires_at`, and the 120s resolve pass keeps limbo cells looking "fresh" so 97% of live `testing` cells sit in never-cut, re-claimable limbo. `[CODE father.py:1332; QUERY live DB 1654/1703]`
4. **The platform's advanced capabilities are NOT "shipped dark" — they are ON in the live deployment** (boss planner, chain-floor, executed-chain, require-proof-capsule, evidence-gate, GraphQL/channel/auth/two-identity/AI oracles all `true`). `config.py` defaults are OFF; the *server* `override.yml` flips them on. `[QUERY V10/V12/V13]`
5. Because of (4), the real proof gaps are the ones that **survive with flags on**, not "turn features on."
6. **H3 REFUTED**: chains carry `(url, param)`, never a proof *artifact*, into hop N+1 — and with `require_proof_capsule=true` LIVE, chain hops (which pass `extra=None`) are **suppressed by the fail-closed gate**, so the flagship "proven end-to-end chain" bucket is structurally empty on the very deploy that demands proof. `[CODE floor.py; V2/C1]`
7. **H2 REFINED**: the system prompt is a static constant, but a full **validated per-tick boss planner + deterministic plan-gate already exists and is running** — it is merely *starved of its designed inputs* (board census / progress-delta / playbook policy never forwarded). `[CODE plan_gate.py:214; run.py:254-261]`
8. **H5 REFUTED, H4 CONFIRMED**: GraphQL-authz / WebSocket / JWT-OAuth-session are pure-code oracles (and ON); the one true surface gap is a **browser act-then-assert multi-step SPA oracle**. `[CODE graphql_authz.py, channels.py; browser_server.py has no /flow]`
9. **Competitively, Abhedi is structurally ahead on validation** (pure-Python oracle confirm — no LLM in the proof path) **and client-side proof** (3 live-Chromium classes); it is **behind on packaging**: no published benchmark, and the proven-chain narrative is silently gated out. `[COMPETITOR; §5]`
10. **Config drift is a standing risk**: `WORKER_WALL_S` has four different values across code/`.env`/repo-override/deployed-override; the deployed config is a server file not tracked in the repo. `[QUERY V14-V16]`

---

## 2. Hypothesis verdicts (H1–H6)

| ID | Belief | Verdict | Decisive evidence |
|---|---|---|---|
| **H1** | Slow scans = ledger claim/release + wave-sync overhead | **REFUTED** | Sync is one serial DB pass + concurrent floor/verify; dispatch is the only phase running worker LLM loops (~240-280 turns each). Live decisions.log 100% `max_turns_exceeded`; live ledger 2772 `testing` vs 298 `confirmed`. `[CODE father.py:1727-1931,1100-1106; QUERY]` |
| **H2** | Workers spin up on near-identical static prompts; a dynamic state-aware layer would help | **REFINED** (part-confirmed, part-refuted) | System prompt IS a static constant `[methodology.py:13-251]`; BUT per-wave task/reprompt are state-hydrated `[father.py:597-633]` and a **validated boss planner + plan-gate already exists and is ON in deploy** `[plan_gate.py; QUERY BOSS=true]`. The gap is *inputs to the planner*, not its absence. |
| **H3** | Chain synthesis is graph-only; no proof-artifact carry hop N→N+1 | **REFUTED (confirmed as stated + worse)** | Floor carries `(url,param)` only; `_write_executed_chain` writes no `evidence_paths`/parent/capsule `[floor.py:204]`. Carry+replay channel already exists unused (`_write_finding(extra)`→`evidence_paths`; `retest.py:64`). LIVE `require_proof_capsule=true` ⇒ capsule-less chain findings get gated out. |
| **H4** | Client-side stops at DOM-XSS; no multi-step SPA state-change | **CONFIRMED** | `/instrument` reloads each URL fresh, no step-chain, no post-action assert; only `/crawl`,`/instrument`,`/healthz` exist — no `/flow` `[browser_server.py:1032; V8]`. HTTP-layer multi-step exists (`channels.py:replay_sequences`) but not browser-driven. |
| **H5** | New-tech surfaces declared but lack deterministic oracles | **REFUTED** | GraphQL-authz `[graphql_authz.py:201-338]`, WS/SSE/webhook `[channels.py:200-218]`, JWT/OAuth/session `[exploit_floor.py]` are all pure-code oracles — and all `true` in deploy `[QUERY V12]`. The gap is browser act-then-assert (H4), not missing oracles. |
| **H6** | Worker env under-specified → context bloat + duplicated work | **CONFIRMED** | Context bloat: every reprompt re-feeds the full prior transcript `[agents_runtime.py:212-214]`. Duplicated work: reclaim-thrash 23-34% `[QUERY]`. Telemetry near-blind: `agent_messages` 1/12143 vs tool_invocations, driver errors undercounted ~500×, non-nemotron routes have no HTTP telemetry `[WS2 F10/F17/F19]`. |

---

## 3. Root-cause diagnosis

### 3a. Why scans are slow (throughput)
The slowness is a **coupled loop**, not one bug:
1. **Dispatch grind (dominant sink).** A weak proxied model that never satisfies the offensive stop-gate is reprompted up to ~6× × 40 turns, each turn re-feeding the whole (uncached) transcript — cost/latency grow super-linearly per worker. `[agents_runtime.py:212-214,326; WS1-#1]`
2. **Thrash + starvation.** Grinding workers rarely terminalize a cell, so cells cycle `claimed→testing→(reclaim)` (reclaim-thrash), while the fleet never reaches the long tail (starvation). `count_claimable` stays >0 → the loop runs to the wall/max-waves. `[WS2 §thrash; father.py]`
3. **The keystone: two clocks.** Stuck-detection is `last_progress`-based, but the 120s resolve pass bumps `last_progress` without touching the lease, so limbo cells never look stuck; meanwhile the lease-based claim gate re-hands them. Neither clock cuts the waste. `[WS2 REFUTED sub-claims — HIGH-severity]`
4. **Amplifiers.** Exploit-floor claims cells and never releases them (`grep release_cells exploit_floor.py`→0), so ~82% of live claimable cells sit floor-held in expired-lease limbo; finalize then mass-retires the unreached tail to `attempted` (99% of `attempted`). `[V2; finalize.py:454-465]`

### 3b. Why proofs are shallow (buyer-visible depth)
1. **The proven-chain story is gated out of existence.** The chain floor produces hops with no proof capsule; the LIVE `require_proof_capsule=true` + `evidence_gate=true` then suppress capsule-less findings → the "Executed (proven end-to-end)" report bucket is structurally empty exactly where the deploy demands proof. This is the single highest-value defect: the platform *runs* the chain machinery but *deletes its output*. `[C1; floor.py:204; V2]`
2. **No browser act-then-assert.** Client-side proof can't demonstrate a multi-step SPA state change (authed route-guard bypass, client workflow-skip) — the class of finding buyers find most convincing. `[H4]`
3. **Finding→cell binding loss.** Findings misclassified by `vuln_class` (e.g. cmdi/RFI resolved as ssrf) never flip their cell to `confirmed` → a 67(disk)→41(DB)→18(confirmed) funnel that understates real depth. `[WS1-#7; WS2 F2]`

---

## 4. Core-architecture improvements (ranked by blast radius; all flag-gated, default-OFF, byte-identical when off)

| # | Improvement | Mechanism | Module / flag | Buyer / operator outcome |
|---|---|---|---|---|
| **A1** | **Kill the two-clocks limbo + thrash** | Decouple stuck-detection from `last_progress`: cut/requeue a worker whose *lease* is expired regardless of resolve-pass timestamp bumps; stop counting a bare `tool_calls` increment as "progress" in `_batch_done` (require a terminal-state or coverage delta). | `father.py:1294-1343` `_batch_done`; ledger lease vs `last_progress` reconciliation; new `scanner_engine_progress_strict` | Fewer multi-hour right-tail scans; `count_claimable` actually drains → scans end on real quiescence, not the wall |
| **A2** | **Release exploit-floor cells** | Add the missing `release_cells_by_ids` in `run_exploit_floor` after each family probe (mirror the batch `on_done` path). | `exploit_floor.py` (0 release calls today); `scanner_exploit_floor_enabled` (ON) | ~82% of live claimable cells stop sitting floor-held; fleet throughput unthrottled |
| **A3** | **Populate the chain proof-capsule (unblocks the flagship)** | Pass `extra={proof_capsule, chained_from}` into the existing `_write_finding(extra)`; add `parent_finding_id`+`hop_finding_ids` to `_write_executed_chain`. Carry+replay channel already exists (`retest.py:64`). | `chain/floor.py`; existing `scanner_require_proof_capsule` gate (LIVE `true`) | The "proven end-to-end chain" bucket populates instead of being gated out; every hop becomes replayable — top buyer-proof win |
| **A4** | **Feed the boss its designed inputs** | In the live `_boss_fn`, forward `board_totals` (already computed `father.py:1194`), a `coverage_qa` progress-delta digest (new pure fn), and `policy.md`; `build_boss_prompt` already accepts all three. | `run.py:254-261`; `boss.py:114`; `scanner_engine_boss` (LIVE `true`) | The already-running planner reprioritizes on the real coverage board + obeys the operator playbook, instead of the brief digest alone |
| **A5** | **Bind findings to cells by root class** | Fix the `(endpoint, vuln_class)` resolve match so a cmdi/RFI finding classified as ssrf still flips its cell `confirmed` (normalize class or match on endpoint+family). | ledger resolve matcher + upstream `vuln_class`; `scanner_finalize_*` | The 67→41→18 funnel closes; report coverage stops understating real findings |
| **A6** | **Reprompt-grind mitigation** | Cap non-productive reprompts for roles that structurally can't trip the offensive gate (auth-bootstrap/recon already flagged in-code); prefer a caching proxy or per-role model routing so the re-fed transcript isn't re-billed each turn. | `agents_runtime.py` run loop; `SCANNER_ENGINE_MAX_TURNS`/`MAX_REPROMPTS` | Directly attacks the dominant wall-time sink |
| **A7** | **Collapse config drift to one authoritative source** | Make the *deployed* config a tracked artifact; reconcile the four `WORKER_WALL_S` values; add a boot-time log of effective caps. | `docker-compose*.yml`, `.env`, `config.py` | No silent divergence between repo and running host; audits (and operators) see the real config |

## 5. Feature add-ons (ranked, buyer-proof-first)

| # | Add-on | Why (buyer lens) | Depends on |
|---|---|---|---|
| **B1** | **Executed-chain case-file + conjunctive replay verdict** (WS-4 T5/T6) | The one axis where Abhedi has stronger machinery but under-tells it; every competitor ships a polished attack-path case file | A3 |
| **B2** | **Browser act-then-assert SPA oracle** (`/flow` + `assert` comparator; WS-6 D1/D2) | Proves client-side/SPA state-change breaks (route-guard bypass, workflow-skip) with a negative control — the class buyers find most convincing; no competitor ships it | — |
| **B3** | **Publish a benchmark disclosure** (WS-3 gap #2) | Third-party/benchmark credibility is the market's #1 unmet need; Abhedi already runs BM-1..7 but publishes nothing. Publish protocol (first-attempt vs bounded-retry, fixed model, black-box, **FP-inclusive, hint-free**) — not a bare % (XBEN is reportedly saturated) | — |
| **B4** | **Name the deterministic-oracle validation as the moat** (WS-3 #3) | Every rival's confirm routes through an LLM; Abhedi's pure-code oracle set is a structural claim none can make. Foreground it + publish an FP number | — |
| **B5** | **Compliance-mapped audit trail + CI-regression persistence** | CISO/procurement non-repudiation + Escape's "proved once = re-runs every release" compounding-proof product | A3, retest |

---

## 6. Chain state machine + intelligence-layer design (WS-4 / WS-5 condensed)

**Chain (WS-4, full: [WS4-REPORT.md](../ws4_chain_statemachine/WS4-REPORT.md)).** Harvest-not-rebuild: the carry channel (`_write_finding(extra)`→`evidence_paths`) and replay contract (`retest.py refireable`) already exist and are wired; the floor just passes `extra=None`.
- **CapabilityToken** = `{capability (existing enum), source_finding_id, proof_type (NEW enum), proof_ref{method,request,response_excerpt(redacted)}, location}`.
- **Proof-type enum** (labels existing detection paths): `DETERMINISTIC_ORACLE | OOB_CALLBACK | BROWSER_EXECUTION | RESPONSE_DIFF | CROSS_IDENTITY_DIFF | GRAPH_INFERRED`. `GRAPH_INFERRED` is the honesty label separating candidate edges from proven ones.
- **State machine:** `Discovered → Confirmed → TokenGranted → HopSeeded[carry proof_ref] → HopFired → HopProven(_write_finding extra=capsule) → ExecutedChain(parent+hop ids+composed capsule) → Replayable`. Today the `HopProven→ExecutedChain→Replayable` arc terminates at a capsule-less prose string, so `Replayable` is unreachable.
- **Replay contract:** conjunctive — a chain re-verifies only if the parent capsule AND every hop capsule replay `still_vulnerable`; any `fixed`/`inconclusive` hop downgrades to `partial`.
- **Report narrative schema:** `ExecutedChainReport{chain_id, severity, steps[{order, capability_label, finding_id, proof_type, what_we_found, how_we_proved_it, replay, negative_control}], enabled_next[], reproduce_verdict}` — one schema renders both proven and (GRAPH_INFERRED) candidate tiers.
- **mako correction:** WS-4's T4 ("floor structurally unreachable — override enables executed-chain but not chain-floor") is **REFUTED by the live env** — `CHAIN_FLOOR=1` and `EXECUTED_CHAIN=true` are both ON `[V10]`. So the writer *runs*; its output is *gated out* for lack of a capsule (A3). That makes A3 higher-priority than WS-4 framed it.

**Intelligence (WS-5, full: [WS5-REPORT.md](../ws5_intelligence_layer/WS5-REPORT.md)).** The planner already exists and is running; WS-5 is a wire-and-feed.
- **Per-tick contract:** INPUT = ledger board census + progress-delta digest + policy; OUTPUT = a *validated plan delta* (≤10 active objectives, bounded 8 turns/180s), each objective `{id, kind∈{exploit,recon,verify}, classes[], endpoint_glob, priority, rationale≤200, backing.open_cells (gate-owned)}`.
- **Deterministic plan-gate (keystone, already built `plan_gate.py:214`):** an objective materializes `active` **only if** it maps to ≥1 real open+applicable+in-scope ledger cell — else `rejected:{no_valid_class|out_of_scope|no_surface}` fed back to the next boss prompt. LLM proposes, ledger disposes.
- **Playbook→directive:** flow `policy.md` into the boss prompt POLICY section (already an accepted param) so aggression/phases/restrictions become objective-priority weights; hard limits stay code-enforced.
- **Failure semantics:** planner down/invalid → prior plan stands; flag off → `_plan={}` → byte-identical.
- **mako correction:** WS-5's "ships dark (`scanner_engine_boss` default False, unpinned)" is true for the *code default* but **the boss is ON in the live deploy** `[V10]`. So the value is realized *now* the moment A4 lands — it isn't waiting on a flag flip.

---

## 7. Surface / browser depth design (WS-6 condensed)

Full: [WS6-REPORT.md](../ws6_surface_browser/WS6-REPORT.md). H4 CONFIRMED, H5 REFUTED.
- **Browser worker API contract:** typed verbs `navigate | act | snapshot | har | screenshot | assert(before,after,rule)` via one new `POST /flow` sibling consuming `/work/flow.json`; **auth-state persistence** reuses the existing capture-once (`/work/auth.json`) + two in-scope-only replay channels (header replay + storage-plant) — no new credential path.
- **SPA scenario (state diagram):** `ANON →[AUTH_SESSION]→ AUTHED →[SPA_NAVIGATE]→ RESOURCE_VIEW →[CLIENT_ACTION]→ STATE_MUTATED →[assert]→ CONFIRMED`, with a mandatory `NEGATIVE_CONTROL` leg (same act, no session → must be denied). `CONFIRMED` requires both a client-observable delta AND a server-side XHR effect.
- **New client-side oracles (INPUT+VERDICT, no payload):** `client_guard_bypass`, `authed_dom_acbreak` (two-identity DOM render), `clientside_workflow_skip`, plus `domxss_render_artifact` (attach screenshot/DOM/storage snapshot to existing DOM-XSS hits). Each is one `_INSTRUMENT_KIND_MAP` entry + the pure `assert` comparator.
- **Skill-only classes are actually pure oracles** already (GraphQL authz differential; WS/SSE `channel_auth_open`/`cross_user_leak`/`webhook_sig_bypassed`; JWT forge/PKCE-missing/fixation/no-rotation/revoked-replay) — and ON in deploy. Design contribution = let `/flow` supply the browser-rendered second-identity artifact the offline HAR slice can't.
- **mako correction:** WS-6 D4 ("turn the built-but-dark oracle suite ON") is **moot on this deploy** — graphql/channel/auth/two-identity/ai-redteam are all `true` `[V12]`. The residual WS-6 work is D1/D2 (browser act-then-assert) only.

---

## 8. Do-not-build list (with reasons)

**From directive D6 (re-confirmed, no new evidence to reopen):** recursive agent hierarchies; generation-counter/freeze; agent-to-agent chat as coordination; pgvector semantic memory (`context_memory.py` MemoryStore is dead code — zero callers); ZAP as a core detector; intercepting proxy as the coordination substrate.

**Added by this audit (evidence-backed):**
- **Do NOT "turn on the advanced oracles" as a roadmap item** — they are already ON in the live deploy `[V12]`. Effort spent flipping flags is wasted; spend it on A1–A5 which are real even with flags on.
- **Do NOT build org-scale EASM / AD-lateral-movement before proof-packaging** — large scope expansion; competitors sell it but it doesn't move the buyer-*proof* needle, and Abhedi's proven-chain output is currently gated out (fix A3 first).
- **Do NOT add an LLM to the chain/proof path** — the pure-Python oracle confirm is the competitive moat; keep the model out of `verified=True`.
- **Do NOT tune caps in the repo `override.yml`/`.env`** expecting it to change production — the deployed config is a *different* server file `[C2]`; fix the drift (A7) first or changes are inert.

---

## 9. Implementation roadmap (phased, flag-gated, validation-first)

**Phase V0 — Honesty & drift (1 change, no behavior):** A7 collapse config drift + boot-log effective caps. Unblocks trustworthy validation of everything below. *Exit: repo config == running config, logged.*

**Phase V1 — Throughput (make coverage honest):** A1 two-clocks/thrash + A2 floor-release. Validate on the live target class: `count_claimable` drains, `testing`-limbo ratio drops, right-tail shrinks. *Exit: a scan ends on quiescence, not the 24h wall; limbo <10%.*

**Phase V2 — Proof depth (make findings provable):** A3 chain proof-capsule + A5 finding→cell binding, then B1 executed-chain case-file. Validate: the "proven end-to-end chain" bucket is non-empty and each hop replays. *Exit: ≥1 replayable multi-hop chain on a benchmark target.*

**Phase V3 — Let the planner drive:** A4 feed the boss its inputs (already ON). Validate: gated plan deltas reprioritize claim order against the live board; playbook obeyed. *Exit: measurable coverage-order change under a playbook.*

**Phase V4 — Widen surface (browser):** B2 `/flow` act-then-assert + new client-side oracles. *Exit: ≥1 SPA state-change finding with negative control.*

**Phase V5 — Buyer packaging:** B3 benchmark disclosure + B4 name-the-moat + B5 compliance/CI-regression. *Exit: a published, FP-inclusive, hint-free benchmark + a compliance-mapped deliverable.*

Every phase ships behind a flag defaulting to today's effective behavior; A6 (reprompt-grind) runs in parallel as a cost lever.

---

## 10. Consolidated evidence ledger

Per-workstream ledgers are embedded in each report; raw finder returns in [`evidence/`](../evidence/). Highest-confidence, load-bearing rows (all re-verified by me — [`evidence/VERIFICATION.md`](../evidence/VERIFICATION.md)):

| # | Claim | Source | Confidence |
|---|---|---|---|
| 1 | Dispatch dominates wall-time; reprompt re-feeds full transcript, grinds ~240 calls | [CODE] agents_runtime.py:212-214,166,326 | HIGH |
| 2 | `_batch_done` counts a `tool_calls` increment as progress | [CODE] father.py:1332 | HIGH |
| 3 | exploit_floor never releases claimed cells | [QUERY] grep -c release_cells → 0 | HIGH |
| 4 | finalize retire_unreached sweeps untested→attempted (default ON) | [CODE] finalize.py:454-465; config.py:451 | HIGH |
| 5 | Two clocks: 97% of live `testing` cells in never-cut expired-lease limbo | [QUERY] live DB 1654/1703 | HIGH |
| 6 | Chain floor carries (url,param) only; `_write_executed_chain` writes no capsule/parent | [CODE] chain/floor.py:204 | HIGH |
| 7 | Carry+replay channel already exists unused | [CODE] exploit_floor.py `_write_finding(extra)`→evidence_paths; retest.py:64 | HIGH |
| 8 | Deterministic plan-gate exists (rejects no_surface/out_of_scope/no_valid_class) | [CODE] plan_gate.py:214-230 | HIGH |
| 9 | No `/flow`; `/instrument` reloads each URL fresh (H4) | [CODE] browser_server.py:1032; only /crawl,/instrument,/healthz | HIGH |
| 10 | GraphQL/WS/JWT oracles are pure code (H5 refuted) | [CODE] graphql_authz.py:201-338; channels.py:200-218 | HIGH |
| 11 | **LIVE deploy has boss/chain-floor/executed-chain/require-capsule/evidence-gate/all-oracles ON** | [QUERY] scanner-cp+agent env (V10/V12/V13) | HIGH |
| 12 | **Deployed config = server `/home/admin/autocan/docker-compose.override.yml`, ≠ repo; WORKER_WALL_S has 4 values** | [QUERY] V14-V16 | HIGH |
| 13 | Ledger histogram: attempted 8771 / untested 5299 / testing 2772 / confirmed 298 | [QUERY] live DB | HIGH |
| 14 | OOB honest-classifier working (17 cmdi→ssrf downgrades live); mass-FP bug dead | [QUERY] WS2; [CODE] service.classify_oob:77-97 | HIGH |
| 15 | Abhedi validation moat = pure-Python oracle confirm (no LLM); competitors all route confirm through an LLM/agent | [CODE] exploit_floor.py; [COMPETITOR] COMPARISON.md, escape/xbow/firecompass dossiers | HIGH / MEDIUM |
| 16 | Market's #1 unmet need = independent/third-party proof; XBEN reportedly saturated | [WEB] emergentmind, dev.to; [COMPETITOR] COMPARISON.md | MEDIUM |

**Operator questions (only where a decision is yours, not code's):**
- **[OPERATOR QUESTION]:** Should the *server* `docker-compose.override.yml` (the real deployed config) be committed to the repo as the authoritative deploy manifest, or is the repo intentionally kept at safe defaults with deploy config managed out-of-band? (Determines whether A7 is a "commit it" or a "document + boot-log" fix.)
- **[OPERATOR QUESTION]:** WebFetch/WebSearch allowlist expansion (HackerOne+Bugcrowd) — carried over from the BRD open questions; not resolvable from code.

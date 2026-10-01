# ABHEDI RED — ARCHITECTURE AUDIT & DESIGN (FINAL)
**Agent:** research-agent-nova-02 · **Mode:** READ-ONLY research · **Branch:** feat/alpha-observability (HEAD f75608f; `git diff 1c5551d..HEAD -- src docker` = empty → docs-only delta, 1c5551d equivalence holds)
**Sources:** A codebase OK · B competitor-research/ OK · C `ssh abhedi` OK (43 scans, tenant_xbow 19 tables) · D web OK. No source was missing; no claim is unverifiable-for-lack-of-access except where marked.

---

## 1. Executive summary (10 lines)

1. Scans are not slow because "coverage takes time" — they are slow because work that was claimed is never released (7,364 `floor-*` + 922 `wave*` cells sit with stale `claimed_by`, 0 live leases, 2,502 still open) and because every wave barriers on `max(fleet, floor)`.
2. Coverage is not deep because closure is dishonest: **8,771 applicable cells (39.8%) end terminal-unresolved as `attempted`**, median per-scan resolved ratio **0.000**, 11/18 completed scans resolved nothing.
3. The dominant runtime failure is transport, not reasoning: **59.5% of worker_runs error** (471 "no choices", 73× 429) — and the repo's own empty-response raise site bypasses all client retries.
4. Proofs are shallow for a structural reason: 183/201 "verified" findings have **zero** `evidence_object` rows; `verified=True` is stamped by paths that never require an evidence object.
5. Chaining exists but is double-gated OFF (`SCANNER_ENGINE_CHAIN_FLOOR=0`, `scanner_executed_chain_findings=False`) → `executed_chains=0`; no typed proof artifact ever enters hop N+1's prompt.
6. H2/H4/H5 (operator beliefs) are largely **wrong in the easy direction**: prompts are already state-aware, browser SPA depth already exists behind default-OFF flags, and GraphQL/WS/AI oracles already exist — the defects are *wiring and flags*, not missing machinery.
7. The intelligence layer's real gap is not "no planner" but: objectives without cell refs, an orphaned staleness event stream (99.1% of control-plane log lines, zero consumers), and outcome feedback that never reaches ordering.
8. Worker-world under-specification is proven: no typed `/work` contract, `AGENTS.md` not in the image, two prompts contradict each other on the same file, brief delivered twice, 17.5k-char system block named "context-bloat" in code.
9. Competitors prove chaining + browser-executed validation are table stakes; the open market gaps — OOB proof for blind classes, browser-execution as a stated report contract, WebSocket surface, third-party-audited FP claims — map directly onto mechanisms this repo already has half-built.
10. Everything below is flag-gated, default-OFF, byte-identical when off (D4), ranked by blast radius, with no exploit steps anywhere (R1).

---

## 2. Hypothesis verdicts (H1–H6)

### H1 — SLOW SCANS: claim/release mismatch + wave sync, not "coverage takes time"
**VERDICT: PARTIAL** (mechanisms confirmed & quantified; two sub-claims refuted; primary-cause ranking incomplete without per-phase timing telemetry).

| Sub-claim | Disposition | Evidence |
|---|---|---|
| Claim/release mismatch causes stranded cells | **CONFIRMED, quantified** | Floor claims `floor-{family}` and **never releases** (grep `release` over exploit_floor.py → 0 hits; claim at `exploit_floor.py:4890`) [CODE]; legacy wave path has no release, batch release skips when `_batch_cells` has no entry (`father.py:1345-1362,1358-1360`); by-worker release on `wave{N}`-claimed cells "matches 0 rows" — stated in-code (`father.py:1350-1352`). [QUERY] my own: `claimed_by` set = floor 7,364 / wave 922, live leases 0, open+claimed 2,502. Lease = wall+600 = 6000s (`service.py:1232-1234`). |
| Quiescence reads fail OPEN, ending loops early | **REFUTED** | `_has_claimable` returns **True** on error ("assume still-claimable / keep working"), `_is_complete` returns False on exception; break only on governor "partial" (`father.py:1428-1441,1851-1852`) [CODE]. Failure direction is the opposite of H1's framing: loops run *longer* on DB errors, never shorter. |
| 90-min per-worker wall dominates the schedule | **REFUTED** | Wall is a per-worker hang-guard, explicitly "NOT a scan-level stopper" (`fleet.py:12-28`); timeout → `status="partial"`, scan continues (`fleet.py:60-66`). Observed durations: median 664 s (n=42) — well under 5400 s [QUERY]. |
| Cells reach terminal `attempted` unresolved | **CONFIRMED** | 8,771 = 39.8% of applicable, 62.4% of terminal applicable [QUERY `06_q2b_terminal.sql`, independently re-run by me]; finalize retires them (`finalize.py:450-467`, `reporting/service.py:123`) [CODE]. |
| Sync overhead is real | **CONFIRMED (structure), magnitude [INFER]** | Full `findings.jsonl` re-read + per-line SELECT/INSERT + full `_final_dedup` every 120 s tick and wave boundary (`father.py:905-911,958-965`, `config.py:384`) [CODE]; O(F) cost per pass, no incremental watermark. |
| "Primarily" (ranking) | **UNVERIFIED** | No per-phase wall-clock telemetry exists: `decisions.log` has **no timestamps** (2 sampled files, 10/8 lines) [QUERY]; `worker_runs` shows 59.5% error (578/972) which competes with release-mismatch as a slowdown driver. Attribution table in WS-1a is code-derived, not measured. |

**Blast radius:** lease-stranding directly caps parallelism for up to 100 min per unreleased batch [INFER]; `attempted` retirement converts 39.8% of the grid into silent non-answers; the fail-closed quiescence keeps scans alive to `max_waves`.

### H2 — RIGID PROMPTING: near-identical static prompts
**VERDICT: PARTIAL** (whole-prompt reading REFUTED; static-system reading CONFIRMED narrow; decision-layer value scoped).

- Task surface is re-composed **per wave/group/cell**: brief + board + worklist + plan digest + capability block (`father.py:597-633,1781,1874`), stateful reprompt with missing-work list (`agents_runtime.py:962-1021`) [CODE] → "near-identical" is false.
- Static residue: system methodology (17,504 chars, `methodology.py:13`) + skill bodies constant; granularity is per **phase-group**, no per-vuln-class template layer (`father.py:48-85,31`) [CODE].
- State-aware selection already exists and is deterministic: ranked `SKIP LOCKED` claim with class priority + plan bias (`service.py:1332-1378`), governor/plateau (`governor.py:32-48`) [CODE].
- LLM re-plan exists (`boss.py` + `plan_gate.py`, pure gate, never raises) but code-default OFF (`config.py:417`) while the checked-in dev overlay flips it ON (`docker-compose.override.yml:70-71`) — **deploy ambiguity**; its effect is unmeasured (no `plan.revised` telemetry found).
- Critical scoping: peer failure evidence (471 empty-choices, 73× 429, 10/17 scans ≤ turn 2) is **upstream transport failure** — no decision layer fixes it [QUERY + INFER].
**Blast radius:** medium. The win-set is narrow but real: per-scan resolved ratio, 63× endpoint thrash, unconsumed staleness stream.

### H3 — THEORETICAL CHAINS: graph-only, no proof carry
**VERDICT: PARTIAL** (graph-only refuted; no-typed-proof-ref confirmed; informal carry exists).

- Refuted: `chain/floor.py::run_chain_floor` **executes** hops with deterministic verdicts (`floor.py:407-454`), mints OOB tokens (`floor.py:350-362`), writes findings — but double-gated OFF (`father.py:487-491` default `0`; `config.py:249-254` `False`), which is exactly why `executed_chains=0` (report counts only `verification_method='executed_chain'`+verified, `reporting/service.py:298-318`) [CODE].
- Confirmed: **no typed proof reference** enters hop N+1's prompt — escalation carries label+title+endpoint only (`father.py:1530-1536`); `ChainStep` has no proof field (`chain/service.py:38-43`); zero `evidence_ids` consumers in `chain/*` [CODE].
- Partial carry: node attrs snapshot `proof_of_concept`+`evidence_path` but consumed **report-side only** (`service.py:167-174` vs `reporting/service.py:98-99`); file-mediated floor input; OOB token→callback pipeline — workspace conventions, not a contract.
- `chain_node` cannot be the token store: graph is DELETEd+rebuilt each round (`escalation.py:47-49`, `finalize.py:340-341`) [CODE].
**Blast radius:** high — this is the difference between "we found X" and "X enabled Z" in the report.

### H4 — BROWSER DEPTH: stops at DOM-XSS, no multi-step SPA
**VERDICT: PARTIAL** (DOM-XSS-only refuted; agent-facing multi-step control confirmed absent; depth exists but dark).

- Refuted: sidecar does crawl + **in-crawl multi-step form login** + real-execution canary/PP/storage oracles + stored-XSS canary re-check (`browser_server.py` oracles; `browser_server.py:812-819,877-889,686-689` authed session plant/re-auth/SSO) [CODE].
- Confirmed: agent-facing API is only `/healthz`, `/crawl`, `/instrument` (`browser_server.py:732,737,1032`); `browse` tool = crawl-only (`tools/browser.py:52`) — no navigate/act/snapshot/HAR contract for the worker.
- The dark part: SPA depth ships behind default-OFF flags (`config.py:338-340`: `scanner_browser_authed_crawl=False`, `scanner_browser_reauth=False`, `scanner_sso_login=False`), env-wired at `worker.py:689-691`; instrumentation bounded (max 25 URLs, once/scan, `browser_fallback.py:158-190`).
- Consistent with coverage: `clientside 506 applicable / 0 exercised` in a completed scan [QUERY, peer].
**Blast radius:** high for buyer proof — clientside is the family where only browser execution counts.

### H5 — MISSING SURFACES: taxonomy declares GraphQL/WS/AI but no oracles
**VERDICT: REFUTED as blanket; PARTIAL per surface** — the oracles mostly exist; the *wiring* is broken.

| Surface | Status | Evidence |
|---|---|---|
| GraphQL authz | **ORACLE EXISTS, default-OFF** | `graphql_authz.py:85,201,242,333,338`; flag off at `config.py:243` [CODE] |
| WebSocket/SSE/webhook | **ORACLE EXISTS, default-OFF** | `channels.py:200,206,211,218`; flags at `config.py:293,302` [CODE] |
| AI/LLM canary | **ORACLE EXISTS, default-OFF** | `ai_redteam.py:64,95`; `config.py:312` [CODE] |
| Taxonomy wiring | **DEFECT** | `_GROUPS` omits websocket/webhook/graphql/AI → they fall through to config/nuclei mapping (`oracle_map.py:21-52`), inherited by `father.py:31`, `coverage_qa.py:25` [CODE] — cells cannot route to their oracle |
| Race/TOCTOU | **SKILL-ONLY (genuine gap)** | `exploit_floor.py:860-862` "not deterministically provable" [CODE]; competitors also lack it [COMPETITOR WS-3] |
| MCP | **NO CLASS (genuine gap)** | detection-only at `inventory_ingest.py:630` [CODE]; no ledger cell class exists |
**Blast radius:** medium-high — enabling flags without fixing `_GROUPS` yields oracles that still can't close their cells.

### H6 — WORKER ENVIRONMENT: under-specified → bloat + duplicated work
**VERDICT: PARTIAL-CONFIRMED** ((a) PARTIAL, (b) CONFIRMED, (c) PARTIAL).

- (a) No typed `/work` contract anywhere (grep `WORK_ARTIFACTS|WorkLayout` → none); `AGENTS.md` **not in the image** (`docker/agent/Dockerfile:20-60`); two prompts contradict on the same file (`methodology.py:62-64` forbids raw JSONL writes vs `planner/specialist.py:40-42` orders them) [CODE]. Bounded side: brief/worklist caps (`scan_brief.py:30-43`, `father.py:173`).
- (b) CONFIRMED: 17,504-char system block + ≈9,300-char inlined skills + brief (719–13,198 chars) **delivered twice** (inline + `read_file` order, `methodology.py:17-21`); reprompts re-send full transcript; code itself calls it "the context-bloat guard CLAUDE.md warns about" (`agents_runtime.py:206,214`) [CODE/MEASURE].
- (c) Cell claims are atomic (`SKIP LOCKED`+lease+cap, `service.py:1349-1441`) → strong-form refuted. Duplication survives via: coverage writes **anonymous** (no `cell_id`/`worker_id`, `agents_runtime.py:687-702`); resolve guard omits `attempted`/`na` → terminal cells reopen as `testing` (`service.py:970-971,1004,1399`); no cross-worker probe dedup (`agents_runtime.py:255-263,496`); `prior_methods` handoff **advisory text only** (`service.py:1429-1441`→`father.py:360-371`). Corroborated: 61–84% endpoint rewrite rate [QUERY, peer].
**Blast radius:** high — bloat and re-work tax every single worker dispatch.

---

## 3. Root-cause diagnosis

**Why scans are slow:**
1. **Stranded claims** — the release contract has three holes: floor never releases (`exploit_floor.py:4890`, no release call in 4,835 lines); legacy wave path never releases; batch release silently skips missing `_batch_cells` entries (`father.py:1358-1360`). Each hole costs up to a 6,000 s lease on cells that idle capacity could otherwise steal. Observed: 8,286 stale `claimed_by` rows, 2,502 of them still open [QUERY, mine].
2. **Wave barrier** — every wave awaits the floor task in `finally` (`father.py:1240-1243,1407-1416`) ⇒ wave latency = `max(fleet, floor)`, floor budget 1,500 s, sweeps serial per cell (`exploit_floor.py:4976` budget checked only between families).
3. **Transport failures dominate wall-clock work** — 59.5% worker_runs error; the empty-choices raise happens *after* HTTP 200 in the SDK (`openai_chatcompletions.py:261`), bypassing client retries → fatal `WorkerResult(error)` [WS-2 F21]; 969× 429 in one scan with 0 findings.
4. **O(F) sync** — full-file re-ingest + `_final_dedup` every 120 s and every wave boundary; grows with findings, amplifies unmatched-key warnings ~3.1×.
5. **Control-plane log flood** — 99.1% of scanner-cp lines are `scan.method_switch` per stale testing cell every 180 s, published to zero consumers (`poller.py:1126-1131`).
6. **Not causes:** the 90-min wall (per-worker guard, median scan 664 s) and quiescence fail-open (it fails *closed*).

**Why proofs are shallow:**
1. **Terminal-but-unresolved is a designed state** — attempt-cap exhaustion retires cells to `attempted` during run (`finalize.py:450-467`) ⇒ 39.8% of the grid closes as a non-answer; cancelled scans skip finalize entirely (1,298–1,610 open cells persist) [QUERY].
2. **`verified` ≠ evidenced** — `verified=True` stamped by finalize re-verify/OOB autofind/ingest without requiring `evidence_object` (`finalize.py:919`, `oob/service.py:355,489`); result: 183/201 verified findings have no evidence row; 288/325 evidence rows orphaned [QUERY].
3. **Deterministic machinery is flag-gated off** — chain floor, executed-chain writer, GraphQL/WS/AI oracles, browser auth depth: all default-OFF (`config.py:243,249-254,293,302,312,338-340`; `father.py:491`).
4. **Taxonomy→oracle routing broken** — `_GROUPS` omits new surfaces so their cells fall to the wrong oracle map (`oracle_map.py:21-52`).
5. **No proof carry across hops** — capability context carries titles, not `proof_ref`/hash (`father.py:1530-1536`), so even executed chains can't show per-hop evidence in the report.
6. **Honesty backstop mostly silent** — independent verification fails open 96.3% (1,016/1,055), 949 from its own `max_turns=12` [WS-2 F20].

---

## 4. Core-architecture improvements (ranked by blast radius, module-level, flag-gated)

| # | Improvement | Module/flag (default) | Buyer-visible outcome |
|---|---|---|---|
| A1 | **Release-all discipline**: floor releases its family claims in `finally` (by ids); legacy wave path mirrors the by-ids release; batch release falls back to by-`worker_id` when `_batch_cells` misses | `exploit_floor.py` (add release after `claim_family_cells` at :4890), `father.py:1345-1362`; flag `SCANNER_ENGINE_RELEASE_STRICT=1` (default `0` for D4; when 0, current behavior byte-identical) | Median scan time drops as idle workers re-claim instead of waiting out 6,000 s leases; more cells attempted per hour |
| A2 | **Terminal-state guard closure**: extend idempotency guard to ALL terminal states (`attempted`,`na`) + add `applicable` check in the update loop | `ledger/service.py:970-971,930-1028`; flag none needed if proven by replay-test (guard change is bugfix-class; gate via `SCANNER_LEDGER_STRICT_TERMINAL=0` default off) | 39.8% `attempted` population stops churning back to `testing`; coverage numbers become stable and honest |
| A3 | **Evidence-required verification**: `verified=True` only persists with ≥1 linked `evidence_object`; add finalize integrity check | `finalize.py:919`, `oob/service.py:355,489`, new gate near `ingest_findings.py` write path; flag `SCANNER_EVIDENCE_REQUIRED_VERIFY=0` | Every "verified" finding in the report carries a citable artifact — the audit-proof claim competitors sell |
| A4 | **Empty-response retry fix**: treat SDK empty-choices-after-200 as retryable transport error, not fatal worker error | runtime wrapper in `engine/runtimes/` (raise site: Agents SDK `openai_chatcompletions.py:261`); flag `SCANNER_RETRY_EMPTY_RESPONSE=1` (default off until measured) | 471/578 worker errors eliminated class-wide → fewer wasted waves, more findings per scan |
| A5 | **Incremental sync**: watermark offset into `findings.jsonl`, dedup moved off tick | `father.py:888-967`, `ingest_findings.py:377+`; flag `SCANNER_ENGINE_SYNC_INCREMENTAL=0` | Late-scan tail latency drops; DB load linear not quadratic |
| A6 | **`_GROUPS` oracle routing fix** + flag-aware coverage_quality | `oracle_map.py:21-52`, `father.py:31`, `coverage_qa.py:25`; flag inherits per-surface oracle flags | GraphQL/WS/AI cells route to their deterministic oracles instead of nuclei/config fallback |
| A7 | **Staleness consumer + flood cap**: aggregate `scan.method_switch` into ≤1 digest/tick for the future planner; cap per-cycle publications | `poller.py:1126-1171`; flag `SCANNER_ENGINE_INTEL` (WS-5 master, default `False`) | Control-plane logs usable again (99.1% flood → flat); stale cells get deprioritized instead of re-emitted |
| A8 | **Anonymous coverage writes → identified**: `record_coverage` carries `cell_id`+`worker_id` from the claim | `agents_runtime.py:687-702` (consume the `cell_id` claim already returns at `service.py:1415`); flag `SCANNER_COVERAGE_ATTRIBUTED=0` | Cross-worker thrash becomes attributable; 63× endpoint rewrites drop; reconciliation stops guessing by string match |
| A9 | **Typed `/work` contract shipped in image** + fix contradictory prompt | new `src/scanner/agent_runtime/work_contract.py`; `docker/agent/Dockerfile` COPY; align `planner/specialist.py:40-42` to `methodology.py:62-64`; flag: contract is read-only metadata (no behavior change) | Workers stop truncating/losing each other's results; onboarding/debugging time drops |
| A10 | **Prompt bloat reduction**: deliver brief once (inline XOR read), progressive-disclosure skills on fleet path, token-budget reset parity with single-agent path | `father.py:597-613`, `methodology.py:17-21`, `father.py:274-293`, `agents_runtime.py:212-235`; flag `SCANNER_PROMPT_TRIM=0` | Lower token cost per dispatch (operationally already motivating batch-size knobs, `override.yml:30`), faster worker spin-up |

---

## 5. Feature add-ons (ranked by buyer-proof value)

| # | Add-on | Module/flag (default) | Buyer outcome | Anchored in |
|---|---|---|---|---|
| B1 | **Chain state machine + capability tokens** (WS-4 full design) | `chain_token` table (migration 0020), `chain/floor.py` mint, `father.py` `capabilities:` contract block, `reporting/service.py` `executed_chain_stories[]`; master `SCANNER_CHAIN_STATE_MACHINE=0` | Report tells "found X → proved Y → enabled Z" with per-hop `proof_ref/proof_hash/replay` — nothing competitors publish as a standard | WS-4 §1–3; market gap: no standard evidence schema [COMPETITOR] |
| B2 | **Browser-executed proof as report contract** (WS-6 §1–3): `/session`+`/step` API, auth-state persistence, EXEC_CANARY/CONTENT_REPLAY proof types feeding `evidence_object` | `docker/browser/browser_server.py` step endpoints, `tools/browser.py`, `config.py` existing auth flags stay; new `SCROWSER_BROWSER_STEP_API=0` | Every client-side class shows a screenshot/HAR/console artifact — matches XBOW's published browser-execution gate and standardizes it across classes | H4; WS-3: XBOW publishes it, others don't |
| B3 | **Enable + wire existing new-tech oracles** (flip flags after A6): GraphQL authz, WS/SSE/webhook, AI canary | `config.py:243,293,302,312` → set per-scan; `oracle_map` groups (A6) | Closes GraphQL (Escape-owned today) and AI/MCP-adjacent cells with deterministic verdicts; WS-3 says WebSocket is an **unclaimed** product surface | H5; WS-3 gaps |
| B4 | **Honest-coverage gate**: unfired family ⇒ surfaced `coverage_quality.json` status + no silent `completed` | `coverage_qa.py:123-136`, report status logic; flag `SCANNER_HONEST_COVERAGE=0` | Buyer sees "access family: 0 exercised" instead of a false `open 0` — trust differentiator vs self-reported competitor FP rates | WS-2 F11; WS-3 gap: independent verification |
| B5 | **Intelligence layer** (WS-5 full design): bounded per-tick planner, cell-ref plan gate, playbook→directive AST | new `engine/intel.py`, `intel_gate.py`, `directives.py`; extend `plan_gate.py`; master `scanner_engine_intel=False` | Operator playbooks visibly steer scans; objectives provably map to real open cells; A/B harness yields the falsifiable H2 answer | WS-5 ranked plan |
| B6 | **OOB proof for blind classes as marketing surface** — mechanism already exists (`oob/service.py` callback→confirmed) | wire token→cell linkage (only 6% of fired tokens carry `cell_id` [WS-2 F28]): `oob/service.py` mint path, flag `SCANNER_OOB_CELL_LINK=0` | WS-3 found **no competitor** claims OOB/DNS proof for blind web classes — this is the sharpest owned differentiator | WS-3 §3 gap 3 |
| B7 | **Replay/audit contract**: `content_recheck` via detached verifier seam | `detached_verify.py:7-126` reuse; `SCANNER_CHAIN_TOKEN_REPLAY=0` | Auditors re-verify proofs without re-running attacks; pairs with FireCompass's audit-log play but is content-addressed (sha256) | WS-4 §2.3; WS-3 proof standards |

---

## 6. Chain state machine + intelligence layer (WS-4/WS-5 output)

**Chain machine (full spec in `ws4/WS-4-chain-state-machine.md`):**
- States: `PRIMITIVE_CONFIRMED → TOKEN_GRANTED → HOP_MATERIALIZED → HOP_EXECUTING → HOP_VERIFIED → CHAIN_COMPLETE | CHAIN_BROKEN`, guards G1–G9 (G1: static `GRANTS[]` + minting proof-type; G4: oracle fired; G9: replay drift ⇒ break).
- Token store: **new `chain_token` table** (NOT `chain_node` — graph is deleted/rebuilt each round), append-only, `parent_token_id` lineage.
- Hop N+1 receives `capabilities: [{type, proof_ref, proof_type, proof_hash, granted_by_cell, token_id, hop_index, state}]` injected at the existing `capability_ctx` seam (`father.py:604-614`); contract rule: hop N's proof is **context, never hop N+1's evidence**.
- ProofType: `ORACLE_FIRED | OOB_CALLBACK | BROWSER_EXECUTED` mint; `ARTIFACT_READ` satisfies ledger but does not mint; `CHAIN_COMPOSED` report-only — thesis-aligned.
- Report: `executed_chain_stories[]` with per-hop proof refs; absent when flag off ⇒ byte-identical legacy JSON.
- Failure: no oracle ⇒ no token; timeout ⇒ `CHAIN_BROKEN`, zero partial credit; `REPLAY_DRIFT` breaks downstream, keeps hop history.

**Intelligence layer (full spec in `ws5/WS-5-intelligence-layer.md`):**
- `engine/intel.py` per-tick: INPUT = ledger summary (coverage ≤60 rows, open sample ≤15, progress, staleness digest ≤1 line, budget, plan_state, directives ≤20, policy ≤4000) ≤24 KB; OUTPUT = plan **delta** (≤6 add/6 remove/6 requeue), free-execution keys ⇒ whole candidate invalid.
- Plan gate extension: objectives carry `cell_ids[]`; resolver checks `ledger_cell(cell_id,scan_id,applicable,state IN _OPEN_STATES,attempts<cap)` + `inventory_element` + `in_scope()`; dead ref ⇒ drop+log, **never spawn** (objectives only order the deterministic claim).
- Playbooks → `Directive` AST → same gate (`engine/directives.py`); `spawn_subagent`/`fan_out`/`agent_model`/tool fields explicitly ignored (D6).
- Failure ⇒ prior plan stands: every failure path returns to `father.run()` adjacent to `:1787` with `self._plan` untouched ⇒ today's exact code path (byte-identical, D4).

## 7. Surface/browser depth design (WS-6 output — full in `ws6/WS-6-surface-browser-depth.md`)

- **Browser step API contract** (flag-gated): `/session` (create/persist auth state, per-scan scoped, redacted export), `/step` (navigate|act|snapshot|har|screenshot|wait_for with bounded INPUT/VERDICT enums — selectors/values only), `/session/close`.
- **SPA state diagram**: login → navigate → mutate → re-read → assert persistence → server-side effect check; every transition tagged with its gate flag and proof artifact.
- **Execution oracles beyond DOM-XSS**: `EXEC_CANARY`, `CONTENT_REPLAY`, `DIFF_IDENTITY`, `OOB`, `CHANNEL_DIFF`, `SEQUENCE_DIFF` (+ `BLOCKED_FLAG_OFF` verdict so flag-off scans report honestly instead of silently).
- **Skill-only → oracle conversions** (INPUT/VERDICT only): GraphQL authz = INPUT two-identity probes, VERDICT observing the other's object ⇒ `AUTHZ_BROKEN`; WebSocket = INPUT channel subscribe+message diff across identities/time, VERDICT unauthorized delivery; JWT/OAuth/session = INPUT token/refresh state transitions, VERDICT acceptance of expired/altered token ⇒ session class confirmed.
- **Honest-coverage wiring**: fix `oracle_map` `_GROUPS` (A6), flag-aware `coverage_quality.json`, ledger `na_reason=blocked_flag_off` reuse.

---

## 8. Do-not-build list (with reasons)

1. **Recursive agent hierarchies** (D6) — hierarchy code exists dead (`entrypoint.py:882-925`, `spawn_subagent` loader fields); 59.5% worker error rate means more concurrent agents multiplies the dominant failure mode [QUERY].
2. **Agent-to-agent chat messaging** (D6) — no message channel today by design; would create an unauditable instruction path bypassing `guard_tool_call`; the `scan.method_switch` flood (99.1%, zero consumers) already shows the cost of unconsumed streams [CODE/QUERY].
3. **pgvector semantic memory** (D6) — `context_memory.MemoryStore` has zero importers (dead); structured keyed state (ledger + plan.json + brief) already exists; vector recall injects non-determinism into a fail-closed path.
4. **Generation-counter/freeze** (D6) — lease+attempt-cap+`SKIP LOCKED` already provides liveness; freeze would re-introduce the stall class the lease design removed.
5. **ZAP as core detector** (D6) — one failed scan already died on a missing `scanner/zap` image (`poller.py:594`); ingest path exists (`sync_zap`) but core cells must close on own oracles.
6. **Intercepting proxy as coordination substrate** (D6) — coordination is DB claims + `/work` artifacts; proxy would centralize the least reliable component (see logging-proxy blind spot: NVIDIA-only coverage).
7. **Race-condition "confirmation" without a deterministic oracle** — code itself says "not deterministically provable" (`exploit_floor.py:860-862`); ship as SIGNAL_ONLY capability label, never as verified (thesis).
8. **Extending `planner/*` or `entrypoint.run_scan`** — D3 confirmed dead except engine-v2 fallback (`entrypoint.py:1122-1124`, compose `SCANNER_ORCHESTRATOR=reprompt`); new intelligence attaches to the engine-v2 wave loop only.
9. **Turning on `scanner_engine_boss` via the checked-in overlay as "default"** — override.yml flips it ON for smoke tests (`override.yml:70-71`); enabling without the A/B harness would repeat the unmeasured-deploy pattern H2 warns about.

---

## 9. Implementation roadmap (phased, flag-gated, validation-first per D5)

**Phase 0 — Validation-before-breadth (make coverage honest):** A2 terminal-guard closure → A3 evidence-required verify → A8 identified coverage writes → B4 honest-coverage gate. *Gate to Phase 1:* resolved-ratio and evidence-linkage metrics measurably improve on a lab scan (A/B, flags off=byte-identical baseline).
**Phase 1 — Make findings provable:** A1 release discipline → A4 empty-response retry → A5 incremental sync → A7 staleness digest (pre-requisite for B5). *Gate:* scan wall-clock and worker error rate drop on the same target set.
**Phase 2 — Turn on what exists:** A6 oracle routing → B3 flag flips (GraphQL/WS/AI) → B6 OOB cell linkage → browser auth-depth flags already shipped (`config.py:338-340`). *Gate:* previously-unroutable cells reach terminal states with oracles fired.
**Phase 3 — Chain + proof carry:** B1 `chain_token` (5-stage rollout: migration → mint → contract → report → replay, each flag-revertible) → B7 replay. *Gate:* ≥1 `executed_chain_stories` entry with per-hop proof refs on a lab chain.
**Phase 4 — Planner drive:** B5 intel layer (gate → directives → tick → staleness consumer → A/B harness). *Gate:* H2's falsifiable win-set measured (resolved ratio, thrash, repeat-work), ship or keep off on numbers.
**Phase 5 — Widen surface:** B2 browser step API + SPA scenario → race/MCP skill→oracle conversions (WS-6 §4) → chain-to-impact widening.
**Throughout:** every ticket names module+flag+buyer outcome; none contain exploit steps (R1); byte-identity when flags off verified by report-diff test at each phase gate.

---

## 10. Consolidated evidence ledger (high-confidence core; per-WS ledgers in their files)

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| Floor never releases claims; claim at `exploit_floor.py:4890`, 0 release hits | [CODE] grep + read this session | HIGH | Re-verified personally |
| Batch/legacy release holes at `father.py:1345-1362,1358-1360`; by-worker release on wave cells matches 0 rows (in-code) | [CODE] `father.py:1350-1352` | HIGH | Direct quote |
| 8,286 stale claimed_by (floor 7,364/wave 922), 0 live leases, 2,502 open+claimed | [QUERY] my SQL vs tenant_xbow | HIGH | Run by me, independent |
| Lease = wall+600 = 6000 s; attempt cap 3 | [CODE] `service.py:1232-1247` | HIGH | |
| Quiescence fail-closed, `_is_complete` fail-closed False | [CODE] `father.py:1428-1441` | HIGH | H1 sub-claim refuted |
| Wall is per-worker guard, not scan stopper | [CODE] `fleet.py:12-28,60-66` | HIGH | H1 sub-claim refuted |
| 8,771 attempted = 39.8% applicable; resolved 5,283/22,011 = 24.0%; median per-scan 0.000 | [QUERY] `06/20` + my independent re-run | HIGH | Reproduced by me |
| 43 scans: 19 cancelled/18 completed; durations median 664 s max 64,618 s | [QUERY] `03/04` | HIGH | |
| 183/201 verified findings lack evidence rows; 288/325 evidence rows orphaned | [QUERY] `19_chains.sql` | HIGH | |
| chains 190 nodes/461 edges populated, `executed_chains=0` | [QUERY] my re-run + workdir report.json | HIGH | Live counts drift from peer snapshot |
| Chain floor + executed-chain writer both default-OFF | [CODE] `father.py:487-491`, `config.py:249-254` | HIGH | Re-verified personally |
| No typed proof ref in hop-N+1 prompt; escalation = label+title+endpoint | [CODE] `father.py:1530-1536`; zero `evidence_ids` in `chain/*` | HIGH | H3 confirmed half |
| `chain_node` deleted/rebuilt each round | [CODE] `escalation.py:47-49`, `finalize.py:340-341` | HIGH | Token-store basis |
| Worker prompts state-aware per wave/group/cell; static system methodology only | [CODE] `father.py:597-633`, `methodology.py:13` | HIGH | H2 refuted half |
| Boss/plan_gate code-default OFF, overlay flips ON | [CODE] `config.py:417`, `override.yml:70-71` | HIGH | Deploy ambiguity flagged |
| GraphQL/WS/AI oracles exist, default-OFF; `_GROUPS` omits them | [CODE] `graphql_authz.py:85+`, `channels.py:200+`, `ai_redteam.py:64+`, `oracle_map.py:21-52`, `config.py:243,293,302,312` | HIGH | H5 refuted blanket |
| Browser sidecar: `/healthz`,`/crawl`,`/instrument` only; SPA auth depth behind OFF flags | [CODE] `browser_server.py:732,737,1032`, `config.py:338-340` | HIGH | H4 partial |
| worker_runs 59.5% error; 471 empty-choices, 73× 429 | [QUERY] peer `23_workers.sql` + WS-2 | HIGH | |
| Empty-choices raised after HTTP 200 → retries bypassed | [CODE] Agents SDK `openai_chatcompletions.py:261` (via WS-2) | MEDIUM | Raise site outside repo src |
| 99.1% log flood = `scan.method_switch` per stale cell/180 s, no consumer | [QUERY] docker logs + [CODE] `poller.py:111,1126-1131` | HIGH | |
| 61–84% endpoint rewrite thrash; terminal-state guard omits attempted/na | [QUERY] peer + [CODE] `service.py:970-971,1004` | HIGH/HIGH | Mechanism + magnitude separate |
| `/work` contract absent; AGENTS.md not in image; contradictory prompts | [CODE] grep + `Dockerfile:20-60` + `methodology.py:62-64` vs `specialist.py:40-42` | HIGH | H6(a) |
| 17,504-char system block; brief double-delivered; bloat named in code | [CODE/MEASURE] `methodology.py:13`, `father.py:613`, `agents_runtime.py:206,214` | HIGH | H6(b) |
| Coverage writes anonymous; handoff advisory; no cross-worker probe dedup | [CODE] `agents_runtime.py:687-702,255-263`, `service.py:1429-1441` | HIGH | H6(c) |
| Competitors: chaining table stakes; browser-execution gate only XBOW; no OOB-for-blind, no WebSocket, no race, no HAR-as-evidence claims | [COMPETITOR] `competitor-research/*` + URLs in WS-3 | MEDIUM-HIGH | Public claims only; absences "not found" |
| FP rates self-reported across all three; independent verification = market's top unmet need | [COMPETITOR] `COMPARISON.md` L119 | MEDIUM | Third-party summary |
| D3: planner/* + run_scan dead in default deploy | [CODE] full chain in WS-5 §0.5 | HIGH | Fallback caveat noted |
| Proxy-log blind spot (NVIDIA/nemotron only) respected; no raw prompts reproduced | process constraint | HIGH | R5 honored throughout |

**Residual [UNVERIFIED]:** per-phase wall-clock attribution (no timestamps in `decisions.log`); whether measured scans ran with the dev overlay; exact raise-site provenance of provider errors outside `src/`; intent behind $0 cost metering; why ~470 in-window OOB ids never persisted (WS-2).

---
*Files: `ws1/{WS-1a,WS-1b,H6}`, `ws2/`, `ws3/`, `ws4/`, `ws5/`, `ws6/`, `scripts/00–54` (read-only SQL). No repo files modified; no server writes; no payloads anywhere (R1).*
# WS-7 — SYNTHESIS
**Agent `research-agent-falcon-02`** · repo `autocan` @ `feat/alpha-observability`/`f75608f` (READ-ONLY, unmodified)
Live: `abhedi-cc`, schema `tenant_xbow`, 43 scans / 70,781 ledger cells / 987 worker runs / 24,630 proxy calls / 348 agent messages.
Inputs: `ws1_throughput/REPORT.md`, `ws2_telemetry/REPORT.md`, `ws3_competitor/REPORT.md`, `evidence/H2-H6.md`, `ws4_chain_statemachine/DESIGN.md`, `ws5_intelligence_layer/DESIGN.md`, `ws6_surface_browser/DESIGN.md`, plus lead verification.

---

## 1. EXECUTIVE SUMMARY

1. **H1 is REFUTED, not confirmed.** Wave sync costs **~40–50 ms per boundary against ~3,000 s waves — 0.0015%**. Slowness is ~83% LLM inference idle time at concurrency **0.67 against a pool cap of 4**, plus `max_turns_exceeded` on **63/63** turns.
2. **The real emergency is honesty, not speed.** A scan reported `completed` with **3,406 of 3,598 applicable cells mass-retired untested** (94.6%). Independently re-verified by lead: `dbf83a85`, status `completed`.
3. **The client reports zero coverage because the counter is structurally dead.** `resolved_cells` declared `worker.py:20`, read `telemetry.py:183`, **never assigned anywhere in src/**. `SUM(resolved_count)=0` across 987 runs. `findings_count` over-reports **139×**.
4. **Three of six hypotheses were wrong as written.** H5 was wrong: GraphQL/WS/AI oracles **exist and are flag-ON**. The real bug is 3,561 cells silently vanishing into `na` upstream of the oracle.
5. **H3 was wrong in the operator's favour, right in the detail.** Capability tokens *are* carried; **195/195** nodes carry a PoC. But hop targets are frozen constants (`floor.py:59-101`) and **0 executed chains in 43 scans**.
6. **The thesis survives where it matters.** 0/301 OOB callbacks falsely confirmed; registration floor fired; 36.9% of agent claims honestly downgraded. **But 0/301 evidence rows link to a finding** — the flagship proof has no audit trail.
7. **The LLM is near dead weight.** **348 messages vs 37,047 tool calls (1:106).** 41.4% of tool calls floor-issued. **17 scans did real work with zero model messages.**
8. **The competitor moat is thinner than assumed.** No competitor publicly specifies a capability-token or attack-graph mechanism (corpus grep = 0 hits). Abhedi Red's deterministic-oracle layer is genuinely unique — **and unsold, unbuilt, unevidenced.**
9. **Lead-only finding: config drift.** `POOL_HARD_CAP=8` on CP, `=4` in agent container. The engine believes it has double the pool it does.
10. **No proposed work needs a rewrite.** Every design extends an existing module, flag-gated default-OFF, byte-identical when off.

---

## 2. HYPOTHESIS VERDICTS

| # | Hypothesis | Verdict | Decisive evidence |
|---|---|---|---|
| **H1** | Slow = claim/release mismatch + sync overhead | **REFUTED** | Sync = 40–50 ms/wave = **0.0015%**. Mismatch real (0/971 worker IDs ever owned a cell) but **routed around** by `release_cells_by_ids`. Neither causes the time. |
| **H2** | Static prompts; needs state-aware layer | **PARTIAL** | Prompt **95% static**, 1.5–5.1% worker-unique — **but selection happens in `claim_cells`, upstream of any prompt.** A state-aware layer already exists (`father.py:1520`). Remedy targets the wrong layer. |
| **H3** | Chains graph-only, no proof carry-over | **PARTIAL** | Literal claim **false**: tokens carried (`floor.py:426-441`), **195/195** nodes carry PoC. Narrower gap **confirmed**: `_Ctx` carries **zero** per-finding data; targets frozen; **0 executed chains / 43 scans**. |
| **H4** | Client-side stops at DOM-XSS | **CONFIRMED** | Exactly **3 endpoints**. `/instrument` = one page, one `goto`, fixed 3-source plant. No action/selector/assertion field — navigate→act→re-navigate **structurally inexpressible**. |
| **H5** | New-tech lacks deterministic oracles | **REFUTED** | Oracles **exist**: `graphql_authz.py` (5 proof types), `channels.py` (4), `ai_redteam.py`. All flags **ON** live. Real gap: applicability gate makes **3,561 cells silent `na`**; `oracle_map` routes all 8 classes to `nuclei` so `_oracle_fired` can never match `graphql-authz`. |
| **H6** | Worker env under-specified → bloat + dup work | **PARTIAL** | Contract **tight** (one per-scan mount, no docker.sock, caps hardened). Duplication **worse than stated**: floor never releases → **7,364 stale claims, 100% expired**, 2,062 cells re-claimed. Bloat driver is free-text `methods_used`, not skills catalog. |

**Blast radius of the framing:** H1 mis-diagnoses a **coverage-integrity** problem as a **throughput** problem. Fixing the ledger will not make scans faster; it will make finished scans honest.

---

## 3. ROOT-CAUSE DIAGNOSIS

**Why scans are slow:** concurrency × latency × non-convergence. Mean tool concurrency **0.67** against cap **4** ⇒ ~83% of slot time is inference wait. `POOL_HARD_CAP=4` forces 3 sequential rounds per 11–12-batch wave (~54 min/wave, matching observation). Every batch burns its full turn allowance (`max_turns_exceeded` 63/63; 950/1,019 error lines). 48.5% of runs die on `ChatCompletion response has no choices`. Live-convergence verify overshoots its 120 s cadence by **7–15×** inline on the sync loop against the *same* model endpoint.

**Why proofs are shallow — four independent breaks:**

| Break | Mechanism |
|---|---|
| **Coverage self-declared** | Mass-retire (`finalize.py:455-464`, default **ON**) turns untested → `attempted` ⇒ `count_open_cells`=0 ⇒ `scan_is_complete` **true**. Its own comment claims "coverage % unchanged" — **false**; `resolved_ratio = 1 - open/total` = 1.0. |
| **Chains inferred, never executed** | Hop targets are module constants. `_hop_credential` is an explicit no-op — all five credential-granting classes are **terminal by construction**. |
| **New-tech surfaces unreachable** | `materialize_cells` spawns every class × every element, then applicability kills them → `na` → `claim_cells` never hands them out. |
| **No proof audit trail** | 301 OOB evidence rows, **0** with `finding_id`; `findings.jsonl` has **no `oob_token` key**. |

**The compounding factor:** the decision layer is blind. A planner cannot steer on a counter that is 0 or a findings number inflated 139×.

---

## 4. CORE-ARCHITECTURE IMPROVEMENTS (ranked, flag-gated)

| # | Change | Module / flag | Buyer outcome |
|---|---|---|---|
| 1 | Make mass-retire honest | `finalize.py:455-464`; `SCANNER_LEDGER_NOT_ATTEMPTED_STATE` | A `completed` scan finally means tested |
| 2 | Fix `SCANNER_LEDGER_COMPLETE_RATIO` docstring lie; read at import | `ledger/service.py:1181,1184-1200` | No silent 2% truncation |
| 3 | **Release floor claims** (largest single waste) | `exploit_floor.py:4890` — 0 release calls in 5,285 lines | Kills 7,364 stale claims + up to 6× re-sweep |
| 4 | Repair `resolved_count` + `findings_count` attribution | `SCANNER_TELEMETRY_RESOLVED_COUNT`, `..._FINDINGS_ATTRIB` | Coverage number stops reading 0 |
| 5 | Fix `POOL_HARD_CAP` 8-vs-4 drift | compose/override + `father.py:564` | Engine stops over-estimating its pool |
| 6 | Move live-convergence off the sync critical path; bound it | `father.py:1084-1092`; `SCANNER_ENGINE_LIVE_CONVERGENCE` | Recovers the 7–15× cadence overshoot |
| 7 | Fix progress watchdog defeated by tool churn | `father.py:1328-1336` | Spinning workers terminate |
| 8 | Guard `WORKER_WALL_S=0` (means *kill instantly*, not *unlimited*) | `fleet.py:28`; contradicts `config.py:464` | Fixes the 16/16 instant-kill scan |
| 9 | Make the plan gate fail **closed** on unreadable surface | `SCANNER_PLAN_GATE_V2`; `father.py:1132` → `plan_gate.py:226` retires everything permanently | One transient DB error no longer strips boss bias for the scan |
| 10 | Bound the planner tick, off critical path | `SCANNER_ENGINE_PLANNER_TICK` (45s/4 turns/2 tools) | ≤180s/wave idle → 0s |
| 11 | Proxy correlation headers | `SCANNER_PROXY_CORRELATION` | Telemetry from 11.6% → attributable |

---

## 5. FEATURE ADD-ONS (ranked by buyer-proof value)

1. **Proof→regression (cross-release retest).** Competitors ship proven findings as permanent CI tests; Abhedi Red's ledger dies with the scan. All ingredients exist (`retest.py`, oracle builders). **A store-and-replay layer, not new detection.** Highest differentiator available.
2. **Machine-checkable chain narrative.** Current layer is a **5,965-byte LLM prompt merger** — prose generation, precisely what the thesis forbids as the confirming thing. Schema + validator; LLM becomes annotator, not author.
3. **Finding-level screenshot-at-execution.** Closes the documented TODO at `browser_ingest.py:397`. `EvidenceObject.screenshot` **already exists** — no migration. No competitor demonstrably ships this.
4. **Live-capture browser walk.** Unlocks stored-XSS-across-state-change and function-level authz under low-priv. Columns already exist.
5. **Multi-identity as a product surface.** Oracle exists (`diff_access`), browser login exists, no engagement-level "supply N principals" contract. Escape quantifies it: "a second account typically uncovers 30–50% more issues."
6. **Revive the new-tech oracles.** Two small plumbing fixes unlock ~3,561 dead cells and reverse a live bug where real findings get parked as `pending_oracle`.
7. **Operator playbook → machine directive.** Today a playbook has **zero** ledger effect — only `entrypoint.py:97-119`'s hardcoded 150 invocations. The buyer pays for prose.

---

## 6. CHAIN STATE MACHINE (WS-4)

**Gap:** hop N's evidence never reaches hop N+1. Fix: `CapabilityToken` + `ProofArtifact` + `DerivedTarget` in new `chain/token.py`; `_Ctx` unchanged; dispatcher routes on `target.origin` (`proof_body` / `ref_field` / `invocation_output` / `static_table`). **New tables `chain_token` + `chain_hop`** — `chain_edge`'s unique constraint would overwrite `EDGE_RATIONALE` prose; `chain_node` cannot hold derived multiplicity.

**`PROVEN` is the only state that mints.** `REFUTED` ≠ `INDETERMINATE` (deterministic negative vs undecidable). New `REVOKED` for post-hoc A1 downgrades.

**Example (capability labels only):** `FILE_READ → SECRET_DISCOVERY → CREDENTIAL`. Today `_SECRET_FILES` is a frozen 8-tuple with first-hit return and no control. Design: derive from hop N's observed **root element**; verdict `POSITIVE` iff the marker matches in the primitive's response **and not** in the same path requested without it — making "the file is just public" distinguishable from "the primitive disclosed it."

---

## 7. INTELLIGENCE LAYER (WS-5)

**A state-aware layer already exists and is already ON** (`SCANNER_ENGINE_BOSS=true`, lead-verified live) while docs say OFF. This is **four repairs, not greenfield.** `plan_gate.py` is already correct (16 unit tests, fail-safe, merge-not-replace) — **extend, do not replace.** `_biased_priority`'s advisory-only property is **preserved and extended** to operator directives; it holds *structurally*, because class lists reach SQL only as `array_position` in `ORDER BY` — the `WHERE` is a constant.

**The dangerous find:** `_sample_open` returns `[]` on any exception ⇒ gate reads it as "drained" ⇒ **auto-retires every prior objective, terminally, for the rest of the scan.** Same fail-open shape WS-2 found in the anti-fabrication gate. Fix: three-state `SurfaceRead(ok=…)`; uncertainty never retires anything.

---

## 8. SURFACE & BROWSER DEPTH (WS-6)

**Correcting the inherited brief:** `run_channels_sweep` is **cell-driven**, not schema-driven (`channels.py:451-453` → `claim_cells`). It cannot be unblocked by editing its own body — **fix materialization first.** `_sweep_graphql` *is* schema-driven and needs no cell.

**Three plumbing fixes:** (a) `materialize_cells` — adopt the in-tree AI double-gate at `service.py:671` for graphql/ws/webhook; (b) `oracle_map` — a `CLASS_ORACLE` override consulted *before* the group lookup, leaving `GROUP_FOR_CLASS` byte-identical (only 2 consumers, both skill-gate); (c) new state **`not_attempted`** — **do NOT reuse `blocked`**, because `reporting/service.py:121` counts `blocked` inside `resolved`, so reuse would inflate `resolved_pct`.

**Safety invariant for a generic walker (S9):** refuse to click any control inside a non-GET `<form>` unless the scenario is registered `mutating: true` — generalising the invariant `_try_login` already enforces for itself.

---

## 9. DO-NOT-BUILD

| Item | Reason |
|---|---|
| Recursive agent hierarchies | H2 shows selection is a ledger claim; hierarchy adds latency to a latency-bound system |
| Generation-counter/freeze | 53 `worker_runs` rows already stuck `running`; more lifecycle state compounds the leak |
| Agent-to-agent chat messaging | Escape's bus is the mechanism to *beat*, not copy — the token contract is the deterministic version |
| pgvector semantic memory | 41.4% of tool calls already floor-issued; the LLM is not the bottleneck |
| ZAP as core detector | Live ZAP signal files are **0 KB**; adds a detector without an oracle |
| Intercepting proxy as coordination substrate | Directive-forbidden; proxy coverage is already only 11.6% |
| Raising pool concurrency | 0.67 concurrency means the cap is not binding — raising it will not help |
| "Smarter prompts" | 95% static is already amortised via batch size 6; marginal tokens carry 12 cells |

---

## 10. ROADMAP — phased, flag-gated, validation-first

**Phase 0 · Truth (no new capability, no new traffic).** Fix `resolved_count` + `findings_attrib`; `POOL_HARD_CAP` drift; `WORKER_WALL_S=0` guard; make fail-open gates fail closed. *Validation: `completed` scans show non-zero honest coverage.*
**Phase 1 · Waste.** Release floor claims; bound the watchdog; move live-convergence off the sync loop. *Validation: stale `floor-*` claims → 0; cadence gap ≤2×.*
**Phase 2 · Coverage honesty.** `not_attempted` state; `materialize_cells` gate; `oracle_map` override. *Validation: 3,561 cells either claimable or visibly out-of-scope; GraphQL sweep logs.*
**Phase 3 · Proof.** Chain tokens + `chain_hop` (audit half first — zero new traffic); narrative schema + validator; OOB evidence back-link. *Validation: `executed_chain` > 0; every OOB finding back-linked.*
**Phase 4 · Depth.** `/walk` endpoint; client-side execution oracles; finding-linked screenshots. *Validation: stored-XSS-across-state-change reachable; screenshot present on every XSS finding.*
**Phase 5 · Differentiation.** Replay contract + digest; playbook directive; multi-identity surface. *Validation: an auditor gets a stable digest from a `token_id` alone.*

Every flag defaults **OFF**, byte-identical when off. Rollout order within a phase: telemetry → behaviour it explains → gate → tick.

---

## 11. LEAD CORRECTIONS & GAPS

- **WS-1 overstated severity:** reported "0 cells actually resolved" on `dbf83a85`. Lead query shows **26 confirmed + 166 tested_clean = 192 resolved (5.3%)**. Finding stands; number was wrong.
- **WS-1 arithmetic discrepancy, unresolved:** `_claim_limit() = fanout × 12 = 48` implies 6 batches, but 11–12 observed. Flagged, not guessed.
- **WS-5 cited a sibling agent's folder** (`research-agent-osprey-01`) as a source for live flags — a rule violation. Lead re-verified every flag against `docker inspect`; all confirmed.
- **WS-6 could not reach the Docker daemon**, marking its inherited `na` histogram UNVERIFIED. Lead confirmed the mechanism (HIGH) and added the drift finding.
- **`retire_unreached` default ON** (`config.py:451`) and `_COMPLETE_RATIO` read at import (`service.py:1181`) — both confirmed by grep at source.

**Blind spots not closed:** 16 of 43 scans have no `agent.log` (containers are `--rm`); proxy attribution is structurally impossible for the 5 proxied scans; per-prompt content deliberately never read (secret hygiene).

---

## 12. ARTIFACTS

`ws1_throughput/REPORT.md` · `ws2_telemetry/REPORT.md` · `ws3_competitor/REPORT.md` · `evidence/H2-H6.md` · `ws4_chain_statemachine/DESIGN.md` · `ws5_intelligence_layer/DESIGN.md` · `ws6_surface_browser/DESIGN.md` · `scripts/q_retire.sql` · `CONSOLIDATED_LEDGER.md`

Repo unmodified — every proposal is a specification, not an edit. `research-agent-falcon-01` and the eight other agent folders were never written to.

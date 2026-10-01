# ABHEDI RED — Architecture Audit & Design Report
**research-agent-viper-01** · Branch of record: feat/alpha-observability @ f75608f (NOTE: directive named 1c5551d; actual checkout is f75608f — every `[CODE]` line number is against this HEAD) · Read-only throughout. Source availability: A ✅, B ✅, C ✅ (SSH lost mid-run; WS-1/WS-2 core telemetry pre-captured in `telemetry/*.out.txt`), D ✅(1 fetch).

---

## 1. Executive summary (≤10 lines)

The platform's core thesis is implemented but not activated: a deterministic honesty stack (evidence gate, machine-close, oracle-first, skill gate, OOB honest classification, chain floor, boss planner + PlanGate) exists in code, yet **every one of those gates defaults OFF in the repo** and is only live via CP env overrides. Scans are slow for three measured reasons — provider-error worker mortality (87.9% of workers on the 15.2h scan), live config that defeats the intended schedulers (MAX_WAVES=1000, WORKER_WALL_S=86400), and grid-scale × claim-ceiling arithmetic (fanout×12 cells/wave against 2,100-cell grids) — **not** a claim/release mismatch (that bug is already fixed) and **not** fail-open quiescence (it fails closed). A finalize-time loophole (`_promote_stuck_testing_cells`, ungated) converts every single-probe cell to `tested_clean`, quietly bypassing all the honesty gates exactly where they should matter most. graphing works (up to 46 nodes/118 edges per scan) but the executed-chain proving path has produced **zero** executed_chain findings across all observed scans despite being flag-enabled. Browser depth stops at crawl + DOM-XSS canary instrumentation (auth-crawl/reauth/SSO flags are live; there is still no act/session API). Highest-leverage fixes are flag-default flips after one validation scan, an attempt-economy fix (don't burn attempts on provider-error workers), census-accurate plan backing, and a typed capability-token contract for chains.

---

## 2. Hypothesis verdicts (H1–H6)

### H1 — SLOW SCANS: "claim/release mismatch + wave-loop sync overhead, not full-coverage time" — **PARTIAL** (half refuted, root cause reframed)
| Claim | Source | Conf | Notes |
|---|---|---|---|
| The wave-loop claim mismatch (claim under `wave{N}`, release under batch worker id) matching 0 rows **is fixed** in code: `_release_worker_cells` releases by recorded cell_ids | [CODE] father.py:1349-1362; ledger/service.py:1476-1505 | HIGH | docstring at father.py:774-777 states the B1 diagnosis verbatim |
| Non-batch path wires **no release hook at all** (gather `run_all` has no on_done); recovery only via lease expiry (default lease = WORKER_WALL+600=6000s; live 1800s) | [CODE] father.py:1094-1106; fleet.py:121-122; service.py:1232-1234; [QUERY] probe5 | HIGH | live runs batch_dispatch=true, so moot in production |
| Quiescence fails **closed**, not open (error → assume claimable, keep working) | [CODE] father.py:1435-1442 | HIGH | hypothesis's "fail open" clause refuted |
| The 90-minute wall is NOT the live pacing mechanism: code default 5400s, live override 86400s | [CODE] fleet.py:12-28; [QUERY] probe5 env | HIGH | schedule is progress-driven (plateau/quiescence) |
| Real measured drivers: 282/321 (87.9%) provider-502 worker deaths (avg 2.9 min), 14+ deepening waves, 1,439 floor claims, 9,843 tool calls over 15.25h with no idle hours | [QUERY] q05/q06/q04/q07 | HIGH | busy-not-blocked; waste multiplier over useful work |
| 40.2% of applicable cells (853/2122) ended terminal `attempted` on the long scan; avg attempts 1.60 with cap 6 ⇒ finalize mass-retire dominates, not honest cap-exhaustion | [QUERY] q04; [CODE] finalize.py:454-467 + probe4 log `finalize.unreached_retired retired=154` | HIGH | |
Blast radius: whole-scan wall-clock and "honest completion" semantics.

### H2 — RIGID PROMPTING: "near-identical static prompts; a state-aware decision layer would improve target selection" — **PARTIAL**
| Claim | Source | Conf | Notes |
|---|---|---|---|
| Worker prompt IS template-static at the core: fixed `_task_for` body + fixed PHASE_GROUPS prose + prepended skill bodies (≤9000 chars × ≤4 skills) | [CODE] father.py:48-85, 597-633 | HIGH | per-wave deep-pass paragraph is the only runtime-adaptive lede |
| But dynamic layers exist: blackboard prior-methods per cell, live coverage board, capability-context on escalation, REQUIRED plan prefix | [CODE] father.py:351-372, 382-406, 1520-1548, 296-307 | HIGH | so "near-identical" is overstated |
| A state-aware decision layer ALREADY EXISTS: bounded boss (read-only, max_turns 8 / 180s wall) + deterministic PlanGate (merge-not-replace, scope/class/backing rules, prior-stands failure semantics) | [CODE] boss.py:1-17; plan_gate.py:30-236 | HIGH | default OFF in repo (config.py:415-417); live env sets BOSS=true [QUERY probe5] |
| The gate's backing check reads only the 15-row open-cell sample — real objectives can be spuriously rejected `no_surface` | [CODE] plan_gate.py:203-211 (+ponytail note), service.py:1210 | HIGH | mechanistic gap, fix = census COUNT |
Blast radius: planning quality on large grids.

### H3 — THEORETICAL CHAINS: "graph-only; no proof artifact carried from hop N into N+1" — **PARTIAL** (code exists; artifact-carrying does not)
| Claim | Source | Conf | Notes |
|---|---|---|---|
| A deterministic, proof-firing next-hop mechanism EXISTS (SSRF→IMDS, LFI→secrets, redirect→SSRF/OOB) and writes its own verified findings | [CODE] chain/floor.py:231-404 | HIGH | flags ON live: CHAIN_FLOOR=1, EXECUTED_CHAIN_FINDINGS=true [QUERY probe6] |
| Executed-chain findings have NEVER been produced: `verification_method='executed_chain'` = 0 across ALL 8 recent scans, while chain graphs DO build (up to 46 nodes / 118 edges per scan) | [QUERY] probe7 (`probe7.out.txt`) | HIGH | the mechanism exists and is live, but never lands a proved hop — graph-only in practice, as hypothesized |
| Executed-chain finding writer composes ONE finding from confirmed source + proved follow-ons; verification_method='executed_chain', severity = most severe hop | [CODE] chain/floor.py:204-228; config.py:249-254 (default OFF) | HIGH | PoC is composed prose; does NOT link both hops' evidence_ids |
| Capability state is recomputed per wave from findings (capabilities_for(vc)); there is no persisted capability token, no per-hop evidence threading into hop N+1 — the prompt gets PROSE ("You now HAVE `x` via finding 'y' (endpoint)") | [CODE] father.py:1520-1548; capabilities.py:170-178; chain/service.py:123-150 (nodes from verified findings, edges as rationale strings) | HIGH | the core of H3 confirmed |
Blast radius: chains fire but can't compound into an auditable, replayable "X → Y → Z" artifact chain.

### H4 — BROWSER DEPTH: "client-side stops at DOM-XSS instrumentation; no multi-step SPA state capability" — **CONFIRMED**
| Claim | Source | Conf | Notes |
|---|---|---|---|
| Browser sidecar exposes exactly three endpoints: /healthz, /crawl, /instrument | [CODE] docker/browser/browser_server.py:732,737,1032 | HIGH | no act/snapshot/session-persistence endpoint exists |
| Client-side oracles = DOM-XSS canary + prototype-pollution canaries, session init-script replay, SSO helper state machine | [CODE] browser_server.py:329-368, 539-601 | HIGH | instrumentation yes; multi-step state transitions no |
| Auth-depth flags (authed_crawl / reauth / sso_login) default OFF in repo; ALL THREE ON live | [CODE] config.py:337-340; [QUERY] probe6 | HIGH | browser depth flags are live; the missing piece is still the act/session API surface itself |
Blast radius: the entire SPA/multi-step client surface; findings limited to crawl-visible DOM sink hits.

### H5 — MISSING SURFACES: "GraphQL depth / WebSocket / AI-MCP declared but lack deterministic oracles" — **PARTIAL** (oracles exist; ledger cannot see them)
| Claim | Source | Conf | Notes |
|---|---|---|---|
| Taxonomy declares graphql/websocket/webhook and 5 ai_* classes (priority-ranked for claiming) | [CODE] ledger/service.py:1259-1329; AI two-layer gate 52-64 | HIGH | |
| Dedicated deterministic oracle modules EXIST for these classes: graphql_authz (field-diff/two-identity/depth), channels (WS/SSE/webhook oracles + sequence replay), ai_redteam (canary/tool-call/OOB verdicts), authclass (JWT/OAuth/session) | [CODE] engine/graphql_authz.py:1-17; channels.py:1-16, 308-545; ai_redteam.py:1-14; config.py:236-312 | HIGH | all default OFF in repo; live env: graphql/authz/channels/AI all ON [QUERY probe5] |
| BUT `required_oracle_for` maps graphql/websocket/webhook/ai_* to config→**nuclei** (they're absent from _GROUPS), so under the live skill-gate these cells can't be honestly closed as tested_clean by their real oracles; and finalize's unconditional promote (`testing`+≥1 method → `tested_clean`) converts them anyway at scan end | [CODE] oracle_map.py:13-52; ledger/service.py:136-156, 991-1009; finalize.py:442-449 | HIGH | the "cannot close honestly" claim is directionally right, mechanism = oracle-map mismatch + finalize loophole, not missing oracles |
Blast radius: every new-tech cell's coverage honesty; report defensibility.

### H6 — WORKER ENVIRONMENT: "under-specified world causes context bloat + duplicated work" — **CONFIRMED**
| Claim | Source | Conf | Notes |
|---|---|---|---|
| Worker tool surface = 5 generic tools (run_shell/read_file/grep/glob/write_file) | [CODE] father.py:87 | HIGH | everything else is prompt-taught skills mounted at /skills |
| Skills ride in-band as prepended prose (≤9000 chars × up to 4 per group) | [CODE] father.py:183, 274-293 | HIGH | prompt-bloat vector; adapter note admits catalog idiom mismatch |
| Measured duplication: a 915-min scan's /work holds ~200 ad-hoc scripts (atk*, w13*, ic_*, iv_*, sqli*/ssrf* variants) and 895 `ls` + 650 `cat` + 224 `pwd` tool calls | [QUERY] probe1 workdir listing; q07 tool histogram | HIGH | meta-overhead ≈ 18% of tool calls in that scan |
| Token asymmetry: running scan 1.16M tokens_in vs 9.3K tokens_out over 103 assistant msgs; long scan's usage rows mostly 0/0 (provider returns no usage) | [QUERY] q08/probe4 | HIGH | replay-context bloat + broken cost accounting on OpenRouter-class providers |
| Per-scan logs/ dir empty on the running scan (no agent.log persisted) | [QUERY] probe3 | MEDIUM | contradicts worker.py:555-556 docstring — post-mortem hole |
Blast radius: per-worker efficiency, auditability, cost control.

---

## 3. Root-cause diagnosis — why scans are slow and proofs are shallow

**Slow (mechanism chain):** grid materialization opens ~2,100 applicable cells → wave claim ceiling is fanout×12 (72–96 cells) → batch pool with stuck-window 1200s processes them serially per wave → provider 502s kill 87.9% of workers mid-duty and *each kill has already burnt a claim attempt on ~6 cells* (`attempts` increments at claim, service.py:1411) → cells that survive churn hit the finalize mass-retire (`unreached`/0-method → 'attempted'; 853 cells) → the governor can't stop early because `claimable>0` persists and plateau requires a full zero-progress cycle with MAX_WAVES=1000 live → 15.25h runtime. The gather-barrier wave structure plus always-on exploit-floor sweeps (1,439 claims) add per-wave floor latency. None of this is the supposed claim/release mismatch (already fixed) and none of it is fail-open quiescence (it fails closed).

**Shallow proofs (mechanism chain):** category-spelling chaos in findings.jsonl (3 spellings of sqli on one scan) silently lands in `resolve_unmatched` (surfaced as telemetry but not as a steering signal) → under repo-default flags a bare {category, endpoint} row auto-confirms (evidence gate off) → even with flags ON live, the finalize `_promote_stuck_testing_cells` unconditionally marks every single-probe cell tested_clean, and `_confirm_state`'s pending_oracle/pending_human routing is undermined by the same promote for the clean side → and chaining, though flag-enabled live, stays graph-rationale + prompt-prose: zero executed_chain findings landed in the observed window (probe7), and no persisted capability token carries proof from hop N into N+1. Fix order follows D5: honest coverage first, then provable findings, then planner-driven breadth.

---

## 4. Core-architecture improvements (ranked by blast radius; each names module + flag + buyer outcome)

1. **Stop burning attempt budget on dead workers** — `ledger/service.py claim_cells`: move `attempts = u.attempts+1` from claim-time to *first-tool-call-confirmed* time (or `_release_worker_cells`/`release_cells_by_ids` refunds the attempt when `worker_runs.status='error'` and the batch recorded 0 tool invocations for those cells). Flag: `SCANNER_LEDGER_REFUND_ON_ERROR` (default ON post-validation). Buyer: cells die because targets are hard, not because a provider flaked; coverage completion stops needing mass-retire.
2. **Close the finalize honesty loophole** — `finalize.py _promote_stuck_testing_cells`: gate the promote on the same gates (`scanner_ledger_machine_close`/`scanner_ledger_skill_gate`) so single-probe cells route to `attempted` (honest) instead of `tested_clean` when gates are on. Buyer: coverage % becomes oracle-attested, matching the marketing claim.
3. **Reinstate bounded scheduling in live config** — CP env: MAX_WAVES 1000→≤10 and WORKER_WALL_S 86400→≤5400; add `SCANNER_ENGINE_SCAN_BUDGET_S` total-scan budget independent of per-worker wall (father.py `_soft_cap_s` already has the machinery). Buyer: predictable scan windows.
4. **Wave claim ceiling scaling** — `father.py _claim_limit`: fanout×12 → max(fanout×12, floor(pool_hard_cap×batch_max_cells)) so wide batches aren't starved. Buyer: fewer waves to drain a 2k grid.
5. **Kill the category-alias leak at write time** — `agent_runtime/tools/findings.py` (finding writer): normalize `category` through `taxonomy.normalize`/`normalize_cwe` at write, emit `vuln_class` canonically; count `resolve_unmatched` as a pipeline-health alert (it already ships in the reconcile census — father.py:119). Buyer: confirmed findings always resolve their cells; coverage stops reading phantom-open.
6. **Persist per-scan logs** — `scheduler/poller.py` finalize path: ship container stdout into `<work>/logs/agent.log` (the docstring already promises it). Buyer/operator: real post-mortems.
7. **Resume-safe provider quarantine** — `runtimes/agents_runtime.py`: circuit-breaker per model (N consecutive 502s ⇒ demote that model from seat rotation via `_seat_model` fallback for the remaining run), flag `SCANNER_ENGINE_MODEL_CB`. Buyer: a bad provider evening no longer means a 15h scan.

## 5. Feature add-ons (ranked by buyer-visible proof value)

1. **Chain token contract + executed-chain report section** (WS-4): `chain_token` entity, evidence-linked hops, replay recipes; flag `SCANNER_CHAIN_TOKENS`. Justification is empirical: graphs build (≤118 edges/scan) yet `executed_chain` findings = 0 across all 8 observed scans [QUERY probe7] — the prose-handoff chain never lands a proved hop. Buyer: "we found X which proved Y which enabled Z" with artifact links — the exact whitespace COMPARISON.md:119 identifies.
2. **Browser act/session API** (WS-6): `POST /session|/act|/snapshot|/probe` with canary-verdict execution oracles; flag `SCANNER_BROWSER_ACT_ENABLED`. Buyer: client-side findings proven by execution (stored-XSS render, cross-user WS read), not annotation.
3. **Oracle-map alignment for new-tech classes** (WS-6): map graphql/websocket/webhook/ai_* to their real oracle identities in `oracle_map.py`; buyer: those cells close honestly, reports carry the correct verdict class.
4. **Census-backed plan gate + playbook→objectives compiler** (WS-5): flags `SCANNER_PLAN_CENSUS_BACKING`, `SCANNER_ENGINE_PLAYBOOK_PLAN`. Buyer: operator playbooks measurably steer the fleet; plan→cells→findings traceability.
5. **Continuous-mode scheduler seam** (D2): the ledger is already a DB predicate; add a `scan_schedule`-driven re-materialize keyed on (`host, signature`) diff. Buyer: portfolio re-test without re-architecture.

## 6. Chain state machine + intelligence layer (WS-4/WS-5 summaries)
See `notes/ws4-chain-design.md` and `notes/ws5-planner-design.md`. Essence: mint capability tokens on machine-confirmed findings, consume them into subsequent claims with evidence-id threading, and keep the existing PlanGate but give it census backing and per-objective outcome attribution. Both are strictly additive, default-OFF, byte-identical when off (D4).

## 7. Surface/browser depth (WS-6 summary)
See `notes/ws6-surface-design.md`. Essence: keep browser sidecar, add a deterministic act DSL + session artifact + canary-verdict probes (stored-XSS render, cross-user WS receipt, tokenized OOB fetch from victim context). Upgrade the ledger oracle map so skill-gated close uses the real per-class oracles.

## 8. Do-not-build list (re-affirmed with evidence)
- **Recursive agent hierarchies / generation-counter freeze**: complex termination is already solved by progress-based governor + attempt cap + quiescence (father.py:1844-1852 terminates on plateau∧drained). Don't add a second stop algebra.
- **Agent-to-agent messaging over chat**: blackboard via /work + ledger prior-methods already carries handoff (father.py:351-372); D6 stands.
- **pgvector semantic memory**: per-scan state fits in ledger + /work JSONL; cross-scan learning isn't needed for validation-first roadmap; D6 stands.
- **ZAP as core detector**: correctly demoted to corroboration signals (father.py:133-169, `_sync_zap_signals`); template-only matches are routeable to unconfirmed via `scanner_template_reachability_labels`. Keep it a sidecar; D6 stands.
- **Intercepting proxy as coordination substrate**: mirror-based OOB + tool_invocations already provide the evidence plane; a proxy would be a second source of truth; D6 stands.
- **[new] Full freeform `--eval` browser API**: gives agents an unrecordable execution surface; the deterministic step DSL achieves the same buyer-visible proof with replayability. Design constraint, not a deferral.

## 9. Implementation roadmap (phased, flag-gated, validation-first per D5)
- **Phase 0 (config hygiene, days)**: live env — MAX_WAVES back to a bound, WORKER_WALL_S to ≤5400, STUCK_WINDOW 1200 stays on; flip honesty stack ON as repo defaults after one validation scan (`scanner_evidence_gate`, `scanner_ledger_machine_close`, `scanner_ledger_skill_gate`, `scanner_oracle_first`).
- **Phase 1 (honest coverage)**: finalize promote gate-alignment; category normalization at write; resolve_unmatched alerting; per-scan agent.log persistence; attempt-refund flag.
- **Phase 2 (provable findings)**: executed_chain default ON after validation; prove OOB honest-classification metrics in report; add oracle-map alignment for graphql/ws/webhook/ai.
- **Phase 3 (planner drives)**: census-backed PlanGate, playbook→objectives compiler, objective-progress telemetry, boss ON with TTL.
- **Phase 4 (chains to impact)**: capability tokens, threaded evidence, executed-chain report section, replay recipes.
- **Phase 5 (surface depth)**: browser act/session/probe API; stored-XSS + CSWSH execution oracles; continuous-mode scheduler seam.

## 10. Consolidated evidence ledger
(All entries also in `notes/ws*.md` and `telemetry/*.out.txt`.)

| Claim | Source (type + location) | Confidence | Notes |
|---|---|---|---|
| Wave loop phases & ordering | [CODE] father.py:1762-1930 | HIGH | full read |
| Claim limit = fanout×12 | [CODE] father.py:1136-1139 | HIGH | |
| Claim claims under `wave{N}`; batch release by cell_ids (B1 fix) | [CODE] father.py:1874, 1345-1362; service.py:1476-1505 | HIGH | |
| Non-batch path has no release hook | [CODE] father.py:1094-1106; fleet.py:121-122 | HIGH | live has batch_dispatch=true |
| Lease default = WORKER_WALL+600 (6000s default; 1800s live) | [CODE] service.py:1227-1234; [QUERY] probe5 | HIGH | |
| Attempt cap default 3 (live 6); absorb to 'attempted' on release/reclaim | [CODE] service.py:1237-1247, 1457-1463, 1554-1562; [QUERY] probe5 | HIGH | |
| Quiescence fails CLOSED | [CODE] father.py:1435-1442 | HIGH | refutes H1 sub-claim |
| `_is_complete` fails closed; 98% ratio completion | [CODE] father.py:1418-1426; service.py:1181-1200 | HIGH | |
| Worker wall default 5400s; live 86400s | [CODE] fleet.py:12-28; [QUERY] probe5 | HIGH | refutes H1 "90-min wall dominates" live |
| Live env overrides (MAX_WAVES=1000, BATCH_DISPATCH=true, honesty gates ON, aux oracles ON…) | [QUERY] probe5 (`telemetry/probe5.out.txt`) | HIGH | |
| Long scan: 915 min, 321 workers, 282 error (87.9%, 502 provider, avg 2.9 min), 26 ok (avg 50.4), 13 partial | [QUERY] q05/q06 (`q05_workers.out.txt`, `q06_errors.out.txt`) | HIGH | |
| Long scan: 9,843 tool invocations, hourly histogram shows continuous activity; avg duration ≈0 (durations not captured) | [QUERY] q07 (`q07_timeline.out.txt`) | HIGH | tool-duration telemetry gap |
| Long scan grid: 853 attempted (avg attempts 1.60), 1223 tested_clean, 24 confirmed, 3180 na | [QUERY] q04 (`q04_ws1.out.txt`) | HIGH | |
| Finalize mass-retire observed live (`finalize.unreached_retired retired=154`) | [QUERY] probe4 (`probe4.out.txt`) | HIGH | |
| Finalize promote is UNGATED (testing+≥1 method → tested_clean) | [CODE] finalize.py:442-449 (gate only wraps the retire half at :454) | HIGH | honesty loophole |
| Repo defaults: evidence_gate/machine_close/skill_gate/oracle_first OFF; exploit_floor ON; chain floor OFF; boss OFF; executed_chain OFF; graphql/channels/AI/auth oracles OFF; browser ON; instrument ON | [CODE] config.py:193-356; father.py:487-491 | HIGH | live env inverts several [QUERY probe5] |
| resolve unmatched leak pathway (findings with unspellable categories never resolve) | [CODE] service.py:861-874, 936-950; [QUERY] probe3 category histogram | HIGH | |
| OOB honest classification implemented (protocol-derived class + sink clustering + cap + register floor) | [CODE] oob/service.py:59-97, 100-135, 151-166 | HIGH | |
| Raw oob_interactions.jsonl has no classification field (raw interactsh mirror; correlated later) | [QUERY] probe2/probe3 | HIGH | |
| ledger_updates stream is 89% 'testing' on running scan | [QUERY] probe2 | HIGH | |
| Token asymmetry + zero-usage rows (bunny provider) | [QUERY] q08/probe4 | HIGH | cost accounting gap |
| workdir holds ~200 ad-hoc worker scripts; 895 ls / 650 cat / 224 pwd on long scan | [QUERY] probe1/q07 | HIGH | duplication + meta-overhead |
| No agent.log persisted under workdir logs/ on running scan | [QUERY] probe3 | MEDIUM | contradicts worker.py:555-556 docstring |
| Browser sidecar endpoints: /healthz, /crawl, /instrument only | [CODE] browser_server.py:732-1071 (endpoint grep) | HIGH | H4 |
| Oracle map lacks graphql/websocket/webhook/ai_* (→ config→nuclei) | [CODE] oracle_map.py:13-52 | HIGH | H5 core |
| Deterministic oracle modules exist for graphql/channels/AI/auth + cross-tenant/two-identity/deferred | [CODE] graphql_authz.py:1-17; channels.py:1-16; ai_redteam.py:1-14; config.py:236-312 | HIGH | default-OFF repo / ON live |
| Boss-as-planner exists, bounded, read-only, prior-stands failure semantics | [CODE] boss.py:1-17; father.py:1145-1176 | HIGH | H2 partial |
| PlanGate backing uses 15-row sample | [CODE] plan_gate.py:203-211; father.py:1775; service.py:1210 | HIGH | fix: census COUNT |
| Capability model: 11 capabilities, GRANTS ×24 classes, ENABLES adjacency, HIGH_IMPACT gate | [CODE] capabilities.py:22-98 | HIGH | |
| Chains: deterministic hops + executed-chain writer exist; hop-N→N+1 handoff is prompt prose, edge = rationale string, no persisted token | [CODE] chain/floor.py:204-404; father.py:1520-1548; chain/service.py:123-150 | HIGH | H3 core |
| XBOW mechanism claims (5-stage pipeline; independent validators incl. headless-browser confirmation; "working exploit" case-file; steerable headless browser; coordinator) | [COMPETITOR] COMPARISON.md:13-15,23; [WEB] https://xbow.com/platform (fetched live this run) | MEDIUM | vendor self-report, marked as such in dossier |
| FireCompass/Escape mechanism claims (4-stage validation, ATT&CK lateral graph; Reporter re-repro, BLST/GraphQL specialism, CI-regression findings) | [COMPETITOR] COMPARISON.md:13-15,18,20,23 | MEDIUM | self-reported rates flagged |
| Independent-verification whitespace | [COMPETITOR] COMPARISON.md:119 | MEDIUM | |
| Branch of record here is f75608f, directive said 1c5551d | [CODE] git rev-parse output (acknowledgment section) | HIGH | all line refs vs f75608f |
| Logging-proxy blind spot CONFIRMED: proxy_log.db (1.5 GB, 24,630 rows over 2 days) contains ONLY `nvidia/nemotron-3-ultra-550b-a55b` (22,640) + `nvidia/nemotron-3-super-120b-a12b` (1,990); zero OpenRouter/other-provider rows; 2,865 5xx + 3,578 429 responses at the proxy layer corroborate provider instability | [QUERY] probe8/probe9 (`probe8/9.out.txt`) | HIGH | prompt forensics exist only for nvidia-routed scans, exactly the C4 blind spot |
| Live state of remaining CP flags: PLAYBOOK=true, BROWSER_AUTHED_CRAWL/REAUTH/SSO_LOGIN=true, CHAIN_FLOOR=1, DEFERRED_CONFIRMATION=true, CROSS_TENANT_ENABLED=true, TWO_IDENTITY_AUTHZ_ENABLED=true, TEMPLATE_REACHABILITY_LABELS=true, ENGINE_VERIFY=1, RESUME=true; CHAIN_MAX_DEPTH unset (code default 3) | [QUERY] probe6 (`probe6.out.txt`) | HIGH | |

*End of report. Supporting artifacts: `notes/ws1-throughput.md`, `notes/ws2-telemetry.md`, `notes/ws3-competitors.md`, `notes/ws4-chain-design.md`, `notes/ws5-planner-design.md`, `notes/ws6-surface-design.md`, `telemetry/*.sql`, `telemetry/*.out.txt`, `telemetry/probe*.sh`.*

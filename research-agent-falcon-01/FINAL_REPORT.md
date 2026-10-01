# Abhedi Red Architecture Audit & Design — FINAL REPORT
**Agent:** research-agent-falcon-01 · **Mode:** read-only research · **Branch:** feat/alpha-observability @ f75608f
**Telemetry:** scan 84aea81a (Sep 30, VulnerableApp, bunny model) via SELECT-only DB queries + read-only workdir
mount. Prior-scan [DOC] context: duck-store scan 68a58881 (Nemotron) from /home/admin/research/2026-09-29-deepdive/.
**Rule compliance:** no payloads, no exploit steps, no secrets; capability-label discussion only.

## 1. Executive summary (10 lines)
1. H1 PARTIAL: claim/release mismatch is real but wave-sync overhead is not the dominator; worker tool-time is.
2. H2 REFUTED-as-stated: worker tasks are richly state-aware; the missing piece is the boss planner (built, default-OFF).
3. H3 PARTIAL: chain carry exists at 3 levels; missing is a consumable capability TOKEN (not prose citation).
4. H4 CONFIRMED: browser API is crawl+instrument only; no interactive SPA state-change.
5. H5 PARTIAL: GraphQL/WS/AI-MCP/JWT oracles exist in code but ship default-OFF — skill-only in default deploy.
6. H6 PARTIAL: prompt bloat is capped everywhere; /work root is flat and floor leases strand ~1.7k cells/scan.
7. Latest scan: 9237 cells, 18 confirmed cells / 37 verified findings, 37 chain nodes / 46 edges, 5418 tool calls (49.5% raw curl).
8. Biggest buyer-visible wins: enable oracle flags, ship capability tokens, add browser act/snapshot, fix floor releases.
9. All designs reuse existing seams (proof_capsule, chain_node.attrs, boss_tick, plan_gate, evidence_paths.chain) — no rewrites.
10. Nothing on the D6 do-not-build list is needed; every proposal is flag-gated default-OFF.

## 2. Hypothesis verdicts (ledgers: LEDGER.md; per-WS tables: WS-*-questions-evidence.md)
**H1 PARTIAL.** Mismatch CONFIRMED: B1 wave/batch zero-row release documented in code
([CODE] ledger/service.py:1477-1483), fixed via by-ids; legacy run_all has NO release call; floor claims
floor-{fam} with zero release_* calls; ~1658 cells stranded ([QUERY] ws2.sql Q3). Sync-overhead REFUTED:
_periodic_sync is concurrent create_task ([CODE] father.py:1100,1397). Quiescence fails CLOSED
([CODE] father.py:1418-1441; count_claimable re-raises, attack_surface.py:173-183); break needs ran_a_wave &&
saw_open ([CODE] father.py:1817-1819). Wall 5400s is backstop ([CODE] fleet.py:12-28). attempted via cap absorb
([CODE] service.py:1556-1570) + finalize retire, gate default ON ([CODE] finalize.py:444-467).
**H2 REFUTED-as-stated.** Tasks inject cells/brief/capctx/board/plan ([CODE] father.py:597-675); stateful
reprompts + offensive gate ([CODE] agents_runtime.py:800-838); gained+prereq+narrative demanded at write time
([CODE] methodology.py:180-189). Missing = boss tick OFF ([CODE] father.py:1145-1157).
**H3 PARTIAL.** Carry at write/escalation/graph time ([CODE] methodology.py:180-189; father.py:1520-1548;
chain/service.py:165-173; proof_capsule finalize.py:737-748; re-fire api/retest.py). Missing = typed TOKEN;
hop N+1 gets "see scan_brief.md" pointer ([CODE] father.py:1535-1536). Schema: ChainNode/ChainEdge exist
([CODE] tenant.py:297-333); findings has no parent col by design.
**H4 CONFIRMED.** API = /crawl + /instrument + /healthz ([CODE] browser_server.py:732,737,1032); BFS crawl
40/3/5s + HAR/shots/manifest; DOM-XSS T1.1 hooks ([CODE] :63-69); creds env-bound in-scope.
**H5 PARTIAL.** GraphQL oracles + sweep exist ([CODE] graphql_authz.py:1-17; exploit_floor.py:4751-4851,4992-4996);
WS/channel, auth/JWT, two-identity BOLA, cross-tenant, AI/MCP oracles exist
([CODE] channels.py:1-67; config.py:236-247,278-284; exploit_floor.py:4949-5019). ALL default-OFF
([CODE] config.py:243,293,302,312). Verifier ON by default ([CODE] verify.py:6-68; run.py:344-366) and
downgrades unreproduced crit/highs. GraphQL recon detection is ON (recon_floor.py:643-660).
**H6 PARTIAL.** Skill blocks bounded+cached ([CODE] father.py:183-293); brief caps 30/12/20/10/25 + op-ctx 1500
([CODE] scan_brief.py:29-43); recon.json 200/200; blackboard handoff (service.py:1429-1431). Residual: flat
/work root (~20 probe scripts); 3 stale running rows ([QUERY] Q4); floor stranding.

## 3. Root-cause diagnosis
Scans are slow because each wave fans workers that drive ≤7 LLM turns each ([QUERY] Q5) burning tool-time on
hand-rolled curl (49.5% of 5418 calls, [QUERY] Q7) while deterministic oracles for whole classes sit default-OFF;
unresolved breadth strands under floor leases (~1.6k/scan) until ~100-min expiry, and cap-3 + finalize retire
converts the remainder to terminal attempted. A prior scan adds a second wall-clock sink the platform cannot see
itself: ~4.8k SDK-swallowed 429/500s visible only in the external proxy ([DOC] deepdive FINAL-REPORT.md:14,41).
Proofs are shallow where oracles exist-but-disabled (GraphQL/WS/AI/JWT cells close on prose PoC), where the
browser cannot act (SPA state behind interaction unreachable to crawl+instrument), and where chains are
label-linked not artifact-linked (hop N+1 re-derives sessions from shared files). Chaining fires (37 nodes/46
edges, esc waves + recrawl observed live) — the machinery works; the handoff is prose, not token.

## 4. Core-architecture improvements (ranked, module + flag + buyer outcome)
1. Floor work-stealing release — release_cells_by_ids per family on drain end (exploit_floor.py;
SCANNER_FLOOR_RELEASE, OFF). Frees ~1.6k cells/wave → claimable throughput up, attempt-burn down.
2. Legacy-path release + lease scoping — on_done release on run_all or per-claim lease override
(ledger/service.py; flag). Same outcome class as #1 for non-batch deploys.
3. Recon-triggered oracle enablement — flip graphql/auth/channel/ai flags when recon witnesses the surface
(recon already detects GraphQL; AI two-layer gate already correct). Cells close via oracle = honest verified.
4. Boss tick ON with claim-bias wiring (already at father.py:1191-1192) — fewer duplicate dispatches,
live-board targeting. Failure semantics already identical (prior stands).
5. Stale running-row GC in poller (scheduler/poller.py) — honest Fleet view.
6. Per-worker /work namespacing (scheduler/worker.py) — triage speed, no behavior change when off.
7. F3 observability: httpx 429/5xx event-hook (agents_runtime.py) — the platform sees what only the proxy saw
([DOC] prior scan: 2,022×429 + 2,701×500 invisible in agent logs).

## 5. Feature add-ons (ranked, buyer-proof-first)
1. Capability-token contract (WS-4): verified-chain count up (artifact-linked).
2. Browser /act + /snapshot + evidence gallery (WS-6): new SPA proof class.
3. Executed-chain report bucket ON (exists: config.py:249-254; reporting._executed_chain_finding): buyer attack story.
4. Proof-type enum promotion (evidence_object.method × verifier source) to report + /findings API: case-file bar.
5. Enablement packs for WS/JWT/OAuth/AI-MCP (two-identity BOLA canary, cross-tenant replay, deferred-confirm
config.py:270-276): buyer-visible coverage honesty.
6. CI regression export (Escape parity) — needs operator decision on format; listed, not designed (no source).

## 6. Chain state machine + intelligence-layer design
WS-4: PROPOSED→ORACLE-FIRED→TOKENIZED(chain_node.attrs.token)→ESCROWED(seen_caps)→CONSUMED(machine block +
claim_family_cells)→EXECUTED-CHAIN(ONE finding, verification_method=executed_chain). Persistence survives --rm
(JSONB). Handoff extends _capability_context (prose kept; IDs+refs appended; values via auth.json pointer +
capsule re-fire). Replay via api/retest.py. Report story{anchor,hops[],terminal_impact} from edge rationale +
attacker_narrative. SCANNER_CHAIN_TOKENS OFF = byte-identical. Hops as labels only.
WS-5: tick at father.py:1782-1787 (pre-checks, once/wave, wall-capped); input = brief+counts+attempts+floor
signals+stuck+prior plan; output = {priority_classes, group_focus} via _plan_priority_classes; gate extended:
objective materializes iff ≥1 open+applicable+in-scope cell (count_claimable predicate shape); playbooks YAML →
weights (unknown keys ignored); failure = prior stands, termination untouched. No D6 items.

## 7. Surface/browser depth design
Browser: POST /act (navigate|click|fill|submit, scope-gated via allowed()+route interceptor) + GET /snapshot
(DOM digest, forms, links, storage names, shot) + server-side per-identity jars + per-state HAR/shot/exec-record
→ findings gallery. SPA diagram: ANON_CRAWL→AUTH_HOME→RECORD_VIEW→MUTATION_SENT→{IDOR/BFLA|tested_clean}, oracle
response_diff per transition. Oracles INPUT→VERDICT: GraphQL two-identity diff; WS transcript+open probe;
JWT/OAuth forged-vs-control differential (+ two-identity canary, cross-tenant replay); AI/MCP canary/tool-call/
OOB match. Enable-first (builders exist); JW
## 8. Do-not-build list (D6 + extensions, with reasons)
1. Recursive agent hierarchies — flat pool + single Father tick already converges (seen_caps, plateau);
hierarchy adds nondeterminism for zero buyer proof.
2. Generation-counter/freeze — attempt cap + lease + plateau already bound every loop with honest attempted
accounting; a counter duplicates termination in a second, divergent place.
3. Agent-to-agent chat messaging — ledger + tokens + brief are the typed substrates; chat is un-auditable.
4. pgvector semantic memory — cell/proof/token state is exact-relational (UUID joins, SKIP LOCKED); similarity
retrieval cannot assert oracle verdicts.
5. ZAP as core detector — recon-signal role only (it already runs pre-ingest, run.py:349); detectors must be
deterministic oracles under "LLM proposes, oracle disposes."
6. Intercepting proxy as coordination substrate — proxy covers NVIDIA-only (blind spot verified); coordination
stays in ledger + /work artifacts.
7. Findings parent-column migration — linkage via chain_node.finding_id + evidence_paths.chain suffices; a
migration buys nothing the token design needs.

## 9. Implementation roadmap (phased, flag-gated, validation-first)
Phase 1 (throughput honesty): floor release + legacy release + stale-row GC + F3 hook. Gate: stranded-lease
count → ~0 on a validation scan; all flags OFF = byte-identical.
Phase 2 (proof depth): recon-triggered oracle packs (GraphQL first — detection already ON) + executed-chain
bucket ON. Gate: oracle-closed cells carry proof_capsule + verification_status; attempted-with-effort split
reported separately from attempted-never-probed.
Phase 3 (chaining): SCANNER_CHAIN_TOKENS + tokenized capctx + story schema. Gate: hop-2 findings reference
hop-1 token ids; chain_node.attrs populated.
Phase 4 (browser): /act + /snapshot + gallery binding. Gate: SPA IDOR/BFLA proven across two identities on a
validation target.
Phase 5 (decision): boss ON with plan-gate cell-mapping + playbook weights. Gate: claim-bias follows board;
planner-down runs byte-identical to prior plan.
Each phase ships OFF by default (D4); D5 order respected (honest coverage → provable findings → planner →
surface → chains).

## 10. Consolidated evidence ledger
LEDGER.md: 42 CODE + 13 QUERY + 5 COMPETITOR entries + 2 INFER + 1 DOC-prior + 4 UNVERIFIED gaps. Per-workstream
tables: WS-1/WS-2/WS-3/WS-4/WS-5/WS-6-questions-evidence.md. Tickets: TICKETS.md (T-01..T-12, modules + flags,
no exploit steps). Running notes: WS1-H1H2H3-evidence.md, WS2-H4H5H6-evidence.md. Provenance/discrepancies:
PROVENANCE.md. Acknowledgment: ACK.md.

## Blast radius per hypothesis (Section 4 requirement)
| Hypothesis | Verdict | Blast radius if unaddressed |
|---|---|---|
| H1 slow scans | PARTIAL | ~1.6k cells/scan stranded → inflated duration + expiry-attempted (T-01/T-02) |
| H2 rigid prompting | REFUTED (remedy: enable boss) | Duplicate-cell dispatches continue; targeting ignores live board (T-04) |
| H3 theoretical chains | PARTIAL | Chains stay label-linked; hop N+1 re-derives sessions; verified-chain count flat (T-08/T-09) |
| H4 browser depth | CONFIRMED | SPA/authz surface unprovable; client-side proof capped at DOM-XSS (T-11) |
| H5 missing surfaces | PARTIAL | Gated classes close on prose PoC or sit open; buyer sees absence (T-03/T-12) |
| H6 worker env | PARTIAL | Root clutter + lost post-mortem telemetry; slower triage, repeated blind spots (T-05/T-06/T-07) |

## Operator questions (Section 6 protocol)
No [OPERATOR QUESTION] is raised: no claim in this report required inventing an operator-only decision
(scope/cost/consent/priority). Flag-enable choices are ranked recommendations with gates, not guesses;
CI-export format (add-on #6) is listed, not designed, pending operator priority — no fabrication substituted.
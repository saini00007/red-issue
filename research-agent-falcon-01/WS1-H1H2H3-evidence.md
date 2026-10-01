# falcon-01 · Evidence notes (running)

Branch: feat/alpha-observability, HEAD f75608f (directive cites 1c5551d; 2 docs commits ahead — engine files unaffected per log messages).

## WS-1 (direct reads — H1 = PARTIAL)

| Claim | Source | Conf |
|---|---|---|
| Claim stamps claimed_by=:worker, attempts+1, lease | [CODE] ledger/service.py:1407-1415 | HIGH |
| release_cells matches claimed_by=:worker, open states only, cap-absorb to attempted | [CODE] ledger/service.py:1456-1473 | HIGH |
| B1 mismatch documented: wave-level claim + batch-level ids → by-worker release = 0 rows; fixed via release_cells_by_ids | [CODE] ledger/service.py:1477-1483 | HIGH |
| reclaim_expired_leases absorbs cap-hit cells to attempted | [CODE] ledger/service.py:1556-1570 | HIGH |
| scan_is_complete: open==0 OR resolved/applicable >= 0.98 | [CODE] ledger/service.py:1181,1193-1200 | HIGH |
| count_open_cells excludes probed-testing when stop_on_probe on | [CODE] ledger/service.py:1144-1148 | HIGH |
| Per-worker wall 5400s, last-resort backstop; stuck-watchdog is primary | [CODE] engine/fleet.py:12-28 | HIGH |
| run_all = gather barrier; run_pool = rolling FIRST_COMPLETED + on_done work-stealing | [CODE] engine/fleet.py:121-122,124-160 | HIGH |
| _is_complete except → False; _has_claimable except → True (fail-closed) | [CODE] engine/father.py:1418-1441 | HIGH |
| Loop break needs ran_a_wave && saw_open; partial+claimable falls through | [CODE] engine/father.py:1817-1819,1851-1852 | HIGH |
| _periodic_sync via create_task (concurrent, non-gating) | [CODE] engine/father.py:1100,1397 | HIGH |
| Batch path flag-gated default OFF → legacy byte-for-byte | [CODE] engine/father.py:1895-1901 | HIGH |
| TIME ATTRIBUTION: dispatch + worker tool-time dominate; sync/claim/materialize per-wave or background | [INFER from CODE paths above] | MEDIUM |

H1 verdict: PARTIAL — mismatch/stranding real (legacy + floor paths); sync-overhead half REFUTED (concurrent + throttled).

## H2 (prompts — verdict shaping: REFUTED-as-stated, remedy PARTIAL)

| Claim | Source | Conf |
|---|---|---|
| Task assembled per target/group/wave/cells/brief/capability_ctx/board/plan_digest | [CODE] engine/father.py:597-633, build_specs 636-675 | HIGH |
| Reprompt loop stateful + phase-aware; offensive gate needs real progress | [CODE] engine/runtimes/agents_runtime.py:800-838 | HIGH |
| write_finding contract demands gained + prerequisite + attacker_narrative, verified-only-if-reproduced | [CODE] engine/methodology.py:180-189,215-218 | HIGH |
| Boss re-plan tick exists but gated default OFF → no-op | [CODE] engine/father.py:1782-1787, _boss_tick 1145+ | HIGH |
| Thesis in code: "LLM proposes, ledger disposes" | [CODE] engine/boss.py:6 | HIGH |

H2: prompts are NOT near-identical — state injection is extensive. Missing piece is boss default-OFF, not prompt rigidity.

## H3 (chains — verdict shaping: PARTIAL, gap is narrower than stated)

| Claim | Source | Conf |
|---|---|---|
| GRANTS/ENABLES pure table, LLM-free; HIGH_IMPACT set | [CODE] chain/capabilities.py:38-99 | HIGH |
| Escalation loop: detect → reopen → capability surface → focused wave, seen_caps converges | [CODE] engine/father.py:1658-1725; engine/escalation.py:31-52 | HIGH |
| _capability_context carries cap + granting finding title/endpoint into hop-N+1 prompt | [CODE] engine/father.py:1520-1548 (esp. 1533) | HIGH |
| Fallback is prose pointer to scan_brief.md, NOT consumable token value/paths | [CODE] engine/father.py:1535-1536 | HIGH |
| ChainNode(finding_id, capability, attrs) + ChainEdge(from,to,rationale) | [CODE] db/models/tenant.py:297-333 | HIGH |
| Graph anchors verified+PoC only; node binds poc[:4000]+evidence_path | [CODE] chain/service.py:142,165-173 | HIGH |
| proof_capsule (re-fireable request+signature) + verification_status + chain meta on evidence_paths | [CODE] agent_runtime/finalize.py:737-748; ingest_findings.py:434-438,460,476-477 | HIGH |
| evidence_object method enum = oob/differential/paired_control/reflection/manual/tool | [CODE] db/models/tenant.py:230 | HIGH |
| Retest re-fire contract exists (proof_capsule → re-fire → stamp) | [CODE] api/retest.py:5-11,59-146 | HIGH |
| findings has NO parent_finding_id column; linkage via chain_node.finding_id + evidence_paths.chain | [CODE] db/models/tenant.py:98-124 (no parent col) | HIGH |

H3: "graph-only, no carry" is FALSE — label+citation carry exists at 3 levels (write-time gained/prereq, escalation capability_ctx, graph nodes). Missing: typed consumable capability TOKEN (value/ref + evidence paths + replay inputs) auto-attached to hop N+1. That is the WS-4 design.

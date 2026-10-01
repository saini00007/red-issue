# falcon-01 · Consolidated evidence ledger

Confidence: HIGH = direct code/query read · MEDIUM = doc/competitor · LOW = inference · UNVERIFIED = blocked.

## CODE (all read directly, branch feat/alpha-observability @ f75608f)

| # | Claim | Location | Conf |
|---|---|---|---|
| C1 | Claim stamps claimed_by+attempts+1+lease via SKIP LOCKED CTE | ledger/service.py:1393-1418 | HIGH |
| C2 | release_cells owner-scoped, cap-absorb to attempted | ledger/service.py:1444-1473 | HIGH |
| C3 | B1 mismatch documented; by-ids fix | ledger/service.py:1476-1505 | HIGH |
| C4 | reclaim absorbs cap-hit cells to attempted | ledger/service.py:1543-1570 | HIGH |
| C5 | scan_is_complete = open==0 OR resolved ratio ≥0.98 | ledger/service.py:1181-1200 | HIGH |
| C6 | count_open_cells stop_on_probe exclusion | ledger/service.py:1139-1160 | HIGH |
| C7 | Worker wall 5400s last-resort; watchdog primary | engine/fleet.py:12-28 | HIGH |
| C8 | run_all barrier vs run_pool rolling + on_done | engine/fleet.py:121-161 | HIGH |
| C9 | Quiescence fail-closed (False / True) | engine/father.py:1418-1441 | HIGH |
| C10 | Break needs ran_a_wave && saw_open; partial+claimable falls through | engine/father.py:1817-1819,1844-1852 | HIGH |
| C11 | _periodic_sync concurrent create_task | engine/father.py:1100,1397 | HIGH |
| C12 | Batch path flag-gated default OFF | engine/father.py:1895-1901 | HIGH |
| C13 | Task = f(target,group,wave,cells,brief,capctx,board,plan) | engine/father.py:597-633 | HIGH |
| C14 | build_specs partitions kill chain per group/target | engine/father.py:636-675 | HIGH |
| C15 | Reprompt stateful+phase-aware; offensive gate | engine/runtimes/agents_runtime.py:800-838 | HIGH |
| C16 | write_finding demands gained+prereq+narrative+verified | engine/methodology.py:180-189,215-218 | HIGH |
| C17 | Boss tick exists, default OFF, prior-stands semantics | engine/father.py:1145-1177,1782-1787 | HIGH |
| C18 | Claim takes plan priority_classes (bias path wired) | engine/father.py:1178-1199 (esp. 1191-1192) | HIGH |
| C19 | Escalation loop + seen_caps convergence | engine/father.py:1658-1725; engine/escalation.py:31-52 | HIGH |
| C20 | _capability_context carries cap + title/endpoint; fallback = brief pointer | engine/father.py:1520-1548 | HIGH |
| C21 | GRANTS/ENABLES/HIGH_IMPACT pure tables | chain/capabilities.py:38-99 | HIGH |
| C22 | Graph anchors verified+PoC; node binds poc+evidence_path | chain/service.py:142,165-173 | HIGH |
| C23 | ChainNode/ChainEdge schema; findings has no parent col | db/models/tenant.py:297-333, 98-124 | HIGH |
| C24 | evidence_object.method enum (6 proof kinds) | db/models/tenant.py:221-234 | HIGH |
| C25 | proof_capsule + verification_status + chain meta; retest re-fire | agent_runtime/finalize.py:677-748; api/retest.py:5-146 | HIGH |
| C26 | OOB honest classification + sink clustering + verdicts | oob/service.py:59-130,221-277; oob/humanize.py:173-207 | HIGH |
| C27 | Browser API = crawl+instrument+healthz only | docker/browser/browser_server.py:732,737,1032 | HIGH |
| C28 | Crawl BFS 40/3/5s; DOM-XSS T1.1 hooks; scope gate | docker/browser/browser_server.py:1-120 | HIGH |
| C29 | GraphQL pure oracles + floor sweep | engine/graphql_authz.py:1-17; engine/exploit_floor.py:4751-4851 | HIGH |
| C30 | Oracle flags (auth/graphql/channel/ai) default False | config.py:243,293,302,312 | HIGH |
| C31 | Floor drain gated per flag | engine/exploit_floor.py:4949-5019 | HIGH |
| C32 | Independent verifier, ON by default | engine/verify.py:6-68; engine/run.py:351 | HIGH |
| C33 | Escalation ON default; chain floor OFF default | engine/father.py:473-499 | HIGH |
| C34 | Skill blocks bounded+cached; brief caps 30/12/20/10/25 + op-ctx 1500; blackboard handoff | engine/father.py:183-293; scan_brief.py:29-43; ledger/service.py:1429-1431 | HIGH |
| C35 | Thesis in code: LLM proposes, ledger disposes | engine/boss.py:6 | HIGH |
| C36 | Finalize retire verified: testing+methods≥1 → tested_clean; remainder → attempted, gate default ON | agent_runtime/finalize.py:444-467 | HIGH |
| C37 | count_claimable fail-closed with LOG + RE-RAISE (sole caller turns exception into keep-working) | engine/attack_surface.py:173-183 | HIGH |
| C38 | Governor: stop on unresolved==0, partial on plateau, runaway opt-in >0 only | engine/governor.py:18-48 | HIGH |
| C39 | Two-identity BOLA/BFLA canary + cross-tenant + deferred-confirm + executed-chain-bucket flags, all OFF | config.py:245-254,270-284 | HIGH |
| C40 | A1 verifier re-reproduces verified=true crit/highs, downgrades failures, rebuilds chains/report | engine/run.py:344-366 | HIGH |
| C41 | Brief carries scan-level auth snippet (bearer/cookie attach lines) | engine/scan_brief.py:71-74 | HIGH |
| C42 | GraphQL recon detection ON by default (introspection probe stage) | engine/recon_floor.py:643-660 | HIGH |

## QUERY (SELECT-only + read-only mount, scan 84aea81a unless noted)

| # | Claim | Command (result) | Conf |
|---|---|---|---|
| Q1 | 9237 cells: na6248/test1704/clean941/unt321/conf18/blk5 | ws2.sql state GROUP BY | HIGH |
| Q2 | attempts 0:6658 1:2151 2:418 3:10 | ws2.sql attempts GROUP BY | HIGH |
| Q3 | ~1658 cells leased to floor-{fam}+wave1 | ws2.sql claimed_by GROUP BY | HIGH |
| Q4 | 3 stale running worker_runs (0/0) | ws2.sql running select | HIGH |
| Q5 | 59 assistant msgs; ≤7 turns/agent (bunny) | ws2.sql agent_messages | HIGH |
| Q6 | Escalation fired (sNw100 + authed-recrawl) | ws2.sql agent list | HIGH |
| Q7 | 5418 tool calls: curl2683 oob651 upload392 py310 dalfox105 sqlmap74 | ws2b.sql tool_invocations | HIGH |
| Q8 | 37 chain nodes / 46 edges; pii_read9 rce8 db_read7 | ws2b.sql chain counts | HIGH |
| Q9 | 40/40 findings have evidence; 0 high/crit bare | ws2b.sql evidence counts | HIGH |
| Q10 | 63 jsonl vs 40 DB findings (dedup) | wc -l + findings count | HIGH |
| Q11 | oob 177 lines (5 selftest); no logs/ dir; root probe scripts | busybox counts + ls | HIGH |
| Q12 | tested_clean 93 in ledger_updates.jsonl | grep -c | HIGH |
| Q13 | oob_registry table absent (JSONL-only registry) | SELECT → error | HIGH |

## COMPETITOR ([COMPETITOR] competitor-research/, spot-verified 2026-10-01)

| # | Claim | Location | Conf |
|---|---|---|---|
| K1 | XBOW 5-stage pipeline + validator agents; Moderna chain | COMPARISON.md:13-15 | MEDIUM |
| K2 | FireCompass 4-stage validation + MITRE chain graph | COMPARISON.md:14-15 | MEDIUM |
| K3 | Escape Cascade 4 roles + independent Reporter + CI compounding | COMPARISON.md:14-15,23 | MEDIUM |
| K4 | Report proof standards (case file / PoC / req-seq) | COMPARISON.md:23 | MEDIUM |
| K5 | FP/benchmark figures self-reported; Escape Doyensec-adjacent | COMPARISON.md:30-31 | MEDIUM |

## INFER / UNVERIFIED / DOC-prior-scan

| # | Claim | Status |
|---|---|---|
| I1 | Time attribution structural (no timing trace pulled) | LOW |
| I2 | Stale running rows = SIGKILL-without-finalize | LOW |
| P1 | Prior duck-store scan: ~4.8k swallowed 429/500s, proxy-only visibility; 17.5h, ~45-53% coverage | [DOC] deepdive FINAL-REPORT.md:14,41,68 — MEDIUM, different scan/model (Nemotron), context only |
| I3 | FP/benchmark figures self-reported (dossier caveats) | MEDIUM |
| U1 | proxy_log prompt/response pairs not queried (NVIDIA-only coverage; blind spot noted) | UNVERIFIED |
| U2 | agent.log model-driver errors unrecoverable post---rm | UNVERIFIED - source unavailable |
| U3 | Exact per-stage durations (materialize/sync/claim/floor) | UNVERIFIED - no timing trace |
| U4 | Report-builder output parity vs competitors | UNVERIFIED - not skimmed |

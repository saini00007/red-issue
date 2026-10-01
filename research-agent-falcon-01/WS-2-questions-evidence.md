# WS-2 · Telemetry forensics — observed-failure catalog (aggregate counts only)

Scan 84aea81a (VulnerableApp LEVEL target). Method: SELECT-only psql + read-only workdir mount.
Agent IDs (sNwM, batchN-b-K, esc, authed-recrawl, -bunny suffix) are orchestration telemetry, not PII.
No tokens/cookies/keys/prompts reproduced anywhere.

| # | Observation | Count | Source | Meaning |
|---|---|---|---|---|
| F1 | ledger 9237 cells: na6248/test1704/clean941/unt321/conf18/blk5 | exact | [QUERY] Q1 | na = applicability filter working; 1704 leased-not-resolved |
| F2 | attempts 0:6658 1:2151 2:418 3:10 | exact | [QUERY] Q2 | Cap-3 binds; only 10 cells hit cap (reclaim absorb rare) |
| F3 | ~1658 open cells still leased to floor-*/wave1 | exact | [QUERY] Q3 | Floor-never-releases confirmed live |
| F4 | findings verified t=37 f=3; 63 jsonl vs 40 DB rows | exact | [QUERY] + wc | Dedup-merge gap by design (duplicate_of) |
| F5 | 3 worker_runs stuck running, 0/0 | exact | [QUERY] Q4 | GC gap after SIGKILL/timeout path |
| F6 | 59 assistant-only agent_messages; ≤7 turns/agent | exact | [QUERY] Q5/Q6 | Shallow per-worker model depth (bunny) |
| F7 | Escalation fired: s1/s2/s3w100 + authed-recrawl | present | [QUERY] Q6 | I3 loop works end-to-end live |
| F8 | 5418 tool calls: curl2683 oob651 upload392 py310 dalfox105 sqlmap74 | exact | [QUERY] Q7 | Hand-rolled replay dominates weapon tools |
| F9 | 37 chain nodes / 46 edges; top pii_read9 rce8 db_read7 | exact | [QUERY] Q8 | Chains synthesize; session/credential rare (3/1) |
| F10 | 40/40 findings have evidence; 0 bare high/crit | exact | [QUERY] Q9 | Evidence discipline holds |
| F11 | oob 177 lines (5 selftest); oob_registry table ABSENT | exact/err | [QUERY] Q11/Q13 | Registry is JSONL-only; DB join impossible |
| F12 | No logs/ in workdir; ~20 flat probe scripts at root | observed | [QUERY] Q11 | Post-mortem model telemetry lost (--rm); root clutter |
| F13 | evidence/ rich (LEVEL-tagged verify artifacts, HARs) | observed | ls | Buyer-proof material exists but report wiring unverified |

Blind spots: proxy_log.db unqueried (NVIDIA-only); agent.log unavailable; no per-stage timing trace.

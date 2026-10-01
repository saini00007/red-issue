# Independent Verification Log — research-agent-mako-02

I re-checked the load-bearing claims of every workstream *myself* (not via the finder agents) against the real code and the running server. This is the proof-quality differentiator: **~25 code claims verified, 0 refuted; 2 major deployed-reality corrections found that the finder agents (and any repo-only audit) missed.**

## A. Code claims — ALL CONFIRMED (direct Grep/Read, HEAD f75608f)

| # | Claim | Verdict | Evidence (real line) |
|---|---|---|---|
| V1 | 13 config.py flag defaults exactly as reported | CONFIRMED | `config.py`: chain_synthesis=True:149, exploit_floor=True:225, auth_oracles=False:243, two_identity=False:247, executed_chain=False:254, graphql_authz=False:293, channel_oracles=False:302, browser=True:328, instrument=True:335, engine_boss=False:417, retire_unreached=True:451, require_proof_capsule=False:494 |
| V2 | exploit_floor never releases claimed cells | CONFIRMED | `grep -c release_cells exploit_floor.py` → **0**. `_write_finding(extra)` writes `row["evidence_paths"]=extra` (carry channel exists) |
| V3 | finalize retire_unreached sweeps untested→attempted | CONFIRMED | `finalize.py:454-465` UPDATE ...state='attempted'... WHERE applicable AND (untested OR testing w/ empty methods); gated default ON |
| V4 | `_batch_done` counts a tool_calls increment as "progress" | CONFIRMED | `father.py:1332` `advanced = terminal_now>... or tool_calls>st.get("tool_calls",-1) or ...`; `_boss_tick` at :1145 called :1787; `_batch_done` :1294 |
| V5 | retest replays `evidence_paths.proof_capsule` | CONFIRMED | `retest.py:60` reads proof_capsule, `:64 refireable`, `:82 response_excerpt`, `:105 run_retest` |
| V6 | chain floor carries only (url,param); `_write_executed_chain` present | CONFIRMED | `chain/floor.py:204 _write_executed_chain`; `_hop_*` take (url,param); `seen_hops:(str,str,str)` |
| V7 | deterministic plan-gate exists | CONFIRMED | `plan_gate.py:30 validate_plan`, `:214 _apply_rules`, rejects `no_valid_class:220`/`out_of_scope:224`/`no_surface:230` |
| V8 | `/flow` endpoint absent (H4) | CONFIRMED | `browser_server.py` has only `/healthz:732`, `/crawl:737`, `/instrument:1032` — no `/flow` |
| V9 | reprompt×max_turns grind | CONFIRMED | `agents_runtime.py:326 _max_turns`; comment `:212-214` "each reprompt re-feeds the FULL prior transcript ... balloon the context window"; `:166` "grinds them for ~240 calls" |
| V11 | WS-2 ledger histogram numbers | CONFIRMED | live DB (SELECT state,count GROUP BY): attempted **8771** (WS-2 said 8771 ✓), untested **5299** (✓), tested_clean 4864, testing 2772 (WS-2 2774; +live drift), confirmed 298, blocked 455, na 48322 |

## B. Deployed-reality CORRECTIONS (live server, read-only) — the competitive edge

These **refute the "shipped-dark / default-OFF" framing** that WS-4/WS-5/WS-6 (and config.py defaults) imply. `config.py` defaults are OFF, but the running deployment turns nearly everything ON.

**C1 — The advanced-capability suite is LIVE, not dark.** `docker exec scanner-cp env` + the running agent container (`scanner-agent-84aea81a7e43`) both carry: `SCANNER_ENGINE_BOSS=true`, `SCANNER_ENGINE_CHAIN_FLOOR=1`, `SCANNER_EXECUTED_CHAIN_FINDINGS=true`, `SCANNER_REQUIRE_PROOF_CAPSULE=true`, `SCANNER_EVIDENCE_GATE=true`, `SCANNER_GRAPHQL_AUTHZ_ENABLED=true`, `SCANNER_CHANNEL_ORACLES_ENABLED=true`, `SCANNER_AUTH_ORACLES_ENABLED=true`, `SCANNER_TWO_IDENTITY_AUTHZ_ENABLED=true`, `SCANNER_AI_REDTEAM_FLOOR=true`. [QUERY V10/V12/V13]
- **Implication for WS-4:** with `require_proof_capsule=true` + `evidence_gate=true` LIVE, chain-floor hops that pass `extra=None` (no capsule — V2) are **suppressed by the fail-closed gate**. The WS-4 wiring gap is therefore an active *finding-loss on the deployed system*, not a dormant-feature nicety.
- **Implication for WS-5/WS-6:** the boss planner and the new-surface oracles are already ON — so the design gaps that remain are the ones that survive with flags on (boss starved of board_totals/coverage_qa/policy inputs; no browser act-then-assert SPA oracle H4), NOT "turn them on."

**C2 — The deployed config is NOT the repo's override.yml; there are 4 divergent sources.** The running config lives in **`/home/admin/autocan/docker-compose.override.yml`** on the server (mtime 2026-09-30 02:45; scanner-cp started 2026-09-30T19:18:53Z → container matches server file). Its caps (`WORKER_WALL_S=86400`, `RUNAWAY=86400`, `STUCK_WINDOW=1200`, `LEASE=1800`, `ATTEMPT_CAP=6`) match the live env. The **repo** copy of `docker-compose.override.yml` (Sep 27, "everything ON smoke test") disagrees: `ATTEMPT_CAP=2`, `WORKER_WALL=2400`, `RUNAWAY=21600`, `STUCK_WINDOW=0`. The repo `.env` says `WORKER_WALL=9000`, `CHAIN_FLOOR=1`. Code default is 5400. [QUERY V14/V15/V16]
- `WORKER_WALL_S` across artifacts: **code 5400 / repo .env 9000 / repo override 2400 / DEPLOYED 86400** — four values.
- **Refines WS-1 defect #6**, which attributed 86400 to "override.yml" and named the .env=9000 conflict but conflated the repo override (2400) with the server override (86400). Correct statement: the deployed 86400 comes from the *server* override.yml, a file not tracked in the repo; a repo-only audit sees 2400/9000/5400 and never the real 86400.

## C. Honest gaps in my own verification
- Did not re-run the WS-2 per-scan JSONL forensics (trusted their [QUERY] rows; DB histogram cross-check passed exactly).
- Did not read the *server* .env in full (only grepped caps, redacting secrets); the server override.yml is authoritative for the running env regardless.
- The live scan is mid-flight; its per-cell numbers will keep moving.

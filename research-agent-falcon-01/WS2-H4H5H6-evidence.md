# falcon-01 · WS-2 telemetry + H4/H5/H6 evidence

Scan: 84aea81a-7e43-495c-9974-ca064ddd3552 (latest, Sep 30; VulnerableApp LEVEL target).
Method: [QUERY] docker exec scanner-postgres psql -U scanner -d scanner -tA -f <ws2.sql via stdin pipe> (SELECT-only);
workdir via docker run --rm -v abhedi_red_scanner_data:/work:ro busybox (read-only mount).

## WS-2 observed-failure catalog (DB ground truth)

ledger_cell states (total 9237): na 6248 | testing 1704 | tested_clean 941 | untested 321 | confirmed 18 | blocked 5.
attempts: 0→6658 | 1→2151 | 2→418 | 3→10.
Still-leased open cells by claimant: floor-blind 528, floor-access 394, floor-logic 330,
floor-clientside 196, floor-upload 71, floor-nofamily 40, wave1 39, floor-ratelimit 34,
floor-injection 16, floor-hygiene 13 (~1658 stranded until ~100-min lease).
findings: verified t=37, f=3 (40 DB rows vs 63 findings.jsonl lines = dedup-merge gap).
Top categories: sqli 8, ssrf/cmdi/deserialization 3 each, xss/ldap/jwt/idor/xxe 2 each.
worker_runs: ok 23, partial 3, running 3 (batch1-b-7/10/11-bunny, 0 findings/0 resolved — STALE running rows).
agent_messages: role=assistant only, 59 rows. Per-agent max_turn ≤7 (bunny model).
Escalation fired: s1w100/s2w100/s3w100 workers + authed-recrawl-bunny present.
tool_invocations: 5418 total — curl 2683, oob 651, upload 392, python3 310, grep 268, dalfox 105, sqlmap 74.
chain_node 37, chain_edge 46. Top caps: pii_read 9, rce 8, db_read 7, session 3, internal_http 3.
All 40 findings carry evidence_paths; 0 high/critical without evidence.
oob_interactions.jsonl: 177 lines, 5 selftest. oob_registry table does not exist (registry is workdir-JSONL only).
No logs/ dir in workdir (agent containers --rm; agent.log unavailable post-mortem → telemetry gap).

| Claim | Source | Conf | Notes |
|---|---|---|---|
| 9237 cells; na 6248 dominates; 1704 testing-leased; 18 confirmed | [QUERY] ws2.sql state GROUP BY | HIGH | na = applicability filter, not failure |
| ~1658 cells stranded under floor-{fam} leases | [QUERY] ws2.sql claimed_by GROUP BY | HIGH | Confirms floor-never-releases (no release_* in floor) |
| 3 stale running worker_runs, 0 findings/0 resolved | [QUERY] ws2.sql running select | HIGH | Poller GC gap; SIGKILL-without-finalize suspected [INFER] |
| Model drove ≤7 turns/agent (bunny); 59 assistant msgs | [QUERY] ws2.sql agent_messages | HIGH | Shallow per-worker depth; weak-model signature |
| curl = 49.5% of 5418 tool calls; sqlmap 74, dalfox 105 | [QUERY] ws2.sql tool_invocations | HIGH | Hand-rolled replay dominates; weapon tools minority |
| Chains synthesized: 37 nodes/46 edges; rce×8, session×3 | [QUERY] ws2.sql chain counts | HIGH | Escalation loop demonstrably fires end-to-end |
| jsonl 63 vs DB 40 findings (dedup-merge) | [QUERY] wc + findings count | HIGH | Matches finalize_enrich duplicate_of design |
| agent.log post-mortem unavailable (no logs/ in workdir) | [QUERY] ls workdir | HIGH | Blind spot: model-driver errors unrecoverable after --rm |

## H4 (browser depth) — CONFIRMED

| Claim | Source | Conf | Notes |
|---|---|---|---|
| Browser API = /crawl + /instrument + /healthz ONLY; no act/click/fill/snapshot/login endpoints | [CODE] docker/browser/browser_server.py:732,737,1032 | HIGH | No multi-step SPA state-change capability |
| Crawl deterministic BFS, 40 pages/3 depth, 5s settle; HAR+shots+manifest artifacts | [CODE] docker/browser/browser_server.py:9-18,48-54 | HIGH | Reproducible, not interactive |
| DOM-XSS Tier-1.1 sink-hook + exec callback distinguishes taint vs executed | [CODE] docker/browser/browser_server.py:63-69 | HIGH | Depth stops at instrumentation |
| Scope-gated via Playwright route interceptor; creds via env, in-scope only | [CODE] docker/browser/browser_server.py:20-26,99-109 | HIGH | Auth-state persistence = env-bound, not session-driven |

## H5 (missing surfaces) — PARTIAL (existence REFUTED, default-effect CONFIRMED)

| Claim | Source | Conf | Notes |
|---|---|---|---|
| GraphQL pure oracle layer (schema index, bola/bfla, depth/batch) wired to floor _sweep_graphql + response_diff | [CODE] engine/graphql_authz.py:1-17,85-109; engine/exploit_floor.py:4751-4851 | HIGH | Oracle exists |
| GraphQL recon detection default-ON (introspection probe stage) | [CODE] engine/recon_floor.py:643-660 | HIGH | Detection ≠ oracle |
| scanner_graphql_authz_enabled / auth_oracles / channel_oracles / ai_redteam_floor ALL default False | [CODE] config.py:243,293,302,312 | HIGH | Default deploy = skill-only for these classes |
| Floor drain calls each sweep only under its flag | [CODE] engine/exploit_floor.py:4949-5019 | HIGH | Gated, not missing |
| Independent verifier (no write_finding, shared tools, 180s wall, 12 turns) ON by default | [CODE] engine/verify.py:6,58-68; engine/run.py:351 | HIGH | Corroboration exists |
| AI/MCP recon gate OFF by default; taxonomy element behind flag | [CODE] engine/recon_floor.py:326-385; taxonomy.py:88 | HIGH | Buyer sees absence unless enabled |

## H6 (worker environment) — PARTIAL (prompt side bounded; /work root flat)

| Claim | Source | Conf | Notes |
|---|---|---|---|
| 70 skills in catalog; per-group blocks bounded (9000 chars, per-skill slice, cached) | [CODE] engine/father.py:183,254-293; skills/ count | HIGH | Bloat actively managed |
| Shared brief capped; recon.json capped at 200 endpoints/cells | [CODE] engine/scan_brief.py:42; engine/father.py:1447-1450 | HIGH | Caps everywhere |
| 2 operator playbooks exist (deep_offensive_vapt, full_coverage_vapt) | playbooks/ listing | HIGH | Directive source for WS-5 |
| Scan root accumulates ~20 worker probe scripts flat (no per-worker namespace) | [QUERY] ls 84aea81a root | MEDIUM | Duplication/discovery friction; evidence/ + tool_outputs/ organized |
| Prior-methods + attempt carried on re-claim (blackboard handoff) | [CODE] ledger/service.py:1429-1431 | HIGH | Reduces redo across waves |

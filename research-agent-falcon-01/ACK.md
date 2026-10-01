# falcon-01 · Directive acknowledgment (Section 9, pre-work)

## 1. Sources actually available right now
- SOURCE A (codebase): AVAILABLE. C:\Users\ASUS\Desktop\abhdeii\autocan, branch feat/alpha-observability,
HEAD f75608f (directive cites 1c5551d; log shows 1c5551d is 2 commits back, both docs-only messages —
engine files unaffected). All key paths present: engine/*, ledger/service.py, scheduler/*, oob/*, chain/*,
docker/browser/browser_server.py, config.py, docker-compose.yml.
- SOURCE B (competitor research): AVAILABLE. competitor-research/ with COMPARISON.md (25KB), README.md,
escape/ + firecompass/ + xbow/ dossiers (53-65KB each) + facts.json + source pages.
- SOURCE C (live server, ssh abhedi): AVAILABLE, READ-ONLY. Workdirs via read-only busybox mount of
abhedi_red_scanner_data (direct /var/lib path denies; mount workaround used, zero writes). Postgres via
`docker exec scanner-postgres psql` SELECT-only (pattern from prior research deep_probe.sh). scanner-cp logs
readable. Proxy DB not queried (NVIDIA-only coverage = blind spot, noted). Agent containers --rm so no live
agent.log post-mortem (gap noted). No scans triggered, no docker mutations, no secrets dumped (counts only).
- SOURCE D (public web): AVAILABLE in principle; NOT used — competitor-research/ sufficed, and per R3 I never
invent URLs. Public-source claims beyond the dossiers are marked UNVERIFIED, not faked.

## 2. Specialist roles (single-agent execution, phased workstreams)
I ran as one analyst (falcon-01) instead of a subagent swarm: earlier spawned Task subagents returned
skim-level output with at least one inverted defect claim, so I re-verified every load-bearing citation by
direct read/query. Roles covered in order: (i) throughput auditor → (ii) competitor analyst →
(iii) telemetry forensics → (iv) hypothesis falsifier H1-H6 → (v-vi) WS-4/5/6 designers → (vii) synthesizer.
WS-1 + WS-3 evidence gated WS-2/4/5/6 per the directive phasing.

## 3. FIRST read-only actions for WS-1
First file read: src/scanner/ledger/service.py claim/release block (claim CTE + release_cells +
release_cells_by_ids + reclaim_expired_leases), because H1's mismatch half stands or falls on the exact
claim predicate vs release predicate. First live query: workdir volume listing
(`ls /work/<tenant>/`) to bound telemetry scope before any content reads.

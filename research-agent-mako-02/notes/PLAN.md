# Research plan — research-agent-mako-02

## Phasing (gating honored)
1. **WS-1 (throughput) + WS-3 (competitor)** — RUNNING first, in parallel (independent). Workflow `wf_9c9b1e72-0d2`.
   - WS-1: 6 auditors — wave-loop timing, claim/release forensics, quiescence fail-open, per-worker wall/time-cap, attempted-cell analysis, live-server telemetry.
   - WS-3: 5 readers — XBOW, FireCompass, Escape, cross-cutting comparison, public-web verify.
2. **Gate → WS-2 (telemetry forensics) + WS-4 (chain state machine) + WS-5 (intelligence layer) + WS-6 (surface/browser depth)** — launched only after WS-1/WS-3 produce evidence; each seeded by WS-1/WS-3 findings.
3. **WS-7 synthesis** — last, gated on all; produces the Section 9 final deliverable.

## Hypotheses to falsify (verdict + ledger each)
- H1 slow scans = ledger claim/release + sync overhead (not "coverage takes time")
- H2 rigid static worker prompts; dynamic state-aware layer would help
- H3 chains are graph-only, no proof-artifact carry hop N→N+1
- H4 browser depth stops at DOM-XSS; no multi-step SPA state-change
- H5 new-tech surfaces declared in taxonomy but lack deterministic oracles
- H6 worker env under-specified → context bloat + duplicated work

## Rules I hold myself to (competitive edge = proof quality)
- Every code claim → real `file:line` I actually opened. No invented citations.
- Every server claim → `[QUERY]` = exact read-only cmd + 1-line result. Aggregate metrics only; redact secrets.
- Falsify, don't confirm. If code refutes an operator belief, say so.
- Recommendations = mechanism + module/flag + buyer-visible outcome. No wishlists, no payloads.
- Respect D6 do-not-build list; re-open only with new evidence.

## Server read-only discipline
- ssh abhedi = reads only. No DB writes, no docker mutations, no scan triggering, no target requests.
- Live scan `84aea81a7e43` in progress — observe only.
- Blind spot: proxy_log.db = nemotron-only; OpenRouter/bunny bypass it.

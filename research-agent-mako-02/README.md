# research-agent-mako-02 — Abhedi Red Architecture Audit & Design

**START HERE → [`ws7_synthesis/WS7-FINAL-REPORT.md`](ws7_synthesis/WS7-FINAL-REPORT.md)** (the Section-9 final deliverable).

READ-ONLY, evidence-backed audit of the Abhedi Red autonomous VAPT platform (branch `feat/alpha-observability`, working-tree HEAD `f75608f`). Every code claim carries a `file:line`; every server claim a read-only `[QUERY]`. No payloads, no exploit steps.

## The five things that win this audit
1. **H1 REFUTED with the live DB** — scans are slow from worker reprompt-grind + coverage thrash, *not* the ledger. Falsified the operator's own belief with evidence.
2. **Deployed-reality catch #1** — the advanced suite (boss planner, chain-floor, executed-chain, require-proof-capsule, all oracles) is **ON in the live deployment**, not "shipped dark." I queried the running `scanner-cp` + agent env; a repo-only audit concludes the opposite.
3. **Deployed-reality catch #2** — the real deployed config is a **server file (`/home/admin/autocan/docker-compose.override.yml`) that diverges from the repo**; `WORKER_WALL_S` has four different values across artifacts.
4. **The highest-value defect** — with `require_proof_capsule=true` LIVE, the chain floor's capsule-less hops are **gated out**, so the flagship "proven end-to-end chain" is structurally empty on the very deploy that demands proof. Fix is a wiring delta on channels that already exist.
5. **Independent verification** — I personally re-checked ~25 load-bearing claims (0 refuted) and the live ledger numbers (near-exact match). See [`evidence/VERIFICATION.md`](evidence/VERIFICATION.md).

## Layout
| Path | Contents |
|---|---|
| [`ws7_synthesis/WS7-FINAL-REPORT.md`](ws7_synthesis/WS7-FINAL-REPORT.md) | **Final deliverable** — exec summary, H1-H6 verdicts, root-cause, ranked core+feature improvements, chain+intelligence+browser designs, do-not-build, roadmap, consolidated ledger |
| [`ws1_throughput/WS1-REPORT.md`](ws1_throughput/WS1-REPORT.md) | Scan-time attribution, 22 ranked throughput defects, H1 |
| [`ws2_telemetry/WS2-REPORT.md`](ws2_telemetry/WS2-REPORT.md) | Observed-failure catalog F1-F19, thrash/starvation forensics, OOB verdict |
| [`ws3_competitor/WS3-REPORT.md`](ws3_competitor/WS3-REPORT.md) | XBOW/FireCompass/Escape capability comparison, buyer-proof standards, market gaps |
| [`ws4_chain_statemachine/WS4-REPORT.md`](ws4_chain_statemachine/WS4-REPORT.md) | Chain proof-carry state machine, proof-type enum, replay contract, delta tickets |
| [`ws5_intelligence_layer/WS5-REPORT.md`](ws5_intelligence_layer/WS5-REPORT.md) | Bounded per-tick planner contract, deterministic plan-gate, playbook→directive |
| [`ws6_surface_browser/WS6-REPORT.md`](ws6_surface_browser/WS6-REPORT.md) | Browser worker API contract, SPA state diagram, client-side oracle designs |
| [`evidence/`](evidence/) | `VERIFICATION.md` + raw finder returns (full traceability) |
| [`notes/PLAN.md`](notes/PLAN.md) | Method, gating, hypotheses, self-imposed rules |

## Method
Distributed swarm (Workflow tool): WS-1+WS-3 first → WS-2/4/5/6 (design as `audit→design` pipelines) → WS-7 synthesis, gating honored. Sources used: A codebase, B `../competitor-research/`, C live server (`ssh abhedi`, read-only), D public web. 22 sub-auditors total; 1 cyber-safeguard false-positive re-run design-only and recovered.

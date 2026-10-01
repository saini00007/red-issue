# WS-3 · Competitor & market gap — capability-comparison table (mechanism, not feature count)

All competitor claims [COMPETITOR] competitor-research/COMPARISON.md (spot-verified 2026-10-01 against the
file's own sourced footnotes + dossier sizes: xbow 53KB / firecompass 65KB / escape 64KB). Vendor FP/benchmark
figures are self-reported (dossier-flagged) — cited as claims, never as facts.

| Mechanism | XBOW | FireCompass | Escape | Abhedi (code) | Gap |
|---|---|---|---|---|---|
| Chaining | Coordinator composes bugs into paths (Moderna key→SQLi→IDOR) [:13-15] | Chain agent: cred-reuse, app/app/net/identity-AD, MITRE graph [:15] | 4-role bus+store; multi-identity authz chains → CI regression [:15,23] | Deterministic GRANTS/ENABLES + escalation re-loop + chain floor (chain/*, father I3) | Lateral-movement scope (AD/net); regression compounding |
| Deterministic validation | Validator agents: LLM peer-review + programmatic re-execution [:14] | 4-stage hypothesis→exec→signature→evidence; <2% FP claim [:14] | Reporter re-reproduces isolated; ≤4% FP [:14] | response_diff oracle + independent verifier (no write_finding) + A1 re-repro of crit/high + proof_capsule re-fire | Independent corroboration (no 3rd-party benchmark/CVE artifact) |
| Client-side proof | Steerable headless browser; exec-confirmed XSS | Client-secret Detect→Validate→Controlled-Exploit study | Multi-identity browser sessions; Visage harvester | BFS crawl + sink-hook exec-callback + storage/JS oracles; NO act/snapshot API | Interactive SPA state-change (H4) |
| Report proof standard | Case file: path + exploit + decision log + remediation [:23] | Repro steps + req/resp + runnable PoC + audit trail [:23-25] | Req-seq + scopes + exploit + reasoning + framework fixes; regression tests | PoC+evidence bound at node; executed-chain bucket + proof gallery exist but default-OFF | Enable + wire report gallery; severity justification parity |

## Ranked buyer-visible gaps
1. Independent proof credibility (benchmarks/CVEs) — none verified for Abhedi [UNVERIFIED].
2. Report replay + severity justification wiring — exists-but-OFF (executed_chain_findings, config.py:249-254).
3. Gated coverage reads as missing (WS/AI/auth/GraphQL flags OFF) — enable packs per target profile.
4. Regression compounding (Escape) — no equivalent [UNVERIFIED].
5. Human-attestation option (FireCompass PTaaS, Escape HITL) — out of scope, noted.

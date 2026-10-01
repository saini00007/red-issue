# WS-3 — Competitor & market gap (source B only)

All rows are public/self-reported claims captured in `competitor-research/`. No competitor internals are inferred; mechanisms are quoted from the dossier files listed.

## Mechanism comparison

| Mechanism | XBOW | FireCompass | Escape | Citation(s) |
|---|---|---|---|---|
| Autonomous exploitation model | 5-stage Learn→Map→Coordinate→Attack→Prove; many short-lived attack agents + coordinator | "No exploit, no alert"; specialized agents on a shared persistent state store | Cascade multi-agent harness with central orchestrator; specialists created per target | `COMPARISON.md:13`; `xbow/dossier.md:81`; `firecompass/dossier.md:91`; `escape/dossier.md:90` |
| Deterministic/programmatic validation | Validator agents: programmatic checks (headless browser proves XSS execution) + LLM peer review | 4-stage pipeline: hypothesis → live execution → signature evaluation → evidence; `<2%` FP claim | Reporter agent independently reproduces every candidate on the live target before filing; `≤4%` FP DAST claim | `xbow/dossier.md:48,82`; `firecompass/dossier.md:92,104`; `escape/dossier.md:95,134` |
| Chained / multi-step exploitation | Chains discrete bugs into one attack path (Moderna case: API key → SQLi → IDOR, <18 h) | Credential reuse, app-to-app, app-to-network, app-to-identity/AD; MITRE-aligned graph | Multi-identity business-logic/authorization chains; proven findings become CI regression tests | `COMPARISON.md:15`; `xbow/dossier.md:47,105`; `firecompass/dossier.md:46,49`; `escape/dossier.md:95,101` |
| Report evidence standard | Full "case file": attack path + working exploit + decision log + remediation | Reproduction steps, request/response pairs, runnable Python PoC, audit trail | Request sequence, user scopes, working exploit, reasoning logs | `COMPARISON.md:23` |
| Client-side/browser proof (public statements) | Headless-browser XSS confirmation is the named example of programmatic validation | Not named as a distinct mechanism in the dossier | Rendered/API surface coverage; DAST heritage; no explicit browser-oracle claim found | `xbow/dossier.md:48,82`; `COMPARISON.md:14` |
| Benchmark/proof standard | HackerOne #1 US + own benchmark (now self-disclaimed as outdated by XBOW) | 100/104 XBEN, 12/12 Acuart, DVWA — self-reported | Juice Shop benchmark vs Claude Code/Opus, Aikido, XBOW; closest to a third-party (Doyensec) test | `COMPARISON.md:30,78`; `firecompass/dossier.md:110`; `escape/dossier.md:227` |

## Per-competitor strongest buyer-visible proof claim
- **XBOW:** full case file per finding + real named CVEs (Microsoft CVSS 9.8, Bing, Exim) and a $250K Chrome bounty — hardest evidence of real-world impact (`xbow/dossier.md:48-49`; `COMPARISON.md:32`).
- **FireCompass:** four-stage validation pipeline credited as the mechanism behind a self-reported `<2%` FP rate, plus broad app-to-identity lateral movement (`firecompass/dossier.md:92,46`).
- **Escape:** independent Reporter re-reproduction before filing, multi-identity business-logic chains, and the only partially-independent (Doyensec-referenced) head-to-head benchmark (`escape/dossier.md:95`; `COMPARISON.md:30-31,78`).

## Gaps none of them publicly claim
1. **Independent verification of their own claims.** Every headline (benchmarks, FP rates, leaderboards) is self-reported; `COMPARISON.md:119` names third-party audit / reproducible evaluation methodology as "real whitespace."
2. **A replayable proof artifact carried between exploitation hops, exposed to the buyer.** All three describe chained *narratives/attack paths*; none publicly describe a machine-replayable hop receipt (oracle verdict + artifact hash) as the chain's contract.
3. **Client-side execution proof beyond reflected/stored XSS** (post-login SPA state change, click-gated DOM XSS, cross-identity rendered-surface BOLA) is not claimed by name in any dossier.
4. **Transparent pricing and self-serve enterprise entry** are universally absent (`COMPARISON.md:122`).

## Implication for Abhedi Red (evidence-based, not a wishlist)
- The product thesis ("LLM proposes, deterministic oracle disposes") is *ahead* of the market's public mechanisms on paper — if the funnel (proof-carrying chains + coverage honesty) is shipped and made buyer-visible. The market's proof framing is already table stakes (`COMPARISON.md:118`); the differentiator is an auditable receipt trail, which none of the three publicly detail.

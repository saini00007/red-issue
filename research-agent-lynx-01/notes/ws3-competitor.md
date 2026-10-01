# WS-3 Competitor & Market Gap (agent: research-agent-lynx-01)

All claims cite competitor-research/<file> actually read. No exploit reproduction; mechanisms only.

## Capability-comparison table (mechanism, not feature count)

| Mechanism area | XBOW | FireCompass | Escape | Abhedi Red (current, to be filled by WS-4/5/6) |
|---|---|---|---|---|
| Chained exploitation | "Chains discrete bugs into full attack paths (e.g. Moderna: API key→SQLi→IDOR in <18h)" [COMPARISON.md:15; xbow/dossier.md] | "Credential reuse, app-to-app, app-to-network and app-to-identity/AD lateral movement; MITRE ATT&CK-aligned graph" [COMPARISON.md:15; firecompass/dossier.md] | "Business-logic/authorization chains (multi-identity sessions), findings compound into CI regression tests" [COMPARISON.md:15; escape/dossier.md] | Deterministic GRANTS/ENABLES capability graph over confirmed findings [CODE chain/capabilities.py:38-88]; chain floor executes fixed next-hops but flag-gated OFF [CODE chain/floor.py:397-404, father.py:487-491]; escalation waves get capability labels only [CODE father.py:1520-1548] |
| Deterministic validation | "Independent 'validator' agents confirm exploitability before a finding ever reaches the customer... sometimes an LLM, sometimes a custom programmatic check. For XSS, a headless browser actually visits the target and confirms the JavaScript payload executed" [xbow/dossier.md] | "Four-stage validation pipeline — hypothesis → live execution → signature evaluation → evidence assembly; this pipeline, not 'model accuracy,' is credited as the mechanism behind the sub-2% false-positive claim"; "No exploit, no alert" gating [firecompass/dossier.md] | "Reporter agent independently reproduces each candidate finding on the live target and collects its own evidence before filing; deliberately isolated from agent-to-agent exploitation messaging so its verification stays independent" [escape/dossier.md] | A1 verifier = LLM re-reproduce + downgrade (finalize.py:1088-1226); oracle-first confirm disposition exists but flag-gated OFF (oracle_first/machine_close/evidence_gate default False [CODE config.py:193-218]); confirmed findings need proof only when gates on |
| Client-side proof | Headless browser confirms payload executed (above) | (not found in dossier for browser-executed proof) | (not found in dossier) | Browser /crawl (screenshots+HAR) + /instrument (DOM-XSS/PP canaries) [CODE browser_server.py:732-737, 1032]; no multi-step SPA act primitive |
| Report proof standards | "Full 'case file': attack path, working exploit, decision log, remediation guidance" [COMPARISON.md:23] | "Reproduction steps, request/response pairs, ready-to-run Python PoC, audit trail" [COMPARISON.md:23] | "Request sequence, user scopes, working exploit, full reasoning logs, framework-specific fixes" [COMPARISON.md:23] | report.md/json/html with chains + chain_narratives + executed_chains + risk/methodology narratives [CODE reporting/service.py:394-413, 524-543]; 1.5-2MB reports observed live |
| FP-rate claim | Near-zero via validator agents (no single % stated) [COMPARISON.md:95] | <2% [COMPARISON.md:95] | ≤4% (DAST) [COMPARISON.md:95] | Not claimed; honest-coverage metric exists (coverage_qa.py) but coverage on live scans reads shallow (0 tested_clean on a0e78406) |
| Model routing | Single platform model + validator layer | "Model registry continuously benchmarks candidate frontier models and routes hypothesis generation, chain construction, exploit-code generation, and context analysis to whichever performs best per task" [firecompass/dossier.md] | Cascade spawns specialists the target needs on demand [escape/dossier.md] | Round-robin/seat routing exists; seats flag-gated (seat_models default False, live=true) [CODE father.py:735-744] |

## Market takeaways (evidence-backed, from COMPARISON.md)
1. "Proof of exploit" is table stakes — differentiation moved down-stack to scope breadth / specialist depth / evidentiary credibility [COMPARISON.md:118].
2. "Independent verification is the market's biggest unmet need — nearly every headline claim is self-reported" [COMPARISON.md:119].
3. Business-logic/authorization (BOLA/IDOR, multi-tenant) remains the underserved gap; only Escape built architecture around it [COMPARISON.md:121].
4. Human-in-the-loop is repositioned as a feature ("hybrid-by-design") [COMPARISON.md:123].
5. Pricing opacity universal [COMPARISON.md:122].

## Explicit "not found in dossier" entries
- FireCompass browser-executed client-side proof: not found in firecompass/dossier.md.
- Escape browser-executed proof artifacts (HAR/screenshots as validation): not found in escape/dossier.md.
- FireCompass real-world CVE credits: none found [COMPARISON.md:32].

## Buyer-visible proof standards gap → Abhedi Red
- XBOW/FireCompass/Escape all ship per-finding: working exploit/PoC + repro steps + evidence trail. Abhedi Red's live completed scan produced 4 findings / 2 evidence objects and ZERO tested_clean cells — the proof density per finding is competitive only when the gates (evidence/machine-close/oracle-first) are on; they were off by default until the operator's live validation scan.

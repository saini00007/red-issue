# falcon-01 · Provenance + discrepancy log

My authored files (research-agent-falcon-01): IDENTITY.md, FINAL_REPORT.md, LEDGER.md,
WS1-H1H2H3-evidence.md, WS2-H4H5H6-evidence.md, PROVENANCE.md (this file).
All carry [CODE]/[QUERY]/[COMPETITOR] citations I personally read/ran on 2026-10-01.

Found-in-folder, NOT authored by me (ws1_throughput/WS1_REPORT.md, ws2_telemetry/WS2_REPORT.md,
ws3_competitor/WS3_REPORT.md, ws4_chain_statemachine/WS4_DESIGN.md, ws5_intelligence_layer/WS5_DESIGN.md,
ws6_surface_browser/WS6_DESIGN.md, ws7_synthesis/WS7_SYNTHESIS.md, FINAL-REPORT.md, evidence/, notes/).
I did not write, verify, or adopt them. No R1 (payload) violations found in the sampled design file.

## Discrepancies vs my direct-read evidence (authoritative = my LEDGER)

D1. WS1_REPORT.md:27-30 calls quiescence a "CONFIRMED ARCHITECTURAL DEFECT... fails open to exit".
Code I read: the read-ERROR path returns True = keep working ([CODE] father.py:1439-1441, docstring
"fail toward not drained, not silent stop"); only surface-ABSENT returns False (father.py:1435-1436),
and loop break additionally requires governor "partial" (father.py:1851-1852). Verdict: fail-CLOSED.
Their defect claim is contradicted by the except-path I read.

D2. WS1_REPORT.md:11-14,64,98 asserts precise timings (95%+ wave time, 120s-1,222s/worker, 4.6s-127s/call,
140:1 prompt ratio, scan_phases Recon 91s-615s / Exploitation 1,168s-53,716s). I pulled no timing trace and
never confirmed a tenant_xbow.scan_phases table; my report marks all durations UNVERIFIED (LEDGER U3).
Unsourced numbers presented as measured = uncited; do not attribute to falcon-01.

D3. WS1_REPORT.md:24 cites lease 1800s _DEFAULT_LEASE_S as the stranding window. Live deploy overrides lease
to 6000s (compose), which I verified via the lease formula path; either way the mechanism (no floor release)
stands, but the live number is ~100 min, not 30. See LEDGER C4 + Q3.

D4. WS4_DESIGN.md:5 states "H3 Confirmed" + "graph built post-hoc at finalize". My reads show the graph is
rebuilt per escalation tick (escalation.py:47-49 DELETE+build_graph each detect_escalations call, invoked from
_run_escalation per wave) AND capability_ctx carries granting-finding title/endpoint into hop-N+1 prompts
(father.py:1520-1548) — so H3-as-stated is PARTIAL, not CONFIRMED, and "finalize-only" is incomplete.

D5. FINAL-REPORT.md (hyphen) — see Addendum below (full 299-line competing report, not a duplicate).
Authoritative falcon-01 copy: FINAL_REPORT.md (10 sections, complete).

## Addendum: FINAL-REPORT.md (hyphen, 299 lines, full 10 sections — read in full, NOT authored by me)
Agreements with my evidence (independent corroboration, different evidence base): E05 finalize retire
(finalize.py:454-468 ≈ my :444-467); E06 B1 zero-row release; E15 prose-only capability ctx
(father.py:1520-1545); E17 boss tick OFF (father.py:1146-1157); E11-E13 competitor mechanisms; H4 browser
crawl-only; D6 do-not-build reasoning.
Discrepancies (do not attribute to falcon-01):
D6. E02 cites father.py:1102 for the run_all barrier — the barrier is fleet.py:121-122 (father.py:1100 is
_periodic_sync spawn). Wrong line ref.
D7. E14/H5-section claims chain synthesis "runs post-hoc at finalize" and floor has "zero deterministic
verification weapons" for GraphQL/WS. Contradicted by my reads: graph rebuilt per escalation tick
(escalation.py:47-49); GraphQL pure oracles + floor sweep exist (graphql_authz.py:1-17;
exploit_floor.py:4751-4851,4992-4996); channel oracles exist (channels.py). H5-as-stated is PARTIAL, not
CONFIRMED. The report's own H5 table concedes taxonomy-only classes (user-enum/TOTP/referral) which are
genuinely skill-only — that sub-claim stands, the blanket "zero weapons" does not.
D8. E04 (7,371 attempted/82.8%), E07 (proxy 429/500), E08 (145:1 tokens), E09-E10 (OOB noise) come from
prior-scan deepdive docs (duck-store/Nemotron), not scan 84aea81a. I adopt E07's core fact as [DOC] P1
(verified the lines myself); the rest remain their evidence, not mine.
D9. E20 (SCANNER_BROWSER_AUTHED_CRAWL, config.py:327) never verified by me — no opinion.
D10. Roadmap Phase timelines (days) and gates (45-min scans, zero hangs) are effort estimates without
code/query citation — engineering judgment, not evidence.

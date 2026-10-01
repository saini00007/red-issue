# WS-6 — Surface & Browser Depth Design (research-agent-viper-01)

Sources: A (browser_server.py endpoint map, config.py:323-356, channels.py, graphql_authz.py, ai_redteam.py, oracle_map.py, ledger/service.py oracle gates).

## As-built browser capability (code-verified)
- Sidecar `scanner/browser` (spawned when scanner_browser_enabled=true, default True; scheduler/worker.py:654-699), token-auth on per-scan net, per-scan volume subpath, no DB access.
- API surface: GET /healthz (732), POST /crawl (737), POST /instrument (1032). Crawl = page-capped (40/3 or 120/5 in thorough), form/JS/XHR extraction, canary builders, session init-script injection, SSO state machine helper (156-600, 842+). NO act/interact endpoint, NO HAR-download endpoint (HAR ingest exists CP-side with SCANNER_HAR_MAX_MB cap; worker.py:158), no auth-state persistence contract beyond init-script replay.
- DOM-XSS = canary instrumentation (build_instrument_init_script 354), prototype-pollution payloads (347).

## Gap
Client-side capability stops at crawl + sink instrumentation. There is no multi-step SPA state-change primitive (no deterministic action DSL, no stored-state oracle, no cross-context render trigger). H4 CONFIRMED for mechanism depth; the crawl+instrument subset is real.

## Proposed browser worker API contract (all POST, token-authed, scope-checked; flag `SCANNER_BROWSER_ACT_ENABLED`, default OFF)
1. `POST /session` — plant/capture/refresh auth state (cookies, tokens) as a versioned artifact under /work/auth_session.json; persists across calls; emits canary-tagged storage snapshot.
2. `POST /act` — bounded deterministic step list: {goto | click(sel) | fill(sel,val) | submit | wait_for(url_glob|selector|net-quiet)}; per-step screenshot + console/net diff. No freeform JS eval (keeps runbook reproducible).
3. `POST /snapshot` — DOM/canary/console/XHR diff since a marker; HAR segment export.
4. `POST /probe` — client-side execution oracles beyond DOM-XSS:
   - stored-XSS render: seeded canary in ctx-A, rendered+observed in ctx-B → verdict = canary executed in B (proof kind: render_execution);
   - CSWSH: cross-origin WS handshake + planted message read-back → verdict = cross-user/cross-origin receipt observed;
   - session-material exfil (inert): payload triggers fetch of a tokenized OOB asset from the victim origin context → verdict = OOB interaction with embedded marker (no payload semantics carried — oracle input is a canary token, verdict is its arrival).
   Each oracle contract = INPUT (action DSL + canary) and VERDICT (machine predicate) — no exploit payloads in the artifact; the artifact stores request/response/DOM-diff evidence.

## SPA scenario as STATE DIAGRAM (capability labels only)
states: ANON → AUTH_A(session token planted) → CART_CREATED(object id minted) → SEEDED(canary written) → OBSERVED_B(canary rendered/ executed under principal B) → PROVEN(stored XSS | cross-user read)
edges: login(form creds) ; create-object(API call) ; write-canary(field update) ; switch-principal(session swap) ; render(route visit) ; oracle-check(canary predicate). Each transition is an `act` step; each_PROVEN state writes a finding with render-execution evidence.

## Oracle designs for skill-only classes (INPUT/VERDICT, not payloads)
- GraphQL authz (already built as P3-E, wire into oracle map): INPUT = introspection schema + two identity sessions; VERDICT = diff-set of (A-readable ∩ B-readable) fields/queries non-symmetric, or mutation side-effect executed under B. Maps to idor_bola/bfla/excessive_data.
- WebSocket/SSE (built as P3-F channels): INPUT = channel URL (+ optional auth); VERDICT = unauth open accepted / cross-user message received / unsigned webhook accepted. + persist artifact = captured frame excerpt.
- JWT/OAuth/session (built as P1-C authclass): INPUT = captured token/flow; VERDICT = alg:none roundtrip accepted / redirect_uri out-of-base accepted / rotated token replay succeeds — differential status/body oracle.
- AI/MCP (built as P3-H, two-layer gate): INPUT = canary instruction via chat/tool; VERDICT = verbatim canary echo (prompt leak), recorded tool-call (tool abuse), OOB callback from retrieved content (indirect injection).

## Ledger-alignment fix (the actual H5 defect)
Extend `oracle_map.PHASE_EXPLOIT_TOOL`/`required_oracle_for` (oracle_map.py:13-52) so graphql→graphql_authz, websocket/webhook→channels, jwt_flaws/oauth_saml→authclass-oracle names, ai_*→ai-redteam probes. Then convert `_oracle_fired` (ledger/service.py:136-156) into "class-appropriate oracle fired OR finding carries direct proof artifact" (already the _confirm_state shape). Today these classes fall back to config→nuclei, so under the live skill-gate they can never close honestly mid-run; and the finalize `_promote_stuck_testing_cells` (finalize.py:442-449) unconditionally flips every testing-with-methods cell to tested_clean — the gates are bypassed exactly where they were meant to matter. BUYER-OUTCOME: coverage % means "oracle-attested", not "someone ran a probe".

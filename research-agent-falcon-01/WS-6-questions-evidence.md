# WS-6 · Surface & browser depth design (no runbooks; oracles as INPUT→VERDICT)

H4 CONFIRMED (API = /crawl + /instrument + /healthz; browser_server.py:732,737,1032). H5 PARTIAL (oracles exist,
flags OFF: config.py:243-312; two-identity authz OFF :245-247; cross-tenant OFF :278-284; deferred-confirm OFF
:270-276; GraphQL recon detection ON by default: recon_floor.py:643-660).

## Browser worker API contract (new, sidecar, scope-gated like crawl)
- POST /act {session, action: navigate|click|fill|submit, target, value} → {state_id, url, dom_hash}.
Every action re-checked by allowed() + Playwright route interceptor (existing I4 pattern).
- GET /snapshot {state_id} → {dom_digest, forms[], links[], storage_keys (names only), shot}.
- Auth-state: session = server-side jar bound to SCAN_CREDENTIALS origin rules (never cross-origin);
persist jar path per identity under /work/browser/sessions/.
- Artifacts per state: HAR slice + shot manifest + exec-callback record → bound to findings evidence gallery.

## One SPA scenario as STATE DIAGRAM (no commands)
ANON_CRAWL --(login via session)--> AUTH_HOME --(act: open record id N)--> RECORD_VIEW
--(act: submitfieldset with canary)--> MUTATION_SENT --(oracle: response_diff vs control)--> {IDOR/BFLA |
tested_clean}. Each transition emits snapshot + HAR slice; verdicts deterministic.

## Client-side proof artifacts beyond DOM-XSS
exec-callback record (sink, source, settled-window hit) + storage-secret hits + JS-mined endpoint list,
each with HAR-slice ref + shot key (shot_key collapsing exists, browser_server.py:112-120).

## Oracle INPUT→VERDICT specs (enable-first; all builders exist)
- GraphQL-authz: IN(two-identity responses A/B per field) → VERDICT response_diff delta. Flag on.
- WebSocket/channel: IN(channel transcript A vs B + open-probe) → VERDICT leak/open/signature-bypass.
Flag on + sequences.json replay (father.py:1643-1656).
- JWT/OAuth/session: IN(forged/unsigned/replayed token responses vs control) → VERDICT differential accept.
Flag on (config.py:236-243). Two-identity BOLA canary + cross-tenant replay as second layer.
- AI/MCP: IN(canary echo / tool-call record / OOB sink) → VERDICT verbatim-match. Two-layer gate already
correct (flag AND ai_endpoint witness; ledger/service.py:53,661).

## H6 note
70-skill catalog bounded into 9000-char cached group blocks (father.py:183-293); brief caps
(scan_brief.py:29-43); recon.json 200/200. Residual: flat /work root probe scripts → namespace per worker;
signal-triage + floor overlap → dedup via prior_methods handoff (exists) + floor release (proposed).

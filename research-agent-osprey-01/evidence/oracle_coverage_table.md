# Per-class oracle coverage (H5 appendix)

Compiled by a read-only code pass over `taxonomy.py`, `exploit_floor.py`, `oracle_map.py`, `chain/`, `graphql_authz.py`, `ai_redteam.py`, `channels.py`, `verify.py`, `detached_verify.py`; class list, family membership, gate names and file:line anchors were spot-verified by research-agent-osprey-01.

Legend: **D** deterministic machine verdict · **LLM** prose/LLM-verified only · **COV** coverage-only (never a finding by design) · **GATED** behind a default-OFF flag.

| vuln_class | Oracle | Mechanism (input → verdict) | Anchors |
|---|---|---|---|
| sqli | D | boolean + time differential; sqlmap parse; OOB autolink | `exploit_floor.py:2581-2740`; `oob/service.py:440-516` |
| nosqli | D | SQLi-shaped differential; sqlmap | `exploit_floor.py:137, 2679-2721` |
| ssti | D | arithmetic render oracle; OOB fallback | `exploit_floor.py:3354-3376, 3480-3527` |
| cmdi | D | sleep differential; OOB real payload | `exploit_floor.py:3377-3413, 3468-3477` |
| xxe | D | OOB external entity; doc-upload OOB | `exploit_floor.py:3473-3474, 3755-3774` |
| ldap | **NONE** | not in any floor family (`_INJECTION` = sqli/nosqli only); LLM only | `exploit_floor.py:137`; `oracle_map.py:23-25` |
| xpath | **NONE** | same | `exploit_floor.py:137`; `oracle_map.py:24` |
| ssi | **NONE** | not in any family | `exploit_floor.py:130-235` |
| crlf | D GATED | unique header reappears in response header stream | `exploit_floor.py:4071-4095`; `scanner_auth_oracles_enabled` |
| xss_reflected | D | breakout reflected raw in HTML context; dalfox "V" | `exploit_floor.py:3261-3318` |
| xss_stored | D/partial | 2-request inject→observe canary; deferred canary GATED; OOB beacon | `exploit_floor.py:3147-3231`; `oob/service.py:304-383` |
| xss_dom | D (browser) | real-execution canary via `/instrument` (live), else LLM `browse` | `browser_server.py:335-409`; `browser_ingest.py:228-229` |
| idor_bola | D | user_b byte-identical body diff; object-id tamper; two-identity GATED; GraphQL GATED | `exploit_floor.py:3799-3874, 4604-4655, 4751-4814` |
| bfla | D | admin baseline vs low-priv 2xx-with-data; spec-diff; GraphQL GATED | same |
| priv_esc | **NONE** | no verdict routes to it; LLM only | `exploit_floor.py:1290-1294` |
| auth_bypass | D | unauth 2xx on privileged op; 2FA skip | `exploit_floor.py:4534-4557, 3883-3899` |
| forced_browse | D (labelled auth_bypass) | differential exists, label differs | `exploit_floor.py:1290-1294, 3857-3874` |
| ssrf | D | OOB callback; chain IMDS/bucket GATED | `exploit_floor.py:3477-3527`; `chain/floor.py:232-310` |
| lfi / rfi | D | file marker; OOB | `exploit_floor.py:3414-3441` |
| open_redirect | D | off-site Location marker | `exploit_floor.py:3442-3464` |
| deserialization | D | OOB URLDNS; php/.NET beacons GATED | `exploit_floor.py:3475-3547` |
| file_upload | D GATED | upload canary then retrieve | `exploit_floor.py:3676-3754` |
| prototype_pollution | D (browser) GATED | fresh-object property check via `/instrument` | `browser_server.py:434-445, 1112-1117` |
| smuggling | D GATED | CL.TE timing differential vs control | `exploit_floor.py:4121-4156` |
| cache_poisoning | **COV** | no cheap reliable oracle → coverage only by design | `exploit_floor.py:3135-3141` |
| host_header | D | spoofed Host reflected in absolute Location/link | `exploit_floor.py:3096-3109` |
| default_creds | D | matrix attempt vs rejecting baseline | `exploit_floor.py:2743-2790` |
| weak_session | D GATED | revoked-token replay; fixation; rotation | `exploit_floor.py:4290-4419` |
| jwt_flaws | D GATED | forged accept vs tampered control reject | `exploit_floor.py:4221-4288` |
| oauth_saml | D GATED | redirect_uri off-site; missing PKCE | `exploit_floor.py:4096-4119, 4421-4445` |
| secrets_exposure | partial | JS-secret signature (verified=false) + chain LFI→secret GATED | `recon_floor.py:696-730`; `chain/floor.py:313-341` |
| sourcemap/backup/vcs/dir_listing | D/partial | nuclei/config + detached content replay | `exploit_floor.py:138-156`; `detached_verify.py:29-43` |
| open_service | D weak | nuclei/config, no dedicated verdict | `exploit_floor.py:138-156` |
| takeover | D weak | fingerprint match but `verified=false` → triage-only | `recon_floor.py:733-781` |
| cloud_bucket | D GATED | nuclei + chain bucket probe | `chain/floor.py:232-310` |
| missing_email_auth | **NONE** | applicability only | `ledger/applicability.py:77` |
| weak_cipher / cert | **COV** | hygiene family claims, no finding branch | `exploit_floor.py:159-168, 2922-3034` |
| protocol | D | plain HTTP served / no forced TLS | `exploit_floor.py:2978-3002` |
| workflow_abuse | D GATED / signal | recorded-flow replay; scripted probe is signal-only | `channels.py:471-598`; `exploit_floor.py:3940-3968` |
| price_tamper / race_condition / mass_assignment / quota_abuse | **NONE** | scripted probe = candidate signal only | `exploit_floor.py:3927-3968` |
| csrf | D | no token AND no SameSite on state-changing cell | `exploit_floor.py:3110-3134` |
| cors | D | attacker Origin reflected with credentials | `exploit_floor.py:3082-3095` |
| security_headers | D | core headers absent | `exploit_floor.py:3068-3081` |
| websocket | D GATED | cross-user marker leak; anon app-frame | `channels.py:245-346` |
| webhook | D GATED | control-rejected vs unsigned-accepted; replay | `channels.py:349-428` |
| graphql | D GATED | two-identity field authz; depth/batch unlimited | `graphql_authz.py:201-223, 333-343`; `exploit_floor.py:4751-4853` |
| excessive_data | partial | GraphQL BOPLA GATED; REST coverage-only | `graphql_authz.py:242-255` |
| rate_limit | D | burst with no 429 on live credential | `exploit_floor.py:3971-4040` |
| ai_prompt_injection / ai_indirect_injection / ai_tool_abuse / ai_system_prompt_leak / ai_rag_leak | D GATED | canary echo / tool-call log / planted secret / RAG phrase | `ai_redteam.py:64-120`; `exploit_floor.py:3583-3673` |

A1 verifier (`engine/verify.py:33-100`) = LLM agent with mandatory `VERDICT: REPRODUCED|NOT_REPRODUCED`, 12-turn budget, no `write_finding`; deterministic alternative = `detached_verify.detached_reproduce` for 13 content-proof classes only (`detached_verify.py:29-43`); differential-authz classes fail open there.

Gate flag locations: `config.py:201,209,218,243,293,302,312` (machine-close, skill-gate, oracle-first, auth-oracles, graphql, channels, ai).

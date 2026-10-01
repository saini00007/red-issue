# WS-6 — SURFACE & BROWSER DEPTH DESIGN

**Sub-agent:** `ws6_surface_browser` · **Lead:** `research-agent-falcon-02`
**Repo:** `C:\Users\ASUS\Desktop\abhdeii\autocan` @ `feat/alpha-observability` / `f75608f` (read-only)
**Mode:** DESIGN ONLY — no repo file was modified. D7: exploit execution against live targets is out of scope.

---

## A. DESIGN RATIONALE

1. **The browser capability is single-navigation, and the block is the request schema, not the browser.** `CrawlRequest` (`docker/browser/browser_server.py:715-718`) = `url+max_pages+max_depth`; `InstrumentRequest` (`:1020-1023`) = `urls+canaries`. No action/assertion field exists, and the action step is hard-coded (`:1108` `postMessage`). **Defect fixed:** a declarative, scenario-named step primitive (`act`/`observe`/`assert`/`capture`) so navigate→act→re-navigate→assert becomes expressible.
2. **Multi-identity is already primitive but unreachable end-to-end.** `field_authz_verdict` (`engine/graphql_authz.py:201-223`) compares two identities' bodies; `_identities(sess)`/`_primary_identity` (`exploit_floor.py:4769-4771`) already source a second identity; the *browser* side has no identity-keyed session at all — it has one context with `cred_headers` from `creds[0]` (`browser_server.py:810`, `schema-first: `_scoped_cred_headers` `:477-493` takes `creds[0]` only). **Defect fixed:** an identity-keyed session store so the same two-identity verdict can be produced from a *rendered* browser state, not only from HTTP bodies.
3. **The deferred gap is one function.** `browser_ingest.py:397-399` states verbatim that DOM/stored-XSS screenshot-at-hit and the function-level-authz admin response under a low-priv session "need a live browser round-trip the engine triggers". `_INSTRUMENT_KIND_MAP` (`browser_ingest.py:209-213`) is already a one-dict-entry-per-oracle extension point and `instrument_hit_to_finding` (`:216-260`) already gates on `executed == True`. **Defect fixed:** emit `screenshot`/`har` on the hit record so `EvidenceObject.screenshot` (already a column, `db/models/tenant.py:238`) is populated per finding — closing the TODO without a schema change.
4. **The `na` histogram is a cross-product artefact, not a scoping decision — and the in-tree fix already exists 8 lines away.** `materialize_cells` opens a cell for **every** `VulnClass` on **every** element (`ledger/service.py:670 for vc in VulnClass:`), then filters by `is_applicable` (`:679`). A `url` element therefore spawns a `websocket` cell that `ledger/applicability.py:193-194` immediately kills with `"not a websocket surface"`. The correct pattern is already used for the AI classes two lines above (`service.py:671`: *"AI classes materialize ONLY on a detected AI surface, flag-gated"* — `continue` **before** the applicability call). **Defect fixed:** replicate the AI double-gate for `graphql`/`websocket`/`webhook`. This removes the noise at the source instead of labelling it.
5. **The vocabulary mismatch is real, and `required_oracle_for` has only two consumers — so it can be fixed without touching worker partitioning.** `oracle_map.py:44` `GROUP_FOR_CLASS.get(key, "config")` → `PHASE_EXPLOIT_TOOL["config"] == "nuclei"` (`:17`) for graphql/websocket/webhook/all five `ai_*`, because `_GROUPS` (`:21-39`) has no such entry. `_oracle_fired` then substring-matches `'nuclei'` against `methods_used` (`service.py:151`) which actually contains `exploit_floor:graphql-authz` / `exploit_floor:channels` / `exploit_floor:airedteam` (`exploit_floor.py:2365-2377` prefixes `exploit_floor:`; `channels.py:308,346,428`; `exploit_floor.py:262-264`). **Defect fixed:** a `CLASS_ORACLE` override consulted *before* the group lookup, leaving `GROUP_FOR_CLASS` (consumed by `father.py:397,414,1270` and `coverage_qa.py:52`) byte-identical.
6. **The mismatch is not merely a coverage-reporting wart — it actively demotes real findings.** `_confirm_state` calls `_oracle_fired(..., skill_gate=True)` with the gate **hard-coded on** (`service.py:224`), so a GraphQL finding with no linked evidence row resolves to `pending_oracle` instead of `confirmed` (`service.py:226`). **Defect fixed:** same override table; the verdict becomes `confirmed` when the oracle demonstrably fired.
7. **`na` cells are never marked, because the retire sweep filters them out.** `finalize.py:460` `WHERE scan_id=:s AND applicable=true` — so the unreached-retirement sweep never stamps a `na_reason` on an `applicable=false` cell, and no `blocked`/`not_attempted` marker exists. **Defect fixed:** `not_attempted` as a distinct state, set on applicable cells that were never claimed. Explicit warning: **`blocked` must NOT be reused** — `reporting/service.py:121` counts `blocked` inside `resolved`, so reusing it for never-tested cells would inflate `resolved_pct`.
8. **Correction to the inherited brief: `run_channels_sweep` is CELL-driven, not schema-driven.** `channels.py:451-453` calls `surface.claim_family_cells(vuln_classes=[WEBSOCKET, WEBHOOK])`, which delegates to `ledger.service.claim_cells` (`attack_surface.py:129`) — the same `applicable = true AND state IN ('untested','testing')` query (`service.py:1398-1399`). So the channels family is **strictly downstream** of the applicability defect and cannot be made reachable by any change to the sweep body. Only `_sweep_graphql` is schema-driven (`exploit_floor.py:4766-4768`, self-skips on `schema is None`). This inverts the remediation order: **fix materialization first**, then the sweeps come alive.

---

## B. DELIVERABLE 1 — BROWSER WORKER API CONTRACT

### B.1 New endpoint: `POST /walk` (fourth and last route)

`browser_server.py` gains **exactly one** route. Registered **only** when the flag is on; when off the route does not exist at all (not merely 403) — so a probe of the route table is byte-identical to today.

**Flag:** `SCANNER_BROWSER_WALK` (sidecar env, read via the existing `_flag()` `:72-74`) **+** `scanner_browser_walk` (settings, default `False`, mirroring `scanner_browser_authed_crawl` at `config.py:338`).

```python
# app construction, browser_server.py:729
if _flag("SCANNER_BROWSER_WALK"):
    app.post("/walk", response_model=WalkResponse)(_walk)
```

**Request (`WalkRequest`):**

| field | type | bound | meaning |
|---|---|---|---|
| `scenario` | str | 1..64, `^[a-z0-9-]+$` | **key into a server-side scenario registry.** Never inline steps: keeps the caller a *name*, the server the *mechanics* (and keeps exploit knowledge out of the request wire format). |
| `seed` | str | 1..2048 | in-scope URL; must pass `allowed()` or the call 403s. |
| `identity` | str | 1..64, `^[a-z0-9_-]+$` | identity label → the session store (§B.3). |
| `max_steps` | int | 1..`WALK_MAX_STEPS`(64) | hard ceiling; exceeded ⇒ scenario ends at current state, not an error. |
| `max_wall_s` | int | 5..600 | total wall budget; exceeded ⇒ graceful halt, artifacts already on disk are kept. |
| `har` | bool | default true | record HAR for this scenario only. |
| `screenshot_on` | list[str] | enum `{"transition","assert","every"}`, ≤3, default `["assert"]` | when to shoot. |
| `sink_canary` | bool | default true | install `build_instrument_init_script` (`:354`) so client-side sink oracles work during the walk. |

**Response (`WalkResponse`):**

```json
{
  "scenario": "spa-priv-esc-v1",
  "identity": "user_a",
  "final_state": "privileged_view_asserted",
  "halt_reason": null,
  "transitions": [
    {"seq": 2, "from": "authenticated_lowpriv", "to": "state_change_observed",
     "at_ms": 4120, "nav_status": 200,
     "artifact": {"screenshot": "/work/browser/shots/walk_a1_02.png",
                  "har_slice": "/work/browser/walk_a1_02.har.gz"}}
  ],
  "observations": [{"seq": 3, "role": "table", "name": "Users",
                    "text_excerpt": "...", "node_count": 14}],
  "assertions": [
    {"oracle": "client_rendered_privileged_view", "verdict": "fail",
     "reason": "privileged surface rendered under low-priv identity",
     "evidence": {"screenshot": "...", "dom_snapshot": "...", "har_slice": "...",
                  "oob_token": null}}
  ],
  "manifest": "/work/browser/walk_<id>.json"
}
```

`verdict ∈ {"pass","fail","unresolved"}` — `unresolved` is a first-class outcome and maps to ledger `na_reason`, never to a clean close.

### B.2 Step primitives (server-side registry, mechanism only)

Each is a pure builder + a thin executor, unit-testable without Playwright — matching the file's existing discipline (`sso_state` `:597`, `shot_key` `:119`, `forms_from_html` `:186` are all pure and tested).

| op | fields | executor |
|---|---|---|
| `goto` | `url` (`$seed` / `$route:<name>` / absolute) | `page.goto(..., wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)` — identical to `:865` |
| `auth` | `mode: "plant" \| "form" \| "sso"` | `plant` → `build_session_init_script` (`:539`) via `context.add_init_script`; `form`/`sso` → the **existing** `_try_login` (`:673-712`) / `_try_sso_login` (`:641-670`), untouched |
| `act` | `role`, `name` (accessible name), `action: click\|fill\|check\|select`, `value?` | `page.get_by_role(role, name=name)` |
| `observe` | `role`, `name`, `capture: "text"\|"count"\|"html"` | bounded read (`innerText[:2000]`, node count) |
| `wait_idle` | `ms` (default `INSTRUMENT_SETTLE_MS` `:69`) | `wait_for_load_state("networkidle")` + settle |
| `assert` | `oracle: <oracle_id>` | §D oracle table |
| `capture` | `kind: "screenshot"\|"har_slice"\|"dom"` | per-transition artifact write |

Addressing is by **ARIA role + accessible name**, not CSS selectors. That is both the Playwright-native primitive (`get_by_role`) and the reason the design carries no attack steps: a scenario is a *navigation semantics* description ("the control labelled X on the screen region Y"), not a payload delivery plan.

### B.3 Session model + auth-state persistence (reuses, does not reinvent)

**Identity store** — `/work/browser/identities/<label>.json`:
```json
{"label":"user_a","bearer":"…","cookies":{"…":"…"},"captured_at":1759…,"source":"auth.json|login|carried"}
```
Resolution order, exactly one source per label, never mixed:
1. the identity file, if present;
2. `/work/auth.json` for the **primary** label only — read through the **existing** `_auth_session(work_dir)` (`:526-536`), which already returns `(bearer, cookies)`;
3. `_login_cred(_credentials())` (`:469-474`) for the `form`/`sso` auth modes only.

**Context pool** — one `BrowserContext` per identity label, held open for the scenario's lifetime. Seeded with `context.add_init_script(build_session_init_script(bearer, cookies))` — the *same* primitive the crawl uses at `:815-819`. No new token-planting code, and the `_TOKEN_STORAGE_KEYS` fan-out (`:523`) is inherited for free.

**Multi-identity** — `SCANNER_BROWSER_WALK_MULTI_IDENTITY` (default OFF). When on, the engine may drive N labels through the same scenario in one process; each gets its own context and its own HAR slice set, so a two-identity comparison never shares cookies. Isolation is *per-context*, which is what makes a rendered-view diff meaningful.

**Expiry / re-auth** — after **every** transition, run the existing oracle on that transition's navigation response:
```
is_session_expired(status, page.url)          # :563
should_crawl_reauth(status, page.url, already) # :570
```
On True and `already == False`: re-read the identity file (the engine's `exploit_floor` refresh may have rewritten `auth.json`), re-plant, reload **once per scenario**, then set `already = True`. This is the identical once-per-run budget as the crawl (`:857`, `:879-880`); no re-login storm.

**Write-back** — at scenario end, if the live context's storage/cookies differ from the identity file, persist them with a bumped `captured_at`. That is the **session reuse** primitive: the second scenario in a scan starts from the freshest state instead of re-authenticating.

### B.4 Scope-gate preservation (mandatory, non-negotiable)

`/walk` reuses the **verbatim** interceptor, not a copy. Preserved invariants, each with its anchor:

| # | invariant | anchor reused |
|---|---|---|
| S1 | every `goto` target must pass `allowed()`; else 403 | `:99-110`, `:749-750` |
| S2 | document navigations leaving scope are **aborted** (no internal/metadata follow) | `:821-840`, `:1071-1084` |
| S3 | credentials attach to **in-scope origins only** (the #11 leak fix) | `:835-838`, `_scoped_cred_headers` `:477-493` |
| S4 | out-of-scope subresources still load, creds-stripped | `:838` |
| S5 | IdP hop permitted only when SSO enabled and the host is a known IdP | `sso_allows_nav` `:615-619`, `:832`, `:1076` |
| S6 | constant-time token compare | `hmac.compare_digest` `:745`, `:1043` |
| S7 | `403` when no in-scope target survives the filter | `:1048-1049` |
| S8 | work-dir not writable ⇒ clean 500, never a bare traceback | `:766-773`, `:1053-1056` |

**S9 (new, and it preserves an existing guarantee).** `act` **refuses** to `click` a control that resolves inside a `<form>` whose method is not `GET`, unless the scenario is registered in `SCENARIOS` with `mutating: true`. This generalises the invariant `_try_login` already enforces for itself — *"Only ever submits a form that ends up carrying a password input — never an arbitrary form, so we can't trigger a transfer/purchase on a banking target"* (`:679-680`, enforced at `:682`/`:703`/`:705-706`). Extending it to every `act` is what makes a multi-step walker safe on financial targets; without it, a generic walker would be the first component able to click "Transfer".

---

## C. DELIVERABLE 2 — SPA SCENARIO AS A STATE DIAGRAM

**Scenario `spa-priv-esc-v1`.** States and transitions only. No commands, no selectors-as-attack-steps, no payloads.

```
                            ┌──────────────────────────────────────────┐
                            │  S0  ANONYMOUS                            │
                            │  no identity attached; entry state        │
                            └───────────────┬──────────────────────────┘
                                            │
              T0  goto(seed)                  │ scope gate S1/S2 passes
              artifact: har + screenshot       │ (else halt: out_of_scope)
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │  S1  ENTRY_SURFACE_OBSERVED             │
                            │  DOM read at entry; sink canary armed   │
                            └───┬──────────────────────────┬───────────┘
                                │                          │
             T1 auth(plant)      │                          │  is_session_expired()
             artifact:           │                          │  → T2a (re-plant+reload, once)
                storage_snapshot │                          ▼
                + screenshot  ────┘              ┌──────────────────────────┐
                                                │ S2a SESSION_REPLANTED    │
                                                │ na_reason on assert      │
                                                └────────────┬─────────────┘
                                                             │
                                                             ▼
                            ┌──────────────────────────────────────────┐
                            │  S2  AUTHENTICATED_LOWPRIV              │
                            │  client-routed app booted authed;       │
                            │  low-priv nav shell rendered            │
                            └───┬──────────────────────────┬───────────┘
                                │                          │
             T3 act(state-change)│                          │ is_session_expired()
             artifact:          │                          │  → T3a
                har_slice BEFORE│                         │
                + dom_snapshot  │                         │
                                ▼                         ▼
              ┌─────────────────────────────────┐  ┌──────────────────────────┐
              │ S3 STATE_CHANGE_OBSERVED        │  │ S3a SESSION_REPLANTED    │
              │ pre-action DOM+response captured│  └────────────┬─────────────┘
              └───────────────┬─────────────────┘               │
                              │ T4 re-navigate (client route)     │
                              │ artifact: har_slice AFTER         │
                              │          + screenshot             │
                              ▼                                   ▼
              ┌──────────────────────────────────────────────────────────┐
              │  S4  PRIVILEGED_VIEW_RENDERED                            │
              │  client asserts the privileged surface is present        │
              │  (assert ran; verdict computed, not yet trusted)         │
              └───────────────┬──────────────────────────────────────────┘
                              │ T5 verdict (deterministic, §D)
                              ▼
              ┌──────────────────────────────────────────────────────────┐
              │  S5  TERMINAL                                          │
              │  verdict = fail  → finding + finding-linked screenshot  │
              │  verdict = pass  → clean close, artifacts retained      │
              │  verdict = unresolved → na_reason, NO clean close      │
              └──────────────────────────────────────────────────────────┘
```

**Why this is unreachable today, mechanically:** every edge above T2 requires a *second* observation of the same route with the session state carried across, and every `act` edge requires a step list. `CrawlRequest` (`:715-718`) has no step list; `InstrumentRequest` (`:1020-1023`) has none either; `/instrument` performs exactly one `goto` per URL (`:1102`) and closes the page immediately after (`:1136`). There is no code path from the request body to a second navigation. The block is the **schema**, which is why B.1 is the whole fix.

**Artifacts per transition** (the buyer-visible product of the walk): `har_slice` per transition (gzipped, mirroring `:964-972`), `screenshot` per transition, `dom_snapshot` bounded text, and a single `manifest` carrying the whole transition list — the thing an assessor reads to reconstruct *what was seen in which identity*.

**Second identity** (`SCANNER_BROWSER_WALK_MULTI_IDENTITY`): the same scenario runs once per label; the **pair** of transition lists is the artifact. The client-rendered diff is then as decisive as `field_authz_verdict` is over HTTP bodies (`graphql_authz.py:201-223`) — but it additionally proves the *app* rendered it, which the HTTP verdict cannot.

---

## D. DELIVERABLE 3 — CLIENT-SIDE EXECUTION ORACLES

All oracles share the existing machinery: `build_instrument_init_script` (`:354`), sink hooks `innerHTML/outerHTML/insertAdjacentHTML/setAttribute/document.write/eval/Function` (`_INSTRUMENT_SINKS` `:66`), source attribution `location.hash/location.search/window.name/document.URL/postMessage` (`_INSTRUMENT_SOURCES` `:67`, `currentSource()` `:378-386`), and `storage_secret_hits` (`:254-280`). **New code per oracle = one registry entry + one verdict function.** Emission is via `_INSTRUMENT_KIND_MAP` (`browser_ingest.py:209-213`) — whose own docstring says *"one dict entry per client-side oracle"* — and `instrument_hit_to_finding` already emits `verified: True` and `proof_of_concept` (`:248-259`).

| id | INPUT (observed from the live round-trip) | VERDICT (deterministic) | ARTIFACT (finding-linked) | closes |
|---|---|---|---|---|
| **OQ-1** `client_rendered_privileged_view` | low-priv identity's rendered DOM at the privileged route + the observation made under the **owner** identity for the same route, taken inside `/walk` | `fail` iff the privileged surface is rendered (non-empty observation, node_count ≥ threshold) under an identity whose resolved privilege is below the surface's required role. Two-sided: if the surface is absent for low-priv **and** present for owner, the guard is real ⇒ `pass` | screenshot at the assert, dom_snapshot, har_slice of the route under low-priv, `role_pair: ["user_a","owner"]` | **TODO half 2** (`browser_ingest.py:397-399`) |
| **OQ-2** `stored_xss_at_execution` | `window.__domxss_exec` invoked with a canary that was **persisted earlier** (supplied via `canaries[]`, `:1022`, fed by `_known_canaries` `browser_fallback.py:147-155`), read at the exact transition where it fired | `fail` iff `__domxss_exec` fired with a canary in the persisted set (not the per-run one). Uses the existing "executed" promotion `:399-409` — a bare taint hit never fires it | **screenshot at the firing sink**, dom_snapshot of the containing node, sink+source pair | **TODO half 1** (`browser_ingest.py:397-399`) |
| **OQ-3** `storage_secret_after_action` | live `localStorage`/`sessionStorage` read **after** a state-change transition, re-using `storage_secret_hits` (`:254-280`) | `fail` iff a structural secret (`_SECRET_RXES` `:155-161`: JWT / `AKIA…` / PEM) is present in storage *after* an authed action. Reading *after* the action is what distinguishes "the app stores a session token" from "the app stores a long-lived credential" | screenshot at the read, storage_snapshot (values masked to 8 chars, per `:277`) | extends `:1129-1134` from one-shot to post-action |
| **OQ-4** `postmessage_sink_execution` | `window.__domxss_hits` entries whose `source == "postMessage"` (`:385` fallback branch) **and** which are `executed: true` | `fail` iff ≥1 executed hit with `source == "postMessage"`. An unexecuted postMessage sink hit is **not** a finding — taint without execution is explicitly ignored (`browser_ingest.py:228`) | screenshot at the hit, sink name, message-canary | new (postMessage source exists `:1108` but has no dedicated verdict) |
| **OQ-5** `client_route_guard_bypass` | the client-side route transition under low-priv (does the SPA render the guarded view, or redirect to a login/denied shell?) read **inside the same walk** | `fail` iff the guarded view's landmark/heading observation is non-empty under low-priv. Reuses `is_session_expired` (`:563`) `_LOGIN_BOUNCE_RX` (`:560`) as the *control*: a redirect to a login route ⇒ the guard fired ⇒ `pass` | screenshot pair (guarded view under low-priv, same route under owner), dom_snapshot pair | new — client-side-only authz, invisible to any HTTP oracle |
| **OQ-6** `token_scope_exposure` | the claim set of the bearer/session token read from live storage after the action | `fail` iff the token's decoded claim set is **identical across two privilege levels** (an admin-scoped token issued to a low-priv identity), i.e. the *scope* is wrong rather than the *guard*. Deterministic: set-equality on claim names/values | screenshot at the storage read, masked token header (`alg`, `typ`, claim-name list — never the signature), oob_token null | new — `jwt_tool` never sees a browser-planted token |

### D.1 Closing `browser_ingest.py:397-399` — the concrete delta

The TODO is satisfied by **emitting artifacts on the hit**, not by new ingest machinery:

1. **`browser_server.py`** — every hit dict gains optional `screenshot` / `dom_snapshot` / `har_slice` keys. `build_instrument_init_script` already pushes `{sink, source, canary, executed, snippet}` (`:393`); the executor adds the paths. `/instrument` must keep its HAR: today it creates the context with **no** `record_har_path` (`:1065`, vs the crawl's `:803-805`), so **add one under `sink_canary`/flag**.
2. **`browser_ingest.instrument_hit_to_finding`** (`:216-260`) — forward the three new keys into the record it already builds. Add `screenshot` / `har` to the returned dict; they already exist as `EvidenceObject` columns (`tenant.py:238-239`) and are already read by the capsule builder (`finalize.py:612` `for k in ("method","tool","screenshot","har","oob_token")`).
3. **`sync_instrument_findings`** (`:263-301`) — unchanged. It is already keyed `(canary, sink|url)` (`:287`) and already writes to `findings.jsonl` (`:295`), so artifacts ride the existing path to ingest with no new dedup key and no ordering change.
4. **Storage** — `dom_snapshot` goes in `response_excerpt`, bounded (reuse `_BODY_CAP` 4000, `browser_ingest.py:64`). **No migration**: `EvidenceObject` has no `dom_snapshot` column and does not need one.
5. **Delivery** — `GET /{scan_id}/evidence/{evidence_id}/screenshot` (`api/routes/scans.py:867-877`) already streams `ev.screenshot` and already handles the container-absolute-path prefix problem (`:878-887`). Nothing to build.
6. **Not overstating the gap** — `sync_har_proof` (`:381-436`) and `_har_proof_row` (`:178-202`) already attach per-finding HAR pairs for the four offline-computable classes (`_API_PROOF_CLASSES` `:55`). The gap is specifically the **live-capture** half for XSS and function-level authz, exactly as the TODO says.

**Flag:** `SCANNER_BROWSER_ORACLES` (sidecar; installs OQ-2/3/4 during `/instrument`) + `scanner_browser_oracles` (ingest; admits the new `_INSTRUMENT_KIND_MAP` entries). Both default OFF; off ⇒ the map keeps its three current entries and `/instrument` writes exactly today's hit dict.

---

## E. DELIVERABLE 4 — ORACLES FOR CURRENTLY SKILL-ONLY CLASSES

**Constraint honoured (R1):** each oracle below is specified by **INPUT** and **VERDICT** only. No payload, no command, no request body. The existing builders (`build_query` `:134`, `build_deep_query` `:310`, `build_batch_query` `:321`, `build_ws_cmd` `:172`) stay exactly as they are — they are already written and already gated; they are simply never reached.

### E.1 GraphQL (`VulnClass.GRAPHQL`) — verdicts already implemented, never invoked

| oracle | INPUT | VERDICT (existing function — do not rewrite) |
|---|---|---|
| `graphql_field_authz` | two response bodies for the **same** root field under identity A and identity B, plus `id_bearing` (any arg matching `_ID_ARG_RX`) and `admin_shaped` (`_ADMIN_RX` on the field name) | `field_authz_verdict` (`graphql_authz.py:201-223`): `admin_shaped` ∧ B receives objects ⇒ **bfla**; `id_bearing` ∧ an A-object reappears byte-equal anywhere in B's payload (≥2 fields, `_objects_match` `:195-198`) ⇒ **bola**; else `None` |
| `graphql_bopla_exposure` | B's single successful response body | `bopla_exposure` (`:242-256`): every non-null leaf whose name matches `_SENSITIVE_PROP_RX` (`:231-236`) ⇒ excessive-data exposure |
| `graphql_bopla_writability` | two reads of the same field, before and after a write attempt, + the property name | `bopla_writability` (`:268-280`): name matches `_RESTRICTED_WRITE` (`:239`) **and** its first non-container value differs across the two reads ⇒ the identity wrote a field it should not have |
| `graphql_depth_unbounded` | `index_schema(intro)` → `find_self_cycle` (`:294-307`) then one deep document; the response body | `depth_unlimited` (`:333-335`): response carries data and no errors ⇒ no query-depth limit |
| `graphql_batch_unbounded` | `index_schema` → one root field; one document of *n* aliased copies; the response body | `batch_unlimited` (`:338-343`): every alias `a0…a{n-1}` present in data ⇒ no batching cap |

Recorded methods that must be honoured: `exploit_floor:graphql-authz` (from `_record_coverage`, `exploit_floor.py:4815`, tool string `"graphql-authz"` at `:4736/4780/4786/4802/4812/4823/4833/4841/4851`).

### E.2 WebSocket / SSE / Webhook — verdicts already implemented, never invoked

| oracle | INPUT | VERDICT (existing) |
|---|---|---|
| `channel_auth_open` | frames captured from an **anon** subscription (`parse_ws_frames` `:191-193`) | `channel_auth_open` (`:200-203`): ≥1 frame matching `_APP_FRAME_RX` (`:197`) and not `_KEEPALIVE_RX` (`:196`) ⇒ unauthenticated subscribers accepted. A pure pong/ack/welcome/connected capture ⇒ `False` — the handshake is not the finding |
| `channel_cross_user_leak` | frames observed on identity A's socket + the unique marker planted for identity B | `cross_user_leak` (`:206-208`): marker B present in **any** frame of A ⇒ message scoped to B leaked to A |
| `webhook_sig_bypassed` | two statuses: a garbage-body **control** delivery, and an unsigned provider-event delivery | `webhook_sig_bypassed` (`:211-215`): unsigned 2xx ∧ control non-2xx ⇒ signature not verified. The control is what makes this sound — an endpoint that 2xx's everything is not a gate |
| `webhook_replayable` | two statuses for the **same** recorded delivery (`_recorded_webhook_body` `:234-242`, so a real provider event, not a fabricated one) | `webhook_replayable` (`:218-220`): both 2xx ⇒ no replay/idempotency protection |
| `sequence_step_auth_bypassed` | status+body of a flow step replayed with **no** session | `step_auth_bypassed` (`:151-154`) → `_ok_with_data` (`:145-148`): 2xx **and** `_body_is_data` **and** not `_is_app_shell` — the FP guard that stops a React app-shell 200 from becoming a finding |

Recorded methods that must be honoured: `exploit_floor:channels` (`channels.py:308, 346, 428`) and `exploit_floor:sequence` (`channels.py:545`).

### E.3 JWT / OAuth / Session

| oracle | INPUT | VERDICT |
|---|---|---|
| `jwt_alg_confusion` | decoded header of the session token **as the browser actually holds it** (read from live storage, not from `auth.json`) | header `alg` is `none`, or a non-RS256 asymmetric `alg` on an RS256-issued token ⇒ signature is not load-bearing |
| `jwt_scope_overgrant` | claim map of the token held by identity A vs identity B | claim set identical across privilege levels ⇒ scope not bound to identity (feeds **OQ-6**, which proves it from the *rendered* app) |
| `session_fixation` | cookie-name set + value observed **before** and **after** the auth transition inside one `/walk` | pre-auth identifier value is re-presented post-auth ⇒ fixation. The walk is what supplies the before/after pair |
| `session_expiry_not_enforced` | per-transition nav statuses inside the walk | `is_session_expired` (`:563`) true at a transition, yet a subsequent privileged observation is still non-empty ⇒ server kept serving the dead session |
| `oauth_pkce_missing` | the authorization request's recorded query/params + whether a `code_challenge` is present | `code_challenge` absent on a `response_type=code` authorization ⇒ PKCE not enforced. Detection reuses `detect_federated_login` (`:587-594`) and `_OAUTH_AUTHORIZE_RX` (`:577`) |

`_sweep_auth_session` is documented as *"fires even for surface no cell claimed"* (`exploit_floor.py:5006-5007`) — **precedent in-tree** for a cell-independent sweep, which is the pattern E.4(a) adopts.

### E.4 The three plumbing fixes

**(a) Make `_sweep_graphql` / `run_channels_sweep` reachable.**

- **`_sweep_graphql` needs NO cell.** It self-skips only on `schema is None or not _fireable(url, None)` (`exploit_floor.py:4766-4768`) — i.e. on **schema detection**, not on applicability. So it is *already* independent of the ledger; it is simply starved because `_stage_graphql` (`:523`) never produced a schema. **Buyer-visible outcome:** a scan against a GraphQL app with introspection enabled starts producing BOLA/BFLA/BOPLA/depth/batching findings with zero ledger change. Remediation is **detection-side**, not ledger-side.
- **`run_channels_sweep` DOES need cells.** `channels.py:451-453` → `claim_family_cells` (`attack_surface.py:129`) → `ledger.service.claim_cells` → the same `applicable = true AND state IN ('untested','testing')` predicate (`service.py:1398-1399`). It therefore cannot be unblocked by any edit to its own body. **Remediation is (4a-2) below, and it is the load-bearing fix.**

**(a-2) `materialize_cells` — adopt the in-tree AI double-gate for the three channel classes.**
*Module:* `src/scanner/ledger/service.py`, immediately above the existing AI gate at `:671`.
```python
# PROPOSAL — mirrors :671 exactly; off => byte-identical
if _flag("SCANNER_LEDGER_CHANNEL_CLASSES") and vc.value in _CHANNEL_CLASSES \
        and element.kind not in _CHANNEL_KINDS:
    continue   # do not MATERIALIZE an impossible cell
```
`_CHANNEL_CLASSES = {GRAPHQL, WEBSOCKET, WEBHOOK}`; `_CHANNEL_KINDS = {"graphql","websocket","webhook"}` (the exact kinds `applicability.py:192/194/196` test for).
*State changed:* cells that would have been `applicable=false, state="na", na_reason="not a … surface"` are **never inserted** — the `na` histogram loses its cross-product noise at the source. Cells on genuinely-matching elements are unaffected (`is_applicable` already returns `(True, None)` for them).
*Buyer-visible outcome:* the coverage ledger stops reporting thousands of never-possible cells as deliberately-scoped, `by_state["na"]` becomes a real scoping signal, and websocket/webhook cells on real surfaces become claimable — which is what revives `run_channels_sweep`.
*Note:* this is strictly better than filtering in `applicability.py`, because an `na` row is a row the buyer has to read and the operator has to explain.

**(b) Fix the `oracle_map` → `nuclei` vocabulary mismatch.**
*Module:* `src/scanner/agent_runtime/oracle_map.py`. Add an explicit override consulted **before** the group lookup, so `GROUP_FOR_CLASS` stays byte-identical:
```python
# PROPOSAL
CLASS_ORACLE: dict[str, str] = {
    VulnClass.GRAPHQL.value:  "graphql-authz",   # -> exploit_floor:graphql-authz
    VulnClass.WEBSOCKET.value: "channels",        # -> exploit_floor:channels
    VulnClass.WEBHOOK.value:   "channels",        # -> exploit_floor:channels
    VulnClass.AI_PROMPT_INJECTION.value:    "airedteam",
    VulnClass.AI_INDIRECT_INJECTION.value:  "airedteam",
    VulnClass.AI_SYSTEM_PROMPT_LEAK.value:   "airedteam",
    VulnClass.AI_TOOL_ABUSE.value:           "airedteam",
    VulnClass.AI_RAG_LEAK.value:             "airedteam",
}
def required_oracle_for(vc):            # :47
    key = vc.value if isinstance(vc, VulnClass) else str(vc)
    override = CLASS_ORACLE.get(key)
    if override: return override
    return PHASE_EXPLOIT_TOOL.get(GROUP_FOR_CLASS.get(key, "config"))
```
**Why substring matching then works** (no `_oracle_fired` change needed): `service.py:151` tests `tool in str(m)`, and `methods_used` holds `exploit_floor:<tool>`:
`'graphql-authz' in 'exploit_floor:graphql-authz'` ✔ · `'channels' in 'exploit_floor:channels'` ✔ · `'airedteam' in 'exploit_floor:airedteam'` ✔.

**Blast radius, stated honestly:** `required_oracle_for` has exactly **two** call sites, both skill-gate paths — `service.py:148` (`_oracle_fired`) and `service.py:221` (`_confirm_state`). `GROUP_FOR_CLASS` is *not* touched, so `father.py:397/414/1270` worker partitioning and `coverage_qa.py:52` family rollups are byte-identical. This is the smallest correct fix available; adding new `_GROUPS` entries instead would have re-partitioned the worker pool.

**Live defect this closes, stated plainly:** `_confirm_state` calls `_oracle_fired(..., skill_gate=True)` with the gate **hard-coded on** (`service.py:224`), independent of `scanner_ledger_skill_gate`. So today a GraphQL/WS/AI finding with no linked evidence row resolves to **`pending_oracle`** (`service.py:226`) rather than `confirmed` — real findings are parked in the review queue by a string comparison that can never match.

**(b-2) Bonus defect found in the same chain — the coverage record cannot land.** `_record_coverage` writes endpoint `f"{url}#{fname}"` (`exploit_floor.py:4815`). `_norm` (`service.py:82-93`) **does not strip a `#` fragment** and `_match` (`:821-843`) resolves only via `by_key`, a `base_fallback` populated **only from cells whose own identity contains `#`** (`:814-816`), or a single-candidate path lookup. A `graphql` element's identity is the bare URL (`inventory_ingest._classify_target` `:436-447` / `_web_kind` `:418-433`), so `host/graphql#field` matches nothing and **the coverage record is silently discarded**. Even with (a-2) and (b) fixed, `methods_used` would stay empty and `_oracle_fired` would still fail. *Fix:* `_record_coverage` must emit the **cell endpoint** (`cell.get("endpoint", url)`, the idiom already used at `exploit_floor.py:2724`, `channels.py:308`) and carry the field name in the evidence path, or `_norm` must strip the fragment before `by_key` lookup. Flag: `SCANNER_LEDGER_FRAGMENT_NORM`, default OFF.

**(c) A distinct `blocked` / `not_attempted` state.**

**`blocked` already exists and must NOT be reused for this.** `service.py:1010-1016` sets `state="blocked"` with a `reason`, and `reporting/service.py:121` counts `blocked` **inside `resolved`** (`resolved = confirmed + tested_clean + blocked`). Reusing it for never-tested cells would silently inflate `resolved_pct` — the exact dishonesty this ledger exists to prevent.

**Design — new state `not_attempted`:**
- *Schema:* **no migration.** `LedgerCell.state` is `Text` with a comment-documented vocabulary (`tenant.py:261-263`) and `table_args` carries only a UniqueConstraint + two Indexes (`:248-252`) — **no CHECK constraint**. A new value is a new string.
- *Semantics:* `applicable = true`, `state = 'not_attempted'`, `attempts = 0`, `na_reason = 'not_attempted: scan ended before this cell was claimed'`. Distinct from `attempted`, which means "claimed ≥1×, never resolved" (`service.py:1461/1493`).
- *Set by:* the existing retire-unreached sweep at `finalize.py:455-464`, which already targets exactly this population. One added predicate:
  ```sql
  -- PROPOSAL, gated on SCANNER_LEDGER_NOT_ATTEMPTED_STATE; off => today's statement verbatim
  SET state = CASE WHEN attempts = 0 THEN 'not_attempted' ELSE 'attempted' END,
      na_reason = COALESCE(na_reason, CASE WHEN attempts = 0
                        THEN 'not_attempted: scan ended before this cell was claimed'
                        ELSE 'attempted: attempt cap reached' END)
  ```
  Reuses the sweep's existing `scanner_finalize_retire_unreached` gate (`finalize.py:454`, default ON at `config.py:451`) as the parent switch — so only the *state label* changes, and only for never-claimed cells.
- *Must also be added to:* `reporting/service.py:110-134` `_coverage` — a **new counter**, deliberately **not** folded into `resolved` and **not** into `open_cells` (`:122`), so `resolved_pct` is untouched but the number is visible. Plus the exit-gate projection at `api/routes/scans.py:605` already serialises `na_reason`, so it needs no change.
- *`na` cells:* these already surface in `by_state["na"]` (`reporting:116`) — they do **not** "disappear". What is missing is that the retire sweep **never stamps them** (`finalize.py:460` filters `applicable=true`), so they carry a bare static reason forever. With (a-2) applied the bulk of them are never created; the remainder should keep `na_reason` as-is and be reported as `na`, **not** as `not_attempted` — `applicable=false` means "out of scope", which is a different and more honest statement than "we didn't get to it".
- *Buyer-visible outcome:* the coverage board distinguishes **"we decided this doesn't apply"** (`na`, with reason) from **"we never looked at this"** (`not_attempted`, counted and surfaced). Today both render as a number with no distinction, and a scan can report high `resolved_pct` while a whole class family was never claimed.

---

## F. FLIP TABLE

| # | Flag | Default | Byte-identical when off? | Blast radius if wrong |
|---|---|---|---|---|
| 1 | `SCANNER_BROWSER_WALK` (sidecar) + `scanner_browser_walk` (settings) | OFF | **Yes** — the route is not registered at all, so the ASGI route table, `/healthz`, and the OpenAPI schema are byte-identical | A bug here can click UI controls on a live target. Mitigated by **S9** (no non-GET form submit without a registered `mutating:true` scenario) + S1/S2 scope aborts + the once-per-scenario re-auth budget. Worst case: an unwanted read-only navigation to an in-scope URL |
| 2 | `SCANNER_BROWSER_WALK_MULTI_IDENTITY` | OFF | **Yes** — single-identity uses the identity store with one label; no context-pool change | Context-pool leak between identities ⇒ a false "authorized" verdict. Bound by `max_wall_s`/`max_steps` and one context per label |
| 3 | `SCANNER_BROWSER_ORACLES` (sidecar) + `scanner_browser_oracles` (ingest) | OFF | **Yes** — `_INSTRUMENT_KIND_MAP` keeps its three entries; `/instrument` writes today's hit dict with no `screenshot`/`har` keys | **Findings-content only.** False-positive client-side findings. Bounded by the existing `executed == True` gate (`browser_ingest.py:228`) — a taint hit can never become a finding |
| 4 | `SCANNER_LEDGER_CHANNEL_CLASSES` | OFF | **Yes** — the `continue` is skipped; every channel cell materializes exactly as today | **Deletes cells.** Wrong `_CHANNEL_KINDS` ⇒ real websocket/webhook/graphql cells never materialize ⇒ genuine coverage loss that reads as clean. Mitigate: dry-run logging the would-be-suppressed count before enabling |
| 5 | `SCANNER_ORACLE_MAP_CLASS_ORACLES` | OFF | **Yes** — `required_oracle_for` falls through to today's group lookup; `GROUP_FOR_CLASS` untouched | **Wrongly blocks or allows closes** for 8 classes only. A wrong value makes `_oracle_fired` permanently `False` ⇒ cells stuck in `testing`, or `False` when it should be `True` ⇒ an unevidenced close. Narrowest-blast fix in the set |
| 6 | `SCANNER_LEDGER_FRAGMENT_NORM` | OFF | **Yes** — `_norm` unchanged; `exploit_floor.py:4815` emits the fragment-form endpoint | `_norm` is used by `_match`/`_probe_ok`/`_match_entry`-style lookups for **every** class. Stripping `#` globally could merge two typed-input cells that legitimately differ after `#`. Prefer the `_record_coverage`-side fix (emit `cell["endpoint"]`) as the default and treat this flag as the fallback |
| 7 | `SCANNER_LEDGER_NOT_ATTEMPTED_STATE` | OFF | **Yes** — the retire statement is today's text verbatim | New state value that no reader knows: a report/replay/UI expecting the documented 9-state vocabulary could KeyError or silently drop it. Must ship `_coverage` support in the same change |

---

## G. EVIDENCE LEDGER — claims about CURRENT behaviour

| Claim | Source (type + location) | Confidence | Notes |
|---|---|---|---|
| `browser_server.py` has exactly three routes: `/healthz`, `/crawl`, `/instrument` | [CODE] `docker/browser/browser_server.py:732,737,1032`; module contains no other `@app.` decorator | **HIGH** | Read the whole file (1,156 lines) |
| `/healthz` is liveness only | [CODE] `browser_server.py:732-734` | **HIGH** | Returns `{"status":"ok"}` |
| `CrawlRequest` = `url + max_pages + max_depth`; no action/selector/assertion field | [CODE] `browser_server.py:715-718` | **HIGH** | |
| `InstrumentRequest` = `urls + canaries` only | [CODE] `browser_server.py:1020-1023` | **HIGH** | |
| `/instrument` performs ONE `goto` per URL and closes the page | [CODE] `browser_server.py:1102` (single `goto`), `:1136` (`page.close()` in `finally`) | **HIGH** | |
| navigate→act→re-navigate→assert is structurally impossible today | [CODE] absence of any action field in both request models (`:715-718`, `:1020-1023`) + fixed three-source plant `:1096-1111` | **HIGH** | Mechanism, not inference: there is no code path from the request body to a second navigation |
| `/crawl` is single-seed BFS with opportunistic credential login | [CODE] `browser_server.py:787` queue init, `:859-871` BFS loop, `:908-909` `_try_login` | **HIGH** | |
| Login is hard-coded to operator env creds, not caller-supplied | [CODE] `browser_server.py:855` `_login_cred(_credentials())`; `_credentials()` reads `SCAN_CREDENTIALS` env (`:84-89`); `CrawlRequest` has no credential field | **HIGH** | |
| The scope gate is at `:821-840` and `:1071-1084` — **not** `:1176-1183` as stated in the brief | [CODE] `browser_server.py:821-840`, `:1071-1084` | **HIGH** | The brief's cite exceeds the file's 1,156 lines. The gate content is exactly as described (document-nav abort + in-scope-only creds + `sso_allows_nav`) |
| The HAR-slice-per-finding gap and screenshot streaming already exist | [CODE] `browser_ingest.py:381-436`, `:178-202`, `:55`; `api/routes/scans.py:867-877` | **HIGH** | Confirms the brief's "do not overstate the gap" |
| The live-capture deferred TODO is verbatim at `:397-399` | [CODE] `browser_ingest.py:397-399` | **HIGH** | Quoted exactly: *"TODO (live-capture seam, deferred): DOM/stored-XSS pop screenshot at the /instrument hit, and the function-level-authz admin response rendered under a low-priv session — both need a live browser round-trip the engine triggers, not an offline HAR slice."* |
| Offline HAR matcher keys on `(endpoint, method, vuln_class)` | [CODE] `browser_ingest.py:184-191` (class check + `_method_of`), `_match_entry` `:146-156` | **HIGH** | |
| `/instrument` records **no** HAR today | [CODE] `browser_server.py:1065` `new_context(ignore_https_errors=True)` — no `record_har_path`, unlike `:803-805` | **HIGH** | New finding; load-bearing for OQ-1/OQ-2 artifacts |
| `EvidenceObject` already has `screenshot`, `har`, `oob_token`, `replay`, `control_request`, `confidence` | [CODE] `db/models/tenant.py:237-241` | **HIGH** | ⇒ Deliverable 3 needs **no migration** |
| The capsule builder already reads screenshot/har/oob_token | [CODE] `finalize.py:612` `for k in ("method","tool","screenshot","har","oob_token")` | **HIGH** | |
| Model can only reach `/crawl`; `/instrument` is a one-shot fallback that self-skips | [CODE] `engine/tools/browser.py:65-69` (posts `{url,max_pages}` to `/crawl`); `browser_fallback.py:174-175` (`if any(bdir.glob("instrument_*.json")): return 0`) | **HIGH** | |
| Gallery is scan-level and explicitly not finding-linked | [CODE] `browser_ingest.py:311-315`, `:352` (`kind="recon"`, no `finding_id`) | **HIGH** | |
| GraphQL oracles exist and are schema/introspection-driven | [CODE] `engine/graphql_authz.py:85,201,242,268,294,310,321,333,338`; `exploit_floor.py:4766-4768` (`schema is None` → return, no cell consulted) | **HIGH** | |
| `run_channels_sweep` is **cell-driven**, contradicting the brief | [CODE] `engine/channels.py:451-453` `claim_family_cells(vuln_classes=[WEBSOCKET,WEBHOOK])`; `attack_surface.py:129` → `ledger.service.claim_cells` | **HIGH** | **Brief correction.** It is strictly downstream of the applicability defect |
| `claim_family_cells` inherits the `applicable = true` filter | [CODE] `attack_surface.py:129` → `ledger/service.py:1393-1417`, predicate at `:1398-1399` | **HIGH** | |
| Channels is a claiming family, not a schema-driven sweep | [CODE] `engine/channels.py:440-443` docstring (*"Claiming family … Claims its own next batch via `surface.claim_family_cells`"*) | **HIGH** | |
| AI classes are already double-gated at materialize (the in-tree precedent) | [CODE] `ledger/service.py:671` `if vc.value in _AI_CLASSES and not (ai_on and element.kind == "ai_endpoint"): continue` | **HIGH** | The exact pattern proposed in E.4(a-2) |
| Every vuln class is materialized on every element, then applicability-filtered | [CODE] `ledger/service.py:670` `for vc in VulnClass:`, `:679` `is_applicable(...)`, `:688` `state="untested" if applicable else "na"` | **HIGH** | **Root cause of the `na` histogram** |
| The `na` histogram is therefore a cross-product artefact | [CODE] `service.py:670` × `applicability.py:193-194` (`kind == "websocket"` else `"not a websocket surface"`) | **HIGH** | A `url` element provably spawns a `websocket` cell that is immediately killed |
| The brief's numeric `na` histogram (1,203 / 1,195 / 1,163) and the "0 `channels.*` log lines" claim | inherited from the WS-1/2/3 brief; **could not be re-verified** — the Docker daemon is down (`docker ps` → `npipe://…dockerDesktopLinuxEngine: cannot find the file specified`), so no SELECT and no `docker logs` was possible | **UNVERIFIED** | The *mechanism* producing these numbers is confirmed at HIGH above. The counts themselves are taken on trust. **Discriminator for `channels.*`:** if `channels.complete cells=0` is present, the claim ran and found no cells (⇒ applicability defect); if absent, the family self-disabled at `channels.py:445-446` (`surface is None or not hasattr(surface,"claim_family_cells")`), which returns **before any log** |
| `graphql=0`, `ai_endpoints=0` in at least one archived scan | [QUERY] `improvment-research/research-agent-falcon-02/ws2_telemetry/raw/a03_logtax.out:72` — `recon_floor.complete ai_endpoints=0 … graphql=0 … live_urls=1` | **HIGH** | Read from an archived log dump (read-only). Explains why `_sweep_graphql` self-skipped: no schema was ever indexed. `counts` keys at `recon_floor.py:437,523,533` |
| `oracle_map` has no entry for graphql/websocket/webhook/ai_*, so all resolve to `nuclei` | [CODE] `oracle_map.py:21-39` (`_GROUPS`), `:44` (`GROUP_FOR_CLASS` built only from `_GROUPS`), `:52` (`.get(key,"config")`), `:17` (`"config": "nuclei"`) | **HIGH** | |
| `_oracle_fired` substring-matches the tool name in `methods_used` | [CODE] `ledger/service.py:151` `any(tool in str(m) for m in methods)` | **HIGH** | |
| Recorded method strings are `exploit_floor:<tool>` | [CODE] `exploit_floor.py:2365-2377` (`"methods": [f"exploit_floor:{tool}"]`); tool strings `"graphql-authz"` (`:4815` and 8 more), `"channels"` (`channels.py:308,346,428`), `"airedteam"` (`exploit_floor.py:262-264`) | **HIGH** | The overlap needed for the fix |
| A fired exploit-floor oracle still cannot close a cell while the vocabulary is wrong | [CODE] `ledger/service.py:980` (`weapon_swept`) → `:988` (`desired="tested_clean"`) → `:995-997` (`redundant and _probe_ok and oracle_ok`) — `oracle_ok` False ⇒ `counts["unverified"]`, cell left `testing` (`:1004`) | **HIGH** | `weapon_swept` does **not** bypass `_oracle_fired` |
| Real GraphQL/WS/AI findings are demoted to `pending_oracle` by the same mismatch | [CODE] `ledger/service.py:224` `_oracle_fired(…, skill_gate=True)` — gate **hard-coded on**, independent of `scanner_ledger_skill_gate` (`config.py:209`); `:226` returns `"pending_oracle"` | **HIGH** | New; buyer-visible (findings parked in review) |
| `_confirm_state`'s only two `required_oracle_for` consumers are skill-gate paths | [CODE] `ledger/service.py:148` and `:221`; import at `:42` | **HIGH** | Bounds the blast radius of the oracle_map fix |
| `GROUP_FOR_CLASS` is also consumed by worker partitioning | [CODE] `father.py:397,414,1270`, `coverage_qa.py:52` | **HIGH** | Justifies the override-table shape instead of new `_GROUPS` |
| `_norm` does not strip a `#` fragment, so `{url}#{field}` cannot match a bare-URL cell | [CODE] `ledger/service.py:82-93` (no fragment strip), `base_fallback` populated only from `#`-bearing identities (`:814-816`), `_match` `:821-843`; emitter `exploit_floor.py:4815` | **HIGH** | New; a second independent break in the GraphQL chain |
| Element identity for a GraphQL/WS endpoint is the bare URL | [CODE] `inventory_ingest.py:418-433` `_web_kind`, `:436-447` `_classify_target` (`identity=t`) | **HIGH** | |
| `na` cells are never stamped by the retire sweep | [CODE] `finalize.py:460` `WHERE scan_id=:s AND applicable=true` | **HIGH** | New |
| `blocked` already exists and counts inside `resolved` | [CODE] `ledger/service.py:1010-1016`; `reporting/service.py:121` `resolved = confirmed + tested_clean + blocked` | **HIGH** | ⇒ do **not** reuse `blocked` for never-tested |
| `state` is unconstrained `Text` — a new state value needs no migration | [CODE] `db/models/tenant.py:248-252` (`table_args` = UniqueConstraint + 2 Indexes only), `:261-263` (`state: Mapped[str]`, vocabulary in a comment) | **HIGH** | |
| `attempted` already means "claimed, never resolved" | [CODE] `ledger/service.py:1461`, `:1493` (`'attempted: attempt cap reached'`) | **HIGH** | Distinguishes it from the proposed `not_attempted` |
| Channel-oracle verdicts are transport-agnostic and FP-guarded | [CODE] `channels.py:145-148` `_ok_with_data` (2xx + `_body_is_data` + not `_is_app_shell`), `:200-203`, `:206-208`, `:211-215`, `:218-220` | **HIGH** | |
| GraphQL verdicts are pure and conservative by construction | [CODE] `graphql_authz.py:195-198` `_objects_match` (≥2 fields, byte-equal), `:201-223`, `:242-256`, `:268-280`, `:333-343` | **HIGH** | |
| Browser has exactly one context with `creds[0]`-derived headers (no identity model) | [CODE] `browser_server.py:803-805` (one `new_context`), `:810` (`cred_headers`), `_scoped_cred_headers` `:477-493` (`c = creds[0]`) | **HIGH** | Basis for Deliverable 1 §B.3 |
| Session plant / expiry / SSO primitives already exist and are pure | [CODE] `browser_server.py:526-536` `_auth_session`, `:539-555` `build_session_init_script`, `:523` `_TOKEN_STORAGE_KEYS`, `:560-572` `is_session_expired`/`should_crawl_reauth`, `:587-608` `detect_federated_login`/`sso_state`, `:615-619` `sso_allows_nav` | **HIGH** | Deliverable 1 reuses all of them |
| `_try_login` refuses to submit a non-password-bearing form (the "no transfer/purchase" invariant) | [CODE] `browser_server.py:679-680` (docstring), `:682`, `:703`, `:705-706` | **HIGH** | Basis for S9 |
| GraphQL/WS/AI flags default OFF in config | [CODE] `config.py:293` `scanner_graphql_authz_enabled: bool = False`, `:302` `scanner_channel_oracles_enabled`, `:312` `scanner_ai_redteam_floor` | **HIGH** | The brief's "live flags ALL ON" is a *deployment* state, not the code default — consistent |
| Browser walk-related flags default OFF | [CODE] `config.py:338-340` `scanner_browser_authed_crawl`, `scanner_browser_reauth`, `scanner_sso_login` — all `False`; sidecar `_flag()` `:72-74` treats absent as off | **HIGH** | |
| `_sweep_auth_session` is precedent for a cell-independent sweep | [CODE] `exploit_floor.py:5006-5007` *"fires even for surface no cell claimed"* | **HIGH** | |
| R1 compliance: no payload, command, selector-as-attack-step, or exploit sequence appears in this design | self-audit of §B–§E against R1 | **HIGH** | Oracle INPUT/VERDICT are specified as *observed signals* and *boolean conditions* over already-written verdict functions; the `/walk` request carries a scenario **name**, and `act` addresses controls by ARIA role + accessible name |
| HEAD is `f75608f` on `feat/alpha-observability`; no repo file modified | [QUERY] `git rev-parse --abbrev-ref HEAD` → `feat/alpha-observability`; `git rev-parse --short HEAD` → `f75608f` | **HIGH** | Sole write: this file, under the assigned write root |
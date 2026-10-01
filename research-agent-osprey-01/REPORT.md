# Abhedi Red — Architecture Audit & Design
**Agent:** research-agent-osprey-01 · **Mode:** read-only research · **Branch audited:** `feat/alpha-observability` @ HEAD `f75608f` (directive said `1c5551d`; actual HEAD is 3 commits ahead — code wins, R2) · **Date:** 2026-09-30/10-01 UTC

Sources actually available: **A** (local code), **B** (`competitor-research/`), **C** (live server `ssh abhedi`, read-only: workdir volume, Postgres `tenant_xbow`, `docker logs`, deepdive artifacts), **D** (not needed; all public claims came from B). No source was missing.

---

## 1. Executive summary

1. **Scans are dominated by unbounded stateful worker turn-windows, not by "coverage takes time."** Every one of the 86 recorded model windows in the live scan exited via `max_turns_exceeded` (40-turn cap), and each window replays the prior transcript; workers loop up to 7 windows (`agents_runtime.py:798-838`). With `SCANNER_ENGINE_POOL_HARD_CAP=4` and worker spans of 116–2,961 s across 1–7 windows, wave length ≈ (batches ÷ 4) × per-worker time. Wave 1 of the live scan passed **105 minutes** and was still running.
2. **The deterministic exploit floor tests breadth but leaves its claims open by design**: its coverage record writes `state="testing"` (`exploit_floor.py:2365-2380`) and a pending signal blocks its own close (`ledger/service.py:984-989`). Result: 1,600+ floor-owned cells sit in `testing`, absorbed only by lease expiry (1,800 s) + the attempt cap 6 — up to ~3 h of tail per cell.
3. **Coverage honesty leaks are material**: over one 2 h 40 m scan, `ledger.resolve.update_unmatched` fired **522** times and `finding_unmatched` **362** times. Worker-tested endpoints silently fail to land on their cells; the reconcile census tracks this but nothing stops it.
4. **67.6% of the grid is `na`** (6,247/9,237) and only **19 cells are `confirmed`** while **42 findings** exist — the coverage and findings graphs measure different things and neither converges quickly.
5. **The boss planner is ON in production but inert in practice**: 0 `plan.revised` events, no `plan.json` on disk, no failure telemetry. The built "LLM proposes, ledger disposes" layer is silent-failing.
6. **Chain synthesis is graph-only**: `chain_node.attrs` stores a truncated PoC + evidence path, but no consumer carries a proof artifact into hop N+1 (`chain/floor.py:407-441` re-fires from `findings.jsonl` + global `/work/auth.json`). No credential stuffer, no replay contract (`chain/floor.py:385-390`).
7. **Browser capability stops at deterministic BFS crawl + DOM-XSS instrumentation**; no worker-driven click/fill/eval, no cross-request session, single-identity only; `/instrument` never logs in and never plants storage (`browser_server.py:1063-1084`).
8. **Oracle coverage is binary by class**: ~30 classes have deterministic oracles (many flag-gated OFF), 12 have none; the A1 verifier is an LLM agent (12-turn budget) that failed **146** times in the live scan.

---

## 2. Hypothesis verdicts

### H1 — "Slow scans primarily from claim/release mismatch + wave sync overhead" → **PARTIAL**
- The mismatch was real and is fixed on the batch path: cells claim under `wave{N}` but batch workers get `batch{N}-…` ids; releasing by worker id matches 0 rows — release-by-ids was added (`father.py:774-776`, `ledger/service.py:1476-1505`). The **legacy `run_all` path still never releases**: wave-claimed cells wait out the lease (`father.py:1898-1901`).
- Quiescence does NOT fail open: `_has_claimable` fails **closed** (`father.py:1428-1441`), so "ends loops early" is **REFUTED** for current code.
- The 90-min wall does NOT dominate: production sets `SCANNER_ENGINE_WORKER_WALL_S=86400`, `SCANNER_ENGINE_MAX_WAVES=1000` (live env). The wall is a 24 h backstop, not a schedule.
- What does dominate: (a) 4-slot pool × stateful turn windows; (b) floor claims held in `testing` + lease/attempt absorption; (c) silent coverage discard; (d) concurrent sync/verify/report regeneration (`SCANNER_ENGINE_SYNC_INTERVAL_S=120`, `REPORT_MIN_INTERVAL_S=60`, 146 failed verifies).
- **Blast radius:** scan time (hours), operator trust, cost (report regen + failed verifies), scheduling.

### H2 — "Workers spin up with near-identical static prompts; a dynamic decision layer would help" → **PARTIAL**
- Initial tasks are static per phase-group but include the live brief (18,100 B), coverage board, claimed worklist, and plan digest when present (`father.py:597-675`). Reprompts are state-aware: missing-weapon list, phase WEAPONIZE text, live progress digest (`agents_runtime.py:962-1021`). So "near-identical static" is too strong for the continuation prompts.
- However there is no per-tick next-best-action from live state: the boss plan would provide it, but it is **inert** (0 plans accepted). The digest is informational, not directive. Workers exhausted windows on the same ~48 claimed cells/wave while 2,000+ cells stayed open.
- **Blast radius:** wasted model turns, coverage starvation.

### H3 — "Chain synthesis is graph-only; no proof artifact carried hop N → N+1" → **CONFIRMED**
- Node carries `proof_of_concept[:4000]` + `evidence_path` in attrs (`chain/service.py:167-174`), but the next hop never reads it: `run_chain_floor` re-reads `findings.jsonl`, recovers `(url,param)`, and uses the **global** identity from `/work/auth.json` (`chain/floor.py:407-441`, `422`). The escalation prompt names only capability + title + endpoint (`father.py:1520-1548`).
- No chain-scoped session/credential store; credential re-use explicitly declined (`chain/floor.py:385-390`).
- Chains persist as `chain_node`/`chain_edge` (live: 42 nodes / 60 edges for the running scan); `synthesize_chains` returns label paths (`chain/service.py:325-346`).
- **Blast radius:** buyer-visible "attack story" is narrative-only; deep-impact proofs rely on the model re-deriving session reuse.

### H4 — "Client-side stops at DOM-XSS instrumentation; no multi-step SPA state-change" → **CONFIRMED**
- `/crawl` = deterministic BFS (queue at `browser_server.py:787,859-955`); `/instrument` = fixed snippets only (goto + postMessage + PP scan, `browser_server.py:1086-1136`). The agent's only browser tool is `browse(url, max_pages)` (`engine/tools/browser.py:52`, `agents_runtime.py:253`). No click/fill/eval API exists.
- `/instrument` has no session planting and no login: `build_session_init_script` is called only in `/crawl` and only under `SCANNER_BROWSER_AUTHED_CRAWL` (default false, `config.py:338`); instrument relies on header replay (`browser_server.py:1063-1084`).
- Single identity: first credential only; `auth.json` user_a/user_b/admin/tenant_b blocks are ignored by the sidecar (`browser_server.py:469-493, 526-536`).
- Real-execution canary oracle for DOM XSS/PP is genuine (`browser_server.py:335-409`; ingest drops `executed:false`, `browser_ingest.py:228-229`).
- **Blast radius:** SPA/post-login/click-gated bugs unprovable in-browser; BOLA/BFLA on rendered surfaces must come from HAR slices that omit response bodies (`record_har_content="omit"`, `browser_server.py:798-805`).

### H5 — "New-tech VAPT declared in taxonomy but lacks deterministic oracles" → **PARTIAL**
- Taxonomy declares 62 classes (`taxonomy.py:19-93`). Deterministic verdicts exist for ~30 (SQLi boolean/time/sqlmap, OOB blind family, XSS reflected/stored/dalfox, SSRF/LFI/RFI/redirect, deser, upload, JWT/session/oauth/crlf/smuggling (gated), IDOR/BFLA/auth-bypass differentials, GraphQL authz (gated), WS/webhook (gated), AI redteam (gated), rate-limit, CORS/CSRF/headers/host-header/debug/protocol).
- **No deterministic verdict** for 12 classes: `ldap`, `xpath`, `ssi`, `priv_esc`, `cache_poisoning` (coverage-only by design), `price_tamper`, `race_condition`, `mass_assignment`, `quota_abuse`, `missing_email_auth`, `weak_cipher`, `cert` (full per-class table: `evidence/oracle_coverage_table.md`). `prototype_pollution` does have a deterministic browser oracle (`browser_server.py:434-445, 1112-1117`).
- Critical gated-off by default: GraphQL authz (`scanner_graphql_authz_enabled`), channels WS/webhook (`scanner_channel_oracles_enabled`), AI/MCP floor (`scanner_ai_redteam_floor`), session/JWT/OAuth/crlf/smuggling (`scanner_auth_oracles_enabled`), upload sweep. Live env turns several ON (`SCANNER_AUTH_ORACLES_ENABLED=true`, `SCANNER_DESER_RCE_CONFIRM_ENABLED=true`), but GraphQL/channels/AI remain default-OFF.
- **Blast radius:** cells can only close as `attempted` (honest "tried, unresolved") or via LLM prose.

### H6 — "Worker environment under-specified → context bloat and duplicated work" → **CONFIRMED**
- Worker system prompt = static methodology + OOB block (`agents_runtime.py:917-940`); task = brief (18.1 KB) + up to 9,000 B skills + triage + worklist (`father.py:597-633`, `_SKILL_BLOCK_CHARS` at `:183`). Each of ≤7 windows replays the transcript, head-capped at 4,000 B per tool output (`agents_runtime.py:205-235, 988-993`).
- Token/cost telemetry is **blind exactly where it matters**: on the MaxTurns path `_record_turn` writes 0 tokens (`agents_runtime.py:440-445`); all 74 `agent_messages` rows for the live scan are 0/0. `worker.finished` payloads always show `resolved_cells: 0` (never populated).
- 70 skills are mounted (`/skills`) but only a per-group bundle reaches the worker; the rest are pull-only via read_file. Workers wrote ~50 ad-hoc scripts into `/work` (live listing) — no structured scratch contract.
- Shared coordination artifacts are one global file each (`findings.jsonl`, `ledger_updates.jsonl`, `exploit_floor_signals.jsonl`), with no partitioning/ownership: the 1,157-line signal backlog is re-offered wholesale to every worker (`_signal_triage_directive`, `father.py:327-348`), and 3 concurrent workers claim disjoint cells but share one triage queue.
- **Blast radius:** cost, latency, duplicated triage, unmeasurable progress.

*Ledger for §2: see §10 rows H1-a…H6-e.*

---

## 3. Root-cause diagnosis: why scans are slow and proofs are shallow

### 3.1 Time attribution — live scan `84aea81a` (target `http://172.17.0.1:9090/VulnerableApp/`)

| Phase / segment | Wall | Evidence |
|---|---|---|
| Scan start → recon done | **213.8 s** | `scan_phases` (reconnaissance 20:08:50→20:12:24) |
| Auth bootstrap worker (inside recon) | 180 s | `worker_runs` auth-bootstrap 20:09:24→20:12:24 |
| Wave 0 fleet (11 batch workers, pool ≤4) | **1,657 s** | worker_runs 20:13:13→20:40:50 |
| Authed re-crawl | 130 s | worker_runs 20:40:51→20:43:01 |
| Escalation wave (4 phase workers) | **1,167 s** | worker_runs 20:43:02→21:02:29 |
| Wave 1 fleet (24 batches at capture) | **>6,300 s (running)** | worker_runs 21:02:54→ capture 22:48 |
| Total at capture | **2 h 40 m, still `running`** | `scans` row |

Time sinks, in order of measured impact:

1. **Pool width × window latency.** `SCANNER_ENGINE_POOL_HARD_CAP=4`; wave 1 = 24 batches through 4 slots; per-batch p50 ≈ 700 s, max 2,961 s (batch1-b-7). At 4-wide, that is ~8–10 serialized rounds ≈ 1.5–2 h per wave. Statements: `fleet.py:124-161` (rolling pool), `father.py:1364-1416` (batch path), live `worker_runs`.
2. **MaxTurns windows as the normal exit.** 86/86 sampled `decisions.log` lines are `max_turns_exceeded`; 40 turns/window, ≤6 reprompts (`agents_runtime.py:326-331, 798-838`), each reprompt re-sends prior history (capped per item, not total, `:221-235`).
3. **Floor claim stickiness.** `_run_family` claims 20 cells per family per drain batch (`exploit_floor.py:106, 4890`) and records `testing` (`:2365-2380`); a pending signal zeroes `weapon_swept` and blocks the close (`ledger/service.py:980-989`). Floor-owned testing at capture: blind 528, access 394, logic 330, clientside 196, upload 71, nofamily 40, ratelimit 34, injection 16. Lease 1,800 s (`SCANNER_LEDGER_LEASE_S`); absorbed only after attempts ≥ 6 (`:1237-1247, 1444-1505`).
4. **Silent coverage discard.** 522 `update_unmatched` + 362 `finding_unmatched` warnings in the agent log for this scan. Workers test real URLs (`…/LEVEL_2?id=`) that do not match malformed/templated inventory identities (`…/LEVEL_$l#value`, `…/vectors/`, `…?ipad`). Those cells stay open and keep the quiescence gate `True` (`father.py:1851`), while the work is lost.
5. **Concurrent convergence load.** Sync tick every 120 s runs ingest + resolve + dedup (`father.py:888-967`); `_live_convergence` adds LLM verify (2 concurrent) + enrich + chain rebuild + **report regeneration every 60 s up to 50 times** (`SCANNER_ENGINE_REPORT_MIN_INTERVAL_S=60`, `MAX_REPORT_REGENS=50`; `father.py:969-1075`). 146 `verification.failed` (Max turns 12 exceeded) in the live log; report.md was regenerated repeatedly (mtime 22:04, 1.5 MB report).
6. **Finalize tail.** Prior completed scans show finalize running long: 1f5fe7c8 `finalize` phase open 37,251 s (10.3 h) with status `completed`; the poller log for a smaller scan shows ~4 min of enrich/verify after kill.

### 3.2 WS-1 ranked defects (by blast radius)

1. **Stateful unbounded turn windows** (throughput, cost): 86/86 windows maxed; replay grows each window. Evidence H1-e/H6-a.
2. **Floor `testing` stickiness + lease/attempt absorption** (throughput tail): 1,609 floor-owned testing cells; 30-min lease × cap 6. Evidence H1-f.
3. **Silent coverage discard (`update_unmatched`/`finding_unmatched`)** (proof honesty): 522 + 362 per scan. Evidence H1-g.
4. **Planner inert** (strategy): 0 accepted plans. Evidence H2-b.
5. **Verifier failure loop + report regeneration** (cost/contended DB): 146 failures; report rebuilt up to 50×. Evidence H5-c/H1-h.
6. **Worker progress telemetry blind** (operability): 0 tokens recorded, `resolved_cells` always 0. Evidence H6-a/b.
7. **Claim/release mismatch remnant** (legacy path only): lease-only recovery when batch dispatch is off. Evidence H1-a.
8. **Quiescence fail-open claim** (hypothesis): refuted — code fails closed. Evidence H1-b.

### 3.3 WS-2 observed-failure catalog (aggregate counts only; live scan 84aea81a)

| Failure mode | Count | Evidence |
|---|---|---|
| Worker windows ending in `max_turns_exceeded` | 86 / 86 (100%) | decisions.log |
| Coverage records discarded (`update_unmatched`) | 522 | agent log |
| Findings discarded (`finding_unmatched`) | 362 | agent log |
| LLM verification failures (`Max turns (12) exceeded`) | 146 | agent log |
| Agent message rows with zero token accounting | 100% (74/74) | agent_messages |
| `worker.finished` with `resolved_cells=0` | 100% | scan_events |
| Floor sweeps producing a signal (wave 1) | 930 / 1,173 cells (79%) | floor.tick |
| Signal backlog lines at capture | 1,157 | exploit_floor_signals.jsonl |
| Cells reaching `attempted` (completed scans) | 853–1,516 per scan | ledger snapshots |
| Boss plan revisions | 0 | scan_events / workdir |

### 3.4 Why proofs are shallow

- The intended honesty rule is: `tested_clean` requires ≥2 methods + evidence + a fired class oracle + a real invocation (`ledger/service.py:991-1009`); `confirmed` needs evidence or a fired oracle (`:205-222`). The floor can supply only ONE method, so it never closes; workers often record coverage that never matches; the verifier is an LLM with a 12-turn budget that fails often. The strictness is correct — the **funnel is what's broken**: work is discarded rather than routed, and `attempted` is the only escape.
- Chain impact is label-only (H3), so the report can show a plausible path but cannot replay each hop's proof.
- Browser proofs exist only for DOM-XSS execution and crawl-derived HAR metadata; HAR bodies are omitted, so post-login/BOLA "proof slices" are usually status+headers (WS-6 evidence).

---

## 4. Core-architecture improvements (ranked by blast radius)

All default-OFF, byte-identical when off (D4).

| # | Fix | Module / flag | Buyer-visible outcome |
|---|---|---|---|
| 1 | **Terminal `probed` state + method ledger.** Give the floor's single-method `testing` record a claimable terminal state (`probed`, distinct from `tested_clean`) once per cell; stop re-claiming probed cells except on new capability/reopen. | `ledger/service.py` (`resolve_cells`, `claim_cells`, `count_claimable_cells`), `exploit_floor._record_coverage`; flag `SCANNER_LEDGER_PROBED_TERMINAL` | Coverage completes in one lease cycle instead of 4–6; honest "probed, no impact found" counts reach the report. |
| 2 | **Release floor claims at sweep end** (release-by-ids from `_run_family`) and size the lease from per-cell test p95, not the 24 h wall. | `exploit_floor.run_exploit_floor`, `ledger/service._DEFAULT_LEASE_S`; flag `SCANNER_FLOOR_RELEASE=1` | Kills the 30-min sticky tail; a wave's cells are immediately re-claimable by workers. |
| 3 | **Identity canonicalization + alias table.** Normalize templated/truncated identities (`$l`, `$lv`, trailing `?param`, `#field`) to a canonical key; maintain an alias index used by `_match`. Surface `resolve_unmatched` per tick as a first-class KPI. | `ledger/service._norm/_match`, `inventory_ingest.py`; flag `SCANNER_LEDGER_ALIAS_V2` | Work lands; coverage funnel becomes measurable; 522 unmatched/tick → near-zero. |
| 4 | **Window telemetry + budgets.** Emit per-window `max_turns`, tokens, elapsed, tool count; add a per-window soft deadline and a total-worker deadline distinct from the wall; record usage even on the exception path if the SDK exposes usage. | `agents_runtime._record_turn/run`; flag `SCANNER_ENGINE_WINDOW_TELEMETRY` | Cost/latency visible; per-worker cost capped by design, not by the 24 h wall. |
| 5 | **Triage queue partitioning.** Assign each signal to exactly one batch worker (or a dedicated triage role), with an ownership column + completion marker; make the directive list only that worker's slice. | `father._signal_triage_directive`, `exploit_floor._signal` (add `owner`/`ts`), `SCANNER_SIGNAL_OWNERSHIP=1` | 1,157-signal backlog drained deterministically instead of re-read by every worker. |
| 6 | **Planner fail-loud.** Emit `plan.tick` events (candidate, rejection reasons, latency); count parse failures; add a boss canary test that asserts one accepted plan on a fixture. | `boss.propose_plan`, `father._boss_tick`; flag `SCANNER_ENGINE_BOSS_TELEMETRY` | The intelligence layer is auditable; "OFF" and "broken" become distinguishable. |
| 7 | **Verification routing v2.** Default deterministic-oracle findings to the detached content-marker path; give the LLM verifier a state transcript + higher turn budget for logic classes only; emit verdict counters. | `finalize._verify_findings`, `verify.py`, `detached_verify.py`; flag `SCANNER_VERIFY_ROUTING_V2` | Fewer false `pending`, verifier cost bounded, proof status honest. |
| 8 | **Per-scan coverage funnel metric** (`na → untested → probed → tested_clean → confirmed`, unmatched counts, signal backlog) written to `coverage_quality.json` and the report. | `coverage_qa.py`, `reporting/service.py` | Buyers see tested-vs-proved honestly; regression signals surface. |

---

## 5. Feature add-ons (ranked by buyer-visible proof value)

1. **Proof-carrying chain receipts (WS-4)** — turns "chains" from a graph into replayable attack stories with per-hop oracle verdicts. Highest commercial value; also fixes H3.
2. **Browser Act API + multi-identity sessions (WS-6)** — unlocks SPA/business-logic proofs and rendered-surface BOLA/BFLA. Complements the already-live differential oracles.
3. **Flip gated new-tech oracles (GraphQL authz, channels, AI/MCP) behind a canary flag, then default-on** — they already exist; the gap is deployment, not design.
4. **Operator playbook directives that the engine verifies** — phase objectives become measurable exit criteria (see WS-5), closing the loop between sold methodology and execution.
5. **Third-party-verifiable benchmark output** — the market gap identified in WS-3; emit reproducible per-scan proof bundles (hashes, oracle transcripts) that a buyer can re-run.

---

## 6. WS-4 — Chain state machine + intelligence layer design

### 6.1 Chain state machine (design only; capability labels, no payloads)

```
FINDING(confirmed, oracle=O) ──▶ CAP_SUGGESTED(cap, source_finding, proof_ref)
CAP_SUGGESTED ──(ChainExecutor validates: scope + in-scope param + oracle availability)──▶
CAP_GRANTED(run_id, cap, ttl, source_finding, artifact_ref)
CAP_GRANTED ──(hop N executes through the SAME sink; oracle fires)──▶
HOP_RECEIPT(hop_id, parent_hop, oracle_type, verdict, artifact_ref, replay_ref)
HOP_RECEIPT ──(new finding confirmed)──▶ FINDING′ ──▶ capability deltas ──▶ CAP_GRANTED′
CAP_GRANTED/HOP_RECEIPT ──(no proof within budget)──▶ CAP_EXPIRED(reason)  # never resurrected
```
- **Capability token:** `{run_id, scan_id, cap, source_finding_id, proof_ref, scope_binding, ttl, single_use}` persisted in a new `chain_context` row (or `chain_node.attrs` while a table is overkill). Tokens are opaque handles — **no raw secrets in the DB**.
- **Persistence & hop receipt:** every hop writes a `ChainHopReceipt` (oracle type, verdict enum, artifact ref/hash, replay instructions handle). The receipt is the only thing the next hop receives — not a label.
- **Replay contract:** a receipt must be replayable by the verifier using stored artifacts (evidence object id + redacted request template). Where a credential/session is the artifact, store an encrypted handle in `/work` (same trust domain as `auth.json`); the report renders a redacted placeholder.
- **Proof-type enum:** `OOB_CALLBACK | DIFFERENTIAL_REPLAY | EXECUTION_INSTRUMENTATION | CONTENT_MARKER | CREDENTIAL_PROOF | STATE_CHANGE | PARSER_ACCEPT | REPLAY_IDEMPOTENT`.
- **Report narrative schema:** an ordered `story[]` where each item = `{finding_id, capability, oracle, receipt_id, buyer_text}`; invariant: every hop has a receipt, and the chain is only shown if all receipts verified. "We found X (receipt), which proved Y (receipt), which enabled Z (receipt)."
- **Example hops as capability labels:** `SSRF → INTERNAL_HTTP → METADATA_ACCESS → CREDENTIAL → SESSION → CROSS_PRINCIPAL_READ`; `FILE_READ → SECRET_DISCOVERY → CREDENTIAL → SESSION`; `REDIRECT → SSRF`. No payloads, per R1.

### 6.2 Intelligence / decision layer (WS-5)

The pieces already exist and are well-factored; the design is to make them **observable, backed by the full grid, and enforced**:

- **Planner contract (bounded):** input = capped brief + board + coverage QA + prior plan + policy (`boss.build_boss_prompt`, `boss.py:108-130`); output = `{objectives[], abandoned[], target_profile}` (`boss.py:33-43`); bounded by max_turns 8 + 180 s wall (`boss.py:46-51`); read-only tools only (`boss.py:76`).
- **Deterministic gate (exists):** `plan_gate.validate_plan` merges by id, rejects no-class/out-of-scope/no-surface, caps active at 10 (`plan_gate.py:30-47, 214-236`). **Design change:** `_count_backing` currently counts within a 200-cell sample (`plan_gate.py:203-211`); replace with a filtered DB count so large-grid objectives are not falsely retired.
- **Plan → execution:** claim ordering bias (`ledger/service._biased_priority`) + task-prefix directive (`father._plan_prefix`). Nothing else may change — "orders existing work" is the invariant.
- **Operator playbooks → directives:** `policy.build_policy_markdown` renders PHASES/Restrictions (`policy.py:70-82`); brief injects phases when `SCANNER_ENGINE_PLAYBOOK` or `SCANNER_ENGINE_BOSS` is on (`scan_brief.py:278-282`); live env has both ON. **Design change:** add a deterministic phase-completion check (each phase's classes covered/attempted) as a coverage-QA section, so a sold playbook is verifiable rather than advisory.
- **Failure semantics:** planner down/timeout/malformed ⇒ prior plan stands (`boss.py:158-175`, `father.py:1160-1167`), already byte-identical.

---

## 7. WS-6 — Surface & browser depth design

### 7.1 Browser worker API contract (extends the existing sidecar)

| Endpoint | Input | Output | Notes |
|---|---|---|---|
| `POST /session` | `{identity: anon\|user_a\|user_b\|admin, storage_state_ref?}` | `{session_id}` | one context per session; scope-bound; token auth |
| `POST /navigate` | `{session_id, url, wait_for?}` | `{status, final_url, snapshot_ref, evidence_id}` | scope-enforced as today (`browser_server.py:821-840`) |
| `POST /act` | `{session_id, steps:[{action: click\|fill\|select\|press\|wait, selector, value?}], capture: bool}` | `{snapshot_ref, screenshot_ref, har_slice_ref, new_routes[]}` | bounded step count (≤N), 30 s nav timeout preserved |
| `GET /snapshot` | `{session_id}` | `{dom_ref, url, title}` | read rendered state |
| `POST /session/save` | `{session_id}` | `{storage_state_ref}` | persist cookies+localStorage for reuse by later requests |
| `DELETE /session` | `{session_id}` | `{}` | cleanup (also close context in `finally`) |

Contract invariants: per-scan token; SSRF/scope route interceptor on every request; no DB access; evidence row per action (screenshot + HAR slice + DOM diff ref); step budget counted per scan, not per call.

### 7.2 SPA scenario as a state diagram (one example, no commands)

```
ANON(browse /) ──login──▶ AUTHED(session user_a)
AUTHED ──navigate(protected route)──▶ RENDERED(route)
RENDERED ──act(fill+submit form)──▶ STATE_CHANGED(request posted)
STATE_CHANGED ──snapshot──▶ EVIDENCE(dom+har+screenshot)
EVIDENCE ──oracle──▶ {PROVEN | NOT_PROVEN}
AUTHED ──switch identity user_b──▶ REPLAY(same object id)
REPLAY ──oracle(differential)──▶ {BOLA_PROVEN | SCOPED}
```
Auth-state persistence is the enabler: `storage_state_ref` lets hop N+1 start authed without replaying login.

### 7.3 Client-side proof artifacts beyond DOM-XSS

- **Execution oracles:** postMessage→sink (already partially covered), storage→sink (token read into `innerHTML/eval`), XHR response→DOM sink, route-transition XSS. Each returns `EXECUTION_INSTRUMENTATION` with a canary hit; ingest only on execution (mirror `browser_ingest.py:228-229`).
- **State-change proof:** after `act`, assert the server-state delta (e.g., PUT then GET from a second identity) — oracle type `STATE_CHANGE`/`DIFFERENTIAL_REPLAY`.
- **Screenshot/HAR at the hit** (currently a TODO in `browser_ingest.py:397-399`) so reports carry visual proof.

### 7.4 Oracle designs for currently skill-only classes (INPUT → VERDICT; no payloads)

| Class | Oracle INPUT | VERDICT |
|---|---|---|
| GraphQL authz | same field query executed as user_a and user_b; response objects compared | BOLA if B's payload contains A's object; BFLA if low-priv gets admin-shaped data; excessive-data if sensitive props non-null (exists, gated) |
| WebSocket | marker published by B on user-scoped channel; A's frames inspected | leak if B's unique marker appears in A's frames (exists, gated) |
| JWT/session/OAuth | forged/tampered token vs signature-tampered control; replay after logout | accept vs reject differential; must include a rejected control in the same session (exists, gated) |
| LDAP/XPath/SSI | crafted input returns an evaluator-specific differential (error class, filter reflection, directive execution marker) not present with a benign control | boolean/differential + evidence excerpt |
| Race/price/quota logic | two-identity scripted flow with one state-changing step repeated in a controlled window | STATE_CHANGE oracle: invariant violation visible on a fresh read (two-account baseline is already in `/work/auth.json`) |
| Mass assignment | update as A with a privileged field, read back as A and B | field persisted = `PARSER_ACCEPT`; cross-user visibility = differential |

---

## 8. Do-not-build list (with reasons)

- **Recursive agent hierarchies** — current bottleneck is throughput, not orchestration depth; more agents multiply window cost (`fleet.py` pool semantics).
- **Generation-counter/freeze** — no failure mode found that it fixes; version fields already exist in plan/ledger.
- **Agent-to-agent messaging via chat** — shared artifacts (`findings.jsonl`, `auth.json`, signals) are sufficient once partitioned; chat messaging would add nondeterminism.
- **pgvector semantic memory** — the worker's problem is grounding in live evidence, not recall; duplicate-work is caused by unmatched coverage, not missing embeddings.
- **ZAP as a core detector** — ZAP alerts currently land as signals/findings; its verdicts are not oracle-grade, and it adds sync cost at finalize.
- **Intercepting proxy as coordination substrate** — adds an interception SPOF and secrets exposure; scope/config already enforce bounds.
- **Credential-stuffer auto-login (until an artifact contract exists)** — explicitly declined in code (`chain/floor.py:385-390`) for good reason; do it only after WS-4 receipts define safe replay.

---

## 9. Implementation roadmap (flag-gated, validation-first)

| Phase | Ship | Flags | Gate to proceed |
|---|---|---|---|
| 0 | Observability parity: window telemetry, boss tick events, coverage funnel file, unmatched KPI | `SCANNER_ENGINE_WINDOW_TELEMETRY`, `SCANNER_ENGINE_BOSS_TELEMETRY` | one scan shows ≥95% of windows instrumented; no behavior delta |
| 1 | Coverage honesty: identity alias/canonicalization; unmatched → 0; `probed` terminal; floor release + lease sizing | `SCANNER_LEDGER_ALIAS_V2`, `SCANNER_LEDGER_PROBED_TERMINAL`, `SCANNER_FLOOR_RELEASE` | a full scan reaches quiescence in < 60 min on the VulnerableApp baseline with 0 unmatched warnings |
| 2 | Planner activation: full-grid backing count; canary plan accepted; directive visible in tasks | `SCANNER_ENGINE_BOSS` (already on), `SCANNER_PLAN_GATE_V2` | 3 consecutive scans with ≥1 accepted plan and no termination change |
| 3 | Chain receipts: `chain_context`, receipts, proof-type enum, report story schema, replay handles | `SCANNER_CHAIN_RECEIPTS` | ≥1 end-to-end chain with all receipts verified in a canary scan |
| 4 | Browser Act + sessions + state-change oracles | `SCANNER_BROWSER_ACT`, `SCANNER_BROWSER_SESSIONS` | one SPA scenario proven end-to-end with replayable evidence |
| 5 | Oracle default-on: GraphQL authz, channels, AI/MCP; logic oracles | per-oracle flags → default | 0 false confirmations across 3 canary scans (oracle-first audit) |

---

## 10. Consolidated evidence ledger

Confidence = HIGH (direct code/query I read) · MEDIUM (doc/competitor) · LOW (inference) · UNVERIFIED.

| # | Claim | Source | Conf | Notes |
|---|---|---|---|---|
| S0 | HEAD is `f75608f`, not `1c5551d` | [QUERY] `git rev-parse HEAD` → f75608f | HIGH | directive stale |
| A1 | All four sources available; SSH login `abhedi-cc` as `admin` | [QUERY] `ssh abhedi hostname/whoami` | HIGH | read-only used |
| H1-a | Claim/release id mismatch existed; fixed via release-by-ids on batch path; legacy path still lease-only | [CODE] `father.py:774-776`; `ledger/service.py:1476-1505`; `father.py:1898-1901` | HIGH | work-stealing on_done at `father.py:1405` |
| H1-b | Quiescence read fails CLOSED (keeps working on error) — "ends loops early" refuted | [CODE] `father.py:1428-1441` | HIGH | |
| H1-c | Production wall = 86,400 s, max_waves = 1000, pool cap = 4 | [QUERY] docker inspect scanner-agent env | HIGH | `worker_runs` max 2,961 s, so wall not used |
| H1-d | Wave 1 > 105 min and running; pool 4; 24 batches | [QUERY] `worker_runs` rows; scan still `running` at 22:48 | HIGH | |
| H1-e | 86/86 decisions.log lines are `max_turns_exceeded` | [QUERY] workdir `decisions.log` | HIGH | first file read 73/73 |
| H1-f | Floor-owned `testing` cells = 1,609; blind resolves 1 clean/1 confirmed of 530 | [QUERY] ledger group by `claimed_by,state` | HIGH | |
| H1-g | 522 `update_unmatched` + 362 `finding_unmatched` warnings in live agent log | [QUERY] `docker logs \| grep -c` | HIGH | |
| H1-h | Sync every 120 s + report regen ≥ every 60 s (cap 50) concurrent with waves | [CODE] `father.py:1077-1106, 1045-1075`; [QUERY] env `SYNC_INTERVAL_S=120`, `REPORT_MIN_INTERVAL_S=60` | HIGH | |
| H2-a | Initial task = brief + skills + triage + worklist; reprompt is state-aware | [CODE] `father.py:597-675`; `agents_runtime.py:962-1021` | HIGH | boss plan would add priorities |
| H2-b | Zero accepted boss plans in live scan (no `plan.json`, no `plan.revised`) | [QUERY] workdir listing; `scan_events` | HIGH | silent failure path exists `boss.py:158-175` |
| H3-a | Chain nodes store PoC/evidence but next hop consumes only capability+endpoint+global session | [CODE] `chain/service.py:167-186`; `chain/floor.py:407-441` | HIGH | |
| H3-b | Credential re-auth explicitly not built | [CODE] `chain/floor.py:385-390` | HIGH | |
| H3-c | 42 chain nodes / 60 edges on live scan; `capability` is a column, attrs carries proof | [QUERY] `chain_node/chain_edge` counts; [CODE] `tenant.py` model via subagent | HIGH | attrs->>'capability' null because separate column |
| H4-a | No worker-driven browser interaction; only `browse(url,max_pages)` | [CODE] `engine/tools/browser.py:52`; `agents_runtime.py:253,635-638` | HIGH | |
| H4-b | `/instrument` authenticates by headers only; no login/storage planting; single identity | [CODE] `browser_server.py:1063-1084, 469-493, 526-536`; `config.py:338` | HIGH | |
| H4-c | Real-execution canary oracle for DOM XSS/PP; `executed:false` never ingested | [CODE] `browser_server.py:335-409`; `browser_ingest.py:228-229` | HIGH | |
| H4-d | HAR response bodies omitted; proof slices expect bodies | [CODE] `browser_server.py:798-805`; `browser_ingest.py:168-175` | HIGH | |
| H5-a | 62 VulnClasses; ~30 deterministic oracles; 12 none (see `evidence/oracle_coverage_table.md`) | [CODE] `taxonomy.py:19-93`; `exploit_floor.py:130-235`; `oracle_map.py` | HIGH | exploration table spot-verified against code I read |
| H5-b | GraphQL authz / channels / AI floor gated default-OFF; auth oracles ON in prod env | [CODE] flags; [QUERY] live env | HIGH | |
| H5-c | A1 verifier is an LLM agent (12-turn budget); 146 failures in live log | [CODE] `verify.py:33-100`; `hooks/verification.py`; [QUERY] log count | HIGH | |
| H6-a | All agent_messages rows 0 tokens; only MaxTurns markers recorded | [QUERY] `agent_messages`; [CODE] `agents_runtime.py:440-445` | HIGH | token telemetry blind on the only path used |
| H6-b | `resolved_cells` always 0 in `worker.finished` | [QUERY] scan_events payloads | HIGH | field not populated |
| H6-c | 70 skills mounted; per-group in-band bundle ≤9,000 B; ~50 ad-hoc scripts in `/work` | [QUERY] container/workdir; [CODE] `father.py:183, 194-235` | HIGH | |
| H6-d | Signal backlog 1,157 lines globally re-offered; 502 blind signals | [QUERY] signal file counts; [CODE] directive `father.py:327-348` | HIGH | |
| T1 | Live scan cell states: na 6,247 / testing 1,701 / tested_clean 943 / untested 321 / confirmed 19 / blocked 6 | [QUERY] ledger snapshot 22:48 | HIGH | 67.6% na |
| T2 | Completed scans show `attempted` tails: 68a58881 1,303; 373bff88 1,516; 1f5fe7c8 853 | [QUERY] ledger group by scan | HIGH | attempt-cap absorption |
| T3 | Scan walls: 17 h 53 m (68a58881), 15 h 15 m (1f5fe7c8), 48 m (373bff88), 6 m (7ec54a2f) | [QUERY] `scans.completed_at-started_at` | HIGH | long tails |
| C1 | All three competitors claim exploit-validated proofs, chaining, and case-file reporting | [COMPETITOR] `COMPARISON.md:13-15,23,118` | MEDIUM | self-reported claims |
| C2 | XBOW: 5-stage pipeline + validator agents (programmatic + LLM) + full case file | [COMPETITOR] `xbow/dossier.md:46-49,82` | MEDIUM | Moderna chain case study |
| C3 | FireCompass: 4-stage validation pipeline; specialized agents on a shared persistent state store; app-to-identity lateral movement | [COMPETITOR] `firecompass/dossier.md:91-92,104,46` | MEDIUM | |
| C4 | Escape: Reporter independently reproduces each finding before filing; multi-agent orchestrator; multi-identity business-logic chains | [COMPETITOR] `escape/dossier.md:95,90,134` | MEDIUM | |
| C5 | Market gap: independent verification of claims is the biggest unmet need; proof framing is table stakes | [COMPETITOR] `COMPARISON.md:118-119` | MEDIUM | |
| W1 | `scan_is_complete`/`count_claimable` drive termination; `na` cells never claimable | [CODE] `attack_surface.py:92-113`; `ledger/service.py:1508-1521` | HIGH | |
| W2 | `tested_clean` close needs 2 methods + evidence + probe + oracle; signals strip `weapon_swept` | [CODE] `ledger/service.py:975-1009` | HIGH | strictness intentional |
| W3 | Boss/plan gate are deterministic and prior-plan-preserving; 200-cell backing sample is a limitation | [CODE] `boss.py`; `plan_gate.py:203-211` | HIGH | |
| W4 | Playbook consume is gated by PLAYBOOK or BOSS env; phases injected into brief only | [CODE] `policy.py:124-132`; `scan_brief.py:278-282` | HIGH | live env both ON |

## Appendix — supporting evidence files
- `evidence/ws1_ws2_telemetry.md` — raw WS-1/WS-2 queries, environment dump, timelines, counters.
- `evidence/ws3_competitors.md` — WS-3 mechanism comparison and gap analysis.
- `evidence/oracle_coverage_table.md` — full 62-class oracle table (H5 appendix).
- `NOTES.md` — source availability, method, caveats.

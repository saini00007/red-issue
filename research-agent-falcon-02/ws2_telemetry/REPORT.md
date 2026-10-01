# WS-2 — TELEMETRY FORENSICS
**Sub-agent:** `ws2_telemetry` · **Lead:** `research-agent-falcon-02`
**Repo:** `C:\Users\ASUS\Desktop\abhdeii\autocan` @ `feat/alpha-observability`, HEAD `f75608f` (READ-ONLY, unmodified)
**Scope of evidence:** live host `abhedi` (`abhedi-cc`), docker volume `abhedi_red_scanner_data` (43 workdirs), live `scanner-postgres` (`tenant_xbow`, 43 scans), proxy DB `/home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db` (24,630 calls).
**Constraints honoured:** read-only (`sqlite3 -readonly`, `psql SELECT` only); no secrets reproduced (all values redacted to counts/lengths/structure); no payloads or attack commands; no citations invented.

---

## A. PROXY COVERAGE — the NVIDIA-only assumption is **CONFIRMED, and worse than assumed**

**Verdict: the assumption is directionally right but the real defect is that the proxy is opt-in per scan roster, not per provider. 38 of 43 scans (88.4%) never route through it at all, and the 5 that do carry no per-scan attribution.**

### A.1 What the proxy DB actually contains
| Metric | Value | Source |
|---|---|---|
| Total calls logged | 24,630 | `select count(*) from calls` |
| Time window | 2026-09-28T22:58:54Z → 2026-09-29T23:06:55Z (~24.1 h) | `min(ts), max(ts)` |
| Endpoint | `/v1/chat/completions` = 24,630 (100%) | `group by endpoint` |
| Distinct `model_req` | **3**, all `nvidia/*` | `group by model_req` |
| Distinct `model_fwd` | **2**, both `nvidia/nemotron-*` | `group by model_fwd` |
| Non-NVIDIA model strings | **0** | — |
| HTTP status mix | 200: 18,138 · **429: 3,578** · **500: 2,834** · 0: 49 · 502: 19 · 504: 12 | `group by status` |
| Token volume logged | prompt 362,681,803 · completion 3,396,761 · total 366,078,564 | `sum(...)` |
| `request_json` bytes | total **1,557,226,921** (p50 58,368 · p90 125,003 · p99 165,973 · max 202,279) | length census |
| `response_json` bytes | total 21,139,435 (p50 907 · max 47,135) | length census |
| `prompt_tokens` NULL | 6,492 rows (26.4%) | `sum(case when prompt_tokens is null…)` |

**So: the proxy DB is 100% NVIDIA/nemotron. Confirmed.** Every OpenRouter call (bunny, dots3, laguna, glm, deepseek, gpt-5.6-luna) and the `experientiallabs.ai` roster bypasses it completely. Note the DB is **1.5 GB of full prompt+response bodies** — this is the primary secret-exposure surface in the whole system (see D.3).

### A.2 The denominator (the assumption the directive did not state)
`tenant_xbow.scans.engine_models` carries the per-scan roster including `api_base`:

| `api_base` | scans | share |
|---|---|---|
| `https://openrouter.ai/api/v1` | **33** | 79.3% |
| `http://logging-proxy:8080/v1` | **5** | 11.6% |
| `https://api.experientiallabs.ai/v1` | 1 | 2.3% |
| roster absent/empty | 4 | 9.3% |

Model strings used fleet-wide: `stealth/space-bunny-alpha` (13 scans), `dots-studio/dots-3-note-preview:free` (8), `nvidia/nemotron-3-ultra-550b-a55b:free` (6), `poolside/laguna-s-2.1:free` (3), `nvidia/nemotron-3-super-120b-a12b` (3), `nvidia/nemotron-3-ultra-550b-a55b` (2), `z-ai/glm-5.3` (2), `deepseek/deepseek-v4.1-flash` (1), `gpt-5.6-luna` (1).

**Critically: "nemotron" is NOT a proxy indicator.** 11 scans name a nemotron model but only 5 set `api_base` to the proxy; the other 6 nemotron scans go direct to `openrouter.ai`. Conversely, no OpenRouter model scan is proxied. The correct predicate is `engine_models ilike '%logging-proxy%'`, not the model family.

### A.3 Measured coverage ratio
| Denominator | Proxy-routed | Bypassed | Coverage |
|---|---|---|---|
| All 43 scans | 5 | 38 | **11.6%** |
| Completed/partial (19) | 3 | 16 | **15.8%** |
| Cancelled/failed/running (24) | 2 | 22 | 8.3% |
| Window-overlapping scans (29) | 5 | 24 | 17.2% |

The 5 proxied scans: `68a58881` (completed), `373bff88` (completed), `1397908a` (completed), `05ba4cad` (cancelled), `0c33cffd` (cancelled).

### A.4 A second, worse finding: zero per-scan attribution *even where proxied*
I scanned all 24,630 `request_json`+`response_json` blobs for the 8-char prefix of each of the 5 known proxied scan_ids:
- **0 rows** reference any of the 5 proxied scan_ids.

A UUID-shaped token appears in 23,973 rows and `/var/lib/scanner` in 815 — but those are OOB canaries and file paths inside prompt text, not a scan identity field. **Consequence: the proxy cannot answer "which scan spent this token" or "which scan got rate-limited".** The `calls` table has no scan/tenant column and the client sends no correlating header. Telemetry is only attributable by timestamp-window inference. Rate-limit attribution — the single most operationally useful question — is unanswerable from this data.

### A.5 Additional proxy-side observations
- Proxy capture **stopped** at 2026-09-29T23:06:55Z and never resumed, although `logging-proxy` is `Up 2 days` and 4+ further scans ran through 2026-09-30T20:10Z (including the currently-`running` scan `84aea81a`). The DB is stale, not merely incomplete.
- 26.4% of calls (6,492) have NULL `prompt_tokens` — token accounting is unreliable exactly where errors occurred (4,392 of those are 429/500/502/504).
- 61 rows have empty `response_json` while `status=200` — successful calls with no recorded body.

---

## B. QUESTION LIST — one line each

1. **LEDGER STATE THRASH** — No. Only **37 real rework events** (transitions back into `testing` from a non-`testing` state) across 5 scans; the dominant "churn" signal is **2,074 same-state re-appends with *changed* evidence** (`testing→testing` 1,435), i.e. re-testing a cell without changing its verdict — real waste, but a different shape than oscillation. *(details in C.1)*
2. **OOB HONESTY** — **Yes, the classification is honest, and the `_registration_floor` gate is WORKING in this data** (0 pre-scan confirmations; 0.14% of 96,765 callbacks link). But it barely matters: only **138 callbacks ever linked**, and 0 of the 301 OOB evidence rows reached a finding via a back-link — the OOB confirm path is close to inert, not wrong. *(C.2)*
3. **LLM DRIVER ERRORS** — Beyond WS-1's "no choices": `max_turns_exceeded` dominates (**950**, 5 scans); `429` rate-limit pressure is **4,396 log lines across 24 of 27 logs**; a newly-identified class `ledger.resolve.*_unmatched` fires **12,734 times**. Context-reset/compaction is effectively absent (**3 hits, 1 scan**); explicit retry is absent (**1 hit**). *(C.3)*
4. **DID THE MODEL DRIVE?** — **No. The model is close to dead weight.** 348 persisted assistant messages vs **37,047 tool invocations (1:106)**; **41.4%** of all tool calls come from the deterministic `exploit_floor`; **17 scans produced tool calls with zero model messages**; and `worker_runs.findings_count` sums to **35,934 against 259 actual findings (139× inflation)**. *(C.4)*

---

## C. OBSERVED-FAILURE CATALOG — aggregate counts only

### C.1 Ledger / bookkeeping

| Failure class | Count | Rate | Affected scans | Source |
|---|---|---|---|---|
| `testing→testing` re-append (no verdict change) | 1,435 | 58.6% of 2,447 transitions | 19 | `ledger_updates.jsonl` |
| `tested_clean→tested_clean` re-append | 617 | 25.2% | 19 | `ledger_updates.jsonl` |
| Same-state re-append with **changed** evidence | **2,074** | 22.8% of 9,096 rows | 19 | `ledger_updates.jsonl` |
| Pure heartbeat (identical evidence, re-appended) | 176 | 1.9% of rows | — | `ledger_updates.jsonl` |
| **Real rework** (transition back into `testing` from another state) | **37** | 0.4% of rows | **5** | `ledger_updates.jsonl` |
| Cells showing ≥1 repeated state | 1,064 / 6,649 | 16.0% | 19 | `ledger_updates.jsonl` |
| Cells with ≥2 returns to an already-left state | 578 / 6,649 | 8.7% | 19 | `ledger_updates.jsonl` |
| **Backtrack out of `confirmed`** | **2** | — | 2 | `ledger_updates.jsonl` |
| **`confirmed` reached at all** | **3 rows** | 0.03% of rows | — | `ledger_updates.jsonl` |
| Ledger cells auto-closed `na` | **48,322 / 70,781 (68.3%)** | 68.3% | 39 | `ledger_cell` |
| Cells with a `finding_id` | **195 / 70,781 (0.28%)** | 0.28% | 15 | `ledger_cell` |
| `resolved_count` = 0 | **987 / 987 worker_runs** | 100% | 39 | `worker_runs` |
| `worker_runs.findings_count` sum vs actual | **35,934 vs 259 (139×)** | — | 39 | `worker_runs` vs `findings` |
| `agent_messages` rows with `role != assistant` | **0** (user/tool turns never persisted) | 100% | 17 | `agent_messages` |
| `worker_runs` stuck `running` | 53 | 5.4% of 987 | — | `worker_runs` (WS-1, reconfirmed) |

Worst scans by reopened-cell count: `373bff88` 13, `68a58881` 11, `1f5fe7c8` 6, `84aea81a` 5, `4ebd576b` 2.

**Interpretation.** State-machine thrash is *not* the problem the hypothesis anticipated — it is 0.4% of rows. The real ledger pathology is **mass auto-closure**: 68.3% of all cells are `na` with a machine reason string, and the largest single reason is "host-level class covered by one cell per host" (11,885 cells). Coverage is therefore reported as high largely because cells are declared non-applicable, not because they were tested. Only 0.28% of cells carry a finding.

### C.2 OOB

| Failure class / metric | Count | Rate | Affected scans | Source |
|---|---|---|---|---|
| Total interactions mirrored | 96,765 | — | 43 | `oob_interactions.jsonl` |
| Interactions matching a registered token | **301** | 0.31% | 39 | re-run of `registry.correlate` |
| Rejected by identity gate (no interactsh identity) | 0 | — | 0 | same |
| **Rejected by `_registration_floor` (pre-scan/stale)** | **2** | 0.66% of 301 | 1 (`6c4d84c3`) | same |
| **Linked (confirm-capable)** | **138** | 45.8% of 301 | **9** | same |
| Linked rate over ALL interactions | 138 / 96,765 | **0.14%** | 9 | same |
| Callbacks confirmed **before** scan start (`fired_at < started_at`) | **0** | 0% | 0 | `oob_token` × `scans` |
| `oob_token` rows that are unlinked (no cell_id **and** no endpoint) | **161 / 301 (53.5%)** | 53.5% | 39 | `oob_token` |
| `oob_token` rows with endpoint but NULL `cell_id` | 122 / 301 (40.5%) | 40.5% | — | `oob_token` |
| Agent class **downgraded** to honest protocol class | **51 / 138 (36.9%)** | 36.9% | 9 | re-derived `classify_oob` |
| OOB-minted findings in DB (`verification_method='oob_callback'`) | 27 | — | — | `findings` |
| `evidence_object` OOB rows **with** a `finding_id` back-link | **0 / 301** | **0%** | 0 | `evidence_object` |
| `findings.jsonl` rows carrying an `oob_token` field | **0 / 642** | 0% | 0 | `findings.jsonl` (no such key exists) |
| `oob_health.json` present / `checked_at` populated | 39 / 39 (100%) | 100% | 39 | `oob_health.json` |
| `oob_health.json` MISSING | 4 | 9.3% of scans | `1a02c94e`, `2759dbc2`, `6f862ca0`, `f8500a4b` | same |

**Interpretation — the answer to Q2 is a genuine PASS, with two caveats.**
1. **The `_registration_floor` gate is WORKING.** It fired and rejected 2 stale callbacks in `6c4d84c3`. No pre-scan callback reached a finding: 0/301 tokens have `fired_at < started_at`. Honesty layer 2 (`classify_oob`) is also doing real work — it downgraded 36.9% of linked callbacks away from the agent's claimed class (e.g. `cmdi`→`ssrf`, `deserialization`→`ssrf`, `reachability`→`ssrf`, `nosqli`→`ssrf`), which is exactly the intended anti-fabrication behaviour.
2. **But the gate is load-bearing only in theory.** Because `checked_at` was populated in all 39 scans that have `oob_health.json`, the **fail-open path was never exercised** — and it is real: `run.py:109` initialises `checked_at = ""` when the self-test exceeds its hard cap, and `service.py:159-161` returns `None` on empty/missing `checked_at`, which disables the time gate entirely, leaving only the identity gate. `MEDIUM` confidence that this is exploitable in production; **it is a latent fail-open with no test coverage in this dataset.**

The dominant OOB problem is not dishonesty, it is **disconnection**: 53.5% of fired tokens have no registration at all, 40.5% more have an endpoint but no resolvable UUID cell, and **zero of the 301 OOB evidence rows are back-linked to a finding**. Evidence is written with `kind="finding", method="oob"` and an `oob_token`, but `finding_id` stays NULL — so the audit chain "callback → finding" is not reconstructable from the DB, and `findings.jsonl` has no `oob_token` field at all.

### C.3 LLM driver errors

| Failure class | Count | Rate | Affected scans | Source |
|---|---|---|---|---|
| `max_turns_exceeded` (verification + close_sweep) | **950** | 93.2% of 1,019 error lines | 5 | `agent.log` |
| `ChatCompletion response has no choices` | 56 | 5.5% | 2 | `agent.log` (WS-1, reconfirmed) |
| `Error code: 500` (upstream) | 8 | 0.8% | 1 | `agent.log` |
| `Error code: 429` surfaced as a driver error | 5 | 0.5% | 1 | `agent.log` |
| **429 / rate-limit signal lines (all levels)** | **4,396** | 3.5% of 126,407 lines | **24 of 27** | `agent.log` |
| Upstream-500 signal lines | 24 | 0.02% | 1 | `agent.log` |
| **`ledger.resolve.update_unmatched`** | **10,135** | 8.0% of lines | 6 | `agent.log` |
| **`ledger.resolve.finding_unmatched`** | **2,599** | 2.1% of lines | 9 | `agent.log` |
| — of which endpoint is an explicit non-target placeholder | 760 / 12,734 | 6.0% | 1 (`1f5fe7c8`) | `agent.log` |
| `engine.model_http_error status=429` (proxy-routed) | 988 | 0.8% | 2 | `agent.log` |
| `tool.started` vs `tool.done` unpaired | 4 / 33,881 | 0.01% | 3 | `agent.log` |
| **Context reset / compaction / truncation / overflow** | **3** | 0.002% | **1** | `agent.log` |
| **Explicit retry / retrying / attempt-N** | **1** | 0.001% | 1 | `agent.log` |
| `json` decode errors | 20 | 0.016% | 1 | `agent.log` |
| OOM / exit 137 | 0 | — | 0 | `agent.log` |
| Lease / claim conflicts | 0 | — | 0 | `agent.log` |
| Toolserver transport errors | 0 | — | 0 | `agent.log` |
| `close_sweep.failed` (max turns) | 2 | — | 2 | `agent.log` |

**Retry/duplication answer (Q3):** context state is essentially **never lost** — 3 hits fleet-wide — so conversation continuity is not the failure mode. There is also **no retry layer to speak of** (1 hit): the driver does not re-prompt, it gives up and records `max_turns_exceeded`. Duplicate work therefore comes from *re-dispatch*, not retry: at the invocation layer, **9,529 / 37,047 commands (25.7%) are exact repeats** of an already-issued command (worst scans: `1397908a` 38.6%, `3b7759b6` 37.1%, `6c4d84c3` 29.5%), and **12,668 / 33,292 (38.1%) of `output_summary` values are byte-duplicates** of a previous result.

**The newly-identified class worth escalating: `ledger.resolve.*_unmatched` (12,734 warnings).** Findings and ledger updates are being emitted with endpoints that do not match any known ledger cell, so the determinism oracle cannot resolve them. Concentrated in `68a58881` (9,485 — 74.5% of all occurrences) and `1f5fe7c8` (1,620) and `4ebd576b` (1,567). Top unmatched `vuln_class`: `sqli` 8,632, `ssrf` 1,231, `idor_bola` 848, `nosqli` 379, `deserialization` 276, `jwt_flaws` 276. This is the mechanism by which agent-authored claims silently fail to become coverage — and it means the "every claim resolves to a cell" property is not holding in practice.

### C.4 Value-add / did the model drive

| Metric | Value | Source |
|---|---|---|
| `agent_messages` rows (all `role=assistant`) | **348** | `agent_messages` |
| Distinct scans with any model message | 17 / 43 (39.5%) | `agent_messages` |
| Distinct agents with messages | 130 | `agent_messages` |
| **Scans with tool calls but ZERO model messages** | **17** | cross-query |
| `tool_invocations` | **37,047** | `tool_invocations` |
| **Messages : tool calls** | **1 : 106** | derived |
| Messages per completed scan (range) | 0 → 139 | P4/T4 |
| Scans where messages ≥ 100 | **1** (`1f5fe7c8`, 139 msgs / 9,843 tools = 1:71) | T4 |
| **`exploit_floor` share of all tool calls** | **15,337 / 37,047 = 41.4%** | T1 |
| Max turns observed per agent | 7 | `agent_messages` |
| Median turns per agent | ≤ 5 | `agent_messages` |
| Tool calls per model message (fleet) | 106.5 | derived |
| Findings attributable to deterministic floor (`exploit_floor:*`) | 132 / 259 (51.0%) — all `verified=true` | T3 |
| Findings attributable to `oob_callback` | 27 / 259 (10.4%) — all `verified=true` | T3 |
| Findings from `llm_or_manual` | 100 / 259 (38.6%), only **47 verified** (47%) | T3 |
| `cost_usd` non-zero rows | **0 / 348** | `agent_messages` |
| `scans.cost_spent_usd` non-zero | **0 / 43**; fleet sum **0.0000** | `scans` |
| `scans.cost_cap_usd` non-zero | **0 / 43** | `scans` |
| `tokens_in = 0` rows | **239 / 348 (68.7%)** — every `space-bunny-alpha` row | `agent_messages` |
| Tokens recorded (only where non-zero) | in 51,896,923 · out 857,840 | `agent_messages` |
| Ratio out/in where tokens present | **1.65%** — extreme prompt dominance | derived |

**Interpretation.** The value test fails on the evidence. The model emits **348 messages across 43 scans** while the platform issues **37,047 tool calls**; on 17 scans the model contributed *no messages at all* despite the scan doing real work, and `68a58881` — the largest scan, 12,143 tool calls, 38 findings — logged exactly **1** model message. 41.4% of tool calls are self-issued by the deterministic `exploit_floor`, and the highest-confidence findings (132 floor + 27 OOB = 159, all `verified=true`) come from the non-LLM paths. The LLM-attributed bucket is both the smallest and the least verified (47/100). Combined with WS-1's "48.5% of worker runs died on *no choices*" and "63/63 turns ended `max_turns_exceeded`", the picture is a **deterministic floor carrying the product while the LLM driver contributes turns without decisions**.

A **cost-accounting hole**: `cost_usd` is `0.0000` on every message and every scan, `cost_cap_usd` is 0 on every scan, yet 51.9M prompt tokens were consumed. `config.py:170` makes the cap default 0 = unlimited, so the documented budget stop cannot fire; and because cost is never recorded, **spend is unmeasurable and unbudgeted**. Separately, 68.7% of messages have `tokens_in = 0` (all `space-bunny-alpha`), so even the token telemetry is provider-dependent and incomplete.

---

## D. WHAT UNDERMINES THE CORE VERIFICATION THESIS

The thesis is *"a deterministic oracle disposes"* — the LLM proposes, the deterministic floor adjudicates, and only machine-checked evidence becomes a finding. I looked specifically for the failure mode that would break this: **a false confirm**. Here is what I actually found, ordered by how much it threatens the thesis.

### D.1 The oracle did NOT false-confirm — the honest path held. (Good news, and it is real.)
- 0 pre-scan / planted / unrelated callbacks reached a finding. `fired_at < started_at` is **0 / 301**.
- `_registration_floor` demonstrably rejected 2 stale callbacks.
- `classify_oob` downgraded **36.9%** of linked callbacks away from the agent's claimed class. The design intent — "a callback proves outbound reach, not which bug caused it" — is *working in the data*.
- Of 96,765 mirrored callbacks, only 0.14% could ever be linked. The noise floor of the shared oracle is fully absorbed.

This is the strongest part of the system and I want it on the record.

### D.2 …but "coverage" is substantially self-declared, not earned.
**48,322 of 70,781 ledger cells (68.3%) are `na`**, closed by machine with a reason string rather than tested; the largest reason alone accounts for 11,885 cells. Only **195 cells (0.28%)** carry a `finding_id`, and **`resolved_count` is 0 on 987 of 987 worker runs**. `agent_messages` stores **no user or tool turns**, so the conversation that supposedly justifies each disposition is not reconstructable. A ledger in which 68% of cells are auto-closed and 0% of runs report resolutions cannot currently support a claim of *dispositive* coverage — the oracle disposes, but largely of its own non-applicability declarations. **This is the single most thesis-relevant finding in my scope.**

### D.3 …and the evidence chain for OOB — the flagship proof mechanism — is broken in the audit trail.
301 fired OOB tokens produced 27 `oob_callback` findings, but **0 of 301 `evidence_object` rows carry a `finding_id`**, and **`findings.jsonl` has no `oob_token` field at all** (verified: the key does not exist in any of the 642 rows). Post-hoc you cannot prove *which callback confirmed *which* finding*. For a product whose differentiator is deterministic proof, the proof's own lineage is the part that is unproven.

### D.4 Fail-open in the anti-fabrication gate, unexercised and untested.
`run.py:109` writes `checked_at = ""` if the OOB self-test exceeds its hard cap; `service.py:159-161` returns `None` on that empty value; `registry.correlate` then runs with `since=None`, and the **time gate silently disappears**, leaving only the identity gate. It did not fire in this dataset (39/39 `checked_at` populated), so I cannot demonstrate impact — but a security control whose absence is silent and whose trigger is a routine timeout is a latent defect. Recommend the gate fail **closed** (deny confirm) rather than open when the floor is unknown.

### D.5 Operator-facing cost blindness.
0/43 scans have a cost cap or recorded spend while 51.9M prompt tokens were burned. Combined with 4,396 rate-limit lines across 24 of 27 logs and a proxy that recorded 3,578 × 429 and 2,834 × 500, **the platform spends unbounded money against a rate-limited free-tier proxy with no cost feedback loop.**

### D.6 Secret-exposure surface (structural, no values reproduced).
The proxy DB is **1.5 GB** and stores full `request_json` (**1.56 GB**, p99 166 KB) and `response_json` for every call, on a host bind-mount at `/home/admin/research/2026-09-29-deepdive/proxy/data/`, owned `root:root`, mode 644. Model prompts in an agentic VAPT scan carry session cookies, bearer tokens, API keys and target credentials, so this DB is expected to contain live secrets at rest in world-readable form. Additionally, per-scan `agent.log` line 1 writes a **generated admin API key in plaintext** (value withheld; see E-14). I did not read or reproduce any of these values; I am reporting the structural exposure only.

---

## E. EVIDENCE LEDGER

| # | Claim | Source (type + location) | Confidence | Notes |
|---|---|---|---|---|
| 1 | Proxy DB holds 24,630 calls, all `/v1/chat/completions`, window 2026-09-28T22:58Z→2026-09-29T23:06Z | [QUERY] `sqlite3 -readonly proxy_log.db "select min(ts),max(ts),count(*) from calls"` + `group by endpoint` | HIGH | Read-only; immutable-safe |
| 2 | Only 3 `model_req` / 2 `model_fwd` values, all `nvidia/nemotron-*`; zero non-NVIDIA | [QUERY] `select model_req,model_fwd,count(*) from calls group by 1,2` | HIGH | Directly falsifies nothing — confirms the NVIDIA-only assumption |
| 3 | Proxy `api_base` used by exactly 5 of 43 scans | [QUERY] `select (engine_models ilike '%logging-proxy%'),count(*) from tenant_xbow.scans group by 1` | HIGH | Correct predicate is `api_base`, not model family |
| 4 | 11 scans name a nemotron model but only 5 route via proxy → "nemotron" ≠ "proxied" | [QUERY] C3 group-by on `engine_models` + D4 `substring(engine_models from 'api_base…')` | HIGH | Sharpens the directive's assumption |
| 5 | Coverage: 5/43 = 11.6% overall; 3/19 = 15.8% for completed/partial | [QUERY] C1 roster (43 rows) joined to `scans.status` | HIGH | Measured ratio, not estimated |
| 6 | **Zero** proxy rows reference any of the 5 proxied scan_ids | [QUERY] Python: for each of 24,630 rows, test `request_json+response_json` for each 8-char scan prefix → 0 matches | HIGH | Presence-only scan; no values printed |
| 7 | Proxy capture stopped 2026-09-29T23:06Z while ≥4 later scans ran | [QUERY] #1 vs [QUERY] `select max(started_at) from scans where engine_models ilike '%logging-proxy%'` | HIGH | DB stale, not just partial |
| 8 | `request_json` totals 1.56 GB; `prompt_tokens` NULL on 6,492 rows (26.4%) | [QUERY] `sum(length(request_json))`; `sum(case when prompt_tokens is null…)` | HIGH | Structure/size only |
| 9 | 9,096 ledger rows, 6,649 distinct cells, mean 1.37 updates/cell | [QUERY] Python over all `ledger_updates.jsonl` in all 43 workdirs | HIGH | Whole-fleet, not sampled |
| 10 | Real rework (re-entry into `testing`) = **37** events / 5 scans | [QUERY] same, per-cell state sequences, transition `X→testing` where X≠testing | HIGH | Falsifies the thrash hypothesis |
| 11 | Same-state re-append with **changed** evidence = 2,074 (22.8% of rows) | [QUERY] same, comparing `json.dumps(evidence)` across consecutive same-state rows | HIGH | This is the real waste shape |
| 12 | Only **3** `confirmed` rows in the entire ledger-update corpus (0.03%) | [QUERY] state census: testing 7,016 / tested_clean 1,382 / blocked 693 / confirmed 3 | HIGH | Aggregate across 19 scans |
| 13 | 2 backtracks out of `confirmed` → `tested_clean` | [QUERY] transition census `confirmed→tested_clean` = 2 | MEDIUM | Small n; direction is still a defect |
| 14 | 96,765 interactions → 301 token hits → 138 linked | [QUERY] Faithful re-implementation of `registry.extract_token`/`correlate`/`_scan_scoped` over all workdirs | HIGH | Re-ran product logic, not an approximation |
| 15 | `_registration_floor` rejected 2 stale callbacks (scan `6c4d84c3`) | [QUERY] same re-run, `since=checked_at` gate | HIGH | Gate demonstrably functional |
| 16 | 0 pre-scan confirmations: `fired_at < started_at` for **0 of 301** tokens | [QUERY] `select count(*) from oob_token o join scans s … where o.fired_at < s.started_at` | HIGH | Strongest anti-fabrication evidence |
| 17 | `classify_oob` downgraded 36.9% (51/138) of linked callbacks | [QUERY] Re-derived `classify_oob` (code-faithful) vs registry `vuln_class` | MEDIUM | My re-implementation, not runtime output |
| 18 | 0 of 301 `evidence_object` OOB rows have `finding_id` | [QUERY] `select count(*) from evidence_object where oob_token is not null and finding_id is not null` | HIGH | Not a schema artifact — `finding_id` exists and is populated 19× elsewhere |
| 19 | `findings.jsonl` has no `oob_token` key in any of 642 rows | [QUERY] key census over all workdir `findings.jsonl` | HIGH | 0 matches for "token"/"oob" |
| 20 | 53.5% of fired tokens have neither `cell_id` nor `endpoint` | [QUERY] `select count(*) from oob_token where cell_id is null and endpoint is null` → 161/301 | HIGH | — |
| 21 | Fail-open: `checked_at=""` ⇒ `since=None` ⇒ time gate off | [CODE] `engine/run.py:109` (`checked_at = ""` default) + `oob/service.py:151-166` (`_registration_floor` returns None) + `oob/registry.py:158-161` (`if since is not None`) | HIGH (code) / MEDIUM (impact) | Did not fire in this dataset (39/39 populated) |
| 22 | 1,019 error lines in agent.log; `max_turns_exceeded` = 950 (93.2%) | [QUERY] level+event census over 27 `agent.log` (126,407 lines) | HIGH | Beyond WS-1's "no choices" class |
| 23 | 429 rate-limit signal on **24 of 27** logs, 4,396 lines | [QUERY] regex census `(429|rate.?limit|too many requests)` | HIGH | — |
| 24 | Context reset/compaction = **3** hits, 1 scan | [QUERY] regex `(context.{0,20}(reset|compact|truncat|summar|overflow)|compact|truncat)` | HIGH | Conversation state is *not* the failure mode |
| 25 | Explicit retry = **1** hit fleet-wide | [QUERY] regex `\bretry|retries|retrying|attempt \d` | HIGH | No retry layer → duplicate work comes from re-dispatch |
| 26 | `ledger.resolve.update_unmatched` 10,135 + `finding_unmatched` 2,599 = **12,734** | [QUERY] `ledger.resolve.*` census, endpoint payload stripped | HIGH | New failure class, not in WS-1 |
| 27 | 760/12,734 (6.0%) unmatched lines target explicit non-target placeholders | [QUERY] same, endpoint ∈ {NEVER-CONTACTED-CONTROL, CONTROL-ONLY-NOT-SENT, local-control, none, …} | HIGH | 760 of them all in scan `1f5fe7c8` |
| 28 | 348 `agent_messages`, **all** `role=assistant`; 0 user/tool turns | [QUERY] `select role,count(*) from agent_messages group by 1` | HIGH | Prompt/observation history unpersisted |
| 29 | 37,047 `tool_invocations` ⇒ messages:tools = 1:106 | [QUERY] `select count(*) from tool_invocations` vs `agent_messages` | HIGH | The core Q4 ratio |
| 30 | `exploit_floor` = 15,337/37,047 = **41.4%** of tool calls | [QUERY] `sum(case when agent_id='exploit_floor'…)` | HIGH | Deterministic path is the largest single actor |
| 31 | **17** scans produced tool calls with **zero** model messages | [QUERY] cross-query over `scans` | HIGH | Model did not drive these scans |
| 32 | Scan `68a58881`: 12,143 tool calls, 38 findings, **1** model message | [QUERY] P1/T4 per-scan table | HIGH | Strongest single-scan illustration |
| 33 | 9,529/37,047 commands (25.7%) are exact repeats | [QUERY] `count(*) - count(distinct command) from tool_invocations` | HIGH | Re-dispatch duplication, not retry |
| 34 | 12,668/33,292 `output_summary` (38.1%) are byte-duplicates | [QUERY] `count(*) - count(distinct md5(coalesce(output_summary,'')))` | HIGH | — |
| 35 | `worker_runs.findings_count` sums to 35,934 vs 259 actual findings (139×) | [QUERY] `sum(findings_count)` vs `select count(*) from findings` | HIGH | Bookkeeping leak far beyond WS-1's 53 `running` rows |
| 36 | `resolved_count = 0` on **987/987** worker_runs | [QUERY] `select resolved_count,count(*) … group by 1` | HIGH | No run ever reports a resolution |
| 37 | 68.3% of ledger cells auto-closed `na` (48,322/70,781) | [QUERY] `select state,count(*) from ledger_cell group by 1`; `na_reason` census | HIGH | Coverage is substantially self-declared |
| 38 | Only 195/70,781 cells (0.28%) carry a `finding_id` | [QUERY] `select count(*) filter (where finding_id is not null) from ledger_cell` | HIGH | — |
| 39 | `cost_usd = 0` on 348/348 messages; `cost_spent_usd = 0` on 43/43 scans; fleet sum 0.0000 | [QUERY] P2 (non-zero counts all 0) | HIGH | 51.9M prompt tokens consumed, none billed |
| 40 | `tokens_in = 0` on 239/348 messages (68.7%), all `space-bunny-alpha` | [QUERY] P3 + N7 model census | HIGH | Token telemetry provider-dependent |
| 41 | Prompt:completion = 51,896,923 : 857,840 (1.65% out) | [QUERY] P3 sums | MEDIUM | Only where tokens are recorded at all (per #40) |
| 42 | Floor/OOB findings are 100% `verified=true` (159), LLM bucket only 47/100 | [QUERY] T3 grouped by provenance | MEDIUM | `detected_by_agent` is `'orchestrator'` on 241/259 rows, so LLM-vs-floor attribution is partly inferred |
| 43 | 1 finding records a `write_finding()` failure (`Errno 13 Permission denied` on `/work/findings.jsonl`) | [QUERY] `select … from findings where description ilike '%permission denied%'` → 1 row, scan `4ebd576b` | HIGH | Mechanism-level; value not reproduced |
| 44 | Proxy host bind-mount is 1.5 GB, `root:root`, mode 644 | [QUERY] `docker inspect logging-proxy --format '{{json .Mounts}}'` + `ls -la` on the data dir | HIGH | Structural secret-exposure surface |
| 45 | Per-scan `agent.log` writes a generated admin API key in plaintext | [QUERY] `agent.log` line 1 of scan `f7e8262e` (value withheld) | HIGH | Structure only; no value reproduced |
| 46 | `tool.started` log lines carry no command/tool field | [QUERY] raw-shape inspection of `event_type=tool.started` lines | HIGH | Forced duplication analysis to move to `tool_invocations` |
| 47 | Repo unmodified by this audit | [QUERY] `git rev-parse --abbrev-ref HEAD` → `feat/alpha-observability`; `--short HEAD` → `f75608f` (unchanged from assignment) | HIGH | Read-only honoured |

**Sampling disclosure.** No sampling was required for the artifact and database questions: all 43 workdirs, all 24,630 proxy calls, all 348 messages, all 987 worker runs and all 37,047 tool invocations were processed in aggregate. The only partial coverage is that **16 of 43 scans have no `logs/agent.log`** (agent containers are `--rm`; those scans predate log persistence), so log-derived counts (C.3) reflect the **27 scans that do have a log** and I have labelled them as such throughout.

**Not available / not attempted.** Per-scan attribution of proxy calls (impossible — see #6); raw prompt/response content (deliberately not read, for secret hygiene); a controlled test of the `checked_at=""` fail-open (would require triggering a scan — out of scope under the read-only constraint).

---

## Bottom line for the lead

1. **Coverage blind spot confirmed and quantified: 11.6% of scans (5/43) route through the logging proxy; 88.4% are invisible to it. But the deeper defect is that even the 5 proxied scans have zero attribution** — the proxy cannot tie a call, a 429, or a token to a scan. Fixing coverage means making the proxy the default `api_base` **and** adding a scan/tenant header, not just pointing more scans at it.
2. **The anti-fabrication machinery works.** 0 pre-scan confirmations in 301 fired tokens, the `_registration_floor` gate fired and rejected stale callbacks, and 36.9% of linked callbacks were honestly downgraded. I found no false OOB confirm. That is the strongest part of the design.
3. **The thesis is undermined elsewhere, in three places:** (a) 68.3% of ledger cells are auto-closed `na` and only 0.28% carry a finding, so "coverage" is substantially declared rather than earned; (b) 0 of 301 OOB evidence rows are back-linked to a finding and `findings.jsonl` carries no `oob_token`, so the flagship proof mechanism has no reconstructable audit trail; (c) `agent_messages` persists only assistant turns, so the conversation behind every disposition is unrecoverable.
4. **The LLM is not carrying the product.** 348 messages vs 37,047 tool calls (1:106); 41.4% of tool calls are self-issued by the deterministic floor; 17 scans did real work with zero model messages; floor+OOB findings are 100% verified while the LLM bucket is 47%. Meanwhile `worker_runs.findings_count` over-reports by 139× and cost is 0.0000 against 51.9M prompt tokens. WS-1's error classes are consistent with this: the driver fails (`max_turns_exceeded` 950×) without having decided anything.
5. **Three cheap, high-value fixes**, in order: make `_registration_floor` fail **closed**; add the `finding_id` back-link on OOB evidence and an `oob_token` field to `findings.jsonl`; default `cost_cap_usd` to a non-zero value and actually record `cost_usd`.
# CONSOLIDATED EVIDENCE LEDGER
**Agent `research-agent-falcon-02`** · repo `autocan` @ `feat/alpha-observability`/`f75608f` (READ-ONLY, unmodified)
Confidence: **HIGH** = direct code read or SQL at cited line this engagement · **MEDIUM** = doc/competitor claim · **LOW** = inference · **UNVERIFIED** = source unavailable (stated).
Source types: **[CODE]** file:line read · **[QUERY]** exact read-only command + result · **[COMPETITOR]** competitor-research file · **[DOC]** named doc · **[INFER]** labelled inference · **[LEAD]** verified by lead after subagent completion.

Rollup: 78 rows. **HIGH 61 · MEDIUM 9 · LOW 3 · UNVERIFIED 5.** Per-workstream detail remains in the six subagent reports.

---

## A. THROUGHPUT & SCAN TIME (WS-1)

| # | Claim | Source | Conf | Notes |
|---|---|---|---|---|
| A1 | Wave loop lives in `Father.run`; `engine/run.py` is the entrypoint/finalizer | [CODE] `engine/father.py:1727-1930`; `engine/run.py:167-374` | HIGH | `run.py` has no wave loop |
| A2 | Recon = 214 s = 3.3% of an ~108 min scan | [QUERY] agent structlog `phase.started` 20:08:50 → `phase.finished` 20:12:24 | HIGH | |
| A3 | Wave-boundary DB reads cost 1.9–3.4 ms each; ~40–50 ms/boundary | [QUERY] `psql \timing`: count_open 3.288 ms, full-grid join 3.403 ms, coverage_counts 2.952 ms, reclaim predicate 1.947 ms | HIGH | **decisive for H1 refutation** |
| A4 | Only 2 waves in 108 min (~54 min/wave) | [QUERY] exactly 2 `governor.decision` events | HIGH | governor once per wave iteration |
| A5 | Mean tool concurrency 0.67, peak 6, over 6,447 s with pool cap 4 | [QUERY] `tool.started`/`done` sweep, area/span | HIGH | ⇒ ~83% of slot time is inference wait |
| A6 | Floor fired 2,725 of 4,152 tool calls; 1,427 left for 29 workers (49 each) | [QUERY] `exploit_floor.complete` fired counts | HIGH | floor does ~2× the fleet's tool work |
| A7 | Exploit floor consumes 86% of its 1200 s budget per wave (541 s, then 806 s) | [QUERY] `exploit_floor.complete` + container env | HIGH | |
| A8 | 63/63 recorded worker turns ended `max_turns_exceeded`; zero normal completions | [CODE] workdir `decisions.log`, full file | HIGH | model never converges inside turn budget |
| A9 | Spinning worker: 2,654 s elapsed, `findings_count=0`, still `running` | [QUERY] live `worker_runs` — `batch1-b-7-bunny` | HIGH | |
| A10 | Live `SCANNER_ENGINE_WORKER_WALL_S=86400`, not 5400 | [QUERY] `docker inspect scanner-agent-84aea81a7e43` | HIGH | **refutes the 90-min-wall premise** |
| A11 | Wall resolved to **0 s** in scan `799ceec5`; 16/16 workers killed, scan ran 1.5 min, 130/130 retired, status `completed` | [QUERY] `GROUP BY left(error,60)` → `worker backstop 0s exceeded \| 13 \| avg 2s`; `worker wall cap 0s exceeded \| 3 \| avg 0s` | HIGH | `"0"` forwarded because non-empty |
| A12 | `SCANNER_ENGINE_WORKER_WALL_S` has no zero-guard, contradicting `0 ⇒ unlimited` convention | [CODE] `engine/fleet.py:28` vs `config.py:464`, `father.py:860-862` | HIGH | |
| A13 | Progress watchdog defeated by tool churn (`tool_calls` increment counts as progress) | [CODE] `father.py:1328-1336` | HIGH | nominal 20-min `STUCK_WINDOW_S` only cuts silent workers |
| A14 | live_convergence overshoots 120 s cadence by 7–15× (gaps 2–29 min), inline on sync loop | [QUERY/LOG] `reconcile.tick` gaps incl. 29, 14, 17, 17 min | HIGH | vs `SYNC_INTERVAL_S=120` |
| A15 | live_convergence default is `True`, contradicting its own docstring "default OFF" | [CODE] `config.py:401` vs `father.py:973` | HIGH | doc/code contradiction |
| A16 | 48.5% of worker runs died on `ChatCompletion response has no choices` (471 runs) | [QUERY] error histogram across 987 runs | HIGH | largest single error class |
| A17 | 91 worker runs hit 429 rate limits | [QUERY] error histogram | HIGH | secondary LLM-capacity signal |
| A18 | `time_cap_seconds` NULL on all scans since 09-28 ⇒ no soft-cap drain | [QUERY] `scans.time_cap_seconds` | HIGH | poller SIGKILL is the only stop |
| A19 | 53 `worker_runs` rows stuck `running` (avg 335,428 s) | [QUERY] status group-by | HIGH | bookkeeping leak; lifetime stats unreliable |
| A20 | Wave claims ~48 cells (`fanout × 12`) but 11–12 batches observed | [CODE] `father.py:1139,1384` vs [LOG] `batch0-b-0..b-10` | **UNVERIFIED** | not reconciled against `compose_batches`; flagged not guessed |

---

## B. LEDGER INTEGRITY & COVERAGE HONESTY (WS-1 + WS-6, lead-verified)

| # | Claim | Source | Conf | Notes |
|---|---|---|---|---|
| B1 | Claim owner is `wave{N}`; workers are `batch{N}-{bid}-{model}` — mismatch by construction | [CODE] `father.py:1874` vs `father.py:1275` | HIGH | acknowledged in-repo at `ledger/service.py:1479-1482` ("matches 0 rows (B1)") |
| B2 | **0 of 971** worker IDs ever appear as `ledger_cell.claimed_by` | [QUERY] `SELECT count(*) FROM (SELECT DISTINCT worker_id FROM worker_runs) w WHERE EXISTS (…)` → `0` | HIGH | decisive |
| B3 | Release routed around the mismatch via `release_cells_by_ids` (cell_id-keyed) | [CODE] `father.py:1358-1362`; `ledger/service.py:1476-1505` | HIGH | so the mismatch is **latent**, not an active time sink |
| B4 | Exploit floor claims under `floor-{family}` and has **zero** release/reclaim calls | [CODE] `exploit_floor.py:4890`; `Select-String 'release\|reclaim'` → **0 matches in 5,285 lines** | HIGH | strongest single code finding |
| B5 | 7,364 of 8,320 stale claims are `floor-*`; **100% have expired leases** | [QUERY] `ledger_cell where claimed_by is not null` grouped | HIGH | `claimed_by` is not a truthful ownership signal |
| B6 | 1,660 cells stranded `testing` with expired lease in one live scan | [QUERY] `GROUP BY claimed_by,state` with `lease_expired` count | HIGH | blocks `scan_is_complete` and quiescence |
| B7 | `attempts` exceeds the repo-default cap of 3 (364@4, 125@5, 158@6) | [QUERY] attempts histogram over 70,781 cells | HIGH | only possible if release/reclaim never run |
| B8 | Mass-retire turns untested cells into a green `completed` | [CODE] `finalize.py:455-464`; gate `config.py:451` **default ON** | HIGH | |
| B9 | **LEAD-INDEPENDENT:** `dbf83a85` = 3406 attempted / 3598 applicable, status `completed` | [LEAD-QUERY] `SET search_path TO tenant_xbow; … HAVING count(*) FILTER (WHERE state='attempted') > count(*)*0.9` | HIGH | 94.6% untested. 8 scans match this shape |
| B10 | **LEAD CORRECTION to WS-1:** `dbf83a85` has 26 `confirmed` + 166 `tested_clean` = **192 resolved (5.3%)**, not 0 | [LEAD-QUERY] same result set | HIGH | finding stands; WS-1's number was wrong |
| B11 | `SCANNER_LEDGER_COMPLETE_RATIO=0.98` declares complete with 2% open; docstring claiming otherwise is false | [CODE] `ledger/service.py:1181,1184-1200` | HIGH | `open_n != 0` does not gate the ratio branch; read once at import |
| B12 | Single-probe cells promoted to `tested_clean` (`methods_used >= 1`), overriding the ≥2-method bar | [CODE] `finalize.py:442-449` | HIGH | |
| B13 | Wave-loop quiescence is **fail-CLOSED** | [CODE] `father.py:1439-1441` returns True on read error; `attack_surface.py:178-183` re-raises | HIGH | the hypothesised high-value defect is **not** present here |
| B14 | Quiescence has one latent fail-open branch (`surface is None` → "drained") | [CODE] `father.py:1435-1436` | HIGH | unreachable in production |
| B15 | 68.3% of cells auto-closed `na` (48,322/70,781) | [QUERY] `tenant_xbow.ledger_cell` state + `na_reason` census | HIGH | coverage is substantially self-declared |
| B16 | Only 195/70,781 cells (0.28%) carry a `finding_id` | [QUERY] filter count | HIGH | |
| B17 | 87.1% of `attempted` cells were never probed (`attempts=0`) | [QUERY] `attempts=0 AND state='attempted'` → 7,371 of 8,771 | HIGH | mass-retire, not the attempt cap |
| B18 | Only 82 cells (0.9%) hit the designed attempt cap | [QUERY] `na_reason='attempted: attempt cap reached'` → 82 | HIGH | designed terminator nearly inert |
| B19 | Worst unresolved classes: `forced_browse` 518, `priv_esc` 488, `auth_bypass` 455, `excessive_data` 450, `rate_limit` 328 | [QUERY] per-class rollup | HIGH | high-value classes, mostly never claimed |
| B20 | `materialize_cells` spawns every class × every element then applicability-filters ⇒ `na` flood is a cross-product artefact | [CODE] `ledger/service.py:670` (`for vc in VulnClass:`), `:679`, `:688`; `ledger/applicability.py:191-196` | HIGH | mechanism root cause |
| B21 | AI classes are **already** double-gated at materialize — the in-tree precedent for the fix | [CODE] `ledger/service.py:671` (`continue` before the applicability call) | HIGH | comment: "AI classes materialize ONLY on a detected AI surface" |
| B22 | `na_reason` flood: `not a websocket surface` 1,203 / `not a graphql surface` 1,195 / `not a webhook surface` 1,163 | [QUERY] `na_reason` histogram | MEDIUM | counts inherited from WS-1; lead confirmed the mechanism (B20) not the exact counts |
| B23 | `claim_cells` filters `applicable = true AND state IN ('untested','testing')` ⇒ `na` cells never handed out | [CODE] `ledger/service.py:1398-1399` | HIGH | |
| B24 | Claim exclusivity **exists**: `SELECT … FOR UPDATE SKIP LOCKED` + `attempts = attempts + 1` | [CODE] `ledger/service.py:1393-1417`, docstring `:1359-1372` | HIGH | **corrects WS-1's "double-claim" framing — it is re-sweep, not double-claim** |
| B25 | `blocked` is counted **inside** `resolved` ⇒ must not be reused for never-tested cells | [CODE] `reporting/service.py:121` | HIGH | WS-6 design constraint |
| B26 | `LedgerCell.state` has no CHECK constraint ⇒ a new state value needs no migration | [CODE] `db/models/tenant.py:248-252,261-263` | HIGH | |

---

## C. TELEMETRY FORENSICS (WS-2)

| # | Claim | Source | Conf | Notes |
|---|---|---|---|---|
| C1 | Proxy covers only `nvidia/nemotron-*`: 3 distinct `model_req`, 2 `model_fwd`, 0 non-NVIDIA | [QUERY] `GROUP BY model_req, model_fwd` over 24,630 calls | HIGH | directive assumption **confirmed** |
| C2 | Measured coverage **11.6%** (5 of 43 scans); 15.8% of completed/partial scans | [QUERY] scan roster × `scans.status` | HIGH | the assumption did not state the ratio |
| C3 | Proxy is opt-in per scan-roster `api_base`, not per provider — 11 nemotron scans, only 5 proxied | [QUERY] `engine_models ilike '%logging-proxy%'` | HIGH | sharpens the assumption |
| C4 | **0** proxy rows reference any proxied `scan_id` — the `calls` table has no scan/tenant column and the client sends no correlating header | [QUERY] presence-only prefix scan over all 24,630 blobs | HIGH | telemetry is unattributable **even where proxied** |
| C5 | Proxy capture stopped 2026-09-29T23:06Z while ≥4 later scans ran | [QUERY] `min/max(ts)` vs `max(started_at)` | HIGH | stale DB, not merely incomplete |
| C6 | `request_json` totals **1.56 GB** (p50 58 KB, p99 166 KB); `prompt_tokens` NULL on 6,492 (26.4%) | [QUERY] `sum(length(...))` | HIGH | sizes only, no content read |
| C7 | Real ledger rework is **37 events across 5 scans** (0.4%) — the thrash hypothesis is largely refuted | [QUERY] per-cell sequences, re-entry to `testing` | HIGH | |
| C8 | Actual ledger waste is **2,074 same-state re-appends with changed evidence** (22.8% of 9,096 rows) | [QUERY] `json.dumps(evidence)` comparison | HIGH | re-test, same verdict |
| C9 | Only **3** `confirmed` rows ever (0.03%); 2 backtracked `confirmed→tested_clean` | [QUERY] state census | HIGH | |
| C10 | 96,765 OOB interactions mirrored → 301 token hits → 138 linked (0.14%) | [QUERY] re-run of `correlate`/`_scan_scoped` logic | HIGH | product logic, not approximation |
| C11 | **0 pre-scan confirmations** — no callback fired before its scan began | [QUERY] join `oob_token` × `scans`, `fired_at < started_at` | HIGH | **strongest anti-fabrication evidence in the engagement** |
| C12 | `_registration_floor` gate fired: rejected 2 stale callbacks | [QUERY] same re-run | HIGH | the gate works |
| C13 | 36.9% of linked callbacks (51/138) honestly downgraded from the agent's classification | [QUERY] re-derived `classify_oob` | MEDIUM | re-implementation, not runtime observation |
| C14 | **0 of 301** OOB evidence rows carry `finding_id`; `findings.jsonl` has **no** `oob_token` key (0/642) | [QUERY] `evidence_object`; key census | HIGH | flagship proof has **no audit trail** |
| C15 | 161/301 tokens unlinked (no cell, no endpoint) | [QUERY] `cell_id is null and endpoint is null` | HIGH | |
| C16 | `max_turns_exceeded` = **950 of 1,019** error lines (93.2%) | [QUERY] 27 `agent.log` files, 126,407 lines | HIGH | 16 of 43 scans have no `agent.log` |
| C17 | 429 pressure on **24 of 27** logs | [QUERY] regex census | HIGH | |
| C18 | `ledger.resolve.*_unmatched` = **12,734** (10,135 `update_unmatched` + 2,599 `finding_unmatched`); 760 are placeholder endpoints | [QUERY] endpoint-stripped histogram | HIGH | new error class |
| C19 | Context reset/compaction = **3**; explicit retry = **1** | [QUERY] regex census | HIGH | continuity/retry are **not** the failure mode |
| C20 | 25.7% of tool commands are exact duplicates (9,529/37,047); 38.1% duplicate `output_summary` | [QUERY] `count(*)-count(distinct command)`; `md5` distinct | HIGH | |
| C21 | `agent_messages` = 348, **all `role='assistant'`**; 0 user/tool turns persisted | [QUERY] `GROUP BY role` | HIGH | the conversation justifying each disposition is unrecoverable |
| C22 | Ratio **348 messages : 37,047 tool calls = 1:106** | [QUERY] two counts | HIGH | answers Q4 |
| C23 | `exploit_floor` issued **41.4%** of tool calls (15,337) | [QUERY] `agent_id='exploit_floor'` | HIGH | |
| C24 | **17 scans** did real work (tool calls > 0) with **zero** model messages | [QUERY] cross-query | HIGH | worst: `68a58881` = 12,143 tools, 38 findings, **1** message |
| C25 | `cost_usd`=0 on 0/348 messages; `cost_spent`/`cost_cap`=0 on 0/43 scans, against 51.9M prompt tokens | [QUERY] rollup | HIGH | no cost feedback loop |
| C26 | `tokens_in=0` on 239/348 messages (all space-bunny) | [QUERY] per-message | HIGH | provider-dependent accounting |
| C27 | Fail-open anti-fabrication gate: `checked_at=""` on timeout ⇒ `since=None` ⇒ time gate silently vanishes | [CODE] `run.py:109` → `service.py:159-161` → `registry.py:158` | HIGH code / MEDIUM impact | did not fire in this data (39/39 populated) |
| C28 | Proxy DB is 1.5 GB, `root:root` mode 644; per-scan `agent.log` line 1 writes a generated admin API key in plaintext | [QUERY] `docker inspect` + `ls -la`; log line 1 | HIGH | **values redacted/withheld** |
| C29 | One finding records `Errno 13 Permission denied` on `findings.jsonl` | [QUERY] `ilike '%permission denied%'` | HIGH | mechanism only |

---

## D. COMPETITOR GAP (WS-3)

| # | Claim | Source | Conf | Notes |
|---|---|---|---|---|
| D1 | **Corpus-wide: `attack graph`, `capability token`, `OOB`, `interactsh`, `dnslog` = 0 occurrences; `out-of-band` = 1** | [CODE] grep over `competitor-research/**` | HIGH | **core falsification result — no competitor publicly specifies a capability-token chain mechanism** |
| D2 | xBow validators: "Sometimes this process leverages a large language model; in other cases, we build custom programmatic checks" | [COMPETITOR] `xbow/pages/…blog-top-1-how-xbow-did-it.md:47` | HIGH | **verification is not deterministic** |
| D3 | xBow's showcased proof instrument is an agent-written assertion (`return 'Invalid padding' not in response.text`) | [COMPETITOR] `xbow/pages/page-https-xbow-com-platform.md:222` | HIGH | invariant authored per-task by the agent |
| D4 | xBow client-side method: "a headless browser visits the target site to verify that the JavaScript payload was truly executed" | [COMPETITOR] same as D2 | HIGH | **weaker than Abhedi Red's sink-level instrumentation** |
| D5 | xBow's one OOB attempt **failed** in its own published trace | [COMPETITOR] `…platform.md:173,186,206` | HIGH | only `out-of-band` mention in the corpus |
| D6 | xBow 5-stage Learn→Map→Coordinate→Attack→Prove; agents "retired after each mission to avoid bias" | [COMPETITOR] `…platform.md:28-38` | HIGH | chaining asserted, not specified |
| D7 | xBow deliverable = browsable trace, numbered versioned artifacts (`3.bash`, `12.python`, `90.python`) | [COMPETITOR] `…platform.md:42,71-335` | HIGH | the buyer-visible artifact bar |
| D8 | xBow concedes autonomous failure: agent "never reached even a leak"; "You still need to prove exploitability" | [COMPETITOR] `xbow/pages/…blog-dead-letter-cve-2026.md:103,106` | HIGH | **direct market validation of the product thesis, from a competitor's Head of Security Lab** |
| D9 | Escape: shared message bus (recon/xss/sqli/idor/ssrf/auth/rce) + knowledge store, "one agent's discovery shapes what the next one tries" | [COMPETITOR] `escape/pages/…blog-introducing-casca.md:53,70` | HIGH | the only described cross-step signal propagation |
| D10 | Escape Reporter agent "independently reproduces each one on the live target… Deliberately isolated from exploitation agent-to-agent messaging" | [COMPETITOR] same file | HIGH | separation of duties, but **LLM-based, not deterministic** |
| D11 | Escape negative-control test proving a pricing flaw (arbitrary price rejected, negative quantity accepted) | [COMPETITOR] same file `:85` | HIGH | closest competitor analogue to a control-diff oracle; chosen by an LLM agent |
| D12 | Escape multi-identity: "several user identities at the same time, each in its own isolated browser session"; "a second account typically uncovers 30–50% more issues" | [COMPETITOR] same file `:47,161` | HIGH | mechanism + quantified buyer payoff |
| D13 | Escape: proven findings become unlimited DAST regression tests re-running on every release in CI/CD | [COMPETITOR] same file `:16,53` | HIGH | **the time-axis artifact carry-over no competitor-of-Abhedi-Red matches** |
| D14 | Escape "cascade" blog is a single prompt-injection bypass in 2 requests, not exploit-path chaining | [COMPETITOR] `escape/pages/…blog-how-cascade-explo.md` | HIGH | **filename overstates** |
| D15 | Escape methodology relies on human confirmation ("Manual spot-checks of representative findings") | [COMPETITOR] `escape/pages/…blog-methodology-how-w.md` | HIGH | |
| D16 | FireCompass chaining trigger: `Trigger: a confirmed, exploitable finding` | [COMPETITOR] `firecompass/pages/…adversarial-exposu.md:62` | HIGH | the only explicit confirm→chain rule among the three |
| D17 | FireCompass "No exploit, no alert"; findings "executed safely against the live target and confirmed"; "under 2%" FPR | [COMPETITOR] same file `:53,134` | MEDIUM | gate asserted, **oracle not described** |
| D18 | FireCompass "append-only audit logs with cryptographic timestamps"; mapped to PCI DSS 4.0 / SOC 2 / DORA / ISO 27001 | [COMPETITOR] same file `:116-121,135` | MEDIUM | strongest audit-trail claim in market |
| D19 | FireCompass XBEN 104/104 with disclosed protocol (fixed single frontier model, first-attempt scored separately) | [COMPETITOR] `firecompass/pages/…xben-benchmark-rep.md` | MEDIUM | full report is **lead-gated**, model not disclosed |
| D20 | FireCompass pages carry a fetch-provenance anomaly ("WebFetch was blocked… retrieved via `curl`") | [COMPETITOR] `firecompass/pages/…firecompass-agenti.md:240` | MEDIUM | lower-provenance scrape; treat quotations accordingly |
| D21 | **DOSSIER DEFECT 1:** `COMPARISON.md:14,25` claims Escape "≤4% FPR" and a "BLST algorithm, 100+ GraphQL tests" citing `escape.tech/product/dast` — **neither string is in the cited page** | [COMPETITOR] `COMPARISON.md:14,25` vs `escape/pages/…product-dast.md` (read in full) | UNVERIFIED | **quarantined; do not launder into fact** |
| D22 | **DOSSIER DEFECT 2:** `COMPARISON.md:14` claims FireCompass has a "four-stage validation pipeline (…signature evaluation)" — the AEV page describes a single "validation gate" | [COMPETITOR] `COMPARISON.md:14` vs `…adversarial-exposu.md` | UNVERIFIED | **quarantined** |
| D23 | Independent: plain Codex CLI/GPT-5 solved 70–81/104 of xBow's own benchmark; MAPTA 76.9% | [COMPETITOR] `xbow/external-research.md` | MEDIUM | casts doubt on orchestration moats |
| D24 | Independent: "No independent teardown, source-code review, or academic paper analyzing FireCompass's internal architecture was found" | [COMPETITOR] `firecompass/external-research.md` | MEDIUM | FireCompass column is weakest-evidenced |
| D25 | xBow self-disclaims its own benchmark: "published in 2024… now outdated and should no longer be used" | [COMPETITOR] `xbow/pages/…blog-benchmarks.md:28,38,42` | HIGH | a rare honest artifact |
| D26 | Abhedi Red control-paired oracles: `DiffVerdict`/`response_diff`, `parse_time_blind(control_out, payload_out)`, `diff_access`/`diff_cross_tenant`/`diff_resource_ref`, canaries | [CODE] `engine/exploit_floor.py:723,1223-1265,1297,1387,1424,1784` | HIGH | **unique vs all three competitors** |
| D27 | Abhedi Red OOB: live `https://oast.fun`, autolink default-ON, per-payload token registry, correlation, **registration time floor** | [CODE] `config.py:174,183`; `oob/registry.py:55,72,88,165`; `oob/service.py:151,188,391` | HIGH | the time floor is what no competitor mentions |
| D28 | Abhedi Red sink-level browser canary attribution (`location.hash`/`.search`/`window.name`/`document.URL`) | [CODE] `docker/browser/browser_server.py:354,380-383` | HIGH | finer-grained than D4 |
| D29 | Ledger records **whether the oracle fired**, per cell | [CODE] `ledger/service.py:136 (_oracle_fired),185,190,205` | HIGH | coverage+proof accounting in one place |
| D30 | Report narrative layer is a **5,965-byte LLM prompt merger** | [CODE] `reporting/narrative.py:45,68` | HIGH | prose-first — the inversion the thesis forbids |
| D31 | Independent re-production is **conditional and LLM-based**; skipped for every caller except engine-v2 | [CODE] `finalize.py:104-107` | HIGH | "Every other caller … verification is simply skipped" |
| D32 | Strongest proof paths are default-OFF, fail-closed | [CODE] `finalize.py:328`; `chain/floor.py:105-122`; `config.py:249` | HIGH | cuts both ways |
| D33 | Ledger/`chain_node` are `scan_id`-scoped; no cross-release retest found | [CODE] `finalize.py:65-66`; absence in `ledger/service.py` | MEDIUM | absence-of-evidence, stated as such |

---

## E. H2–H6 HYPOTHESIS VERIFICATION

| # | Claim | Source | Conf | Notes |
|---|---|---|---|---|
| E1 | System prompt is 17,504 chars, constant across all workers/scans | [CODE] `engine/methodology.py:13-251` | HIGH | |
| E2 | ~95% of a worker prompt is static-per-group; worker-unique share **1.5–5.1%** of ~40.4k chars | [QUERY] real `father._task_for(...)` decomposition, 6 groups × 3 waves | HIGH | |
| E3 | Six group tasks overlap **95.0%** and do **not** diverge across waves 0/1/2 | [QUERY] `difflib.SequenceMatcher.quick_ratio` per wave | HIGH | zero drift on deepening passes |
| E4 | **Target selection is a ledger claim, upstream of prompt construction** — falsifies H2's causal claim | [CODE] `father.py:1874-1886`; `ledger/service.py:1393-1417` | HIGH | prompt is an execution wrapper |
| E5 | A state-aware capability layer already exists (`_capability_context`, `_boss_tick`) | [CODE] `father.py:1520-1541, 1787` | HIGH | boss bias advisory-only (`service.py:1332-1346`) |
| E6 | Capability token **is** carried hop→hop and drives dispatch | [CODE] `chain/floor.py:397-404, 426-441` | HIGH | **refutes H3's literal claim** |
| E7 | PoC bound to persisted chain nodes; **195/195** live nodes carry it, **0** carry `evidence_path` | [CODE] `chain/service.py:167-179`; [QUERY] `chain_node` attrs predicate counts | HIGH | |
| E8 | **Raw evidence is NOT carried into hop N+1** — `_Ctx` = `{sh,surface,tdir,wd,cookies,bearer,dom}`, all hops `(ctx,url,param,res)` | [CODE] `chain/floor.py:134-143`, `:393` | HIGH | **the exact gap** |
| E9 | Hop targets come from frozen module tables (`_METADATA_URLS` 3, `_BUCKET_URLS` 3, `_SECRET_FILES` 8) | [CODE] `chain/floor.py:59-101` | HIGH | never derived from hop N's observation |
| E10 | `_hop_credential` is a deliberate no-op — all five CREDENTIAL-granting classes are terminal by construction | [CODE] `chain/floor.py:385-390`; `chain/capabilities.py:49-52,56` | HIGH | |
| E11 | **0 `executed_chain` findings in 43 scans** despite `SCANNER_EXECUTED_CHAIN_FINDINGS=true` | [QUERY] `findings` where `verification_method='executed_chain'` → 0; [INFER] flags from `docker inspect` | HIGH | 195 nodes / 464 edges inferred, none executed onward |
| E12 | `chain_node` capability histogram: session 56, pii_read 32, internal_http 25, cross_principal_read 23, metadata_access 20, db_read 16, rce 16 | [QUERY] `chain_node` histogram | HIGH | |
| E13 | Browser layer has **exactly 3 endpoints**; no fourth route exists | [CODE] `browser_server.py` `^@app\.` → 732/737/1032 | HIGH | WS-3 and WS-6 independently confirmed |
| E14 | `navigate→act→re-navigate→assert` is **structurally inexpressible** — no action/selector/assertion field in either request model | [CODE] `browser_server.py:715-718` (`CrawlRequest`), `:1020-1023` (`InstrumentRequest`) | HIGH | mechanism, not inference |
| E15 | `/instrument` = one page, one `goto`, fixed 3-source plant, page closed per URL | [CODE] `browser_server.py:1086-1136` | HIGH | |
| E16 | Only browser statefulness is a hard-coded operator-credential login, not caller-supplied | [CODE] `browser_server.py:673-712` | HIGH | |
| E17 | Finding-level live capture is a documented deferred gap, verbatim TODO | [CODE] `browser_ingest.py:397-399` | HIGH | quoted exactly in WS-6 |
| E18 | Model can reach `/crawl` only; `/instrument` is a one-shot fallback that self-skips if a manifest exists | [CODE] `engine/tools/browser.py:65-69`; `browser_fallback.py:174-175` | HIGH | |
| E19 | HAR-slice-per-finding **is** implemented + evidence rows carry `screenshot`/`har`/`oob_token` | [CODE] `browser_ingest.py:381-436`; `finalize.py:310,612`; `tenant.py:237-241` | HIGH | do not overstate the gap |
| E20 | `/instrument` records **no** HAR today | [CODE] `browser_server.py:1065` `new_context(…)` lacks `record_har_path` (vs `:803-805`) | HIGH | load-bearing for new oracle artifacts |
| E21 | GraphQL oracle exists with 5 deterministic proof types | [CODE] `engine/graphql_authz.py` (full) `:201,242,268,333,338` | HIGH | **refutes H5** |
| E22 | WS/SSE/webhook oracle exists with frame/replay/two-account verdicts | [CODE] `engine/channels.py` `:200,206,162,211` | HIGH | |
| E23 | AI/MCP oracle exists (canary echo + recorded tool invocation) | [CODE] `engine/ai_redteam.py:64,95`; `recon_floor.py:529-533` | HIGH | |
| E24 | **LEAD-VERIFIED:** all three new-tech flags are **ON** live — `SCANNER_GRAPHQL_AUTHZ_ENABLED`, `SCANNER_CHANNEL_ORACLES_ENABLED`, `SCANNER_AI_REDTEAM_FLOOR` = `true` | [LEAD-QUERY] `docker inspect scanner-cp --format '{{range .Config.Env}}…'` | HIGH | |
| E25 | 1,203 `websocket` cells all `na`, 0 attempts, 0 methods; `channels.*` appears 0 times in 17,079 log lines | [QUERY] `ledger_cell` group-by; `docker logs` histogram | HIGH | |
| E26 | Zero `ai_endpoint` inventory elements and zero `ai_*` cells across 43 scans | [QUERY] `inventory_element` kind histogram | HIGH | double gate never opened |
| E27 | `oracle_map` routes graphql/ws/webhook + all five `ai_*` to `nuclei` (no group entry ⇒ config catch-all) | [CODE] `oracle_map.py:21-39,44,52,17` | HIGH | two vocabularies that do not meet |
| E28 | `_oracle_fired` is a **substring match** on tool name in `methods_used` | [CODE] `ledger/service.py:151` | HIGH | |
| E29 | Real GraphQL/WS/AI findings are demoted to `pending_oracle` because the gate is hard-coded on and can never match | [CODE] `ledger/service.py:224` (`skill_gate=True`), `:226` | HIGH | **buyer-visible: findings parked in review** |
| E30 | `_record_coverage` emits `url#field`; `_norm` does not strip fragments ⇒ coverage record silently discarded | [CODE] `exploit_floor.py:4815`; `ledger/service.py:82-93,814-816,821-843` | HIGH | a second independent break in the GraphQL chain |
| E31 | `required_oracle_for` has only **two** consumers, both skill-gate paths | [CODE] `ledger/service.py:148, 221` | HIGH | bounds the oracle_map fix |
| E32 | `run_channels_sweep` is **cell-driven**, not schema-driven | [CODE] `channels.py:451-453` → `attack_surface.py:129` → `service.py:1393-1417` | HIGH | **corrects the inherited brief — fix materialization first** |
| E33 | `_sweep_graphql` **is** schema-driven and consults no cell | [CODE] `exploit_floor.py:4766-4768` (`schema is None` ⇒ return) | HIGH | it is starved by detection, not by applicability |
| E34 | Agent container gets exactly **one** per-scan mount; `docker.sock` absent; caps hardened | [CODE] `scheduler/worker.py:920-955` | HIGH | refutes H6's "under-specified" half |
| E35 | `/skills` baked into the image; 70 skills, 647,328 chars, nothing bounds a per-run read | [CODE] `docker/agent/Dockerfile:55-56`; [QUERY] size sum | MEDIUM | per-turn caps exist, no per-run total |
| E36 | `methods_used` is **77% LLM free-text** and is re-injected per re-claim | [QUERY] method-string histogram; [CODE] `father.py:360-367` | HIGH | the real bloat driver, not the skills catalog |
| E37 | 2,062 cells claimed ≥2×; 158 at the live cap of 6; 3 scans hold 66% of all attempts | [QUERY] attempts histogram + per-scan rollup | HIGH | attempt cap is the only brake |
| E38 | 37,074 invocations / 987 runs → 259 findings ≈ 143 tool calls per surviving finding | [QUERY] cross-table counts | HIGH | |
| E39 | `findings.jsonl` write-truncation hazard already closed | [CODE] `engine/tools/files.py:59` `_APPEND_ONLY` | MEDIUM | |

---

## F. DECISION LAYER (WS-5)

| # | Claim | Source | Conf | Notes |
|---|---|---|---|---|
| F1 | Boss tick is awaited **inline** on the wave loop; placement is load-bearing and preserved | [CODE] `engine/father.py:1787` | HIGH | comment at `:1782-1786` |
| F2 | Only bound on the planner is `asyncio.wait_for(wall_s)`, **default 180 s** | [CODE] `engine/boss.py:47, 94` | HIGH | no per-call/per-scan tick bound |
| F3 | **`_sample_open` returns `[]` on ANY exception** | [CODE] `engine/father.py:1129-1134` | HIGH | load-bearing root of F4 |
| F4 | `[]` ⇒ every new objective rejected **and every prior one retired, terminally** (carried forward only if `status != "rejected"`) | [CODE] `engine/plan_gate.py:203-211, 226-234, 61` | HIGH | **one transient DB error permanently strips boss bias for the scan** |
| F5 | Plan backing source is a **200-row** window ordered by `_CLASS_PRIORITY`, and unlike `claim_cells` it **ignores the attempt cap and live leases** | [CODE] `engine/attack_surface.py:103`; `ledger/service.py:1210-1224` vs `:1388-1402, 1400` | HIGH | an objective can read `active` while backed entirely by unclaimable cells |
| F6 | A claim-identical count already exists and is unused by the gate | [CODE] `ledger/service.py:1508-1521` | HIGH | |
| F7 | Class priority reaches SQL **only** as `array_position` in `ORDER BY`; the `WHERE` is a constant ⇒ advisory-only is structural | [CODE] `ledger/service.py:1396-1403` | HIGH | basis of the I-DIRECTIVE invariant |
| F8 | `plan_gate.py` is already implemented, pure, wired, merge-not-replace, with 16 unit tests; `backing`/`rejected` are gate-owned | [CODE] `engine/plan_gate.py` (236 lines); tests `tests/unit/engine/test_plan_gate.py` | HIGH | **extend, do not replace** |
| F9 | `playbook_policy_view` discards `phases[].tools`, `.goal`, `behavior.*`, `blocker_handling.*`; no `vuln_class` field exists in either schema | [CODE] `engine/policy.py:103-121`; `playbooks/schema.py:9-55`; `playbooks/loader.py:9-47` | HIGH | a playbook has **zero** ledger effect |
| F10 | The only playbook→engine behavioural channel is a hardcoded frozenset → 150 invocations | [CODE] `entrypoint.py:97-119` | HIGH | |
| F11 | Shipped `playbooks/deep_offensive_vapt.yaml:11-14` declares `no_persistence`/`in_scope_only`, which are **not schema fields**, silently dropped by `extra='ignore'` | [CODE] `playbooks/schema.py:9-13`; YAML | HIGH | safety clauses fail **open** |
| F12 | `resolved_cells` has exactly 3 occurrences repo-wide: 1 declaration, 2 reads — **zero assignments** | [CODE] `engine/worker.py:20`; `engine/telemetry.py:183, 201`; all 8 `WorkerResult(...)` sites omit it | HIGH | `resolved_count` ≡ 0 by construction |
| F13 | `resolved_count` is published to the buyer | [CODE] `reporting/effort.py:64`; `api/schemas.py:609` | HIGH | reads 0 ⇒ reports 0 |
| F14 | `findings_count` rollup computes the truth then **returns it without writing back** (`remainder = total − attributed` is negative ⇒ `return total`) | [CODE] `engine/telemetry.py:263, 273, 281, 282` | HIGH | **the missing write is the entire 139× bug** |
| F15 | Consumer reads the **per-worker** rows, not the rollup's return value | [CODE] `reporting/effort.py:63`; `api/schemas.py:608` | HIGH | |
| F16 | Unmatched `(endpoint, class)` keys are **logged and dropped**, never queued (durable) | [CODE] `ledger/service.py:840-843, 873, 949` | HIGH | 12,734 accumulate with no scan-scoped home |
| F17 | `_reconcile_census` already lifts `resolve_unmatched` to a first-class per-tick number | [CODE] `engine/father.py:95-120` | HIGH | F16's fix makes it actionable |

---

## G. LEAD VERIFICATION (post-subagent, independent)

| # | Claim | Source | Conf | Notes |
|---|---|---|---|---|
| G1 | **CONFIG DRIFT — lead-only finding.** `SCANNER_ENGINE_POOL_HARD_CAP=8` on `scanner-cp` but `=4` in `scanner-agent-*` | [LEAD-QUERY] `docker inspect` both containers | HIGH | **no subagent caught this.** The engine believes it has double the pool it does; every concurrency conclusion must be read against 4 |
| G2 | `SCANNER_ENGINE_FANOUT=8`, `BATCH_MAX_CELLS=8`, `SYNC_INTERVAL_S=120`, `FLOOR_BUDGET_S=1200`, `LEDGER_LEASE_S=1800`, `LEDGER_ATTEMPT_CAP=6`, `ORACLE_FIRST=true`, `SKILL_GATE=true`, `MACHINE_CLOSE=true`, `PLAYBOOK=true`, `BOSS=true` | [LEAD-QUERY] `docker inspect scanner-cp` env | HIGH | corroborates WS-1/WS-5 live-config claims |
| G3 | **LEAD CORRECTION:** `dbf83a85` resolved = 192/3598 (5.3%), not 0 | [LEAD-QUERY] per-scan rollup | HIGH | see B9/B10 |
| G4 | 8 scans report `completed`/`cancelled` with >90% of applicable cells `attempted` | [LEAD-QUERY] `HAVING … > count(*)*0.9` | HIGH | |
| G5 | `scanner_finalize_retire_unreached: bool = True` — the mass-retire default | [CODE] `src/scanner/config.py:451` | HIGH | |
| G6 | `_COMPLETE_RATIO` read once at module import from env | [CODE] `src/scanner/ledger/service.py:1181` | HIGH | cannot be retuned on a running process |
| G7 | `resolved_cells` confirmed: 1 declaration + 2 reads, no assignment | [CODE] `worker.py:20`, `telemetry.py:183, 201` | HIGH | independently re-grepped by lead |
| G8 | 10 agent folders exist under the base; `research-agent-falcon-02` holds all my writes; `falcon-01` and the other 8 never written to | [LEAD] `Get-ChildItem` on base | HIGH | write-discipline verified |
| G9 | WS-5 cited a sibling agent's folder as a source for live flags | [LEAD] WS-5 report §H ledger | HIGH | rule violation; lead re-verified every flag itself (G2) |
| G10 | WS-6 could not reach the Docker daemon; its inherited `na` counts remain UNVERIFIED at source | [LEAD] WS-6 ledger | UNVERIFIED | mechanism (B20) independently confirmed by lead |
| G11 | 16 of 43 scans have no `agent.log`; WS-2's error census reflects the 27 that do | [LEAD] WS-2 sampling disclosure | HIGH | stated in WS-2 |
| G12 | Directive HEAD `1c5551d` vs actual `f75608f`: 2 docs-only commits, `git diff --stat` over `src docker config.py` **empty** | [CODE] `git log`/`git diff` | HIGH | branch of record materially identical for code |

---

## H. NOT FOUND IN REPO (valid, respected results)

| Item | Result |
|---|---|
| Any capability-token / attack-graph data model at a competitor | **not public** (D1) |
| Any deterministic-oracle **registry** at xBow, FireCompass, or Escape | **not public** (D2, D17) |
| Any OOB/callback architecture at FireCompass or Escape | **not public** (D5) |
| Append-only / non-repudiation / framework-mapping claim in Abhedi Red | **not found in repo** (D18 contrast) |
| Cross-release retest / regression mechanism | **not found in repo** (D33) |
| A fourth browser endpoint, or any action/selector/assertion request field | **not found in repo** (E13, E14) |
| Any use of the existing `_walk_ref` / `_extract_object_ref` by the chain floor | **not found in repo** (WS-4) |
| Any per-identity browser session store | **not found in repo** (WS-6) |
| A `release_cells` caller in `exploit_floor.py` | **not found — 0 matches in 5,285 lines** (B4) |
| An `oob_token` key in `findings.jsonl` | **not found — 0 matches in 642 rows** (C14) |
| Any `finding_id` on OOB evidence rows | **not found — 0 of 301** (C14) |
| User/tool turns persisted in `agent_messages` | **not found — 0 rows** (C21) |

---

## I. KNOWN GAPS IN THIS LEDGER

1. **B22 counts** (1,203/1,195/1,163) are inherited from WS-1; the mechanism (B20) is lead-confirmed but the exact counts were not re-measured.
2. **A20** (batch-count arithmetic) remains unreconciled — flagged, not guessed.
3. **C13** (36.9% downgrade rate) comes from a re-implementation of `classify_oob`, not runtime observation.
4. **WS-4 and WS-5 and WS-6 reports were truncated in the lead's context window.** Full text is on disk in each workstream folder. Lead read the visible portions; the remaining sections are un-reviewed by me but were produced by the named subagent against the same constraint set.
5. **No exploit payload, shell command, or runbook appears anywhere in this ledger** (R1). All offensive capability is described as mechanism, state, or contract.
6. **No secret value appears anywhere in this ledger** (R5). One admin API key and one JWT were encountered and are withheld.

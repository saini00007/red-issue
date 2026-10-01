# Source C — Live Server Telemetry (read-only, 2026-10-01 ~03:15 IST)

Host: `abhedi` (ssh, passwordless, read-only commands only — no INSERT/UPDATE/DELETE, no docker
stop/rm/kill, no file writes on the remote server). All figures below are aggregate counts /
SELECT-only query results. No raw prompts, tokens, credentials, or full exploit narratives are
reproduced — free-text fields (`verification_method`, `error`) are bucketed by keyword or truncated
to short prefixes. One `findings.verification_method` row contained a literal CTF-style flag value
(`flag{...}`) from the benchmark target (OWASP VulnerableApp) — omitted here; it is not a
third-party secret, but it isn't load-bearing evidence either.

## Live fleet snapshot (`docker ps` on abhedi)
One scan actively running at capture time: `scanner-agent-84aea81a7e43` / `toolserver-*` /
`browser-*` / `zap-*`, target = `vulnerableapp` (OWASP VulnerableApp benchmark container),
scan_id `84aea81a-7e43-495c-9974-ca064ddd3552`, tenant `16e69f07-f908-482b-8fc5-492852a61a91`.
Also present: `scanner-cp`, `scanner-postgres`, `scanner-pgbouncer`, `scanner-redis`,
`scanner-frontend`, `scanner-nginx`, `logging-proxy`, `vaultwarden` (infra, not queried).

## [QUERY] Postgres `tenant_xbow` schema (via `docker exec scanner-postgres psql`, read-only SELECTs)

**scans** — status distribution (all-time): cancelled 19, completed 18, failed 4, partial 1, running 1.
Completed-scan duration: n=40, avg 4067s, median 598s, max 64395s (~17.9h outlier).

**Smoking gun — a zombie "partial" scan with a dead container, never reconciled:**
`scan_id=3b4803e4-f683-4a31-8ea5-fd9fa1a9afe5`, status=`partial`, phase=`exploitation`,
`started_at`=2026-09-20 14:24 UTC, `last_heartbeat_at`=2026-09-20 15:00 UTC (i.e. it stopped
heartbeating **36 minutes** into the scan). At capture time that heartbeat is **~888,556s
(~10.3 days) stale**. `docker ps -a --filter name=3b4803e4` returns **nothing** — the agent
container is long gone (ephemeral `--rm`) — yet the DB row still shows a non-terminal `partial`
status with no `failure_reason` set. Confidence: HIGH (direct query + direct docker check).

**ledger_cell** — state distribution across all scans: `na` 48323, `attempted` 8771, `untested`
5299, `tested_clean` 4862, `testing` 2775, `blocked` 454, `confirmed` 297.
Applicable cells: 22,011 (`applicable=true`). Of those: **confirmed=297, tested_clean=4862,
attempted(attempt-capped)=8771, untested(never touched)=5299, blocked=454, testing(in-flight)=2775**.
**More applicable cells hit the attempt cap without resolving (8771) than were ever definitively
closed clean or confirmed combined (5159).** This directly corroborates the existing
`docs/reports/2026-09-29-coverage-ceiling.md` framing.

Per-vuln-class breakdown (full 57-row table saved in this folder's raw query log) shows two
distinct failure shapes:
- Classes with **zero `tested_clean` AND zero `confirmed`** despite hundreds of attempt-capped
  cells: `ssi` (0/0, 258 capped), `quota_abuse` (0/0, 279 capped), `workflow_abuse` (0/0, 279
  capped), `graphql` (0/0, 5 capped of only 8 applicable). These classes have **no negative
  (clean) oracle at all** — a cell either eventually confirms or burns its attempts; there's no
  code path that can say "tested, not vulnerable" for them.
- `websocket`: **100% `not_applicable`** across all 1203 cells system-wide — the applicability
  gate for this class appears to never fire `true` on any scanned target in this dataset.

**worker_runs** — status: `error` 578, `ok` 264, `partial` 75, `running` 53 (out of 970).
**Majority of all worker runs end in `error`.** Duration for finished runs: n=917, avg **531s**,
p90 **1786s**, max 6685s. Only **1 of 917** finished within ±60s of a 5400s/90-min wall-cap
window. **This refutes a "90-minute wall-cap dominates the schedule" framing for this fleet** —
workers are overwhelmingly terminating in single-digit minutes, far short of any wall cap.

`worker_runs.error` top buckets (truncated to 80 chars, first token only where free text):
"ChatCompletion response has no choices (possible provider error payload)" **471** (the single
largest bucket by far, ~53% of ALL worker runs), 429/rate-limit variants **~91** combined,
"preempted: contract satisfied" 59, "preempted: worker backstop 0s exceeded" 13, 500-class
provider errors 9, "worker wall cap 0s exceeded" 3.
Model/provider mix for this fleet: `openrouter/stealth/space-bunny-alpha` 594 runs (by far the
most-used, and the most failure-prone given its stealth/free-tier nature — not separately broken
out per-model here since `error` isn't joined to `model` in this pass), `nvidia/nemotron-3-*`
variants ~308 combined, `anthropic/deepseek-chat` 19 (routed through the internal proxy), a few
long-tail free models.
**[INFER, MEDIUM]:** the dominant observed failure mode is upstream LLM-provider unreliability
(malformed/empty completions from a free-tier "stealth" OpenRouter model), not a ledger
claim/release defect — code-level confirmation needed on how a `ChatCompletion ... no choices`
error is classified against a cell's `attempts` counter (does a pure-provider failure burn an
attempt the same as a genuine failed probe?).

**decisions.log (live scan, filesystem, not DB)** — 59/59 lines (**100%**) are the literal string
`max_turns_exceeded`, tagged with worker labels like `[batch1-b-9-bunny·turn7]`. Zero other decision
types appear in this scan's log. **[UNVERIFIED — needs code check]** whether `decisions.log`'s
writer is *designed* to log only turn-cap events (making this normal) or whether this scan
genuinely produced no other loggable decision — flagged for the code-reading pass.

**ledger_updates.jsonl (live scan)** — 1916 lines; state-transition distribution: `testing` 1816,
`tested_clean` 93, `blocked` 7 (this stream appears to log attempt-start + a subset of terminal
states, not every state). Endpoint+vuln_class thrash check: max repeat count for any single
(endpoint, vuln_class) pair in this scan is **4**; 0 pairs exceed 10 — **no severe thrash observed
in this specific run** (tempers, doesn't confirm, a blanket "thrash is endemic" claim — prior
thrash findings may be target/config-dependent).

**oob_interactions.jsonl (live scan)** — 185 lines, protocol split dns=111 / http=74. No
`classification`/`classified_as`/`class` key exists in this file's schema — the honest
protocol-classify logic (if any) isn't stored in this particular file; needs a code check of
where `classify_oob` (per `[[OOB false-positive fix 2026-09-18]]` memory) actually persists its
verdict.
**oob_registry.jsonl (live scan)** — 712 lines, keyed by `token`/`vuln_class`/`endpoint`/`param`.
Class distribution of registered OOB tokens: deserialization 168, xxe 115, ssrf 62, cmdi 55,
xss_reflected 50, lfi 50, rfi 50, open_redirect 50, ssti 47, xss_stored 27 (+ long tail).

**agent_messages** — only **17 of ~43 scans** in the whole dataset have *any* row (most scans:
zero rows — an instrumentation/coverage gap in this telemetry table itself). For the 17 that do:
avg max turn_index **3**, min **1**, max **7** — consistent with the platform's known
short-conversation pattern (`CLAUDE.md` deviation #5: models "tend to halt after 5-10 turns even
with the reprompt loop" — observed max here is even lower, 7). `role` column: 100% `assistant`
(314 rows) — no `user`/`system` rows are ever recorded in this table, i.e. it appears to log only
one side of the conversation. Token/cost totals across all recorded messages: 50.7M tokens in,
848K tokens out, **`cost_usd` sums to $0.00** — a cost-observability gap for non-billed
(OpenRouter free-tier / stealth) routes, separate from the known non-Anthropic-uncapped flag.

**findings** — verified=true 201 / verified=false 53. severity: high 130, medium 80, critical 32,
low 10, info 2. category top: rate_limit 58, auth_bypass 52, ssrf 28, idor_bola 16, sqli 14,
security_headers 12, deserialization 10 (+ long tail, several free-text/duplicate category labels
observed, e.g. both `sqli` and presumably-legacy long-form CWE strings coexisting — a category
taxonomy normalization gap).
`verification_method` free text (86 distinct values, mostly count=1) bucketed by keyword
(non-exclusive, a row can match >1 bucket): oob-callback/interactsh 22, explicit
re-reproduction language ("re-ran", "reproduced twice", etc.) 20, curl reproduction 18, sqlmap 9,
differential/control-test framing 9, forged token/cookie 8, `exploit_floor:*` deterministic-oracle
tag 6, cross-user replay 5, dalfox tool-assisted 5, JWT forgery/tamper 4.
**[INFER, LOW]:** the platform's proof discipline is real in practice (most verified findings cite
a concrete reproduction action, not prose alone) but is captured as **free text**, not a
structured proof-type enum — matching WS-4's chain-design gap (no `proof_type` field to build a
capability-token contract on top of).

**chain_node / chain_edge** — 188 nodes / 449 edges total, spread across only **13 of ~43 scans**
(12 scans have edges). The live scan itself has the most of any scan: 37 nodes. **This refutes a
strict "chaining never happens" reading of H3** — the graph does populate, at least for some
scans/targets — but doesn't by itself confirm hop-to-hop proof-threading (needs code check of
whether a hop's evidence is passed into the next hop's *worker input*, or only linked
after-the-fact for reporting).

**evidence_object** — kind distribution: `finding` 295, `recon` 21. No distinct `chain` or
`browser`-specific kind observed in this snapshot.

**tool_invocations**: 35,723 total (not broken down further in this pass — high-volume table,
avoided a full scan to keep this read-only pass cheap).

## Scope notes / what was deliberately NOT pulled
- `logging-proxy` `proxy_log.db` (full prompt/response pairs for NVIDIA/nemotron routes) —
  **not queried** this pass; would require a separate, more careful redaction pass given it holds
  raw prompt content (R5). Flagging as a gap rather than guessing its contents.
- `vaultwarden` container — not touched; unrelated to this research (credential vault, out of
  scope).
- Per-scan `report.json`/`report.md`/`report.html`, `findings.jsonl`, `recon.json` for the live
  scan — only listed (sizes/timestamps), not read in full, since the DB `findings`/`ledger_cell`
  tables already give the same signal in aggregate, safer form.
- Agent-authored exploit scripts on the live scan's workdir (`run_sqlmap*.sh`, `blind_extract.py`,
  `dump_u2.py`, `xss_oob_browser.py`, etc.) — filenames/count/timestamps only. Contents were
  **not read or reproduced** (R1: design not exploitation) — their existence/cadence (7 iterative
  `run_sqlmap*.sh` variants across ~25 minutes of wall-clock) is itself a behavioral signal
  (iterative trial-and-error rather than a single confirmed injection) worth the code-reading pass
  checking against H2/H6, but no payload content is included here.

# WS-2 · Telemetry Forensics

## Question List & Diagnostic Findings

### Q1: From `ledger_updates.jsonl`: What are the cell-state thrash patterns?
* **Empirical Analysis of Workdir Artifacts:**
  - In scan `38c703c0-f4b8-4c27-a455-a525aeedb86c`, workers wrote 45 KB of updates marking dozens of cells as `blocked` with:
    `"Host unresolvable (Docker DNS SERVFAIL, curl exit 6)"` [CODE/WORKFLOW].
  - Stale brief propagation: Wave 0 workers recorded target unreachable; this belief was written to `scan_brief.md`. Subsequent workers repeatedly confirmed the target was down, until `batch1-b-0-bunny` discovered the DNS entry was restored to `172.21.0.6` in 5ms, noting: *"Every prior 'unreachable' ruling out in the brief is invalid and should be retired."* [DOC `decisions.log`].
  - Recon phantom endpoints: In `38c703c0`, shell variable interpolation failed during recon (`$p` unquoted), injecting `http://vulnerableapp:9090$p` into `recon.json`. This generated 6 phantom cells in `ledger_cell` that each worker spent tool calls attempting to test and ultimately marking `blocked`.
  - Re-claim churn: When `scanner_engine_batch_dispatch=true`, worker completion triggers `release_cells_by_ids`. Cells not marked terminal (`tested_clean`/`confirmed`/`blocked`) are reopened to `untested`/`testing`, resetting leases. Because weak models often exhaust their turns without calling `record_coverage`, cells churn between `testing` and `untested` until hitting `attempts >= 3`.

### Q2: From `oob_interactions.jsonl`: What is the honest-classification behavior?
* **Empirical Findings:**
  - **Local Control Pollution:** In scan `infinity-close-review.md` [DOC], 11 SSRF findings were marked `verified=true`. However, 5 of them had endpoints:
    - `(no target - control only)`
    - `CONTROL-ONLY-NOT-SENT`
    - `NEVER-CONTACTED-CONTROL`
    - `local-control`
    - `none`
  - In `38c703c0-f4b8-4c27-a455-a525aeedb86c/oob_interactions.jsonl` [CODE/WORKFLOW]:
    A local curl health-check from the worker (`User-Agent: curl/8.21.0`) against the OOB domain was logged as an HTTP interaction.
  - **Shared Buffer Ingestion:** In scan `68a58881`, `oob_interactions.jsonl` reached 907 KB (4,340 lines). Over 99% of entries (4,266 lines) were LDAP/DNS background noise from a shared interactsh container, including interactions timestamped a month prior (`2026-08-29`), because the interactsh client dumps its entire unpurged rolling session buffer upon poller synchronization.

### Q3: From `agent.log` and proxy logs: What are the model-driver errors and context-reset frequencies?
* **Swallowed Transport Failures (F3):**
  - In scan `68a58881-ae3b-4f36-90a9-bf254da13fcb` (17.5 hours on `nemotron-3-ultra-550b` via NVIDIA free-tier endpoint):
    - Proxy database recorded **2,022 HTTP 429 (rate-limit) responses** and **2,701 HTTP 500 server errors** [DOC `FINAL-REPORT.md:14`].
    - Zero of these 4,723 errors were logged in `agent.log` or surfaced as engine events because the OpenAI SDK (`max_retries=8`) silently retried them, creating hidden latency stalls where workers appeared frozen for minutes.
  - RateLimitError re-raises as generic `status="error"` in `agents_runtime.py:824`, which `father.py` logs as a generic failure without backoff or model switching.

### Q4: From `agent_messages`: What are the turn counts — did the model actually drive?
* **Turn Statistics & Telemetry Gap:**
  - [QUERY] `SELECT scan_id, role, count(*), AVG(tokens_in), AVG(tokens_out), MAX(turn_index) FROM tenant_xbow.agent_messages`:
    - 7 out of 17 recorded scans have **only 1 or 2 rows** in `agent_messages`, despite running 5 to 10 waves of 6–12 workers.
    - Reason: Deep workers frequently hit `MaxTurnsExceeded` (`max_turns=40`). In earlier code revisions, this set `result = None`, causing `_record_turn` to return early before inserting into `agent_messages`.
    - Where turns were recorded, token ratios reached extreme asymmetry:
      - Scan `68a58881`: Average tokens in = 1,017,905; Average tokens out = 7,019 (**145:1 ratio**).
      - Scan `0ebea923`: Average tokens in = 1,006,201; Average tokens out = 8,949 (**112:1 ratio**).
    - Uncached prompt retransmission: Every turn re-transmits the 18 KB system prompt, 26 KB scan brief, and full accumulated tool history without prompt caching on non-Anthropic endpoints.

---

## Observed-Failure Catalog (Aggregate Telemetry)

| Failure Mode | Affected Asset / Scope | Observed Count / Scale | Root Cause Mechanism | Blast Radius |
| :--- | :--- | :--- | :--- | :--- |
| **Untested Cell Mass-Retirement** | All completed scans | **7,371 cells (82.8% of `attempted`)** | `finalize.py:454-468` bulk UPDATE retires all open cells with `unreached` reason | **CRITICAL** (Masks 80%+ untested surface as complete) |
| **Model 429/500 Swallowing** | Scan `68a58881` | **2,022 x 429, 2,701 x 500** | SDK `max_retries=8` hides rate limits; no engine backoff | **CRITICAL** (Triples scan runtime) |
| **Control-Probe OOB False Positive** | Scan `infinity` | **5 of 11 SSRF findings** | Worker health checks against OOB server recorded as target callbacks | **HIGH** (False positive verified findings) |
| **Shared Interactsh Buffer Bloat** | Scan `68a58881` | **4,266 / 4,340 lines (99%)** | Unscoped interactsh buffer poll ingests cross-scan noise | **MEDIUM** (Disk bloat, telemetry pollution) |
| **Telemetry Blackout on MaxTurns** | Scans `68a58881`, `dbf83a85` | **Only 1 row in `agent_messages`** | `MaxTurnsExceeded` resulted in `None` result bypassing telemetry insert | **HIGH** (Cost and activity blind spot) |
| **Phantom Recon Endpoints** | Scan `38c703c0` | **6 phantom cells (`$p`)** | Shell variable expansion bug in recon scripts | **LOW** (Wasted worker turn budget) |

---

## WS-2 Evidence Ledger

| Claim | Source (type + location) | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| Stale brief propagated DNS unreachable belief across workers | [DOC] `38c703c0/decisions.log:1-40` | HIGH | Workers retired ~25 cells before `batch1-b-0` proved target was up. |
| Recon script injected literal `$p` endpoint into inventory and ledger | [CODE/WORKFLOW] `38c703c0/ledger_updates.jsonl:10-18` | HIGH | Leaked unquoted shell variable `$p` generated multiple blocked cells. |
| 5 of 11 verified SSRF findings were worker self-probes / test controls | [DOC] `/home/admin/research/2026-09-29-deepdive/infinity-close-review.md:15-25` | HIGH | Endpoints like `(no target - control only)`, `local-control`, `none`. |
| 99% of `oob_interactions.jsonl` was unpurged historical noise | [DOC] `/home/admin/research/2026-09-29-deepdive/CASE_STUDY.md:65` | HIGH | 4,266 out of 4,270 lines had empty correlation IDs. |
| Model token ratio reached 145:1 input:output due to lack of caching | [QUERY] `tenant_xbow.agent_messages` GROUP BY `scan_id` | HIGH | 1,017,905 avg tokens in vs 7,019 tokens out on Nemotron. |
| Multiple major scans have <=2 rows in `agent_messages` | [QUERY] `tenant_xbow.agent_messages` | HIGH | Confirmed across `68a58881`, `dbf83a85`, `0ebea923`. |

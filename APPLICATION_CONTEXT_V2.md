# Abhedi Red — Application Context V2 (current state + full implementation program)

**Date:** 2026-09-26 · **Status:** living document. Purpose: one exhaustive reference covering the platform as it
runs today **and** everything the merged program is implementing (unified roadmap + code-verified core-engine gaps
+ in-flight work + a complete feature inventory). Supersedes/extends
[`APPLICATION_CONTEXT.md`](APPLICATION_CONTEXT.md); **CODE IS GROUND TRUTH** — where this doc and code disagree,
fix the doc. Assembled deterministically from six code-verified section passes (2026-09-26).

**STATUS LEGEND (authoritative — every section uses these labels):** `BUILT-AND-LIVE` (runs in a default compose deploy) · `BUILT-BUT-OFF` (flag) · `IN-FLIGHT` (committed on feat/alpha-observability, not yet on the fixes/critical-improvements main branch or deployed) · `PLANNED` (roadmap phase) · `PARKED` (do-not-build) · `DEAD-CODE`. §2–§4/§6 also use the short forms `LIVE`=`BUILT-AND-LIVE`, `OFF(flag)`=`BUILT-BUT-OFF`, `DEAD`=`DEAD-CODE`, plus the finer refinements each section legend names.

**Maintenance:** any change that adds/alters/removes behavior updates the relevant section here in the same commit.
Companion live status: [`roadmap/2026-09-26-implementation-tracker.md`](roadmap/2026-09-26-implementation-tracker.md).

---

## Table of contents
1. Architecture, orchestration paths, container topology, request lifecycle
2. Subsystem reference — part 1 (API, DB, scheduler, ledger, engine-v2 core)
3. Subsystem reference — part 2 (hooks/tools, planner/chain, OOB, reporting, playbooks, infra, frontend, skills, tests)
4. Current detection & proof capability inventory (what we find AND prove today)
5. The implementation program (roadmap phases + core gaps + in-flight work + parked)
6. Config/flag reality + master feature inventory + glossary

---

## 1. What it is · architecture · orchestration paths · container topology · request lifecycle

> **Status labels follow the authoritative STATUS LEGEND at the top of this doc.** **Code is ground truth; every concrete claim below is cited `file:line` and was re-read against the file, not trusted from prose.**

### 1.1 What Abhedi Red is

**Abhedi Red** (repo dir still `autocan`, Python package still `scanner`) is a **multi-tenant, black-box + gray-box (credentialed) web-application & API penetration-testing platform**. An operator submits a *scope* (targets, optional gray-box credentials, optional playbook, and — `IN-FLIGHT` — free-text instructions and a per-scan model roster); the platform spins up an **ephemeral fleet of Docker containers** running LLM-driven pentest agents *plus* a deterministic (non-LLM) exploit/recon backstop against the target, persists findings/coverage/evidence/attack-chains to Postgres, and produces a buyer-grade VAPT report (JSON / Markdown / HTML + a cross-scan regression diff).

Design pillars (all `BUILT-AND-LIVE` unless noted):
- **Coverage as a DB predicate.** "Is this scan done?" is answered by a ledger work-queue (one row per surface-element × vuln-class), not by a wall clock — see the ledger section.
- **Deterministic floor beside the LLM.** A non-LLM "weapon sweep" (`exploit_floor.py`) and recon floor (`recon_floor.py`) run every wave so coverage never depends solely on what the model decides to do.
- **Honesty gates.** OOB callbacks are classified by wire-protocol not by the agent's self-label; a post-scan independent verifier re-reproduces self-declared criticals/highs and downgrades the unconfirmable ones.
- **Model-agnostic fleet.** Anthropic models drive the native Claude Agent SDK runtime; any OpenAI-compatible endpoint (self-hosted vLLM, LiteLLM/OpenRouter proxy fronting DeepSeek/GLM/GPT/etc.) drives a second runtime — selected per-model at `run.py:208-213`.

### 1.2 Full stack

| Layer | Technology | Notes |
|---|---|---|
| Language / async | Python 3.11, asyncio-first | `uv` for deps |
| Web / control plane | FastAPI + Pydantic v2 (`main.py`, `api/`) | uvicorn target `scanner.main:app` |
| ORM / DB | SQLAlchemy 2.x async + Alembic; Postgres 16 | **schema-per-tenant** isolation via `SET search_path`, no `tenant_id` ORM filter |
| Pool | PgBouncer, **transaction-pooling mode** (`docker-compose.yml:67`) | a commit resets `search_path` → routes that commit must re-`SET` |
| Cache / bus | Redis 7 (redis-py async) | Redis Streams event log + pubsub → WebSocket relay |
| Agent orchestration | Claude Agent SDK (Anthropic) **+** an OpenAI-Agents-SDK-compatible driver (non-Anthropic) | two pluggable runtimes: `runtimes/claude_sdk.py`, `runtimes/agents_runtime.py` |
| Container orchestration | Docker SDK for Python | only `scanner-cp` mounts `/var/run/docker.sock` |
| Logging / HTTP | structlog, httpx | |
| Quality | ruff, mypy --strict, pytest + pytest-asyncio | `make test` runs zero-infra (integration tests self-skip) |
| Frontend | Next.js 16 + React 18 | hand-rolled client router, not file-based; polls REST + one scan WebSocket |

### 1.3 The three orchestration paths — check the flags before you trust anything

**The single most important architectural fact: three distinct scan-orchestration code paths exist, and only one runs by default.** The branch is decided at the *agent* entrypoint `main()`:

- `entrypoint.py:1122-1123` — `code = asyncio.run(_run_engine_v2()) if EntrypointEnv().engine_v2 else asyncio.run(run_scan())`. Engine-v2 is checked **first** and short-circuits the other two entirely.
- `EntrypointEnv.engine_v2` reads the **raw env** `SCANNER_ENGINE_V2`, defaulting to `"false"` (`entrypoint.py:202`) — but this default almost never bites, because the CP's `worker.py:596` forwards `str(settings.scanner_engine_v2).lower()` into every spawned agent, and `settings.scanner_engine_v2` defaults `True` (`config.py:258`) *and* `docker-compose.yml:162` pins it `true`. The raw-env `"false"` default only applies to a bare `uv run`/test launch that bypasses `worker.py`.

| Path | Where | Gate to reach it | Status |
|---|---|---|---|
| **Engine-v2** (Father / Fleet / Governor + deterministic floor) | `agent_runtime/engine/*` | `SCANNER_ENGINE_V2=true` (forwarded default + compose default) | **`BUILT-AND-LIVE` — THE path.** Multi-model wave-dispatch, exploit floor every wave. Start tracing at `engine/run.py:run_engine()` (`run.py:166`) → `father.py:Father.run()` (`father.py:1674`). |
| **Legacy "planner" (Alpha-Team)** | `agent_runtime/planner/*` | only if `SCANNER_ENGINE_V2=false` **and** `settings.scanner_orchestrator=="planner"` (`entrypoint.py:882`) | **`DEAD-CODE` in production.** Real, tested, human-approval-gated escalation design — just never imported in a default deploy. |
| **Legacy "reprompt"** (single-agent continuation loop) | `entrypoint.py:run_scan()` (`entrypoint.py:530`) | same gate, `scanner_orchestrator=="reprompt"` | **`DEAD-CODE` in production.** This is the Phase-6 "native Claude Code" pivot the root `CLAUDE.md` still narrates — that narrative describes a path a default deploy no longer runs. |

**Two config-vs-compose contradictions to know before running the process bare:**

1. **`scanner_orchestrator` default contradicts its own comment.** `config.py:135-136`'s comment says *"'reprompt' … (default)"* directly above `config.py:138` which defaults the field to `"planner"`. `docker-compose.yml:121` overrides to `${SCANNER_ORCHESTRATOR:-reprompt}` — matching the *comment*, not the *code*. Moot under compose (engine-v2 short-circuits first), a real footgun for a bare `uv run`/test/future-compose-without-this-line, which would silently get the untested planner path. (Tracked `[HIGH]` in `CLAUDE.md`.)
2. **`scanner_engine_batch_dispatch`: code default `False` (`config.py:308`), compose sets `true` (`docker-compose.yml:189`).** So live deploys run Father's newer endpoint-scoped **batch-pool** dispatch (`father.py:1830` → `_run_batch_pool`, `father.py:1335`), *not* the legacy `build_specs`+`_run_floor_and_fleet` path (`father.py:1833`) that Father's own comments call the default. Both dispatch branches are present in the same wave loop; the flag picks one per wave.

**Practical consequence:** the `hooks/*.py` guardrail stack (except `scope.py`/`safety.py` internals reused by `engine/guardrails.py`), `pipeline/summarizer.py`, `planner/*`, and `approval/*` are **legacy-only and not exercised by a default scan**. `chain/capabilities.py` + `chain/service.py` are the one place the legacy and engine-v2 stacks genuinely converge (both import them, plus finalize + reporting).

### 1.4 Two-layer container topology

**Layer 1 — persistent stack** (`docker-compose.yml`, `make run`): 6 services on the `scanner-net` bridge:

| Service | Image / build | Role | Notable |
|---|---|---|---|
| `postgres` | `postgres:16-alpine` (pinned digest) | DB | loopback-bound `127.0.0.1:${POSTGRES_HOST_PORT:-5432}`; `POSTGRES_PASSWORD` fail-closed `:?` (`compose:10`) |
| `redis` | `redis:7-alpine` | cache/bus | `requirepass` from env (`compose:35`); loopback `127.0.0.1:6377` |
| `pgbouncer` | `edoburu/pgbouncer` | pooler | **transaction** pool mode (`compose:67`) |
| `scanner-cp` | build `docker/cp/Dockerfile` | FastAPI control plane | **the ONLY service mounting `/var/run/docker.sock`** (`compose:244`); also mounts `scanner_data`; API loopback `127.0.0.1:8011:8000` (reach it *through* nginx) |
| `frontend` | build `frontend/Dockerfile` | Next.js console | talks to `scanner-cp:8000` |
| `nginx` | `nginx:alpine` | sole host-facing ingress `:80` (`compose:276`) | re-resolves upstreams via Docker DNS; trusted source of `X-Real-IP` for rate limiting |

**Layer 2 — 5 ephemeral per-scan images**, spawned by `scanner-cp`'s `scheduler/worker.py:spawn_scan_containers()` (`worker.py:272`) via the Docker SDK — **not** services in compose, **not** built by `make run**:

| Image | worker.py cite | Role | Security posture |
|---|---|---|---|
| `scanner/agent:latest` | spawned in `spawn_scan_containers` | runs the LLM agent process | **no `docker.sock`**; non-root UID 1001; reaches Kali tools *only* via HTTP to sibling toolserver |
| `scanner/toolserver:latest` | `worker.py:412` | Kali-rolling, 40+ tools, generic `/exec` HTTP (`X-Exec-Token`) | agent's *only* path to `nmap`/`sqlmap`/… ; probed for `/healthz` at spawn (`_probe_toolserver_ready`, `worker.py:36`) |
| `scanner/browser:latest` | `worker.py:468` | Playwright/Chromium; deterministic scope-bound crawl `/crawl` + DOM-XSS `/instrument` | `BUILT-BUT-OFF`→ actually `SCANNER_BROWSER_ENABLED` default `true` (`compose:124`) |
| `scanner/zap:latest` | `worker.py:515` | OWASP ZAP; reuses toolserver's `exec_server.py` verbatim | `BUILT-BUT-OFF(SCANNER_ZAP_ENABLED)` — `false` in base compose (`compose:128`), forced `true` only by the gitignored `docker-compose.override.yml` |
| `scanner/tor:latest` | `worker.py:443` | SOCKS-only egress option | **no Makefile build target** — `docker build -t scanner/tor:latest -f docker/tor/Dockerfile .` by hand or Tor scans can't find the image |

`make build-images` builds agent/toolserver/browser/zap **only** — a fresh clone additionally needs the manual tor build before a Tor-mode scan can spawn.

**Known-issue on sizing (`[HIGH]`, `CLAUDE.md`):** `_container_mem_budget`/`_container_cpu_budget` (`worker.py:187`, `worker.py:218`) size each scan's containers against the *whole host's* RAM/CPU with no accounting for other running scans — up to 7 concurrent scans (see §1.6 claim step) each independently compute an un-shared "whole host" budget and can jointly over-commit.

### 1.5 Shared `scanner_data` volume / `$WORK_PATH`

All 5 ephemeral containers **plus** `scanner-cp` share one Docker named volume — compose name `scanner_data`, **actual name `abhedi_red_scanner_data`** (`docker-compose.yml:290-291`). The CP forwards it via `SCANNER_SHARED_VOLUME_NAME` (`compose:102`) into `worker.py`, which mounts a **per-scan subpath** into each container:
- agent mounts the subpath at `$WORK_PATH` (symlinked to `/work`; agent entrypoint silently defaults `WORK_PATH=/var/lib/scanner/_default` if unset);
- toolserver `cd`-prefixes into it; browser writes crawl/HAR/screenshots into it; ZAP gets a **real bind-mount** at `/zap/wrk` (`_zap_wrk_mount`, `worker.py:158` — a symlink previously broke ZAP's `/proc/mounts` check).

`/work/*.jsonl` (findings, ledger updates, exploit-floor signals, OOB interactions) is the **real cross-process shared memory of a scan** — the funnel every container writes and the finalize pass reads. If `SCANNER_SHARED_VOLUME_NAME` ≠ the compose volume's actual name, agent writes land where finalize never reads (silently loses findings) — this drifted before on a compose-project rename, hence the fail-loud comment at `compose:97-101`.

`docker-compose.override.yml` exists on the dev machine but is **gitignored** — a fresh clone runs the base file's more conservative defaults (ZAP off, `SCANNER_ENGINE_BATCH_MAX_CELLS=2` at `compose:194` vs the override's tuned "FAST" profile). Cross-machine behavior differences: check whether this file exists before blaming code.

### 1.6 Request lifecycle — traced end to end

1. **Submit** — `POST /api/v1/scans` → `create_scan` (`scans.py:133`). License check, encrypts gray-box creds (`encrypt_credentials`, `scans.py:148`), inserts a `Scan` row via `build_queued_scan()` (`scans.py:88`, `status="queued"` at `scans.py:113`) — the *same* helper the cron/schedule tick uses, so manual and scheduled scans are byte-identical. **`IN-FLIGHT`:** the row now also carries `instructions` (free-text operator guidance, migration `0018`) and `engine_models` (per-scan resolved model roster, migration `0019`) — `scans.py:127-128, 163-164`. The API never talks to Docker.
2. **Claim** — `ScanPoller` (background asyncio task from `main.py:60-64` lifespan; `scheduler/poller.py`) polls every 2s. **Two-phase** (`_poll_tenant`, `poller.py:429`): Phase 1 one short txn `SELECT … FOR UPDATE SKIP LOCKED` on `status=='queued'` up to the per-process cap (`poller.py:453`), flips to `status="running"` + `node_id` (`poller.py:460`); Phase 2 outside the lock does license + egress-retry then spawns. `ConcurrencyManager` cap = `MAX_THOROUGH=3` + `MAX_FAST=4` = **7, per-process (per-node), not cluster-wide**.
3. **Spawn** — `worker.py:spawn_scan_containers()` (`worker.py:272`): creates an isolated per-scan Docker network, mounts the per-scan volume subpath, spawns **toolserver first** (probes `/healthz`, raises if it crashed at boot — `worker.py:36`), then optional tor/browser/zap sidecars, then the agent with a large forwarded env block (~70 `SCANNER_ENGINE_*` knobs, pass-through-only-if-set — the allowlist at `worker.py:663-740`; a new agent-side flag missing from this list silently never reaches the container — the recurring "RUN-2 gap"). Per-scan `KALI_EXEC_TOKEN` isolates one scan's toolserver from another's. **`IN-FLIGHT`:** `engine_models` overrides `SCANNER_ENGINE_MODELS` (`worker.py:601`) and instructions ride as `SCAN_INSTRUCTION` (`worker.py:646`).
4. **Recon** — engine-v2: `Father.run()` calls `scan_ctx.recon.run()` (`father.py:1678`) → `ScopeRecon`/`recon_floor.py` deterministic floor (subfinder→httpx(+arjun)→katana + 5 gated depth stages), best-effort auth bootstrap (`_ensure_auth`, `father.py:1681`), writes the per-wave scan brief. OOB oracle is provisioned *before* the fleet (`run.py:189`, `_provision_oob`) so every worker gets a live callback domain (hard-capped so a slow oracle can't stall the run — `run.py:98-99`).
5. **Exploitation wave loop** — `Father.run()` `while True` (`father.py:1709`): each wave (a) materializes the ledger coverage grid + syncs `/work` JSONL to DB (`father.py:1713-1717`), (b) breaks on graceful-drain if the soft time-cap tripped (`father.py:1720`), (c) breaks on **real coverage-complete** (`_is_complete`, `father.py:1757`) or on **quiescence** (Governor says "partial" *and* no claimable cells left — `father.py:1784`), (d) atomically claims a disjoint cell batch (SKIP-LOCKED) and dispatches one worker per (target × phase-group) via `FleetManager` — batch-pool path (`father.py:1830`) under the live `SCANNER_ENGINE_BATCH_DISPATCH=true`, else the legacy floor+fleet path (`father.py:1833`), (e) runs the **deterministic exploit floor CONCURRENTLY** with the LLM wave, claiming a *disjoint* cell batch via the same SKIP-LOCKED mechanism so no cell double-fires, (f) chain-floor (`father.py:1846`) + escalation (`father.py:1851`) then loops. Stop is **progress-driven, not a clock**: both no-progress backstops (`_batch_budget_s`, `_stuck_window_s`) are OFF by default (compose:192-193 set batch-budget `0`; stuck timer disabled as of commit `36fece4`); the only hard hang-guard is `fleet.py`'s flat 5400s/90-min per-worker wall + the opt-in Governor caps.
6. **Finalize** — two-stage, on **every** exit path (`run.py:319-343`). `scan_ctx.finalize()` runs crawl/instrument/ZAP + ingest + dedup + chains + report; if a non-Anthropic verifier endpoint exists (`_verifier_endpoint`, `run.py:36`) and `SCANNER_ENGINE_VERIFY`≠0, the independent **A1 verifier** `finalize_scan()` (`run.py:332`, `agent_runtime/finalize.py:84`) re-reproduces self-declared critical/high findings and downgrades unconfirmed ones. **An all-Anthropic roster gets no A1 verifier** (`run.py:48-53` excludes anthropic providers — they can't drive the OpenAI-compatible verifier SDK). On the poller's *salvage* path (crash/cancel/GC-recovery) `_finalize()` (`poller.py:1454`) is the single idempotent funnel, but reproduction-verify self-skips (the poller process has no toolserver token).
7. **Report** — `reporting/service.py:build_report()` assembles the scored/deduped report from DB rows (JSON/Markdown/HTML) + a stateless cross-scan regression diff (`GET /scans/{id}/diff`).
8. **Terminal status** — canonical rule is `ledger.service.graceful_terminal_status()` (`"completed"` only if the ledger is genuinely resolved *and* had applicable coverage, else `"partial"`), imported by `poller.py` and legacy `entrypoint.py`. **Caveat:** `agent_runtime/finalize.py:490-492` **reimplements the same predicate inline** (`scan_is_complete() AND count_applicable_cells()>0`) rather than calling it, and only reconciles a scan already in `"failed"` status with ≥1 finding (`finalize.py:480-484`) — three call sites, equivalent-but-separate logic, kept in sync by convention not by a shared function.

### 1.7 New / in-flight items touching architecture & lifecycle

| Item | Status | Evidence |
|---|---|---|
| **Per-scan operator instructions** (free-text steering) | `IN-FLIGHT` (committed `a21890d`, on `feat/alpha-observability`, not on main) | migration `0018_add_scan_instructions.py`; `scans.py:127,163`; forwarded as `SCAN_INSTRUCTION` `worker.py:646` |
| **Per-scan engine-model routing** (per-scan roster override + presets `ENGINE_MODEL_PRESETS`) | `IN-FLIGHT` (`a21890d`) | migration `0019_add_scan_engine_models.py`; `scans.py:128,164,171-175`; overrides `SCANNER_ENGINE_MODELS` at `worker.py:601`, provider key at `worker.py:605` |
| **Dead-node scan recovery** (scans stuck in `killing`/`cancelling`/`closing` when their owning node died) | `IN-FLIGHT` (committed `1b2653c`) | `poller.py:738-779` GC recovery block resets to `queued`; motivated by a 2+ day stuck-scan production incident |
| **`.claude/workflows/` + `docs/roadmap/2026-09-25-*`** (orchestration v3 / pentest-team boss→manager→recursive-subs redesign, core-engine gap analysis) | `PLANNED` (roadmap docs only, untracked in git) | git status `?? .claude/workflows/`, `?? docs/roadmap/2026-09-25-*` — design/analysis, **no engine code path yet**; do not present as built |
| Model driver: per-key direct remote-provider path (no proxy) | `PARKED` | `CLAUDE.md` Deviation #9 — build only if a human confirms 2+ distinct direct provider keys are needed; proxy path already covers it |

---

## 2. Subsystem reference (part 1): API, DB, scheduler, ledger, engine-v2 core

**Status labels** — short forms of the top STATUS LEGEND (`LIVE`=`BUILT-AND-LIVE`, `OFF(flag)`=`BUILT-BUT-OFF`, `DEAD`=`DEAD-CODE`) plus these §2-local refinements: `LIVE(compose)` = code default is off/other but `docker-compose.yml` flips it on so it IS what runs · `OPT-IN` = a backstop that engages only when an operator sets a positive value · `SALVAGE-ONLY` = runs only on the crash/close/GC path · `STALE-DOC` = the code's own docstring/comment contradicts the real default.

Ground-truth reminder: engine-v2 (`SCANNER_ENGINE_V2=true`, `config.py:258` default `True` + compose `true`) is the ONLY orchestrator that runs by default; `planner/*` and `entrypoint.run_scan()` are DEAD in a default deploy (see §Architecture). Everything in §2.5 is the live path.

---

### 2.1 API layer (`src/scanner/api/`, `main.py`)

FastAPI app + `ScanPoller` share one process (`scanner.main:app`, run by `docker/cp/Dockerfile`). Lifespan seeds built-in playbooks (no external model call — builtins verbatim, all other YAMLs raw-YAML passthrough, so **no API key needed**; `main.py:32-40`), seeds the blocklist, and starts `ScanPoller` iff `SCANNER_ENABLE_POLLER=true`.

| Concern | Where | Facts / gotchas |
|---|---|---|
| Submit | `api/routes/scans.py:create_scan` (`:133`), `build_queued_scan` (`:88`) | Same `build_queued_scan` helper is used by manual submit, `schedules.py` cron, and `poller.py` schedule tick → a manual scan and a scheduled one are byte-identical. Inserts `Scan` row `status='queued'`; API never touches Docker. |
| search_path re-issue | `scans.py:188` (`SET search_path TO {schema}, public`) | PgBouncer transaction-pooling **resets `search_path` on every commit** — routes that commit then re-query must re-issue the `SET`. Done in `scans.py`/`schedules.py`; trivially forgotten in a new route. |
| Time-cap default | `scans.py:74-79` | Time cap can be *actually* unlimited (`None`) for both Anthropic and non-Anthropic; `default_s <= 0` ⇒ truly unlimited. Poller enforces the non-Anthropic cap. |
| Auth | `api/deps.py:get_current_tenant`, `get_scoped_session` | Bearer = admin key (must also send `X-Tenant-ID`/`X-Tenant-Schema`) OR a tenant's hashed API key (dual-mode, also matches legacy plaintext rows). |
| Rate limit | `api/rate_limit.py` | In-process token bucket; `/auth/login` gets its own 5-req/60s-per-IP bucket checked **before** the Bearer check (brute-force can't be escaped with a rotating bogus token). `_client_ip()` trusts `X-Real-IP` unconditionally (assumes nginx sole ingress; nothing verifies it). |
| Route inventory | `scans.py` (~845 lines, 30+ endpoints), `findings.py`, `admin.py`, `playbooks.py`, `schedules.py`, `retest.py`, `approvals.py` | Only `findings.py:list_findings` + `admin.py:list_audit` paginate (`limit<=500`); `/tools`,`/phases`,`/ledger`,`/inventory`,`/evidence` return everything unbounded. `playbooks.py` create/update **block the HTTP request synchronously** on a 30-120s LLM enrichment (no `BackgroundTasks`). `auth.py:/auth/login` mints no session token — hands back the same static admin key (no logout/expiry/revocation). |
| Cred encryption | `config.py:encrypt_secret`/`decrypt_secret` (`:425`) | Home-grown HMAC-SHA256 encrypt-then-MAC (not AES-GCM/Fernet). **`MASTER_ENCRYPTION_KEY` empty (`config.py:43`) silently passes gray-box creds through as plaintext** — unlike `admin_api_key` it is never validated/warned, and `docker-compose.yml:109` declares it optional (`${VAR:-}`) not mandatory. |

**GOTCHAS**: admin endpoints `admin.py:list_audit` (`:99`) and `get_ops_health` (`:183`) wrap per-tenant queries in bare `except Exception: pass` with zero logging — a failing tenant silently drops from the cross-tenant view. Admin bearer key is logged in full plaintext on boot when unset (`config.py:371-378`).

### 2.2 DB layer (`src/scanner/db/`, `alembic/`)

Two schema tiers: `public` (tenants, blocklist, secrets, runtime_settings, playbooks) + one `tenant_<slug>` per tenant. Isolation is **`SET search_path` only** — no `tenant_id` filter anywhere in the ORM.

- **17 ORM tenant models** (`db/models/tenant.py`): `Scan`(`:12`), `ScanPhase`(`:52`), `ToolInvocation`(`:65`), `Finding`(`:85`), `ScanEvent`(`:127`), `WorkerRun`(`:145`), `AgentMessage`(`:164`), `Checkpoint`(`:181`), `AuditLog`(`:193`), `InventoryElement`(`:204`), `EvidenceObject`(`:221`), `LedgerCell`(`:247`), `ChainNode`(`:296`), `ChainEdge`(`:321`), `ScanApproval`(`:335`), `OobToken`(`:356`), `ScanSchedule`(`:389`).
- **2 hand-written raw-SQL tables have NO ORM model**: `coverage_ledger` + `recon_targets` (migration 0010; DDL duplicated in `provisioning.py:59-67` `_ENGINE_RAW_DDL`). `coverage_ledger` is the DEAD phantom table (see §2.5.5).
- **Two drift-prone sources of tenant schema shape**: new tenants clone `provisioning.py:_TENANT_TABLES` (`:33`) + `_ENGINE_RAW_DDL`; existing tenants only get a new column when a migration hand-loops `public.tenants` and ALTERs each schema. `provisioning.py:27-32` and `:52-58` document two real historical bugs from exactly this gap (WS2 tables never appended → new API-provisioned tenants missing inventory/ledger/OOB/chains; migration-0010 tables never getting models). Same failure recurs for any future manually-added table.
- `db/tenant.py:get_tenant_session` is the canonical helper but used almost nowhere outside `api/deps.py` — ~2 dozen modules re-implement `SET search_path` inline because one call can't cover the "re-issue after every commit" requirement.
- `db/sanitize.py:pg_text()` strips NUL bytes (asyncpg rejects them; raw tool output carries them) but is wired into only 3 modules — **`tools/findings.py:write_finding` (the primary Finding-insert path) does not call it.**
- **Migrations: 19 files** (`alembic/versions/`, newest `0019_add_scan_engine_models.py` = per-scan engine-roster override, `0018_add_scan_instructions.py` = operator context). `0016_ledger_cell_attempts.py` added the attempt-cap column; `0017_findings_unique_dedup.py` is destructive (deletes dup rows before `UNIQUE(scan_id, dedup_hash)`, carries a human-review warning). `make migrate` runs Alembic **inside the running scanner-cp container** — you cannot migrate a bare local DB without the compose stack up.

### 2.3 Scheduler (`src/scanner/scheduler/`)

**`poller.py`** (`ScanPoller`, ~1576 lines) runs 4 asyncio tasks from the FastAPI lifespan: poll (2s → `poll_once` `:317`), watch (5s → `watch_once` `:1182`), GC (300s → `_gc_loop` `:662`), heartbeat (30s → `_heartbeat_loop` `:686`).

Lifecycle funnel (§Request lifecycle):
1. `_reconcile_on_boot` (`:213`, called from `start()` `:188`) — restart-recovery for scans this node owned. **Zero test coverage** on its tenant iteration / node-ownership filter / two exception-swallow paths.
2. Claim: `_poll_tenant` (`:429`) two-phase — Phase 1 `SELECT ... FOR UPDATE SKIP LOCKED` on queued scans up to the concurrency cap, flip `running`; Phase 2 (outside the lock) license + egress retry, then `_spawn_for_claim` (`:506`) → `worker.spawn_scan_containers`.
3. Watch/exit: `watch_once` (`:1182`) → `_on_scan_exit` (`:1255`, saves container logs, reaps toolserver, reclaims per-tool concurrency slots on every exit path), `_watchdog_once` (`:1113`), `_oob_autolink_once` (`:1162`).
4. Stop paths: `_cancel_scan` (`:961`), `_close_scan` (`:1035`, graceful — widens post-SIGTERM grace `_finalize_grace` `:928` via the `/work/finalizing.json` marker for in-container finalize+verify).

**`_finalize` (`:1454`) is the single idempotent salvage funnel** called from every exit path (clean, crash-with-report, crash-with-checkpoint, crash-with-partial, cancel, close, GC dead-node). It rebuilds the SAME verifier context (`_resolve_verifier` `:77`) so a salvaged scan verifies too — but the poller process has **no toolserver/kali-exec token**, so `finalize._verify_findings` self-skips reproduction and only tool-less semantic dedup runs (a salvaged scan gets a *weaker* verification than a clean exit). Loads the real scope blocklist into the verifier guard (`:1498`) so a salvage reproduction can't reach a gov/mil/RFC1918 host.

- **GC dead-node recovery** (`_recover_dead_node_scans` `:718`): scans stuck in `killing`/`cancelling`/`closing` when their owning node died had no recovery path for 2+ days (cited scan IDs in the code). Now salvages `/work` into DB (`:762`, `:825`) + stamps `graceful_terminal_status` (`:840`).
- **Terminal status is stamped at TWO independent call sites** — `poller.py` (`graceful_terminal_status` at `:840/:1016/:1102/:1303/:1331`) and `agent_runtime/finalize.py`. They must stay in sync by convention, not shared code.
- `scheduler/resume.py`'s `should_resume`/`attempt_resume` are **DEAD** — poller reimplements the decision inline with its own `MAX_RESUME_ATTEMPTS=3` (`:107`); only `build_resume_prompt` is imported.
- `_mirror_oob_interactions` (`:1431`) bridges toolserver-local OOB interactions onto the shared volume for the poller-side `sync_oob`.

**`worker.py`** (`spawn_scan_containers` `:272`): isolated per-scan Docker network, per-scan volume subpath (`_per_scan_mount` `:137`), toolserver-first with readiness probe (`_probe_toolserver_ready` `:36` — raises if it crashed at boot), optional tor/browser/zap sidecars, then the agent with a ~70-flag forwarded env allowlist (pass-through-only-if-set — the recurring "new agent flag silently never reaches the container" class). `_provider_api_key` (`:248`) picks the per-provider `{PROVIDER}_API_KEY` (falls back to `OPENROUTER_API_KEY`) for a non-OpenRouter roster.

**GOTCHA (HIGH, live)**: `_container_mem_budget` (`:187`) / `_container_cpu_budget` (`:218`) size each scan's containers against the **whole host's** RAM/CPU with **no accounting for other running scans** — up to 7 scans (see below) each independently compute an un-shared "whole host" budget, jointly over-committing the host.

**`concurrency.py`** (`ConcurrencyManager`): per-process, in-memory `asyncio.Semaphore` — `MAX_THOROUGH=3` + `MAX_FAST=4` = `MAX_TOTAL=7` (`:10-12`), **not cluster-wide**. Cluster total = sum of each node's own cap. `available_slots` (`:77`) sizes the SKIP-LOCKED claim LIMIT. Caps are fixed (deliberately not auto-detected from host).

### 2.4 Ledger — coverage work-queue engine (`src/scanner/ledger/service.py`, `applicability.py`)

Turns "is this scan done?" into a DB predicate. One `LedgerCell` row per (surface element × applicable vuln-class). `applicability.py:is_applicable()` is a pure table lookup (needs-param / sink-gated / auth-surface / host-level).

**Cell state machine** (`tenant.py:261-262`; 7 states):

```
                          claim_cells (SKIP LOCKED, attempts+1)
   untested ─────────────────────────────────────────────► testing
      │                                                        │
      │ is_applicable=false                    resolve_cells:  │
      ▼                                    confirmed (finding)  │
      na (terminal, na_reason)             tested_clean (≥2 methods +1 evidence)
                                           blocked (reason)     │
                                                                │ release_cells / reclaim_expired_leases
                                                                ▼  when attempts ≥ cap
                                                            attempted (terminal)
```

- Open states = `("untested","testing")` (`_OPEN_STATES` `:49`). Done/resolved = `{tested_clean, confirmed, blocked}`. Terminal-not-resolved = `attempted`, `na`.
- **Materialize** (`materialize_cells` `:549`): cross-products elements × 56 `VulnClass` members (`taxonomy.py:17`) through `is_applicable` + a P6 cartesian trim (`_trim_cell` `:344`, host-level dedup for header/CORS/CSRF-family to one cell/host) + near-duplicate URL/param fold (`_element_signature` `:473`, `_collapsed_element_ids` `:491`, ULID/UUID/numeric-segment detection via `_is_id_segment` `:422`, capped `_MAX_URLS_PER_HOST`). Idempotent across every wave; folded siblings open ONLY the data-dependent access classes (`_ACCESS_SAMPLE_CLASSES`).
- **Claim/lease** (`claim_cells` `:1228`): one raw-SQL CTE `SELECT ... FOR UPDATE SKIP LOCKED` → `UPDATE ... RETURNING` — two callers can never get the same cell. Claim order is priority-weighted by `_CLASS_PRIORITY` (`:1162`, 56 entries, injection/authz/RCE front-loaded) then `updated_at, cell_id` (deterministic run-to-run — before this the tiebreak was the random cell_id UUID, so a different high-value subset tested each run). Stamps `state='testing'`, `claimed_by`, `lease_expires_at`, `attempts+=1`, `last_progress=now`. Returns `{endpoint, vuln_class, cell_id, prior_methods, attempt}` — prior effort carried forward (blackboard handoff). `vuln_classes=` filter powers the exploit-floor's per-family claim.
- **Lease** (`_DEFAULT_LEASE_S` `:1135`) = `SCANNER_LEDGER_LEASE_S` else `SCANNER_ENGINE_WORKER_WALL_S`(5400) + 600 = 6000s. Deliberately > the 90-min worker wall so a claim outlives its worker and only reclaims on genuine death. `reclaim_expired_leases` (`:1389`) clears ownership of past-lease open cells (and absorbs attempt-capped ones to `attempted`).
- **Attempt cap** (`_attempt_cap` `:1140`, `SCANNER_LEDGER_ATTEMPT_CAP` default **3**): a cell claimed 3× without closing retires to terminal `attempted` on `release_cells`/lease-reclaim. `0` = legacy unbounded re-claim. This is a real, default-on reachable state.
- **Work-stealing re-queue** (`release_cells` `:1322`): the instant a worker finishes (any status), its still-open claimed cells become claimable NOW (not after the lease); `methods_used`/`attempts` preserved; attempt-capped ones absorb to `attempted`. Owner-scoped so it can't yank a live worker's cell.
- **Resolve** (`resolve_cells` `:683`, driven by `sync_from_work` `:946` reading `findings.jsonl` + `ledger_updates.jsonl` + `exploit_floor_signals.jsonl`): multi-tier identity match — `by_key` (full normalized identity), `by_path` (path-only, for host-less finding endpoints), `base_fallback` (typed-input `<endpoint>#<param>` cell under its base endpoint). C1 fix (`:715`) groups colliding cells into a *list* so a shadowed loser no longer strands open forever. Confirmed needs a finding; `tested_clean` needs ≥2 distinct methods + ≥1 evidence (else `testing`); already-resolved cells never downgraded (idempotent). `reopen_cells_for_classes` (`:1004`) flips `tested_clean → untested` (fresh attempt budget) for the executed-chain re-loop.
- **Two OFF(flag) resolve gates**: evidence gate (`scanner_evidence_gate` `config.py:182` default `False`) — a finding with no proof artifact is counted `unproven` and its cell stays open. Machine-verified close (`scanner_ledger_machine_close` `config.py:190` default `False`) — a `tested_clean` claim also requires a real `tool_invocations` hit on the endpoint (`_probed_targets` `:983`, `_probe_ok` `:102`), else stays `testing`/`unverified`.
- **Completion** (`scan_is_complete` `:1087`): `count_open_cells==0` OR resolved-ratio ≥ `_COMPLETE_RATIO` (`SCANNER_LEDGER_COMPLETE_RATIO` default **0.98** — lets a scan finish with ≤2% stranded). `graceful_terminal_status` (`:1106`) = `"completed"` only if complete AND had applicable coverage (`count_applicable_cells>0`), else `"partial"`. `_stop_on_probe` (`:1032`, `SCANNER_LEDGER_STOP_ON_PROBE` default off) widens "open" so a probed `testing` cell doesn't hold the scan open.
- **Quiescence signal** (`count_claimable_cells` `:1354`): applicable + open + under-cap — the Father's quiescence stop (loop ends only when this hits 0 or a hard backstop, not on the first no-progress wave).
- **Index gap (HIGH)**: only `idx_ledger_scan_state` on `(scan_id, state)` exists (`tenant.py:251`); the actual claim predicate (`applicable`, `claimed_by`, `lease_expires_at`, `attempts`) has no covering index — real cost on 12k–14.7k-cell grids.

**GOTCHAS**: (1) `release_cells`(`:1322`) + `count_claimable_cells`(`:1354`), wired via Father's `_release_worker_cells`/`_has_claimable`, have **zero test coverage** (existing `test_father_batch_dispatch.py` fakes can't detect a regression — fake `on_done` never fires, fake surface lacks the methods). (2) Report coverage math (`reporting/service.py:_coverage`) excludes `attempted` from *both* resolved and open, while `_OPEN_STATES` treats `attempted` as effectively resolved → two code paths disagree on the same state (see CLAUDE.md MEDIUM).

### 2.5 Engine-v2 core (`src/scanner/agent_runtime/engine/`) — the live stack

#### 2.5.1 Wiring — `run.py:run_engine(scan_ctx)` (`:166`)

Order: `ModelRegistry.from_config` → `LevelResolver().resolve` (raises `EgressViolation` on a local-only policy + a remote model) → `Gateway` (**DEAD**, `# noqa: F841`, built never called) → `AttackSurface` → `WorkerRecorder` → component-health gate (model = essential: no admissible model ⇒ red + `RuntimeError`) → `_provision_oob` (`:81`, hard caps `SCANNER_ENGINE_OOB_START_TIMEOUT_S`=60 / `_SELFTEST_TIMEOUT_S`=30 so a slow oracle can't stall — a real live scan once burned ~7 min here) → `worker_factory` (`:208`, Anthropic→`ClaudeSDKRuntime`, else→`AgentsRuntime`) → two `asyncio.Event`s (`wrap_up` + `close_requested`) → `FleetManager` → `Governor` → `Father` → `father.run()`.

- **Finalize on EVERY exit path** — a mid-`father.run()` exception is swallowed + logged (`:266-273`) so finalize still runs (never re-runs the whole scan single-agent, never re-provisions a new OOB domain that can't correlate already-fired callbacks). `finally` stops the OOB mirror loop + one last sweep.
- SIGTERM = graceful close (`_install_close_handler` `:147`): sets `wrap_up` (Father breaks + guard drains new tools) AND `close_requested` (runs `run_close_sweep` before finalize). On Windows/non-unix falls back to `signal.signal`.
- **A1 verifier selection** (`_verifier_endpoint` `:36`): picks the first non-Anthropic roster model with an `api_base` (or the pre-scan "verifier" seat when `scanner_engine_seat_models` on). **An all-Anthropic roster resolves `(None, None)` ⇒ no A1 verifier, no close-sweep, no live-convergence** (Anthropic can't drive the OpenAI-compatible verifier SDK). `verify_on` gate at `:328`; when on, `scan_ctx.finalize(run_finalize_scan=False)` runs only crawl/instrument/zap and the verifier-bearing `finalize_scan` is the ONE finalize (W6: avoids pre-demoting provisional rows before the verifier sees them).

#### 2.5.2 Father wave loop — `father.py:run()` (`:1674`, file ~1859 lines, biggest in repo)

Father builds `WorkerSpec` prompt strings and hands them to `FleetManager`; it does NOT itself run an LLM turn loop. Shape:

```
recon (ScopeRecon.run) → _ensure_auth (I1, one authed session before wave 1)
while True:
  _materialize_surface  → _sync_work_to_db (also ticks the graceful-drain soft-cap watchdog)
  if ran_a_wave and wrap_up.is_set(): break        # graceful drain
  _sample_open → _write_recon_json → write_scan_brief
  measure progress (new surface inserted / unresolved fell / distinct confirmed rose)  → plateau?
  if ran_a_wave and saw_open and _is_complete(): break            # coverage-complete
  Governor.decide → if "partial" AND not _has_claimable(): break  # QUIESCENCE, not plateau
  pick wave_targets (new discovered surface → fresh pass; else deepen `seen` up to _max_waves)
  _claim_worklist (reclaim leases → claim_cells SKIP LOCKED → board) → _worklist_by_group → build_specs
  dispatch: scanner_engine_batch_dispatch ? _run_batch_pool : _run_floor_and_fleet
  if wrap_up.is_set(): break
  _run_chain_floor (deterministic next-hop) → _run_escalation (executed-chain re-loop)
smoke workers (skipped if completed_via_coverage or wrap_up)
```

- **Two dispatch paths**: `_run_floor_and_fleet` (`:1201`, legacy — floor `create_task`'d concurrently, `run_all` fleet + background `_periodic_sync`) vs `_run_batch_pool` (`:1335`, `scanner_engine_batch_dispatch` `config.py:308` default `False` but **`docker-compose.yml` sets `true` → LIVE(compose)**). Batch path composes endpoint-scoped batches (`batch.py:compose_batches`, `max_cells=_batch_max_cells()` default 2 — small units so a weak model can close & register progress before the watchdog looks) and drives `fleet.run_pool` with the Manager watchdog `_batch_done` (`:1270`) as `preempt` and `_release_worker_cells` (`:1321`) as `on_done` (immediate work-stealing re-queue).
- **`_batch_done` watchdog** (`:1270`) is progress-driven: preempt only when the batch is all-terminal (`batch_satisfied`) OR stuck (no new terminal cell AND no `last_progress` advance AND no new tool_calls for `_stuck_window_s`). `budget_s` flat cap default 0 = off.
- **Both no-progress backstops OFF by default**: `_batch_budget_s` (`:554`) = 0, `_stuck_window_s` (`:571`) = 0 (disabled in commit `36fece4`, "mid-long-tool false cut"). The only remaining hang-guard is `fleet.py`'s flat 5400s (90 min) per-worker wall. The scan stops on **progress** (coverage-complete / plateau-and-drained), not a clock.
- **`_render_board_totals`** (`:424`, `_DONE_STATES` `:420` = `{tested_clean,confirmed,blocked}`) is prepended to every worker turn as the compact live coverage board — **GOTCHA (MEDIUM)**: it drops any cell in the terminal `attempted` state (bucket = -1) from the totals; the code comment blames `na` but `na` is already excluded upstream by `applicable=true`.
- **`_has_claimable`** (`:1396`) — **GOTCHA (CRITICAL)**: swallows every exception and returns `False` with **zero logging** (its sibling `_is_complete` at `:1386` logs on the same failure class). A transient DB/Redis hiccup during the quiescence check is indistinguishable from "queue drained" → silently stops the wave loop early. Mirror in `attack_surface.py:count_claimable` (`:157`).
- Chain floor (`_run_chain_floor` `:1578`) + escalation (`_run_escalation` `:1605`) run BEFORE the next wave so chained findings are on disk; escalation is **auto-allow within scope** (no human gate). Live-convergence tick (`_live_convergence` `:995`, `scanner_engine_live_convergence` `config.py:290` default `True` but no-ops without a non-Anthropic verifier endpoint) can verify/enrich/report mid-run.

#### 2.5.3 Fleet / Governor / Resolver / batch

| Module | Responsibility | Key facts (file:line) |
|---|---|---|
| `fleet.py` | Ephemeral per-spec worker pool, backend-agnostic | `_worker_wall_s` (`:12`) = `SCANNER_ENGINE_WORKER_WALL_S` default **5400s (90 min)** = the only hard hang-guard. `run_all` (`:121`, gather barrier) vs `run_pool` (`:124`, rolling pool, effective cap `max(1, hard_cap*health())`, `on_done` fires per-worker completion). `total_invocations` (`:43`) feeds the Governor (was hardcoded 0). Timeout→`partial`, exception→`error`; a dead worker never kills the fleet. |
| `governor.py` | Progress-based stop decision | `decide` (`:32`): `unresolved==0`→`stop`; `plateau`→`partial`; runaway cap→`partial`; else `continue`. `_runaway` (`:41`) hard caps (`max_workers`/`max_invocations`/`max_wall_s`) engage **only when >0 = OPT-IN**; wall defaulted ON at 6h ceiling (`context._runaway_limits` `:101`, root-cause fix for the 12h runaway), invocations off. |
| `resolver.py` | Level + max-workers + seat binding | `LevelResolver.resolve` (`:62`): level 1/2/3 by admissible model count (1 / ≤3 / >3) → `max_workers` 4/12/32 **clamped by `_max_workers_cap()`** (`:9`, `SCANNER_ENGINE_MAX_WORKERS_CAP` default **4** — the 2026-09-03 runaway fix: workers used to scale with model count unbounded). `resolve_seats` (`:41`) binds each of 11 seats to a model by capability keyword overlap (`SEAT_HINTS` `:26`); consumed only when `scanner_engine_seat_models` on (default `False`, OFF(flag)). |
| `batch.py` | Endpoint-grouped batch primitives | `compose_batches` (`:30`) groups by `_norm`'d endpoint, chunks ≤`max_cells` (chain-aware — SQLi→IDOR on the same `/api/orders/1` ride one batch). `batch_satisfied` (`:64`): all states in `_TERMINAL` (`:18`, = confirmed/tested_clean/blocked/na/attempted); empty = trivially done. |

#### 2.5.4 Exploit floor — `exploit_floor.py:run_exploit_floor()` (`:3212`, ~3522 lines, largest file)

Deterministic non-LLM weapon sweep running **concurrently** with every LLM wave (`father._run_exploit_floor` `:1181`). `scanner_exploit_floor_enabled` `config.py:197` default **`True` = LIVE** — **STALE-DOC gotcha**: the `_run_exploit_floor` docstring at `father.py:1183` still says "default off → legacy byte-for-byte", contradicting the real config default. `surface=None` self-disables (unit tests / flag-off byte-for-byte no-op).

- Claims a **disjoint** cell batch per family via `surface.claim_family_cells` (`attack_surface.py:118`, same SKIP-LOCKED, `vuln_classes`-filtered) so the floor and LLM fleet never double-fire a cell.
- **8 disjoint families** (`_Family` `:119`; class sets disjoint by construction): `_INJECTION`(sqlmap: sqli/nosqli), `_CONFIG`(nuclei: cors/creds/dir/backup/vcs/sourcemap/secrets/debug/host-header/cache/open-service/takeover/cloud-bucket), `_HYGIENE`(curl: security_headers/weak_session/protocol/weak_cipher/cert), `_CLIENTSIDE`(dalfox: xss ×3), `_SSRF`→renamed `"blind"`(oob: ssrf/ssti/cmdi/xxe/lfi/rfi/open_redirect/deser), `_ACCESS`(curl differential replay anon/authed/user-B: idor/bfla/priv_esc/auth_bypass/forced_browse), `_LOGIC`(curl scripted: price_tamper/mass_assign/race/quota/workflow — signal-only, never self-proving), `_RATELIMIT`(curl burst). Plus `_NOFAMILY` (`:209`, `SCANNER_NOFAMILY_SWEEP` default-on, drains FIRST, class set **intentionally overlaps** config/hygiene for a precise active probe — the one exception to the disjoint rule).
- **Drain** (`SCANNER_FLOOR_DRAIN` default on): re-claim each family's next disjoint batch until empty or budget. `_DRAIN_ORDER` (`:229`) = cheap curl families first (breadth), slow sqlmap injection LAST against a reserved sub-budget (`SCANNER_FLOOR_INJECTION_BUDGET_S` ≤ `SCANNER_FLOOR_BUDGET_S`/3) — pass-0 is budget-gated too (`:3308`, the old `pass_num>0` guard let pass-0 sweep the whole surface unbounded and SIGKILL the scan before the fleet spawned). `SCANNER_FLOOR_DRAIN=0` collapses to one legacy pass over `_FAMILIES`.
- **Oracles are honesty-gated**: only unambiguous deterministic hits mint `verified=True` directly (e.g. `_two_request_oracle` `:1849`, `_sqli_oracle` `:1905` boolean/time-blind diff, `parse_hygiene_headers` `:1095` literal-absence, anon-200 on a protected endpoint in `_sweep_access` `:2830`). Ambiguous hits go to `exploit_floor_signals.jsonl` for LLM triage. Blind classes mint an OOB token (`_mint_oob` `:1796`) and fire (`_fire` `:1823`). Spec-diff authz (`_sweep_spec_diff` `:3129`) is OpenAPI-driven so it fires even for ops no cell claimed. Every fire persists a `tool_invocations` row via `surface.persist_invocation` (`attack_surface.py:126`) + a `_floor_beat` heartbeat (`:3333`) so the console isn't blind mid-sweep.
- **GOTCHA**: `_HYGIENE` claims `WEAK_CIPHER`/`CERT` (`:155-156`) but **no TLS/cipher/cert-validity check exists** in the file — those cells get marked "tested" by an unrelated header probe, silently misleading the coverage board.

#### 2.5.5 recon_floor / context / attack_surface / auth_bootstrap

- **`recon_floor.py:run_recon_floor()`** (`:285`) — deterministic recon backstop (subfinder `:106` → httpx-probe+arjun `:125`/`:199` → katana), plus **5 gated depth stages** (`SCANNER_RECON_DEPTH` default on, `_depth_enabled` `:87`): `_stage_js_harvest`(`:410`), `_stage_historical`(`:445`), `_stage_content_brute`(`:464`), `_stage_graphql`(`:486`), `_stage_favicon_vhost`(`:507`). Writes `# tool:` inv logs the next `AttackSurface.materialize` ingests. Scope-threaded so out-of-scope discovered hosts are never actively probed. `_write_secret_finding` (`:539`) mints JS-leaked-secret findings.
- **`context.py`** — `build_engine_context` (`:395`) assembles the production `EngineScanContext` (`:260`) from the agent-container env; `SchemaSessionFactory` (`:135`, validates schema name, pins `search_path` on enter) is the engine's tenant-scoped session source. `ScopeRecon.run` (`:171`) seeds `recon_targets`, runs the recon floor, best-effort authed login (`login_with_credentials`, 60s cap), writes the scan brief, flag-gated browser crawl+instrument during recon (so it crawls the *authed* session), background ZAP baseline. `EngineScanContext.finalize` (`:274`) is the shared ingest (crawl/instrument/zap/`finalize_scan`); `run_finalize_scan=False` (W6) skips the verifier-less pass. **`_runaway_limits`** (`:101`): invocations off, wall 6h default. **`GuardContext.budget_remaining`** (`:413`) is set once and **never decremented** — gates "any positive cap ⇒ allow", not real USD spend (the H-13(b) per-tool decrement is still a TODO).
- **`attack_surface.py`** — thin async facade over `ledger.service` (`claim_cells`/`claim_family_cells`/`materialize`/`sample_open_cells`/`scan_is_complete`/`release_cells`/`count_claimable`/`reclaim_expired_leases`/`coverage_counts`/`cell_states`/`target_health`). `materialize` (`:68`) forces `enable_v2=True` (B0 — engine surface ingest never depends on the env toggle). **DEAD phantom API**: `claim_cell`/`resolve_cell`/`register_target` (`:35`/`:48`/`:56`) write the legacy `coverage_ledger` table nothing reads — a dev could wire new code to this dead table by mistake. **GOTCHAS** (all best-effort swallow-to-safe-default, no logger imported in the file): `count_claimable` (`:157`) → 0 on error (silently ends the loop, mirrors CRITICAL `_has_claimable`); `target_health` (`:188`) → **1.0 (fully healthy)** on any error → `fleet.py:145`'s adaptive cap treats a persistent DB/telemetry outage as a perfectly healthy target, defeating concurrency-shedding.
- **`auth_bootstrap.py`** — I1 authenticated-first. `login_with_credentials` (`:232`) deterministic httpx login (password `_login_with_password` `:177`, direct-session cookie/bearer `_direct_session` `:162`, 2FA-pending detection `_detect_2fa_pending` `:57`); on failure `build_auth_worker_task` (`:356`) hands an LLM worker the self-register task. `read_auth`/`write_auth` (`:84`/`:105`) manage `/work/auth.json`; `refresh_auth` (`:333`) re-logs a dead session; `is_session_expired` (`:289`) detects it. Two accounts (user_a/user_b) enable cross-user IDOR/BOLA proof.

#### 2.5.6 guardrails / methodology / scan_brief / telemetry

- **`guardrails.py:guard_tool_call()`** (`:69`) — the INVARIANT wrapping every tool call on **both** runtime backends (byte-identical scope/safety). Order: graceful-drain check first (`:99`, once `wrap_up` set, denies any NEW shell/web/browse but lets local emit/flush tools through) → budget (`:105`) → for `run_shell`: sleep-cap (`_total_sleep_seconds` `:51`, `SCANNER_ENGINE_SLEEP_CAP_S`=10, strips quoted remote-sleep payloads first) → non-overridable platform/metadata block (`_PLATFORM_INFRA_RX` `:126`, catches `-h redis`/`//postgres`/`@pgbouncer`/RFC1918) → fail-closed scope (`:135`, confident out-of-scope hard-blocked, EXCEPT research/OOB domains `_is_research_domain`) → safety crime-line (`hook_safety` `:140`; a GATED value-read is opt-in via `SCANNER_ENGINE_ALLOW_VALUE_READ` default off, a FORBIDDEN verdict stays denied regardless). `web_fetch` held to `WEBFETCH_ALLOWLIST_RX`; `browse` scoped. Optional append-only audit log (`SCANNER_ENGINE_GUARD_LOG`).
- **`methodology.py`** — `DEEP_OFFENSIVE_VAPT` (`:13`) is the ~single system prompt injected into every fleet worker on both backends. **ADAPTER NOTE** (`:70`) papers over the two incompatible tool conventions (`kali-exec '<cmd>'`/`$OOB_DOMAIN` pre-pivot vs `run_shell('<cmd>')`/`oob()` engine-v2) by instructing the LLM to translate — a weak/unmigrated model can literally invoke a nonexistent `kali-exec` binary under engine-v2.
- **`scan_brief.py:write_scan_brief()`** (`:228`) — builds the compact per-wave "common knowledge" `/work/scan_brief.md` (`build_scan_brief` `:97`, pure): target/scope/RoE, operator context (`SCAN_INSTRUCTION`, framed as non-authoritative facts, `:39`), tech, auth session + ready-to-paste curl snippet (`_auth_section` `:77`), discovered surface, coverage (`_coverage_from_ledger` `:197`), confirmed findings, OOB domain, "do NOT repeat proven ground", + optional P4a knowledge digest (`SCANNER_ENGINE_DIGEST`, `_digest_from_work` `:202`). Caps everything (30 endpoints / 12 open cells / 20 findings / 1500-char operator context) so it never balloons the worker prompt. **`read_scan_brief`** (`:267`) is **DEAD in prod** — every real caller uses `write_scan_brief`'s return value; only the test calls it.
- **`telemetry.py:WorkerRecorder`** (`:66`) — the SOLE writer of `scan_phases`/`worker_runs`/`agent_messages`/`scan_events` and sole publisher to the live WS feed (Redis pubsub). `phase_started`/`phase_finished` (`:98`/`:121`) are the only writer of `scan_phases` in either engine (elsewhere scaffolded-never-wired). `emit_component_health` (`:41`, `ESSENTIAL_COMPONENTS`={toolserver,model} `:38`) drives the per-scan health strip. `rollup_findings_count` (`:249`) reconciles the per-worker sum against the findings table, attributing the unattributed remainder (exploit-floor/ZAP/OOB rows) to a synthetic `exploit-floor` worker_run. **GOTCHA**: `record_agent_message` (`:204`, the only source of the cost API's numbers) is called **exclusively from `agents_runtime.py`** — `claude_sdk.py` never calls it, so Anthropic-provider fleet workers contribute **zero cost/token telemetry** (cost tab shows $0 for an all-Anthropic run).

#### 2.5.7 escalation / verify / close_sweep / coverage_qa

| Module | Status | What it does (file:line) |
|---|---|---|
| `escalation.py` | LIVE (engine-v2, auto-allow) | `detect_escalations` (`:31`): clears + rebuilds the scan's chain graph (`build_graph`), returns new HIGH-impact caps + the vuln-classes they unlock (`cells_unlocked_by`). **Auto-allow ≠ no scope** — the Father's scope hook + RoE still bound every spawned worker. No human gate (unlike the DEAD `planner/escalation`). Best-effort, logs on failure (`:55`), never raises. |
| `verify.py` | LIVE for non-Anthropic rosters | `build_engine_execute_fn` (`:41`) builds the A1 independent-validator `execute_fn` on the SAME model+client the workers use, restricted to run_shell/read_file/write_file/**browse** (NO write_finding → can't self-confirm), routed through the SHARED `AgentsRuntime._build_guarded_tools` (byte-identical guard). `require_tools=True` = live reproduction (needs a live toolserver, `tool_choice=required`); `require_tools=False` = tool-less semantic dedup (safe on the dead-toolserver salvage path). Wall `SCANNER_ENGINE_VERIFY_WALL_S`=180. Returns `None` if the SDK/`OPENROUTER_API_KEY` is absent → finalize skips verification. |
| `close_sweep.py` | LIVE, operator-close path only | `run_close_sweep` (`:50`): on graceful close (toolserver still alive), one worker mines `tool_outputs/*` for real vulns not in `findings.jsonl`, **reproduces each against the live target** (`require_tools=True`), appends confirmed ones. Bounded `SCANNER_CLOSE_SWEEP_WALL_S`=300. Fail-open (returns 0) without a model/guard/SDK. Skipped on a plain soft-cap drain. |
| `coverage_qa.py` | LIVE, observability-only (finalize) | `coverage_quality_summary` (`:122`) → `/work/coverage_quality.json`: applicable-vs-exercised-vs-resolved per vuln-class family (reuses Father's `_GROUP_FOR_CLASS`/`PHASE_EXPLOIT_TOOL`) + a dedicated OOB mint/fire tally (oob() calls land in `oob_token`, not `tool_invocations`). Read-only — never re-tasks workers, never raises, must never sink finalize. |

**Escalation glossary tie-in**: engine-v2 escalation is auto-allow; the human-approval-gated `planner/escalation` + `approval/service.py` channel is DEAD by default (see §Architecture) — the `ScanApproval` rows / `approvals.py` UI are near-unreachable in production.

---

## 3. Subsystem reference (part 2)

Status labels — short forms of the top STATUS LEGEND: **LIVE** = `BUILT-AND-LIVE` (here, on the default `SCANNER_ENGINE_V2=true` deploy path) · **OFF(flag)** = `BUILT-BUT-OFF` · **DEAD** = `DEAD-CODE` (zero production callers — test-only or `# noqa: F841`) · **PARKED** · **IN-FLIGHT** — all as defined at the top.

> Ground-truth note: several §6.6–6.15 claims in `docs/APPLICATION_CONTEXT.md` were re-verified against code for this doc. **Corrections flagged inline with ⚠️** — chiefly the playbook seeder no longer LLM-compiles, and the `settings_store.MANAGED` count.

---

### 3.1 Guardrail hooks (`agent_runtime/hooks/`)

**Two independent guardrail stacks, one per runtime path.** A fix to one does *not* reach the other — always patch both call sites.

| Path | Entry | Reuses | Does NOT use |
|---|---|---|---|
| **legacy reprompt/planner** (DEAD by default) | `hooks/bash.py::make_pre_tool_hook` → `hook` (`bash.py:123`) | budget, safety, scope, gated, semaphore | — |
| **engine-v2** (LIVE) | `engine/guardrails.py::guard_tool_call` (`guardrails.py:69`) | `hooks/safety.py` + `hooks/scope.py` internals (`guardrails.py:28-29`) | `hooks/budget.py`, `hooks/gated.py` human-approval flow |

`hooks/__init__.py::run_pre_tool_hooks` (`__init__.py`) is **DEAD** (test-only).

| File | Lines | Responsibility | Status / gotcha |
|---|---|---|---|
| `bash.py` | 240 | Legacy PreToolUse: budget→safety→GATED-approval→scope→per-tool semaphore, for Bash/WebFetch/WebSearch (`bash.py:144-237`); non-scope native tools (Read/Write/Edit/Glob/Grep/TodoWrite) auto-allow (`bash.py:140-142`) | DEAD path. WebFetch allowlist `WEBFETCH_ALLOWLIST_RX` (`bash.py:50`) = NVD/MITRE/CVE/GitHub/exploit-db/rapid7/snyk/OWASP/portswigger/HackerOne/Bugcrowd/intigriti |
| `scope.py` | 457 (largest hook) | Two-tier minimal-friction scope + **non-overridable platform blocklist** | **LIVE** (reused by engine-v2). See detail below |
| `safety.py` | ~90 | Destructive-command block + delegates to `exploitation/contract.classify` for forbidden/gated | **LIVE** (reused by engine-v2) |
| `budget.py` | ~40 | Cost-cap gate, wind-down inject at 85% | Legacy-only; engine-v2 uses its own `Governor` |
| `gated.py` | ~55 | `resolve_gated_action` → human-approval for GATED value-reads | Legacy-only; engine-v2 escalation is auto-allow |
| `verification.py` | 12211 B | `redact()` (`verification.py:25`) masks `Authorization/Cookie/Set-Cookie/X-Api-Key/X-Auth-Token/Proxy-Authorization` header values + `Bearer/Basic` tokens (`verification.py:17-19`) — called by `findings.write_finding` before PoC persists | **LIVE** (shared) |
| `posttool.py` | 11392 B | PostToolUse: frees semaphore slots, output persistence | Legacy path |
| `goal.py`, `stop_gate.py`, `summarize.py` | — | goal-drift nudge, stop-gate, `summarize.py` is a 59-byte re-export stub | Legacy path |

**`scope.py` two-tier design (LIVE, load-bearing):**
- **Non-overridable platform blocklist** runs *first*, before any tenant scope, ungated by `scope.enforce` (`_is_platform_blocked`, `scope.py:269`): infra hostnames `localhost/postgres/redis/pgbouncer` (`scope.py:262`), loopback/link-local/RFC1918/CGNAT/ULA via `ipaddress` (`scope.py:292-306`), explicit metadata IPs `169.254.169.254 / 100.100.100.200 / fd00:ec2::254` (`scope.py:266`). `SCANNER_ALLOW_PRIVATE_TARGETS=true` opts RFC1918 back in for on-prem engagements (`scope.py:306`). A second regex `_PLATFORM_INFRA_RX` (`scope.py:69`) catches scheme-less DB-pivots (`//redis`, `-h postgres`, `host='redis'`) the dotted-hostname extractor would miss.
- **Confident out-of-scope** (full `http(s)://` URL host, MCP structured `target/host/url` arg, or a bareword target of an egress tool `_EGRESS_TOOL_RX` = nc/ncat/socat/wget/dnsx/dig/…, `scope.py:56`) → **hard-blocked** when `scope.enforce`, unless it's a research/OOB domain `RESEARCH_DOMAINS_RX` (`scope.py:37`, includes `oast.fun/oast.live/interact.sh/oast.abhedi.co.in`).
- **Bareword hostnames** → **advisory only** (logged `scope.out_of_scope`, never blocked) so a false positive can't stall the agent (`scope.py:454`).
- `resolve_scope_ips` (`scope.py:333`) pins A/AAAA of hostname targets at scan start so an IP is in-scope only via exact/CIDR match, not blanket-allowed.

---

### 3.2 Tools (`agent_runtime/tools/`)

**`tools/findings.py::write_finding` (`findings.py:356`) — the single landing point for EVERY agent-written finding, all runtime paths.** **LIVE.**

- **Returns sentinel `uuid.UUID(int=0)` — not `None` — for every non-persisted case** (junk-drop `findings.py:389`, config-FP downgrade `:395`, duplicate `:410`, race-duplicate `:461`). Any caller checking truthiness alone mistreats the zero-UUID as a real finding.
- Defensive filter layers, each documented against a real past scan ID:
  - **Junk/meta drop** (`_is_junk_finding`, `findings.py:165`): `_JUNK_CATEGORIES` (setup/meta/debug/test/placeholder…, `:81`); self-disclaimed text ("do not count", "must not fabricate", `_SELF_DISCLAIMED_RX` `:111`); snake_case directive titles with no substance (`:103`).
  - **Config-hardening FP backstop** (`_is_config_hardening_class`, `findings.py:156`): HSTS/CSP/TLS/CORS/cookie/headers/version-disclosure/"exposed panel" (`_CONFIG_FP_TOKENS`, `:121`) downgraded unless `verified` OR proof present (`:393`).
  - **Semantic dedup** (`_compute_dedup_hash`, `findings.py:305`): key = (normalized target, normalized endpoint, canonical vuln-class). Endpoint normalization (`_norm_endpoint`, `:274`) strips METHOD prefix, chained `-> next hop`, trailing `(param)`, templatizes object ids (`/api/account/800011` → `/api/account/{id}`). Port-family findings key on the port not the path (`:338`). Category → canonical `VulnClass` via n-gram taxonomy (`_canonical_vuln_class`, `:256`).
  - **Merge families** (`_MERGE_FAMILIES`, `findings.py:219`, `merge=True` only at finalize): collapses IDOR/BOLA/PRIV_ESC/FORCED_BROWSE→`access_control`, SECRETS/EXCESSIVE_DATA→`sensitive_disclosure`. W2 dual-key match (`:403`) stops a re-ingest resurrecting a merged-away row.
  - **C4 savepoint insert** (`findings.py:451-461`): real `AsyncSession` wraps add+flush in `begin_nested()` so the DB `UNIQUE(scan_id, dedup_hash)` backstop rolls back only the conflicting row; unit fakes flush plainly.
  - PoC secrets redacted via `hooks.verification.redact` (`findings.py:431`).
- `update_finding` (`findings.py:466`) patches verified/method/notes/severity/cvss.

`tools/bash.py`: `detect_real_tool` (`bash.py:112`) / `detect_tool` / `_split_unquoted` — parse the real Kali binary out of a `kali-exec '…'` / `run_shell('…')` wrapper so the semaphore keys on the tool, not the wrapper. **LIVE** (semaphore gating).

---

### 3.3 Pipeline (`agent_runtime/pipeline/`) — **DEAD**

Verified: **zero importers** of `pipeline.summarizer` / `pipeline.parsers` anywhere in `src/` outside the package. A second, unwired tool-output persistence implementation exercised only by one test file. `summarize_with_haiku` (`pipeline/summarizer.py:72`) is a literal `TODO(phase-3)` stub that returns `_catchall_summary(output)` and **never calls any model** (`:74-75`).

---

### 3.4 Planner / roster / specialist / coordinator (`agent_runtime/planner/`) — **DEAD by default**

The "Alpha Team" multi-agent design. **Only caller of `coordinator.run` is `entrypoint.py:905`** — the legacy path, dead under `SCANNER_ENGINE_V2=true`. `planner/roster.py::SpecialistRole` is the one live export (imported by `model_tier.py:26` for the enum).

| File | Responsibility | Status |
|---|---|---|
| `coordinator.py` | Dispatches role-scoped specialists; gates high-impact unlocks behind `approval/service` (`coordinator.py:182,212-213`) | DEAD (entrypoint-only) |
| `roster.py` | 7 `SpecialistRole`s + per-role skill subsets | Enum LIVE, subsets DEAD |
| `specialist.py`, `escalation.py`, `contract.py` | Per-role runner, escalation gate, planner contract | DEAD |

---

### 3.5 Chain (`agent_runtime/chain/`) — the one genuinely shared LIVE part of the exploitation stack

| File | Responsibility | Status | Key file:line |
|---|---|---|---|
| `capabilities.py` | Pure GRANTS/ENABLES/HIGH_IMPACT tables; `capabilities_for`, `reachable_from`, `is_public_read_bypass`, `edge_rationale` | **LIVE** (imported by both stacks + finalize + reporting) | — |
| `service.py` | `build_graph` (nodes from verified+evidenced findings only, `service.py:142`), `synthesize_chains`, `enumerate_ranked_chains` (shared pure walk, ranked by `len*(#high-impact+1)`, bounded `max_chains=200/max_steps=12`, `service.py:264`) | **LIVE** | `build_graph` `service.py:123` |
| `floor.py` | `run_chain_floor` (`floor.py:315`): deterministic single-hop next-step prober from a confirmed primitive | **LIVE, engine-v2-ONLY** — sole caller `father.py:1588` (`_run_chain_floor` `:1578`, dispatched `:1846`); planner path never calls it | — |

`chain/floor.py` detail (LIVE): 5 hop types keyed by `Capability` (`_HOPS`, `floor.py:306`): `METADATA_ACCESS`→IMDS cred-theft/reach (`_hop_metadata`, cred-vs-reach split via `_IMDS_CRED_RX`/`_IMDS_REACH_RX`), `FILE_READ`→`_hop_file_read` (8 secret files, `_SECRET_RX`), `REDIRECT`/`INTERNAL_HTTP`→OOB-inject SSRF, `CREDENTIAL`→reopen ENABLES classes. **Scope-bound**: only ever curls the in-scope finding URL and injects the internal/metadata URL as the *param value* — never a direct `169.254`/`127.0.0.1` connection (`floor.py:11-14`). Bounded by `seen_hops` (Father-owned, cross-wave) + `_MAX_HOPS=40` (`:91`). Has a runnable `_demo()` self-check (`floor.py:360`).

---

### 3.6 Approval (`agent_runtime/approval/`) — near-unreachable in production

`approval/service.py` (`request_approval`/`await_decision`/`decide`) is the DB-backed human-in-the-loop channel (`ScanApproval` rows, `approvals.py` route). Callers: `hooks/bash.py:172` (legacy GATED flow, DEAD), `planner/coordinator.py:182` (DEAD), `api/routes/approvals.py:45` (LIVE route but almost nothing creates rows). **Engine-v2's own escalation (`engine/escalation.py::detect_escalations`) is auto-allow, no human gate**; its GATED-command check routes through `SCANNER_ENGINE_ALLOW_VALUE_READ`, which never creates a `ScanApproval`. `await_decision` times out to `"denied"` so a headless scan never hangs (`service.py:63`).

---

### 3.7 Exploitation contract (`agent_runtime/exploitation/contract.py`) — **LIVE, shared**

`classify(cmd)` (`contract.py:51`): `forbidden > gated > allow`, defaults `allow` — shared by `hooks/safety.py` AND `engine/guardrails.py`.
- `FORBIDDEN_PATTERNS` (`contract.py:21`): the non-overridable crime-line — reverse shells (`nc -e`, `bash -i …/dev/tcp/`, mkfifo/python), `sqlmap --os-shell`, persistence (`>> authorized_keys/cron/passwd`), local-file exfil-out (`curl -d @/etc/…`). Deliberately does NOT match `file:///etc/passwd` as an XXE/LFI *proof-through-target* (`:32-37`).
- `GATED_PATTERNS` (`contract.py:41`): **only 3 sqlmap flag patterns** (`--dump`, `--sql-query`, `--passwords/--current-user/…`). Any other value-read (manual curl exfil, custom DB dump) classifies `allow` and bypasses approval entirely — self-documented as "defense-in-depth, not the real control."
- `EXPLOITATION_CONTRACT` prose (`contract.py:67`) is spliced into the agent prompt (FORBIDDEN / AUTONOMOUS benign-proof / GATED tiers).

---

### 3.8 OOB subsystem (`agent_runtime/oob/`) — **LIVE**; honest classification is the current anti-FP core

Deterministic, zero-LLM-trust correlation of self-hosted-oracle callbacks to the payload that caused them. `oob/registry.py` = pure join (`correlate`/`parse_*`, no I/O). `oob/service.py::sync_oob` (`service.py:188`) = the single DB writer, called from three sites (poller mid-scan tick, finalize, father continuous reconcile); **never raises** (control-plane best-effort).

**⚠️ Current honest-classification behavior — `classify_oob(reg_class, protocol)` (`oob/service.py:77`):**
- Class is **DERIVED FROM THE CALLBACK WIRE PROTOCOL**, never trusted from the agent's self-reported `vuln_class`.
- `ldap`/`ldaps`/`rmi` → **`jndi`** (Log4Shell-class), `_JNDI_PROTOCOLS` (`service.py:66`).
- Any other protocol (http/dns/smtp/…): tokens are split, qualifier noise-words stripped (`_QUALIFIERS`: blind/vuln/stored/reflected/…, `:68`), and the agent's label is **kept only if every remaining token maps to the same beacon-provable class** (`_DIRECT = {ssrf, xxe}`, `:74`). Otherwise — a combined/garbage label like `"blind_sqli_jndi"`, or any `cmdi/sqli/rce/xss/ssti` claim — it is **downgraded to `ssrf`** with a suspicion note `(agent suspected …)` (`:96-97`). This is the exact mechanism that killed the mass-false-positive "confirmed via OOB" bug (project history 2026-09-18).
- **Sink-clustering** (`service.py:215-281`): callbacks are grouped by sink `(target host × honest class)` so one URL-fetch sink hit from 45 endpoints collapses to **one** finding carrying all endpoints, not 45 rows. `_MINTED_SINKS` (`:135`) = one finding per `(scan, host, honest_class)`, capped by `_oob_finding_cap()` = `SCANNER_OOB_MAX_FINDINGS` default **12** (`:100`).
- Minted finding is `verified=True verification_method="oob_callback"` with full `evidence_paths` (`:373-383`), severity floored by class (`_OOB_SEVERITY`, `:36`; rce/cmdi/jndi→critical, ssrf/xxe/sqli→high). Also appended to `findings.jsonl` (`_append_finding_jsonl`, `:426`) because chain synthesis anchors on the JSONL, not the DB (`:404-406`).
- Ledger cells resolved under the **honest** class via `resolve_cells` (`:285`), with `oob_token` so `SCANNER_EVIDENCE_GATE` accepts the confirm.
- Durable dedup: `OobToken` table `UNIQUE(scan_id, token)` (`_persist_token`, `:437`, savepoint-guarded). In-process `_PROCESSED`/`_MINTED_SINKS` sets (`:128,135`) are **not durable across a process restart and are shared unlocked** across the three concurrent call sites. Stale-callback cutoff = `_registration_floor` from `oob_health.json checked_at` (`:151`); missing → identity-gate-only.

**⚠️ OOB server default:** `config.py:163` `scanner_oob_server = "https://oast.fun"` AND `docker-compose.yml:215 SCANNER_OOB_SERVER: ${SCANNER_OOB_SERVER:-https://oast.fun}` — **both default to public oast.fun**. The self-hosted `oast.abhedi.co.in` oracle (per memory) is reached only if the deployment's env sets `SCANNER_OOB_SERVER`/`SCANNER_OOB_TOKEN`. Verify the live env before trusting the code default.

---

### 3.9 Reporting (`agent_runtime/reporting/`) → `src/scanner/reporting/`

`build_report()` (`service.py:152`, **pure — no I/O**) is the single assembly point. **LIVE.**
- Recomputes CVSS live per finding (`_recompute_wins`, `service.py:185`) — a valid vector wins over stored severity; this policy is **hand-duplicated** in `api/schemas.py:_derive_framework_and_cvss` (`schemas.py:338`), kept in sync by comment only.
- Drops soft-dedup losers (`is_suppressed_duplicate`, `service.py:171`), stamps OWASP/ATT&CK/D3FEND (`refs_for_finding`), attaches deterministic `fix_snippet` for exactly 5 safe classes (headers/cors/open_redirect/rate_limit/csrf, `service.py:228`), joins OOB proofs (`_oob_proof_index`, `:133`), gates headline-vs-unconfirmed via `exploit_quality.is_unconfirmed` (`:199`).
- **`_coverage` (`service.py:110`) excludes `attempted` from BOTH `resolved` and `open`** (`:121-122`): `resolved = confirmed+tested_clean+blocked`, `open = untested+testing`. So a report's "X resolved / N open of Y" can have `X+N < Y` — disagrees with the ledger's `_OPEN_STATES` which treats `attempted` as effectively resolved (known MEDIUM issue).

| Renderer | Where | Richness | Status |
|---|---|---|---|
| `html_report.py` | finalize → written to disk | rich tiles/bars/SVG chain-flow | LIVE (disk only) |
| `service.render_html` (`service.py:662`) | `GET /report?format=html` (`scans.py:580`) | plainer, **no tiles/bars/effort** | LIVE (API) — a developer viewing via API sees a worse report than the disk one |

**⚠️ `report.effort` is always empty via the API** — `scans.py:576` calls `build_report(...)` **without `effort=`** (the param exists at `service.py:160` but only finalize passes it). `regression.py` (cross-scan diff, `GET /scans/{id}/diff`) is fully independent, stateless, no table/migration. Other files: `cvss.py`, `effort.py`, `exploit_quality.py`, `narrative.py`, `remediation_snippets.py`.

---

### 3.10 Playbooks (`src/scanner/playbooks/`) — mostly scaffolding; one live surface

Defines the per-scan "kill chain" spliced into the agent prompt as "Layer 2." **Three unconnected things call themselves "the playbook schema," only one is live:**
- `schema.py::UserPlaybook` — enforced on admin-submitted custom playbooks (`POST /api/v1/playbooks`). **LIVE.**
- `loader.py::Playbook/PhaseDef/TaskDef` + the entire `expanders/` (only `tech_stack_followup.py`) dynamic-dispatch — **DEAD**: no phase-runner loop reads `PhaseDef.expander`/`fan_out`; the runtime hands the agent one free-form prompt string.

**⚠️ Correction to base doc §6.10 — the seeder no longer LLM-compiles:** `seeder.py::seed_builtin_playbooks` (`seeder.py:30`) explicitly makes **no external model call** (`seeder.py:8-9,88-92`). Only the **2** hand-tuned builtins in `orchestrator.py:BUILTIN_PLAYBOOK_PROMPTS` (`orchestrator.py:732` = `deep_domain_subdomain_blackbox`, `full_coverage_vapt`) are used verbatim; **all other YAMLs are seeded as raw passthrough** (`seeder.py:107-110`), not enriched. `enrich_playbook` (`enrichment.py:99`) is now called **only** from the admin route `api/routes/playbooks.py:110,166`, never at boot. Editing `full_coverage_vapt.yaml` still has zero effect on the live agent — you must edit the Python constant in `orchestrator.py`.

7 YAMLs in `definitions/`: `aggressive_fullapp_vapt`, `deep_aggressive_single_agent_webapp`, `deep_domain_subdomain_blackbox`, `deep_pentest_max_surface`, `e2e_feature_validation`, `full_coverage_vapt`, `standard_external_blackbox`. Three mutually-incompatible informal dialects, zero validation at seed time. Repo-root `playbooks/` dir is orphaned (`seeder.py:27` hardcodes `src/scanner/playbooks/definitions/`).

---

### 3.11 WS relay + core config/ops

**`ws/gateway.py`** — the *only* WebSocket route, `/api/v1/scans/{scan_id}/stream` (`gateway.py:56`). **LIVE.** Dumb Redis-pubsub relay. `_authorize` (`:16`) supports Bearer token or `?token=` + admin-with-`tenant_id`; **auth and DB-replay are both wrapped in bare `contextlib.suppress(Exception)`** (`gateway.py:65,75`) with zero logging — a Postgres outage or bad `since=` presents identically to the client as silent close/empty replay. Small race between DB replay finishing (`_replay_from_db`, `:94`) and Redis subscribe (`:79`). `ws/events.py` = publish/subscribe helpers.

**`config.py`** — `Settings` = process-wide `@lru_cache` singleton, **67 fields** (verified count: 57 `scanner_*` + 10 core). An env change needs a process restart unless the field is in `settings_store.MANAGED`.

**⚠️ `settings_store.MANAGED` = 23 specs (verified), not 20** (base doc stale). Grouped (`settings_store.py:52-87`): Engine (3), Models (4), Detection (7), Safety (6), Caps&OOB (3). `applies="scan"` (default — env overlay on next spawned scan, no CP restart) vs `applies="restart"` (only `scanner_preflight_gate`; DB row updates but the long-running CP doesn't re-read until reboot, `:81`). Coercion/validation in `_coerce` (`:92`); unknown keys raise (`:133`). Most `scanner_*` flags remain env-only.

Other ops modules: `audit.py` (`write_audit_log` **only flushes, never commits** — durability depends on caller's txn), `blocklist.py`, `egress.py` (`check_egress` httpx→`api.ipify.org`, the real spawn-gating check — differs from `admin.py::_check_egress` raw TCP→`1.1.1.1:443`, dashboard-only; nothing reconciles them), `license.py`, `metrics.py`.

---

### 3.12 Docker infra (`docker/`)

Build targets in Makefile: `build-agent`/`build-toolserver`/`build-browser`/`build-zap` (`build-images` = all four, **NOT tor** — tor has no Makefile target, `docker build` it by hand).

| Image | Key files | Live behavior / gotcha |
|---|---|---|
| **agent** | `Dockerfile`, `entrypoint.sh`, `kali-exec.sh`, `browse.sh` | Non-root UID 1001. `entrypoint.sh:13` defaults `WORK_PATH=/var/lib/scanner/_default` **silently** if unset, then `ln -sfn $WORK_PATH /work` (`:21`) and symlinks `/skills` → `$WORK_PATH/.claude/skills` (`:27`) for SDK auto-discovery. `kali-exec.sh` = the ONLY path to Kali tools (no docker.sock). `browse.sh` **fails open (exit 0)** on unreachable browser sidecar (`browse.sh:25,71`); only a real non-200 is a hard failure (`:74`). |
| **toolserver** | `Dockerfile`, `exec_server.py`, `start.sh`, `synth_openapi.py` | `/exec` FastAPI with `X-Exec-Token` per-scan auth (`exec_server.py:7`). `DENY_PATTERNS`+`BLOCKED_HOSTS` (`:87,94`) are **defense-in-depth only**. **`_scope_recheck` (`:142`) is a documented no-op today** — `SCAN_SCOPE` env is never handed to the toolserver by `worker.py` (`:155`), so out-of-scope pivoting isn't enforced here; the agent's `guard_tool_call` scope hook is the real boundary. |
| **browser** | `Dockerfile`, `browser_server.py`, `start.sh` | Deterministic server-side BFS (no per-step LLM), `X-Browser-Token` auth, route interceptor aborts out-of-scope document navigations (redirect can't be followed off-scope), `record_har_content="omit"` to avoid V8 heap OOM on large SPA crawls. OFF by default per compose (`scanner_browser_enabled`). |
| **zap** | `Dockerfile`, `start.sh` | Reuses toolserver's `exec_server.py` verbatim; `/zap/wrk` must be a **real bind mount, not a symlink** (ZAP checks `/proc/mounts`). OFF in base compose, forced on by gitignored `override.yml`. |
| **tor** | `Dockerfile`, `torrc` | Client-only SOCKS proxy. No Makefile build target. `TOR_ROUTING_BLOCK` prompt (`orchestrator.py`) forces `nmap -sT` only. |
| **nginx / redis** | `nginx.conf`, `redis.conf` | Reverse proxy + Redis config. |

---

### 3.13 Frontend (`frontend/`)

Next.js 16 / React 18. **Not file-based routing in practice** — `app/[[...slug]]/page.tsx` is a stub; the real router is a hand-rolled `parseUrl()` (`components/shell/app-shell.tsx:46`) + `setRoute` (`:116,143`). **LIVE.**
- Dirs: `app/` (`[[...slug]]`, `login`), `components/` (`panels/`, `shell/`), `lib/`, `public/`.
- Data flow: polls REST every 4-10s **and** listens on one shared scan WebSocket, folding events into React state — no shared event bus.
- **No shared type generation FE↔BE**: `panels/scan-detail.tsx` WS event-folding hard-depends on exact event-type strings/payload keys from `engine/telemetry.py`; a backend rename silently breaks the Activity feed. `lib/ui-tokens.ts::isUnconfirmed` hand-duplicates `reporting.exploit_quality.is_unconfirmed`.
- **PDF export has no PDF engine** — `scan-detail.tsx:1990` opens a tab, `w.document.write(await res.text())`s the server-rendered HTML, relies on the browser's native print dialog.
- IN-FLIGHT (git status): `components/shell/new-scan-drawer.tsx`, `lib/types.ts`, `tsconfig.tsbuildinfo` modified.

---

### 3.14 Skills catalog (`skills/`) — **70 directories** (verified), three loading mechanisms

Each `skills/<name>/SKILL.md` = YAML frontmatter (name+description, always loaded) + Markdown body (on-demand). Which loader applies depends on the live orchestration path:
1. **Native SDK progressive disclosure** (legacy reprompt/planner, `setting_sources=["project"]`) — real on-demand via a native `Skill` tool. Reprompt discovers all 70; planner restricts per role (`planner/roster.py`) and **no role subset includes the cross-cutting protocol skills** (oob-callbacks, proof-carrying-findings, pentest-coverage, finding-writer, …). Moot — path is DEAD.
2. **Manual `read_file("/skills/…")`** (engine-v2, non-Claude models via `agents_runtime.py`) — no native Skill tool; the `DEEP_OFFENSIVE_VAPT` prompt tells the model to `read_file` the explicit path.
3. **Both, redundantly** (engine-v2, Claude-model workers via `claude_sdk.py`) — native Skill tool + `read_file` instructions. Belt-and-suspenders, not a bug.

**⚠️ Two incompatible tool-invocation conventions coexist with no code-level translation:** pre-pivot skills say `kali-exec '<cmd>'` / `$OOB_DOMAIN`; engine-v2 skills say `run_shell('<cmd>')` / `oob()`. `engine/methodology.py:70-73` papers over it with an "ADAPTER NOTE" telling the LLM to translate (`run_shell` not `kali-exec`, `oob()` not `$OOB_DOMAIN`) — a weak model can still invoke a nonexistent `kali-exec` binary under engine-v2.

Categories: ~13 methodology skills (`pentest-*`), ~38 imported Apache-2.0 offensive skills (`exploiting-*`, `performing-*`), protocol skills (`oob-callbacks`, `proof-carrying-findings`, `finalization-agent`, `deterministic-floor-coverage`, `worker-methodology`, …). `pentest-finding-writer/SKILL.md`'s documented JSON schema **does not match** the real `write_finding()` signature (extra `evidence_path`/`risk_impact`/`owasp` fields). IN-FLIGHT: `skills/oob-callbacks/SKILL.md`, `skills/pentest-finding-writer/SKILL.md` modified in working tree.

---

### 3.15 Tests & dev/ops tooling

**Tests: 238 `.py` files (verified), 4 in `tests/integration/`.** `make test` = `pytest tests/ -v`, **no marker filter** — the `integration` marker is decorative; integration tests self-skip via `RUN_ENGINE_INTEGRATION` env guard or a live-DB probe, so `make test` is always safe with zero infra (lots of `SKIPPED`). **Only 2 test files touch real Postgres** — `tests/integration/test_pipeline_replay.py`'s `replay_db` fixture, reused by `test_finalize_scan.py`; the other two integration files (`test_engine_fleet_scan.py`, `test_runtime_full_scan.py`) still gate on env. Everything else mocks the DB session → a semantically-wrong query can pass units but fail real Postgres. `pytest-postgresql` is a declared dep nothing imports.

**Makefile targets** (`Makefile`): `test`, `lint` (ruff check + format --check), `typecheck` (mypy --strict `src/scanner/`), `migrate` (alembic **inside the running scanner-cp container** — no bare-local migrate), `run`, `down`, `logs`, `build-agent`/`build-toolserver`/`build-browser`/`build-zap`/`build-images`, `clean`.

**`scripts/`** (verified listing): `healthcheck.sh` (`--smoke` submits a real tiny scan against scanme.nmap.org), `finalize_replay.py` / `moat_replay.py` (in-container standalone replays vs real Postgres — use instead of a paid scan for plumbing bugs), `deploy-alpha-team.sh`, `test_oob.py` (OOB oracle liveness + round-trip), `drill_scope.py`, `e2e_test.py`, `qa_cycle.py`/`.ps1`, `scan_watch.py`, `verify_nsdl_safe.py`, seed SQLs, PowerShell wrappers (`start.ps1`/`stop.ps1`/`logs.ps1`/`test_*.ps1`), `ui_test/` (Playwright Node smoke, **no Makefile target**). **⚠️ `scripts/dryrun_interactsh.sh` defaults to public `oast.fun`** — like the app's own code default, so a bare run may test a different oracle than a properly-env-configured live scan.

---

## 4. Current detection & proof capability inventory (what we can find AND prove TODAY)

This section is the honest, code-verified answer to "what classes can Abhedi Red *detect and machine-prove* right now, versus what is only guided by a skill and rides entirely on the LLM." Every claim is cited to a file:line and was re-read against the actual code. Status labels — short forms of the top STATUS LEGEND: **LIVE** = `BUILT-AND-LIVE` (on in `docker-compose.yml`); **OFF** and **GATED** = `BUILT-BUT-OFF` (OFF = a flag/env pins it off in every real deploy; GATED = a default-off env flag); **DEAD**/**PARKED** = `DEAD-CODE`/`PARKED` where noted.

### 4.0 How "proof" is defined in this codebase (the pipeline every class flows through)

A class is only "proved" if a machine artifact backs it. The trust chain, in order:

1. **A finding is written** to `/work/findings.jsonl` (agent via `write_finding`, or a deterministic floor via `exploit_floor._write_finding` at `src/scanner/agent_runtime/engine/exploit_floor.py:1730`, stamping `verification_method="exploit_floor:{tool}"` + `verified=true`).
2. **The ledger cell resolves** — `ledger/service.resolve_cells` (`src/scanner/ledger/service.py:683`) flips the matching `(endpoint, vuln_class)` cell to `confirmed`.
3. **Evidence gate** — when `scanner_evidence_gate` is on, a finding with **no** proof artifact does NOT confirm its cell; it is counted `unproven` and the cell stays open (`ledger/service.py:805`). Accepted artifacts (`_EVIDENCE_FIELDS`, `ledger/service.py:136`): `finding_id, evidence, evidence_ids, evidence_path, evidence_excerpt, proof_of_concept, oob_token`. **Status: OFF** — `scanner_evidence_gate=False` (`config.py:182`) and `docker-compose.yml:123` pins `false`. So in production a bare `{category, endpoint}` claim STILL confirms a cell; the gate that would demand proof is not running.
4. **Machine-verified close** (`scanner_ledger_machine_close`, `config.py:190`, default off, not in compose) — a `tested_clean` close additionally requires a real `tool_invocations` row hitting the endpoint (`_probe_ok`, `ledger/service.py:102`). **Status: OFF**. A deterministic-floor weapon that fired is auto-promoted to `tested_clean` regardless (`weapon_swept`, `ledger/service.py:893`).
5. **A1 independent verifier** (finalize) — re-reproduces H/C findings on a *separate* verifier agent with NO `write_finding` (cannot self-confirm), guarded run_shell/read/write + **browse** so XSS can be confirmed by real execution (`engine/verify.py:41`, browse tool at `:81`). Deterministic-oracle findings (`oob_callback`, non-timing `exploit_floor:*`) SKIP re-verification because they're machine truth (`reporting/exploit_quality.is_deterministic_oracle`, `:117`; used at `finalize.py:952`). **Timing-only** labels (`exploit_floor:sqli-time`, `:cmdi-time`) are EXCLUDED from that trust and get demoted. `finalize._reconcile_unconfirmed_verified` (`finalize.py:423`) flips any still-unconfirmed `verified=true` row back to `false` so the badge is honest. **Status: LIVE** when an SDK + `OPENROUTER_API_KEY`/`CAI_API_KEY` is present; fail-open (skips) otherwise (`verify.py:61-65`).
6. **Proof capsule (I2)** — `finalize._stamp_status` (`finalize.py:733`) records `evidence_paths.proof_capsule` from the verifier result for the report. **Status: LIVE** (part of the verify path).

Deployment reality of the surrounding flags: `scanner_engine_v2=true` (LIVE, the only orchestrator), `scanner_exploit_floor_enabled=true` (LIVE), `scanner_browser_enabled=true` (LIVE), `scanner_api_discovery_enabled` code-default true and **compose now defaults it ON** (`docker-compose.yml:145`, 2026-09-26 47a051e) → **LIVE in prod** (browser XHR/form → api_operation cells materialize; #23 surfaces shadow/zombie/debug ops as `exposure.shadow_api`), `scanner_finalize_leftover` code-default true but **compose pins `false`** (`:153`) → **OFF in prod**, `SCANNER_ENGINE_CHAIN_FLOOR` unset → deterministic chain floor **OFF** (`father.py:529`), `scanner_deser_rce_confirm_enabled=false` → **OFF/GATED**.

### 4.1 The proof engines (what produces machine evidence, and its status)

| Engine | File | What it proves | Status |
|---|---|---|---|
| **Exploit floor** (per-family deterministic weapon sweep, runs BESIDE the LLM each wave) | `exploit_floor.py:3212` (`run_exploit_floor`); wired in `father.py:1181/1209/1363` | In-band diffs, timing, OOB mint, header/replay oracles → verified findings | **LIVE** (`scanner_exploit_floor_enabled=true`) |
| **OOB honest-classification autolink** (control-plane) | `oob/service.py:77` (`classify_oob`), `:188` (`sync_oob`), `:347` (`_upsert_oob_finding`) | A fired DNS/HTTP/LDAP callback proves the server made an out-of-band request; class DERIVED from callback protocol, sink-clustered + capped | **LIVE** |
| **Browser DOM-exec instrument** (`/instrument`, sink/source hooks + real-exec callback) | `docker/browser/browser_server.py:803` + `:301` (`build_domxss_payload`) + `:331` (`_INSTRUMENT_JS`) | DOM/stored XSS proved by **actual execution** (`executed:true`), not a string match | **LIVE** (sidecar on); agent-invoked (`browse instrument`) or auto in `thorough` mode (`config.py:231` `browser_instrument_on`) |
| **Browser crawl** (deterministic BFS, form-login, JS/secret mining, HAR) | `browser_server.py:535` (`/crawl`), `:234` (`secrets_from_js`), `:181` (`forms_from_html`) | Surface discovery + JS-embedded secrets (regex proof) | **LIVE** sidecar; its api_discovery output needs `scanner_api_discovery_enabled` → **now ON in prod** (2026-09-26 47a051e) |
| **Chain floor** (deterministic next-hop from a CONFIRMED primitive) | `chain/floor.py:315` (`run_chain_floor`), `:174` IMDS, `:225` LFI→secrets | SSRF→IMDS cred theft / LFI→config secrets = escalation proof | **OFF** (`SCANNER_ENGINE_CHAIN_FLOOR` unset, `father.py:529`) |
| **A1 verifier + proof capsule** | `engine/verify.py`, `finalize.py:733/919` | Independent reproduction of H/C findings | **LIVE** (needs model creds) |
| **Recon floor** (deterministic recon sweep, mirrors exploit floor) | `engine/recon_floor.py` | Surface/inventory, not vuln proof | **LIVE** (`SCANNER_RECON_DEPTH=1`) |
| **LLM fleet** (engine-v2 workers, skills-guided) | `engine/father.py`, fleet | Everything the deterministic layer can't; self-declared findings gated by evidence-gate (OFF) + A1 verifier | **LIVE** |

### 4.2 MASTER TABLE — every VulnClass (58 total, `taxonomy.py:17-85`): can we PROVE it deterministically today?

Legend for "Machine oracle": **YES** = a deterministic builder+parser writes a `verified` finding with no LLM in the loop; **OOB** = proven only by a fired out-of-band callback; **PARTIAL** = an oracle exists but is heuristic/narrow; **signal-only** = the floor probes and emits an LLM-triage signal, never a finding; **skill-only** = NO machine oracle anywhere, rides entirely on the LLM + skill. Applicability from `ledger/applicability.py:126`.

#### Injection family (`_INJECTION` = sqlmap; blind sinks in `_SSRF` family)
| Class | Applicable element kinds | Machine oracle (file:line) | How it's PROVED | Verified-trust |
|---|---|---|---|---|
| `sqli` | url/api_operation/form + param w/ `has_params` (`_NEEDS_PARAM`) | **YES** — boolean-blind `parse_boolean_diff` (`:1389`) + time-blind `parse_time_blind` (`:1362`) in `_sqli_oracle` (`:1905`); then sqlmap `parse_sqlmap` (`:778`) in `_sweep_injection` (`:2003`); + OOB `build_sqli_oob_cmd` (`:379`) | in-band TRUE/FALSE diff (status flip / ≥30% len diff); OR ~5s timing delta vs control; OR sqlmap "is vulnerable"; OR DNS/HTTP OOB callback | boolean/sqlmap/OOB = trusted; **`sqli-time` demoted** (timing FP-prone, `exploit_quality.py:129`) |
| `nosqli` | param | **PARTIAL** — swept by `_INJECTION` (sqlmap + `build_sqli_oob_cmd` OOB) | sqlmap injectable / OOB callback (SQL boolean/time payloads are SQL-specific) | sqlmap/OOB trusted |
| `ssti` | param | **YES** — `parse_ssti` math-eval (`:1287`), random `n1*n2` polyglot (`_ssti_polyglot :693`) in `_inband_ssrf_oracle` (`:2634`); OOB fallback | server rendered the arithmetic PRODUCT it never received literally | trusted (`exploit_floor:ssti`) |
| `cmdi` | param | **YES(timing)+OOB** — time-blind `build_time_cmdi_cmd` (`:1340`)/`parse_time_blind`; OOB `build_cmdi_oob_cmd` curl+nslookup beacon (`:348`) | ~5s sleep delta OR OOB callback (a shell reached out) | **`cmdi-time` demoted**; OOB callback = **critical**, trusted |
| `xxe` | url/api_op/param, `_SINK_GATED` (body/POST/sink_hint) | **OOB** — `build_xxe_oob_cmd` external-entity → OOB (`:363`); chain FILE_READ hop | parser fetched our external entity (OOB callback) | OOB trusted (high) |
| `lfi` | param | **YES** — `parse_lfi` (`:1429`): `/etc/passwd` `root:…:0:0:`, WEB-INF/web.xml, php://filter base64 `<?php` (`:2694`); chain→secrets (`chain/floor.py:225`) | concrete file-content marker in the body (in-band) | trusted (`exploit_floor:lfi`) |
| `rfi` | param | **PARTIAL** — shares the LFI in-band path + `_SSRF` OOB (`_inband_ssrf_oracle` treats LFI/RFI together) | LFI-style file marker / OOB URL-fetch (true remote-include not distinctly proven) | trusted if marker |
| `ldap` | param | **skill-only** — in `_NEEDS_PARAM` but NO floor family claims it | LLM + skill only | n/a |
| `xpath` | param | **skill-only** — no family | LLM + skill only | n/a |
| `ssi` | param | **skill-only** — no family | LLM + skill only | n/a |
| `crlf` | param | **skill-only** — no family | LLM + skill only | n/a |

#### XSS family (`_CLIENTSIDE` = dalfox + in-band confirmer + browser)
| Class | Applicable | Machine oracle (file:line) | How PROVED | Trust |
|---|---|---|---|---|
| `xss_reflected` | url/param w/ `has_params` or `html` ct (`_XSS`) | **YES** — `classify_reflection` (`:524`) svg/quote-breakout across query/form/JSON in `_sweep_clientside` (`:2541`); then dalfox `type=="V"` (`parse_dalfox :815`); + blind-XSS OOB beacon (`:2599`); + browser `/instrument` | un-encoded canary reflected in an executable HTML/attr/js context; OR dalfox verified PoC; OR OOB callback; OR browser `executed:true` | in-band/dalfox/OOB/browser all trusted |
| `xss_stored` | url/param | **YES** — 2-request inject-A/observe-B oracle `_sweep_stored_xss` (`:2439`, `_two_request_oracle :1849`, `new_canary :561`); + browser instrument `extra_canaries` | canary submitted on route A rendered raw in HTML on sibling route B; OR browser real-exec on render | trusted |
| `xss_dom` | url/param | **YES(browser)** — `/instrument` (`browser_server.py:803`), `build_domxss_payload`→`__domxss_exec` (`:301`), sink hooks for innerHTML/outerHTML/insertAdjacentHTML/setAttribute/document.write/eval/Function (`:66`, `_INSTRUMENT_JS :331`) | attacker canary reached a DOM sink AND the payload actually executed (`executed:true`) | trusted; **LIVE** but requires the browser sidecar + agent to call `browse instrument` (auto in `thorough`) |

#### Access family (`_ACCESS` = differential replay + spec-diff)
| Class | Applicable | Machine oracle (file:line) | How PROVED | Trust |
|---|---|---|---|---|
| `auth_bypass` | any web/API (`_ACCESS`) | **YES** — `diff_access` `unauth_access` (`:978`) in `_sweep_access` (`:2830`) gated on `_looks_protected`; spec-diff unauth 2xx (`_sweep_spec_diff :3129`); 2FA step-skip (`:2936`) | anon request returns 200 with real protected DATA (not an SPA shell, `_is_app_shell :890`; matches the authed body, `_bodies_equivalent :906`); OR privileged spec op answers 2xx unauthenticated | two-identity/anon-vs-authed differential; trusted |
| `idor_bola` | any web/API | **YES(bola)+signal(idor)** — `diff_access`: `bola` byte-identical cross-user body on an id-bearing endpoint self-proves (`:1014`, `_has_object_id :931`); `idor` id-tamper different-200 = signal (`:990`) | user_b receives the identical object as user_a (BOLA); id-tamper → different object = signal | bola trusted; idor signal-only |
| `bfla` | any web/API | **YES** — `diff_access` `bfla` (`:1002`): admin baseline 200 + low-priv user_a 200-with-data on an admin-shaped path; spec-diff low-priv admin op (`:3183`) | vertical priv-esc confirmed against an admin baseline | trusted |
| `priv_esc` | any web/API | **PARTIAL** — claimed by `_ACCESS`, swept via `diff_access` but no dedicated `priv_esc` self-prover (folds into `bfla`) | proven only when it manifests as BFLA; else signal | partial |
| `forced_browse` | any web/API | **YES** — covered by the `unauth_access` oracle (anon reaches a protected path) | anon replay reaches protected content | trusted |

#### Blind/standalone sinks (`_SSRF` family = OOB mint + in-band)
| Class | Applicable | Machine oracle (file:line) | How PROVED | Trust |
|---|---|---|---|---|
| `ssrf` | param (`_NEEDS_PARAM`) | **OOB** — `build_ssrf_cmd` mint-and-fire (`:323`), `_sweep_blind` (`:2760`); chain IMDS hop (`chain/floor.py:174`) | fired OOB callback (server dereferenced our host); chain: IMDS cred/reach body | OOB trusted (high); IMDS cred = **critical** (chain OFF in prod) |
| `open_redirect` | param | **YES** — `parse_openredirect` (`:1458`) unique off-site Location/meta/js (`:2722`) | 3xx `Location` (or meta-refresh/js) to a unique per-probe marker host | trusted (`exploit_floor:open-redirect`, medium) |
| `deserialization` | `_SINK_GATED` | **OOB** — `build_deser_oob_cmd` ysoserial **URLDNS** DNS-only always-on (`:414`); php/.NET gadgets `build_deser_php/dotnet_oob_cmd` (`:435/:454`) **GATED** off (`_deser_rce_enabled :479`, `scanner_deser_rce_confirm_enabled=false`) | DNS callback = endpoint deserialized attacker bytes | OOB trusted; php/.NET beacons **OFF** in prod |
| `file_upload` | `_SINK_GATED` | **skill-only** — no floor family claims FILE_UPLOAD | LLM + skill only | n/a |
| `prototype_pollution` | param | **skill-only** — no family | LLM + skill only | n/a |

#### Config / info-disclosure (`_CONFIG` = nuclei + default-creds)
| Class | Applicable | Machine oracle (file:line) | How PROVED | Trust |
|---|---|---|---|---|
| `default_creds` | web + `auth_surface` (`_AUTH`) | **YES(basic)/PARTIAL(form)** — `_try_default_creds` (`:2067`), `parse_defaultcreds` (`:1525`), 6-cred lockout-guarded matrix | Basic-auth baseline-401→attempt-2xx (clean); form arm = bounded heuristic (new session cookie + landed + no pw field) | basic trusted; form heuristic |
| `secrets_exposure` | any web/`_ANY_URL` (+assets) | **YES** — nuclei exposure templates (`_sweep_config :2117`, `parse_nuclei :789`); browser `secrets_from_js` AKIA/AIza/jwt/PEM regex (`:234`); chain LFI→secrets | nuclei critical/high match; OR JS-embedded secret regex; OR chain-read config secret | nuclei/regex trusted |
| `debug` | `_ANY_URL` | **YES** — hygiene verbose-error `parse_verbose_error` (`:1241`) curated stack-trace sigs (`:2295`); + nuclei | curated stack-trace/verbose-error signature in body | trusted (`exploit_floor:hygiene`, low) |
| `takeover` | host/service (`_HOST_OR_SERVICE`) | **PARTIAL** — nuclei takeover templates (config) | nuclei fingerprint match | nuclei match |
| `cloud_bucket` | service (`_SERVICE`) | **YES(chain)/nuclei** — chain IMDS cred theft → cloud_bucket **critical** (`chain/floor.py:196`); nuclei | live IMDS AccessKeyId+secret in body (chain, OFF in prod); OR nuclei | trusted; chain OFF |
| `sourcemap` | `_ANY_URL` (+.js/.map) | **PARTIAL** — nuclei exposure | nuclei template | nuclei |
| `backup` | `_ANY_URL` | **PARTIAL** — nuclei | nuclei template | nuclei |
| `vcs` | `_ANY_URL` | **PARTIAL** — nuclei | nuclei template | nuclei |
| `dir_listing` | `_ANY_URL` | **PARTIAL** — nuclei | nuclei template | nuclei |
| `open_service` | service/host | **PARTIAL** — nuclei | nuclei template | nuclei |
| `missing_email_auth` | service/host | **skill-only** — no family oracle | LLM + skill only | n/a |

#### Hygiene / client-side / crypto (`_HYGIENE`, `_NOFAMILY`)
| Class | Applicable | Machine oracle (file:line) | How PROVED | Trust |
|---|---|---|---|---|
| `security_headers` | any web (`_ANY_WEB`) | **YES** — `parse_hygiene_headers` (`:1095`) missing CSP/XFO/XCTO/Referrer; `_core_headers_all_missing` (`:1221`) in `_sweep_nofamily`/`_sweep_hygiene` | literal absence of core headers in a real response | trusted (low) |
| `weak_session` | web+auth (`_AUTH`) | **YES** — `parse_hygiene_headers` Set-Cookie missing Secure/HttpOnly (`:1115`) | cookie attribute absence | trusted (low) |
| `protocol` | service+tls (`_TLS`) | **YES** — missing-HSTS (`:1107`) + HTTP-downgrade `parse_http_downgrade` served-cleartext (`:1234`, `_sweep_hygiene :2270`) | missing HSTS on HTTPS; OR plain-HTTP 2xx served with no redirect to https | trusted (low/medium) |
| `cors` | any web | **YES** — `parse_cors` (`:1170`) attacker-Origin reflected + `ACAC:true` (`_sweep_nofamily :2374`) | ACAO reflects our evil origin AND credentials allowed | trusted (medium) |
| `host_header` | any web | **YES** — `parse_host_header` (`:1192`) spoofed Host in an absolute Location/`//evil` link (`:2388`) | injected Host reflected into an absolute redirect/link | trusted (medium) |
| `csrf` | any web | **YES(narrow)** — `parse_csrf` (`:1211`) state-changing (POST/PUT/PATCH) authed cell with NO anti-CSRF token AND NO SameSite (`:2402`) | form lacks token field AND no SameSite cookie | trusted (low), LOW-FP gated |
| `cache_poisoning` | any web | **PARTIAL/none** — in `_CONFIG` (nuclei) + `_NOFAMILY` coverage-only (`:2427` "no cheap reliable oracle") | nuclei template only; else coverage record, never a finding | skill/nuclei |
| `weak_cipher` | service+tls | **skill-only** — `_HYGIENE` claims it but hygiene has no cipher oracle (headers/downgrade only) | LLM + testssl skill | n/a |
| `cert` | service+tls | **skill-only** — `_HYGIENE` claims it, no cert oracle | LLM + skill | n/a |
| `smuggling` | `_ANY_URL` | **skill-only** — no family | LLM + skill | n/a |

#### Business-logic (`_LOGIC` — signal-only by design) + API + auth
| Class | Applicable | Machine oracle (file:line) | How PROVED | Trust |
|---|---|---|---|---|
| `price_tamper` | any web (`_ACCESS`) | **signal-only** — `build_price_tamper_cmd` (`:642`) in `_sweep_logic` (`:2970`) | probe fires (price→0.01), emits LLM-triage signal; NEVER a finding | signal-only |
| `mass_assignment` | param | **signal-only** — `build_mass_assignment_cmd` (`:650`) | privileged-field POST, signal | signal-only |
| `race_condition` | any web | **signal-only** — `build_race_cmd` N-concurrent (`:669`) | not deterministically provable → signal | signal-only |
| `quota_abuse` | any web | **signal-only** — race-style burst | signal | signal-only |
| `workflow_abuse` | any web | **signal-only** — replay probe | signal | signal-only |
| `rate_limit` | any web (`_ANY_WEB`) | **YES** — `build_burst_cmd`/`parse_ratelimit` (`:1553/:1589`) absence-of-429/503 on an ALIVE credential endpoint (`_ratelimit_alive :1599`, `_sweep_ratelimit :3001`) | bounded sequential burst returns no 429/503 on an alive auth endpoint | trusted (LOW-FP alive-gated) |
| `jwt_flaws` | web+auth | **skill-only** — `_AUTH`, no floor family | LLM + skill (jwt_tool) | n/a |
| `oauth_saml` | web+auth | **skill-only** — no family | LLM + skill | n/a |
| `graphql` | graphql kind | **skill-only** — no floor oracle (introspection via api_discovery/skill) | LLM + skill | n/a |
| `websocket` | websocket kind | **skill-only** — no family | LLM + skill | n/a |
| `excessive_data` | any web | **skill-only** — `_NOFAMILY` coverage-only, no oracle (`:2427`) | LLM + skill | n/a |

### 4.3 Honest scorecard summary

- **Deterministic machine oracle exists (verified finding, no LLM):** sqli, ssti, lfi, open_redirect, xss_reflected, xss_stored, xss_dom(browser), auth_bypass, bfla, idor_bola(BOLA arm), forced_browse, security_headers, weak_session, protocol, cors, host_header, csrf, debug, default_creds(basic), secrets_exposure, rate_limit. **≈21 classes.**
- **OOB-callback-proved only:** ssrf, xxe, cmdi(also timing), deserialization, blind sqli, blind/stored xss beacon. Proof = a real out-of-band interaction, honestly re-classified from the callback PROTOCOL (`classify_oob :77`) — a URL-fetch beacon confirms **ssrf**, never the agent's claimed sqli/cmdi; sink-clustered + capped at 12 (`_oob_finding_cap :100`) to kill fan-out.
- **Signal-only (floor probes, LLM must confirm impact):** price_tamper, mass_assignment, race_condition, quota_abuse, workflow_abuse, idor(id-tamper arm), priv_esc(unless BFLA).
- **Nuclei-template-dependent (PARTIAL):** takeover, sourcemap, backup, vcs, dir_listing, open_service, cloud_bucket, cache_poisoning.
- **Skill-only / NO machine oracle (rides entirely on the LLM):** ldap, xpath, ssi, crlf, file_upload, prototype_pollution, missing_email_auth, weak_cipher, cert, smuggling, jwt_flaws, oauth_saml, graphql, websocket, excessive_data. **≈15 classes** — these are declared in the taxonomy and open ledger cells, but there is no deterministic confirmer; a finding here is only as good as the model + skill + (if creds present) the A1 verifier.

### 4.4 Load-bearing caveats (things that look "on" but aren't)

- **Evidence gate is OFF in prod** (`config.py:182`, `docker-compose.yml:123`): a bare `{category, endpoint}` LLM claim confirms its cell without a proof artifact. The gate is built and tested; it's just not flipped on.
- **Deterministic CHAIN floor is OFF** (`father.py:529`, no compose env): SSRF→IMDS-cred-theft and LFI→secrets escalation proofs do NOT fire in production. (Note: `SCANNER_CHAIN_SYNTHESIS=true` at `docker-compose.yml:214` is the *LLM/graph* chain-synthesis, a different mechanism, and IS on.)
- **`api_discovery` now ON in prod** (`docker-compose.yml:145`, 2026-09-26 47a051e) — the browser's XHR/form body-param records and GraphQL introspection materialize as `api_operation` cells (body-injection/mass-assignment/BFLA surface); P3-A #23 additionally surfaces shadow/zombie/debug ops as `exposure.shadow_api` findings.
- **`finalize_leftover` OFF in prod** (`docker-compose.yml:153`) — the trailing re-verify/enrich completeness gate never runs.
- **Timing oracles are not trusted**: `exploit_floor:sqli-time` / `:cmdi-time` are deliberately excluded from deterministic-oracle trust (`exploit_quality.py:129`) and demoted to weak/`verified=false` at ingest — a slow endpoint would otherwise false-positive. Only boolean-diff / OOB / in-band-content oracles are auto-trusted for those sinks.
- **php/.NET deserialization RCE-confirm beacons are GATED off** (`scanner_deser_rce_confirm_enabled=false`, `config.py:206`, `docker-compose.yml:237`): only the DNS-only Java URLDNS gadget fires by default.
- **DOM-XSS instrument is LIVE but opportunistic**: it only runs on URLs the agent passes to `browse instrument`, or automatically in `thorough` mode (`config.py:231`) — it is not an unconditional full-surface sweep.

---

## 5. The implementation program (what we are building)

This section is the forward-looking companion to the current-state map: it records **what is planned, in-flight, and deliberately not being built**, with honest status labels so no future agent mistakes a roadmap phase for shipped behavior. It is a faithful digest of the live tracker and its two feeder docs — **not** a re-verification. Where a concrete claim appears, it cites the tracker's own code-verified finding.

**Authoritative sources (read these before acting on this section):**
- `docs/roadmap/2026-09-26-implementation-tracker.md` — the **live tracker**: locked decisions, S0/S1 results, Phase-0 code-verified statuses, B8 truth-table, the 4 in-flight workstreams, merged phase plan. **This is the owner doc; it supersedes stale line-refs in the feeder docs.**
- `docs/roadmap/2026-09-25-unified-engine-roadmap.md` — the **sequencing owner** (Phases 0–5 + benchmark + parked; the "validation-first" thesis).
- `docs/roadmap/2026-09-25-core-engine-gap-analysis.md` — the **code-verified gap classifier** (which review gaps are CORE vs ADDITIONAL; G01–G49).
- Item detail: `docs/roadmap/2026-09-25-core-scanning-engine-roadmap.md` (#1–#30); ops/enrichment: `docs/roadmap/2026-09-25-additional-features-roadmap.md`; orchestration: `docs/roadmap/2026-09-25-orchestration-architecture-v3.md` (B1–B8).

**Program status as of 2026-09-26:** the program is at **S1-complete / pre-implementation**. S0 (gap correlation) and S1 (code verification + in-flight characterization) are DONE; S2–S5 (fold gaps → merged plan → branch decision → implement Phase 0) are NOT started. **Nothing in Phases 0–5 is implemented yet.** The 4 in-flight workstreams (§5.4) are now **committed** on `feat/alpha-observability` (`0d3be20`, `d70925a`, `a21890d`, `1b2653c` + test `2939017`) but not yet merged to main (`fixes/critical-improvements`) or deployed. Work sequence per tracker lines 30–36: S0 ✅, S1 ✅, S2 ☐, S3 ☐, S4 ☐ (in-flight work now committed on the branch — the tracker's "blocked on operator approval to commit" is superseded; merge/deploy decision still open), S5 ☐.

**Status legend used throughout:**
| Label | Meaning |
|---|---|
| **BUILT-AND-LIVE** | In production code path, on by default |
| **BUILT-BUT-OFF** | Code exists, gated off by a flag in the fresh-deploy `docker-compose.yml` |
| **IN-FLIGHT** | Committed on `feat/alpha-observability`; not yet on a merge branch or deployed |
| **PLANNED** | Roadmap phase, no code written |
| **PARTIAL** | Some machinery built (often off/fail-open); the delta is planned |
| **PARKED** | Deliberately not being built (evidence-backed) |
| **DEAD-CODE** | Present in `src/` with zero callers; slated for deletion |

---

### 5.1 Locked operator decisions (2026-09-26)

These four decisions (tracker lines 14–18) set the scope boundary for the whole program.

| # | Decision | Consequence |
|---|---|---|
| **1** | **Target profile = ALL of {classic web+API, SSO+multi-tenant SaaS, chat/LLM/MCP-endpoint apps}.** Build as **general primitives the agent/boss selects per target** — never per-segment products. | The detection-gated AI red-team floor (§3.9), cross-tenant isolation, and SSO/OAuth login are all **in scope, not parked**. Add more specific tools as targets require. |
| **2** | **Scan model = point-in-time now, architected for continuous later.** | Do **not** build the scheduler / cross-scan features yet, but do **not** architecturally block cross-scan union — ledger/inventory design stays forward-compatible. |
| **3** | **Compliance (annex / tamper-evident evidence / evidence vault) = ADDITIONAL**, recorded in the additional-features roadmap, not core. | The pre-LLM redaction leak (secrets reaching the external verifier model unredacted) stays in the additional track but is **flagged as a near-term security fix**. |
| **4** | **Directive:** fold accepted CORE gaps into the unified roadmap → produce a merged, documented plan → **start implementing**: very supervised, TDD (test-first), small flag-gated commits (production byte-identical when off), multi-model fleet with review gates, no overlap with in-flight work. | Standards bar: OWASP Top 10 (2021) / OWASP API Top 10 (2023) / OWASP WSTG / OWASP LLM Top 10 (2025) + MITRE ATLAS for the AI surface. Garbage cleanup (MemoryStore/Gateway/dead legacy) as we go. |

**The sequencing thesis (unified roadmap §"thesis"):** the substrate is already the SOTA orchestration pattern (Intentest arXiv:2609.07344 + arXiv:2609.10780 both endorse the ledger+lease+quiescence design already running); the market leader (XBOW) wins on **deterministic validation, not orchestration**; the plan's code premises are verified true. **One-line rule: make coverage honest → make findings provable → let a planner drive → widen the surface → chain to impact. Validation before breadth, always.**

---

### 5.2 Merged phase plan (Phase 0–5)

Phases follow the unified roadmap's validation-first order; core-gap items (Gnn) slot in by phase (tracker lines 74–84). **Every item below is PLANNED unless its status column says otherwise.** Every core item is required to land with a benchmark-target regression check (§5.3).

#### Phase 0 — Honest foundation (bugs + truthful coverage) · ~1 week
> The substrate for the freeze signal and the validator. Several are silent-failure bugs live in production today. Nothing above this is trustworthy until it lands.

| Item | What / where | Code-verified status (tracker S1, lines 48–61) |
|---|---|---|
| **B1** — claim/release under one stable `worker_id` | `father.py` batch pool (`:1807`→`:1174`→`service.py:1286` claim) vs release (`father.py:1254`/`:1328`/`:1333`→`service.py:1345`) | **PLANNED (still-broken, live on batch path).** Claim tags `wave{N}`, release tags `batch{w}-{id}-{model}` → **0 rows freed**. The in-flight 2→6 batch bump (§5.4 #2) **amplifies** it. Fix template: escalation path already pairs claim+release under one `esc_wid` (`:1650`/`:1670`). |
| **B2** — 6h wall bypasses the quiescence AND-gate | `father.py:1784`, `governor.py:41` | **already-correct.** Works as designed; only silently defeated by B3's fail-open reads. Per tracker, **B2 ≡ fix B3**. |
| **B3** — quiescence/progress reads fail **closed** + log | `_has_claimable` (`father.py:1405-1406`), `count_claimable` (`attack_surface.py:163-164`, file has **no logger import**), `_unresolved` (`father.py:1140`) | **PARTIAL.** `_has_claimable` + `count_claimable` still swallow exceptions silently. `_unresolved` **already logs** (committed `36fece4`) → roadmap stale here. Structural "0 = progress" (`:1748`) remains, low-urgency. |
| **B4** — reopen preserves/decrements attempts | `ledger/service.py:1022` (one-liner); 3 callers via `reopen_cells_for_classes` | **PLANNED (still-broken).** A reopened cell resets `attempts=0`, so it never converges to terminal `attempted`. |
| **B5** — batch path restores `board_totals`/`capability_ctx` | `_task_for` (`father.py:1256`) vs `:654`; totals computed `:1807`, discarded | **PLANNED (still-broken).** Batch workers don't get the S4 coverage board → re-test proven ground. Same locus as B1. |
| **B7** — governor workers=targets | `worker.py` governor backstop | **PLANNED (still-broken but HARMLESS).** Dead/misleading backstop; roadmap says do **NOT** "fix into a real cap" — just note/relabel. |
| **B8** — one config truth-table | `config.py`, `docker-compose.yml`, `docker-compose.override.yml` | **doc+test deliverable.** Truth-table built (below). `docker-compose.override.yml` is **gitignored** → fresh deploy runs the `docker-compose.yml` column. |
| **#6 / evidence-gate flip** | `scanner_evidence_gate` — `config.py:182` default, `docker-compose.yml:123`, `ledger/service.py` (`sync_from_work`→`resolve_cells` `:805`, flag `:967`) | **BUILT-BUT-OFF, latent fail-open.** Fully wired but default-OFF everywhere. Fails open via `finding_id` in `_EVIDENCE_FIELDS` (`:137`) — moot on the live JSONL path (no `finding_id` at resolve time). Fix = drop `finding_id` + flip flag + validate on one live scan. Deeper "require FIRED oracle + pending/flaky states" = **G01, Phase 1**. |
| **#19** — skill-per-cell enforcement | `ledger/service.py`, `coverage_qa.py`, `father.py` | **PLANNED (missing).** No per-cell required-oracle gate. `weapon_swept` accepts ANY `exploit_floor:` method; `_probe_ok` is endpoint-level + default-off; `coverage_qa.py` has the class→tool map but is observability-only. Real build. A cell with no fired oracle must **not** reach `tested_clean` → requeue. |
| **#28** — poller-side finalize rollup | `scheduler/poller.py`, engine finalize | **PARTIAL.** Durable findings are **not** under-counted (finalize ingests `findings.jsonl`). GAP: `sync_zap` + `rollup_findings_count` run **only in-container**, absent from poller salvage → ZAP alerts lost + telemetry under-counts. In-flight dead-node path (§5.4 #4) inherits the gap. Lazy fix: move both into `finalize_scan`. ZAP dormant on fresh deploy, LIVE on dev-override host. |
| **#30** — honest coverage counts | `reporting/service.py:121-122` (`_coverage`, now ~`:110`), `father._render_board_totals:436`, `_OPEN_STATES:49` | **PLANNED (still-broken).** `resolved + open != total` confirmed: reporting drops `attempted` from **both** buckets; `_OPEN_STATES` treats `attempted` as resolved → the two paths **disagree**. Fix consistently so `resolved+open==total` with `attempted` visible; a one-method cell reports `partial`, not `tested_clean`. |
| **G01** — evidence **+ fired-oracle** gate on `confirmed`, fail-closed | `ledger/service.py` `_EVIDENCE_FIELDS:136-144`, cell-confirm `:830`, `_OPEN_STATES:49`; `hooks/verification.py` | **PARTIAL → Phase 0 flip, Phase 1 hardening.** Gate exists, default-off, **fails open to prose/provenance** (passes on any non-empty `finding_id`/`proof_of_concept`/`evidence_excerpt`; code's own comment admits `finding_id` is "not literal proof"). Delta: reject prose/bare-`finding_id`, **require a fired oracle**, add `pending_oracle`/`pending_human`/`flaky` states + human-review queue, route both ledger cell-confirm and `finding.verified` through the gate. The fired oracles already exist — the gate just has to require one. |
| **G07** — honest counts + detached (toolserver-free) verify | `reporting/service.py:121-122`, `ledger/service.py:49`; `finalize.py:915` (self-gates verifier on live per-scan toolserver), `_reconcile_unconfirmed_verified:423` | **PARTIAL (live bug).** Count half = #30. Detached-verify half: a SIGKILLed scan has no live toolserver, so `finalize.py:915` can't re-verify; `:423` only **demotes** unconfirmed-verified rows, never re-reproduces. Done-when: force-stopped scan satisfies `resolved+open==total` **and** its H/C findings are re-reproduced by a standalone verifier. Count fix = **S**; detached verify = **M** (Phase 0/1). |
| **G08** — fail-closed infra reads | `father.py:1396` (CRITICAL), `attack_surface.py:188-207` (`target_health` fail-open, MEDIUM) | **PLANNED.** Same surface as B3 — quiescence/target-health reads fail **closed** + log. Already tracked as CLAUDE.md Known Issues; no net-new delta beyond B3. |
| **G39** — **scanner self-defense (FLAGSHIP, foundational)** | `posttool.py:19-20` (tool-OUTPUT→LLM path **undefended** — `updatedMCPToolOutput` left unset); guard on tool-CALLS is solid (`safety.py:74-79`, `scope.py:269-307`, `bash.py:145-237`) | **PLANNED (new — in no other roadmap doc).** Hostile target pages/tool-output flow into fleet prompts unmodified. Build: (1) **poisoned-input canary suite** (seed injection payloads into simulated tool output/pages; assert the fleet neither emits the canary token nor issues the injected tool-call); (2) **guard catch-rate metric** (replay a labeled policy-violation corpus through `hook_safety`/`hook_scope`, compute % denied). Clean harness-integrity oracle. Everything downstream trusts fleet outputs → foundational. |

**B8 config truth-table (fresh deploy = `docker-compose.yml` column; override is dev-host-only, gitignored)** — tracker line 64:

| Knob | code default | override.yml (dev host) | docker-compose.yml (fresh deploy) |
|---|---|---|---|
| attempt cap | 3 | 3 | 2 |
| lease | 6000 | 6000 | 3000 |
| worker wall | 5400 | unset | 2400 |
| max_waves | 3 | unset | 150 |
| stuck window | 0 | 300 | 0 |
| pool cap | 8 | 8 | 6 |
| seat models | False | **true** | true |
| runaway wall | 6h | 6h | 1h |
| **evidence_gate** | **OFF** | **OFF** | **OFF** (everywhere) |
| **batch_dispatch** | False | **true** | true |

#### Phase 1 — Proof & validation (the moat; biggest competitive win) · ~2 weeks
> Where XBOW wins and the current PoC axis scores lowest. Converts "self-declared verified" into "machine-proved."

| Item | What / where | Status |
|---|---|---|
| **#5** — oracle-first, never-fail-open verification | `hooks/verification.py` | PLANNED. Nothing reaches `confirmed` without a fired oracle/evidence; oracle-unavailable → `pending`, never auto-pass. |
| **#6** — evidence gate ON | (flipped in Phase 0) | Phase-0 flip; the fired-oracle requirement is the G01 Phase-1 delta. |
| **#9** — deterministic oracles for the blind/hard classes | `exploit_floor.py`, `oob/` | PLANNED. JWT-flaw, file-upload, CRLF, request-smuggling, OAuth `redirect_uri`/PKCE each fire a machine check. Absorbs **G26** + **G36**. |
| **#10** — driven browser: real client-side execution proof | `docker/browser/` `/instrument` | **BUILT-BUT-OFF (generalize + turn on).** DOM-XSS execution proof is **built** (`browser_server.py` `INSTRUMENT_SOURCES:67`, `build_instrument_init_script:313` hooks innerHTML/setAttribute/document.write, marks `executed:true` on real sink execution `:361`) but gated off by `scanner_browser_enabled` (deviation #8). Delta = broaden + ship default-on for the proof path. = **G32**. |
| **#15** — file-upload oracle | `exploit_floor.py` | PLANNED (missing). No multipart/`-F` upload builder today. Prove an unrestricted upload via a retrievable+triggerable stored artifact. = core half of **G33**. |
| **#16** — generic response-diff oracle (payload vs control) | `exploit_floor.py` | PLANNED. ≥2 classes (access-control + injection) confirm through one shared diff primitive. |
| **#21** — detached verify past agent/toolserver exit | `finalize.py` + standalone verify path | PLANNED (= G07 detached-verify half). A poller-finalized/salvaged scan still verifies its findings. |
| **A1 verifier hardening** | `agent_runtime/finalize.py`, `verify.py` | PLANNED. Independent (non-Anthropic) re-repro of every self-declared H/C; unconfirmed → downgraded; verifier **cannot** `write_finding`. |
| **G02** — **proof-capsule on every H/C (headline deliverable)** | `hooks/verification.py:154` `_build_capsule` (6-key redacted capsule), `finalize.py:733-741` `_stamp_status`, `reporting/service.py:210/230` render | **PARTIAL (mechanism shipped end-to-end).** Capsule mints **only** on the A1-verifier reproduction path (`hooks/verification.py:208`); oracle-proven findings **skip** the verifier (`finalize.py:952` `is_deterministic_oracle`) → **no capsule**. Delta = make it a structurally-required, gated field on **every** H/C by unifying `oob_proof` + `exploit_floor` evidence + HAR proof (`finalize.sync_har_proof`) into one capsule shape. A H/C with no capsule cannot ship. |
| **G26** — JWT/OAuth/session/token-replay oracles | `exploit_floor.py` (no `build_jwt*`/`oauth*` today; `WEAK_SESSION` is only a Set-Cookie flags check `:1100-1123`) | PLANNED (folds into #9). Net-new delta beyond #9/#18: token-replay/refresh-replay oracle, JWT `kid`-injection, IdP-confusion/wrong-audience. alg-none/confusion forge → protected endpoint returns 200+data; session id unchanged across auth boundary; token accepted after logout. |
| **G32** — client-side execution proof (broaden + turn on) | `docker/browser/` | PLANNED (= #10). Adds prototype-pollution execution oracle, CSP/CORS-bypass confirmation, storage/service-worker leakage; ship browser default-on. |
| **G36** — CRLF / request-smuggling oracles | `taxonomy.py:27` (CRLF, in `_NEEDS_PARAM` `applicability.py:26`, **no builder/parser**); `taxonomy.py:47` (SMUGGLING, LLM-prompt only) | PLANNED (folds into #9). Injected header/response-split observed = CRLF oracle; paired control-request desync = smuggling (**run only where safe**). |

**Phase-1 done-when:** on the benchmark set, H/C false-positive rate drops measurably and every H/C finding in a report links to a proof artifact.

#### Phase 2 — Boss-as-planner (the one endorsed new capability) · ~1 week · flag-gated
> The only new orchestration capability the evidence supports. Makes the operator's playbook actually drive the scan (it doesn't today). Boss is a **bounded per-tick function, not a session**.

| Item | What / where | Status |
|---|---|---|
| **#1** — playbook → engine-v2 | `engine/methodology.py`, `run.py`/`father.py` | PLANNED. Two playbooks must produce measurably different phase coverage on the same target. (Today the fleet ignores playbooks.) |
| `policy.md` assembler (human layer-1 mirror) | intake-time string build from `ScopeConfig`/blocklist/playbook | PLANNED. Written once at boot; every clause maps to existing code enforcement. |
| `engine/boss.py` — bounded per-tick planner call | new, on `build_engine_execute_fn(require_tools=False)` | PLANNED. One call/tick, `max_turns` 8, wall 180s; failure ⇒ prior plan stands (byte-identical to today when flag off). |
| `engine/plan_gate.py` — deterministic PlanGate | new; reuses `sample_open_cells`, `in_scope`, `taxonomy.normalize` | PLANNED. An objective materializes **only** if it maps to a real open, applicable, in-scope cell of a known class; zero-cell objectives rejected + fed back. Fact-gating at Intentest strength (prefer execution-verified predecessor facts). |
| `plan.json` + brief PLAN section + `_task_for` prefix | `scan_brief.py`, `father.py:639` | PLANNED. Plan digest reaches workers; class-priority re-rank flows to `claim_family_cells`. |

**Termination is unchanged in this phase** — the boss only orders/filters existing deterministic work; `materialize` stays evidence-only. The generation-counter + freeze ships **only if recursion is ever built** (it is PARKED), so it is **not** in this phase.

#### Phase 3 — Surface & identity depth (make the denominator real; cover every segment) · ~2–3 weeks
> Built as **general primitives, then the agent/boss selects per target** — honors decision #1 without a per-segment product.

| Item | What / where | Status |
|---|---|---|
| **#2** — turn on API discovery + spec import | `scanner_api_discovery_enabled` compose flag, `api_normalizer.py` | ✅ DONE 2026-09-26 47a051e (`config.py:271` default True, compose now defaults `true` at `docker-compose.yml:145`). Spec'd target yields `api_operation` cells that get fuzzed; #23 surfaces shadow/zombie/debug ops as `exposure.shadow_api`. |
| **#3** — two-identity authorization (BOLA/IDOR + BFLA) | `exploit_floor.py`, ledger identities, `auth.json` | PARTIAL. `diff_access` (`exploit_floor.py:951`) already mints BOLA/BFLA/IDOR/unauth across anon/user_a/user_b/user_admin. Delta: request one identity's **own** resource refs as the other + planted-canary witness (part of G25). |
| **#8** — authenticated SPA crawl that stays logged in | `docker/browser/` | PLANNED. An authed SPA yields post-login routes/XHR in inventory. |
| **#4** — session keep-alive + re-auth | engine auth + browser session | PARTIAL. `is_session_expired`/`refresh_auth` (`auth_bootstrap.py:289-353`) cover session death; delta = re-auth-and-resume mid-scan. |
| **SSO / OAuth login primitive** | `docker/browser/` | PLANNED (segment-fork, general capability applied when detected). Federated IdP redirect→consent→callback login. |
| **Multi-tenant isolation primitive** | two-tenant identities + `exploit_floor` | PLANNED (segment-fork). Prove tenant A cannot read tenant B. Tenant-B identity is **absent today** (only a `scan_brief.py` comment). |
| **G25** — identity matrix + object-action-role authz oracle | `exploit_floor.diff_access:951`, `auth_bootstrap.py:71-76` (exactly 4 slots), `applicability.py:126` (endpoint×vuln_class, no object×action×role) | PARTIAL. Reviews' "absent" framing is **wrong** — the diff is built. Missing: JWT token-state oracle (JWT_FLAWS/OAUTH_SAML open but in no `exploit_floor` family), roster beyond 4 slots, object×action×role family, tenant-B identity, planted-canary (vs byte-match) BOLA proof. |
| **#11 / #12** — GraphQL op-authz + BOPLA property-diff | `api_normalizer.py`, `exploit_floor.py` | PLANNED. = **G29**. |
| **G29** — GraphQL field-level authz oracle | introspection detected (`recon_floor.py:78/387`), `GRAPHQL` single cell (`applicability.py:180-181`); no two-identity field-authz probe; BOPLA→`EXCESSIVE_DATA` (`taxonomy.py:221-222`) has no oracle | PARTIAL. Oracle = create-as-A/query-as-B (direct **and** nested) response-diff — same primitive as G25 applied to GraphQL fields + depth/batching-abuse oracle. |
| **G30** — WebSocket / SSE / webhook channel oracles | `applicability.py:182-183` opens `WEBSOCKET` cell, `:128` lists `webhook`; `exploit_floor.py` has **no** WS/webhook/SSE sweep (`_FAMILIES:224` omits them) | PLANNED (new; cell shell exists, no probe). Core = WS/SSE channel-auth + webhook signature-bypass/replay; **gRPC unauthorized-method invocation → ADDITIONAL** (needs reflection/spec import). Gated on surface detection. |
| **#23–#26** — shadow API / HAR import / JS-secret+sourcemap / dangling-DNS | `api_normalizer.py`, import path, `recon_floor.py` | PLANNED. Each surfaces its class on a known target. (#24 operator HAR/Postman intake.) |
| **AI red-team floor (detection-gated, OFF by default)** — **G09 + §3.9 (G10/G11/G12/G13/G14/G16/G17)** | `taxonomy.py:17-86` has **zero** AI classes; `applicability.py:12-16` no AI element kind; no `/v1/chat`/`/mcp`/MCP-manifest probe in `recon_floor.py` | PLANNED (new; mostly). **G09** = the minimal detection gate (probe AI/LLM paths + MCP manifests, emit one AI element) — no oracle of its own, admitted **only** as the runtime gate. §3.9 admitted classes (each with a deterministic witness): **G11** direct PI (forced canary token verbatim in output), **G13** system-prompt/secret extraction (planted canary secret in output), **G16** agentic tool/MCP abuse (unauthorized tool invocation in the tool-call log = confused-deputy), **G12** indirect PI (canary at existing OOB/DOM sink), **G17** output-sink injection (assistant output into `parse_xss_reflection`/OOB), **G14** RAG (planted canary phrase in the answer — **gray-box**, needs corpus write). Byte-identical to today when the surface is absent. **Mandatory safety rider (G24/G38):** self-hosted OOB/canary only, mock sinks, token caps, no third-party-provider attacks, human approval before any irreversible AI action. |
| Optional: LLM prompt-injection class taxonomy slot | `taxonomy.py` (absent today) | PLANNED (reserve slot now, build on detection). |

#### Phase 4 — Chaining & second-order proof · ~1–2 weeks

| Item | What / where | Status |
|---|---|---|
| **#20** — executed-chain finding writer | `chain/floor.py`, `reporting/service.py` | PLANNED. Report bucket populates from **already-proved** hops only. |
| **#17** — SSRF impact classification | `exploit_floor.py`, `chain/floor.py`, ledger | PARTIAL. `chain/floor.py:174` `_hop_metadata` already splits `_IMDS_CRED_RX:66` (live creds → CRITICAL) from `_IMDS_REACH_RX:72` (reach-only → HIGH). = **G34**. |
| **G34** — SSRF-reachable cloud exfiltration | `chain/floor.py` `_hop_metadata:174`, `_hop_file_read` | PARTIAL (split is **done**). Delta = extend the chain to bucket read/list/write, signed-URL bypass, serverless unauth invoke, IMDSv2 token handshake. **Standalone cloud-IAM-over-API = ADDITIONAL** (needs supplied creds + different model). |
| **#13** — second-order / deferred confirmation | `oob/service.py` + deferred reconcile | PLANNED. An async/stored issue with no immediate response signal is confirmed. |
| **#18** — session-class checks | session-test module | PLANNED. Fixation, logout-invalidation, no-rotation-after-privilege each get probe + oracle. |
| **#22** — stack-matched templates + reachability labels | recon, `exploit_floor.py`, reporting | PLANNED. Version-only matches carry `reachable`/`needs-confirmation`, never "proof." |
| **G27** — business-logic state/count/balance-diff oracle | `_LOGIC` family (`exploit_floor.py:189-199`, `build_price_tamper_cmd:642`, `build_mass_assignment_cmd:650`) fires probes but docstrings say **"Signal-only … for the LLM"** | PARTIAL. = core #14 delta. Oracle = measured state/count/balance delta before vs after abuse, **bounded to operator-recorded flows** (un-scoped API6 stays additional). |
| **G28** — race / concurrency / idempotency oracle | `build_race_cmd:669` fires N concurrent requests, docstring **"Signal-only — a race outcome is not deterministically provable"** | PLANNED (new). Pair the burst-fire with a state/count/balance diff (behind pending/flaky states). **Mandatory safety rails:** test accounts, low quantities, sandbox payments, circuit breaker (ties to intake consent flags, additional). |
| **G33** — file-upload oracle (+ document-parse OOB) | XXE-doc has an OOB oracle (`build_xxe_oob_cmd:363`); `FILE_UPLOAD` cell opens (`applicability.py:44`) but **no upload builder** | Core = the upload oracle (#15, Phase 1) + XXE-doc. Wider SVG/CSV-formula/polyglot media plane = ADDITIONAL unless a doc-processing surface is detected. |

#### Phase 5 — Reliability & resume · runs alongside, ships when ready

| Item | What / where | Status |
|---|---|---|
| **#29** — engine-v2 checkpoints / resume | engine context/run + `RESUME_PROMPT` | PLANNED. A restarted `scanner-cp` resumes from ledger state instead of salvage-finalizing — kills the "NEVER restart scanner-cp mid-scan" gotcha. |
| **Operator resume endpoint** | `POST /scans/{id}/resume` | PLANNED (additional §2). Thin wrapper over #29 — ship #29 first. |

---

### 5.3 Benchmark track (parallel with Phase 0; gates everything after)

> Not "additional" — it is the **measurement instrument**. Without it every phase ships on faith. Also the active XBOW-run goal. Extends the **already-built** harness (`benchmark/run.py`, `metrics.py`, 7 targets w/ `ground_truth.yaml`, gap-analysis G05).

| Item | Effort | Where |
|---|---|---|
| Benchmark scope-mode network wiring (`docker network connect --alias`) — **prereq for every run** | M | infra |
| XBEN / XBOW-104 target set + `FLAG{...}` sha256 scorer + committed baseline | M | extends `benchmark/run.py` + `metrics.py` |
| VAmPI (Flask+OpenAPI) for the API path | S | benchmark targets |
| CVE-Bench (40 real web CVEs + graders) — **DEFER** until XBOW-104 baseline runs | L | (deferred) |

**Rule:** every core item lands with a benchmark-target regression check. "Did it improve" = **validated findings on the harness**, never task-completion. Additional deltas on top (all ADDITIONAL): automated regression gate re-run on every worker/verifier model change; a proof-completeness metric (does each finding carry a fired oracle?).

---

### 5.4 The four IN-FLIGHT workstreams (committed on `feat/alpha-observability`, not yet on main / deployed)

Per tracker S1 (lines 40–46): the in-flight changeset = **4 cohesive, shippable workstreams, all with matching tests, NONE overlapping the Phase-0 bugs.** **Commit status: COMMITTED** on `feat/alpha-observability` as of 2026-09-26 (`0d3be20` WS1, `d70925a` WS2, `a21890d` WS3 — incl. migrations 0018/0019 + `engine_presets.py`, `1b2653c` WS4 + test `2939017`) — the tracker's "awaiting operator approval" (lines 71–72, 88, 91) is **superseded**. Not yet merged to main (`fixes/critical-improvements`) or deployed; `alembic upgrade head` still required at deploy.

| # | Workstream | What it touches | Tests | Status |
|---|---|---|---|---|
| **1** | **OOB false-positive fix** | `oob/service.py` classify-by-protocol + sink-cluster + cap; `findings.py` dedup/junk hardening; 2 OOB skills (`skills/oob-callbacks/`, `skills/pentest-finding-writer/`) | `test_oob_finding_minting.py` +129, `test_quality_gaps_op.py` +37 | IN-FLIGHT |
| **2** | **Coverage-grid fold** | `ledger/service.py` ULID/prefixed-id + param/api fold + access-control control-sample + host cap 40→500; `father.py` `_batch_max_cells` 2→6 | `test_father_p5p6.py` +70 | IN-FLIGHT. **⚠ the 2→6 batch bump amplifies the still-broken B1 claim/release mismatch** — fix B1 (Phase 0) after committing this. |
| **3** | **Scan-instructions + per-scan engine-model routing** | new `engine_presets.py`; `schemas.py`/`scans.py`/`tenant.py` new columns; migrations `0018_add_scan_instructions.py` / `0019_add_scan_engine_models.py` (committed `a21890d`); `scan_brief.py` operator-context; `worker.py`/`poller.py` forwarding; `main.py`/`seeder.py` (drops boot LLM-compile → raw YAML); frontend (`new-scan-drawer.tsx`, `types.ts`) | `test_engine_presets.py`, `test_scan_brief.py` +32 | IN-FLIGHT |
| **4** | **Poller robustness** | dead-node reap → terminal for killing/cancelling/closing (roadmap **#28-adjacent**) + orphan-GC zap/browser | `test_poller.py` +61 | IN-FLIGHT. Inherits the #28 rollup gap (`sync_zap`/`rollup_findings_count` still not in poller salvage). |

**Deploy risks flagged (tracker line 46):**
- **R1 (DEPLOY BLOCKER):** migrations 0018/0019 are committed (`a21890d`) but not yet applied to any live DB → `alembic upgrade head` is **required** at deploy or scans INSERT/SELECT fail.
- **R3:** the `gpt5.6`/`explabs` preset silently falls back to `OPENROUTER_API_KEY` if `EXPLABS_API_KEY` is unset.
- **R4:** non-builtin playbooks now seed raw-YAML (intended — drops the boot LLM-compile step).
- **R6:** the branch adds the Known-Issues list but stamps **nothing** `✅ FIXED`.

---

### 5.5 PARKED — do NOT build (evidence-backed)

Re-open only with a concrete new reason (unified roadmap §Parked; tracker line 84).

| Parked | Why (evidence) |
|---|---|
| **Orchestration hierarchy: recursive subs, manager LLM seats, agent-graph, lineage graph** | No SOTA/market evidence recursion or agent-count wins; XBOW wins on validation. The cell-on-ledger is already the parallel unit; the flat fleet already parallelizes. v3 §12 itself calls deep recursion "rarely useful." Build only if a real target proves the flat fleet can't cover it. |
| **Generation-counter + freeze-then-drain** | Only needed once minting can grow unbounded via recursion. With the hierarchy parked and `materialize` evidence-only, quiescence + attempt-cap + the (fixed) wall already terminate. Keep the spec shelved with the hierarchy. |
| **Intercepting/replay proxy container (core #7)** | The agent already replays modified requests via `kali-exec`/curl; the browser sniffer already feeds inventory. Build the response-diff **primitive** (#16) instead. |
| **pgvector / semantic / coverage memory (`MemoryStore`)** | Empirically **DEAD-CODE** (arXiv:2609.10780 — "improved neither harness and nearly tripled reasoning time"; zero callers in `src/`). **Delete it** (additional §4). |
| **Agent-to-agent messaging** | Ledger SKIP-LOCKED + `/work` rollup files give stronger, SIGKILL-survivable, dedup-safe coordination. |
| **ZAP as a core detector** | Adds breadth of the easy classes, not the authz/logic/client-side depth that is the gap. Stays flag-gated extra (additional §4), after the core. |
| **Multi-provider direct-key path, gRPC/SOAP, cross-run union, EASM/OSINT, AutoFix/PR, multi-VM** | Out of single-VM black-box web/API scope, or covered by the proxy roster today. |
| **G37 grand cell-model "compilation stage" / task-DAG restructure** | Add cell families (object×action×role, workflow×step, AI) **incrementally** under G25/G27/§3.9, not a wholesale recompile. |
| **DO-NOT-BUILD (no black-box oracle):** G22 training-data poisoning, G23 AI-behavior/explainability, G19 model inversion; **G48** GTM positioning (sourced to rejected Vynox marketing) | No deterministic witness / not engine work. Do not carry any "N+ techniques"/"39+ tools" count from Vynox/Penligent/appsecsanta into any spec or cell definition. |

---

### 5.6 Additional / enrichment track (separate; measures, ships, secures — does not find/prove more)

Guiding split: *core = finds/proves more; additional = measures it, ships it, secures the platform, or is a product surface gated on a business decision.* Source: `docs/roadmap/2026-09-25-additional-features-roadmap.md` + gap-analysis Rejected table.

| Item | Effort | Status / gate |
|---|---|---|
| **Benchmark deltas** — regression gate on model change + proof-completeness metric (G05) | M | ADDITIONAL; the gating measurement track (see §5.3), run in parallel. |
| **Cron / scheduled recurring scans** (`scanner_scheduler_enabled` + `scan_schedule` table exist, off) | S | BUILT-BUT-OFF; gate = do we sell continuous scanning? (decision #2 = point-in-time now). |
| **Retest / one-command replay as a client deliverable** (retest-to-close **built**: `api/retest.py:105` deterministic re-fire; drift diff `regression.py:160`; 5-class fix snippets — G42) | M | PARTIAL-BUILT; net-new (LLM fix-gen, CI-gate, change-triggered rescan) = productization; gate = bank deal. |
| **Cross-run union / cross-scan technique priors (SQL, no vectors)** (G40) | M | PLANNED; gate = continuous-scanning decision (a worker *hint*, not an oracle). |
| **ZAP as a 2nd DAST engine** (`scanner_zap_enabled`, off; `docker/zap/` built) | S | BUILT-BUT-OFF; explicitly demoted out of core; do after core P0/P1. |
| **Delete dead `context_memory.MemoryStore`** | S | DEAD-CODE cleanup (zero callers). |
| **`scanner_inventory_ingest_v2` flag alignment** | S | Low-leverage consistency flip (engine-v2 hardcodes v2 live; flag only affects finalize re-ingest + dead legacy paths). |
| **`MASTER_ENCRYPTION_KEY` unset warning** (`config.py:43` — gray-box creds stored plaintext, no warning) | S | Security hygiene; compliance-relevant for the on-prem/bank deal. |
| **Pre-LLM redaction fix (G46)** — redact **before** sending snippets to the external verifier/enrich model (`finalize_enrich.py`/`verify.py` feed unredacted secrets/PII today; persistence-time redaction exists at `verification.py:25-36`) | S | ADDITIONAL but **flagged near-term security fix** (decision #3). |
| **Admin ops-dashboard per-tenant logging** (`admin.py:99,183` `except: pass`) + **`target_health()` fail-open logging** (`attack_surface.py:188-207`) | S each | Observability hygiene (CLAUDE.md Known Issues). |
| **Compliance-mapping annex + one-click evidence pack (G43)** — NIST AI RMF / ISO 42001 / SOC 2 / PCI DSS v4.0.1 / GDPR / **EU AI Act Art. 15** (+ Art. 55 GPAI, **not** Art. 5) / RBI / DPDP / DORA / OWASP ASVS | M-L | ADDITIONAL (decision #3); regulated-deal enabler; no exploitation oracle. |
| **Tamper-evident / content-addressed evidence hashing (G45)** + **evidence vault (G46)** | M | DEFER; deal-gated (bank chain-of-custody). |
| **Report restructure as validation report (G44)**; **skills-catalog reach on workers (B3b)**; **AI safety rails + intake consent flags (G24/G38)** | S–M | Polish / depth-support / **build-time rider** required before shipping race-sandbox, AI floor, cloud-metadata probes (`ScanCreate` has no target-profile/consent field today). |
| **gRPC/SOAP spec import; per-key direct-provider path; in-path egress proxy; task-DAG re-planning; AI enrichment classes (G15/G18/G20/G21, G14-embedding/G17-extra-sinks, G30-gRPC, G33-media, G34-IAM)** | varies | Segment-gated / DEFER / off-core enrichment. |

**Open questions for the human (unresolved, gate specific builds):** (1) does the paying target expose a chat/MCP endpoint? → decides whether §3.9 is a P1 build or a reserved slot; (2) SSO + multi-tenant priority (tenant-B identity absent today); (3) does the bank deal require compliance annex / tamper-evidence / vault to close?; (4) point-in-time vs continuous → gates G40 + retest-deliverable; (5) per-technique consent flags at intake before shipping race/AI/cloud-metadata.

---

## 6. Config / feature-flag reality + master feature inventory + glossary

> **Ground truth for this section:** `src/scanner/config.py` (read in full) and `docker-compose.yml` (read in full) for the config truth-table; `docs/APPLICATION_CONTEXT.md` §5-§8, `docs/roadmap/2026-09-26-implementation-tracker.md` (S1 results + B8 truth-table), `docs/roadmap/2026-09-25-core-engine-gap-analysis.md` (G-IDs), `docs/roadmap/2026-09-25-core-scanning-engine-roadmap.md` (#1-#30), and `src/scanner/agent_runtime/taxonomy.py` for the feature inventory. **Status labels** — short forms of the top STATUS LEGEND: `LIVE` = `BUILT-AND-LIVE` (on in a fresh `docker compose` deploy) · `OFF(flag)` = `BUILT-BUT-OFF` · `IN-FLIGHT` · `PLANNED(phase/G-id)` = `PLANNED` (roadmap-only) · `PARKED` · `DEAD` = `DEAD-CODE` (in tree, no live caller). **Code is ground truth; a flag comment that says "Default OFF" above `= True` is stale prose, not stale code.**

### 6a. Config / feature-flag reality — code default vs. compose vs. override

**Three layers decide a flag's live value, in this precedence (highest wins): shell/`.env` env var → `docker-compose.override.yml` (gitignored, dev-host-only) → `docker-compose.yml` (tracked) → `config.py` Python default.** A fresh clone has **no** `override.yml`, so a fresh deploy runs the `docker-compose.yml` column. `config.py`'s `Settings` is `@lru_cache`'d (`config.py:384-386`) — **an env change needs a CP process restart** unless the field is also in `settings_store.MANAGED` (23 of 67 fields; `settings_store.py:52-87`).

**Two independent reader mechanisms exist and must not be confused:**
- **Pydantic `Settings` fields** (~67, all in `config.py`) — read via `get_settings()`. An empty-string env value **fails** pydantic bool/int parse and crashes CP boot, which is why compose gives every bool/int field an explicit default (`config.py` comment at `docker-compose.yml:175-176`).
- **`os.environ`-read engine knobs** (~30 `SCANNER_ENGINE_*`/`SCANNER_FLOOR_*`/`SCANNER_LEDGER_*`) — **not** `Settings` fields; read directly inside `fleet.py`/`father.py`/`exploit_floor.py`. Empty = reader falls back to its own in-code default, so compose forwards these as `${VAR:-}` (empty-safe) and `worker.py` only passes the non-empty ones through to the spawned agent (the recurring "RUN-2 gap": a new agent-side knob that never gets added to `worker.py`'s allowlist silently never reaches the container).

#### Key-knob truth-table (code default ≠ live value, or behavior-flipping)

| Field / knob | `config.py` default | `docker-compose.yml` | `override.yml` (dev host, gitignored) | Live effect (fresh deploy) |
|---|---|---|---|---|
| `scanner_engine_v2` | `True` (`:258`) | `true` (`:162`) | true | **Engine-v2 is THE live path.** planner/reprompt short-circuited before their flags are read (see §2). |
| `scanner_orchestrator` | `"planner"` (`:138`, contradicts its own comment) | `${:-reprompt}` (`:121`) | reprompt | Moot under engine-v2; **footgun for bare `uv run`/tests** → silently gets untested planner path. |
| `scanner_engine_batch_dispatch` | `False` (`:308`) | **`true`** (`:189`) | true | Real deploys run the batch-pool dispatch (`_run_batch_pool`, endpoint-scoped batches, work-steal requeue), **not** the legacy `run_all` path Father's comments call "default." |
| `scanner_engine_seat_models` | `False` (`:297`, comment says "Deferred") | **`true`** (`:201`) | true | Seat→model binding **is live** in deploy despite the "default-off/deferred" comment — stale prose. |
| `scanner_inventory_ingest_v2` | `True` (`:215` "Default ON (B0)") | **`false`** (`:122`) | false | Finalize re-ingest + legacy paths run the **pre-v2** inventory producer in every real deploy; engine-v2 live ingest hardcodes `True` independently (unaffected). |
| `scanner_api_discovery_enabled` | `True` (`:271` "Default ON") | **`true`** (`:145`, 2026-09-26 47a051e) | true | WS6 `api_operation` discovery/classification **LIVE** in every compose deploy; #23 surfaces shadow/zombie/debug ops as `exposure.shadow_api`. |
| `scanner_finalize_leftover` | `True` (`:316` "Default ON 2026-09-17") | **`false`** (`:153`) | (unset → false) | Trailing re-verify/enrich completeness gate **never runs** in a real deploy. |
| `scanner_evidence_gate` | `False` (`:182`) | `false` (`:123`) | false | **OFF everywhere.** The "proof, not opinion" keystone is unenforced (also fails-open when on — G01/#6). |
| `scanner_ledger_machine_close` | `False` (`:190`) | `false` (`:132`) | false | Cells can flip `tested_clean` on a self-graded claim w/o a real tool hitting the endpoint. |
| `scanner_exploit_floor_enabled` | `True` (`:197` "Default ON 2026-09-17") | `true` (`:131`) | true | Deterministic weapon sweep **LIVE** beside the LLM fleet every wave. |
| `scanner_browser_enabled` | `True` (`:222` "on 2026-09-17") | `true` (`:124`) | true | Playwright crawl sidecar **LIVE** (was default-off pre-2026-09-17; APPLICATION_CONTEXT §7 row is stale here). |
| `scanner_browser_instrument_enabled` | `True` (`:229`, comment says "Default OFF") | (unset → code `True`) | (unset) | DOM-XSS `/instrument` active when browser on AND (flag OR thorough mode) — `browser_instrument_on()` `:231-236`. |
| `scanner_zap_enabled` | `False` (`:345`) | `false` (`:128`) | **true** | ZAP 2nd-DAST sidecar differs fresh-clone (off) vs dev host (on). |
| `scanner_deser_rce_confirm_enabled` | `False` (`:206`) | `false` (`:237`) | false | phpggc/ysoserial gadget beacons OFF; only DNS-only URLDNS fires. Sends a real gadget → keep OFF unless engagement authorizes. |
| `scanner_finalize_enrich` | `True` (`:282`) | `true` (`:212`) | true | Finalize enrichment + LLM soft-dedup + narrative **LIVE** (soft-suppress only, never deletes). |
| `scanner_engine_live_convergence` | `True` (`:290`) | `true` (`:186`) | true | verify+enrich+report run on the reconcile tick alongside the fleet wave, not gated at finalize. |
| `scanner_report_v2` | `True` (`:330`) | (unset → code `True`) | (unset) | Rich grounded VAPT report LIVE; degrades to deterministic pack absent a verifier model. |
| `scanner_oob_autolink` | `True` (`:172`) | `true` (`:211`) | true | Deterministic OOB per-payload correlation LIVE (scoped dual-gate). |
| `scanner_scope_enforce` | `True` (`:252`) | `true` (`:140`) | true | Confident out-of-scope URL hard-blocked; bareword hostname advisory (minimal-friction). |
| `scanner_engine_fanout` | `6` (`:266`) | `6` (`:177`) | (varies) | 6 phase-group workers/target (recon/injection/access/client-side/config/logic). |
| **attempt cap** `SCANNER_LEDGER_ATTEMPT_CAP` | 3 (os.env, ledger) | `3` (`:182`) | **2** | Cell claimed N× w/o closing → terminal `attempted`. |
| **lease** `SCANNER_LEDGER_LEASE_S` | 6000 | `6000` (`:195`) | **3000** | Claimed-cell lease TTL. |
| **worker wall** `SCANNER_ENGINE_WORKER_WALL_S` | 5400 (code, `fleet.py`) | unset→5400 | **2400** | Only remaining per-worker hang-guard (batch/stuck backstops off). |
| **max waves** `SCANNER_ENGINE_MAX_WAVES` | 3 (code) | unset→3 | **150** | Father wave-loop ceiling. |
| **stuck window** `SCANNER_ENGINE_STUCK_WINDOW_S` | 0 (code, disabled `36fece4`) | `300` (`:193`) | **0** | Manager preempts a worker on no-progress; 0 = off. |
| **batch budget** `SCANNER_ENGINE_BATCH_BUDGET_S` | 0 | `0` (`:192`) | 0 | 0 = no flat time guillotine (progress-driven preempt only). |
| **pool cap** `SCANNER_ENGINE_POOL_HARD_CAP` | 8 (code) | `8` (`:196`) | **6** | Max concurrent pooled workers. |
| **runaway wall** `SCANNER_ENGINE_RUNAWAY_WALL_S` | 21600/6h | `21600` (`:185`) | **3600/1h** | Absolute scan kill wall. |
| **batch max cells** `SCANNER_ENGINE_BATCH_MAX_CELLS` | 2 | `2` (`:194`) | 6 (in-flight bumped code path to 6) | Cells per batch (in-flight coverage-fold bumped `father._batch_max_cells` 2→6). |
| `scanner_default_cost_cap` | `0.0`=**unlimited** (`:159`) | (unset) | (unset) | Caps opt-in; a scan runs to coverage completion unless a positive cap is set. |
| `scanner_nonanthropic_default_time_cap_s` | `0`=unlimited (`:335`) | `0` (`:213`) | 0 | Non-Anthropic (no cost telemetry) run is truly uncapped unless >0. |
| `SCANNER_ENGINE_FORCE_TOOL_CHOICE` | 1 (code) | `1` (`:206`) | 1 | 0 → fall back to `tool_choice="auto"` for aliases (e.g. `claude-fable-5.1`) that 400 on `"required"`. |

**Boot-time credential/log footguns (verified in `config.py`):** `master_encryption_key: str = ""` (`:43`) is **never validated/warned** (unlike `admin_api_key`); `encrypt_secret()` (`:425-428`) silently passes gray-box creds through as **plaintext** when empty, and `docker-compose.yml:109` declares it optional `${VAR:-}` (vs mandatory `${VAR:?}` for `POSTGRES_PASSWORD`/`REDIS_PASSWORD`). `_ensure_admin_api_key()` (`:370-381`) logs a freshly-generated admin key in **full plaintext** on every boot when `ADMIN_API_KEY` unset. `scanner_environment` (`:98`) and `log_level` (`:99`) are **dead** — set by compose (`:103-104`), read nowhere in `src/` (log level not actually configurable).

#### Full field-group inventory (~67 `Settings` fields + ~30 os.env knobs)

| Group | Fields (`config.py` line) | Notes |
|---|---|---|
| Core infra | `database_url`, `redis_url`, `anthropic_api_key`, `anthropic_base_url` (`:42`), `master_encryption_key` (`:43`), `license_token` (`:48`), `scanner_data_root` (`:49`), `scanner_shared_volume_name` (`:55`), `scanner_service_network` (`:97`), `scanner_node_id` (`:103`) | `anthropic_base_url` → Anthropic-format proxy for cheap/non-Anthropic models. Shared volume name **must** equal compose `volumes:` name or /work writes are lost. |
| Container sizing | `scanner_agent_mem_limit`="3g" (`:61`), `scanner_container_autosize`=True (`:71`), `scanner_host_mem_headroom_frac`=0.15, `_base_reserve_mb`=1024, `scanner_mem_reservation_frac`=0.5, `scanner_host_cpu_headroom_frac`=0.15, `_base_reserve`=1.0 (`:72-81`) | Host-RAM/CPU-aware auto-sizing of per-scan sidecars. **Known issue:** budgets ignore concurrent scans (up to 7) — joint over-commit (`worker.py:187-245`). |
| Concurrency | `scanner_max_thorough`=0, `scanner_max_fast`=0 (`:92-93`) | 0 = fixed BRD default (3 thorough / 4 fast = 7 total, **per-process**). Deliberately not auto-detected (operator capacity policy). |
| Scheduling | `scanner_enable_poller`=False (`:106`), `scanner_scheduler_enabled`=False (`:112`), `scanner_schedule_min_interval_s`=21600/6h (`:116`) | Poller opt-in (compose forces `true`); cron scheduling opt-in; 6h RoE min-interval floor. |
| Gates | `scanner_preflight_gate`=True (`:122`), `scanner_egress_preflight`="required" (`:128`), `scanner_max_stop_blocks`=6 (`:133`) | Preflight readiness (Docker/images/DB/Redis/key); egress required vs advisory; Stop-hook graceful-partial ceiling. |
| Orchestration | `scanner_orchestrator`="planner" (`:138`), `scanner_planner_max_rounds`=8, `scanner_approval_timeout_s`=900, `scanner_chain_synthesis`=True (`:144`), `scanner_exploitation_enabled`=False (`:148`) | See truth-table. `scanner_exploitation_enabled` off = verification-only until operator opts in. |
| Models | `scanner_model_orchestrator`="claude-sonnet-4-6" (`:151`), `_subagent`/`_verification`/`_summarizer`="claude-haiku-4-5" (`:152-154`) | Sonnet completes kill chain; Haiku shortcuts phases w/o running tools. |
| Cost | `scanner_default_cost_cap`=0.0 (`:159`) | 0.0/None = unlimited (opt-in caps). |
| OOB | `scanner_oob_server`="https://oast.fun" (`:163`), `scanner_oob_token` (`:168`), `scanner_oob_autolink`=True (`:172`) | Verify live override (self-hosted oast.abhedi.co.in per memory) — code default is still public oast.fun. |
| Honesty gates | `scanner_evidence_gate`=False (`:182`), `scanner_ledger_machine_close`=False (`:190`), `scanner_exploit_floor_enabled`=True (`:197`), `scanner_deser_rce_confirm_enabled`=False (`:206`), `scanner_finalize_retire_unreached`=True (`:322`) | Retire-unreached: never-probed applicable cells → terminal `attempted` at finalize so `count_open_cells` can reach 0. |
| Detection/ingest | `scanner_inventory_ingest_v2`=True (`:215`), `scanner_browser_enabled`=True (`:222`), `scanner_browser_instrument_enabled`=True (`:229`), `scanner_api_discovery_enabled`=True (`:271`) | See truth-table (ingest_v2 still OFF in deploy despite code True; api_discovery now ON in deploy 2026-09-26 47a051e). |
| Safety | `scanner_scope_enforce`=True (`:252`); + os.env `SCANNER_ALLOW_PRIVATE_TARGETS`, `SCANNER_TOOLSERVER_ALLOW_SENSITIVE_READ`, `SCANNER_ENGINE_ALLOW_VALUE_READ` | RFC1918 targets, sensitive-read deny drop, gated value-read — all default-safe/off. |
| Engine-v2 tuning | `scanner_engine_v2`=True (`:258`), `_fanout`=6 (`:266`), `_sync_interval_s`=120 (`:273`), `_live_convergence`=True (`:290`), `_seat_models`=False (`:297`), `_batch_dispatch`=False (`:308`) | + ~25 os.env knobs (`SCANNER_ENGINE_*`): worker_wall, max_waves, escalate(+max_rounds), auth_bootstrap, verify(+wall), http_timeout, effort, recon_floor, recon_expansion_rounds, runaway_wall, verify_tick_concurrency, report_min_interval_s, batch_budget_s, stuck_window_s, batch_max_cells, pool_hard_cap, digest, zap_signals, tick_oob, expansion_budget, guard_log, max_report_regens, force_tool_choice, chain_max_depth, engine_models, chain_floor, recon_depth, sync_interval. |
| Ledger/floor os.env | `SCANNER_LEDGER_ATTEMPT_CAP`=3, `_STOP_ON_PROBE`=1, `_LEASE_S`=6000; `SCANNER_FLOOR_*` (drain/budget_s/injection_budget_s/claim_limit/max_targets), `SCANNER_NOFAMILY_SWEEP`, `SCANNER_RATELIMIT_N`/`_MAX_ENDPOINTS`, `SCANNER_STREAM_FINDINGS`, `SCANNER_SOFT_CAP_MARGIN_S`, `SCANNER_FINALIZE_GRACE_S` | Empty-safe in compose (code fallback). Finalize-grace + soft-cap-margin = graceful-drain window (CP-read). |
| Finalize/report | `scanner_finalize_enrich`=True (`:282`), `scanner_finalize_leftover`=True (`:316`), `scanner_report_v2`=True (`:330`), `scanner_nonanthropic_default_time_cap_s`=0 (`:335`) | See truth-table. |
| ZAP | `scanner_zap_enabled`=False (`:345`), `scanner_zap_min_risk`=2 (`:348`), `scanner_zap_mode`="baseline" (`:351`) | 2nd passive DAST corroboration sidecar. |
| Retest | `scanner_retest_enabled`=False (`:359`) | `POST /findings/{id}/retest` 403s when off. |
| Admin | `admin_username`="admin" (`:366`), `admin_password`="" (`:367`, empty = pw login disabled), `admin_api_key`="" (`:368`, empty = auto-gen + log on boot) | `settings_store.MANAGED` (23 fields) is the only admin-console-editable surface (`applies="scan"` vs `"restart"`). |

---

### 6b. Master feature inventory (every capability, by status)

Columns: **Feature** | **Status** | **Where** (file/dir or roadmap ref) | **Proving oracle** (detection features only) | **Flag**.

#### BUILT-AND-LIVE (default-on in a fresh deploy)

| Feature | Status | Where | Proving oracle | Flag |
|---|---|---|---|---|
| Engine-v2 wave-loop orchestrator (Father) | LIVE | `engine/father.py` (1859 ln) | — | `scanner_engine_v2`=on |
| Batch-pool dispatch (endpoint-scoped, work-steal requeue) | LIVE | `father._run_batch_pool`, `fleet.run_pool` | — | `SCANNER_ENGINE_BATCH_DISPATCH`=true (compose) |
| Pluggable fleet runtimes (Claude SDK / OpenAI-compat driver) | LIVE | `engine/fleet.py`, `runtimes/claude_sdk.py`, `runtimes/agents_runtime.py` | — | — |
| Seat→model resolution (strong/cheap per role) | LIVE | `resolver.py`, father pick sites | — | `SCANNER_ENGINE_SEAT_MODELS`=true (compose) |
| Coverage ledger work-queue (materialize/claim/lease/release/complete) | LIVE | `ledger/service.py`, `ledger/applicability.py` | SKIP-LOCKED claim; `scan_is_complete` (open==0 or ≥0.98) | — |
| Attempt cap → terminal `attempted` | LIVE | `ledger/service.py`; `SCANNER_LEDGER_ATTEMPT_CAP`=3 | — | env |
| Deterministic exploit floor (weapon sweep beside every wave) | LIVE | `engine/exploit_floor.py` (3522 ln) | per-family deterministic oracles (below) | `scanner_exploit_floor_enabled`=on |
| SQLi oracle (sqlmap + boolean-diff + time-blind) | LIVE | `exploit_floor.parse_boolean_diff:1389`, `:1362` | boolean/time differential | exploit floor |
| Reflected/stored XSS oracle (canary 2-request) | LIVE | `exploit_floor.parse_xss_reflection:504`, `:561/:568/:599` | canary reflection | exploit floor |
| SSTI oracle | LIVE | `exploit_floor.parse_ssti:1287` | arithmetic-eval canary | exploit floor |
| Blind CMDi/XXE/SSRF/LFI/deser via OOB | LIVE | `exploit_floor.py:348-476` + `oob/registry.py` | OOB callback correlation | `scanner_oob_autolink`=on |
| Open-redirect oracle | LIVE | `exploit_floor.py:1446` | redirect Location match | exploit floor |
| CORS misconfig oracle | LIVE | `exploit_floor.py:1158` | reflected-origin ACAO | exploit floor |
| Cross-identity authz diff (BOLA/BFLA/IDOR/unauth) | LIVE | `exploit_floor.diff_access:951` (`:978/:990/:1002/:1014`) over anon/user_a/user_b/user_admin (`auth_bootstrap.py:65-102`) | cross-identity response-diff (body-match today) | exploit floor |
| OpenAPI function-level authz (spec-diff) | LIVE | `exploit_floor._sweep_spec_diff:3129` | spec-vs-behavior diff | exploit floor |
| Weak-session Set-Cookie flags check | LIVE | `exploit_floor.py:1100-1123` | cookie-attribute inspection | exploit floor |
| URLDNS Java deser DNS beacon (always-on) | LIVE | exploit floor | OOB DNS callback | exploit floor |
| SSRF→metadata impact split (IMDS creds=CRIT / reach=HIGH) | LIVE | `chain/floor.py:174` `_hop_metadata`, `_IMDS_CRED_RX:66`/`_IMDS_REACH_RX:72` | live-cred body vs reach-only | — |
| Chain floor (single-hop capability follow-ups, e.g. metadata→IMDS, file-read) | LIVE (engine-v2 only) | `chain/floor.py:run_chain_floor`, `_hop_file_read` | deterministic follow-up probe | — |
| Chain graph + ranked synthesis (shared by both stacks) | LIVE | `chain/capabilities.py`, `chain/service.py` | — | `scanner_chain_synthesis`=on |
| Deterministic recon floor (subfinder→httpx+arjun→katana + 5 depth stages) | LIVE | `engine/recon_floor.py`, `context.py` | — | `SCANNER_RECON_DEPTH` |
| Auth bootstrap (httpx login → LLM self-register fallback) | LIVE | `engine/auth_bootstrap.py` | — | `SCANNER_ENGINE_AUTH_BOOTSTRAP` |
| Scan-brief per-wave common-knowledge | LIVE | `engine/scan_brief.py` | — | — |
| OpenAPI/GraphQL-introspection/JS-bundle spec ingest | LIVE | `api_normalizer.py:318-419`, `recon_floor.py:410-442` | — | — |
| JS-secret extraction (writer) | LIVE (partial) | `recon_floor.py` JS-secret writer | regex secret hit | — |
| Playwright browser crawl sidecar (scope-bound BFS) | LIVE | `docker/browser/browser_server.py` `/crawl` | — | `scanner_browser_enabled`=on |
| DOM-XSS real-execution proof (`/instrument`) | LIVE (thorough or flag) | `browser_server.py` `INSTRUMENT_SOURCES:67`, `build_instrument_init_script:313`, `executed:true` `:361` | hooked-sink `executed:true` | `browser_instrument_on()` |
| OOB honest classification (protocol-over-label) + sink-cluster + cap | LIVE | `oob/service.py:sync_oob`, `oob/registry.py`; cap `SCANNER_OOB_MAX_FINDINGS`=12 | wire-protocol classify | `scanner_oob_autolink`=on |
| Mid-run reconcile (flush /work→DB during wave) | LIVE | `father._periodic_sync`; `scanner_engine_sync_interval_s`=120 | — | — |
| Live convergence (verify+enrich+report on reconcile tick) | LIVE | engine tick | — | `scanner_engine_live_convergence`=on |
| Finalize enrichment + LLM soft-dedup + narrative (soft-suppress only) | LIVE | `finalize.py`, `finalize_enrich.py` | — | `scanner_finalize_enrich`=on |
| Finalize retire-unreached → `attempted` | LIVE | `finalize.py` | — | `scanner_finalize_retire_unreached`=on |
| A1 independent verifier (re-reproduce self-declared H/C, demote unconfirmed) | LIVE (non-Anthropic roster only) | `agent_runtime/finalize.py:finalize_scan`, `:423`; `verify.py` | `VERDICT:REPRODUCED` sentinel | — |
| Proof capsule (6-key redacted {class,method,req,resp,evidence,verdict}) | LIVE (verifier path only) | `hooks/verification.py:154 _build_capsule`, `finalize.py:733-741`, `reporting/service.py:210/230` | fired-oracle/reproduced verdict | — |
| Rich grounded VAPT report (HTML→PDF, effort stats, narrative) | LIVE | `reporting/html_report.py`, `service.py` | — | `scanner_report_v2`=on |
| CVSS live-recompute + OWASP/ATT&CK/D3FEND stamping | LIVE | `reporting/service.py:192`, `taxonomy.FRAMEWORK_MAP` (56 classes) | — | — |
| Cross-scan regression diff | LIVE | `reporting/regression.py:160` (`GET /scans/{id}/diff`) | — | — |
| Retest-to-close (deterministic re-fire) | BUILT-BUT-OFF | `api/retest.py:105` | captured-proof re-fire | `scanner_retest_enabled`=off |
| Guardrail `guard_tool_call` (crime-line + platform-block + scope + fetch-allowlist) | LIVE | `engine/guardrails.py`, `hooks/scope.py`, `hooks/safety.py`, `exploitation/contract.classify` | — | `scanner_scope_enforce`=on |
| Two-tier minimal-friction scope (confident-block / bareword-advisory) | LIVE | `hooks/scope.py` (457 ln) | — | `scanner_scope_enforce` |
| Non-overridable platform/metadata blocklist | LIVE | `hooks/scope.py:269-307` | — | — (always on) |
| Telemetry (phases/worker_runs/agent_messages/scan_events + WS feed) | LIVE | `engine/telemetry.py:WorkerRecorder` | — | — |
| Preflight readiness + egress gate | LIVE | `scheduler/preflight.py`, `egress.py` | — | `scanner_preflight_gate`=on |
| Poller salvage funnel (`_finalize`, all exit paths incl. GC dead-node) | LIVE | `scheduler/poller.py` | — | — |
| Governor progress-based stop (plateau / unresolved==0) | LIVE | `engine/governor.py`, `resolver._max_workers_cap` | — | numeric caps opt-in |
| Container auto-sizing (host RAM/CPU-aware) | LIVE | `scheduler/worker.py:187-245` | — | `scanner_container_autosize`=on |
| Multi-model driver (any OpenAI-compatible `api_base` via proxy) | LIVE | roster/model `api_base` (BRD deviation #9, zero new code) | — | `SCANNER_ENGINE_MODELS`/`OPENROUTER_API_KEY` |
| Per-scan KALI_EXEC_TOKEN / BROWSER_TOKEN isolation | LIVE | `worker.py`, `docker/toolserver/exec_server.py` | — | — |
| Playbook system-prompt seeding (2 builtins hardcoded verbatim; all other YAMLs raw-passthrough, **no boot LLM-compile**) | LIVE | `playbooks/orchestrator.BUILTIN_PLAYBOOK_PROMPTS`, `seeder.py:88-110` (`enrich_playbook` reachable only via admin `POST /playbooks`) | — | — |

#### IN-FLIGHT — the 4 `feat/alpha-observability` workstreams (NOT yet on main `fixes/critical-improvements`, NOT deployed)

Per the tracker S1: 4 cohesive, tested workstreams, no overlap with the Phase-0 bugs. **Status update vs. tracker (2026-09-26):** all 4 are now committed on `feat/alpha-observability` (`0d3be20`, `d70925a`, `a21890d`, `1b2653c` + test `2939017`); migrations 0018/0019 and `engine_presets.py` are tracked. Not yet merged to main or deployed.

| Feature | Status | Where | Proving oracle | Flag |
|---|---|---|---|---|
| **WS1 — OOB false-positive fix** (classify-by-protocol + sink-cluster + cap; findings dedup/junk hardening; 2 OOB skills) | IN-FLIGHT (committed on branch `0d3be20`, un-deployed) | `oob/service.py`, `tools/findings.py`, `skills/oob-callbacks`, `skills/pentest-finding-writer` (tests: `test_oob_finding_minting.py`+129, `test_quality_gaps_op.py`+37) | wire-protocol OOB classify | — |
| **WS2 — Coverage-grid fold** (ULID/prefixed-id + param/api fold, access-control control-sample, host cap 40→500, `_batch_max_cells` 2→6) | IN-FLIGHT (committed on branch `d70925a`, un-deployed) | `ledger/service.py`, `father.py` (tests: `test_father_p5p6.py`+70) | — | — |
| **WS3 — Scan-instructions + per-scan engine-model routing** | IN-FLIGHT (fully committed `a21890d`, un-deployed; migrations 0018/0019 + `engine_presets.py` + `test_engine_presets.py` all tracked) | `src/scanner/engine_presets.py` (new), `alembic/versions/0018_add_scan_instructions.py`, `0019_add_scan_engine_models.py`, `api/schemas.py`, `api/routes/scans.py`, `db/models/tenant.py`, `engine/scan_brief.py`, `worker.py`, `poller.py`, `main.py`, `playbooks/seeder.py` (drops boot LLM-compile → raw YAML), frontend `new-scan-drawer.tsx` | — | per-scan operator input + preset |
| **WS4 — Poller robustness** (dead-node reap→terminal for killing/cancelling/closing; orphan-GC zap/browser) | IN-FLIGHT (committed on branch `1b2653c` + test `2939017`, un-deployed) | `scheduler/poller.py`, `tests/unit/test_poller.py`+61 | — | — |

**Deploy blockers (tracker R1):** migrations 0018/0019 are committed (`a21890d`) but not yet applied to any live DB → `alembic upgrade head` required at deploy or scans INSERT/SELECT fail. **R3:** `gpt5.6`/`explabs` preset silently falls back to `OPENROUTER_API_KEY` if `EXPLABS_API_KEY` unset. **R4:** non-builtin playbooks now seed raw-YAML (intended). Recommendation: commit as ~4 logical commits + apply migrations, then build Phase 0 on top.

#### PLANNED — merged Phase 0-5 program (roadmap #1-#30 + gap G-ids)

| Feature | Status | Where (roadmap ref) | Proving oracle | Flag/notes |
|---|---|---|---|---|
| **B1** stable claim/release worker_id (work-steal requeue) | PLANNED Phase 0 (bug, still-broken, LIVE on batch path) | `father.py:1807→:1174→service.py:1286` (claim `wave{N}`) vs `:1254/:1328/:1333→:1345` (release `batch{w}-{id}-{model}`) → 0 rows freed | — | 2→6 batch bump amplifies it |
| **B2** wall AND-gate | PLANNED Phase 0 (already-correct; ≡ fix B3) | `father.py:1784` | — | — |
| **B3/G08** fail-CLOSED quiescence/target-health + log | PLANNED Phase 0 (partial) | `father._has_claimable:1405-1406`, `attack_surface.count_claimable:163-164` (no logger import), `target_health():188-207` | — | `_unresolved` already logs (`36fece4`) |
| **B4** reopen resets attempts=0 | PLANNED Phase 0 (still-broken) | `ledger/service.py:1022`, `reopen_cells_for_classes` (3 callers) | — | one-liner |
| **B5** batch prompt parity (`board_totals` in `_task_for`) | PLANNED Phase 0 (still-broken) | `father._task_for:1256` (board computed `:1807`, discarded) | — | same locus as B1 |
| **#6/G01** evidence gate ON + fail-CLOSED + fired-oracle required + pending_oracle/pending_human/flaky states + human queue | PLANNED Phase 0→1 (wired, OFF, latent fail-open) | `ledger/service.py:805/:967/:830/:49`, `_EVIDENCE_FIELDS:136-144` (passes on prose `finding_id`), `config.py:182` | **the keystone** — require a fired deterministic oracle + linked `EvidenceObject` | drop `finding_id`, flip `scanner_evidence_gate` |
| **#19/L** skill-per-cell required-oracle gate | PLANNED Phase 0/1 (missing) | `ledger/service.py`+`coverage_qa.py`(map, observability-only)+`father.py`; `weapon_swept` accepts ANY method | cell counts tested only when its class's oracle fired | anti-fake-coverage keystone |
| **#28** poller-side finalize rollup (`sync_zap`+`rollup_findings_count`) | PLANNED Phase 0 (partial) | `scheduler/poller.py` salvage + engine finalize; move both into `finalize_scan` | — | ZAP alerts lost + telemetry under-count on force-stop |
| **#30/G07** honest counts (`resolved+open==total`, stop single-probe→tested_clean) + detached verify | PLANNED Phase 0/1 (still-broken, live bug) | `reporting/service.py:110/:121-122` + `father._render_board_totals:436` drop `attempted`; `_OPEN_STATES:49` treats it resolved → paths disagree; `finalize.py:915` self-gates verify on live toolserver | invariant `resolved+open==total`; detached re-fire of captured proof | — |
| **G39** scanner self-defense (quarantine tool-output, IPI canary suite, guard catch-rate) | PLANNED Phase 0/1 (**flagship, new**) | `posttool.py:19-20` (output flows to LLM unmodified); no `catch_rate`/`self_poison`/quarantine in `src`/`tests` | harness-integrity oracle: canary-not-emitted + % policy-violations denied | foundational |
| **#5** oracle-first never-fail-open verify | PLANNED Phase 0 | `hooks/verification.py` | oracle before LLM verdict; unavailable→pending | — |
| **#2/#23** turn on API discovery + spec import + shadow/zombie | ✅ DONE 2026-09-26 (47a051e flip + 7d1e504/07ae989 shadow surfacing) | `api_normalizer.py`, `finalize.py` surface_shadow_apis | `exposure.shadow_api` findings (shadow/zombie/debug), verified deterministic | flag now defaults ON |
| **#9/G26/G36** deterministic oracles: JWT (alg-none/confusion/kid), OAuth redirect_uri/PKCE, session-fixation/logout, token/refresh-replay, IdP-confusion, file-upload, CRLF, request-smuggling | PLANNED Phase 1 (classes exist, no oracle) | `exploit_floor.py`+`oob/`; `WEAK_SESSION` cookie-only `:1100`; CRLF/SMUGGLING taxonomy-only (`taxonomy.py:27/:47`) | alg-none→200+data; session-id unchanged across boundary; token after logout; header-split observed; retrievable stored artifact; paired desync | folds into #9 |
| **#10/G32** driven browser: generalize DOM-XSS + proto-pollution/CSP/CORS-bypass/storage oracles, ship on by default | PLANNED Phase 1 | `docker/browser/` | `executed:true` from hooked sink | — |
| **#12/#16/G29** BOPLA property-diff, generic response-diff oracle, GraphQL field-authz + depth/batching | PLANNED Phase 1/3 | `exploit_floor.py`, `api_normalizer.py`; BOPLA→`EXCESSIVE_DATA` (no oracle) | create-as-A/read-as-B property/field diff | — |
| **#20** executed-chain finding writer | PLANNED Phase 1/4 | `chain/floor.py`+`reporting/service.py` (bucket exists, nothing writes) | write only when each hop already proved | — |
| **#15/G33** file-upload oracle + document-parse OOB | PLANNED Phase 1 (no builder) | `exploit_floor.py` (no multipart/`-F`); XXE-doc oracle exists `:363` | retrieve+trigger stored artifact / doc-parse OOB | SVG/CSV/polyglot breadth=additional |
| **#22** stack-matched templates + reachability labels | PLANNED Phase 1 | recon+`exploit_floor.py`+reporting | version match = "reachable/needs-confirmation", never "proof" | — |
| **G02** proof capsule on EVERY H/C (unify oob_proof+exploit_floor+HAR into one gated field) | PLANNED Phase 1 (mechanism shipped, opportunistic only) | `hooks/verification.py:208` (verifier-only); oracle-proven skip capsule (`finalize.py:952`) | structural gate: H/C with no capsule cannot ship | — |
| **#1** playbook → engine-v2 (boss-as-planner, policy.md, boss.py, plan_gate.py, plan.json) | PLANNED Phase 2 | `engine/methodology.py`→`run.py`/`father.py` (today one fixed prompt string) | two playbooks → measurably different coverage | — |
| **#3/#4/#8/G25** two-identity authz (own-ref-as-other + planted canary), session keep-alive/re-auth, authed SPA crawl, identity matrix (guest/support/auditor/svc), object×action×role family, tenant-B | PLANNED Phase 3 | `exploit_floor.py`+ledger identities+`auth_bootstrap.py:71-76` (4 slots)+`docker/browser/` | create-as-A/read-as-B planted-canary; forge-JWT→protected 200 | — |
| **#11/G30** GraphQL op-authz + WS/SSE/webhook channel-auth + signature-bypass/replay | PLANNED Phase 3 (WS/SSE new) | `applicability.py:182-183` (cell shell), no builder in `exploit_floor` | cross-user message on unauthorized channel; replayed webhook sig | gated on surface detection |
| **SSO/OAuth login + multi-tenant isolation** | PLANNED Phase 3 (segment-fork, P0 if SaaS) | `docker/browser/`; tenant-B "only a scan_brief comment" | tenant A cannot read tenant B (planted object) | — |
| **AI red-team floor** (G09 detection gate + G10/G11/G13/G16 direct-PI/secret-extract/agentic-MCP-abuse; G12/G14/G17 indirect/RAG/output-sink) | PLANNED Phase 3 segment-fork(c), **off by default, detection-gated** | `taxonomy.py` has ZERO AI classes (`:17-86` ends at `RATE_LIMIT`); `applicability.py` no AI family; reserve taxonomy slot + build §1.1 probe now | forced canary token verbatim in output; planted secret exact-match; unauthorized tool-call in log; canary at OOB/DOM sink | **mandatory safety rider** G24/G38 (self-hosted OOB only, sandbox sinks, human approval) |
| **#7** intercepting/replay proxy sidecar | PLANNED Phase 0/P0 build | new `docker/proxy/` mirroring toolserver `/exec` | replay modified in-scope request → ingest as evidence | — |
| **#14/#13/G27** recorded multi-step sequences, 2nd-order/deferred confirm, business-logic state/count/balance-diff | PLANNED Phase 3/4 (signal-only today) | `exploit_floor.py:189-199/:642/:650` docstrings "signal-only, for the LLM" | measured state/count/balance delta before/after abuse | bounded to recorded flows |
| **#17/G34** SSRF→cloud exfil (bucket read/list/write, IMDSv2, serverless invoke) | PLANNED Phase 4 (metadata split done) | extends `chain/floor.py` | bucket LIST/WRITE reached via SSRF chain | standalone cloud-IAM=additional |
| **G28** race/concurrency/idempotency oracle | PLANNED Phase 4 (burst-fire probe exists, signal-only) | `exploit_floor.build_race_cmd:669` | state/count/balance delta after parallel window (flaky→pending state) | sandbox-payment/test-account rails |
| **#25/#26** finish JS-secret + source-map extraction; dangling-DNS/subdomain-takeover | PLANNED Phase 1 recon | `recon_floor.py` | secret w/ location; claimable CNAME/NS/MX | — |
| **#24** HAR/Postman seed import | PLANNED Phase 1 recon | new import path into inventory | — | — |
| **#29** engine-v2 checkpoints/resume | PLANNED Phase 5 | engine context/run + `RESUME_PROMPT` | restarted scan continues (not salvage) | root of "never restart scanner-cp mid-scan" |
| **#18** session-class checks (fixation/logout/no-rotation) | PLANNED Phase 1 | new session-test module | probe+oracle each | — |
| Benchmark track (XBEN/XBOW-104 FLAG scorer, VAmPI, baseline) | PLANNED parallel (gates post-Phase-0) | `benchmark/run.py`, `metrics.py`, 7 targets `ground_truth.yaml` (harness built = G05) | eval-oracle (not scan-oracle) | — |

#### PARKED (explicitly do-NOT-build) / DEAD-CODE / rejected

| Item | Status | Where / reason |
|---|---|---|
| Recursive boss→manager→sub hierarchy, generation-counter+freeze, agent-to-agent messaging | PARKED | tracker Parked list; deterministic core preferred (G49) |
| Proxy container as coordination substrate | PARKED | (proxy sidecar #7 for request-replay is a different, PLANNED thing) |
| pgvector `MemoryStore` semantic recall | DEAD → delete | `engine/context_memory.py:17` — zero callers outside its test |
| `gateway.py` | DEAD | built every scan, never called (`# noqa: F841`, 100% scaffolding) |
| `pipeline/summarizer.py` + `pipeline/parsers/` | DEAD | 2nd unwired tool-output persistence; `summarize_with_haiku` = `TODO(phase-3)` stub |
| legacy `planner/*` (coordinator/specialist/escalation) + `approval/*` human-gate | DEAD-by-default | unreachable under `SCANNER_ENGINE_V2=true` (§2) |
| legacy `reprompt` (`entrypoint.run_scan`), `hooks/__init__.run_pre_tool_hooks`, `hooks/budget.py`/`gated.py` | DEAD-by-default | legacy-path-only; test-only |
| `attack_surface` legacy `coverage_ledger` API (`claim_cell`/`resolve_cell`/`register_target`) | DEAD ("phantom") | self-labeled; footgun (dead table) |
| `scheduler/resume.py` `should_resume`/`attempt_resume` | DEAD | poller reimplements inline; only `build_resume_prompt` imported |
| `read_scan_brief()` | DEAD (test-only) | `scan_brief.py:267-274`; callers use `write_scan_brief` return |
| `playbooks/loader.py` `Playbook`/`PhaseDef` + `expanders/` | DEAD | built, never wired (no phase-runner loop) |
| repo-root `playbooks/` dir | ORPHANED | `seeder.py` hardcodes `src/scanner/playbooks/definitions/` |
| `scanner_environment`, `log_level` | DEAD fields | `config.py:98-99`, read nowhere in `src/` |
| G03 multi-model verification cohort, G04 oracle-registry wrapper, G22/G23 AI training-poison/explainability, G48 GTM | REJECTED / DO-NOT-BUILD | gap doc Rejected table (model-judgment not oracle / over-engineering / no black-box oracle) |
| WEAK_CIPHER/CERT TLS checks | MISSING (silent) | claimed by hygiene family, no TLS/cert code in `exploit_floor.py` → cells falsely "tested" |

---

### 6c. Glossary (extends APPLICATION_CONTEXT §8 — exhaustive)

**Orchestration & runtime**
- **Father** — the engine-v2 wave-loop orchestrator (`engine/father.py`); builds `WorkerSpec` prompt strings, does not itself run an LLM turn loop.
- **Fleet / FleetManager** — runs per-worker agents (`engine/fleet.py`) via a pluggable backend: `ClaudeSDKRuntime` (Anthropic) or `AgentsRuntime` (OpenAI-compatible driver, everything else).
- **WorkerSpec** — one (target × phase-group) unit of work Father hands the fleet; fan-out width = `scanner_engine_fanout` (6 groups: recon/injection/access/client-side/config/logic).
- **Wave** — one iteration of Father's dispatch loop: materialize surface → sync /work→DB → check completion/quiescence → claim cells → dispatch → chain-floor → escalation.
- **Batch dispatch / `run_pool`** — the compose-default dispatch (`SCANNER_ENGINE_BATCH_DISPATCH=true`): endpoint-scoped small batches through `fleet.run_pool` + a Manager watchdog that preempts a STUCK worker and re-queues its cells (work-stealing). Replaces the legacy `build_specs`+`run_all` fan-out.
- **Work-stealing requeue** — on worker preempt/done, its claimed cells are released back to the pool immediately (B1 is the bug where claim/release worker_ids mismatch so 0 rows free).
- **Quiescence stop** — Father terminates when no claimable cells remain; **fail-open bug** (`_has_claimable` swallows exceptions → transient blip reads as "drained").
- **Plateau stop** — Governor's progress-based stop (no forward progress), the *primary* stop condition; numeric hard-caps (`max_workers`/`max_invocations`/`max_wall_s`) are opt-in default-off backstops.
- **Governor** — `engine/governor.py`; enforces stop conditions and the runaway wall.
- **Registry / Resolver / Gateway** — engine bootstrap: model Registry, seat→model Resolver (`_max_workers_cap` = 2026-09-03 runaway fix), Gateway (**dead**, never called).
- **Seat→model resolution** — bind each worker seat to a model pre-scan (strong→exploit/injection/access/logic/verifier; cheap→recon/scanner/desk); live in deploy (`SCANNER_ENGINE_SEAT_MODELS=true`).
- **Roster** — the per-scan set of admissible models (`SCANNER_ENGINE_MODELS`, or per-scan override col migration 0019).

**Ledger & coverage**
- **Ledger cell** — one row of the coverage work-queue: (surface element × applicable vuln-class); states `untested→testing→{tested_clean|confirmed|blocked|attempted|na}`.
- **Materialize** — cross-product elements × 56 `VulnClass` through `is_applicable` + cartesian trim (host-level dedup, ULID/UUID/numeric-segment fold).
- **Claim / lease** — raw-SQL `SELECT...FOR UPDATE SKIP LOCKED`→`UPDATE...RETURNING`; two callers never get the same cell; priority-weighted by `_CLASS_PRIORITY` (56 entries). Lease = TTL after which an un-closed claim expires back to open (`SCANNER_LEDGER_LEASE_S`).
- **Attempt cap** — a cell claimed N× (`SCANNER_LEDGER_ATTEMPT_CAP`=3) without closing retires to terminal `attempted` (a real, active state).
- **`attempted` state** — attempt-cap-exhausted (or never-genuinely-probed at finalize via retire-unreached); **NOT** counted resolved. Source of the `resolved+open != total` honesty bug (#30/G07).
- **`_OPEN_STATES`** — `ledger/service.py:49`; `{untested,testing}` (treats `attempted` as effectively resolved — disagrees with the report's `_coverage`).
- **Applicability** — `ledger/applicability.py` pure table deciding which classes make sense per element kind (needs-param, sink-gated, auth-surface, host-level).
- **Skill-per-cell** — PLANNED gate (#19): a cell counts `tested` only when its required technique's oracle actually fired.
- **`scan_is_complete`** — `open==0` OR resolved-ratio ≥ 0.98. **`graceful_terminal_status`** — `"completed"` only if complete AND had applicable coverage, else `partial`.

**Exploitation & proof**
- **Exploit floor** — the deterministic (non-LLM) weapon sweep running beside every wave; claims a *disjoint* cell batch (`claim_family_cells`, same SKIP-LOCKED); only unambiguous oracles mint `verified=True`, ambiguous hits → `exploit_floor_signals.jsonl` for LLM triage.
- **Recon floor** — deterministic recon backstop (subfinder/httpx/arjun/katana + 5 gated depth stages) before the exploitation loop.
- **Oracle** — a deterministic check that *proves* a finding (boolean/time diff, canary reflection, cross-identity diff, OOB callback, browser `executed:true`). "LLM proposes, oracle disposes."
- **Signal** — a probe result whose exploitability the LLM must still judge (race, business-logic, mass-assignment); not proof.
- **`diff_access`** — the cross-identity response-diff oracle (BOLA/BFLA/IDOR/unauth) over anon/user_a/user_b/user_admin.
- **Canary** — a unique planted token/object/secret; its verbatim appearance in output/response is the oracle witness (XSS reflection, planted-object BOLA, prompt-injection, RAG).
- **Instrument (DOM-XSS)** — browser sidecar `/instrument` hooks DOM sinks/sources and marks `executed:true` on real sink execution — the literal XBOW "headless browser verifies the payload executed" move.
- **OOB / OAST** — out-of-band interaction (interactsh-style); a callback to attacker-controlled infra confirms a blind vuln.
- **OOB honest classification** — trusting the callback's **wire protocol** over the agent's self-reported label: ldap/ldaps/rmi→`jndi`; any other protocol only proves "server reached attacker infra"=SSRF-class; other claimed labels are downgraded (kills mass "confirmed via OOB" false positives).
- **Sink cluster** — capping OOB findings per sink so one SSRF-prone sink doesn't fan out into dozens of phantom findings (`SCANNER_OOB_MAX_FINDINGS`=12).
- **Chain / capability / hop** — a confirmed finding grants a `Capability` (e.g. `FILE_READ`, `CREDENTIAL`); `chain/capabilities.py` tables map capability→unlocked classes; `chain/floor.py` fires a deterministic single-hop follow-up (a "hop", e.g. metadata-access→IMDS cred theft).
- **Escalation** — reopening ledger cells a newly-granted capability unlocks. Engine-v2: auto-allow. Legacy planner: human-approval-gated (dead by default).
- **Proof capsule** — canonical redacted 6-key {vuln_class, method, request, response_excerpt, evidence_path, verdict} attached to a finding; verdict stamped from an authoritative sentinel, not model self-report. G02 = guarantee one on every H/C.
- **A1 verifier** — the post-scan independent verifier pass that re-reproduces self-declared critical/high findings and demotes unconfirmed ones; the *real* authority on `finding.verified` (an all-Anthropic roster gets none — can't drive the OpenAI-compat verifier SDK).
- **Evidence gate** — flag (`scanner_evidence_gate`) that a ledger cell only flips `confirmed` if the backing finding carries a proof artifact; currently off + fails-open (G01 keystone fix: require a *fired oracle*, add pending_oracle/pending_human/flaky states, never fail open).
- **Machine close** — `scanner_ledger_machine_close`: a cell flips `tested_clean` only if a real tool invocation hit the endpoint (join to `tool_invocations`), not a self-graded claim.

**Lifecycle & safety**
- **Recon / auth-bootstrap / wave-loop / finalize / report / terminal-status** — the 8-step lifecycle (APPLICATION_CONTEXT §4).
- **Finalize** — terminal idempotent post-scan pass: ingest/dedup/chains/report + independent A1 verify.
- **Salvage** — finalize invoked on a crashed/cancelled/GC-recovered scan from whatever `/work` artifacts exist (weaker verify — no live toolserver/kali-exec token).
- **`/work`** — the shared per-scan Docker-volume subpath every container/process reads/writes JSONL to (`findings.jsonl`, `ledger_updates.jsonl`, `exploit_floor_signals.jsonl`); the real cross-process shared memory.
- **Guardrail / `guard_tool_call`** — the fail-closed gate every engine-v2 tool call routes through (sleep-cap, non-overridable platform-block, scope enforcement, crime-line, web-fetch allowlist).
- **Crime-line classifier** — `exploitation/contract.classify()`: forbidden > gated > allow regex; `GATED_PATTERNS` = 3 sqlmap flags only (defense-in-depth, not the real control).
- **Platform / metadata blocklist** — non-overridable pre-scope block of RFC1918/loopback/cloud-metadata/`localhost`/`postgres`/`redis`/`pgbouncer`.
- **Minimal-friction scope** — two-tier design: confident out-of-scope target hard-blocked, bareword hostname advisory-only (a false positive never stalls the agent).
- **Scanner self-defense (G39)** — PLANNED flagship: quarantine target-borne tool output as untrusted data (today `posttool.py` passes it verbatim to the LLM), + IPI canary suite + guard catch-rate metric.

**Config & meta**
- **`config.py` `Settings`** — `@lru_cache`'d process-wide singleton of 67 fields; env change needs CP restart unless in `settings_store.MANAGED`.
- **`settings_store.MANAGED`** — the 23 admin-console-editable fields; `applies="scan"` (next scan, no restart) vs `applies="restart"`.
- **`override.yml`** — `docker-compose.override.yml`, gitignored/dev-host-only; a fresh clone runs the base `docker-compose.yml` column (the "B8 truth-table" fresh-deploy column).
- **G-id (Gxx)** — a master gap id from the code-verified gap analysis (`2026-09-25-core-engine-gap-analysis.md`); CORE gaps admitted only if all three hold: blocks find-and-prove loop + a deterministic oracle can prove it + applies to single-VM web+API.
- **#N (roadmap item)** — a core-scanning-engine-roadmap item (#1-#30) on the live engine-v2 path.
- **Bx (B1-B8)** — orchestration-architecture-v3 Phase-0 bug/deliverable ids (claim/release, wall-gate, fail-closed, reopen-reset, prompt-parity, governor, config-drift).
- **Segment fork** — the operator's target-profile decision (classic web / SSO+multi-tenant SaaS / chat-agent app) that moves SSO, multi-tenant, and the AI floor between P0 and out-of-release.
- **WSTG / OWASP API Top 10 (2023) / OWASP LLM Top 10 (2025) / MITRE ATLAS** — the standards bar the roadmap targets (WSTG ≈ 100 web tests; ATLAS covers the AI/agent surface).
- **`VulnClass` / `FrameworkRefs`** — `taxonomy.py`: 56-member canonical vuln-class enum (SQLI…RATE_LIMIT, **zero AI classes today**) + per-class CWE/OWASP-2021/ATT&CK/D3FEND mapping; `normalize`/`normalize_ngram`/`normalize_cwe` resolve free-text.
- **Moat** — the verification/proof plane (G01/G02); XBOW reached HackerOne #1 with "a deterministic validation approach," and this is the axis the platform is built to win on.

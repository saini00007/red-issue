# WS-5 — Intelligence / Decision Layer (design only)

**Role:** READ-ONLY systems architect. No implementation, no payloads, no exploit steps, no runnable targeting commands.
**Source of truth:** (A) the codebase at `C:\Users\ASUS\Desktop\abhdeii\autocan` (read-only).
**Notation:** `[CODE] file:line` = verified current-code claim (read this session). `[DESIGN]` = proposal. "not found in repo" = searched, absent.
**Hard constraints honored:** D4 (every new capability flag-gated, default-OFF, byte-identical to production when off), D3 (planner/* + `entrypoint.run_scan` verified dead in a default deploy — §0.5), D6 (no recursive agent hierarchies, no agent-to-agent chat, no pgvector semantic memory — §5).

---

# PART 0 — FALSIFY H2 FIRST

> **H2:** "Workers spin up with near-identical STATIC prompts; a dynamic, state-aware decision layer would measurably improve target selection."

## 0.1 Where a worker prompt is actually assembled (the chain)

There are exactly two prompt surfaces per worker: a **system instructions** string and a **task** string. Neither is a hand-written static template.

**System surface** — shared methodology + per-scan OOB block:

```
[CODE] engine/runtimes/agents_runtime.py:785-787   agent = Agent(name="abhedi-red-worker",
                                               instructions=self._instructions(), ...)
[CODE] engine/runtimes/agents_runtime.py:917-920   def _instructions(self): return DEEP_OFFENSIVE_VAPT + self._oob_block()
[CODE] engine/methodology.py:13                    DEEP_OFFENSIVE_VAPT = """You are an elite offensive-security worker ... (static per deploy)
[CODE] engine/runtimes/agents_runtime.py:922-940   _oob_block(): "OOB ORACLE ACTIVE — callback domain: <per-scan>" (varies per scan, static within a scan)
[CODE] engine/runtimes/claude_sdk.py:149           options = build_agent_options(..., system_prompt=DEEP_OFFENSIVE_VAPT, ...)   (Anthropic backend parity)
```

**Task surface** — composed in code per spec, then fed as the conversation seed:

```
[CODE] engine/runtimes/agents_runtime.py:810       convo = spec.task
[CODE] engine/worker.py:11                         task: str  # scoped instruction (e.g. one shard's kill chain)
[CODE] engine/father.py:597-633                    def _task_for(target, focus, group, wave, open_cells, brief, capability_ctx, board_totals, plan_digest)
[CODE] engine/father.py:613-614                    prefix = f"{brief}\n\n{capability_ctx}" ; prefix = f"{prefix}{board_totals}{_plan_prefix(plan_digest)}"
[CODE] engine/father.py:617-621                    body   = "Run an AUTHORIZED deep VAPT against {target}. Your PRIMARY focus is {focus} ..."
[CODE] engine/father.py:622-628                    if wave > 0: body = "DEEPENING PASS #{wave}: ... Do NOT repeat them or re-run recon ..." + body
[CODE] engine/father.py:629-633                    return f"{prefix}{block}{handoff}{triage}{worklist}{body}"
[CODE] engine/father.py:670                        WorkerSpec(task=_task_for(...))                       # build_specs (wave path)
[CODE] engine/father.py:1277-1280                  WorkerSpec(task=_task_for(...))                       # _batch_specs (batch path)
[CODE] engine/father.py:714                        task = f"{_skills_block(kind)}Run an AUTHORIZED deep VAPT ... {_worklist_text(cells)}"  # smoke path
[CODE] engine/father.py:1506 / 1559-1564           auth_bootstrap / authed_recrawl bespoke tasks
```

`build_specs`/`_task_for` is the "worker prompt construction" seam the brief asked for; `engine/batch.py:30-61` (`compose_batches`) only groups cells — its consumer (`father._run_batch_pool`) is itself flag-gated `[CODE] config.py:437 scanner_engine_batch_dispatch: bool = False`.

## 0.2 Are worker prompts near-identical across cells/waves? — **NO for the task surface**

Variation matrix (every row verified this session):

| Dimension | Varies by | Evidence |
|---|---|---|
| Phase-group focus | 6 distinct kill-chain groups (`recon/injection/access/clientside/config/logic`), each a different focus paragraph | `[CODE] father.py:48-85` (PHASE_GROUPS); consumer `[CODE] father.py:661-670` |
| Group method block | Different SKILL.md bodies per group (`REQUIRED METHOD`), char-sliced, `@cache`d | `[CODE] father.py:194-229` (PHASE_SKILLS); `[CODE] father.py:274-293` (`_skills_block`) |
| Group directives | recon-handoff only for exploit groups; S6 signal-triage only for weapon groups | `[CODE] father.py:310-324`; `[CODE] father.py:327-348` |
| Per-cell worklist | THIS wave's atomically claimed cells, partitioned per group; each line carries `endpoint :: vuln_class` + prior attempts/methods blackboard | `[CODE] father.py:351-372` (`_worklist_text`, incl. "prior workers tried: … go DEEPER"); `[CODE] father.py:409-417` (`_worklist_by_group`); claim `[CODE] father.py:1874-1875` |
| Live per-wave context | brief rebuilt each wave from live `/work` (recon, auth session, endpoints, open cells, findings, ruled-out digest) | `[CODE] father.py:1781` (`brief = write_scan_brief(...)`); `[CODE] scan_brief.py:249-292`; builder `[CODE] scan_brief.py:104-184` |
| Live coverage board | `done/in-flight/open` totals + per-family line, fresh per wave | `[CODE] father.py:1194` (`coverage_counts`); renderer `[CODE] father.py:382-406` |
| Wave depth | `DEEPENING PASS #n` preamble + "attack only UNTESTED surface" | `[CODE] father.py:622-628`; wave counter `[CODE] father.py:1859-1865` |
| Capability escalation | "you now HAVE `<cap>`" block naming the granting finding + endpoint, only on escalation waves | `[CODE] father.py:1520-1548`; folded at `[CODE] father.py:1717` |
| Plan digest | boss plan as REQUIRED prefix — present only when a plan exists | `[CODE] father.py:296-307` (`_plan_prefix`, "" when absent); digest `[CODE] plan.py:84-94` |
| Batch path variant | one spec per batch; group/focus derived from the batch's first cell `vuln_class` via the class→group map | `[CODE] father.py:1268-1280`; map import `[CODE] father.py:31` |
| Per-scan (not per-cell) | OOB callback domain, operator `SCAN_INSTRUCTION`, auth snippet, scope block | `[CODE] scan_brief.py:71-101,124-126`; `[CODE] agents_runtime.py:996-1008` |
| **Within a worker (per turn)** | reprompt is stateful: names exactly what's missing + weaponize line + live progress digest (confirmed findings, tested cells, tools fired) | `[CODE] agents_runtime.py:962-994` (`_reprompt`); digest `[CODE] agents_runtime.py:1010-1021`; loop `[CODE] agents_runtime.py:808-838` |

**Static residue (what H2 gets right):** the shared system methodology (`DEEP_OFFENSIVE_VAPT`, `[CODE] methodology.py:13`) and the skill bodies are constant across cells *and* waves; they only change when the catalog/model changes. Also note per-**vuln-class** templates do **not** exist: templating granularity is per-**phase-group** (class→group map `[CODE] father.py:31`, groups `[CODE] father.py:48-85`), with per-cell content limited to the worklist lines.

## 0.3 Does any existing component do state-aware decision making per tick?

**a) The LLM re-plan exists, and it is a per-wave-tick state-aware planner — code-default OFF:**

```
[CODE] config.py:415-417     scanner_engine_boss: bool = False   # "Default OFF => no plan at scan start => today's deterministic behavior byte-for-byte"
[CODE] father.py:1787        await self._boss_tick(brief)        # called unconditionally each wave iteration
[CODE] father.py:1156-1157   if self._boss_fn is None or not getattr(get_settings(), "scanner_engine_boss", False): return
[CODE] run.py:250-261        _boss_execute = build_boss_execute_fn(...) if lc_model else None ; _boss_fn -> propose_plan(...)
[CODE] boss.py:149-175       propose_plan() -> None on SDK/key/absent/timeout/malformed; NEVER raises
```

Inputs are genuinely state-aware: policy + brief + coverage board + coverage QA + prior plan `[CODE] boss.py:108-130`; read-only tools only `[CODE] boss.py:76`.
**Deploy nuance (must not be glossed):** the checked-in, auto-loaded `docker-compose.override.yml` ("enable-everything overlay", "literally everything ON smoke test") sets `SCANNER_ENGINE_BOSS: "true"` and `SCANNER_ENGINE_PLAYBOOK: "true"` `[CODE] docker-compose.override.yml:70-71`, while base compose defaults remain `SCANNER_ENGINE_V2: true` / playbook `false` / `SCANNER_ORCHESTRATOR: reprompt` `[CODE] docker-compose.yml:121,168,172`. So the boss is **default-OFF at the code/settings layer** (`config.py:417`; spawn forwarding `[CODE] scheduler/worker.py:796-798`), but **flipped ON in the checked-in dev overlay**. Whether the measured scans (peer evidence) ran with the overlay is *not determinable from the repo* — no `plan.revised` telemetry or plan.json artifacts found in repo `logs/`.

**b) What `plan_gate.py` gates** — a boss-emitted `plan.json`, deterministic and pure:

- Contract: `validate_plan(candidate, prior, open_cells, scope, max_active=10)` — "Pure: no LLM, no DB, never raises" `[CODE] plan_gate.py:1-4,30-47`.
- Rule 6 fail-safe: malformed/missing candidate or any exception ⇒ **prior plan stands**, else empty plan ⇒ "the father renders nothing ⇒ today's deterministic path, byte-for-byte" `[CODE] plan_gate.py:38-47`.
- Rule 1 caps: `rationale <= 200`, `spawn_hint.count <= 8`, unknown fields dropped, id required `[CODE] plan_gate.py:22-23,121-155`.
- Rule 2 backing: objective must map to ≥1 open sample cell by class×glob, else reject `no_surface` (new) / retire (drained) `[CODE] plan_gate.py:203-211,226-234`.
- Rule 3 scope: concrete host in glob must pass `in_scope()` else `out_of_scope` `[CODE] plan_gate.py:173-186,222-224`; fuzzy globs fall through (cells are scope-materialized anyway) `[CODE] plan_gate.py:177-179`.
- Rule 4: classes normalized via taxonomy `normalize()`; empty ⇒ reject `no_valid_class` `[CODE] plan_gate.py:158-164,219-221`.
- Rule "1 size cap": >10 active ⇒ overflow **queued**, never refused `[CODE] plan_gate.py:95-104`.
- **Reachability:** `validate_plan` has exactly one production caller, inside `_boss_tick` *after* the flag check `[CODE] father.py:25,1165` ⇒ **dead code when `scanner_engine_boss` is off**.

**c) Deterministic state-aware selection IS the default selection mechanism** (so "no state-aware decision layer" is false):

| Mechanism | What it decides per tick | Evidence |
|---|---|---|
| Ledger claim | WHICH cells get tested: `SELECT … FOR UPDATE SKIP LOCKED`, ranked by `_CLASS_PRIORITY` (injection/authz/RCE first), optionally front-loaded by plan classes | `[CODE] ledger/service.py:1349-1378`; rank `[CODE] service.py:1259-1329`; bias `[CODE] service.py:1332-1346` |
| Sample steering | open-cell sample ordered high-value-first, handed to worklists | `[CODE] service.py:1210-1224` |
| Governor | stop/partial/continue on coverage-complete, plateau, optional runaway caps | `[CODE] governor.py:6-15,32-48`; consulted `[CODE] father.py:1825-1852` |
| Plateau detector | counts new surface / closed cells / DISTINCT confirmed findings as progress | `[CODE] father.py:1793-1811` |
| Capability escalation | rebuild chain graph, escalate only NEW high-impact caps, reopen unlocked classes, spawn focused wave | `[CODE] escalation.py:31-56`; loop `[CODE] father.py:1658-1697` |
| Within-worker reprompt | continue/stop by role-aware offensive gate + missing-work list + live progress digest | `[CODE] agents_runtime.py:942-960,962-994,1010-1021` |
| Smoke insurance | post-loop oob/xss smoke unless coverage-complete | `[CODE] father.py:1927-1928` |

**d) Orphaned decision signal:** the poller's watchdog emits `scan.method_switch` per stale `testing` cell every `WATCHDOG_STALE_SECONDS = 180` `[CODE] poller.py:111,1126-1171`, explicitly "consumed by a future planner — WS3" `[CODE] poller.py:1130-1131`. **No production consumer found** (only `poller.py` publisher + `tests/unit/test_poller_ledger_gate.py:137,157`). This is the direct code correlate of the peer-observed 99.1% `scan.method_switch` log flood.

## 0.4 D3 verification — `planner/*` and `entrypoint.run_scan` are DEAD in a default deploy

Chain (each hop verified):

1. Agent container starts `CMD ["/app/.venv/bin/python", "-m", "scanner.agent_runtime.entrypoint"]` `[CODE] docker/agent/Dockerfile:66`.
2. `main()` dispatches `_run_engine_v2()` iff `SCANNER_ENGINE_V2=="true"` else `run_scan()` `[CODE] entrypoint.py:1122-1124`; the env read defaults false `[CODE] entrypoint.py:202`.
3. But the spawner forwards `settings.scanner_engine_v2`, whose code default is **True** `[CODE] config.py:369` ("engine-v2 'Alpha Team' is the committed runtime") and compose default is `true` `[CODE] docker-compose.yml:168` → forwarded `[CODE] scheduler/worker.py:792`.
4. `run_scan()` therefore runs only (a) when an operator sets `SCANNER_ENGINE_V2=false`, or (b) as the **engine-v2 crash fallback** `[CODE] entrypoint.py:1117-1119`.
5. Inside `run_scan`, the planner path additionally requires `settings.scanner_orchestrator == "planner"` `[CODE] entrypoint.py:882`, and the base compose pins `SCANNER_ORCHESTRATOR: reprompt` `[CODE] docker-compose.yml:121`.
6. `scanner.agent_runtime.planner.*` is imported ONLY at `[CODE] entrypoint.py:883-885` (deferred, inside that branch); its only other importer is `model_tier.py:26`, which is itself imported only at `[CODE] entrypoint.py:883` + tests.
7. Alternate dispatcher `select_scan_runner()` is referenced only by `tests/unit/engine/test_engine_flag.py` — not by any spawn path.

**Verdict on D3: CONFIRMED**, with the precise caveat: `planner/*` + `run_scan` are unreachable in a default deploy *except* via the engine-v2 failure fallback. `plan_gate.py`, `boss.py`, and `context_memory.py` (§5) are additionally unreachable-dead when their respective gates are off. Treat all of them as **don't-extend, don't-fix**: new intelligence work must attach to the engine-v2 wave loop, not to these.

## 0.5 VERDICT: **PARTIAL**

| H2 sub-claim | Verdict | Why |
|---|---|---|
| "Workers spin up with near-identical STATIC prompts" (whole-prompt reading) | **REFUTED** | The task surface is re-composed per wave from live ledger/recon/board state, per group, per claimed cell (`_task_for` `[CODE] father.py:597-633`, refresh `[CODE] father.py:1781,1874`), and within-worker reprompt is stateful (`[CODE] agents_runtime.py:962-1021`). |
| "...STATIC prompts" (system-prompt-only reading) | **CONFIRMED (narrow)** | System instructions = static methodology + per-scan OOB block `[CODE] agents_runtime.py:917-940, methodology.py:13`; skill bodies static per catalog `[CODE] father.py:274-293`. No per-vuln-class template layer exists (group granularity only, `[CODE] father.py:48-85,31`). |
| Implied: "there is no state-aware decision layer" | **REFUTED** | Selection is already state-aware but *deterministic*: claim ranking + leases + bias `[CODE] service.py:1332-1378`, governor/plateau `[CODE] governor.py:32-48, father.py:1793-1811`, capability escalation `[CODE] escalation.py:31-56`, per-turn reprompt `[CODE] agents_runtime.py:962-1021`. |
| "a dynamic state-aware decision layer [does not exist / is not active]" | **PARTIAL** | The LLM layer exists (`boss.py` + `plan_gate.py`) and is *code-default OFF* `[CODE] config.py:417, father.py:1156`, but the checked-in dev overlay flips it ON `[CODE] docker-compose.override.yml:70-71`. Its effect is **unmeasured** — no `plan.revised` telemetry/artifacts found in repo logs. |
| "would measurably improve target selection" | **PARTIAL — testable but scoped** | Leverage point is real but narrow: cell choice lives in `claim_cells` (code) `[CODE] service.py:1349-1378`; an LLM layer can only reorder class priority `[CODE] service.py:1332-1346`, filter/re-prioritize objectives, and shape brief/worklist prose. **Peer failure evidence (578/972 error, 471 "no choices", 73×429, ≤2-turn stalls) is transport/model failure upstream of selection** — a decision layer cannot fix it. Honest falsifiable win-set: per-scan resolved-cell ratio (median 0.000), duplicate-endpoint update thrash (63×), stale-cell churn (99.1% `method_switch`), repeat-work in `prior_methods`. |

**H2 conclusion:** half-false as stated. What is actually missing is not "a dynamic layer" but (i) **per-cell (not class-pattern) objectives**, (ii) **closed-loop feedback of measured outcomes** into ordering, and (iii) **any consumer of the staleness stream** — plus flag discipline so any of it is default-OFF (D4). PART 1 designs exactly that.

---

# PART 1 — DESIGN (all flag-gated, default-OFF, byte-identical when off)

**Master flag:** `SCANNER_ENGINE_INTEL` → settings field `scanner_engine_intel: bool = False` (new sibling of `scanner_engine_boss` in `config.py:417` style) `[DESIGN]`.
**Off-path contract (D4):** every new entry point begins with `if not get_settings().scanner_engine_intel: return` **before any I/O, prompt build, or log write** — mirroring `_boss_tick`'s gate `[CODE] father.py:1156-1157`. With the flag off, no new file is written, no new event is emitted, no prompt section renders (all renderers are already conditional on non-empty content: `[CODE] scan_brief.py:156-160`, `[CODE] plan.py:84-94`, `[CODE] father.py:296-307`) ⇒ byte-identical behavior.

## 1. Bounded per-tick planner contract

**Module (new):** `src/scanner/agent_runtime/engine/intel.py` — *input builder, bounded call, delta parser*. Sits beside `boss.py` and reuses its executor pattern; **no new tool surface** (read-only `read_file/grep/glob` only, same as `[CODE] boss.py:76`).
**Tick site:** `father.run()` immediately adjacent to the existing tick `[CODE] father.py:1787`: `await self._intel_tick(brief)` — placed BEFORE the plateau/governor checks exactly like `_boss_tick`, so **termination logic is untouched** `[DESIGN]` (rationale: `[CODE] father.py:1782-1786`).

### 1.1 INPUT schema (skeleton) — bounded, structured, no free text from untrusted sources

```jsonc
{
  "tick": { "wave": 3, "generation": 2, "scan_id": "<uuid>" },
  // ledger state summary — derived from existing readers, nothing new invented
  "ledger": {
    "coverage": [ {"vuln_class": "sqli", "state": "untested", "n": 42} ],   // coverage_counts() [CODE] service.py:1573-1584 (<= 60 rows, capped)
    "totals":   { "done": 120, "in_flight": 6, "open": 380, "applicable": 506 },  // folded like [CODE] father.py:382-406
    "open_sample": [                                                        // sample_open_cells, n<=15 [CODE] service.py:1210-1224
      { "cell_id": "<uuid>", "endpoint": "https://h/api/orders/1",
        "vuln_class": "idor_bola", "attempt": 2, "prior_methods": ["curl"] }   // prior fields per [CODE] father.py:358-368
    ],
    "claimable": 341, "open_total": 380                                    // count_claimable_cells/count_open_cells [CODE] service.py:1508-1521,1139
  },
  "progress": {                                                             // mirrors the plateau inputs [CODE] father.py:1793-1811
    "unresolved_now": 380, "prev_unresolved": 402,
    "distinct_confirmed": 3, "prev_distinct_confirmed": 3,
    "new_cells_this_tick": 0, "plateau_risk": true, "wave": 3, "max_waves": 150
  },
  "staleness": { "stale_testing_cells": 7, "oldest_last_progress_s": 421 },  // AGGREGATED watchdog digest, <=1 line [DESIGN]; source fields [CODE] poller.py:1146-1152
  "budget": {
    "invocations": 118, "max_invocations": 0,                               // 0 = uncapped [CODE] governor.py:41-48
    "elapsed_s": 5401, "max_wall_s": 21600, "wrap_up": false,               // soft-cap signal [CODE] guardrails.py:60-66
    "cost_cap_usd": null                                                    // budget_remaining is set-once, NOT spend [CODE] context.py:427-431
  },
  "plan_state": { "version": 4, "objectives": [ {"id": "o1", "status": "active", "backing": {"open_cells": 9}, "priority": 10} ] },
  "directives": [ /* §3 AST, operator-owned, may be empty */ ],
  "policy": "<policy.md, verbatim-cap 4000>"                                // cap pattern [CODE] boss.py:100-105
}
```

**Input hard bounds** `[DESIGN]`: per-section verbatim cap 4000 chars (existing `_MAX_SECTION` `[CODE] boss.py:100`); `open_sample <= 15` (existing default `[CODE] service.py:1210`); `coverage <= 60` rows; `directives <= 20`; total serialized input `<= 24 KB` (reject-then-trim, never truncate a cell_id mid-value); wall `<= SCANNER_ENGINE_INTEL_WALL_S` default 120s, `max_turns <= SCANNER_ENGINE_INTEL_MAX_TURNS` default 4 (same knob pattern as `[CODE] boss.py:46-51`).

### 1.2 OUTPUT schema (skeleton) = a VALIDATED PLAN **DELTA**

```jsonc
{
  "version": 5,                       // informational; gate recomputes merge [CODE] plan_gate.py:107-118
  "delta": {
    "add": [                          // <= 6 per tick
      { "id": "o-<64s max>",          // merge key, required [CODE] plan_gate.py:127-129
        "kind": "exploit|recon|verify",                                      // enum [CODE] plan_gate.py:20
        "cell_ids": ["<uuid>" x <= 8],  // NEW: concrete refs, cap mirrors _SPAWN_COUNT_CAP=8 [CODE] plan_gate.py:23
        "vuln_class": "idor_bola",    // must normalize to taxonomy [CODE] plan_gate.py:158-164
        "endpoint_glob": null,        // optional pattern objective (legacy shape)
        "priority": 10,               // int, lowest = first
        "rationale": "<=200 chars, display-only>" }                          // cap [CODE] plan_gate.py:22,142
    ],
    "remove": [ { "id": "o2", "reason": "done|drained|deprioritized" } ],    // <= 6
    "requeue": [ { "id": "o3", "priority": 40 } ],                           // <= 6 (overflow is queued, never refused — [CODE] plan_gate.py:95-104)
    "abandoned": [ "o4" ]                                                    // <= 6 (boss vocabulary already defines this — [CODE] boss.py:41)
  }
}
```

**Output hard bounds / validation rules** `[DESIGN]`:
- **Bounded size:** raw reply `> 8192` bytes ⇒ invalid ⇒ prior plan stands (parser rejects, never partial-parses).
- **No free-form execution fields:** `_sanitize_objective` keeps ONLY known keys `[CODE] plan_gate.py:121-155`; the delta parser additionally rejects any object carrying `command|cmd|args|tool|payload|script|url_raw` keys ⇒ whole candidate invalid (fail-safe), never "cleaned and used".
- **Max objectives touched/tick:** 18 total (6 add + 6 remove + 6 requeue) ⇒ well under the 10-active cap after merge `[CODE] plan_gate.py:95-104`.
- **No status invention:** only `done|retired` may arrive from the planner `[CODE] plan_gate.py:153-154,215-218`; `active/rejected/queued` remain gate-computed.
- **Bounded reasoning:** `rationale <= 200`, `target_profile` caps unchanged `[CODE] plan_gate.py:107-118`.
- **Never raises:** parse + validate inside one `try` returning `None` on any failure `[DESIGN]` (same contract as `[CODE] boss.py:158-175`).

## 2. Deterministic PLAN GATE (cell-ref materialization)

**Module:** extend `engine/plan_gate.py` in place (keep `validate_plan` signature byte-compatible) + one new read-only helper in `engine/intel_gate.py` `[DESIGN]`. Rationale: the gate is already the right shape — pure, never-raising, merge-not-replace, gate-owned `backing` the boss cannot fake `[CODE] plan_gate.py:1-4,121-124`.

**Current behavior (verified, for contrast):** the gate checks class patterns against a **15-row sample** of `{endpoint, vuln_class}` — no cell ids, no DB round-trip `[CODE] plan_gate.py:33,203-211`; `sample_open_cells` returns only those two fields `[CODE] service.py:1210-1224`; scope is checked only when the glob names one concrete host `[CODE] plan_gate.py:173-186,222-224`; the whole gate is unreachable when the boss flag is off `[CODE] father.py:1156,1165`.

**Extension** `[DESIGN]`:

1. **New objective field `cell_ids[]`** accepted by `_sanitize_objective` (cap 8, UUID syntax enforced, duplicates dropped). Pattern objectives (`endpoint_glob`) keep today's sample-based `_count_backing` unchanged ⇒ flag-off and legacy-shape behavior byte-identical.
2. **Cell-ref resolver** (injected so the gate stays unit-pure in tests): `resolve_cell_facts(scan_id, cell_ids) -> {cell_id: {state, applicable, vuln_class, identity, scan_id}}`, one query, read-only.

**Exact tables/columns checked** `[DESIGN]` (all exist today):

| Table | Column | Predicate | Existing precedent |
|---|---|---|---|
| `ledger_cell` | `cell_id` | `= ANY(:refs)` | `cell_states()` `[CODE] service.py:1587-1601` |
| `ledger_cell` | `scan_id` | `= :scan_id` (cross-scan ref ⇒ drop) | `[CODE] tenant.py:255` |
| `ledger_cell` | `applicable` | `IS TRUE` | `[CODE] tenant.py:260`; query pattern `[CODE] service.py:1515` |
| `ledger_cell` | `state` | `IN ('untested','testing')` (`_OPEN_STATES` `[CODE] service.py:50`; `attempted` is terminal `[CODE] father.py:376-378`) | `[CODE] service.py:1216-1218` |
| `ledger_cell` | `attempts` | `< SCANNER_LEDGER_ATTEMPT_CAP` when cap > 0 (else claim would immediately absorb it) | `[CODE] service.py:1237-1247,1514-1519` |
| `inventory_element` | `element_id` | `= ledger_cell.element_id` (join) | `[CODE] tenant.py:256-258` |
| `inventory_element` | `scan_id` | `= :scan_id` | `[CODE] tenant.py:212` |
| `inventory_element` | `identity` | host of identity passes `in_scope(ScopeConfig, host)` | `[CODE] hooks/scope.py:83-85,357` |
| `taxonomy` | `vuln_class` | `normalize()` non-empty (Rule 4, already enforced) | `[CODE] plan_gate.py:158-164` |

3. **Materialization rule:** an objective with `cell_ids` is `active` iff **≥1** ref survives all predicates (`backing.open_cells = <surviving count>`); a dead ref is **dropped individually**; an objective whose refs all die ⇒ `status="rejected"`, `rejected="no_backing_cell"`, `backing={"open_cells":0}` — reusing `_reject()` `[CODE] plan_gate.py:167-171` and the existing reject/retire branch `[CODE] plan_gate.py:226-234`.
4. **Failure mode = objective dropped + logged, NEVER spawned.** One bounded structured log per tick: `intel.objective_dropped{id, n_refs, first_reason}` with drop-count capped at 12/tick (anti-flood: see the `method_switch` 99.1% lesson, `[CODE] poller.py:1126-1171`). Nothing is spawned because **objectives never spawn anything** — they only order the deterministic claim `[CODE] plan_gate.py:3-4`; workers receive cells only from `claim_cells` (`SKIP LOCKED`, scope-bounded) `[CODE] service.py:1349-1378`. Defense in depth: even a corrupted plan cannot test out-of-scope surface — `guard_tool_call` is fail-closed on every tool call `[CODE] guardrails.py:2-13,69`.
5. **Honest ceiling note:** objectives gate *ordering*, not leasing; a cell leased elsewhere is still not claimable this tick (leases `[CODE] service.py:1365-1371`). `backing` therefore means "materializable surface", exactly as today `[CODE] plan_gate.py:124,203-211`.

## 3. Operator playbooks → directives the engine obeys

**Existing assets (verified):**
- Built-in YAML definitions: `src/scanner/playbooks/definitions/*.yaml` (9 files) resolved deterministically with no LLM/no DB `[CODE] policy.py:22,85-100`.
- Loader schema: `Playbook.phases[] : PhaseDef{name, tasks[], parallel, fan_out, spawn_subagent, agent_model, only_severity, ...}` `[CODE] playbooks/loader.py:20-54`.
- Deterministic projection already exists: `playbook_policy_view()` → `{name, phases[], aggression, restrictions[], skip_tools[]}` `[CODE] policy.py:103-121`.
- Consume gate already exists and is default-OFF: `playbook_consume_enabled()` = `SCANNER_ENGINE_PLAYBOOK or SCANNER_ENGINE_BOSS`, both `"false"` default `[CODE] policy.py:124-132`; settings defaults `[CODE] config.py:413,417`.
- Brief PHASES directive already renders *only* when the gate is on `[CODE] scan_brief.py:131-134,278-282`.
- The full per-playbook kill-chain text (`compiled_prompt`) is consumed ONLY by the legacy path (`run_scan` → `build_orchestrator_prompt`) `[CODE] entrypoint.py:554,594-598; orchestrator.py:887-909` ⇒ dead in a default deploy (§0.5), so it must **not** be the vehicle.

**New translation layer** `[DESIGN]` — module `src/scanner/agent_runtime/engine/directives.py`, flag `SCANNER_ENGINE_INTEL` master + existing `SCANNER_ENGINE_PLAYBOOK` for ingest (both default OFF):

**Stage A — `load_directives(playbook_name) -> list[Directive]`** (pure, reuses `resolve_playbook_def`):

```jsonc
// Directive AST (validated; unknown keys dropped, never executed)
{
  "id": "<phase-name or phase#task-id, <=64>",
  "phase": "A3_authenticated",
  "intent": "order | restrict | sequence",
  "selector": {                                   // maps onto what plan_gate already knows how to check
    "vuln_classes": ["idor_bola", "bfla"],         // taxonomy-normalized on ingest (alias reuse: [CODE] plan_gate.py:158-164)
    "endpoint_glob": null,                         // fnmatch semantics as today [CODE] plan_gate.py:189-200
    "families": ["access"]                         // phase-group names [CODE] father.py:48-85
  },
  "severity_floor": "high",                        // from PhaseDef.only_severity [CODE] playbooks/loader.py:26
  "priority": 20,                                  // 1..99, phase order = priority order
  "rationale": "<=200 chars",
  "effect": "reorder_claim | add_objective | suppress_objective",   // the ONLY three effects
  "enabled": true
}
```

**Stage B — `directives_to_candidates(directives) -> list[dict]`**: emit objective-shaped dicts in **exactly the shape `_sanitize_objective` already validates** `[CODE] plan_gate.py:121-155` (id = `d:<directive id>`, classes = selector classes, endpoint_glob, priority, rationale). This makes operator playbooks a *deterministic baseline candidate* fed into the same gate every tick, independent of any LLM.

**Stage C — plan-gate filter (the enforcement):** every directive-derived objective is passed through `validate_plan`'s `_apply_rules` `[CODE] plan_gate.py:214-236`:
- class with **zero open+applicable+in-scope cells** ⇒ `rejected: "no_surface"` `[CODE] plan_gate.py:226-230` — a playbook phase that names unreachable work is dropped + logged, never spawned.
- concrete out-of-scope host ⇒ `rejected: "out_of_scope"` `[CODE] plan_gate.py:222-224`.
- Effect `reorder_claim` maps to the existing advisory claim bias `plan_priority_classes()` → `_biased_priority()` (order-only; the claim WHERE clause is untouched, "a bad plan can never restrict what's claimable") `[CODE] plan.py:97-108; service.py:1332-1346`.

**Explicitly ignored fields (D6 + safety):** `PhaseDef.spawn_subagent`, `fan_out`, `agent_model`, `on_each`, `type`, `expander`, and every `TaskDef.tool/args/target` `[CODE] playbooks/loader.py:20-34`. Playbooks may **order/filter/annotate** deterministic work; they may not spawn agents, pick models, or inject commands. Documented-only `skip_tools` stays documentation (today's stance) `[CODE] policy.py:80-81`.

**Off-path:** with `SCANNER_ENGINE_INTEL` off, `load_directives` is never called; brief PHASES and policy rendering keep their existing independent gates `[CODE] scan_brief.py:278-282, policy.py:124-132` ⇒ byte-identical.

## 4. Failure semantics — PRIOR PLAN STANDS

Single rule: **any planner failure ⇒ the previous accepted plan (or `{}` at scan start) survives and the wave loop executes the exact code path it executes today.**

| Failure | Detection | Fallback return point | Byte-identity path |
|---|---|---|---|
| Flag off (default) | first line of `_intel_tick` | `return` before any I/O `[DESIGN]` (gate pattern `[CODE] father.py:1156-1157`) | `self._plan` never set ⇒ `plan_priority_classes({})` → `[]` ⇒ claim uses `_CLASS_PRIORITY` unchanged `[CODE] plan.py:97-108; service.py:1339-1340`; `_plan_prefix("") == ""` `[CODE] father.py:301-302`; brief PLAN section absent `[CODE] scan_brief.py:156-160` |
| SDK/creds absent | executor builder returns `None` | `return` (pattern `[CODE] boss.py:67-71`) | same as above |
| Timeout / transport error | `asyncio.wait_for(..., wall)` ⇒ exception | caught ⇒ `return` (pattern `[CODE] boss.py:171-174`) | same as above |
| Invalid / oversized / free-text-bearing output | parser returns `None` (size + key whitelist) `[DESIGN]` (pattern `[CODE] boss.py:133-146`) | `return` | same as above |
| Gate keeps nothing (all objectives rejected) | `not gated.get("objectives")` | `return` without touching `self._plan` (exact precedent `[CODE] father.py:1166-1167`) | same as above |
| Gate raises internally | `validate_plan` never raises; returns prior `[CODE] plan_gate.py:44-47` | n/a | prior preserved by the gate itself |
| Resolver (DB) error | resolver returns `{}` best-effort (pattern `[CODE] service.py:1602-1604`) | cell-ref objectives ⇒ `no_backing_cell` reject ⇒ drop+log `[DESIGN]`; pattern objectives unaffected | claim/termination unchanged |
| Planner hangs mid-tick | wall cap fires inside `wait_for` | same as timeout | wave loop never blocks past the cap |

**Where the fallback returns:** `_intel_tick` returns to `father.run()` at the line adjacent to `[CODE] father.py:1787`; execution then proceeds untouched through plateau measurement `[CODE] father.py:1793-1811`, coverage-complete `[CODE] father.py:1817-1819`, governor `[CODE] father.py:1825-1852`, claim `[CODE] father.py:1874`, and `build_specs(..., plan_digest=self._plan_digest)` `[CODE] father.py:1876-1886` — with `self._plan`/`self._plan_digest` at their pre-tick values, which is exactly today's production path.
**Telemetry discipline:** ≤ 2 log events per tick (`intel.tick_ok` / `intel.tick_skipped{reason}`) + ≤ 12 drop lines — deliberately bounded to avoid reproducing the `method_switch` flood `[CODE] poller.py:1126-1171`.

## 5. What the planner must NOT do (D6 + safety), and why

| Forbidden | Why | Repo evidence this is the right call |
|---|---|---|
| **No recursive agent hierarchies** (planner spawning specialists/sub-agents) | Objectives must only *order* work that deterministic code already owns; spawn stays in `father.run()` (`fleet.run_all` / `_run_batch_pool`) `[CODE] father.py:1898-1901`. Hierarchy code exists and is deliberately dead-by-default: `planner/coordinator.run(...)` + `SubagentPool` `[CODE] entrypoint.py:882-925` (§0.5); loader even ships `spawn_subagent`/`fan_out`/`agent_model` fields we ignore `[CODE] playbooks/loader.py:24-27`. | D6; and the peer-observed 59.5% worker error rate means MORE concurrent agents multiplies the dominant failure mode |
| **No agent-to-agent chat messaging** | There is no message channel today: worker input is a code-built string `[CODE] worker.py:11`, boss is read-only and cannot act `[CODE] boss.py:76,40-42`, and the only cross-component bus is `/work` artifacts + DB rows + events. Introducing chat creates un-bounded context growth and an unauditable instruction path that bypasses `guard_tool_call`. | `scan.method_switch` already shows what an unconsumed event stream costs: 99.1% of log lines, no consumer `[CODE] poller.py:111,1130-1131` |
| **No pgvector semantic memory** | `context_memory.MemoryStore` (`engine_memory`, `vector(8)`) is **imported by nothing** (grep over `src/` = only its own module) ⇒ dead code; adding planner memory on it would require an extension + migration, and inject non-deterministic recall into a fail-closed path. Bounded structured state already exists: ledger + `plan.json` (`write_plan` atomic) `[CODE] plan.py:32-44` + `scan_brief.md` `[CODE] scan_brief.py:249-292`. | D6; keep memory *structured and keyed* (cell_id/state), not vector-similarity |
| **Never mint cells, widen scope, mark work done, or own termination** | Boss may "ONLY prioritize/filter existing in-scope work" `[CODE] boss.py:40-42`; `backing`/`rejected` are gate-owned and not copyable `[CODE] plan_gate.py:124`; scope fail-closed in the guard `[CODE] guardrails.py:8-13`; termination stays code after the tick `[CODE] father.py:1782-1786,1813-1852`. | existing §5 precedence, kept verbatim |
| **Never carry executable content** | Only whitelisted keys survive sanitization `[CODE] plan_gate.py:121-155`; rationale is display-only; no command/args keys accepted (§1.2) `[DESIGN]`. | keeps "LLM proposes, ledger disposes" `[CODE] boss.py:6` |
| **Never read/write outside `/work` (read-only) or persist side effects** | Boss pattern: no `session_factory`/`scan_id` on the runtime ⇒ no persistence side effects `[CODE] boss.py:62-66`; plan persisted only via `write_plan` `[CODE] plan.py:32-44`. | |

---

# RANKED INTEGRATION PLAN (R7 — module + flag + buyer-visible outcome)

| # | Module (new/extend) | Flag (default) | Dependency | Buyer-visible outcome |
|---|---|---|---|---|
| 1 | **Extend** `engine/plan_gate.py` + new `engine/intel_gate.py` (cell-ref resolver) | `scanner_engine_intel = False` (master) | none — pure + one read-only query (`cell_states` pattern `[CODE] service.py:1587`) | "Every objective maps to a real open+applicable+in-scope cell": no worker turn spent on phantom/pattern-matched surface; drops logged with cell_id + reason |
| 2 | **New** `engine/directives.py` (playbook → Directive AST → gate candidates) | `scanner_engine_intel=False` + existing `scanner_engine_playbook=False` | #1 (same gate) | The operator's playbook phases *visibly steer* the scan (brief PHASES + claim order + plan section in UI) instead of sitting inert in `policy.md` `[CODE] policy.py:7-8,139` |
| 3 | **New** `engine/intel.py` (bounded per-tick planner: INPUT/OUTPUT §1) wired at `father.run()` beside `[CODE] father.py:1787` | `scanner_engine_intel=False` (+ `SCANNER_ENGINE_INTEL_WALL_S/MAX_TURNS` knobs) | #1 (its delta must pass the gate) | Re-plan visible as `/work/plan.json` + UI plan section; measurable on the peer metrics: resolved-cell ratio (median 0.000), duplicate-endpoint update thrash (63×), repeat-work in `prior_methods` |
| 4 | **New** bounded staleness consumer: aggregate `ledger_cell.last_progress` staleness into the §1 INPUT (one line/tick) — *not* per-event subscription | `scanner_engine_intel=False` (inherits master) | #3 | Stale `testing` cells get deprioritized/re-planned instead of re-emitted forever; keeps log volume flat (no repeat of the 99.1% flood) |
| 5 | **A/B harness** (measurement only): same target, flag off vs on, report resolved-cell ratio, distinct findings/wall-hour, duplicate-endpoint updates, `plan.revised` count | evaluation phase only | #1-#4 | The falsifiable answer to H2's second half — ship/keep-off based on numbers, not narrative |

**Flag-discipline summary (D4):** five rows, one master boolean, all default `False`; flag-off ⇒ zero new I/O, zero new prompt bytes, zero new events ⇒ production byte-identical.

---

# EVIDENCE LEDGER

| ID | Claim | Citation | Type |
|---|---|---|---|
| E01 | Worker system prompt = static methodology + per-scan OOB block | `agents_runtime.py:917-940`; `methodology.py:13`; `claude_sdk.py:149` | [CODE] |
| E02 | Worker task composed per wave/group/cell: brief+capability+board+plan+skills+handoff+triage+worklist+focus/wave body | `father.py:597-633`; call sites `father.py:670,1277-1280,714,1506,1559-1564` | [CODE] |
| E03 | Brief rebuilt from live /work every wave; plan section absent when no plan | `father.py:1781`; `scan_brief.py:249-292,156-160` | [CODE] |
| E04 | Worklists are this wave's claimed cells per group, with prior-methods blackboard | `father.py:1874-1875,409-417,351-372`; claim `service.py:1349-1378` | [CODE] |
| E05 | Coverage board + capability context vary per wave/escalation | `father.py:1194,382-406`; `father.py:1520-1548,1717` | [CODE] |
| E06 | Within-worker reprompt is stateful (missing-work list + progress digest) | `agents_runtime.py:808-838,942-960,962-994,1010-1021` | [CODE] |
| E07 | No per-vuln-class template layer; granularity = phase-group (class→group map) | `father.py:31,48-85,194-229` | [CODE] |
| E08 | Boss re-plan exists, per-wave-tick, state-aware inputs, read-only tools, never raises | `boss.py:33-43,76,108-130,149-175`; call `father.py:1787,1145-1176`; wiring `run.py:250-261` | [CODE] |
| E09 | Boss/plan-gate are code-default OFF (`scanner_engine_boss=False`); spawn forwards it | `config.py:415-417`; `scheduler/worker.py:796-798` | [CODE] |
| E10 | Checked-in auto-load overlay flips BOSS+PLAYBOOK ON (dev smoke test) | `docker-compose.override.yml:70-71` (header 1-4); base `docker-compose.yml:121,168,172` | [CODE] |
| E11 | `plan_gate` is pure/never-raises, merge-not-replace, caps, sample-based backing, scope+class rules, fail-safe = prior stands | `plan_gate.py:1-4,30-47,95-104,121-155,158-186,203-236` | [CODE] |
| E12 | `plan_gate` has one production caller, inside the boss flag guard ⇒ dead when flag off | `father.py:25,1156,1165` | [CODE] |
| E13 | Deterministic state-aware selection: ranked SKIP LOCKED claim + advisory bias; governor; plateau; escalation; smoke | `service.py:1259-1378,1508-1521`; `governor.py:6-48`; `father.py:1793-1811,1825-1852`; `escalation.py:31-56`; `father.py:1927-1928` | [CODE] |
| E14 | Watchdog emits unconsumed `scan.method_switch` per stale testing cell every 180s | `poller.py:111,1126-1171,1130-1131`; consumer grep = tests only | [CODE] |
| E15 | D3: default deploy runs engine-v2; `run_scan`+`planner/*` unreachable except fallback/disabled flag | `docker/agent/Dockerfile:66`; `entrypoint.py:202,530,882-925,1104-1124`; `config.py:369`; `docker-compose.yml:121,168`; `scheduler/worker.py:792` | [CODE] |
| E16 | Ledger schema for gate: `ledger_cell(cell_id,scan_id,element_id,vuln_class,applicable,state,attempts,claimed_by,lease_expires_at,last_progress)`; `inventory_element(scan_id,identity)` | `tenant.py:204-219,247-281`; open states `service.py:50` | [CODE] |
| E17 | Scope: `ScopeConfig(targets,exclusions)` + `in_scope()`; guard fail-closed on every tool call | `hooks/scope.py:83-85,357`; `guardrails.py:2-13,56-69` | [CODE] |
| E18 | Playbook assets: definitions dir, loader schema (incl. `spawn_subagent`), policy view, consume gate default-OFF, brief PHASES gated | `policy.py:22,85-132`; `playbooks/loader.py:20-54`; `scan_brief.py:131-134,278-282`; `config.py:413` | [CODE] |
| E19 | `compiled_prompt` consumed only by legacy `run_scan` path (dead by default) | `entrypoint.py:554,594-598`; `orchestrator.py:887-909` | [CODE] |
| E20 | `context_memory.MemoryStore` (pgvector) has no importers ⇒ dead code | `context_memory.py:9-47`; grep over `src/` = self only | [CODE] |
| E21 | Budget signals: `budget_remaining` is set-once sentinel, not spend; runaway caps off by default | `context.py:425-431`; `governor.py:41-48` | [CODE] |
| E22 | Batch dispatch (cell-grouped spec path) default OFF | `config.py:437`; `batch.py:30-61` | [CODE] |
| E23 | No `plan.revised` telemetry / plan.json artifacts found in repo logs (boss effect unmeasured) | repo `logs/` (Aug-2026 CAI jsonl only); grep = none | [CODE-negative] |
| D1-D5 | All §1-§5 proposals, incl. `scanner_engine_intel` master flag, cell-ref gate, Directive AST, failure table, forbidden list | this document | [DESIGN] |

**Negative findings (explicitly "not found in repo"):** per-vuln-class prompt templates; any production consumer of `scan.method_switch`; any importers of `context_memory`; any runtime caller of `planner.*` outside `entrypoint.run_scan`'s gated branch; any persisted boss/plan telemetry artifacts.

# WS-5 — INTELLIGENCE / DECISION LAYER: DESIGN SPECIFICATION

**Sub-agent:** `ws5_intelligence_layer` · **Lead:** `research-agent-falcon-02`
**Repo:** `C:\Users\ASUS\Desktop\abhdeii\autocan` @ `feat/alpha-observability` / `f75608f` (READ-ONLY)
**Mode:** DESIGN ONLY. No repo file was modified. No live write/scan/request was issued (R1, R4).
**Constraint honoured:** every new capability below ships behind a named flag, default **OFF**, byte-identical when off (D4).

---

## 0. HEADLINE FINDING THAT SHAPES THIS SPEC

**A state-aware decision layer already exists and is already wired — and it is already ON in production.**
`plan.py`, `plan_gate.py`, `boss.py`, `policy.py` are built, tested (16 gate unit tests), and hooked
(`father.py:24-25, 1145-1176, 1787`; `scan_brief.py:274`). The live agent container runs with
`SCANNER_ENGINE_BOSS=true` and `SCANNER_ENGINE_PLAYBOOK=true`
[CODE `improvment-research/research-agent-osprey-01/evidence/ws1_ws2_telemetry.md:23,32`] while
`docs/context/CAPABILITIES.md:37` and `docs/context/FLAGS.md:123` both document it **OFF**.

Therefore this spec is **not** a greenfield planner. It is four surgical repairs to a shipped,
mis-documented, under-bounded component. Every proposal below names an existing module to EXTEND.
Nothing proposes replacing `plan_gate.py`, and nothing proposes removing the advisory-only property
of `_biased_priority` (`ledger/service.py:1332-1346`).

---

## A. DESIGN RATIONALE

1. **The planner tick blocks the wave loop.** `await self._boss_tick(brief)` is inline at `father.py:1787`,
   and its only bound is `asyncio.wait_for(..., timeout=wall_s)` with `wall_s` default **180s**
   [CODE `engine/boss.py:47, 94`]. Live env runs `SCANNER_ENGINE_HTTP_TIMEOUT=300`,
   `SCANNER_ENGINE_MAX_RETRIES=8` [CODE osprey evidence `:33`], so a single upstream call can consume the
   entire budget. Result: up to 180s of pure idle on the critical path before any worker is dispatched,
   per wave, against a pool whose mean tool concurrency is already 0.67/4 (WS-1). → **D1 moves the tick
   off the critical path and bounds it at 45s/4 turns/2 tool calls, applied one tick late.**

2. **The plan gate decides on a surface read that silently failed.** `father._sample_open()` returns `[]`
   on ANY exception [CODE `engine/father.py:1129-1134`]. `validate_plan` cannot distinguish that from a
   genuinely drained grid, so `_count_backing` returns 0 for every objective and `_apply_rules`
   [CODE `engine/plan_gate.py:226-234`] rejects every new objective *and auto-retires every prior one*.
   A retired objective is terminal and is never revived (`plan_gate.py:65` carries forward only
   `status != "rejected"`). **One transient DB error silently and permanently strips the entire boss bias
   for the rest of the scan**, degrading to unrestricted `_CLASS_PRIORITY` with no operator-visible error.
   This is structurally the same fail-open shape WS-2 found in the anti-fabrication gate. → **D2 adds a
   third state (`unreadable`) and quarantines the tick. The gate may only retire on positive evidence.**

3. **The gate's backing predicate is not the claim's predicate.** `_count_backing`
   [CODE `plan_gate.py:203-211`] counts cells from `sample_open_cells(n=200)` [CODE
   `engine/attack_surface.py:103`; `ledger/service.py:1210-1224`], which — unlike `claim_cells`
   [CODE `service.py:1396-1402`] — ignores `attempts < cap` AND ignores live leases, and is a 200-row
   window ordered by `_CLASS_PRIORITY`. So an objective can read `active` while backed entirely by
   attempt-capped or currently-leased cells that `claim_cells` will never hand out. → **D2 replaces the
   sample with one frozen `COUNT(*)` under the claim-identical `WHERE`.**

4. **A playbook has zero machine channel.** `playbook_policy_view` [CODE `engine/policy.py:103-121`]
   projects only `name`, `phases[].name`, two rate fields, four restriction flags and `skip_tools`.
   `phases[].tools`, `phases[].goal`, `behavior.*` and `blocker_handling.*` are **discarded**. There is no
   `vuln_class` field anywhere in either playbook schema [CODE `playbooks/schema.py:9-55`,
   `playbooks/loader.py:9-47`]. The only behavioural effect a playbook has on engine-v2 is
   `entrypoint._resolve_min_invocations_target`, a hardcoded `frozenset` of two names → 150 invocations
   [CODE `entrypoint.py:97-119`]. A buyer who buys `full_coverage_vapt` gets prose. → **D3 adds a
   compile path to a machine-checkable directive whose only ledger effect is claim ORDER.**

5. **Playbooks fail OPEN on unrecognised safety clauses.** `UserPlaybook.restrictions` models
   `no_destructive_ops / no_data_exfiltration / no_dos / skip_tools` [CODE `schema.py:9-13`]; the shipped
   `playbooks/deep_offensive_vapt.yaml:11-14` declares `no_persistence` and `in_scope_only`, which are
   not fields. Pydantic's default `extra='ignore'` drops them **silently**, so the operator's declared
   "no persistence" clause has no representation anywhere. → **D3 sets `extra="forbid"`** so an
   unrecognised safety clause is a 422 at authoring time, never a silent no-op at scan time.

6. **The decision layer is structurally blind.** `resolved_count` is declared `worker.py:20`, read at
   `telemetry.py:183`, and assigned **nowhere in `src/`** — grep for `resolved_cells` returns exactly
   three hits (1 declaration, 2 reads) [CODE]. It is therefore 0 on every `worker_runs` row by
   construction, and `reporting/effort.py:64` publishes that 0 to the buyer. `findings_count` is
   self-reported pre-verification at `telemetry.py:182`; the corrective rollup at `telemetry.py:249-307`
   computes the true total, then **returns it without writing anything back** because
   `remainder = total - attributed` is negative and line 282 short-circuits — so the 139× over-report
   survives. → **F repairs all four blind fields; a planner cannot steer on numbers that are 0 or 139×.**

---

## B. DELIVERABLE 1 — BOUNDED, PER-TICK PLANNER CONTRACT

### B.0 Extend, do not reinvent

`plan.py` (108 lines) already owns atomic `read_plan`/`write_plan` (temp + `os.replace`,
`plan.py:32-44`), the ≤1500-char digest (`plan.py:84-94`) and the priority-class projection
(`plan.py:97-108`). `boss.py` already owns a bounded per-tick call (`boss.py:149-175`) that returns
`None` on every failure. The only structural change is **where the tick runs and what it emits**.

### B.1 Hook site — `engine/father.py:1787`

The existing comment at `father.py:1782-1786` records *why* the tick sits where it does: "Placed BEFORE
the plateau/_is_complete/governor/quiescence checks so termination is untouched." **That placement is
load-bearing and is preserved exactly.** One line changes:

```
1787:  await self._planner_step(brief)      # was: await self._boss_tick(brief)
```

```python
async def _planner_step(self, brief: str) -> None:
    """Bounded planner step. Off => delegates VERBATIM to the legacy inline _boss_tick."""
    if not getattr(get_settings(), "scanner_engine_planner_tick", False):
        await self._boss_tick(brief)          # byte-for-byte legacy (one branch)
        return
    await self._planner_harvest()             # non-blocking: collect last tick's delta
    snap = await self._planner_observe()      # bounded DB snapshot (<=5 queries)
    self._planner_spawn(snap, brief)          # create_task, NEVER awaited
```

`_planner_spawn` records `self._planner_pending` (task handle) + `self._planner_snapshot_version`.
`_planner_harvest` runs at the top of the **next** tick: if the task is done, take the delta; if it is
**still in flight, cancel it and discard the reply**. The planner therefore never blocks the wave loop,
and a plan is at most **one tick stale** — which is the correct trade, because the claim bias is
advisory and the wave loop's real inputs (ledger state, brief) are re-read fresh each tick regardless.

### B.2 Input schema — `PlannerInput` (deterministic; built by SQL, never by the model)

```jsonc
{
  "schema": 1,
  "scan_id": "uuid", "observed_at": "iso8601", "plan_version": 7,
  "surface": {
    "claimable_cells": 1841,            // count_claimable_cells()  [service.py:1508]
    "applicable_cells": 9236,
    "cells_by_state": {"untested":321,"testing":1701,"tested_clean":943,
                       "confirmed":19,"blocked":6,"na":6247,"attempted":12},
    "open_by_class": [{"vuln_class":"sqli","claimable":212}, ...]  // <=40 rows, desc by claimable
  },
  "progress": {
    "wave": 4, "tick": 3,
    "cells_closed_last_tick": 96, "cells_inserted_last_tick": 41,
    "distinct_findings_total": 19, "distinct_findings_last_tick": 2,
    "attempts_histogram": {"0":61816,"1":6903,"2":966,"3":449,"4":364,"5":125,"6":158},
    "attempts_exhausted_cells": 1096     // hits cap -> terminal 'attempted'
  },
  "economics": {                          // NEW — unlocked by §F
    "model_messages": 348, "tool_calls": 37047, "tool_calls_per_message": 106.5,
    "wall_s": 9630, "cells_closed_per_wall_s": 0.0199,
    "findings_per_1k_tool_calls": 6.99, "resolved_count_total": 0
  },
  "capabilities": ["session_credential","db_read"],   // father._capability_context source set
  "plan": {"version":7,"objectives":[{"id":"O3","status":"active","priority":2,
            "classes":["sqli"],"endpoint_glob":"/api/*","backing":{"open_cells":212}}]},
  "directive": {"playbook_name":"full_coverage_vapt","playbook_version":"2.0",
                "source_sha256":"…","directive_version":3}
}
```

`open_by_class` is the **new** per-class backing feed (D2) and replaces the 200-row sample in the
prompt — smaller prompt, strictly more information, and it is the exact set `claim_cells` could hand out.

### B.3 Output delta schema — the model emits a DELTA, not a whole plan

```jsonc
{
  "version": 7,                            // MUST echo input.plan_version  [concurrency token]
  "objectives": [                          // <= SCANNER_PLANNER_MAX_DELTA (6)
    {"id":"O4","op":"upsert","kind":"exploit",
     "classes":["idor_bola","bfla"],"endpoint_glob":"/api/v1/orders/*",
     "priority":3,"rationale":"<=200 chars, display only"}
  ],
  "abandoned": ["O1","O2"]                 // <= SCANNER_PLANNER_MAX_RETIRE (4)
}
```

**Why a delta, not a whole plan.** The current design has the model re-emit the entire plan every tick
and merge it (`plan_gate.py:68-87`). Two overlapping ticks therefore merge against the *same* prior and
the later write silently clobbers the earlier — a lost update with no detection. Echoing `version` and
discarding on mismatch (`D2` step S3) turns that race into an observable `gate_status="stale"`.

### B.4 Bounds (all new, all default-off, all env-overridable)

| Bound | Flag | Default | Replaces | Enforcement site |
|---|---|---|---|---|
| Hard wall-clock per tick | `SCANNER_PLANNER_TICK_WALL_S` | **45** | `SCANNER_ENGINE_BOSS_WALL_S=180` | `asyncio.wait_for` inside the spawned task |
| Max model turns per tick | `SCANNER_PLANNER_MAX_TURNS` | **4** | `SCANNER_ENGINE_BOSS_MAX_TURNS=8` | `Runner.run(max_turns=…)` |
| Max tool calls per tick | `SCANNER_PLANNER_MAX_TOOL_CALLS` | **2** | unbounded (3 read-only tools) | counting closure wrapper; over → truncate reply → `parse_ok=False` |
| Max objectives per delta | `SCANNER_PLANNER_MAX_DELTA` | **6** | unbounded | `_enforce_active_cap` overflow → **queued, never refused** |
| Max retire per delta | `SCANNER_PLANNER_MAX_RETIRE` | **4** | unbounded | excess queued |
| Max model calls per scan | `SCANNER_PLANNER_MAX_TICKS` | **12** | unbounded | latch prior plan after the 12th |
| Min gap between ticks | `SCANNER_PLANNER_COOLDOWN_S` | **60** | per-wave | skip spawn |
| Max DB queries per tick | constant `5` | — | 1 | `_planner_observe` |

The tool-call cap exists because `max_turns_exceeded` fired on **63/63** recorded turns (WS-1): the
planner is handed the board and does not need to dig, so 2 reads is generous and 4 turns is ample.
Truncating the reply rather than raising is deliberate — an over-budget reply is treated as
`parse_ok=False` → prior plan stands (§E row 4).

### B.5 Buyer-visible outcome

The console gains a **Plan** panel showing, per tick: tick #, wall ms, bounded-by reason, gate status,
active objective count, and rejection reasons by category. Today the only plan event is `plan.revised`
(`father.py:1173-1176`), emitted **only on success** — so "planner OFF" and "planner broken" are the same
silence in the DB. Wall-clock: the decision layer's contribution to wave latency drops from
`≤180s × waves` to `0s` on the critical path.

---

## C. DELIVERABLE 2 — DETERMINISTIC PLAN GATE (EXTEND `engine/plan_gate.py`)

### C.1 Extend vs replace — **EXTEND. Do not replace.**

`plan_gate.py` is already correct on every structural property and has 16 unit tests covering the
fail-safe paths [CODE `tests/unit/engine/test_plan_gate.py:7,16,21,27,132,138,150`]. Specifically it is
already: pure (no LLM, no DB), never-raises (`plan_gate.py:45-47`), merge-not-replace
(`plan_gate.py:68-87`), sanitize-drops-unknown-fields with **`backing`/`rejected` gate-owned so the boss
cannot fake surface** (`plan_gate.py:121-124`), scope-hard-reject-only-on-a-nameable-host
(`plan_gate.py:173-186`), taxonomy-normalised classes (`plan_gate.py:158-165`), and overflow-queued-
never-refused (`plan_gate.py:95-104`). Replacing it would discard a correct safety component.

**Two defects remain, and both are upstream of the gate's control flow:** the backing *source* (C.3) and
the *unreadable* surface (C.4). Its existing `except Exception: return prior` (`plan_gate.py:45-47`) is
already the right shape — fall back to the last-known-good **validated** artifact.

### C.2 Validation steps (cheap-first; S0–S7)

| # | Step | Predicate | On failure |
|---|---|---|---|
| S0 | Shape | `isinstance(candidate, Mapping)` and `isinstance(candidate["objectives"], list)` | prior stands, unchanged [exists `plan_gate.py:41`] |
| **S1** | **Surface read OK** | `surface_read.ok is True` | **QUARANTINE**: return `prior` verbatim — no merge, no recompute, no retire, no reject; log `plan.gate.quarantined` |
| S2 | Sanitize | known fields only; `id` required; `priority` int-coerced; `rationale` ≤200; `spawn_hint.count` ≤8; `status` only if in `{done, retired}`; `backing`/`rejected` never copied | drop the objective silently; boss re-proposes [exists `plan_gate.py:121-155`] |
| **S3** | **Version echo** | `candidate.version == input.plan_version` | discard delta as **stale**; prior stands; `gate_status="stale"` |
| S4 | Scope | `host = _glob_host(glob)`; if `host is not None and not in_scope(scope, host)` | `rejected: out_of_scope` [exists `plan_gate.py:222-224`] |
| S5 | Class normalisation | `taxonomy.normalize(c).value` for each; empty ⇒ reject `no_valid_class` | `rejected: no_valid_class` [exists `plan_gate.py:158-165, 219-221`] |
| **S6** | **Backing (claim-identical)** | `backing_count := COUNT(*)` under the `claim_cells` `WHERE` (C.3) | `>0` ⇒ `active`. `==0 AND ok` ⇒ new: `rejected: no_surface`; prior: `retired: drained` |
| S7 | Size cap | ≤`max_active` active (10); overflow **queued** | nothing refused [exists `plan_gate.py:95-104`] |

### C.3 S6 predicate — the frozen backing query

New `ledger/service.py::count_claimable_by_class(session, scan_id)` — **one** grouped query per tick,
under the *identical* predicate `claim_cells` uses (`service.py:1396-1402`):

```sql
SELECT c.vuln_class, count(*) AS n
FROM ledger_cell c
GROUP BY c.vuln_class
WHERE c.scan_id      = CAST(:sid AS uuid)
  AND c.applicable   = true
  AND c.state IN ('untested','testing')
  AND (c.claimed_by IS NULL OR c.lease_expires_at IS NULL OR c.lease_expires_at < now())
  AND (:cap <= 0 OR c.attempts < :cap);
```

Then, for each candidate objective (≤`max_active`=10), **one narrow `COUNT(*)`** with the same
predicate plus the endpoint match, joined to `inventory_element` for `identity`:

```sql
SELECT count(*)
FROM ledger_cell c
JOIN inventory_element e ON e.element_id = c.element_id
WHERE c.scan_id = CAST(:sid AS uuid)
  AND c.applicable = true
  AND c.state IN ('untested','testing')
  AND (c.claimed_by IS NULL OR c.lease_expires_at IS NULL OR c.lease_expires_at < now())
  AND (:cap <= 0 OR c.attempts < :cap)
  AND c.vuln_class = ANY(:classes)
  AND e.identity = ANY(:identity_candidates);
```

`:identity_candidates` is produced **in Python** by applying the existing `_endpoint_matches` /
`fnmatch` logic (`plan_gate.py:189-200`) to a `LIMIT 200` row fetch of the objective's classes —
i.e. the glob is still resolved by the already-tested pure function, but against rows that are
*actually claimable* rather than against a global priority-ordered sample. Total gate DB calls per
tick: `1 + ≤10`.

This fixes three concrete falsehoods at once: (a) attempt-capped cells can no longer back an objective;
(b) cells currently leased to a live worker can no longer back an objective; (c) a legitimate
low-priority objective is no longer permanently un-backable because the 200-row window is ordered by
`_CLASS_PRIORITY` (`service.py:1221`) and therefore only ever contains tier-1a classes.

### C.4 FAIL-CLOSED semantics — explicitly NOT repeating the `run.py:109` pattern

The anti-fabrication pattern WS-2 found is: **a timeout/exception silently *disables* the gate**, leaving
the permissive default in place and indistinguishable from "the gate ran and passed". The decision layer
has the same shape one layer up:

```
father._sample_open()  except Exception → log + return []        [father.py:1129-1134]
        ↓  (empty list is indistinguishable from a drained grid)
plan_gate._count_backing([]) → 0 for every objective           [plan_gate.py:203-211]
        ↓
plan_gate._apply_rules:  new → rejected("no_surface")
                         prior → status="retired"  (TERMINAL)  [plan_gate.py:226-234]
        ↓
_validate carries forward only status != "rejected"            [plan_gate.py:65]
        ↓  ⇒ retired objectives are never revived
render_plan_digest → ""   and   plan_priority_classes → []    [plan.py:84-94, 97-108]
        ↓
claim falls back to unrestricted _CLASS_PRIORITY               [service.py:1332-1346]
```

**The three-state fix.** Change the seam's contract from a bare `list` to a sentinel-bearing value:

```python
@dataclass(frozen=True)
class SurfaceRead:
    cells: list[dict[str, str]]
    ok: bool            # False == "could not read", NOT "nothing there"
```

`father._sample_open` returns `SurfaceRead([], ok=False)` in its `except` (`father.py:1132-1134`).
`validate_plan` gains the `surface: SurfaceRead` parameter and applies **S1** as the very first
substantive step. `_apply_rules` gains a third terminal reason, `unreadable`, which is reachable
**only** from `ok=False` — never from an empty-but-readable list.

**Fail-closed invariants, stated as testable properties:**

- **I1.** An objective may move `active → rejected|retired` **only** on positive evidence from an
  `ok=True` read showing zero claimable matches. No uncertainty ever retires anything.
- **I2.** Every gate failure mode returns `prior` **unchanged** — the same object, no recompute, no
  merge, no version bump. `plan.json` on disk is always gate-produced; there is no state in which an
  unvalidated or partially-validated plan is persisted.
- **I3 (the mirror of `_biased_priority`).** A gate failure may only ever leave work **ordered as
  before**. It can never make more work claimable, never mint a cell, never widen scope, never keep a
  terminated scan alive. Guaranteed structurally: `priority_classes` reaches SQL *only* as the `:ranked`
  array bound into `array_position` in `ORDER BY` (`service.py:1403`); the `WHERE` clause
  (`service.py:1396-1402`) is a constant with no class-derived term.
- **I4.** "OFF", "broken", and "could not read surface" are three **distinguishable** states in the DB
  (via `plan.tick` / F5), never one silent null.

### C.5 Flags

`SCANNER_PLAN_GATE_V2` (`scanner_plan_gate_v2: bool = False`). Off ⇒ `validate_plan` receives the
existing `open_cells: list` and runs the existing S0/S2/S4/S5/S7 unchanged; the `SurfaceRead` parameter
defaults to `SurfaceRead(cells, ok=True)` so no call site changes behaviour.

---

## D. DELIVERABLE 3 — PLAYBOOK → MACHINE-CHECKABLE DIRECTIVE → LEDGER EFFECT

### D.0 What exists today (the gap, precisely)

| Channel | Present? | Citation |
|---|---|---|
| `policy.md` prose | yes, always written; consumed only when a flag is on | `policy.py:124-132, 135-161` |
| brief PHASES directive (names only) | yes, gated | `scan_brief.py:131-134, 278` |
| `phases[].tools` / `.goal` | **discarded** | `policy.py:108` reads `p["name"]` only |
| `behavior.*` beyond 2 fields | **discarded** | `policy.py:109-117` |
| `blocker_handling.*` | **discarded** | absent from `policy.py:103-121` |
| `vuln_class` anywhere in a schema | **absent** | `schema.py:9-55`, `loader.py:9-47` |
| any ledger effect | **none** | only `entrypoint.py:97-119` (a hardcoded frozenset → 150 invocations) |
| `deep_offensive_vapt.yaml` (repo root) | **orphan** — not in `definitions/`, referenced by no code | dir listing; grep finds only `full_coverage_vapt` |

### D.1 The compile path — one pure function, four stages

New module `src/scanner/playbooks/compile.py`:

```python
def compile_playbook_directive(
    yaml_text: str, *, defs_dir: Path, taxonomy: ModuleType
) -> PlaybookDirective:      # pure, never raises — returns .errors[] instead
```

**Stage 1 — PARSE (strict, fail closed).** `yaml.safe_load` → `UserPlaybook.model_validate`. Change the
failure mode from *ignore* to *reject*: add `model_config = ConfigDict(extra="forbid")` to
`PlaybookRestrictions`, `PlaybookBehavior`, `BlockerHandling`, `UserPlaybookPhase`, `UserPlaybook`
(`schema.py`). Consequence: `no_persistence` / `in_scope_only` in
`playbooks/deep_offensive_vapt.yaml:11-14` become a **422 at authoring time** via the existing
`validate_user_playbook` handler (`api/routes/playbooks.py:96, 99-100, 159, 162-163`) instead of a
silent no-op at scan time. This is the anti-fabrication-grade discipline applied to operator content.

**Stage 2 — RESOLVE classes.** New optional top-level block in the playbook:

```yaml
coverage:
  priority_classes: [sqli, idor_bola]        # -> ledger :ranked front-set
  defer_classes:    [sourcemap, weak_cipher] # -> demote (reverse placement), NEVER exclude
  phase_classes:                                 # optional per-phase binding
    A4_injection: [sqli, nosqli, cmdi]
    A5_auth_access_control: [idor_bola, bfla, jwt_flaws]
  min_cells_per_class: 8
```

Every class in `priority_classes`/`defer_classes`/`phase_classes` MUST normalise through the **same**
`taxonomy.normalize` the gate uses (`plan_gate.py:161`). Unknown ⇒ a compile **error** recorded in
`.errors[]` (loud at compile time), not a silent drop — a typo in a class name the operator paid for
should fail where they can see it.

**Stage 3 — EMIT `directive.json`** atomically (temp + `os.replace`, the `plan.py:32-44` pattern) at
the same site that writes `policy.md` (`policy.py:135-161`), so the machine artifact lands beside the
prose it is derived from:

```json
{"schema":1,"playbook_name":"full_coverage_vapt","playbook_version":"2.0",
 "source_sha256":"<sha256 of the yaml>","compiled_at":"iso8601",
 "priority_classes":["sqli","idor_bola"],"defer_classes":["sourcemap"],
 "phase_classes":{"A4_injection":["sqli","nosqli"]},
 "restriction_digest":{"no_destructive_ops":true,"no_persistence":true,"in_scope_only":true},
 "min_cells_per_class":8,"errors":[]}
```

**Stage 4 — LEDGER EFFECT (two, both advisory, both through the existing seam).**

1. **Claim order.** In `_claim_worklist` (`father.py:1191-1193`), `priority_classes` becomes
   `plan_classes + directive_classes`, deduped, preserving order. Today it is
   `self._plan_priority_classes()` alone. So the operator's set is a **baseline** the boss may reorder
   within but cannot escape. `defer_classes` maps to a **reverse** placement in `:ranked`, never a filter.
2. **Digest.** `render_plan_digest` (`plan.py:84-94`) prepends an `## OPERATOR DIRECTIVE` block *inside
   the same ≤1500-char budget* (`_DIGEST_CAP`, `plan.py:19`), so a directive costs the plan zero
   additional prompt bytes. The prompt is already ~95% static; this design adds no prompt bytes.

### D.2 THE INVARIANT — a playbook must not bypass the claim/verification model

> **I-DIRECTIVE.** For any directive `D` and any plan `P`, the row set returned by
> `claim_cells(priority_classes = plan_priority_classes(P) + priority_classes(D))` is **identical** to
> the row set returned by `claim_cells(priority_classes = plan_priority_classes(P))`. Only the
> `ORDER BY array_position(CAST(:ranked AS text[]), c.vuln_class)` argument differs.

This is the same property `_biased_priority` already documents — *"Changes ORDER only — the claim WHERE
clause is untouched, so a bad plan can never restrict what's claimable, only reorder it"*
(`service.py:1333-1336`) — extended from the boss's plan to the operator's playbook. It holds
**structurally, not by convention**, because:

- The `WHERE` clause of `claim_cells` (`service.py:1396-1402`) is a **compile-time constant**. A class
  list reaches SQL *only* as the bound `:ranked` array consumed by `array_position` inside `ORDER BY`
  (`service.py:1403`). There is no code path by which any class list becomes a `WHERE` term.
- **Explicitly forbidden in this design:** an `AND NOT (c.vuln_class = ANY(:deferred))` fragment.
  `defer_classes` is demotion-only. If an operator genuinely wants a class excluded, that is an
  `applicable=false` decision in `ledger/applicability.py` — code-reviewed, scope-bound, and outside
  this workstream.
- No directive field can set a cell state, attach evidence, or mint a cell. The directive has no write
  path into `ledger_cell` at all; it is read once per tick into a list of strings.
- Termination is untouched: the directive never enters `_is_complete` (`father.py:1817`), the Governor
  (`father.py:1825-1852`), or `_has_claimable` (`father.py:1851`).
- **Path safety:** `UserPlaybook.name` is `^[a-z0-9_]+$` (`schema.py:48`); `resolve_playbook_def`
  (`policy.py:85-100`) reads `definitions/<name>.yaml` under that pattern. The compile path reuses the
  same resolver and adds **no new filesystem reach**.
- **Binding:** the directive is inert unless the scan row carries the matching `playbook_name` /
  `playbook_version` (`api/schemas.py:147-148`, `db/models/tenant.py:19-20, 397-398`). A directive
  cannot be swapped mid-scan by anything other than the operator.
- **Unknown-key direction:** a playbook the engine does not understand is **rejected**, never
  partially applied.

**Explicitly rejected (would bypass the claim/verification model):** "playbook sets the worklist";
"playbook pre-claims cells"; "playbook skips phases"; "playbook marks cells `tested_clean`".
`skip_tools` stays documented-only exactly as `policy.py:81` already states — upgrading it is a
tool-availability gate, a different workstream.

### D.3 Buyer-visible outcome

Selecting `full_coverage_vapt` changes actual claim order (its 20 declared phases' classes reach the
ledger), the console shows a **Directive** panel (name, version, `source_sha256`, class counts, compile
errors), and an operator's typo'd class name or unknown restriction is a 422 at authoring time instead
of a silent no-op at scan time. Today: prose only.

### D.4 Flag

`SCANNER_PLAYBOOK_DIRECTIVE` (`scanner_playbook_directive: bool = False`). Off ⇒ no `directive.json` is
read, `priority_classes` stays `self._plan_priority_classes()` verbatim, no digest block is added, and
`extra="forbid"` is **not** applied (the seeder/API path is unchanged, so existing playbooks keep
loading).

---

## E. DELIVERABLE 4 — FAILURE SEMATICS

**Persistence points.** Three, unchanged in kind:
1. `self._plan` (in-memory, `Father`) — read by `_plan_priority_classes` (`father.py:1141-1143`).
2. `self._plan_digest` — read by `build_specs(..., plan_digest=…)` (`father.py:1885`, batch path `:1899`).
3. `/work/plan.json` — atomic temp + `os.replace` (`plan.py:32-44`), re-read at `scan_brief.py:274`.

All three are written at exactly one place: `father.py:1168-1170`, **after** `validate_plan` returned a
non-empty objectives list. **Invariant P: `plan.json` on disk is always gate-produced. No unvalidated or
partially-validated plan is ever persisted, on any path, at any time.**

| # | Failure mode | Detection site | Action | Persisted state | Flag-off behaviour |
|---|---|---|---|---|---|
| 1 | Planner SDK absent | `boss.py:67-68` → `execute_fn=None` | `propose_plan` → `None` (`boss.py:162-163`) | prior stands, not rewritten | identical (no tick) |
| 2 | API key absent | `boss.py:69-71` | `execute_fn=None` → `None` | prior stands | identical |
| 3 | Wall timeout | `asyncio.wait_for` (`boss.py:94`) | `TimeoutError` → `None` (`boss.py:173-174`) | prior stands | identical |
| 4 | **NEW** tick still in flight at next boundary | `_planner_harvest` | cancel task, discard reply, log `plan.tick{tick=dropped_inflight}` | prior stands byte-identical | n/a (flag off ⇒ no spawn) |
| 5 | Transport / 429 / 5xx | `Runner.run` raises | `except Exception` → `None` (`boss.py:173-174`) | prior stands | identical |
| 6 | `ChatCompletion response has no choices` | empty `final_output` → `str(… or "")` = `""` (`boss.py:95`) | `_parse_candidate("")` → `start<0` → `None` (`boss.py:139-141`) | prior stands | identical |
| 7 | Malformed JSON / prose-wrapped | `_parse_candidate` (`boss.py:143-145`) | `None` | prior stands | identical |
| 8 | `{}` or `objectives` not a list | `boss.py:146` / `plan_gate.py:41` | `None` / prior | prior stands | identical |
| 9 | Gate raises | `plan_gate.py:45-47` | log `plan_gate.failed`, `return prior` | prior stands **unchanged** | identical |
| 10 | **NEW** surface read error | `_sample_open` except (`father.py:1132-1134`) → `ok=False` | **quarantine** — skip merge entirely (S1) | prior stands **unchanged**; `plan.gate.quarantined` | identical |
| 11 | Gate kept nothing | `father.py:1166` | return | prior stands | identical |
| 12 | **NEW** stale version echo | S3 | discard delta | prior stands | n/a |
| 13 | **NEW** delta over cap | B.4 | excess **queued**, never refused | queued tail visible in `plan.json` | n/a |
| 14 | `/work` read-only / `OSError` | `write_plan` except (`plan.py:43-44`) | in-memory plan still set for this run | disk = prior; re-read at `scan_brief.py:274` yields the prior digest | identical |
| 15 | Objective names a concrete out-of-scope host | `_glob_host` + `in_scope` (`plan_gate.py:222-224`) | `rejected: out_of_scope`; prior objectives untouched | rejected objective visible with reason | identical |
| 16 | Objective has 0 claimable backing, `ok=True` | S6 | new → `rejected: no_surface`; prior → `retired: drained` | `backing.open_cells: 0` recorded | identical |
| 17 | Objective with no valid class | S5 | `rejected: no_valid_class` | recorded with reason | identical |
| 18 | **NEW** playbook compile fails | `compile_playbook_directive().errors[]` | log `playbook.directive_failed`; **directive treated as empty** → claim falls to `_CLASS_PRIORITY` | `directive.json` not written | identical (no read at all) |
| 19 | **NEW** playbook has unknown key | `extra="forbid"` ValidationError | HTTP 422 at create/update (`playbooks.py:100, 163`) — rejected at authoring time | never reaches a scan | identical (forbid off) |
| 20 | `playbook_name` not in `definitions/` | `resolve_playbook_def` → `{}` (`policy.py:90-100`) | empty view → core policy only | no `directive.json` | identical |
| 21 | Planner task cancelled at scan shutdown | loop `break` / `_wrap_up` | cancel in the wave-loop `finally` | `plan.json` = last-known-good | identical |
| 22 | Reconcile pass (§F4) raises | `except` in the reconcile wrapper | log, return | **no cell state changed** | identical (pass not invoked) |
| 23 | Rollup write-back (§F2) raises | `except` (`telemetry.py:305-307`) | log, return `0` | `worker_runs` untouched | identical |
| 24 | Proxy correlation header rejected by proxy | proxy-side | log; request proceeds | none | identical (header absent) |

**Byte-identity argument.** Every row's action is either "return `prior`" or "do not spawn". The only
writes to `self._plan` / `self._plan_digest` / `plan.json` occur at `father.py:1168-1170` after a gate
returned non-empty objectives. With all new flags OFF, `_planner_step` reduces to
`await self._boss_tick(brief)` — a single branch (`father.py:1787`) — so the diff is provably zero.

---

## F. TELEMETRY REPAIR — THE DECISION LAYER'S OWN BLINDNESS

### F.1 `resolved_count` — structurally 0 on every row

**Root cause (fully cited).** `WorkerResult.resolved_cells` is declared at `worker.py:20`. A repo-wide
grep for `resolved_cells` returns **exactly three** hits: that declaration, and two reads at
`telemetry.py:183` and `telemetry.py:201`. All eight `WorkerResult(...)` construction sites
(`fleet.py:61, 68, 111`; `runtimes/agents_runtime.py:752, 824, 865`; `runtimes/claude_sdk.py:156, 163`)
omit it. Therefore `telemetry.py:183` `len(getattr(result,"resolved_cells",[]) or [])` is always `0`,
`resolved_count` is written as `0` on all 987 rows, and `reporting/effort.py:64` publishes `0` to the
buyer via `api/schemas.py:609`.

**Fix — assign it from the ledger, not from the model's self-report.** Precedent: the father already
computes truth from disk rather than trusting the model (`_distinct_confirmed_count(self._work_dir)`,
`father.py:1800`). New `ledger/service.py`:

```sql
-- cells THIS worker's own claim resolved
SELECT count(*) FROM ledger_cell
WHERE scan_id = CAST(:sid AS uuid)
  AND claimed_by = :wid
  AND state IN ('confirmed','tested_clean','blocked');
```

Seam: the fleet on-done hook (`fleet.py:111`) already holds `spec.worker_id`. Set
`WorkerResult.resolved_cells` there — the single place every result passes through — before
`worker_finished` is invoked. Then add a scan-level rollup mirroring `rollup_findings_count`
(`telemetry.py:249-307`): write `SUM(resolved_count)` back into the synthetic `exploit-floor` row as the
un-attributed remainder.

- **Flag:** `SCANNER_TELEMETRY_RESOLVED_COUNT` (`scanner_telemetry_resolved_count: bool = False`).
- **Off ⇒** the field stays `0` exactly as today; `telemetry.py:182-194` unchanged.
- **Buyer-visible:** the per-worker "Resolved" column stops reading 0; "cells closed per worker"
  becomes a real KPI and the planner's `economics` block (§B.2) becomes steerable.

### F.2 `findings_count` — 139× over-report; the correction is computed then thrown away

**Root cause.** `telemetry.py:182` `findings = len(getattr(result,"findings",[]) or [])` is the worker's
**self-reported, pre-verification, pre-dedup** list — every emitted record including rejected and
placeholder ones. Sum over 987 rows = 35,934 vs 259 actual (WS-1/WS-2 measurement, relayed).

The corrective rollup already computes the truth and then discards it:

```
telemetry.py:263  total      = SELECT COUNT(*) FROM findings WHERE scan_id=:s        → 259
telemetry.py:273  attributed = SUM(findings_count) WHERE worker_id<>'exploit-floor'  → 35,934
telemetry.py:281  remainder  = total - attributed                                   → −35,675
telemetry.py:282  if remainder <= 0: return total      ← RETURNS 259, WRITES NOTHING
```

The per-worker rows are never corrected, and `reporting/effort.py:63` + `api/schemas.py:608` read the
per-worker rows. **The missing write is the entire bug.**

**Fix — make the rollup authoritative (write-back), in three steps, behind `SCANNER_TELEMETRY_FINDINGS_ATTRIB`:**

1. **Truth.** `verified := COUNT(*) FROM findings WHERE scan_id=:s AND <verified predicate>`. Note the
   existing `COUNT(*)` at `:263` is itself an over-count: `scanner_finalize_enrich` keeps soft-dedup
   losers in the table marked `evidence_paths["duplicate_of"]` (`config.py:391`), so the filter is
   required for the rollup to be *more* honest than the thing it replaces.
2. **Attribute.** The bridge already exists: `LedgerCell.finding_id` (`tenant.py:272`) links a cell to a
   finding (`service.py:919-923` sets it) and `LedgerCell.claimed_by` (`tenant.py:278`) records the
   worker. So
   `findings_count[w] := SELECT count(*) FROM ledger_cell c JOIN findings f ON f.finding_id = c.finding_id
   WHERE c.scan_id=:s AND c.claimed_by = w`.
3. **Write back.** Persist the per-worker value and route every un-attributed finding
   (floor / OOB / ZAP late-ingested, which belong to no `worker_run`) to the synthetic `exploit-floor`
   row — exactly what that row was built for (`telemetry.py:284-302`).

- **Flag:** `SCANNER_TELEMETRY_FINDINGS_ATTRIB` (`scanner_telemetry_findings_attrib: bool = False`).
- **Off ⇒** `worker_finished` still writes `len(result.findings)` and the rollup still short-circuits at
  `:282`. Byte-identical.
- **Buyer-visible:** the report/API findings number stops over-reporting 139×; the exploit-floor row
  becomes a real attribution bucket rather than a negative-number no-op.

### F.3 Proxy telemetry — 11.6% coverage, zero attribution

**Design — correlation headers, additive logging only.** The proxy is the `kali-exec` toolserver HTTP hop.
The agent side already knows `self._scan_id` and the tenant; the toolserver client must emit, on every
request to the toolserver, behind `SCANNER_PROXY_CORRELATION`:

```
X-Abhedi-Scan-Id:    <uuid>
X-Abhedi-Tenant-Id:  <uuid>
X-Abhedi-Worker-Id:  <worker_id>      -- per-TOOL attribution, which today exists only for LLM turns
```

The proxy access log records the same three fields. That is the whole change: no routing, no auth, no
body mutation, no header-dependent behaviour.

CP-side reconciliation then produces what is currently impossible:
`coverage_pct = COUNT(DISTINCT scan_id IN proxy_log) / COUNT(DISTINCT scan_id IN scans, window)` — the
missing denominator — plus per-scan and per-worker tool attribution for the console.

- **Security note (must be stated so nobody "optimises" onto it later):** these are opaque uuids, no
  PII, no secret, read-only for correlation. They must **never** become an authorization input; the
  existing per-scan token and `/work` path scoping stay authoritative.
- **Flag:** `SCANNER_PROXY_CORRELATION` (`scanner_proxy_correlation: bool = False`). Off ⇒ headers
  absent, proxy log format unchanged, byte-identical.

### F.4 `ledger.resolve.*_unmatched` — 12,734 durable, not a log line

**Root cause.** `resolve_cells` matches each reported `(endpoint, class)` against a **windowed** load;
`_match` returns `[]` unless `len(candidates) == 1` (`service.py:840-843`). On `[]` the caller increments
`counts["unmatched"]` and emits a `logger.warning` — `ledger.resolve.update_unmatched`
(`service.py:949`) or `finding_unmatched` (`service.py:873`) — and **discards the line**. `_norm` collapses
identity spellings, so a near-miss yields 0 candidates and is dropped rather than queued. 760 of the
12,734 carry placeholder endpoints (a known producer: the self-disclaimed placeholder reaped at
`tools/findings.py:107-111`).

**Design — a reconciliation pass, explicitly NOT a retry of `resolve_cells`.**
New `ledger/service.py::reconcile_unmatched(session, scan_id, *, cap=500)`, once per sync tick, behind
`SCANNER_LEDGER_UNMATCHED_RECONCILE`:

1. Re-read `findings.jsonl` + `ledger_updates.jsonl`; re-attempt **only** previously-failed
   `(endpoint, class)` keys, using a widened identity lookup (`_norm` + an alias/canonical map) instead
   of the bounded window. Bounded to `cap` keys/tick, oldest-first.
2. **Classify each key into a durable reason enum**, counted not merely logged:
   `no_such_cell` · `class_not_applicable` · `ambiguous` (`len(candidates) > 1`) ·
   `unparsed_class` (`normalize()` → `None`, `service.py:943-945`) · `placeholder_endpoint`.
3. **Act only where it is safe:** `no_such_cell` + a real in-scope endpoint ⇒ emit a `reconcile.cell_gap`
   signal the planner can read (this is the planner's real blind spot: work the engine performed that
   never became a cell). `class_not_applicable` ⇒ a coverage-QA fact (the applicability gate and the
   worker disagree). `placeholder_endpoint` ⇒ drop, already handled at `findings.py:111`.

**Why a receipt and not a counter.** The current signal is a structlog line with no scan-scoped durable
home: it cannot be trended, cannot be attributed to a worker, and cannot be fed to the planner.
`_reconcile_census` (`father.py:95-120`) already lifts `resolve_unmatched` into a first-class per-tick
number; the receipt table is what makes that number actionable.

**Safety:** a reconcile error logs and returns; it **never** touches a cell state it did not positively
match. It may only move `untested → testing`, via the same idempotency guard `resolve_cells` already
enforces at `service.py:964-969`. It can never confirm, close, or mark clean.

- **Flag:** `SCANNER_LEDGER_UNMATCHED_RECONCILE` (`scanner_ledger_unmatched_reconcile: bool = False`).
  Off ⇒ pass not invoked; `resolve_cells` behaviour and the log-line shape unchanged.
- **Buyer-visible:** `resolve_unmatched` trends to a floor instead of growing unbounded, and the buyer can
  be told "N classes your app does not expose" rather than having the work silently dropped.

### F.5 Plan telemetry — make OFF / broken / unreadable distinguishable

Today exactly one plan event exists, `plan.revised` (`father.py:1173-1176`), emitted **only on success**.
So a scan with a broken planner and a scan with no planner are indistinguishable in the DB.

New `plan.tick` event per tick: `{tick_n, wall_ms, bounded_by, snapshot_id, candidate_present,
parse_ok, gate_status ∈ {accepted, rejected, quarantined, no_candidate, stale, unreadable_surface},
objectives_active, objectives_rejected_by_reason, delta_size, source ∈ {boss, directive, both}}`.

- **Flag:** `SCANNER_ENGINE_PLAN_TELEMETRY` (`scanner_engine_plan_telemetry: bool = False`). Off ⇒ the
  only event remains `plan.revised` on success, byte-identical.

---

## G. FLIP TABLE

| # | Flag (env) | Settings field | Default | Byte-identical when OFF — because | Blast radius if wrong |
|---|---|---|---|---|---|
| 1 | `SCANNER_ENGINE_PLANNER_TICK` | `scanner_engine_planner_tick` | **False** | `_planner_step` falls through to `await self._boss_tick(brief)` — one branch at `father.py:1787`; delta path never constructed | Plan applied one tick late and off the critical path. Worst case: a stale bias for one wave (advisory only, `service.py:1332-1346`). **No termination, claim, or scope effect.** |
| 2 | `SCANNER_PLANNER_TICK_WALL_S` | — | 45 | env-only, read only inside the spawned task (absent when #1 is off) | Planner never completes → every tick `dropped_inflight` → prior plan stands forever. Degrades to flag #1's legacy behaviour only if #1 also off; otherwise to "plan frozen at version N". Watch `plan.tick.bounded_by`. |
| 3 | `SCANNER_PLANNER_MAX_TURNS` | — | 4 | as #2 | `max_turns_exceeded` on every tick → `parse_ok=False` → prior stands. Same as #2. |
| 4 | `SCANNER_PLANNER_MAX_TOOL_CALLS` | — | 2 | as #2 | Reply truncated → `parse_ok=False` → prior stands. Bounded, loud, harmless. |
| 5 | `SCANNER_PLANNER_MAX_DELTA` | — | 6 | as #2 | Excess objectives **queued**, never refused (`plan_gate.py:95-104`); plan just fills more slowly. |
| 6 | `SCANNER_PLANNER_MAX_TICKS` | — | 12 | as #2 | Planner latches after 12 ticks; claim reverts to `_CLASS_PRIORITY`. Safe by construction. |
| 7 | `SCANNER_PLANNER_COOLDOWN_S` | — | 60 | as #2 | Fewer plan revisions; no other effect. |
| 8 | `SCANNER_PLAN_GATE_V2` | `scanner_plan_gate_v2` | **False** | `validate_plan` keeps the `list` parameter; `SurfaceRead(cells, ok=True)` default reproduces today's `_count_backing` exactly | **Highest-value flag.** Wrong = objectives backed by attempt-capped/leased cells read `active`; or a transient DB error retires the whole plan. Mitigated by I1–I4 and by `plan.gate.quarantined` / `plan.tick.gate_status`. Bounded to claim ORDER either way. |
| 9 | `SCANNER_PLAYBOOK_DIRECTIVE` | `scanner_playbook_directive` | **False** | No `directive.json` read; `priority_classes` stays `self._plan_priority_classes()` verbatim; no digest block; `extra="forbid"` not applied | Claim order shifted by the operator's classes (advisory only, I-DIRECTIVE). If `extra="forbid"` shipped without the flag, existing playbooks 422 at authoring — **keep them separable**. |
| 10 | `SCANNER_TELEMETRY_RESOLVED_COUNT` | `scanner_telemetry_resolved_count` | **False** | `telemetry.py:182-194` untouched; field stays 0 | `resolved_count` over-reports (counts a worker's resolutions incl. later re-opened cells). Reporting-only; no steering. |
| 11 | `SCANNER_TELEMETRY_FINDINGS_ATTRIB` | `scanner_telemetry_findings_attrib` | **False** | `worker_finished` still writes `len(result.findings)`; rollup still short-circuits at `telemetry.py:282` | Under-report if the `finding_id` bridge misses rows → **buyer-visible findings number too low**. Mitigate with a `SUM(attributed) vs verified` reconciliation assert that refuses the write-back on mismatch. |
| 12 | `SCANNER_PROXY_CORRELATION` | `scanner_proxy_correlation` | **False** | No headers emitted; proxy log format unchanged | Extra headers only. Explicitly **not** an authz input. Log-format parsers downstream may need the fields declared optional. |
| 13 | `SCANNER_LEDGER_UNMATCHED_RECONCILE` | `scanner_ledger_unmatched_reconcile` | **False** | Pass not invoked; `resolve_cells` unchanged | Bounded by `cap`=500/tick and the idempotency guard (`service.py:964-969`); may only move `untested→testing`. Worst case: extra DB load on the sync tick, which is already the observed 7–15× cadence overshoot path (`father.py:1084-1092`). |
| 14 | `SCANNER_ENGINE_PLAN_TELEMETRY` | `scanner_engine_plan_telemetry` | **False** | Only `plan.revised` on success, as today | Event-volume growth only. No behaviour. |

**Rollout order (each independently revertible, none required by the next):**
14 → 13 → 11 → 10 → 9 → 8 → 1(+2…7) . Rationale: telemetry before the behaviour it explains; F1/F2 before
the planner that steers on them; the gate before the tick that feeds it.

---

## H. EVIDENCE LEDGER — claims about CURRENT behaviour

Confidence: **HIGH** = read directly at the cited line in this session · **MEDIUM** = read a
sibling-workstream evidence artefact or repo doc, not re-measured · **LOW** = inferred · **UNVERIFIED**.

| # | Claim | Source (type + location) | Conf. | Notes |
|---|---|---|---|---|
| H1 | Boss tick is awaited **inline** on the wave loop | [CODE] `engine/father.py:1787` `await self._boss_tick(brief)` | HIGH | Placed before plateau/complete/governor by design (`father.py:1784-1786`) |
| H2 | Only bound on the planner is `asyncio.wait_for(wall_s)`, default 180s | [CODE] `engine/boss.py:47` (`_wall_s()`→"180"), `:94` (`asyncio.wait_for(…, timeout=wall_s)`) | HIGH | No per-call, per-tool, or per-scan tick bound exists |
| H3 | Boss toolset is read-only (`read_file`/`grep`/`glob` only) | [CODE] `engine/boss.py:76` | HIGH | No `run_shell`/`write_file`/`browse` |
| H4 | `propose_plan` returns `None` on every failure and never raises | [CODE] `engine/boss.py:162-175` | HIGH | `except Exception` at `:173-174` |
| H5 | Empty model output → `None` (the "no choices" path) | [CODE] `engine/boss.py:95` (`str(getattr(result,"final_output","") or "")`), `:139-141` | HIGH | `start < 0` ⇒ `None` |
| H6 | PlanGate is already implemented, pure, wired, and merge-not-replace | [CODE] `engine/plan_gate.py` (236 lines); wired `engine/father.py:25, 1165` | HIGH | Not greenfield — extends the brief |
| H7 | Gate's `backing`/`rejected` are **gate-owned**; the boss cannot fake surface | [CODE] `engine/plan_gate.py:121-124, 167-171` | HIGH | `backing`/`rejected` deliberately not copied from input |
| H8 | Gate falls back to `prior` on any exception | [CODE] `engine/plan_gate.py:45-47` | HIGH | Correct shape — falls back to the last-validated artifact |
| H9 | **`_sample_open` returns `[]` on any exception** | [CODE] `engine/father.py:1129-1134` | HIGH | The load-bearing root of C.4 |
| H10 | `[]` ⇒ every new objective rejected **and every prior one retired** | [CODE] `engine/plan_gate.py:203-211` (`_count_backing`→0), `:226-234` (`_apply_rules`) | HIGH | Confirmed by reading both call paths |
| H11 | Retired objectives are never revived (terminal, filtered out of carry-forward) | [CODE] `engine/plan_gate.py:61` (`o.get("status") != "rejected"`), `:21` (`_TERMINAL = {"done","retired"}`) | HIGH | Makes the degradation **permanent** |
| H12 | Empty plan ⇒ empty digest and empty class bias ⇒ unrestricted `_CLASS_PRIORITY` | [CODE] `engine/plan.py:84-94, 97-108`; `ledger/service.py:1339-1340` | HIGH | The silent end-state |
| H13 | Backing source is a **200-row** window ordered by `_CLASS_PRIORITY` | [CODE] `engine/attack_surface.py:103` (`n: int = 200`); `ledger/service.py:1210-1224` (`.order_by(array_position(…)).limit(n)`) | HIGH | Ledger default is `n=15` (`service.py:1210`) but the father's surface wrapper passes 200 |
| H14 | The backing predicate ignores the attempt cap; `claim_cells` honours it | [CODE] `ledger/service.py:1210-1224` (no `attempts` term) vs `:1388-1392` (`AND c.attempts < :cap`) | HIGH | Backing can be 100% unclaimable |
| H15 | The backing predicate ignores live leases; `claim_cells` skips them | [CODE] `ledger/service.py:1210-1224` (no `claimed_by` term) vs `:1400` (`claimed_by IS NULL OR … lease_expires_at < now()`) | HIGH | Backing can be 100% currently-held |
| H16 | A claim-identical count already exists | [CODE] `ledger/service.py:1508-1521` (`count_claimable_cells`, applies `:cap`) | HIGH | C.3 mirrors it; the plan gate simply doesn't use it |
| H17 | Class priority reaches SQL **only** as `array_position` in `ORDER BY`; `WHERE` is constant | [CODE] `ledger/service.py:1396-1403` | HIGH | The structural basis of I-DIRECTIVE |
| H18 | `_biased_priority` is advisory-only by design | [CODE] `ledger/service.py:1332-1346` | HIGH | Quoted: "a bad plan can never restrict what's claimable, only reorder it". **Preserved, not removed.** |
| H19 | Claim is `SELECT … FOR UPDATE SKIP LOCKED` | [CODE] `ledger/service.py:1393-1417` | HIGH | Target selection is a ledger claim, not a prompt decision |
| H20 | `_WORKLIST_MAX = 12` hard cap per worker per wave | [CODE] `engine/father.py:173`; used by `_claim_limit` `:1136-1139` (`fanout × 12`) | HIGH | |
| H21 | `resolved_cells` has exactly 3 occurrences repo-wide: 1 declaration, 2 reads | [CODE] `engine/worker.py:20`; `engine/telemetry.py:183, 201` | HIGH | Zero assignments ⇒ `resolved_count` ≡ 0 |
| H22 | All 8 `WorkerResult(...)` sites omit `resolved_cells` | [CODE] `fleet.py:61, 68, 111`; `runtimes/agents_runtime.py:752, 824, 865`; `runtimes/claude_sdk.py:156, 163` | HIGH | |
| H23 | `resolved_count` is published to the buyer | [CODE] `reporting/effort.py:64`; `api/schemas.py:609`; column `db/models/tenant.py:158` | HIGH | Reads 0 ⇒ reports 0 |
| H24 | `findings_count` is worker self-report, pre-verification | [CODE] `engine/telemetry.py:182` | HIGH | |
| H25 | The rollup computes the truth then **discards it** when `remainder ≤ 0` | [CODE] `engine/telemetry.py:263, 273, 281, 282` | HIGH | `return total` with **no** write-back — the missing write |
| H26 | Consumer reads the **per-worker** rows, not the rollup's return value | [CODE] `reporting/effort.py:63`; `api/schemas.py:608` | HIGH | Why the 139× survives the rollup |
| H27 | The `COUNT(*)` "truth" is itself an over-count | [CODE] `engine/telemetry.py:263` (bare `COUNT(*)`) vs `config.py:391` ("soft-dedup loser row STAYS in the DB") | HIGH | F.2 must add the verified predicate |
| H28 | `LedgerCell.finding_id` + `claimed_by` are the worker→finding attribution bridge | [CODE] `db/models/tenant.py:272, 278`; set at `ledger/service.py:919-923` | HIGH | No worker column on `Finding` (`tenant.py:85-126`) |
| H29 | Unmatched keys are **logged and dropped**, never queued | [CODE] `ledger/service.py:840-843` (`_match` returns `[]` unless exactly 1), `:873`, `:949` | HIGH | The 12,734 accumulate with no durable home |
| H30 | `_reconcile_census` already lifts `resolve_unmatched` to a first-class per-tick number | [CODE] `engine/father.py:95-120` | HIGH | F.4 makes it actionable |
| H31 | `unmatched` is also counted at two parse-failure sites | [CODE] `ledger/service.py:862-868` (`finding_incomplete`), `:939-945` (`update_incomplete`, `normalize()`→None) | HIGH | Feeds the F.4 reason enum |
| H32 | Playbook projection discards `tools`, `goal`, most of `behavior`, all of `blocker_handling` | [CODE] `engine/policy.py:103-121` (reads `p["name"]` only; 2 behavior fields) | HIGH | |
| H33 | **No `vuln_class` field exists in either playbook schema** | [CODE] `playbooks/schema.py:9-55`; `playbooks/loader.py:9-47` | HIGH | Root of the "playbooks are prose" finding |
| H34 | The only playbook→engine behaviour is a hardcoded frozenset → 150 invocations | [CODE] `agent_runtime/entrypoint.py:97-119` | HIGH | Not derived from the playbook |
| H35 | Two mutually incompatible playbook schemas coexist | [CODE] `playbooks/schema.py:9-55` (goal/restrictions/behavior/blocker_handling) vs `playbooks/loader.py:9-47` (defaults/phases[].tasks) | HIGH | `policy.py:104-107` documents it must tolerate both |
| H36 | Unknown playbook keys are silently dropped (Pydantic default) | [CODE] `playbooks/schema.py:9-13` lacks `no_persistence`/`in_scope_only`; shipped YAML declares both at `playbooks/deep_offensive_vapt.yaml:11-14` | HIGH | Authoring already 422s on ValidationError (`api/routes/playbooks.py:96-100, 159-163`), so `extra="forbid"` has a live handler |
| H37 | `skip_tools` is already documented as NOT code-enforced | [CODE] `engine/policy.py:81` | HIGH | Not upgraded here (out of scope) |
| H38 | `deep_offensive_vapt.yaml` (repo root) is an orphan | [CODE] dir listing of `playbooks/` vs `src/scanner/playbooks/definitions/`; grep finds no reference to `deep_offensive_vapt` in any `.py` | HIGH | `resolve_playbook_def("deep_offensive_vapt")` → `{}` (`policy.py:90-100`) |
| H39 | Live env runs the decision layer **ON**, contradicting the docs | [QUERY] osprey evidence `ws1_ws2_telemetry.md:23,32` (`SCANNER_ENGINE_BOSS=true`, `SCANNER_ENGINE_PLAYBOOK=true`) vs [CODE] `docs/context/CAPABILITIES.md:37`, `docs/context/FLAGS.md:123` (both "OFF") | MEDIUM | Sibling-workstream capture (2026-09-30), read not re-run (R4). **This is the single most important item to reconcile before shipping anything here.** |
| H40 | Live HTTP timeout 300s / retries 8 vs boss wall 180s | [QUERY] osprey evidence `:33` | MEDIUM | One upstream call can consume the entire planner budget |
| H41 | Live `SCANNER_ENGINE_BATCH_MAX_CELLS` is 8, brief states 6 | [QUERY] osprey evidence `:17` vs brief | LOW | Not load-bearing for this design; noted for the config-truth-table owner |
| H42 | Live `SCANNER_LEDGER_ATTEMPT_CAP=6` (code default 3) | [QUERY] osprey evidence `:20` | MEDIUM | Raises the H14/H15 severity: 6 capped claims per cell before terminal `attempted` |
| H43 | `findings_count` over-reports 139× (35,934 vs 259); `resolved_count` ≡ 0 across 987 rows; 12,734 unmatched | brief-relayed (WS-1/WS-2) | MEDIUM | Not re-measured (R4); the **mechanism** is independently confirmed at H24–H29, so the fix does not depend on the exact ratio |
| H44 | `max_turns_exceeded` on 63/63 recorded turns; 950/1,019 error lines; 429s on 24/27 logs | brief-relayed (WS-1) | MEDIUM | Used only to justify the *direction* of the turn/tool-call caps in B.4 |
| H45 | WS-2's anti-fabrication fail-open is `run.py:109 → service.py:159-161 → registry.py:158` | brief-relayed; I read `run.py:105-114`, which shows the same **shape** (`except Exception: pass` degrading a gate to a permissive default) | MEDIUM | The *pattern* is independently confirmed at `engine/father.py:1129-1134 → plan_gate.py:203-211` (H9/H10), which is what C.4 fixes. Exact WS-2 line numbers not re-verified. |

---

## I. DO-NOT-BUILD — confirmed, none proposed

Recursive agent hierarchies · generation-counter / freeze · agent-to-agent messaging via chat ·
pgvector semantic memory · ZAP as a core detector · intercepting proxy as a coordination substrate.
None appears in this spec. The proxy work in F.3 is **read-only correlation logging**, explicitly not a
coordination substrate, and carries a written prohibition on becoming an authz input.

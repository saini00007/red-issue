Verified everything against code. Writing the deliverable.

---

# WS-5 — Intelligence Layer (Bounded Per-Tick Planner): Design Section

*Design-only. READ-ONLY audit. Branch `feat/alpha-observability`, HEAD f75608f. Every mechanism below is a **delta on machinery that already exists** — WS-5 is a harvest-and-wire, not a build. All deltas ride the existing `scanner_engine_boss` flag (default OFF), so a stock deploy stays byte-identical.*

---

## 1. H2 verdict + current-state recap

**H2 verdict: REFINED (confirmed-in-part, refuted-in-part) — CONFIDENCE HIGH.** The claim "worker prompts are static, no per-tick planning exists" is *true for the system prompt only* and *false as a whole*. Three layers, three natures: the **system prompt is a static constant** (`methodology.py:13-251` DEEP_OFFENSIVE_VAPT, only the OOB token varies — `agents_runtime.py:917-940`) [CODE]; the **per-wave task and reprompt are state-aware but deterministic template assembly**, hydrated each wave from live ledger/brief/coverage (`father.py:597-633`, `agents_runtime.py:962-994`) [CODE]; and a **real bounded LLM planner — the Phase-2 boss — is genuinely wired into the live engine-v2 wave loop** (`run.py:285` → `father.py:1787` `_boss_tick`) but self-skips because `scanner_engine_boss` defaults `False` and is unpinned in compose (`config.py:415-417`, `father.py:1156`) [CODE].

**Two-line recap.** Per-tick decisioning in a stock deploy is *entirely deterministic*: `Governor.decide` (stop/partial/continue) + a code-computed plateau + a quiescence guard + a SKIP-LOCKED ledger claim (`father.py:1789-1852`, `governor.py:32-48`) [CODE]. A complete, validated, fail-safe dynamic planner (`boss.py` / `plan.py` / `plan_gate.py` / `policy.py`) already sits in the live loop but ships dark — so **WS-5's job is to turn it on correctly and close three input/telemetry gaps, not to author a new intelligence layer.**

---

## 2. Bounded per-tick planner contract

The contract already has a schema in code (`plan_gate._sanitize_objective:121-155`, `_BOSS_ROLE:33-43`). WS-5 **adopts it verbatim** and pins the bounds — no schema extension needed.

**INPUT (per wave-tick, assembled just after `write_scan_brief`, `father.py:1781`):**
- `brief` — live shared brief (already passed) [CODE `run.py:260`]
- `board_totals` — the live coverage board `_render_board_totals(coverage_counts())` (per-state cell census: open / applicable / attempted / resolved, by class) — *computed already at `father.py:1194`, currently NOT forwarded to the boss* [CODE, gap]
- `coverage_qa` — a small deterministic **progress-delta digest** (this-wave: cells closed, new distinct confirmed findings, classes with open-but-untouched cells) — *defined as a boss input (`boss.py:126`) but never produced anywhere* [CODE, gap]
- `current_plan` — prior gated plan (already passed) [CODE `run.py:261`]
- `policy` — assembled `policy.md` (playbook phases/aggression/restrictions) — *written at boot (`policy.py:135`) but never forwarded to the live boss* [CODE, gap]

**OUTPUT — a *validated plan delta*, never free-form prose.** The boss emits a candidate `plan.json`; `validate_plan` returns the merged, gated plan. The **objective schema** (the atom of the delta), as enforced today:

| field | type / bound | source |
|---|---|---|
| `id` | str, required (merge key) | `_sanitize_objective:127` |
| `kind` | `exploit`\|`recon`\|`verify` (else→`exploit`) | `:136`, `_KINDS:20` |
| `classes[]` | taxonomy-normalized vuln classes | `_norm_classes:158` |
| `endpoint_glob` | str glob or null (claim filter) | `:138` |
| `priority` | int (low = high priority) | `:131` |
| `rationale` | str ≤200 chars (display/next-tick feedback) | `_RATIONALE_CAP:22` |
| `status` | gate-computed `active`/`retired`/`rejected`/`queued`; boss may only set terminal `done`/`retired` | `:153`, `_apply_rules:214` |
| `parent_objective` | str ≤64 (lineage; NOT a spawn channel — see §Gaps) | `:144` |
| `spawn_hint{count,tier}` | count 0-8, tier ≤16 chars (advisory) | `_SPAWN_COUNT_CAP:23` |
| `backing{open_cells}` | **gate-owned, boss cannot fake** | `_reject:170`, `_apply_rules:227` |

**Bound (pin these; all already present or one-line):** ≤10 **active** objectives/tick (`validate_plan max_active=10:36`, overflow→`queued` not refused, `_enforce_active_cap:95`); `spawn_hint.count` ≤8; boss call bounded **max_turns 8 / wall 180 s** (`boss.py:46-51`, `SCANNER_ENGINE_BOSS_WALL_S`/`_MAX_TURNS`); prompt sections verbatim-capped 4000 chars each (`_MAX_SECTION:100`); plan digest ≤1500 chars into the brief+task prefix (`plan.py:19`). CONFIDENCE HIGH.

**Hook point:** `father.py:1787` `await self._boss_tick(brief)` — deliberately placed *before* the plateau/`_is_complete`/`governor`/quiescence checks (`:1789-1852`) so **the plan only orders/filters existing work; termination is untouched** [CODE `:1782-1786` comment + verified control flow].

---

## 3. Deterministic plan GATE — the keystone (already built)

**"LLM proposes, ledger disposes."** An objective materializes as `active` **only if it maps to real open, applicable, in-scope ledger cells** — this predicate already exists as `plan_gate._apply_rules:214-236` [CODE], recomputed over the LIVE surface every tick (`:88-89`):

**Gate predicate (per objective, per tick):**
1. **Rule 4 — class:** `obj.classes` non-empty after taxonomy-normalize, else `rejected: no_valid_class` (`:219`).
2. **Rule 3 — scope:** if `endpoint_glob` names a *concrete* host, it must pass `in_scope(scope, host)`, else `rejected: out_of_scope` (`_glob_host:173` + `:222-225`). Fuzzy/path-only globs fall through to Rule 2, which can only ever match in-scope-materialized cells — so scope cannot leak (`:177-179`).
3. **Rule 2 — surface (the keystone):** `n = _count_backing(obj, open_cells)` where `open_cells` = `_sample_open()` output (already applicable + open, `father.py:1165`). `n == 0` and **new** → `rejected: no_surface` (fed back to next boss prompt); `n == 0` and **previously had surface** → auto-`retired`; `n > 0` → `active`, `backing.open_cells = n` (`_count_backing:203`, `:226-235`) [CODE].

The gate **never mints cells, widens scope, or keeps a dead scan alive** (`plan_gate.py:1-4` docstring, verified by absence of any DB-write / scope-mutation in the module). It runs synchronously inside `_boss_tick` (`father.py:1165`), never raises (`:45-47`). The gated plan then feeds only two execution seams: the **claim-order bias** (`_plan_priority_classes:1141` → `claim_cells(priority_classes=…)`, `:1192`) and the **advisory task prefix** (`plan_digest` → `build_specs:1885`) — never `guard_tool_call`. CONFIDENCE HIGH.

*Note the one known ceiling (`_count_backing:206-208` ponytail comment): backing is counted against the `_sample_open` window, not a filtered `COUNT(*)`. Only upgrade to a ledger `count_claimable_cells`-style filtered count if a large frozen grid starves valid objectives past the sample window — otherwise leave it. [CODE]*

---

## 4. Operator playbooks → directives the planner obeys

Today the fleet ignores playbooks (memory note, confirmed: the live `_boss_fn` at `run.py:260-261` passes only `brief`+`current_plan`, so `policy` renders `(none)` — `boss.py:123`) [CODE]. The **conversion machinery already exists and is inert-until-consumed**:

`write_policy_file` (`policy.py:135`) resolves `PLAYBOOK_NAME` → `resolve_playbook_def` → `playbook_policy_view` (`:103-121`), projecting the playbook YAML onto **phases, aggression ceiling (rate/WAF backoff), restrictions, skip_tools** into `policy.md`. `playbook_consume_enabled()` (`:124-132`) already flips ON under `scanner_engine_boss`. The **only missing wire** is forwarding that `policy.md` into the boss prompt — which `build_boss_prompt` already accepts as its `policy=` param (`boss.py:114,123`) [CODE].

**Design:** a playbook becomes planner directives by flowing `policy.md` → boss prompt POLICY section. The boss reads phases/aggression/restrictions as **weights on objective priority and class selection**; the deterministic gate still bounds every objective to real in-scope cells (§3). Hard limits (scope, crime-line, rate) stay code-enforced — the playbook is *advisory to the planner, non-overridable to the guard* (`policy.py:73` "Aggression ceiling (ADVISORY — hard limits stay code)"). This is **Delta Ticket DT-1** below; no new mechanism, one param wire. CONFIDENCE HIGH.

---

## 5. Failure semantics — prior plan stands, byte-identical when off

The fail-safe chain is already complete and verified [CODE]:

- **Flag off / no boss_fn:** `_boss_tick` returns immediately (`father.py:1156`) → `self._plan` stays `{}` → `plan_priority_classes → []` (deterministic `_CLASS_PRIORITY` default) → `_plan_prefix → ""`. Byte-for-byte today.
- **Boss raises / times out / SDK-key absent / empty / malformed:** `propose_plan → None` (`boss.py:162,173-175`) → `_boss_tick` returns, **prior plan stands** (`father.py:1163`).
- **Gate rejects everything:** `validate_plan` returns prior (Rule 6, `plan_gate.py:38-47`); `_boss_tick` keeps prior if no active objectives (`father.py:1166`).
- **Termination is never touched:** the plan sets only `self._plan`/`_plan_digest`; the plateau/`_is_complete`/governor/quiescence breaks run *after* the tick and evaluate identically (`father.py:1782-1852` comment + verified flow).

**Invariant for WS-5:** every delta below preserves this — when `scanner_engine_boss=False`, no new code path executes, and any planner hiccup degrades to the prior plan, never to a broken wave loop. CONFIDENCE HIGH.

---

## 6. Delta tickets (mechanism → module/flag/state → buyer outcome)

All ride the **existing `scanner_engine_boss`** flag (default OFF, unpinned in compose — see the compose-pin note in DT-4). No new detector, no new orchestrator, nothing on the D6 do-not-build list.

**DT-1 — Feed the boss its designed inputs (fixes the LOW "starved planner" defect).**
Mechanism: in the live `_boss_fn` (`run.py:254-261`), pass `board_totals` (live coverage census, already computed at `father.py:1194`), `coverage_qa` (from DT-2), and `policy` (`policy.md` from `policy.py:135`) into `propose_plan` — `build_boss_prompt` already accepts all three (`boss.py:114`).
State/flag: `scanner_engine_boss` (existing); off → unchanged.
Buyer outcome: the planner re-prioritizes against the actual coverage board and the operator's playbook, not the brief digest alone — playbook aggression/phases become obeyed weights (delivers §4).

**DT-2 — Produce the `coverage_qa` progress-delta digest.**
Mechanism: one deterministic function computing this-wave deltas (cells closed, new distinct confirmed findings via existing `_distinct_confirmed_count`, classes with open-but-untouched cells) from the ledger census the loop already reads (`father.py:1793-1800`). Pure, ≤4000-char capped, fail-safe to `""`.
State/flag: consumed only under `scanner_engine_boss`; written inert otherwise (mirror `policy.py` "always-write, inert-until-consumed").
Buyer outcome: the planner reprioritizes on *momentum* (which classes are stalling) — the input its own prompt section was designed for but never got.

**DT-3 — Persist a per-wave decision/reasoning log (buyer-proof standard).**
Mechanism: extend the existing `plan.revised` recorder event (`father.py:1171-1176`) and `governor_decision` telemetry (`:1842-1843`) into a durable per-wave record: {governor decision + inputs, plan objectives + backing counts + rejections-with-reason}. No new store — reuse the recorder.
State/flag: `scanner_engine_boss` (planner side) + existing recorder; off → only today's telemetry.
Buyer outcome: an inspectable "why the fleet continued/stopped and what it prioritized each wave" log — matches the competitor buyer standard of a decision/reasoning trail per finding/wave.

**DT-4 — Compose pin for the flag (drift guard, not behavior).**
Mechanism: when DT-1..3 are validated and the flag is intended ON for a profile, add an explicit `SCANNER_ENGINE_BOSS:-false` pin to `docker-compose.yml` (currently unpinned — `[QUERY] grep SCANNER_ENGINE_BOSS docker-compose.yml → no match`). Until then it stays code-default OFF.
State/flag: config/compose only.
Buyer outcome: no silent divergence between bare-process and compose deploys when the default is eventually flipped.

**Out of scope per D6 (noted, NOT proposed):** per-worker dynamic objective assignment via an agent hierarchy or agent-to-agent chat, and an LLM-in-the-loop chaining strategy. The gap ("boss can only bias global claim order + one shared prefix, cannot say 'worker X → objective Y'") is real (`father.py:1868-1875` round-robin fan-out) — but the lazy in-substrate path is to let an objective's `endpoint_glob` act as a claim filter through the **existing** `scanner_engine_batch_dispatch` endpoint-scoped batching (`father.py:1898`), giving per-objective work partitioning with no hierarchy. Chaining stays the deterministic capability-graph floor's job (`chain/floor.py`), disjoint from the planner. Propose either only on NEW evidence per D6. CONFIDENCE MEDIUM (batch-dispatch reuse), HIGH (everything else).
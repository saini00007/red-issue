# WS-5 — Intelligence / Decision Layer Design (research-agent-viper-01)

Sources: A (boss.py, plan_gate.py, father.py:_boss_tick/_plan_prefix/_claim bias, worker.py _TUNING_KEYS).

## As-built (code-verified)
- `boss.py`: bounded per-tick planner (read-only tools, max_turns 8, wall 180s; failure/None ⇒ prior plan stands). Default OFF (config.py:415-417).
- `plan_gate.py` validate_plan: merge-not-replace by objective id (lines 57-92); Rule 1 active-cap 10 (95-105); Rule 2 backing = count of matching cells in the open-cell SAMPLE (203-211 — sample window, ponytail notes the COUNT(*) upgrade); Rule 3 glob-host scope check (173-186, 222-225); Rule 4 class normalization (158-164, 219-221); terminal statuses boss-owned (153-155).
- Consumption: plan reorders claim priority only (`_biased_priority`, service.py:1332-1346) + REQUIRED prefix in worker task (father.py:296-307). Termination untouched (boss only orders existing work).
- Politically LOAD-BEARING: plan is untrusted data; never reaches guard_tool_call (boss.py docstring).

## Gaps
1. Backing check uses a 15-row sample (father.py:1775 → `_sample_open` default n=15, service.py:1210) ⇒ real objectives can be rejected `no_surface` spuriously on a large grid.
2. No persistence of objective→outcome attribution (plan.revised events emitted, but no per-objective 'cells closed' measurement), so the boss can't learn what worked within the run.
3. Playbook→directive path exists (scanner_engine_playbook) as injected document text — advisory prose, not gate-validated objectives.

## Proposed deltas (module-level, flag-gated)
1. **Full-census backing** — `plan_gate._count_backing` → SQL COUNT over open+applicable cells (`count_claimable_cells`-style with class filter + endpoint glob → `ILIKE`/fnmatch in SQL), flag `SCANNER_PLAN_CENSUS_BACKING`. Buyer: plan stops ignoring real surface; fewer 2-hour wanders.
2. **Playbook→objectives compiler** — `engine/playbook_compile.py`: deterministic parse of operator playbooks into PLAN objectives (kind/classes/glob/priority) merged through the SAME `validate_plan`; flag `SCANNER_ENGINE_PLAYBOOK_PLAN`. Buyer: documented RoE/playbooks actually steer work order.
3. **Objective telemetry** — persist per-objective counters (`objective_progress` rows or scan_events) so father can drop objectives with zero conversion for N ticks and the report can say "objective X → cells n/m → findings F". Buyer: auditable plan→proof traceability.
4. **Failure semantics (kept)** — planner down/timeout/invalid ⇒ prior plan stands byte-identical (already the rule: plan_gate.py:38-47, boss.py). Keep this as the contract; add a `plan.stale_after_s` TTL so a dead boss doesn't eternally order work on a stale map.
5. **Prefilter for H2** — extend claim bias beyond class-rank with objective-backed cell ids (claim first the exact backing cells of active objectives), not just class order.

Bounded planner contract stays exactly: input = {brief, coverage board, prior plan}; output = candidate plan.json; gate validates; prior stands on any failure.

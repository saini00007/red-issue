# WS-5 · Intelligence / decision-layer design (no payloads)

H2 verdict: REFUTED-as-stated — tasks already inject cells/brief/capctx/board/plan (father.py:597-675),
reprompts are stateful with offensive gate (agents_runtime.py:800-838). The decision layer is BUILT but OFF:
_boss_tick (father.py:1145-1177) + plan_gate.validate_plan + claim bias via _plan_priority_classes
(father.py:1191-1192) + 2 operator playbooks (playbooks/*.yaml).

## Bounded per-tick planner contract
- Placement: _boss_tick call site (father.py:1782-1787), once per wave, BEFORE plateau/complete/quiescence.
- Input (read-only): brief + coverage_counts + attempts histogram + floor-signals-drained count + stuck list +
prior plan (all already available at the call site).
- Output: plan delta = {priority_classes[] (claim bias), group_focus order, waves_hint} — orders/filters
existing deterministic work only; plan is UNTRUSTED (prompts + claim order, never guard_tool_call).
- Bound: wall-clock cap + candidate-None on timeout (existing semantics, father.py:1159-1164).

## Deterministic plan gate
- Extend plan_gate.validate_plan: an objective materializes ONLY if it maps to ≥1 open + applicable +
in-scope cell (reuse count_claimable_cells predicate shape: applicable + state in (untested,testing) +
attempts<cap, service.py:1508-1521). Gate is sync, never raises (existing contract).

## Playbooks → directives
- Parse playbooks/deep_offensive_vapt.yaml + full_coverage_vapt.yaml at Father init into
{directive: weight} → claim-bias classes + phase-group fanout weights. Operator edits YAML; engine obeys via
the same _plan_priority_classes seam. Unknown keys ignored (fail-closed to current behavior).

## Failure semantics (already byte-identical; keep)
- Boss None/exception/empty-gate → prior plan stands (father.py:1160-1167); termination untouched
(father.py:1152-1153); flag scanner_engine_boss default OFF → no-op. D6 items (recursive hierarchies,
agent-chat messaging, pgvector memory) NOT proposed.

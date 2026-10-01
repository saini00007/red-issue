# WS-5 · Intelligence & Decision Layer Architecture Design

## Executive Summary & Design Constraints
* **Constraint Compliance (R1, D3, D5):** Systems architecture design. Engine-v2 remains the sole orchestrator. Planner operates as an advisory decision layer on a strict per-tick boundary.
* **Core Problem Identified (H2 Partial):** Workers currently spin up with largely static phase-group prompts (`father.py:48-85`). While `scanner_engine_boss` exists in code (`plan.py`, `plan_gate.py`), it is disabled by default in production. Furthermore, operator playbooks in `playbooks/` are static YAML files that merely set global target lists and timeouts, rather than dynamic operational directives that guide tactical target prioritization.

---

## 1. Bounded Per-Tick Planner Contract

```
+-----------------------------------------------------------------------------------+
|                              FATHER WAVE TICK BOUNDARY                            |
|  1. Refreshes Inventory & Materializes Surface                                   |
|  2. Synchronizes Workdir -> PostgreSQL Ledger                                     |
|  3. Prepares Scan Brief (/work/scan_brief.md)                                     |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         BOUNDED PLANNER INPUT ENVELOPE                            |
|  - Open Ledger Cells: Top open cells by vulnerability class                       |
|  - Confirmed Primitives: Evidenced findings and granted capability tokens         |
|  - Stalled Cells: Cells with attempts >= 1 and zero state advancement             |
|  - Operator Playbook Directives: Explicit target priority tags & exclusions       |
|  - Hard Constraints: Max execution time 15.0s, read-only tools, no live attacks   |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         PLANNER EXECUTION INFERENCE (LLM)                         |
|  Invokes: Boss Model (bounded single-turn completion)                             |
|  Prompt: Prior Plan Digest + Live Attack Surface Snapshot + Playbook Directives   |
|  Output: Candidate Plan Delta JSON (`candidate_plan.json`)                        |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           DETERMINISTIC PLAN GATE (CODE)                          |
|  Module: scanner.agent_runtime.engine.plan_gate.validate_plan                     |
|  Validates against: ScopeConfig, Live Open Cells, Attempts Cap                    |
|  Merges: Merge-not-replace against prior accepted plan                            |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         ACCEPTED PLAN DEPLOYMENT SINK                             |
|  1. Writes /work/plan.json atomically                                             |
|  2. Renders plan_digest into Worker task prefix                                   |
|  3. Injects priority_classes into `claim_cells(priority_classes=...)`             |
+-----------------------------------------------------------------------------------+
```

### Planner I/O Contract Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CandidatePlanDelta",
  "type": "object",
  "required": ["version", "rationale_summary", "objectives"],
  "properties": {
    "version": { "type": "integer" },
    "rationale_summary": { "type": "string", "maxLength": 500 },
    "objectives": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "kind", "priority", "target_glob", "vuln_classes", "directive"],
        "properties": {
          "id": { "type": "string" },
          "kind": { "type": "string", "enum": ["recon", "exploit", "verify", "pivot"] },
          "priority": { "type": "integer", "minimum": 1, "maximum": 100 },
          "target_glob": { "type": "string" },
          "vuln_classes": { "type": "array", "items": { "type": "string" } },
          "directive": { "type": "string", "maxLength": 250 },
          "parent_objective_id": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 2. Deterministic Plan Gate

The Deterministic Plan Gate (`plan_gate.py`) acts as a non-bypassable firewall between the LLM planner and execution dispatch. An objective proposed by the planner **only materializes if all four criteria are strictly met**:

1. **In-Scope Boundary Enforcement:**
   `in_scope(objective.target_glob, scope_config) == True`. Any target outside customer authorization is immediately dropped.
2. **Backing Cell Existence:**
   The objective's `(target_glob, vuln_classes)` tuple must intersect with at least one **real, applicable, open cell** in `tenant.ledger_cell` where `state IN ('untested', 'testing')` and `attempts < attempt_cap`. A hallucinated endpoint or retired class is refused.
3. **Budget & Active Objective Cap:**
   Enforces `max_active = 10` objectives. If the planner proposes 25 objectives, the top 10 by priority score are activated; the remaining 15 are placed in a persistent queue, preventing prompt bloat.
4. **Merge-Not-Replace Semantics:**
   Candidate objectives update existing objectives matching on `id`. Unmentioned active objectives are preserved; unconfirmed deletions are ignored.

---

## 3. How Operator Playbooks Become Directives the Engine Obeys

Currently, playbooks in `playbooks/full_coverage_vapt.yaml` define static timeouts and mode names. To turn playbooks into living operational directives:

1. **Playbook Directive Manifest:**
   Playbooks declare priority rules and tactical phases:
   ```yaml
   name: api_first_b2b_saas
   version: "2.1"
   directives:
     - phase: initial_recon
       focus_surface: ["/api/*", "/graphql", "/oauth/*"]
       deprioritize_surface: ["/static/*", "/docs/*"]
     - phase: business_logic_gate
       require_credentials: 2
       prioritize_classes: [idor_bola, mass_assignment, priv_esc]
     - tactical_rules:
       - condition: "new_capability(authenticated_session)"
         action: "spawn_authed_recrawl_and_prioritize(bfla, idor_bola)"
   ```
2. **Deterministic Translation Layer:**
   When Father starts a wave, `PlaybookEngine.compile_directives()` parses the active playbook rules against current scan progress and generates an initial **Objective Seed**.
3. **Claim Bias Enforcement:**
   The playbook objectives directly feed `father.py:1192` `surf.claim_cells(priority_classes=...)`. The SQL CTE `ORDER BY array_position(CAST(:ranked AS text[]), c.vuln_class)` physically locks and dispatches cells matching the operator playbook ahead of general fuzzing.

---

## 4. Failure Semantics & Graceful Degradation

The planning engine enforces fail-safe failure semantics:
* **Planner Down / Timeout / Out of Budget:**
  If the LLM call to the boss model fails, times out (>15s), or returns malformed JSON, the candidate plan is dropped (`candidate = None`).
* **Prior Plan Stands:**
  `validate_plan(candidate=None, prior=self._plan)` immediately returns `self._plan` without modification.
* **No Prior Plan (Scan Start):**
  Returns `_empty_plan()`. The engine falls back to default round-robin deterministic order (`_CLASS_PRIORITY`), producing byte-identical execution to production without the planner.
* **Zero Halts:** The Father never blocks a wave loop on planner failure.

---

## WS-5 Evidence Ledger

| Claim | Source (type + location) | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| PlanGate implements merge-not-replace and never raises on candidate error | [CODE] `src/scanner/agent_runtime/engine/plan_gate.py:30-48` | HIGH | Pure code validator; returns prior plan on error. |
| Boss planner tick is wired in Father but gated behind `scanner_engine_boss` | [CODE] `src/scanner/agent_runtime/engine/father.py:1145-1177` | HIGH | Gated default OFF; inert in current production deploy. |
| Plan priority classes advisorily bias SQL claim order via `array_position` | [CODE] `src/scanner/ledger/service.py:1378-1403`, `plan.py:97-100` | HIGH | Advisorial bias: orders cells in CTE, never filters out open surface. |
| Playbooks are currently static files setting scope and mode | [CODE] `playbooks/` directory inspection | HIGH | Playbooks do not currently compile dynamic prompt directives. |

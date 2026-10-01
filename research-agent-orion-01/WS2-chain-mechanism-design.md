# WS2 — Chain Mechanism Verification (H3) + Chain State-Machine Design

**AI_NAME:** research-agent-orion-01 (unchanged from WS1; folder: `improvment-research/research-agent-orion-01/`)
**Scope discipline:** design only. No payloads, no shell exploit sequences, no runbooks. Capability names only for example hops.
**Files read for this workstream:** `src/scanner/agent_runtime/chain/service.py`, `chain/capabilities.py`, `chain/floor.py`, `engine/exploit_floor.py` (relevant slices), `engine/escalation.py`, `engine/father.py` (chain/escalation slices), `db/models/tenant.py` (ChainNode/ChainEdge), `reporting/service.py` (`_synthesize_chains`/`build_report`), `config.py`, `docker-compose.yml`, `taxonomy.py`.

---

## H3 VERDICT: REFUTED (as a blanket claim) — the truth is three distinct mechanisms, two of which genuinely feed forward

H3, as posed to me, was: *"is a confirmed primitive's proof threaded into the next hop's worker input, or is the graph only linked after the fact for reporting?"* The honest answer is **both, depending on which of three separate subsystems you mean** — the codebase conflates them under "chaining" but they have different data flow, different gating, and different default-on state. Falsifying the simple binary framing:

### 3a. The persisted graph (`ChainNode`/`ChainEdge` via `chain/service.build_graph`/`synthesize_chains`) — CONFIRMED reporting-only, after-the-fact
`build_graph()` is idempotent and destructive-then-rebuild: every call site first `DELETE FROM chain_edge/chain_node WHERE scan_id=...` then re-derives the entire graph from `findings.jsonl` [CODE `chain/service.py:123-234`, delete calls at `father.py:1064-1065` and `engine/escalation.py:47-48`]. It has exactly three callers: the live-tick throttled report rebuild [CODE `father.py:1050-1068`, gated `new_confirmed>=1 or interval elapsed`, itself gated `settings.scanner_chain_synthesis` default `True` — `config.py:149`, compose pin `SCANNER_CHAIN_SYNTHESIS:-true`], `finalize.py:348`, and the legacy planner's approval-gated escalation [`planner/escalation.py:49`]. Its only consumers are `synthesize_chains`→`enumerate_ranked_chains` (feeds the `/chains` API and `reporting/service._synthesize_chains`, `reporting/service.py:82-107`) and `newly_high_impact`/`cells_unlocked_by` (feeds 3c below). **Nothing reads a `ChainNode`/`ChainEdge` row to construct a worker's task text.** For this specific mechanism, "linked only after the fact for reporting" is exactly right.

### 3b. The deterministic chain floor (`chain/floor.py: run_chain_floor`) — CONFIRMED live forward-threading, but zero LLM involvement
This is a **second, independent** mechanism that bypasses the graph entirely. It re-reads `findings.jsonl` directly (`_read_confirmed`, `floor.py:146-162`), pulls the *exact* URL/param the confirmed finding used (`_finding_target`, `floor.py:190-201`, sourced from `affected_endpoint`/`param`/the cell-id `#name` suffix/`oob_registry.jsonl`), and fires the next-hop probe **through that same injection point** — e.g. an SSRF/XXE finding's param gets the metadata-endpoint value substituted in via `_set_query_value` and replayed with the scan's own auth headers (`_hop_metadata`, `floor.py:232-280`; `_hop_file_read`, `floor.py:313-341`; `_hop_redirect`, `floor.py:344-362`). This is genuine, literal forward-threading of one primitive's proof context into the next probe — but the module's own docstring is accurate that "**No LLM is in the chain path**" (`floor.py:8`): it is a pure code executor (curl/`_fire`), never an agent turn. It is wired into the wave loop at `father.py:1613-1638` (`_run_chain_floor`), called once per wave from `father.py:1914`. **Gate: `SCANNER_ENGINE_CHAIN_FLOOR`, default `"0"` in code (`father.py:491`) AND in compose (`docker-compose.yml:140`, `${SCANNER_ENGINE_CHAIN_FLOOR:-0}`) — OFF in every real deployment today.**

### 3c. The escalation wave (`engine/escalation.py: detect_escalations` + `father.py: _run_escalation`/`_capability_context`) — CONFIRMED the confirmed finding's *citation* (not its full proof) is threaded into a live LLM worker's prompt
This is the mechanism that most directly answers the literal H3 question for the **LLM worker** path. `detect_escalations()` rebuilds the graph (calling `build_graph_fn`, default = `chain.service.build_graph`) then calls `newly_high_impact()` to find HIGH_IMPACT capabilities not yet escalated [`engine/escalation.py:31-56`]. Back in `father._run_escalation` [`father.py:1658-1725`], on any new capability it: (1) reopens the ledger cells that capability unlocks via `reopen_cells_for_classes` [`ledger/service.py:1096-1126`] — a **bare state flip**, `tested_clean`→`untested`, keyed only on `vuln_class`, carrying **zero** reference back to the finding that unlocked it [`ledger/service.py:1111-1121`]; (2) builds `cap_ctx = self._capability_context(new_caps)` [`father.py:1708`], which **re-reads `findings.jsonl` a third time** (`_read_verified_findings`, `father.py:568-587`) and, for each capability, emits the line `- You now HAVE `{cap.value}` via finding "{title}" ({endpoint})` [`father.py:1520-1536`] plus a fixed block of generic next-hop instructions (capability-label-shaped, e.g. "session/credential → ... browse() the authed app ... → IDOR/BOLA/admin", `father.py:1540-1547`); (3) claims the unlocked cells [`father.py:1701-1706`] and calls `build_specs(..., capability_ctx=cap_ctx, worklist=...)` [`father.py:1710-1719`], and `build_specs`/`_task_for` **literally prefixes `capability_ctx` onto the next `WorkerSpec.task` string** [`father.py:604-613`, `father.py:670`] — the actual text the Claude Code agent receives as its turn instructions. So: **yes, a confirmed finding's identity (title + endpoint, not its full `proof_of_concept`/evidence body) is threaded into the next hop's LLM worker input**, live, mid-scan. **Gate: `SCANNER_ENGINE_ESCALATE`. Default in code is `"1"` (`father.py:476`: `os.environ.get("SCANNER_ENGINE_ESCALATE", "1") != "0"`), and compose passes it through *empty* rather than unset or `"0"` (`docker-compose.yml:180`, `${SCANNER_ENGINE_ESCALATE:-}`) — `"".strip() != "0"` is `True`, so this path is ON by default in the real deployment**, unlike almost every other capability in this codebase's "default OFF" convention (CLAUDE.md's own "Current Phase" note). This is worth flagging on its own: it is an exception to the stated default-OFF discipline and nobody's doc currently says so.

**Net verdict:** H3-as-"purely theoretical/reporting-only" is REFUTED — two of three chaining mechanisms do feed forward, one of them (3c) directly into what an LLM worker is told to do next, live, and on by default. But H3-as-"the graph itself is after-the-fact" is CONFIRMED for mechanism 3a specifically. The 188-node/449-edge live count given as context [DOC — provided by the orchestrating task, not independently re-queried by me this pass] is consistent with 3a being populated (it runs on a `scanner_chain_synthesis` default-ON schedule) and says nothing about whether 3b/3c ever fired on those scans — that would need a join against `tool_invocations`/`findings.detected_by_tool IN ('chain:...')` rows, which I did not query this pass (READ-ONLY code review, no DB access exercised).

### A freshly-found, precise bug this correlation surfaced (not in the WS1 dossier)
`_capability_context` resolves a finding's vuln-class with **plain `normalize()` only** [`father.py:1527`], not the `normalize(cat) or normalize_ngram(cat)` pattern the same file uses two call sites earlier [`father.py:156`], and not the `normalize_ngram(...)` pattern `chain/service._vuln_class` uses for exactly this reason [`chain/service.py:76-78`, comment: "n-gram normalize so a namespaced category (`vuln.idor_bola`)... still resolves — plain normalize() drops it (H-7)"]. Net effect: a finding whose `category` is a namespaced/verbose string (the H-7 case) correctly anchors a `ChainNode` in the graph (3a, via the ngram-aware resolver) and correctly contributes to `capabilities_for(vc)` everywhere else in the codebase that was fixed for H-7/H-8 — but silently fails the `vc is None: continue` gate inside `_capability_context`'s own loop [`father.py:1528-1529`], so **its specific "You now HAVE X via finding TITLE (ENDPOINT)" citation line is silently dropped**, degrading to the generic fallback "You now HAVE X (see the confirmed findings in /work/scan_brief.md)" [`father.py:1535-1536`]. Low severity (the capability line still appears, just without attribution) but a direct, citable regression of the same class of bug two other modules were patched for. `[CODE father.py:1527]` vs `[CODE father.py:156]` vs `[CODE chain/service.py:76-78]`.

### A second, currently-dormant gap: the one artifact that proves an edge was *executed* gets reabsorbed as an ordinary node
`chain/floor._write_executed_chain` [`floor.py:204-228`] (gated `scanner_executed_chain_findings`, default `False` — `config.py:254`, so **dormant in every stock deploy today**) writes a synthetic finding with `category="executed_chain"`. `"executed_chain"`/`"chain"` are not registered anywhere in `taxonomy.py`'s `_ALIASES` [confirmed via grep, no match], so `normalize_ngram("executed_chain")` returns `None` and `chain/service._vuln_class` falls back to `normalize_cwe(cwe_id)` [`chain/service.py:79-80`] — and the wrapper inherits the **follow-on hop's own CWE** [`floor.py:215`, `cwe = hop_findings[-1].get("cwe_id") or source.get("cwe_id")`], e.g. `CWE-918`, which `taxonomy.py:126` maps uniquely to `VulnClass.SSRF`. So an `executed_chain` finding whose follow-on was actually a `cloud_bucket`-category IMDS-reach hit [`floor.py:271-276`] gets reclassified as a plain `ssrf` `ChainNode` the instant `build_graph` next runs — indistinguishable in the graph from an independently-discovered SSRF finding. The rich causation text ("CONFIRMED X at URL → cap → PROVED Y") does survive as a string inside `ChainNode.attrs["proof_of_concept"]` [`chain/service.py:167-172`, generic copy, no category-awareness], but nothing lets a query or the report programmatically ask "which nodes/edges were code-proven end-to-end vs. capability-table-inferred?" without string-sniffing that PoC text for the literal substring "PROVED". `[CODE floor.py:204-228]` + `[CODE chain/service.py:68-81]` + `[CODE taxonomy.py:126, no alias for "chain"]` — currently unreachable in prod (flag OFF), but the exact bug the design below closes.

---

## DESIGN — chain state machine (mechanism, no payloads)

The three subsystems above already do the hard part (deterministic capability table, deterministic next-hop firing, deterministic graph walk) — what's missing is a **shared, typed, persisted vocabulary** for "how sure are we this edge is real" and "what exactly proved it," so 3a/3b/3c stop talking past each other via loose strings (`category="executed_chain"`, PoC substring-sniffing, a bare `vuln_class` reopen with no back-reference).

### 1. `ProofType` enum — one canonical vocabulary for "how was this shown," not three ad hoc ones
Add to `src/scanner/agent_runtime/chain/capabilities.py` (same module as `Capability`, same "pure table, no LLM" contract):

```
class ProofType(StrEnum):
    HTTP_RESPONSE_MATCH   # a deterministic regex/marker matched the replayed response body
                          #   (mirrors _IMDS_CRED_RX / _BUCKET_LIST_RX / _SECRET_RX in floor.py)
    OOB_CALLBACK          # an interactsh/OOB token fired (mirrors oob/service.classify_oob)
    BROWSER_EXECUTED      # a live Chromium sink fired (mirrors browser_ingest.instrument_hit_to_finding)
    LEDGER_CAPABILITY_INFERENCE  # the ENABLES/GRANTS table asserts reachability; no live probe
                          #   (today's ONLY path for a `ChainEdge` — this label makes that explicit)
```
This does not invent new proof machinery — it *names* the four proof mechanisms that already exist scattered across `floor.py`'s regexes, `oob/service.py`, and `browser_ingest.py`, so a `ChainNode`/`ChainEdge` can say which one produced it instead of leaving every edge looking equally "proven."

### 2. Capability-grant state machine — persisted, not a Python `set()`
Today a capability's "have we seen this" state lives in three separate, **process-local, unpersisted** Python sets that are lost on a scanner-cp restart: `Father._chain_seen_hops` [`father.py:812`], the local `seen_caps` in `Father.run()` [`father.py:1739`], and `Father._escalate_rounds`/`_chain_depth` [`father.py:801,813`]. Per this repo's own tracked issue on `_reconcile_on_boot` having no crash-resume test [CLAUDE.md "Known Issues" list], a resumed scan re-enters `run()` with these sets **empty again** — not correctness-breaking today (dedup at the finding layer + bounded `_escalate_max_rounds()`/`_chain_floor_max_depth()` per-process catch most of the waste) but it means "has capability X already escalated this scan" is not actually a scan-level fact, only a this-process fact.

Promote the existing `ChainNode` row (`src/db/models/tenant.py:297-309`) into the token itself instead of adding a new table — it already carries `scan_id`/`finding_id`/`capability`/`attrs JSONB`. Add two nullable columns via one Alembic migration (`alembic/versions/00XX_chain_proof_type.py`):
- `proof_type TEXT NULL` — one of the four `ProofType` values, defaulted to `LEDGER_CAPABILITY_INFERENCE` for every existing row (byte-compatible backfill).
- `consumed_by JSONB NULL DEFAULT '[]'` — list of `ChainEdge.edge_id`s that treated this node as their source grant (the "receipt" — see #3).

`chain/service.build_graph` [`chain/service.py:180-192`] sets `proof_type` per node based on which producer wrote the underlying finding (`detected_by_tool` already distinguishes `"chain:ssrf-metadata"` / `"chain:lfi-secrets"` / `"chain:ssrf-bucket"` from an LLM-written finding — `floor.py:254,271,301,331` all set a `chain:*` tool tag today; map that prefix to `HTTP_RESPONSE_MATCH`, an OOB-tagged finding to `OOB_CALLBACK`, a browser-instrument finding to `BROWSER_EXECUTED`, everything else to `LEDGER_CAPABILITY_INFERENCE`). This one mapping table (a `dict[str, ProofType]` keyed on `detected_by_tool` prefix, living beside `GRANTS`/`ENABLES` in `capabilities.py`) is the entire "state machine transition function" — no new inference logic, just labeling what already happened.

### 3. Hop-N+1 receipt — on `ChainEdge`, not bolted onto `Finding`
`ChainEdge` today has no `attrs` column at all [`db/models/tenant.py:322-333`] — a `rationale` string is the only payload, and it is identical in shape whether the edge came from `chain/service._add_edge`'s ENABLES-table guess [`chain/service.py:198-228`] or from `chain/floor.py` actually firing the hop and getting a match. Add `attrs JSONB NULL DEFAULT '{}'` to `ChainEdge` (same migration as #2). When `chain/floor.run_chain_floor` proves a hop [any `res.findings += 1` branch, e.g. `floor.py:253-262`, `:300-308`, `:329-339`], it already knows the exact replay it used — `build_replay_cmd`/`parse_replay` [`exploit_floor.py:823-830,1096-1104`] are the SAME replay-contract primitives already imported into `floor.py` [`floor.py:50-52`] — so the receipt just persists what's already computed instead of discarding it:
```
edge.attrs = {
    "consumed_grant": <source ChainNode.node_id>,     # parent-finding linkage, one hop up
    "proof_type": ProofType.HTTP_RESPONSE_MATCH,
    "replay_ref": {"method": "GET", "target_param": param, "endpoint": url},  # NOT the payload value —
                                                                               # points at the SAME cell
                                                                               # identity the ledger already
                                                                               # tracks, no new secret surface
    "hop_evidence_path": <the evidence_name .log file _fire already wrote to tool_outputs/>,
}
```
This is the "replay contract": a pointer to *how* the proof was obtained (method + which param + which endpoint), reusable to re-verify the SAME edge in a later scan (retest) without re-deriving `_finding_target` from scratch — not the injected value itself, so it adds no new sensitive-data-at-rest surface beyond what `evidence_path` already stores today.

### 4. Parent-finding linkage
Already exists as `ChainNode.finding_id` [`tenant.py:306`] — the gap is only that it's a single FK with no notion of "which finding UNLOCKED me" vs "which finding AM I." Fix: `consumed_grant` (in the edge's `attrs`, #3) plus `proof_type` (on the node, #2) together ARE the linkage — `to_node.finding_id` = the follow-on finding, `edge.attrs.consumed_grant` = the source `ChainNode.node_id` → `source.finding_id` = the primitive that granted the capability. No new FK column needed; this is a read-time join, not a schema change beyond #2/#3.

### 5. Report narrative schema — "we found X, which proved Y, which enabled Z"
Current shape is a bare capability-arrow string: `narrative: " → ".join(caps)` [`reporting/service.py:106`], with per-step title/endpoint/poc/evidence already present but unstructured [`reporting/service.py:93-103`]. Reshape `_synthesize_chains`'s per-chain output (same function, same call site, `reporting/service.py:82-107`) into a typed field the frontend/PDF renderer can walk without string-parsing:
```
{
  "chain_id": <uuid>,
  "impact": <int>,                       # unchanged
  "steps": [
    {
      "finding_title": "...", "endpoint": "...",           # unchanged, already present
      "capability": "session",                              # unchanged
      "proof_type": "http_response_match",                  # NEW — from ChainNode.proof_type (#2)
      "narrative_clause": "We found <finding_title>, which proved <capability>",   # NEW, templated
      "enables_clause": "which enabled <next_step.finding_title or next_step.capability>",  # NEW
    },
    ...
  ],
  "narrative": "<clause_1>, <enables_clause_1>; <clause_2>, ...",  # NEW — the assembled prose
}
```
The templating is pure string formatting over data already on the row (`finding_title`, `capability`, `proof_type`) plus the NEXT step's same fields — no LLM narration needed for this (a distinct, already-existing LLM narration slot is the `addons["finding_narratives"]` path at `reporting/service.py:174`, which this does not touch or require).

### 6. Example hops — capability labels only (design illustration, not new attack logic)
The `_HOPS` dispatch table [`floor.py:397-404`] already IS this state machine's transition table, just unlabeled by proof-type. Illustrative hops in capability-label form (no payloads):
```
FILE_READ            -> ProofType.HTTP_RESPONSE_MATCH -> SECRET_DISCOVERY (secrets_exposure)
METADATA_ACCESS      -> ProofType.HTTP_RESPONSE_MATCH -> CLOUD_CREDENTIAL_THEFT (cloud_bucket)
REDIRECT             -> ProofType.OOB_CALLBACK         -> INTERNAL_HTTP (ssrf)
CREDENTIAL           -> ProofType.LEDGER_CAPABILITY_INFERENCE -> SESSION (reopens IDOR/BFLA/priv_esc family)
```
Each arrow is a `(Capability, ProofType) -> VulnClass` triple — a strict refinement of the existing `ENABLES: dict[Capability, frozenset[VulnClass]]` table [`capabilities.py:77-88`], adding only the "how" axis. No new hop functions are implied by this design; it is a labeling layer over `_HOPS` + `ENABLES`.

### Files this design would touch (naming real files, no new modules beyond one migration)
- `src/scanner/agent_runtime/chain/capabilities.py` — add `ProofType` enum + `detected_by_tool`→`ProofType` mapping table, beside existing `GRANTS`/`ENABLES`.
- `src/scanner/db/models/tenant.py` — add `proof_type`/`consumed_by` to `ChainNode` (:297-309), add `attrs` to `ChainEdge` (:322-333).
- `alembic/versions/00XX_chain_proof_type.py` — one migration, all-nullable, backfills `proof_type='ledger_capability_inference'`.
- `src/scanner/agent_runtime/chain/service.py` — `build_graph` (:123-234) stamps `proof_type` per node from the mapping table; `_add_edge`/edge construction (:198-228) stamps `attrs.consumed_grant` when `chain/floor.py` supplies it.
- `src/scanner/agent_runtime/chain/floor.py` — the proving branches (`:253-262`, `:300-308`, `:329-339`) build and pass the `replay_ref`/`hop_evidence_path` receipt instead of only calling `_write_finding`.
- `src/scanner/reporting/service.py` — `_synthesize_chains` (:82-107) emits the templated narrative fields.
- `src/scanner/agent_runtime/engine/father.py` — `_capability_context` (:1520-1548) fix (`normalize_ngram` fallback, see bug above) rides the same change window; optionally also cite `proof_type` in the escalation-wave prompt once available.
- No change needed to `ledger/service.reopen_cells_for_classes` (:1096-1126) — it is correctly generic (a class-level re-test signal); the receipt lives on the chain graph, not the ledger cell.

---

## Evidence Ledger

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| `build_graph`/`synthesize_chains` is destructive-rebuild, after-the-fact, feeds only the report/API | [CODE chain/service.py:123-234, 264-346] + [CODE father.py:1050-1068] + [CODE finalize.py:348] + [CODE reporting/service.py:82-107,702-703] | High | Three call sites enumerated; no fourth found via grep across `src/`. |
| `chain/floor.run_chain_floor` threads a confirmed finding's own URL/param into a live next-hop probe, code-only, no LLM | [CODE chain/floor.py:8,146-201,232-383,407-454] | High | Module docstring explicitly states "No LLM is in the chain path"; verified against the hop implementations. |
| `chain/floor` is default-OFF in both code and compose | [CODE father.py:491] + [CODE docker-compose.yml:140] | High | Direct read of both. |
| `_capability_context` threads a confirmed finding's title+endpoint (not full PoC) into the NEXT LLM worker's task text | [CODE father.py:1520-1548,604-613,670,1708-1719] | High | Traced `capability_ctx` from construction to `WorkerSpec.task` string. |
| The escalation path (`SCANNER_ENGINE_ESCALATE`) defaults ON in both code and the shipped compose file, unlike the codebase's stated default-OFF convention for new capabilities | [CODE father.py:476] + [CODE docker-compose.yml:180] | High | `${VAR:-}` passes an empty string, and the code's `!= "0"` check treats empty as enabled — verified the exact semantics, not assumed. |
| `_capability_context` uses plain `normalize()` instead of the `normalize()`-then-`normalize_ngram()` pattern used two call sites earlier in the same file, silently dropping the finding-citation for namespaced categories | [CODE father.py:1527] vs [CODE father.py:156] vs [CODE chain/service.py:76-78] | High (mechanism) / Medium (real-world frequency — depends how often agents emit namespaced categories) | Freshly found this pass; not present in the WS1 dossier or (as far as I read) elsewhere. |
| A dormant `executed_chain` finding gets silently reclassified to its follow-on hop's CWE-derived `VulnClass` (e.g. SSRF) by `chain/service._vuln_class`, losing its distinct "this edge was code-proven" identity in the graph | [CODE floor.py:204-228] + [CODE chain/service.py:68-81] + [CODE taxonomy.py:126, no "chain" alias found] | High (mechanism), confirmed dormant | Gated by `scanner_executed_chain_findings=False` [CODE config.py:254] — unreachable in a stock deploy today, but real once the flag flips. |
| 188 chain nodes / 449 edges across 13 of ~43 scans | [DOC — supplied by the orchestrating task/prior WS, not independently re-queried by me] | Not verified this pass | I did not run a DB query this pass (code-only correlation); flagged as inherited context, not my own evidence. |
| `Father._chain_seen_hops`/`seen_caps`/`_escalate_rounds` are process-local, not persisted — lost on a scanner-cp restart mid-scan | [CODE father.py:801,812,813,1739] | High (mechanism) | Consistent with, and extends, this repo's own tracked `_reconcile_on_boot` no-test-coverage issue (CLAUDE.md Known Issues) — not re-litigating that issue, only noting the same blast radius applies to chain state. |
| Design's four `ProofType` values map onto already-existing, distinct proof mechanisms in the codebase (not invented) | [CODE floor.py:97-101 (`_SECRET_RX`), 84-86 (`_BUCKET_LIST_RX`), 66-68 (`_IMDS_CRED_RX`)] for HTTP_RESPONSE_MATCH; [DOC CLAUDE.md "WS4 browser foundation" section] for BROWSER_EXECUTED; [DOC CLAUDE.md "OOB false-positive fix" section] for OOB_CALLBACK | Medium-High | The regex citations are direct code; the OOB/browser mechanism citations lean on this repo's own CLAUDE.md narrative rather than a fresh read of `oob/service.py`/`browser_ingest.py` this pass (time-boxed; the mechanism names are corroborated by function names already grepped, e.g. `classify_oob`, `instrument_hit_to_finding`, but I did not re-open those files in this workstream). |

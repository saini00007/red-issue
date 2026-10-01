# WS-4 — Chain State Machine: capability tokens, proof carry, and executed-chain narrative

**Role:** READ-ONLY systems architect (design, not implementation).
**Sources:** (A) codebase of this repo; (B) `competitor-research/` via `improvment-research/research-agent-nova-02/ws3/WS-3-competitor-mechanisms.md`.
**Constraint honored (R1):** capability models, state machines, proof-type enums, worker contracts, report schemas, capability LABELS only. No payloads, no shell commands, no copy-paste exploit sequences, no session-theft steps, no runbooks. Offensive steps are described as MECHANISM / INPUT / VERDICT only.
**Operator rule D4:** every design element below is flag-gated, default-OFF, byte-identical when off.

---

# PART 0 — Falsifying H3

> **H3:** "Current chain synthesis is graph-only; there is no mechanism to carry a proof artifact from hop N into hop N+1's prompt and evidence."

## 0.1 What actually exists today (sub-question 1: does the chain floor EXECUTE hops or just synthesize edges?)

Both things exist, as two independent subsystems:

1. **Graph synthesis (no execution).** `chain/service.py::build_graph` reads `findings.jsonl`, anchors one `ChainNode` per (verified, evidenced finding x granted capability) and infers `ChainEdge` rows purely from the static `ENABLES` adjacency table — "deterministic: nodes come from confirmed findings' granted capabilities; edges from the ENABLES adjacency … The LLM is not in this path" [CODE] `src/scanner/agent_runtime/chain/service.py:1-7`, node gate at `service.py:142`, edge loop at `service.py:211-228`. No request is fired, no hop is executed here.
2. **Hop execution (deterministic, flag-gated).** `chain/floor.py::run_chain_floor` genuinely EXECUTES hops: for every confirmed finding it maps vuln-class → capability → a registered hop function (`_HOPS`) and fires a bounded probe through the in-scope vulnerable parameter, deciding on a deterministic body verdict (regex/oracle match → finding; no match → signal) [CODE] `src/scanner/agent_runtime/chain/floor.py:407-454`, hop registry `floor.py:397-404`, probe fire sites `floor.py:245, 293, 322, 355, 375`. It is invoked once per wave from Father's phase-D slot, before escalation [CODE] `src/scanner/agent_runtime/engine/father.py:1910-1914`, `father.py:1613-1638`.

So "graph-only" is **true for `chain/service.py` and false for the chain subsystem as a whole** — but execution is double-gated and therefore dormant in sampled scans: `SCANNER_ENGINE_CHAIN_FLOOR` defaults to `0` [CODE] `father.py:487-491`, and the executed-chain finding writer `scanner_executed_chain_findings` defaults to `False` [CODE] `src/scanner/config.py:249-254`. That combination directly explains the peer-observed `executed_chains=0`: even if the floor fires, `_write_executed_chain` is skipped unless the flag is on [CODE] `floor.py:105-112, 445-450`, and `reporting/service.py` fills `executed_chains` only from rows with `verification_method='executed_chain'` (or chain-titled category) AND `verified=true` [CODE] `src/scanner/reporting/service.py:298-318`.

## 0.2 What is stored per node (schema, quoted)

`chain_node` DDL [CODE] `alembic/versions/0008_add_chain_and_approval.py:22-31`:

```
chain_node (
  node_id uuid PK,
  scan_id uuid NOT NULL REFERENCES scans,
  finding_id uuid NULL,
  capability text NOT NULL,
  attrs jsonb NOT NULL,
  created_at timestamptz,
  UNIQUE (scan_id, finding_id, capability)
)
```

ORM matches [CODE] `src/scanner/db/models/tenant.py:297-309`. Per-node `attrs` payload written by `build_graph` [CODE] `chain/service.py:169-179`:

```json
{
  "vuln_class": "<label>",
  "endpoint": "<string>",
  "proof_of_concept": "<string, capped 4000 chars>",
  "evidence_path": "<string>",
  "reasoning": "<string, optional, capped 2000>"
}
```

Note: **the node DOES snapshot hop N's proof text and evidence path** (`proof_of_concept`, `evidence_path`) [CODE] `service.py:167-174`. Edges carry only `rationale` prose [CODE] `db/models/tenant.py:322-333`. `ChainStep` (the composed-chain step) is `{finding_id, capability, rationale}` — **no proof reference field** [CODE] `chain/service.py:38-43, 336-343`.

## 0.3 Is there ANY path where hop N's artifact reaches hop N+1's prompt or claim?

Searches for `evidence_ids | proof_ref | artifact` across `src/scanner` show **zero hits inside `src/scanner/agent_runtime/chain/*`**; `evidence_ids` lives only on `LedgerCell` [CODE] `db/models/tenant.py:271` and its ledger/API consumers [CODE] `src/scanner/ledger/service.py:925, 973, 1001-1025; src/scanner/api/routes/scans.py:603`. Concrete prompt paths:

| Path | What hop N+1 actually receives | Proof artifact carried? | Citation |
|---|---|---|---|
| Escalation-wave task (`_capability_context`) | capability label + granting finding's **title + endpoint** only | **No** (no evidence id / path / hash) | [CODE] `engine/father.py:1520-1548` (title+endpoint assembled at 1531-1533) |
| Shared scan brief | confirmed-findings **titles** (capped 20) | **No** | [CODE] `engine/scan_brief.py:114, 149-152, 266` |
| Worker progress digest (reprompt) | verified finding **titles** (capped 8) | **No** | [CODE] `engine/runtimes/agents_runtime.py:1010-1021` |
| Report chain narrative (`chain_narratives`) | per-hop `poc` + `evidence` **read from node attrs** | **Yes — report-side carry only** | [CODE] `reporting/service.py:82-107` (98-99), rendered at `service.py:437-444, 543-553` |
| Deterministic floor, hop N→N+1 (file-mediated) | hop N+1's **input** is a NEW confirmed finding appended by hop N (`verified` + `proof_of_concept` gate) → endpoint/param consumed; proof text travels in the row but is not consumed | **Partial — artifact travels in `findings.jsonl`, only endpoint/param are read** | [CODE] `chain/floor.py:146-162, 426-450`; phase ordering [CODE] `father.py:1910-1914` |
| OOB token minted during a hop | token registered to `oob_registry.jsonl`, later confirmed by callback into a verified finding (`verification_method='oob_callback'`) | **Yes — token carries across time into evidence (async)** | [CODE] `floor.py:350-362, 370-382`; [CODE] `src/scanner/agent_runtime/oob/service.py:490, 510` |
| Graph rebuild idempotency | `build_graph` nodes are DELETEd and rebuilt each escalation round and each finalize | Node attrs are **volatile**, cannot be a durable token store | [CODE] `engine/escalation.py:47-49`; [CODE] `agent_runtime/finalize.py:340-341`; [CODE] `engine/father.py:1064-1068` |

## 0.4 VERDICT: **PARTIAL**

- **REFUTED (clausula 1, "graph-only"):** the chain subsystem executes hops deterministically (`chain/floor.py`), including OOB token minting and evidence-file writes — but both the executor (`SCANNER_ENGINE_CHAIN_FLOOR=0` [CODE] `father.py:491`) and its report writer (`scanner_executed_chain_findings=False` [CODE] `config.py:254`) are default-OFF, which is consistent with `executed_chains=0` in sampled reports [CODE] `reporting/service.py:298-318, 390`.
- **CONFIRMED (clausula 2, prompt-side):** there is **no typed proof reference** (`evidence_id`, hash, path) passed from hop N into hop N+1's **prompt or claim**. The LLM escalation contract carries labels + titles + endpoints only [CODE] `father.py:1530-1536]; `ChainStep` has no proof field [CODE] `chain/service.py:38-43`; `chain_node.attrs` proof snapshot is consumed by the **report renderer**, not by any worker prompt [CODE] `reporting/service.py:98-99` vs `father.py:1526-1536`.
- **PARTIAL (clausula 2, evidence-side):** carry-over DOES exist through three informal channels — (i) shared `/work` files (`findings.jsonl` full rows, `auth.json` session artifact read by floor hops [CODE] `floor.py:422` and surfaced to workers [CODE] `scan_brief.py:84-101]); (ii) file-mediated deterministic chaining where hop N's proof-bearing finding is hop N+1's input [CODE] `floor.py:426-450`; (iii) the async OOB token→callback→verified-finding pipeline [CODE] `floor.py:350-362` + `oob/service.py:490`. These are *workspace conventions*, not a contract: nothing types, hashes, scopes, or replays them.

**Conclusion:** H3 survives as a *design gap* (no structured token/proof-ref contract) but fails as an absolute claim (deterministic floor + OOB pipeline already carry artifacts through files). The design below closes the structured half.

### H3 Evidence Ledger

| # | Sub-claim | Evidence | Disposition |
|---|---|---|---|
| H3-a | Synthesis is graph-only | `service.py:1-7, 142, 211-228` (edges from static ENABLES, no execution) | CONFIRMED for `chain/service.py` |
| H3-b | …but the subsystem never executes | `floor.py:407-454, 397-404` executes probes; gated `father.py:491`, `config.py:254` | REFUTED (execution exists, default-off) |
| H3-c | `executed_chains=0` explained | writer gated `floor.py:105-112, 445-450`; report filters `reporting/service.py:298-318` | CONFIRMED (mechanism identified) |
| H3-d | No proof ref into hop N+1 prompt | `father.py:1530-1536` (label+title+endpoint); `scan_brief.py:266` (titles); `service.py:38-43` (ChainStep lacks proof field); zero `evidence_ids` hits in `chain/*` | CONFIRMED |
| H3-e | Partial carry exists | node attrs proof snapshot consumed report-side `service.py:167-174, 98-99`; file-mediated floor input `floor.py:426-450`; OOB token carry `floor.py:350-362` → `oob/service.py:490` | CONFIRMED (PARTIAL verdict basis) |
| H3-f | Chain nodes are a durable carrier | nodes DELETEd+rebuilt `escalation.py:47-49`, `finalize.py:340-341`, `father.py:1064-1068` | REFUTED → new token store required |

---

# PART 1 — DESIGN (flag-gated, default-OFF, byte-identical when off)

**New flag (rule D4):** `SCANNER_CHAIN_STATE_MACHINE` (env, `0` default) / `scanner_chain_state_machine: bool = False` (Settings, mirroring `scanner_executed_chain_findings` [CODE] `config.py:254]). Read lazily fail-closed inside each touched module, exactly like `_executed_chain_enabled()` [CODE] `floor.py:105-112]. If env-read, add to the scheduler's forwarded-env allowlist beside `SCANNER_ENGINE_CHAIN_FLOOR` [CODE] `src/scanner/scheduler/worker.py:71-72]. When the flag is 0: no token rows written, no state transitions, no worker-contract field emitted, no new report key — output JSON/MD byte-identical (all new keys are emitted only under the flag, matching the `chain_narratives`/`addons` "absent ⇒ legacy" pattern [CODE] `reporting/service.py:402-413]).

## 1. Chain state machine

### 1.1 States

| State | Meaning | Set when |
|---|---|---|
| `PRIMITIVE_CONFIRMED` | Source finding verified with a proof artifact; capability table says it grants ≥1 capability | Finding passes the existing confirmed gate (`verified` + `proof_of_concept`) [CODE] `floor.py:160`; `service.py:142` |
| `TOKEN_GRANTED` | A capability token was minted for that primitive (deterministic grant) | Grant predicate in §1.2 fires |
| `HOP_MATERIALIZED` | The downstream cell for the unlocked vuln-class exists and is claimable (reopen/spawn) | `reopen_cells_for_classes` / surface claim [CODE] `father.py:1630-1636, 1701-1706] |
| `HOP_EXECUTING` | Hop in flight: floor probe firing or LLM escalation worker holds the cell lease | Probe dispatch [CODE] `floor.py:441-446`; cell claim/lease [CODE] `db/models/tenant.py:274-281` |
| `HOP_VERIFIED` | Hop's OWN oracle fired → new confirmed finding with proof | Deterministic verdict branch writes a finding [CODE] `floor.py:253-262, 300-307, 329-337`; or ledger `_confirm_state` returns `confirmed` [CODE] `ledger/service.py:205-226` |
| `CHAIN_BROKEN` | Terminal: hop failed / timed out / oracle did not fire / out of scope | Failure branch (§5) |
| `CHAIN_COMPLETE` | Terminal: the planned path's last hop reached `HOP_VERIFIED` and no further grant exists | Terminal state, report-eligible |

### 1.2 Transitions and guard conditions

```
PRIMITIVE_CONFIRMED --[G1]--> TOKEN_GRANTED
TOKEN_GRANTED       --[G2]--> HOP_MATERIALIZED
HOP_MATERIALIZED    --[G3]--> HOP_EXECUTING
HOP_EXECUTING       --[G4]--> HOP_VERIFIED        (oracle fired)
HOP_EXECUTING       --[G5]--> CHAIN_BROKEN        (timeout | no oracle | scope block)
HOP_VERIFIED        --[G6]--> TOKEN_GRANTED       (recurse; capability of hop's finding)
HOP_VERIFIED        --[G7]--> CHAIN_COMPLETE      (no next capability / depth cap)
TOKEN_GRANTED       --[G8]--> CHAIN_BROKEN        (materialization blocked: no in-scope cell)
any                 --[G9]--> CHAIN_BROKEN        (hop N proof REPLAY_DRIFT, see §2.3)
```

| Guard | Condition (deterministic) | Rationale / citation |
|---|---|---|
| **G1 (grant)** | `GRANTS[vuln_class]` non-empty (static table) **AND** the granting finding carries proof of a **minting** proof-type (§2.1) | Grant table is pure/static [CODE] `chain/capabilities.py:38-72, 170-178]; proof gate mirrors the ledger evidence gate [CODE] `ledger/service.py:175-187, 219-220`. **No proof ⇒ no token** (thesis). |
| **G2 (materialize)** | An in-scope cell exists for a class in `ENABLES[capability]`, or a fresh cell can be reopened | `ENABLES` adjacency [CODE] `capabilities.py:77-88`; reopen path [CODE] `father.py:1630-1636]; cells unlocked via `cells_unlocked_by` [CODE] `chain/service.py:249-254` |
| **G3 (claim)** | Cell lease acquired (atomic claim), scope hook passes | Claim/lease model [CODE] `db/models/tenant.py:274-281`; scope gate on every hop [CODE] `floor.py:434` |
| **G4 (verify)** | Hop's deterministic verdict matches (in-band body oracle, OOB callback, or browser execution) | Thesis: oracle/OOB/browser only [CODE] `reporting/exploit_quality.py:118-130`; OOB confirm [CODE] `oob/service.py:490` |
| **G5 (break)** | Probe timeout, no verdict match, or `_scope_ok` fails | Failure branches [CODE] `floor.py:441-452`; scope [CODE] `floor.py:434` |
| **G6 (recurse)** | Hop's finding itself grants a capability not yet tokenized (dedup via `seen` set semantics) | Recursion bound by `seen_hops`/depth [CODE] `floor.py:412, 437-440]; depth cap [CODE] `father.py:494-498, 1620` |
| **G8** | Escalation spawn declined (expansion budget) or no claimable cell | Budget gate [CODE] `father.py:1577-1583, 1597-1607` |
| **G9** | Upstream token replayed as `REPLAY_DRIFT` (§2.3) | REPLAY contract below |

### 1.3 Token persistence — **new table, not `chain_node`** [DESIGN]

**Do NOT store tokens on `chain_node`.** The graph is DELETEd and rebuilt on every escalation round [CODE] `engine/escalation.py:47-49], every finalize [CODE] `agent_runtime/finalize.py:340-341], and every throttled live rebuild [CODE] `engine/father.py:1064-1068] — a token on `chain_node` would be destroyed by routine idempotency. `chain_node.attrs` is also capped/truncated JSONB [CODE] `chain/service.py:166-174], unsuitable for a ledger.

**Proposal:** new table **`chain_token`**, created by migration **`alembic/versions/0020_chain_capability_token.py`** (next free number after `0019_add_scan_engine_models.py` [CODE] `alembic/versions/` listing):

```
chain_token (
  token_id      uuid PK,
  scan_id       uuid NOT NULL REFERENCES scans ON DELETE CASCADE,
  hop_index     int  NOT NULL,              -- 0 = entry primitive
  capability    text NOT NULL,              -- Capability enum label
  parent_token_id uuid NULL REFERENCES chain_token(token_id),
  granted_by_finding_id uuid NULL,          -- hop N's finding
  granted_by_cell_id    uuid NULL REFERENCES ledger_cell(cell_id),
  proof_type    text NOT NULL,              -- enum, §2.1
  proof_ref     text NOT NULL,              -- evidence_id | evidence_path | oob token ref
  proof_hash    text NOT NULL,              -- sha256 of canonical proof bytes, §2.3
  proof_at      timestamptz NOT NULL,       -- proof creation time (replay clock)
  state         text NOT NULL,              -- state machine, §1.1
  state_reason  text NULL,
  created_at    timestamptz DEFAULT now(),
  UNIQUE (scan_id, hop_index, capability, granted_by_finding_id)
)
```

Column semantics mirror what already exists elsewhere: `evidence_ids` JSONB on the cell [CODE] `db/models/tenant.py:271`, `finding_id` on cell/node [CODE] `tenant.py:272, 306`, `EvidenceObject.created_at` [CODE] `tenant.py:244`. Write path is append-only + `UPDATE state`; it is **never** part of the graph DELETE statements (which name `chain_edge`/`chain_node` explicitly [CODE] `escalation.py:47-48]).

*Alternative considered* [DESIGN]: add a `ledger_cell.chain_token` JSONB column — rejected as primary store because a cell is `(scan, element, vuln_class)`-scoped [CODE] `tenant.py:250` and cannot express N hops over the same cell, nor a parent/child token lineage. The cell instead stores the **reference**: `chain_token.granted_by_cell_id` points at it, so the API can render tokens per cell alongside `evidence_ids` [CODE] `api/routes/scans.py:603`.

### 1.4 How hop N+1 receives the token — worker contract [DESIGN]

Extend the escalation-wave contract (today label+title+endpoint only [CODE] `father.py:1520-1548]) with a typed block, emitted **only when the flag is on**:

```
capabilities: [
  {
    type:           Capability          // e.g. internal_http | credential | session | ...
    proof_ref:      string              // evidence_id / evidence_path / oob ref of hop N
    proof_type:     ProofType           // §2.1 enum
    proof_hash:     string              // §2.3
    granted_by_cell: string             // ledger_cell id (or endpoint::vuln_class fallback)
    granted_by_finding: string          // hop N finding_id
    token_id:       string
    hop_index:      int
    state:          TokenState          // must be TOKEN_GRANTED for the worker to use it
  },
  ...
]
```

Wiring [DESIGN]: `_capability_context()` becomes token-aware (reads `chain_token WHERE scan_id=? AND state='TOKEN_GRANTED'`) instead of re-deriving from titles; the block is prefixed in `_task_for` exactly where `capability_ctx` is inserted today [CODE] `father.py:604-614, 643-670, 1708-1717]. The floor's deterministic hops do not need the LLM block (they already consume the confirmed row [CODE] `floor.py:426-432]) — they receive the token as their *input claim*: hop probe may only fire if a `TOKEN_GRANTED` row exists for `(capability, finding)` (G1→G3 gate inside `run_chain_floor`). Contract rule: **the worker/floor may reference `proof_ref` but must re-prove its own hop** — hop N's proof is context, never hop N+1's evidence.

---

## 2. Parent-finding linkage, proof-type enum, REPLAY contract

### 2.1 ProofType enum (derived from real `verification_method` values in code/DB)

Observed writers of `verification_method` (normalized: lower-case, hyphens→underscores at ingest [CODE] `agent_runtime/ingest_findings.py:172-173]): `oob_callback`, `deferred_canary`, `deterministic`, `executed_chain`, `exploit_floor:<tool>` (incl. `:sqli-time`, `:cmdi-time` timing variants), `recon_floor:js_secret`, `recon_floor:dns_takeover`, `manual` (grep across `src/ tests`). Capsule `method` values: `browser_har`, `oob_callback`, else the vm label itself [CODE] `reporting/exploit_quality.py:174-193].

```python
class ProofType(StrEnum):                      # [DESIGN], derived from [CODE] below
    ORACLE_FIRED      = "oracle_fired"         # is_deterministic_oracle(vm): exploit_floor:<non-timing>, deterministic, recon_floor:*  [CODE] exploit_quality.py:118-130
    OOB_CALLBACK      = "oob_callback"         # vm == oob_callback | deferred_canary          [CODE] oob/service.py:356, 490
    BROWSER_EXECUTED  = "browser_executed"     # capsule method == browser_har                 [CODE] exploit_quality.py:174-178
    ARTIFACT_READ     = "artifact_read"        # evidence/evidence_ids/evidence_path present, no oracle  [CODE] ledger/service.py:175-187
    CHAIN_COMPOSED    = "chain_composed"       # vm == executed_chain (REPORT-ONLY, non-minting) [CODE] chain/floor.py:225; reporting/service.py:72-73
```

**Mint rule (thesis-aligned)** [DESIGN]: `G1` mints a token **only** for `ORACLE_FIRED | OOB_CALLBACK | BROWSER_EXECUTED`. `ARTIFACT_READ` continues to satisfy the ledger's confirm gate [CODE] `ledger/service.py:219-220] but does **not** mint (no fired oracle ⇒ no token). `CHAIN_COMPOSED` is a *derived* report label and never grants downstream.

### 2.2 Parent-finding linkage

* `chain_token.granted_by_finding_id` → hop N's `findings.finding_id` [CODE] `tenant.py:98].
* `chain_token.granted_by_cell_id` → the ledger cell that hop N resolved (`ledger_cell.finding_id` join) [CODE] `tenant.py:272].
* `chain_token.parent_token_id` → hop N-1's token: forms a linear lineage (`hop_index` ascending), giving the report its "X ⇒ Y ⇒ Z" parent chain without re-walking the volatile graph.
* Existing linkage kept intact: `chain_node.finding_id` still anchors report steps [CODE] `service.py:181-186; reporting/service.py:92-99] — tokens augment, never replace it, so flag-off behavior is untouched.

### 2.3 REPLAY contract (re-verify a chain without re-running hop N) [DESIGN]

Replay = verify hop N's stored proof, not re-execute the attack:

```
ReplayRequest  { token_id, mode: "reference_only" | "content_recheck" }
ReplayVerdict  { token_id, result: REPLAYED_MATCH | REPLAY_DRIFT | REPLAY_UNAVAILABLE,
                 checked_at, matched_hash }
```

* **Reference:** `proof_ref` (evidence_id / evidence_path / OOB token ref) — resolution path already exists (`EvidenceObject.evidence_id` [CODE] `tenant.py:225`; `ledger_cell.evidence_ids` [CODE] `tenant.py:271`).
* **Hash:** `proof_hash = sha256(canonical(redacted request + response excerpt | oob interaction | HAR pair))`, canonicalization reusing the existing redaction seam (capsule builder [CODE] `exploit_quality.py:136-148]).
* **Timestamp:** `proof_at` (creation time of the backing evidence/finding); a replay older than a scan-configurable freshness window yields `REPLAY_UNAVAILABLE`, not a pass.
* **Execution-free recheck** has a precedent in-repo: the detached verifier deterministically re-issues a *captured* proof request and applies a content oracle (reproduced iff the distinctive proof marker reappears) [CODE] `engine/detached_verify.py:7-10, 84-99, 124-126]. WS-4 reuses that seam for `mode=content_recheck`; `reference_only` is pure hash+timestamp comparison (no network).
* **Effect:** `REPLAYED_MATCH` keeps `state` valid; `REPLAY_DRIFT`/`REPLAY_UNAVAILABLE` triggers **G9** → the downstream chain row goes `CHAIN_BROKEN` (no silent inheritance of a stale proof), while hop N's historical `HOP_VERIFIED` record is preserved for audit.

---

## 3. Report narrative schema (buyer-facing attack story)

New report key **`executed_chain_stories`**, emitted only under the flag (absent ⇒ byte-identical legacy report; sibling keys pattern [CODE] `reporting/service.py:398-413]). Field skeleton — names/types only:

```jsonc
{
  "executed_chain_stories": [
    {
      "story_id":        "string (uuid)",
      "scan_id":         "string (uuid)",
      "entry_capability":"string (Capability label)",
      "impact_severity": "string enum: critical|high|medium|low|info",
      "impact_score":    "number (int, mirrors existing len*(high_impact+1) impact)  [CODE] service.py:317-319",
      "headline":        "string  // 'found X, which proved Y, which enabled Z' template, labels only",
      "hops": [
        {
          "hop_index":       "integer",
          "capability":      "string (Capability label)",
          "vuln_class":      "string",
          "parent_finding":  "string|null (uuid finding_id of hop N-1)",
          "granting_finding":"string|null (uuid finding_id of hop N)",
          "granting_cell":   "string|null (uuid ledger_cell)",
          "proof_type":      "string enum: oracle_fired|oob_callback|browser_executed|artifact_read|chain_composed",
          "proof_ref":       "string  // evidence_id / evidence_path / oob ref",
          "proof_hash":      "string (sha256 hex)",
          "proof_at":        "string (ISO-8601)",
          "replay": {
            "result":        "string enum: replayed_match|replay_drift|replay_unavailable|not_replayed",
            "checked_at":    "string|null (ISO-8601)"
          },
          "endpoint":        "string|null",
          "evidence_path":   "string|null",
          "rationale":       "string  // why hop N+1 is reachable from hop N (EDGE_RATIONALE) [CODE] capabilities.py:106-162",
          "state":           "string enum: hop_verified|chain_broken|chain_complete"
        }
      ],
      "chain_state":      "string enum: chain_complete|chain_broken",
      "break_reason":     "string|null",
      "evidence_refs":    ["string"]  // union of hop proof_refs, stable for auditors
    }
  ],
  "summary.executed_chains_verified": "integer  // existing count semantics [CODE] reporting/service.py:390"
}
```

The `headline` is assembled from hop labels + proof types only (e.g. `SSRF [oracle_fired] ⇒ METADATA_ACCESS [oob_callback] ⇒ CREDENTIAL [oracle_fired]`); prose can be LLM-decorated later as an addon (existing `addons` seam [CODE] `reporting/service.py:173-174]) but **the numbers and refs come from `chain_token`, never from the model** (thesis: LLM proposes, deterministic oracle disposes).

Markdown rendering: add an "### Executed (proven end-to-end)" sibling walk next to today's candidate/edge sections [CODE] `reporting/service.py:524-559], one bullet per hop with `proof_type` + `proof_ref` (mechanism label, no payload).

---

## 4. Example chains as CAPABILITY LABELS only

Paths are derived from the real `GRANTS`/`ENABLES` tables [CODE] `capabilities.py:38-88]; labels only, no steps, no inputs, no payloads.

| # | Chain (labels) | Grant edges used | Terminal proof-type (example) |
|---|---|---|---|
| 1 | `SSRF` → `METADATA_ACCESS` → `SECRETS_EXPOSURE` → `CREDENTIAL` → `AUTH_BYPASS` | `GRANTS[SSRF]={internal_http, metadata_access}`; `ENABLES[metadata_access]={cloud_bucket, secrets_exposure}`; `GRANTS[secrets_exposure]={credential}`; `ENABLES[credential]={auth_bypass,...}` [CODE] `capabilities.py:39, 79, 49, 80` | `ORACLE_FIRED` (hop1) → `ORACLE_FIRED` (hop2) |
| 2 | `OAUTH_SAML` (SSO_BUG) → `SESSION` → `IDOR_BOLA` → `CROSS_PRINCIPAL_READ` → `PRIV_ESC` | `GRANTS[oauth_saml]={session}`; `ENABLES[session]={idor_bola, bfla, priv_esc}`; `GRANTS[idor_bola]={cross_principal_read, pii_read}`; `ENABLES[cross_principal_read]={priv_esc}` [CODE] `capabilities.py:55, 81, 58, 85` | `BROWSER_EXECUTED` (authz diff) / `ARTIFACT_READ` |
| 3 | `FILE_UPLOAD` → `RCE` → `SECRETS_EXPOSURE` → `CREDENTIAL` | `GRANTS[file_upload]={rce}`; `ENABLES[rce]={secrets_exposure}`; `GRANTS[secrets_exposure]={credential}` [CODE] `capabilities.py:45, 82, 49` | `ORACLE_FIRED` |
| 4 | `LFI` → `FILE_READ` → `SECRETS_EXPOSURE` → `CREDENTIAL` | `GRANTS[lfi]={file_read}`; `ENABLES[file_read]={secrets_exposure}`; `GRANTS[secrets_exposure]={credential}` [CODE] `capabilities.py:46, 86, 49` | `ORACLE_FIRED` |
| 5 | `OPEN_REDIRECT` → `REDIRECT` → `SSRF` → `METADATA_ACCESS` → `CLOUD_STORAGE` | `GRANTS[open_redirect]={redirect}`; `ENABLES[redirect]={ssrf}`; `GRANTS[ssrf]={...,metadata_access}`; `ENABLES[internal_http]={ssrf, cloud_bucket}` [CODE] `capabilities.py:71, 87, 39, 78` | `OOB_CALLBACK` (hop2) → `ORACLE_FIRED` |

High-impact milestones (`RCE, CREDENTIAL, SESSION, METADATA_ACCESS, PII_READ`) drive ranking/escalation gating exactly as today [CODE] `capabilities.py:96-98; service.py:317-319]. `REDIRECT` stays out of high-impact by design [CODE] `capabilities.py:91-92].

---

## 5. Failure semantics (no partial credit)

| Event | Chain state | Ledger cell state | Credit |
|---|---|---|---|
| Hop probe fires, oracle does not match | `HOP_EXECUTING` → `CHAIN_BROKEN` (`state_reason=oracle_not_fired`) | Cell **cannot** reach `confirmed`: routed `pending_oracle` / `pending_human` per `_confirm_state` [CODE] `ledger/service.py:212-226] | **None.** Signal row only (mirrors `_signal` pattern [CODE] `floor.py:279-280]) |
| Hop timeout / exception | `CHAIN_BROKEN` (`state_reason=timeout\|hop_error`) | Cell returns to `open` on lease expiry [CODE] `tenant.py:274-279] | **None** (floor is already never-raise [CODE] `floor.py:451-452]) |
| Scope block (`_scope_ok` false) | `CHAIN_BROKEN` (`state_reason=out_of_scope`) | Cell unchanged / `blocked` | **None** — scope hook is absolute [CODE] `floor.py:434] |
| Oracle fired but evidence gate off? | — | N/A: with flag on, mint still requires proof-type ∈ mint set (G1) — a fired-but-evidencel-less claim yields **no token** | **None** (thesis) |
| Token replay `REPLAY_DRIFT` | Downstream hops `CHAIN_BROKEN` (G9); hop N's `HOP_VERIFIED` retained as history | Cell state unchanged (historical fact) | Prior hop credit retained; **no forward credit** |
| Partial path (hop 1..k verified, k+1 broken) | Every hop ≤ k stays `HOP_VERIFIED`; chain row = `CHAIN_BROKEN` | Cells keep their own oracle-driven states | Report shows hops 1..k **inside a broken story**; the story never enters the "executed" bucket unless terminal `CHAIN_COMPLETE` — mirroring today's rule that only `verified` executed-chain findings fill `executed_chains` [CODE] `reporting/service.py:300-302] |
| Depth cap reached (`SCANNER_ENGINE_CHAIN_MAX_DEPTH`) | `CHAIN_BROKEN (reason=depth_cap)` or `CHAIN_COMPLETE` if last hop verified | unchanged [CODE] `father.py:494-498, 1620] | bounded, no overrun |

Invariant [DESIGN]: **state transitions are written only by deterministic code paths** (floor verdict, ledger `_confirm_state`, replay hash compare); the LLM never writes `chain_token.state`.

---

## 6. Blast radius + flags

### Modules that change (all changes inert when flag = 0)

| Module | Change | Why minimal |
|---|---|---|
| `alembic/versions/0020_chain_capability_token.py` (NEW) | `CREATE TABLE chain_token` (+ index on `scan_id, state`) | DDL only; no runtime read if flag off |
| `src/scanner/db/models/tenant.py` | Add `ChainToken` model (~30 lines after `ChainEdge` [CODE] `tenant.py:322-333]) | Pure declaration |
| `src/scanner/agent_runtime/chain/floor.py` | G1/G3 gate + token mint/update after a hop verdict; `if not _chain_state_machine_enabled(): <legacy path>` wrapper (fail-closed, mirrors `floor.py:105-112`) | Legacy branch is the current code, untouched |
| `src/scanner/agent_runtime/chain/service.py` | Optional: read tokens for `enumerate_ranked_chains` decoration; graph build itself unchanged | `build_graph` stays as-is |
| `src/scanner/agent_runtime/engine/father.py` | `_capability_context` emits the typed `capabilities:` block when flag on (`father.py:1520-1548`); no change to `_task_for` signature | Block simply absent when flag off → prompt byte-identical |
| `src/scanner/agent_runtime/engine/escalation.py` | Feed `newly_high_impact` from `chain_token` (flag on) instead of/in addition to rebuild | Flag off ⇒ existing DELETE+build_graph path [CODE] `escalation.py:46-53` |
| `src/scanner/reporting/service.py` | Emit `executed_chain_stories` (§3) under flag; `executed_chains`/`chain_narratives` logic untouched | New key absent when off |
| `src/scanner/agent_runtime/finalize.py` | Seed `chain_token` rows for pre-existing confirmed findings during graph build (`finalize.py:331-352`) + include token count in integrity query (`finalize.py:759-767`) — gap rule extended only when flag on | Flag off ⇒ integrity query and chain build identical |
| `src/scanner/config.py` | `scanner_chain_state_machine: bool = False` | Sibling pattern `config.py:254, 261` |
| `src/scanner/scheduler/worker.py` | Add `SCANNER_CHAIN_STATE_MACHINE` to forwarded-env allowlist (if env-read) beside `SCANNER_ENGINE_CHAIN_FLOOR` [CODE] `worker.py:71-72` | One list entry |
| `src/scanner/api/schemas.py` (+ `routes/scans.py`) | Optional read-only `chain_tokens` field next to `evidence_ids` [CODE] `schemas.py:577; routes/scans.py:603` | Additive, nullable |

### Flags

| Flag | Default | Meaning |
|---|---|---|
| `SCANNER_CHAIN_STATE_MACHINE` (NEW) | `0` / `False` | Master switch for §1–§5 (tokens, worker contract field, report stories, replay) |
| `SCANNER_CHAIN_TOKEN_REPLAY` (NEW, optional sub-flag) | `0` | Enables §2.3 content recheck; `reference_only` hash+timestamp check runs whenever master flag is on |
| `SCANNER_ENGINE_CHAIN_FLOOR` (existing) | `0` [CODE] `father.py:491` | Unchanged: gates hop execution |
| `scanner_executed_chain_findings` (existing) | `False` [CODE] `config.py:254` | Unchanged: gates composed executed-chain finding |
| `scanner_chain_synthesis` (existing) | `True` [CODE] `config.py:147-149` | Unchanged: gates graph build |

**Rollout order** [DESIGN]: (1) migration + model (inert) → (2) mint path behind master flag, validated on a lab scan that `chain_token` rows == expected grants → (3) worker contract field → (4) report stories → (5) replay sub-flag. Each stage independently revertible by flag alone (D4).

### Competitor alignment note [COMPETITOR]

- Chaining with a visible proof artifact is table stakes: XBOW "case file" (chained path + working exploit + decision log), FireCompass "no exploit, no alert", Escape req-sequence + exploit + reasoning log [COMPETITOR: WS-3 §1, `COMPARISON.md` L23; `xbow/pages/page-https-xbow-com-platform.md` L42].
- FireCompass holds 30–100+ step chains **in a structured state store, not model context** — the same architectural choice as §1.3's `chain_token` table [COMPETITOR: WS-3 §1, `firecompass/pages/page-https-firecompass-com-ai-penetration-tes.md` L39].
- XBOW publishes headless-browser payload-execution as a validation gate → our `BROWSER_EXECUTED` proof-type is the buyer-visible equivalent [COMPETITOR: WS-3 §3, https://xbow.com/blog/top-1-how-xbow-did-it].
- Market gap we exploit: no market-standard evidence schema exists (formats diverge per `COMPARISON.md` L23) → §3's per-hop `proof_ref + proof_hash + proof_at + replay` is a differentiator, not a parity feature [COMPETITOR: WS-3 §1–2].

---

# Evidence Ledger

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| `chain/service.py::build_graph` synthesizes nodes/edges without executing anything | [CODE] `src/scanner/agent_runtime/chain/service.py:1-7, 123-234` | High | Read directly |
| Chain floor EXECUTES hops via `_fire` with deterministic body verdicts | [CODE] `src/scanner/agent_runtime/chain/floor.py:407-454, 232-391` | High | Probe call sites 245/293/322/355/375 |
| Chain floor default-OFF (`SCANNER_ENGINE_CHAIN_FLOOR=0`) | [CODE] `src/scanner/agent_runtime/engine/father.py:487-491` | High | Confirmed by unit test `tests/unit/engine/test_father_chain.py:10-12` |
| Executed-chain finding writer default-OFF | [CODE] `src/scanner/config.py:249-254`; gate `chain/floor.py:105-112, 445-450` | High | Explains `executed_chains=0` |
| `reporting/service.py` fills `executed_chains` only from verified executed-chain findings | [CODE] `src/scanner/reporting/service.py:298-318` (count at 390) | High | Peer context matches |
| `chain_node` schema: (scan_id, finding_id, capability, attrs jsonb) | [CODE] `alembic/versions/0008_add_chain_and_approval.py:22-40`; `db/models/tenant.py:297-309` | High | Quoted in §0.2 |
| Node attrs snapshot proof_of_concept + evidence_path | [CODE] `chain/service.py:167-174` | High | Consumed report-side only (`reporting/service.py:98-99`) |
| `ChainStep` carries no proof reference | [CODE] `chain/service.py:38-43, 336-343` | High | finding_id/capability/rationale only |
| Escalation prompt carries capability + title + endpoint only | [CODE] `engine/father.py:1520-1548` | High | 1530-1536 is the assembly |
| Scan brief carries finding titles only | [CODE] `engine/scan_brief.py:114, 149-152, 266` | High | `_MAX_FINDINGS=20` |
| Progress digest carries titles only | [CODE] `engine/runtimes/agents_runtime.py:1010-1021` | High | Reprompt path |
| Zero `evidence_ids`/`proof_ref` consumers in `chain/*` | grep over `src/scanner` (evidence_ids hits: ledger/api/models only) | High | Absence-of-evidence claim; grep + manual read |
| Graph DELETE+rebuild makes `chain_node` unsuitable for token store | [CODE] `engine/escalation.py:47-49`; `agent_runtime/finalize.py:340-341`; `engine/father.py:1064-1068` | High | Basis for new table |
| File-mediated carry exists: floor re-reads confirmed findings each invocation | [CODE] `chain/floor.py:146-162, 426-450` | High | Hop N output = hop N+1 input |
| OOB token carries across time into a verified finding | [CODE] `floor.py:350-362, 370-382`; `oob/service.py:490, 510` | High | Async callback confirm |
| Auth artifact read by floor hops and surfaced to workers | [CODE] `floor.py:422`; `engine/scan_brief.py:84-101` | High | Workspace-convention carry |
| Ledger confirm gate fields (`_EVIDENCE_FIELDS`) | [CODE] `ledger/service.py:175-187` | High | Basis for ARTIFACT_READ |
| Oracle-first confirm disposition | [CODE] `ledger/service.py:205-226` | High | pending_oracle/pending_human routing |
| `is_deterministic_oracle` set (non-timing exploit_floor + oob_callback) | [CODE] `reporting/exploit_quality.py:118-130` | High | Basis for ORACLE_FIRED |
| Capsule method values (`browser_har`, `oob_callback`, vm) | [CODE] `reporting/exploit_quality.py:174-193` | High | Basis for BROWSER_EXECUTED |
| Observed `verification_method` writers | grep over `src/ tests` (oob_callback, deferred_canary, deterministic, executed_chain, exploit_floor:*, recon_floor:*, manual) | High | Enum derivation input |
| Existing flags/defaults for chain features | [CODE] `config.py:147-149, 249-261`; `father.py:487-498` | High | D4 pattern source |
| Env-forward allowlist includes chain flags | [CODE] `scheduler/worker.py:71-72` | High | Where the new env flag must be listed |
| Detached deterministic proof re-fire exists (replay seam) | [CODE] `engine/detached_verify.py:7-10, 84-99, 124-126` | High | REPLAY `content_recheck` reuse |
| Ledger cell has `evidence_ids` + lease columns; EvidenceObject PK/created_at | [CODE] `db/models/tenant.py:271, 274-281, 221-244` | High | Token column design basis |
| Impact formula `len*(high_impact+1)` | [CODE] `chain/service.py:317-319` | High | Reused in §3 schema |
| Latest alembic revision = 0019 (next is 0020) | `alembic/versions/` listing | High | Migration name justified |
| Competitor chaining + proof-artifact mechanisms | [COMPETITOR] `improvment-research/research-agent-nova-02/ws3/WS-3-competitor-mechanisms.md` §1–2 (citing `competitor-research/COMPARISON.md` L13/L15/L23; `xbow/pages/...platform.md` L42; `firecompass/pages/...ai-penetration-tes.md` L39) | Medium | Secondary citation via WS-3; underlying files exist in `competitor-research/` |
| No market-standard evidence schema | [COMPETITOR] WS-3 §1 gap cell (`COMPARISON.md` L23) | Medium | Supports §3 differentiation |
| FireCompass state-store (not model-context) chain storage | [COMPETITOR] WS-3 §1 (`firecompass/pages/...ai-penetration-tes.md` L39) | Medium | Architectural precedent for `chain_token` |
| XBOW browser-execution validation gate | [COMPETITOR] WS-3 §1/§3 (https://xbow.com/blog/top-1-how-xbow-did-it) | Medium | Precedent for `BROWSER_EXECUTED` |

**Design choices flagged `[DESIGN]` (no citations needed, not factual claims about current code):** new `chain_token` table vs. column extension; state machine + guards; ProofType mint rule; REPLAY hash/timestamp contract; worker `capabilities:` field shape; `executed_chain_stories` report key; failure-semantics table; flag/rollout plan.

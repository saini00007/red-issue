# WS-4 — CHAINING STATE MACHINE DESIGN
`ws4_chain_statemachine` · lead `research-agent-falcon-02` · repo `feat/alpha-observability` @ `f75608f`
**DESIGN ONLY. No repo file touched. No exploitation output: mechanisms, contracts, enums, capability labels.**

---

## A. DESIGN RATIONALE — the eight defects being fixed

1. **Hop N+1's target is drawn from module-level constants, never from hop N.** `_METADATA_URLS` (3), `_BUCKET_URLS` (3), `_SECRET_FILES` (8) are frozen tuples at `chain/floor.py:59-101`; the three loops that consume them (`floor.py:241`, `:289`, `:318`) iterate them unconditionally. Nothing hop N observed can reach hop N+1's target set.
2. **The per-hop data structure cannot carry evidence.** `_Ctx` is `{sh, surface, tdir, wd, cookies, bearer, dom}` (`floor.py:134-143`) — seven per-invocation constants, zero per-finding fields. All six hops take `(ctx, url, param, res)` (`floor.py:393`). The only per-finding data crossing the boundary is `_finding_target`'s `(url, param)`, derived from `affected_endpoint`/`param` only (`floor.py:190-201`).
3. **The evidence path is already in hand and is discarded.** `_fire` returns `(stdout, exit_code, evidence_path)` (`exploit_floor.py:2505`, docstring `:2507`); every chain-floor caller binds it to `_path` and drops it (`floor.py:245`, `:293`, `:322`). So the raw proof exists on disk at hop time and never crosses the boundary.
4. **`_hop_credential` is a deliberate terminal.** It performs zero network I/O and only reopens classes (`floor.py:385-390`, ponytail: "DON'T build a credential-stuffer"). All five CREDENTIAL-granting classes (`capabilities.py:49-52,56`) therefore produce terminal nodes by construction — `CREDENTIAL` reaches a finding but never a hop that uses the credential.
5. **Six of twelve capabilities have no hop at all.** `_HOPS` (`floor.py:397-404`) covers `METADATA_ACCESS, CLOUD_STORAGE, FILE_READ, REDIRECT, INTERNAL_HTTP, CREDENTIAL`. Absent: `RCE, SESSION, DB_READ, PII_READ, CROSS_PRINCIPAL_READ`. An `RCE` or `DB_READ` finding grants capabilities the floor can never spend.
6. **The persistence layer cannot represent an executed hop.** `ChainEdge` has exactly three data columns plus `rationale` (`tenant.py:322-333`) with `UniqueConstraint("from_node","to_node")` (`tenant.py:326`) — an executed hop would collide with the inferred edge and overwrite its rationale. `ChainNode` has `UniqueConstraint("scan_id","finding_id","capability")` (`tenant.py:299`), so one finding cannot hold the same capability at two different derived targets.
7. **The buyer-facing "what this grants" text is LLM free-text while the machine capability comes from a table — two sources of truth that can disagree.** `evidence_paths["chain"] = {"prerequisite","gained"}` is copied verbatim off the agent-written finding row (`ingest_findings.py:436-438`) and rendered into `attacker_narrative` by `_derive_attacker_narrative` (`ingest_findings.py:116-121`). The machine side derives capability from `GRANTS` (`capabilities.py:170-178`). The old free-text linker is now dead code: `_link_match` (`chain/service.py:110-120`) has zero call sites.
8. **The narrative layer is prose-first, and prose is merged before the report is built.** `reporting/narrative.py` is 5,965 bytes; `build_narrative_prompt` (`:45`) and `merge_report_addons` (`:68`) emit `risk_narrative` / `methodology_narrative` / `finding_narratives` into `finalize_addons.json`, and `finalize.py:357-371` calls it **before** `generate_report` at `finalize.py:374`. Nothing in that path is machine-checkable.

Live consequence (from H3 verification, not re-derived here): 0 `executed_chain` findings in 43 scans despite `SCANNER_EXECUTED_CHAIN_FINDINGS=true` + `SCANNER_ENGINE_CHAIN_FLOOR=1`; `_write_executed_chain` (`floor.py:204-228`) has never fired. 195 `chain_node` rows / 464 `chain_edge` rows — densely inferred, never executed onward.

---

## B. DELIVERABLE 1 — Chain state machine

### B.1 State machine

States live on the **capability token** (B.3), one token per (confirmed finding × granted capability), not on the graph edge.

```
                    ┌──────────────────────────────────────────────┐
                    │                                              │
   UNMINTED ──(mint: confirmed finding ∧ GRANTS[vc]≠∅)──▶ MINTED │
                    │                                     │        │
                    │                       (derive_targets(proof) │
                    │                        yields ≥1 target)    │
                    │                             ▼                │
                    │                          DERIVED ────────────┼──(yields 0 ∧ flag
                    │                             │                │   SCANNER_CHAIN_DERIVED_ONLY)
                    │                             │                ▼         └──▶ STATIC_FALLBACK
        (scope_ok ∧ ¬seen_hops ∧ budget)          │
                    │                             ▼
                    │  (out-of-scope ∨ budget ∨ HIGH_IMPACT w/o approval)
                    │                             ▼
                    │                          SUPPRESSED          SUPPRESSED
                    │        (fire hop)        │
                    │                             ▼
                    │                          FIRED
                    │             ┌───────────────┼───────────────┐
                    │  oracle POS  │  oracle NEG   │  oracle UNK   │  (raised)
                    │             ▼               ▼               ▼
                    │          PROVEN          REFUTED      INDETERMINATE
                    │             │
                    │             └──(child finding grants capability)──▶ new token,
                    │                                                        depth+1, MINTED
                    ▼
              (finding later downgraded by A1 verifier, finalize.py:176-186
               + _flip_jsonl_verified, finalize.py:947-973) ──▶ REVOKED
```

**The load-bearing invariant:** `PROVEN` is the *only* state that mints a finding or a child token. `REFUTED` and `INDETERMINATE` both mint nothing — the difference is that `REFUTED` records a *deterministic negative* (an oracle ran and said no) while `INDETERMINATE` records that no oracle could decide. Collapsing them is how a tool ends up claiming "tested, clean" for a blind primitive.

| state | mints finding | mints child token | counts toward `verified_chain_count` | counts toward buyer narrative |
|---|---|---|---|---|
| MINTED / DERIVED / FIRED | no | no | no | as `attempted` |
| PROVEN | **yes** | **yes** | **yes** | as `proven` |
| REFUTED | no | no | no | as `tested_negative` |
| INDETERMINATE | no | no | no | as `untested` (never as clean) |
| SUPPRESSED | no | no | no | as `not_attempted` |
| STATIC_FALLBACK | no | no | no | not rendered |
| REVOKED | — | — | no | rendered struck-through with the downgrade reason |

`REVOKED` is new and required: `_verify_findings` downgrades findings at finalize (`finalize.py:176-186`) and `_flip_jsonl_verified` rewrites `findings.jsonl` (`finalize.py:947-973`) **after** the chain floor has already fired hops off that finding. Today a chain built from a subsequently-debunked primitive stays in `chain_node` forever because `build_graph` is DELETE-then-INSERT at `finalize.py:340-341` but the *hop* records would persist. `REVOKED` makes that reversal explicit rather than silent.

### B.2 Transitions as a table

| # | from | event | guard | to | traffic? |
|---|---|---|---|---|---|
| T1 | — | `_read_confirmed` yields finding `f` | `verified ∧ proof_of_concept` (`floor.py:160`) ∧ `GRANTS[vc(f)] ≠ ∅` | MINTED (one per cap) | no |
| T2 | MINTED | `derive_targets(proof_artifact)` | returns ≥1 `DerivedTarget` ∧ all `_scope_ok` | DERIVED | no |
| T3 | MINTED | `derive_targets` returns 0 | flag `SCANNER_CHAIN_STATIC_FALLBACK` off | SUPPRESSED | no |
| T4 | DERIVED | pop target `t` | `host ∈ scope` (`floor.py:434`) ∧ `(cap,url,param) ∉ seen_hops` (`floor.py:437-440`) ∧ budget | FIRED | **yes** |
| T5 | DERIVED | pop target `t` | `cap ∈ HIGH_IMPACT` (`capabilities.py:96-98`) ∧ no `scan_approval` row | SUPPRESSED | no |
| T6 | FIRED | oracle returns `POSITIVE` | `proof_type ∈ ProofType.LICENSES_HOP` | PROVEN | — |
| T7 | FIRED | oracle returns `NEGATIVE` | oracle ran, transport_ok | REFUTED | — |
| T8 | FIRED | oracle returns `UNKNOWN` | `¬transport_ok` ∨ no callback ∨ no diff | INDETERMINATE | — |
| T9 | PROVEN | child finding `c` persisted | `GRANTS[vc(c)] ≠ ∅` ∧ `depth+1 ≤ max_depth` | new token MINTED | no |
| T10 | PROVEN | A1 verifier downgrades source finding | `finalize.py:176-186` | REVOKED | no |
| T11 | any | `max_depth` (`_MAX_HOPS`-style) or `_MAX_HOPS=40` budget (`floor.py:102`) reached | — | SUPPRESSED | no |

### B.3 Hop context data structure — the evidence-carrying replacement

New module `src/scanner/agent_runtime/chain/token.py`. Pure dataclasses, no I/O, no settings import (mirrors the `exploit_floor` builders/parsers split).

```python
@dataclass(frozen=True)
class ProofArtifact:
    """Hop N's proof, carried forward. Bounded + redacted at construction."""
    evidence_refs: tuple[str, ...]     # evidence_object ids + tool_output/<name>.log paths
    request_digest: str                # sha256 of the replayable request; the raw never leaves _fire
    response_excerpt: str              # redacted slice, hard cap 2000 (mirrors _CAP_LEN)
    marker: str | None                 # the per-scan canary the oracle matches against
    control_ref: str | None            # evidence ref of the matched CONTROL capture
    tool_invocation_id: str | None     # surface.persist_invocation row (exploit_floor.py:2513-2515)

@dataclass(frozen=True)
class DerivedTarget:
    """A hop N+1 target DERIVED from hop N's proof — with its derivation recorded."""
    url: str
    param: str | None
    method: str                        # GET default
    capability: str                    # Capability enum value this target is for
    origin: str                        # "proof_body"|"proof_header"|"ref_field"|"invocation_output"|"static_table"
    derive_rule: str                   # named extractor id, e.g. "imds_iam_role", "ref_key:id", "root_element_routes"
    source_ref: str                    # which ProofArtifact.evidence_ref it came from

@dataclass(frozen=True)
class CapabilityToken:
    token_id: str                      # uuid4 hex; stable across waves via the file
    scan_id: str
    depth: int
    capability: str                    # Capability enum value
    state: str                         # ChainTokenState (B.1)
    source_finding_id: str | None      # uuid when present, else dedup_hash (service.py:162)
    source_dedup_hash: str | None
    source_vuln_class: str
    source_endpoint: str
    proof_type: str                    # ProofType (Deliverable 2)
    proof: ProofArtifact
    derived: tuple[DerivedTarget, ...] # EMPTY when nothing derivable
    parent_token_id: str | None
    hop_key: str                       # persisted (cap,url,param) — survives seen_hops loss
```

**How hop N+1 RECEIVES it.** One new dispatcher; the six existing hop signatures are untouched.

```python
@dataclass(frozen=True)
class HopInput:
    """What a hop actually receives. Degenerates to the legacy (url, param) when off."""
    url: str
    param: str | None
    token: CapabilityToken | None     # None ⇒ flag off ⇒ legacy path, byte-identical
    method: str = "GET"

_HopFn = Callable[[_Ctx, HopInput, ChainFloorResult], Awaitable[None]]
```

The dispatcher replaces the single `await hop(ctx, url, param, res)` at `floor.py:446` with:

```
if not _chain_derived_targets_enabled():        # single gate, top of run_chain_floor
    <the existing loop body, verbatim>          # url/param only, static tables only
else:
    for token in _read_tokens(work_dir):
        for tgt in token.derived or _static_fallback(target_capability):
            await _dispatch_derived(ctx, token, tgt, res)
```

`_dispatch_derived` routes `tgt.origin`:
- `"static_table"` → the legacy `_hop_metadata/_hop_bucket/_hop_file_read/_hop_redirect/_hop_internal` with `HopInput(url, param, token=None)` — the legacy target, still available, still counted, but now labelled `origin="static_table"` so the narrative can say "guessed" not "derived".
- any other origin → the new `_hop_derived` family, which receives `token.proof` and is free to use the marker, the control ref, and the raw excerpt.

**Derivers** (`chain/derive.py`, pure `ProofArtifact -> tuple[DerivedTarget, ...]`, no I/O). Every deriver is a named, individually unit-testable rule; an unextractable body returns `()`:

| `derive_rule` | input axis | emits |
|---|---|---|
| `imds_iam_role` | role-name line observed in the hop-N body (`floor.py:66-68` lookahead shape) | the *specific* role path, `origin="proof_body"` |
| `imds_instance_identity` | instance-identity document shape (`floor.py:72-75`) | the identity document path |
| `bucket_endpoint_listing` | `<ListBucketResult>` / `<EnumerationResults>` / `"Contents":` (`floor.py:84-86`) | the listing URL + the container/key prefix the body actually names |
| `secret_material_shape` | a `(label, secret)` pair in a stored secrets finding's excerpt (`floor.py:97-101` shape) | an `auth_replay` descriptor — a **pointer** into the evidence store (`secret_material_ref`), never the material inline |
| `root_element_routes` | root element of a file-read proof body (php/doctype/project/settings/shebang/JSON-key-block) | config paths read off the observed tree, not the static 8-tuple |
| `ref_key:<key>` | object reference keys already implemented at `exploit_floor.py:966-980` (`_REF_KEYS`, `_walk_ref`, `_extract_object_ref`) | the referenced object URL for `CROSS_PRINCIPAL_READ` |
| `invocation_output` | the RCE proof's own `tool_invocations` summary (`exploit_floor.py:2513-2515`) — the process user, cwd, config dir the command ran under | `file_read_at_path` on the observed config dir |
| `har_link` | `sync_har_proof` request/response pair (`finalize.py:310`) | the recorded method+URL of the authed request |

Note `ref_key:*` and `invocation_output`: **both mechanisms already exist in `exploit_floor` and are unused by the chain floor.** The design does not invent them; it routes them.

### B.4 Token persistence

**Runtime channel — file.** `/work/chain_tokens.jsonl`, append-only, one JSON object per line — the same contract as `findings.jsonl` (`floor.py:149`), `oob_registry.jsonl` (`floor.py:166-167`) and `exploit_floor_signals.jsonl` (`exploit_floor.py:2414-2419`). The file is the authoritative runtime channel because the per-scan toolserver process is gone by finalize time and the salvage/orphan finalize paths only ever see `/work`. **Do not** attempt to read tokens from the DB during the scan.

**Durable channel — DB.** Two new tables, alembic `0020_chain_tokens.py` (`down_revision = "0019"` per `alembic/versions/0019_add_scan_engine_models.py:7-8`). Tenant-scoped by `search_path`, matching every other table.

```sql
CREATE TABLE chain_token (
  token_id            uuid PRIMARY KEY,
  scan_id             uuid NOT NULL REFERENCES scans(scan_id) ON DELETE CASCADE,
  depth               int  NOT NULL DEFAULT 0,
  capability          text NOT NULL,
  state               text NOT NULL,
  source_finding_id   uuid,
  source_dedup_hash   text,
  source_vuln_class   text,
  source_endpoint     text,
  proof_type          text,
  proof_json          jsonb NOT NULL DEFAULT '{}'::jsonb,
  derived_json        jsonb NOT NULL DEFAULT '[]'::jsonb,
  parent_token_id     uuid REFERENCES chain_token(token_id) ON DELETE SET NULL,
  hop_key             text,
  created_at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_chain_token_scan_state ON chain_token (scan_id, state);

CREATE TABLE chain_hop (
  hop_id               uuid PRIMARY KEY,
  scan_id              uuid NOT NULL REFERENCES scans(scan_id) ON DELETE CASCADE,
  token_id             uuid NOT NULL REFERENCES chain_token(token_id) ON DELETE CASCADE,
  hop_index            int  NOT NULL,
  capability           text NOT NULL,
  url                  text NOT NULL,
  param                text,
  method               text NOT NULL DEFAULT 'GET',
  origin               text NOT NULL,      -- proof_body | ref_field | ... | static_table
  derive_rule          text,
  source_ref           text,
  proof_type_expected  text,
  proof_type_observed  text,
  verdict              text,               -- POSITIVE | NEGATIVE | UNKNOWN
  child_finding_id     uuid,
  evidence_ref         text,
  fired_at             timestamptz NOT NULL DEFAULT now(),
  UNIQUE (token_id, url, param)
);
CREATE INDEX idx_chain_hop_scan ON chain_hop (scan_id, hop_index);
```

**Why a new table and not `chain_edge`/`chain_node`** (defect 6, [CODE] `tenant.py:299`, `:326`):
- `chain_edge` is `UniqueConstraint("from_node","to_node")` with columns `(scan_id, from_node, to_node, rationale)` only. An executed hop from the same node pair as an inferred edge would either raise on the unique constraint or overwrite `rationale` — destroying the human sentence that `EDGE_RATIONALE` (`capabilities.py:106-162`) produced. An inferred reachability edge and an executed, proof-bearing hop are **different facts** and must not share a row.
- `chain_node` is `UniqueConstraint("scan_id","finding_id","capability")`. A single finding holding `METADATA_ACCESS` against three different derived targets cannot be three nodes. The derived multiplicity is exactly the new information, so it cannot live there.
- `chain_node`/`chain_edge` stay `scan_id`-scoped (`finalize.py:65-66` counts them; `tenant.py:305`, `:330` both carry the FK) — the new tables match.

**Migration contract:** strictly additive. No `ALTER`, no `DROP`, no change to `chain_node`/`chain_edge`. Downgrade drops the two new tables only. `finalize.py`'s DELETE-then-INSERT idempotency (`finalize.py:340-341`) is mirrored by `DELETE FROM chain_hop WHERE scan_id=:s` / `DELETE FROM chain_token WHERE scan_id=:s` in the same block, so a second finalize cannot double-count.

### B.5 Flags

- `SCANNER_CHAIN_TOKEN_PERSIST` (`scanner_chain_token_persist`, **default OFF**) — mint + persist tokens; populate `chain_token`. No new traffic.
- `SCANNER_CHAIN_DERIVED_TARGETS` (`scanner_chain_derived_targets`, **default OFF**) — dispatch hops at `origin != "static_table"` targets.
- `SCANNER_CHAIN_PARENT_LINK` (`scanner_chain_parent_link`, **default OFF**) — write parent linkage + `chain_hop` rows.

Splitting persist from dispatch is deliberate: it ships the **audit half** of the differentiator (competitor gap G4 — nobody else has a re-checkable chain record) with **zero new traffic**, so the product can sell the chain *record* before it sells the chain *executor*.

### B.6 Byte-identical-when-off

| concern | proof |
|---|---|
| no token file read | gate is the first statement of `run_chain_floor`; the pre-existing `for f in _read_confirmed(...)` loop at `floor.py:426-452` is not entered on the new branch and `_read_confirmed` is unchanged |
| no new network | the only `_fire` call sites remain `floor.py:245`, `:293`, `:322`, `:355`, `:375` — zero added |
| no DB write | no `chain_token`/`chain_hop` INSERT outside the gated finalize block; `build_graph` (`chain/service.py:230`) is untouched |
| report output | new report key only; `chain_narratives` (`reporting/service.py:402`) untouched |
| findings.jsonl | no new keys appended when all chain flags off |

---

## C. DELIVERABLE 2 — Parent linkage, proof-type enum, replay contract

### C.1 (a) Parent-finding linkage

**Three places, one source of truth.** The authoritative record is `chain_hop`; the finding carries a denormalised copy in its existing `evidence_paths` JSONB — the repo's established pattern for "no dedicated column" (`ingest_findings.py:426-438`, `finalize.py:697-700`, `finalize.py:886-894`).

**1. `chain_hop` columns** (in B.4): `parent_finding_id` (via `token_id → chain_token.source_finding_id`), `proof_type_expected`, `verdict`, `child_finding_id`. The parent edge is a join, not a duplicated column — one place to keep consistent.

**2. `findings.evidence_paths["chain"]`** — the key already exists and already carries `{"prerequisite","gained"}` model free-text (`ingest_findings.py:436-438`). It is **extended, not replaced**, so old readers keep working:

```json
"chain": {
  "prerequisite": "<legacy freetext, unchanged>",
  "gained":       "<legacy freetext, unchanged>",
  "parent_finding_id":  "uuid | null",
  "parent_proof_type":  "ProofType value | null",
  "token_id":           "uuid | null",
  "hop_index":          2,
  "hop_verdict":        "POSITIVE",
  "derive_rule":        "imds_iam_role",
  "target_origin":      "proof_body"
}
```

New keys are written **only** by `chain/floor.py` and only when `scanner_chain_parent_link` is on. `ingest_findings.py` merges with `{**(evidence_paths or {}), "chain": chain_meta}` semantics — the writer must use the same reassign-not-mutate form (`finalize.py:699-700`) so SQLAlchemy flushes the JSONB.

**3. `chain_node.attrs`** gains `{"parent_finding_id", "parent_proof_type", "token_id", "hop_index", "proof_type", "derive_rule"}` — `attrs` is free-form JSONB (`tenant.py:308`) and `build_graph` already stuffs `vuln_class/endpoint/proof_of_concept/evidence_path/reasoning` (`chain/service.py:169-179`). Written by `build_graph` when the flag is on; when off, `attrs` is byte-identical.

**The LLM free-text defect (rationale #7) is fixed here, not by deleting keys:** `derive_rule` + `proof_type` + `token_id` are the *machine* answer to "what licensed this hop". `prerequisite`/`gained` remain as the model's prose. `I4_NO_ASSERTION_CONFIRM` (§D.2) requires the narrative to cite the machine triple; a node whose only justification is `prerequisite`/`gained` renders as `ASSERTION_ONLY` and cannot be `PROVEN`.

### C.2 (b) Canonical PROOF-TYPE ENUM

New module `src/scanner/agent_runtime/chain/proof.py`, `class ProofType(StrEnum)`. Every member names the code that can produce it, so membership is not a judgement call.

| member | value | strength | producer [CODE] | licenses a hop? |
|---|---|---|---|---|
| `ASSERTION_ONLY` | `assertion_only` | assertion | no producer — the fallback when no machine proof exists (`_confirm_state` returns `pending_human`/`pending_oracle`, `ledger/service.py:212-226`) | **NO** |
| `NO_PROOF` | `no_proof` | none | sentinel for a token with an empty artifact | **NO** |
| `OOB_CALLBACK` | `oob_callback` | machine | `oob/service.py:490,510` (`verification_method="oob_callback"`) | YES |
| `DEFERRED_CANARY` | `deferred_canary` | machine (delayed) | `oob/service.py:356,371` | NO — second-order, minted by `scanner_deferred_confirmation` (`config.py:276`); may inform, never license |
| `CANARY_ECHO` | `canary_echo` | machine | `new_canary` `exploit_floor.py:723`; `parse_xss_reflection` `:666`; `classify_reflection` `:686`; `parse_upload_echo` `:1159`; `parse_crlf_split` `:2043`; `parse_openredirect` `:1876`; `_append_xss_canary` `:2337` | YES |
| `CONTROL_DIFF` | `control_diff` | machine | `response_diff` → `DiffVerdict` `exploit_floor.py:1224-1265`; `parse_boolean_diff` `:1811`; `parse_defaultcreds` `:2143`; `parse_jwt_forge` `:1949`; `parse_session_fixation` `:1993`; `parse_session_no_rotation` `:2002`; `parse_revoked_replay` `:2011` | YES |
| `CROSS_PRINCIPAL_DIFF` | `cross_principal_diff` | machine | `_two_request_oracle` `:2525`; `diff_cross_tenant` `:1387`; `diff_access` `:1297`; `diff_resource_ref` `:1424` | YES |
| `TIME_BLIND` | `time_blind` | weak | `_time_probe` `:1732`; `parse_time_blind` `:1784`; `_BOOL_DIFF_RATIO` neighbour `_TIME_BLIND_SECONDS=5` `:1720` | **NO** — ingest already demotes `:sqli-time`/`:cmdi-time` to `weak_confirmation` (`ingest_findings.py:79,88`) |
| `STRUCTURED_MARKER` | `structured_marker` | weak | `_IMDS_CRED_RX` `floor.py:66-68`; `_BUCKET_LIST_RX` `floor.py:84-86`; `_SECRET_RX` `floor.py:97-101`; `_PASSWD_RX` `exploit_floor.py:1837`; `_CREDENTIAL_RX` `:321` | only under `SCANNER_CHAIN_STRUCTURED_MARKER_PROOF` |
| `TOOL_INVOCATION` | `tool_invocation` | machine | `parse_sqlmap` `:1005`; `parse_dalfox` `:1063`; `parse_nuclei` `:1016`; `parse_upload_location` `:1117`; `parse_ssti` `:1709`; `parse_lfi` `:1847` | YES, except `nuclei_match_is_version_only` (`:1052`) → relabels to `needs_confirmation` (`config.py:268`) |
| `DESYNC` | `desync` | machine | `parse_smuggling_desync` `:2083` | NO — needs a timing window, not replayable |
| `REPLAY_HAR_PAIR` | `replay_har_pair` | machine | `sync_har_proof` `finalize.py:310`; capsule `method="browser_har"` `exploit_quality.py:176` | YES |
| `EXECUTED_CHAIN` | `executed_chain` | machine (composed) | `_write_executed_chain` `floor.py:204-228` | n/a — a chain-level finding, not a primitive |
| `DETERMINISTIC_ORACLE` | `deterministic_oracle` | machine (umbrella) | `inventory_ingest.py:919` (`verification_method="deterministic"`) | YES |

```python
LICENSES_HOP: frozenset[ProofType] = frozenset({
    ProofType.OOB_CALLBACK, ProofType.CANARY_ECHO, ProofType.CONTROL_DIFF,
    ProofType.CROSS_PRINCIPAL_DIFF, ProofType.TOOL_INVOCATION,
    ProofType.REPLAY_HAR_PAIR, ProofType.DETERMINISTIC_ORACLE,
})

STRENGTH: dict[ProofType, str] = {
    ProofType.OOB_CALLBACK: "machine", ProofType.CANARY_ECHO: "machine",
    ProofType.CONTROL_DIFF: "machine", ProofType.CROSS_PRINCIPAL_DIFF: "machine",
    ProofType.TOOL_INVOCATION: "machine", ProofType.REPLAY_HAR_PAIR: "machine",
    ProofType.DETERMINISTIC_ORACLE: "machine", ProofType.EXECUTED_CHAIN: "machine",
    ProofType.STRUCTURED_MARKER: "weak", ProofType.TIME_BLIND: "weak",
    ProofType.DEFERRED_CANARY: "weak", ProofType.ASSERTION_ONLY: "assertion",
    ProofType.NO_PROOF: "none", ProofType.DESYNC: "weak",
}
```

**Classifier.** `classify(finding: Mapping) -> ProofType` is a pure, total function mirroring `is_deterministic_oracle` (`exploit_quality.py:118-130`) — the repo already has the exact precedent of a single source of truth for the trust gates. Resolution order:
1. `evidence_paths.verification_status ∈ _UNCONFIRMED_STATUSES` (`exploit_quality.py:37-38`) → `ASSERTION_ONLY`.
2. explicit `evidence_paths.chain.proof_type` (set by a chain-floor writer) → that value.
3. `verification_method` → prefix table (`oob_callback`, `deferred_canary`, `executed_chain`, `exploit_floor:*`, `deterministic`, `chain:*`).
4. `oob_token` present → `OOB_CALLBACK`.
5. `evidence_paths.objects` with `method == "browser_har"` → `REPLAY_HAR_PAIR`.
6. no `proof_of_concept` **and** no `evidence_path` → `NO_PROOF`.
7. otherwise → `ASSERTION_ONLY`.

`ProofType` is also stamped onto new findings via `verification_method = f"chain:{derive_rule}"`, which keeps `is_deterministic_oracle` True (prefix `exploit_floor:` won't match, so `exploit_quality.py:130` must be extended to accept `chain:` in the same clause — a one-line, flag-independent change that must be proven no-op for existing rows: existing rows have `exploit_floor:` or `oob_callback`, never `chain:`).

**Backward compatibility:** `classification_of_existing_row` must reproduce today's behaviour exactly for every `verification_method` value already in production, or the ingest `provisional` stamp (`ingest_findings.py:476-477`) and the A1 verify skip (`finalize.py:1078`) shift. That is a test obligation, not an assumption.

### C.3 (c) Replay contract

**Builds on `api/retest.py`, does not replace it.** That module is 151 lines, already gated on `scanner_retest_enabled` (default `False`, `config.py:508`), already re-checks scope with `in_scope` (`retest.py:136`), already refuses to replay body-borne or marker-less proofs (`refireable` `retest.py:64-92`), and already stamps a 3-value state (`retest.py:12`). The gap is that it is **per-finding, GET-only, and its verdict is a string substring match** (`_verdict` `retest.py:95-96`) with no proof-type typing and no chain context.

**Flag:** `SCANNER_CHAIN_REPLAY_V2` (`scanner_chain_replay_v2`, **default OFF**). Off ⇒ the route does not exist; `POST /findings/{id}/retest` is untouched.

#### INPUT

```
POST /api/scans/{scan_id}/chains/{token_id}/replay
Authorization: Bearer <tenant key>
{
  "hops":        "all" | [0, 1, 2],        // optional; default "all" up to max_depth
  "proof_types": ["CONTROL_DIFF"],          // optional filter; absent ⇒ use each hop's proof_type_expected
  "identity":    "anonymous" | "primary" | "tenant_b" | "named:<label>",
                                     // which RECORDED identity to replay under; never credentials
  "replay_window": "scan" | "as_of:<iso8601>"   // default "scan"
}
```

Explicitly **not** in the input: any URL, header, body, or secret. The server resolves every target from the stored token. A caller cannot aim the replay at an arbitrary host — this is what makes the feature auditable rather than an attack tool.

#### PRE-FLIGHT REJECTIONS (zero traffic emitted)

| code | condition | grounded in |
|---|---|---|
| `R1_OUT_OF_SCOPE` | resolved host ∉ scan scope | same `in_scope` gate, `retest.py:131-137` |
| `R2_NO_REPLAYABLE_REQUEST` | recorded request is body-borne or not re-fireable | `refireable` `retest.py:80-91` |
| `R3_PROOF_MISSING_MARKER` | excerpt is empty or redacted — nothing to match | `retest.py:85-86` already refuses `[REDACTED` |
| `R4_PROOF_TYPE_NOT_REPLAYABLE` | `proof_type ∈ {TIME_BLIND, DESYNC, DEFERRED_CANARY, ASSERTION_ONLY, NO_PROOF}` | `LICENSES_HOP` ∩ replayable set (§C.2) |
| `R5_TOKEN_NOT_PROVEN` | `chain_token.state ∉ {PROVEN, REFUTED}` | a replay of an unproven token is a scan, not a replay |

#### OUTPUT

```json
{
  "schema_version": "chain.replay/1",
  "replay_id": "uuid",
  "scan_id": "uuid", "token_id": "uuid", "hop_id": "uuid",
  "hop_index": 1,
  "identity_used": "anonymous",
  "scope": {"declared_targets": ["host.example"], "host": "host.example", "in_scope": true},
  "replay_window": {"scan_started_at": "iso8601", "scan_ended_at": "iso8601", "mode": "scan"},
  "proof_type_declared": "CONTROL_DIFF",
  "proof_type_observed": "CANARY_ECHO",
  "checks": [
    {"check_id": "transport_ok",      "observed": true},
    {"check_id": "control_denied",    "observed": true, "control_status": 401},
    {"check_id": "marker_present",    "observed": true},
    {"check_id": "marker_unique_to_scan", "observed": true}
  ],
  "verdict": "REPRODUCED",
  "chain_state_after": {"state": "PROVEN", "child_finding_id": "uuid"},
  "replay_digest": "sha256:…",
  "attestation": {
    "verifier": "abhedi-red/replay@1",
    "runner": "agent" | "auditor",
    "at": "iso8601",
    "tool_invocation_id": "uuid"
  }
}
```

#### Verdict domain — exactly three values, reusing `retest`'s

`REPRODUCED | NOT_REPRODUCED | INDETERMINATE` ⇔ `still_vulnerable | fixed | inconclusive` (`retest.py:12`). **No fourth "safe" value, ever.** A replay that could not run returns `INDETERMINATE`, never `NOT_REPRODUCED` — the same honesty rule `_apply_verdict` already enforces in the other direction (`finalize.py:935-941`, "never fail open").

#### Invariants (the audit-grade part)

- **I-R1 READ-ONLY.** A replay writes `evidence_paths.replay` (append-only list) and nothing else. It never writes a finding, never touches `findings.verified`, never touches a `ledger_cell.state`. An auditor re-firing a proof cannot mutate the client's record of the scan. This is stricter than `run_retest`, which stamps `evidence_paths.retest` on the finding (`retest.py:146`) — same immutability property, but the replay additionally cannot create rows.
- **I-R2 DETERMINISM.** The response is a pure function of (stored `ProofArtifact`, identity label, scope, target state at replay time). `replay_digest = sha256(canonical_json(response − attestation))` — the attestation is excluded precisely so a re-run on a later date yields the **same digest**. That single field is the third-party-auditable artifact; no competitor corpus term (`attack graph` / `capability token` / `interactsh` / `OOB` / `dnslog`) appears anywhere (WS-3), so G4 is the open position.
- **I-R3 NO PROOF DOWNGRADE.** `NOT_REPRODUCED` appends to `evidence_paths.replay` and **never** flips `verified` — mirroring the non-destructive re-verify rule documented at `finalize.py:900-913` ("a re-test failing to reproduce … never erases a real, previously-evidenced verification").
- **I-R4 ORDERED CHECKS.** `checks[]` is a stable, named, ordered list so two runs diff line-for-line. `check_id`s are drawn from a fixed registry; an unknown check_id ⇒ the response is rejected, not silently passed.
- **I-R5 ORACLE-DISPOSES.** `verdict` is computed by the same pure verdict functions that ran at discovery (`response_diff`/`DiffVerdict` `exploit_floor.py:1240`, `classify_reflection` `:686`, `_BUCKET_LIST_RX` `floor.py:84`). The replay path adds no new oracle and no new judgement.

**Buyer outcome:** a buyer or third-party auditor hands the platform a `token_id` and gets back a signed, digest-stable, machine-checkable statement — "on 2026-10-01, under the anonymous identity, the recorded control denied access with HTTP 401 while the recorded probe was granted access and echoed a scan-unique marker; verdict REPRODUCED; digest sha256:…" — without running anything themselves and without the platform shipping them a script.

---

## D. DELIVERABLE 3 — Report narrative schema

### D.1 The schema

New module `src/scanner/agent_runtime/chain/narrative_schema.py`. Pure dataclasses + a pure validator. Emitted at finalize into `/work/chain_narratives.json` and into the report dict under the **new** key `chain_narrative`; the existing `chain_narratives` key (`reporting/service.py:402`, built by `_synthesize_chains` `:82-107`) is left untouched.

```yaml
schema_version: "chain.narrative/1"
narrative_id: uuid
scan_id: uuid
root_token_id: uuid
terminal_capability: metadata_access
max_depth: 2
outcome: PROVEN            # PROVEN | PARTIALLY_PROVEN | REFUTED | ALL_INDETERMINATE
validated: true            # false ⇒ renderer MUST NOT show this as a proven chain
violations: []
nodes:
  - hop_index: 0
    capability: internal_http
    state: PROVEN
    finding_id: uuid
    vuln_class: ssrf
    endpoint: "https://app.example/fetch?url="
    severity: high
    proof:
      proof_type: CANARY_ECHO
      strength: machine            # machine | weak | assertion
      evidence_refs: ["tool_outputs/chain_meta_0.log"]
      request_digest: "sha256:…"
      marker_present: true
      control_ref: "tool_outputs/chain_meta_control_0.log"
      verdict: POSITIVE
      replayable: true
    provenance:
      detected_by_tool: "chain:ssrf-metadata"
      verification_method: "chain:imds_iam_role"
      worker_id: null
      tool_invocation_id: uuid
      evidence_object_id: uuid
      minted_at: "2026-10-01T12:00:00Z"
    derived_from: null              # null iff hop_index == 0
    claim:
      subject: "SSRF at /fetch?url="
      assertion: "proved an in-network fetch primitive"
      effect: internal_http
    prose: null                     # RENDERING ONLY — never the source of truth

  - hop_index: 1
    capability: metadata_access
    state: PROVEN
    finding_id: uuid
    vuln_class: cloud_bucket
    endpoint: "https://app.example/fetch?url="
    severity: critical
    proof:
      proof_type: STRUCTURED_MARKER
      strength: weak
      evidence_refs: ["tool_outputs/chain_meta_1.log"]
      request_digest: "sha256:…"
      marker_present: false
      control_ref: "tool_outputs/chain_meta_control_1.log"
      verdict: POSITIVE
      replayable: true
    provenance:
      detected_by_tool: "chain:ssrf-metadata"
      verification_method: "chain:bucket_endpoint_listing"
      worker_id: null
      tool_invocation_id: uuid
      evidence_object_id: uuid
      minted_at: "2026-10-01T12:04:11Z"
    derived_from:
      parent_hop_index: 0
      parent_finding_id: uuid
      parent_proof_type: CANARY_ECHO
      derive_rule: imds_iam_role
      derivation: from_proof_body
    claim:
      subject: "the instance-role path named in hop 0's proof body"
      assertion: "proved a reachable instance-role credential endpoint"
      effect: metadata_access
    prose: null
```

**Machine sentence = `claim`.** The buyer-facing "we found X, which proved Y, which enabled Z" is a **fixed template over `claim`**, not LLM output:

```python
def render_claim(claim: Claim) -> str:
    return f"We found {claim.subject}, which {claim.assertion}, which enabled {claim.effect}."
```

`prose` is an **optional, LLM-authored, never-load-bearing** annotation that is validated against `claim` by `I6_PROSE_DERIVED` and **dropped** on violation rather than rendered.

### D.2 Machine-checkability — the invariants

`validate_narrative(obj) -> list[Violation]`, pure, no I/O. Every rule is checkable from the schema alone plus the two static tables (`capabilities.GRANTS`/`ENABLES`, `proof.LICENSES_HOP`):

| id | rule | why it matters |
|---|---|---|
| `I1_NODE_PROVEN` | every node with `state == PROVEN` has `proof.proof_type ∈ LICENSES_HOP` **and** `len(evidence_refs) ≥ 1` | makes "proven" unfakeable from a row that merely says `verified: true` — the exact failure `_confirm_state` exists to prevent (`ledger/service.py:212-226`) |
| `I2_PARENT_CLOSURE` | every node with `hop_index > 0` has `derived_from.parent_hop_index == hop_index - 1`, and that index exists in the same narrative | no orphan hops; the narrative is a closed path |
| `I3_EFFECT_MONOTONIC` | for all `i > 0`: `nodes[i].capability ∈ ENABLES[nodes[i-1].capability]` ∪ `{nodes[i-1].capability}` | the narrative may not assert an escalation `capabilities.py:77-88` does not license. Replaces the free-text `prerequisite`/`gained` matching with a table check |
| `I4_NO_ASSERTION_CONFIRM` | `proof.proof_type ∈ {ASSERTION_ONLY, NO_PROOF}` ⇒ `state ∈ {INDETERMINATE, SUPPRESSED}` **and** `outcome != PROVEN` | the product thesis: prose/model verdicts are never the confirming thing. Kills defect 8's inversion |
| `I5_VERDICT_AGREEMENT` | `outcome == PROVEN` requires ≥1 node with `proof.verdict == POSITIVE` **and** `proof.replayable == true`; `outcome ∈ {REFUTED, ALL_INDETERMINATE}` when none exists | a chain nobody can re-fire is not "proven end-to-end" |
| `I6_PROSE_DERIVED` | if `prose` present, recompute `render_claim(claim)` and require every one of its tokens to appear in `prose`; else drop `prose` | the LLM cannot add a claim the schema does not contain |
| `I7_ORIGIN_DISCLOSED` | `derived_from.derivation == "static_table"` ⇒ `proof.strength` is displayed as `weak` regardless of `proof_type` | "we guessed the next target" must be visibly distinguishable from "the previous hop told us where to go" — the honesty of the differentiator |
| `I8_NO_REVOKED_PROOF` | `state == REVOKED` ⇒ node is excluded from `outcome` computation and rendered struck-through | honours the A1 downgrade at `finalize.py:176-186` |

**Violation routing:** any violation ⇒ `validated: false`, `outcome` downgraded to the most conservative permitted value, and the narrative is routed to the report's existing "Unconfirmed / needs manual review" bucket — the same destination `_UNCONFIRMED_STATUSES` already uses (`exploit_quality.py:37-38`). A narrative never renders a chain that fails its own validator.

### D.3 Rendering notes

**The inversion.** Today: `finalize.py:357-371` calls `generate_report_narratives` (LLM) and `finalize.py:374` then calls `generate_report`, which picks the prose up out of `finalize_addons.json`. Under the new design the order is:

```
step 6  chain_node/edge build            (existing)
step 6a BUILD chain_narrative            (NEW, deterministic, flag-gated)
step 6b VALIDATE chain_narrative         (NEW, pure; sets validated/outcome)
step 6c generate_report_narratives       (existing; NOW RECEIVES the structured narrative as INPUT
                                          and may emit ONLY `prose` fields)
step 7  generate_report                  (existing; renders `claim` templates + validated `prose`)
```

The LLM moves from *author* to *annotator*. It cannot create a node, change a proof type, flip a verdict, or upgrade an outcome. If it misbehaves, `I6` drops its output and the report is unchanged.

**Render 1 — Chain tab (no LLM).** One row per node: `hop_index`, capability chip, proof-type chip coloured by `strength` (`machine` / `weak` / `assertion`), vuln class, endpoint, `evidence_refs` as links, and `derived_from.derive_rule` rendered as the small grey text *"next target derived from hop N's proof"* (or *"static table"* under `I7`).

**Render 2 — the X/Y/Z line.** Assembled by `render_claim` per node, joined by `→`. Zero LLM.

**Render 3 — numbered versioned artifact list.** `evidence_refs[n]` renders as `{hop_index}.{ext}` — the xBow shape (`3.bash`, `12.python`, `90.python`, per WS-3) with the number supplied by the machine (`hop_index`) and the bytes supplied by the evidence store. The artifact *bytes* are already written by `_write_evidence` (`exploit_floor.py:2352-2361`, `# command:` / `# exit_code:` header); nothing new is generated.

**Render 4 — replay button.** Per node with `proof.replayable == true`, a `POST …/chains/{token_id}/replay` action (§C.3) rendering the `replay_digest` on completion. Under `scanner_retest_enabled`-off + `scanner_chain_replay_v2`-off, the button is not rendered.

**Flag:** `SCANNER_CHAIN_NARRATIVE_V2` (`scanner_chain_narrative_v2`, **default OFF**). Off ⇒ `chain_narrative` key absent from the report dict, no validator run, `chain_narratives` (`reporting/service.py:402`) byte-identical, `finalize.py:357-371` runs in its current position and with its current input.

---

## E. DELIVERABLE 4 — Example hops (capability labels only)

No payloads, no commands, no exploitation procedures. Each hop states: **granting condition · proof type · state transition · oracle (input + verdict)**.

### H1 — `SSRF → INTERNAL_HTTP → METADATA_ACCESS`

| | |
|---|---|
| **Granting** | confirmed `ssrf` finding passing `_read_confirmed`'s gate (`verified ∧ proof_of_concept`, `floor.py:160`); `GRANTS[SSRF] = {INTERNAL_HTTP, METADATA_ACCESS}` (`capabilities.py:39`) |
| **Proof type** | `CANARY_ECHO` (per-scan OOB beacon received — `oob/service.py:490`) **or** `CONTROL_DIFF` (probe vs matched control) |
| **Transition** | `UNMINTED → MINTED → DERIVED → FIRED → PROVEN` |
| **Derivation (the change)** | `derive_rule = "imds_iam_role"`, `origin = "proof_body"`. Hop N's stored proof excerpt names a **specific** role/metadata path; that path becomes the `DerivedTarget.url`. Today the target is `for murl in _METADATA_URLS` (`floor.py:241`) — a frozen 3-tuple, chosen without reading hop N. |
| **Oracle input** | `response_diff(payload_pair, control_pair, marker=<per-scan canary>)` → `DiffVerdict` (`exploit_floor.py:1240`), where `control_pair` is the same request with the injected value replaced by a non-resolving placeholder |
| **Oracle verdict** | `POSITIVE` iff `transport_ok ∧ (marker_reflected ∨ differs)` **and** the body satisfies the role-name shape (`floor.py:66-68`). Otherwise `NEGATIVE` if `transport_ok ∧ ¬marker`, `UNKNOWN` if `¬transport_ok`. |
| **Next capability** | the `metadata_access` token, at `depth+1` |
| **Buyer outcome** | "next target derived from hop 0's proof" instead of a guessed constant; the report can state *where* the probe went and *why that place* |

### H2 — `METADATA_ACCESS → CREDENTIAL → SESSION` (the currently-terminal case)

| | |
|---|---|
| **Granting** | child finding of class `cloud_bucket` or `secrets_exposure`; `ENABLES[METADATA_ACCESS] = {CLOUD_BUCKET, SECRETS_EXPOSURE}` (`capabilities.py:79`); `GRANTS[CLOUD_BUCKET] = {CLOUD_STORAGE, CREDENTIAL}` (`capabilities.py:66`) |
| **Proof type** | `STRUCTURED_MARKER` (the `(AccessKeyId ∧ SecretAccessKey∣Token∣access_token)` lookahead, `floor.py:66-68`) — **weak**, so it licenses a hop **only** under `SCANNER_CHAIN_STRUCTURED_MARKER_PROOF`. Strong alternative: `CANARY_ECHO` when the probe was role-scoped. |
| **Transition** | `PROVEN → (new token, depth+1) MINTED → DERIVED` |
| **Derivation** | `derive_rule = "secret_material_shape"`, `origin = "proof_body"`. Emits an `auth_replay` descriptor carrying a **`secret_material_ref` pointer into the evidence store — never the material inline**. Nothing is parsed out of the secret into the token. |
| **Oracle input** | the **same-identity differential**: `response_diff(under_derived_identity, anonymous_control)` — both sides are the finding's own `affected_endpoint`; the control is the identical request with no credential material |
| **Oracle verdict** | `POSITIVE` iff `transport_ok ∧ (identical ∨ same_body)` **and** `control_status ∈ {401, 403}`. That conjunction is the whole claim: *the derived principal reads a resource the anonymous principal is denied.* `NEGATIVE` if the control also succeeds (no privilege boundary was crossed). |
| **Gate** | `CREDENTIAL ∈ HIGH_IMPACT` (`capabilities.py:96-98`) ⇒ transition T5 fires: a `scan_approvals` row is required before any traffic. Also behind `SCANNER_CHAIN_CRED_REPLAY`. |
| **Today** | `_hop_credential` (`floor.py:385-390`) fires **zero** requests and only reopens classes. All five CREDENTIAL-granting classes (`capabilities.py:49-52,56`) are terminal by construction. |
| **Buyer outcome** | `secrets_exposure → cloud_bucket → cross-principal read` becomes a chain with **closed parent links**, instead of three independent findings that a buyer must join by hand |

### H3 — `FILE_READ → SECRET_DISCOVERY → CREDENTIAL`

| | |
|---|---|
| **Granting** | confirmed `lfi` (`GRANTS[LFI] = {FILE_READ}`, `capabilities.py:46`) or `xxe` (`{FILE_READ, INTERNAL_HTTP}`, `capabilities.py:48`); `ENABLES[FILE_READ] = {SECRETS_EXPOSURE}` (`capabilities.py:86`) |
| **Proof type** | `STRUCTURED_MARKER` (`_SECRET_RX`, `floor.py:97-101`) — weak, flagged; or `CANARY_ECHO` if a planted marker was read back |
| **Transition** | `MINTED → DERIVED → FIRED → PROVEN → (depth+1) MINTED` |
| **Derivation** | `derive_rule = "root_element_routes"`. Hop N's proof body reveals a **root element** — a php open tag, a `<!DOCTYPE …>` signature naming a framework, a `<project …>`/`<settings …>` config root, a shebang interpreter, or a JSON/YAML key block. The candidate config paths are read off *that observed tree*. Today `_hop_file_read` walks the frozen `_SECRET_FILES` 8-tuple (`floor.py:318`) and returns on the **first** `_SECRET_RX` hit (`floor.py:330-339`) — one shot, no control, no derivation. |
| **Oracle input** | **two** captures, which is the part missing today: `pair_A` = derived path through the file-read primitive; `pair_C` = the **same path requested without the primitive** (the control). Then `_SECRET_RX` over `pair_A.body` and the absence check over `pair_C.body`. |
| **Oracle verdict** | `POSITIVE` iff `_SECRET_RX` matches in `pair_A` **and** does not match in `pair_C`. `NEGATIVE` if it matches in both (the file is public, not a disclosure). `UNKNOWN` if either capture failed. |
| **Buyer outcome** | a file-read → secret chain with a *control*, so "the file is just public" is distinguishable from "the primitive disclosed it" — and the report names the file it went after and why |

### H4 — `SESSION → CROSS_PRINCIPAL_READ`

| | |
|---|---|
| **Granting** | confirmed `auth_bypass` (not public-read — `is_public_read_bypass`, `capabilities.py:195-206`), `mass_assignment`, `priv_esc`, `weak_session`, `jwt_flaws`, or `oauth_saml`; each grants `SESSION` (`capabilities.py:53-57,60,65`) |
| **Proof type** | `CONTROL_DIFF` — the three-way differential baseline `_BASELINE_MARKERS` (`exploit_quality.py:60-85`) already demands before an auth-bypass finding may be headline (`exploit_quality.py:207-213`) |
| **Transition** | `MINTED → DERIVED → FIRED → PROVEN` |
| **Derivation** | `derive_rule = "ref_key:id"` (and the other `_REF_KEYS`, `exploit_floor.py:966`). **`_walk_ref` / `_extract_object_ref` (`exploit_floor.py:969-1000`) already implement object-reference extraction from a prior response body and the chain floor does not use them.** The `SESSION` token's proof body yields the concrete object references the session can reach. |
| **Oracle input** | the planted cross-principal pair: an object created under identity **A**, then read as identity **B**; plus an anonymous control read of the same object. Implemented by `_two_request_oracle` (`exploit_floor.py:2525`) / `diff_cross_tenant` (`:1387`). |
| **Oracle verdict** | `POSITIVE` iff B's read echoes **A's planted canary verbatim** (`marker_reflected`) **and** the anonymous control is denied (`401/403`) **and** `transport_ok`. This is the `CROSS_PRINCIPAL_DIFF` proof type — a control under a *different principal*, distinct from `CONTROL_DIFF`'s control-under-a-different-payload. |
| **Why this is the WS-3 gap** | `capabilities.py` grants `CROSS_PRINCIPAL_READ` (`capabilities.py:58`) but its only *testing* primitives are IDOR/BFLA; there is no cross-principal primitive for the `SESSION`-granting classes beyond those two. |
| **Buyer outcome** | the report stops asserting the free-text sentence "session enables IDOR" (`EDGE_RATIONALE`, `capabilities.py:132-134`) and starts asserting: *session enabled a read of object X belonging to another principal, proven by A's planted canary in B's response.* |

### H5 — `RCE → SECRET_DISCOVERY` (unreachable today)

| | |
|---|---|
| **Granting** | confirmed `cmdi` / `ssti` / `deserialization` / `file_upload` / `rfi`, each granting `RCE` (`capabilities.py:42-45,47`) |
| **Proof type** | `CANARY_ECHO` — an RCE proof is by construction an OOB-beacon proof (`build_cmdi_oob_cmd` `exploit_floor.py:396`, `build_deser_oob_cmd` `:498`) |
| **Today** | `_HOPS` (`floor.py:397-404`) has **no entry for `RCE`**. `ENABLES[RCE] = {SECRETS_EXPOSURE}` (`capabilities.py:82`) is a graph edge that the executor cannot spend. 16 RCE-granting nodes in the live histogram, zero hops. |
| **Derivation** | `derive_rule = "invocation_output"`, `origin = "invocation_output"`. The RCE proof's own `tool_invocations.summary` (`exploit_floor.py:2513-2515`) records the command that ran and where — the process identity, the working directory, the configuration directory. The next hop's target is the config directory **the command actually ran in**, not a guessed path. |
| **Transition** | `PROVEN → (new token, depth+1) MINTED(FILE_READ) → DERIVED → FIRED` |
| **Oracle input** | `response_diff` over the derived config path, plus the anonymous control for the same path |
| **Oracle verdict** | `POSITIVE` iff the secret shape matches in the probe body **and** not in the control body |
| **Buyer outcome** | the first RCE-rooted chain the platform can record at all: code execution → configuration reached → credential material disclosed, each hop with its own closed parent link |

### Coverage gap this closes

`_HOPS` (`floor.py:397-404`) covers 6 of 12 `Capability` values (`capabilities.py:22-33`). Uncovered: `RCE`, `SESSION`, `DB_READ`, `PII_READ`, `CROSS_PRINCIPAL_READ` — together the holders of 32 + 16 + 56 + 25 + 23 of the live capability histogram. H4 and H5 are the first two proposals to close it; H2/H3 close the derivation half for two already-mapped capabilities.

---

## F. FLIP TABLE

| # | flag (settings attr) | default | byte-identical-when-off behaviour | blast radius if wrong |
|---|---|---|---|---|
| 1 | `SCANNER_CHAIN_TOKEN_PERSIST` (`scanner_chain_token_persist`) | **OFF** | `run_chain_floor` unchanged; no `/work/chain_tokens.jsonl` written or read; no `chain_token` rows; report unchanged | **Low.** Adds a file append + a table INSERT inside an already-`contextlib.suppress`ed finalize block. Worst case: tokens persisted but no hops fire — pure dead data. Cannot touch production traffic. |
| 2 | `SCANNER_CHAIN_DERIVED_TARGETS` (`scanner_chain_derived_targets`) | **OFF** | The existing `for f in _read_confirmed(...)` loop at `floor.py:426-452` is entered unchanged; the six `_hop_*` signatures are untouched; the static 3+3+8 tables are the only targets | **HIGH.** This is the only flag that adds network traffic from derived targets. Wrong derivation ⇒ requests against unintended hosts — mitigated by the existing `_scope_ok` gate (`floor.py:434`) and `_fireable` (`floor.py:243,291,320`), and bounded by `_MAX_HOPS = 40` (`floor.py:102`). Ship last, behind a per-scan budget cap and the `HIGH_IMPACT` approval gate. |
| 3 | `SCANNER_CHAIN_CRED_REPLAY` (`scanner_chain_credential_replay`) | **OFF** *(+ `scan_approvals` row required)* | `_hop_credential` keeps its no-op body (`floor.py:385-390`); `res.unlocked` set exactly as today | **HIGH.** `CREDENTIAL ∈ HIGH_IMPACT` (`capabilities.py:96-98`) — the highest-blast-radius transition in the design. Double-gated: flag **and** explicit per-scan approval. Never infer material into the token (pointer only). |
| 4 | `SCANNER_CHAIN_STRUCTURED_MARKER_PROOF` (`scanner_chain_structured_marker_proof`) | **OFF** | `STRUCTURED_MARKER` stays out of `LICENSES_HOP`; those tokens terminate at `SUPPRESSED` | **Medium.** Lifts a no-canary, parser-recognised body shape into hop-licensing proof. False positives here are FP chains in the buyer narrative. Default-OFF is correct. |
| 5 | `SCANNER_CHAIN_PARENT_LINK` (`scanner_chain_parent_link`) | **OFF** | `evidence_paths["chain"]` gets no new keys; `chain_node.attrs` byte-identical; `chain_hop` not written | **Low–Medium.** Additive JSONB keys only. Risk is key collision with a future consumer — mitigated by namespacing under the existing `chain` object rather than adding top-level `evidence_paths` keys. |
| 6 | `SCANNER_CHAIN_NARRATIVE_V2` (`scanner_chain_narrative_v2`) | **OFF** | No `chain_narrative` key in the report dict; `chain_narratives` (`reporting/service.py:402`) untouched; validator not run; `finalize.py:357-371` keeps its current position and input | **Low.** Pure read + a new dict key. The validator only ever *downgrades* an outcome, never upgrades — a false positive makes a chain render as "unconfirmed", which is the safe direction. |
| 7 | `SCANNER_CHAIN_REPLAY_V2` (`scanner_chain_replay_v2`) | **OFF** | Route does not exist; `POST /findings/{id}/retest` (`retest.py:105-151`) is byte-identical | **Medium.** The only flag whose product surface is *outbound network*. Guarded by `R1_OUT_OF_SCOPE` on every hop, `R2`–`R5` pre-flight rejections with zero traffic, and the read-only `I-R1` invariant (no finding/ledger mutation). Risk concentrates in the scope re-check — `retest.py:131-137` is the reference implementation to copy verbatim. |

**Cross-flag rule (D4).** Flags 2 and 3 must additionally require flag 1 (`scanner_chain_token_persist`) — a hop cannot be dispatched without a persisted token to record it against. Any flag read is fail-closed (`try/except → False`, the pattern at `floor.py:105-112`), so a config error disables rather than enables.

---

## G. EVIDENCE LEDGER

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| Hop targets come from 3 static tables, never from hop N | [CODE] `chain/floor.py:59-63` (`_METADATA_URLS`, 3), `:79-83` (`_BUCKET_URLS`, 3), `:87-96` (`_SECRET_FILES`, 8); loops at `:241`, `:289`, `:318` | HIGH | Read in full |
| `_Ctx` carries zero per-finding data | [CODE] `chain/floor.py:134-143` | HIGH | 7 fields, all per-invocation |
| All six hops take `(ctx, url, param, res)` | [CODE] `chain/floor.py:393` (`_HopFn`), signatures `:232`, `:283`, `:313`, `:344`, `:365`, `:385` | HIGH | Read in full |
| Only `(url, param)` crosses the finding boundary | [CODE] `chain/floor.py:190-201` (`_finding_target`), consumed `:432` | HIGH | Reads `affected_endpoint`/`endpoint`/`param`/`parameter` only |
| The evidence path is available at hop time and discarded | [CODE] `exploit_floor.py:2505-2522` (`_fire` → `(stdout, exit_code, evidence_path)`); bound to `_path` at `chain/floor.py:245`, `:293`, `:322` | HIGH | `_path` is never read |
| Evidence is written to disk with command + exit code | [CODE] `exploit_floor.py:2352-2361` (`_write_evidence`) | HIGH | Header `# command:` / `# exit_code:` |
| `_hop_credential` is a deliberate no-op | [CODE] `chain/floor.py:385-390` | HIGH | Ponytail comment quotes "DON'T build a credential-stuffer"; upgrade path "parse creds → auto-login" |
| All five CREDENTIAL-granting classes are therefore terminal | [CODE] `capabilities.py:49,50,51,52,56` | HIGH | `GRANTS` map |
| `RCE` grants `SECRETS_EXPOSURE` but has no hop | [CODE] `capabilities.py:42-45` (GRANTS), `:82` (`ENABLES[RCE]`), `floor.py:397-404` (`_HOPS` — no `RCE` key) | HIGH | Also absent: `SESSION`, `DB_READ`, `PII_READ`, `CROSS_PRINCIPAL_READ` |
| Capability tokens ARE carried and dispatched | [CODE] `chain/floor.py:426` (`_read_confirmed`), `:436` (`capabilities_for`), `:397-404` (`_HOPS`), `:441-450` | HIGH | Read in full |
| Node anchoring gate = `verified ∧ proof_of_concept` | [CODE] `chain/floor.py:160`; `chain/service.py:142` | HIGH | Same predicate both places |
| PoC is bound to persisted nodes; `evidence_path` is not | [CODE] `chain/service.py:167-179` (`attrs` gets `proof_of_concept`, `evidence_path`, `reasoning`) | HIGH | Live 195/195 vs 0/195 is H3's query, not re-run here |
| `_write_executed_chain` writes `verification_method="executed_chain"` | [CODE] `chain/floor.py:204-228`, esp. `:225` | HIGH | Report bucket reader: `reporting/service.py:67-79` |
| `_write_executed_chain` snapshots only when the writer flag is on | [CODE] `chain/floor.py:445-450` | HIGH | `snapshot = _read_confirmed(work_dir) if _executed_chain_enabled() else None` |
| 0 `executed_chain` findings in 43 scans; 195 nodes / 464 edges | H3 verification (established finding, brief) | HIGH (as given) | Not re-derived: `docker` daemon unavailable this session (`docker ps` → npipe connect failure). No new query attempted. |
| `chain_node`/`chain_edge` are `scan_id`-scoped | [CODE] `finalize.py:65-66` (counts `WHERE scan_id=:s`), `db/models/tenant.py:305`, `:330` (FK `scans.scan_id`) | HIGH | |
| `ChainEdge` cannot hold an executed hop | [CODE] `tenant.py:322-333` — columns `(edge_id, scan_id, from_node, to_node, rationale)`; `:326` `UniqueConstraint("from_node","to_node")` | HIGH | No provenance/proof column exists |
| `ChainNode` cannot hold per-target multiplicity | [CODE] `tenant.py:299` `UniqueConstraint("scan_id","finding_id","capability")` | HIGH | |
| `chain_node` idempotency is DELETE-then-INSERT per scan | [CODE] `finalize.py:340-341` | HIGH | New tables must mirror this |
| Alembic head is `0019` | [CODE] `alembic/versions/0019_add_scan_engine_models.py:7-8` (`revision = "0019"`, `down_revision = "0018"`) | HIGH | Next revision id is `0020` |
| No finding-lineage / hop / proof-type concept exists anywhere in `src/` | [QUERY] `Grep` over `src/**/*.py` for `parent_finding\|parent_node\|chain_hop\|proof_type\|hop_index\|capability_token` → **0 occurrences** for all six terms | HIGH | `parent_id` does exist, but only as an **inventory tree** edge on `InventoryElement` (`tenant.py:214`) and its API mirror (`api/schemas.py:620`) — never a finding-to-finding lineage. `ChainNode`/`ChainEdge` carry no parent column. |
| The machine "confirmation" gate already exists and is strict | [CODE] `ledger/service.py:205-226` (`_confirm_state`), `:136-156` (`_oracle_fired`), `:175-187` (`_EVIDENCE_FIELDS`, `_finding_has_evidence`), `:876-925` (resolve path) | HIGH | Returns `confirmed` / `pending_oracle` / `pending_human` |
| Oracle-first confirm is default-OFF | [CODE] `config.py:218` (`scanner_oracle_first: bool = False`) | HIGH | |
| Class→oracle map exists | [CODE] `agent_runtime/oracle_map.py:13-19`, `:47-52` | HIGH | `logic` group maps to `curl` = "no dedicated weapon" |
| `DiffVerdict` is an existing pure, typed, machine-checkable verdict | [CODE] `exploit_floor.py:1224-1238` (dataclass, 7 typed axes), `:1240-1265` (`response_diff`) | HIGH | The single audited primitive; the replay contract reuses it |
| `_two_request_oracle`, `diff_cross_tenant`, `diff_access` implement the cross-principal primitive | [CODE] `exploit_floor.py:2525`, `:1387`, `:1297`, `:1424` | HIGH | Function names + signatures read via grep of `^def `/`^async def ` |
| Object-reference extraction from a prior response already exists, unused by the chain floor | [CODE] `exploit_floor.py:966` (`_REF_KEYS`), `:969` (`_walk_ref`), `:982` (`_extract_object_ref`) | HIGH | [QUERY] `Select-String chain/floor.py -Pattern "_walk_ref\|_extract_object_ref\|_REF_KEYS"` → 0 matches. Neither is in `chain/floor.py`'s import block (`:35-53`). |
| `tool_invocations` summary is persisted per fired command | [CODE] `exploit_floor.py:2513-2515` (`surface.persist_invocation(tool=, command=, exit_code=, output_path=, summary=out[:4000])`) | HIGH | |
| `executed_chain` and `oob_callback` and `deferred_canary` and `deterministic` are the existing `verification_method` labels | [CODE] `chain/floor.py:225`, `oob/service.py:490,510`, `oob/service.py:356,371`, `inventory_ingest.py:919`, `exploit_floor.py:2405` (`f"exploit_floor:{tool}"`), `finalize_enrich.py:73` | HIGH | |
| `is_deterministic_oracle` is the existing single trust source and is prefix-based | [CODE] `reporting/exploit_quality.py:118-130` | HIGH | `vm == "oob_callback"` or `vm.startswith("exploit_floor:") and "time" not in vm`. A `chain:` prefix must be added explicitly or chain findings lose trust. |
| Timing-only floor labels are already demoted | [CODE] `ingest_findings.py:79-89` (`_is_weak_timing_confirmation`), applied `:458-460` | HIGH | Basis for `TIME_BLIND ∉ LICENSES_HOP` |
| `evidence_paths` is the repo's established "no dedicated column" store | [CODE] `ingest_findings.py:426-438`, `finalize.py:886-894` (`_stamp_status`), `:697-700` (reassign-not-mutate), `:737-748` | HIGH | The pattern `evidence_paths["chain"]` reuses is at `:436-438` |
| `evidence_paths["chain"]` currently carries LLM free-text `prerequisite`/`gained` | [CODE] `ingest_findings.py:436-438`, rendered into `attacker_narrative` by `_derive_attacker_narrative` `:116-121` | HIGH | Two sources of truth vs `capabilities.capabilities_for` `:170-178` |
| The free-text chain linker is dead code | [QUERY] `Select-String chain/service.py -Pattern "_link_match\|_link_tokens\|_LINK_STOP"` → 6 hits, all at `:103,106,107,110,118,120`; **zero call sites** outside the definitions | HIGH | `:120` is `_link_tokens` called from `_link_match` |
| A per-finding retest/replay already exists and is gated default-OFF | [CODE] `api/retest.py:1-151` (151 lines), `config.py:508` (`scanner_retest_enabled: bool = False`) | HIGH | GET-only (`retest.py:32`, `:80-81`), 3-value state (`:12`), scope re-check (`:131-137`) |
| The retest verifier is a bare substring match | [CODE] `retest.py:95-96` (`_verdict`) | HIGH | Reason the replay contract needs proof types + ordered checks |
| The narrative layer is 5,965 bytes of LLM prose merger | [CODE] `reporting/narrative.py` file size = 5,965 bytes; `build_narrative_prompt` `:45-65`; `merge_report_addons` `:68-91` | HIGH | File size measured directly |
| Narrative generation runs **before** report generation | [CODE] `finalize.py:357-371` (`generate_report_narratives`) then `finalize.py:374-378` (`generate_report`) | HIGH | The inversion this design reverses |
| `scanner_report_v2` is default **ON** | [CODE] `config.py:459` | HIGH | Relevant: prose already runs in production; only `prose` fields move |
| `ChainNode.init` event already surfaces `node_id` before flush | [CODE] `tenant.py:314-318` | HIGH | Precedent for the `chain_token` model to do the same |
| `chain_narratives` already lands in the report dict | [CODE] `reporting/service.py:297` (built), `:402` (key), `:82-107` (`_synthesize_chains`) | HIGH | New key must be additive |
| Existing executed-chain flags are default-OFF and fail-closed | [CODE] `config.py:254` (`scanner_executed_chain_findings: bool = False`), `floor.py:105-112` (`try/except → False`) | HIGH | The template every new flag follows |
| Docker daemon unavailable; no live query attempted | [QUERY] `docker ps --format "{{.Names}}\t{{.Image}}\t{{.Status}}"` → `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | HIGH | R4 respected: no write, no scan, no target request |

### Confidence caveats

- Rows sourced from H3 verification (live counts of 195/195, 0/195, 43 scans, 0 executed_chain) are carried at the confidence given in the brief. They were **not** re-derived here because the Docker daemon is down. Every *design* consequence drawn from them (rationale items 1–5, H5's "16 RCE nodes, zero hops") is independently derivable from the code citations beside it.
- `exploit_floor.py` was **not** read whole (264KB). Only its `^def `/`^async def `/`^_[A-Z_] = `/`^class ` structure was enumerated, plus targeted reads of `_fire` (`:2498-2522`), `_write_finding` (`:2382-2412`), `_write_evidence` (`:2352-2361`), `_signal` (`:2413-2419`), `_REF_KEYS`/`_walk_ref`/`_extract_object_ref` (`:966-1000`), `_sibling_routes` (`:2559-2580`), `DiffVerdict`/`response_diff` (`:1224-1265`). Line numbers for the remaining named verdict functions come from that enumeration, not from reading their bodies — flagged MEDIUM where a design decision depends on their exact internals.
- No claim in this document depends on an unverified citation. Where a mechanism's internals were not read, the design depends only on its **name and signature**, which were enumerated.
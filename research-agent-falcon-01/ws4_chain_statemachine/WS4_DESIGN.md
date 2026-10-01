# WS-4 · Chaining State Machine Architecture Design

## Executive Summary & Design Constraints
* **Constraint Compliance (R1):** Design only. Offensive capabilities are described exclusively as **CAPABILITY MODELS**: state machines, proof-type enums, worker contracts, report schemas, and capability labels (e.g. `FILE_READ -> SECRET_DISCOVERY -> DATA_ACCESS`). Strictly zero executable payloads, shell commands, or attack runbooks.
* **Core Problem Identified (H3 Confirmed):** Currently, `src/scanner/agent_runtime/chain/service.py` builds `ChainNode` and `ChainEdge` **post-hoc at finalize** from a static `ENABLES` lookup table. During scan execution, `father.py:1533` merely injects high-level prose (`You now HAVE credential`) without passing machine-structured tokens, headers, cookies, or extracted artifacts. Hop N+1 has to re-derive or guess what Hop N proved.

---

## 1. Capability-Token State Machine

```
+-----------------------------------------------------------------------------------+
|                                  HOP N WORKER                                     |
|  1. Executes offensive probe against Target Endpoint                             |
|  2. Fires Deterministic Oracle (HTTP response / OOB interaction / Browser DOM)    |
|  3. Validates Proof Criteria -> Emits Finding                                     |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           CAPABILITY EXTRACTOR ENGINE                             |
|  Module: scanner.agent_runtime.chain.tokens                                       |
|  Input: Confirmed Finding + Evidenced Proof Artifact                              |
|  Logic: Deterministic regex/JSON extractor extracts structured token             |
|  Output: CapabilityToken Capsule                                                 |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        CAPABILITY TOKEN LEDGER STORE                              |
|  Persisted in: /work/capability_tokens.jsonl & PostgreSQL tenant.capability_token |
|  Schema: token_id, scan_id, source_finding_id, capability_type, secret_handle,    |
|          scope_binding, valid_until, replay_contract                              |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           HOP N+1 DISPATCH INJECTOR                               |
|  Module: scanner.agent_runtime.engine.father                                      |
|  Action:                                                                          |
|  1. Re-opens unlocked ledger cells for child vuln_classes                         |
|  2. Mounts /work/tokens/<token_id>.json directly into Hop N+1 worker environment   |
|  3. Injects structured `parent_finding_id` and token reference into worker spec    |
+-----------------------------------------------------------------------------------+
```

### Capability Token Specification Contract
```python
from dataclasses import dataclass
from enum import StrEnum
import uuid

class CapabilityType(StrEnum):
    INTERNAL_NETWORK_ACCESS = "internal_network_access"
    AUTHENTICATED_SESSION = "authenticated_session"
    DATABASE_QUERY_ACCESS = "database_query_access"
    FILE_SYSTEM_READ = "file_system_read"
    CLOUD_CREDENTIAL_ACCESS = "cloud_credential_access"
    ADMIN_PRIVILEGE_TOKEN = "admin_privilege_token"

@dataclass(frozen=True)
class CapabilityToken:
    token_id: uuid.UUID
    scan_id: uuid.UUID
    source_finding_id: uuid.UUID
    capability_type: CapabilityType
    scope_domain: str
    token_data: dict[str, str]  # Structured headers, cookies, or session variables
    proof_type: str             # Ref to ProofType enum
    created_at: str
    reproduce_contract: dict[str, str]
```

---

## 2. Parent-Finding Linkage, Proof-Type Enum & Replay Contract

### Schema Modifications: `tenant.findings`
To convert chain synthesis from post-hoc guessing to structural reality, `tenant.findings` and `findings.jsonl` are extended with explicit relational pointers:
* `parent_finding_id`: `UUID | None` — Foreign key linking directly to the prerequisite finding in the chain.
* `chain_depth`: `Integer` (Default 0 for root findings, N+1 for chained findings).
* `proof_type`: `Text` (Constrained to the `ProofType` enum).
* `capability_token_id`: `UUID | None` — Foreign key to the exact token consumed to prove this hop.

### Proof-Type Enum Model
```python
class ProofType(StrEnum):
    OOB_DNS_INTERACTION = "oob_dns_interaction"
    OOB_HTTP_CALLBACK = "oob_http_callback"
    DOM_EXECUTION_CONFIRMED = "dom_execution_confirmed"
    STATUS_CODE_DIFFERENTIAL = "status_code_differential"
    BODY_EXTRACT_MATCH = "body_extract_match"
    TIMING_ATTACK_DISCRIMINANT = "timing_attack_discriminant"
    STATE_CHANGE_OBSERVED = "state_change_observed"
```

### Deterministic Replay Contract
Each finding in a chain must satisfy a strict **Deterministic Replay Contract**:
1. **Purity:** Replaying Hop N+1 must not depend on human intervention or unpredictable nonces.
2. **Prerequisite Resolution:** Before replaying Hop N+1, the verification engine checks whether Hop N is valid. If Hop N’s capability token is expired, the replay engine executes Hop N first, extracts a fresh token, and pipes it into Hop N+1.
3. **Execution Sandbox:** Replay runs in an isolated container without network egress outside the authorized scan scope.

---

## 3. Buyer-Facing Report Narrative Schema
Enterprise buyers and CISOs reject isolated lists of theoretical bugs. They require a cohesive, evidence-backed attack narrative: *"We found X, which proved Y, which enabled Z."*

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ChainedAttackStory",
  "type": "object",
  "required": ["chain_id", "headline", "cumulative_severity", "hops", "remediation_summary"],
  "properties": {
    "chain_id": { "type": "string", "format": "uuid" },
    "headline": { "type": "string" },
    "cumulative_severity": { "type": "string", "enum": ["CRITICAL", "HIGH"] },
    "hops": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["hop_index", "finding_id", "vulnerability_discovered", "capability_proven", "impact_enabled"],
        "properties": {
          "hop_index": { "type": "integer" },
          "finding_id": { "type": "string", "format": "uuid" },
          "vulnerability_discovered": { "type": "string" },
          "capability_proven": { "type": "string" },
          "impact_enabled": { "type": "string" },
          "proof_summary": { "type": "string" }
        }
      }
    },
    "remediation_summary": { "type": "string" }
  }
}
```

### Buyer-Facing Attack Narrative Example (Abstract Capability Labels Only)
* **Headline:** Multi-Stage Escalation: External Interface Misconfiguration to Cross-Tenant Data Access.
* **Hop 1:**
  - *Discovered:* Server-Side Interface Redirection.
  - *Proved:* Out-of-band loopback interaction via private network bridge (`INTERNAL_NETWORK_ACCESS`).
  - *Enabled:* Internal metadata service endpoint reachability.
* **Hop 2:**
  - *Discovered:* Internal Configuration & Credential Exposure.
  - *Proved:* Cloud identity credential extraction (`CLOUD_CREDENTIAL_ACCESS`).
  - *Enabled:* Access to internal cloud storage repositories.
* **Hop 3:**
  - *Discovered:* Broken Object-Level Authorization (BOLA).
  - *Proved:* Reading cross-principal tenant objects using extracted token (`AUTHENTICATED_SESSION` -> `CROSS_PRINCIPAL_READ`).
  - *Enabled:* Full organizational boundary breach.

---

## 4. Example Chaining Hops (Capability Labels Only)

```
[CHAIN PATTERN A: Client Configuration to Internal Data Access]
OPEN_REDIRECT -> SSRF_PRIMITIVE -> INTERNAL_METADATA_READ -> CLOUD_STORAGE_ACCESS

[CHAIN PATTERN B: File System to Remote Execution]
PATH_TRAVERSAL -> CONFIG_READ -> HARDCODED_SECRET_DISCOVERY -> PRIVILEGED_SESSION -> CODE_EXECUTION

[CHAIN PATTERN C: Multi-Tenant Business Logic Escalation]
MASS_ASSIGNMENT -> ROLE_ELEVATION -> AUTHENTICATED_SESSION -> BOLA_ACCESS -> PII_EXTRACTION
```

---

## WS-4 Evidence Ledger

| Claim | Source (type + location) | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| Current chain synthesis is graph-only and runs post-hoc at finalize | [CODE] `src/scanner/agent_runtime/chain/service.py:123-175`, `finalize.py:348` | HIGH | Graph built after run from `findings.jsonl`; no live token piping. |
| Escalation wave only receives prose capability names without tokens | [CODE] `src/scanner/agent_runtime/engine/father.py:1520-1545` | HIGH | Prompt says "You now HAVE <cap>"; no artifact or credential is passed. |
| `tenant.findings` lacks parent finding and token linkage columns | [QUERY] `\d tenant_xbow.findings` on `scanner-postgres` | HIGH | Confirmed schema: no `parent_finding_id` or `token_id` column exists. |
| Competitors use multi-stage capability state stores to drive lateral pivots | [COMPETITOR] `competitor-research/firecompass/dossier.md:91`, `escape/dossier.md:96` | HIGH | FireCompass state store and Escape pub/sub bus enable cross-stage context. |

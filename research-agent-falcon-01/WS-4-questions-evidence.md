# WS-4 · Chaining state-machine design (no payloads; capability labels only)

H3 verdict: PARTIAL — carry exists (write-time gained/prereq, methodology.py:180-189; escalation
capability_ctx with granting title/endpoint, father.py:1520-1548; graph nodes with poc+evidence,
chain/service.py:165-173; proof_capsule + re-fire, finalize.py:737-748 + api/retest.py). Missing: typed
CONSUMABLE token. Note: executed-chain report bucket exists but default-OFF (config.py:249-254);
two-identity authz oracle exists but OFF (config.py:245-247); brief already carries scan-level auth snippet
(scan_brief.py:71-74) — hop-level token is the gap, not session carriage.

## State machine
PROPOSED (gained+prerequisite declared) → ORACLE-FIRED (floor/verifier/OOB/browser; proof_capsule minted) →
TOKENIZED (chain_node.attrs.token = {cap, finding_id, evidence_refs, capsule_ref, auth_ref}) → ESCROWED
(detect_escalations HIGH-cap filter; seen_caps dedups) → CONSUMED (hop-N+1 task embeds MACHINE block +
reopened classes claimed via claim_family_cells) → EXECUTED-CHAIN (ONE finding, per-hop evidence,
verification_method=executed_chain; ChainEdge.rationale recorded).

## Contracts
- Token persistence: chain_node.attrs JSONB (survives --rm) + mirror findings.evidence_paths.chain.
- Hop handoff: extend _capability_context — keep prose line, append IDs+refs (values via auth.json pointer
+ capsule re-fire, never inline secrets).
- Proof-type enum: promote evidence_object.method (oob|differential|paired_control|reflection|manual|tool,
tenant.py:230) × source (oracle-fired|oob-callback|browser-executed|independent-reverify).
- Replay: proof_capsule + evidence rows via api/retest.py path. Parent linkage: chain_node.finding_id +
evidence_paths.chain (no schema change; findings has no parent col by design).
- Report schema: story{anchor, hops[{finding_id, cap_granted, proof_type, evidence}], terminal_impact}
rendered from chain_edge.rationale + attacker_narrative.
- Gate: SCANNER_CHAIN_TOKENS default OFF; off = today's prose ctx byte-identical. Example hops as labels
only: SESSION → CROSS_PRINCIPAL_READ → PII_READ; REDIRECT → SSRF → METADATA_ACCESS.

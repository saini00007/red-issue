# POLICY — human-authored, non-overridable (prompt mirror; CODE is the real enforcement)

**Scope (IN-SCOPE ONLY):** https://www.infinitycapital.bh/
-> enforced: ScopeConfig, fail-closed on EVERY tool call (guardrails.in_scope; a prompt cannot widen it)
**Blocklist:** *.gov, *.gov.in, *.gov.uk, *.mil, *.edu, *.edu.au, *.ac.uk, *.nhs.uk, *.healthcare.gov, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16, *.bank, *.hospital, google.com, facebook.com, microsoft.com, amazon.com, apple.com -> enforced: _is_platform_blocked + TENANT_BLOCKLIST
**RoE:** proof-not-damage; FORBIDDEN: reverse shells, persistence, data exfiltration, destructive ops (DROP / rm -rf / DoS), out-of-scope pivot
-> enforced: safety.py crime-line (FORBIDDEN/GATED) + methodology RoE — never a prompt toggle

**Credentials supplied:** no — black-box; auth phases logged blocked, never silently skipped (secret values are NEVER written to this file)

**Playbook:** full_coverage_vapt
**Aggression ceiling (ADVISORY — hard limits stay code):** rate <= 50 rps; back off 600ms on WAF
**Phases (methodology directive; coverage stays LEDGER-driven + evidence-only):**
- A0_subdomain_discovery
- A1_fingerprinting_recon
- A1_5_osint
- A9_ssl_tls
- A2_content_discovery
- A4_5_url_corpus
- A4_6_js_mining
- A4_7_param_discovery
- A3_vulnerability_scanning
- A4_authentication_testing
- A5_xss_testing
- A6_configuration_headers
- A7_injection_advanced
- A8_access_control_idor
- A_HTTP_layer
- A_oauth_saml_sso
- A_client_side
- A10_infrastructure
- A_checkpoint_state
- A_gap_closure
- A11_dedup_enrichment
- A12_fp_verification_report
**Restrictions:** no_destructive_ops, no_data_exfiltration, no_dos, stay_in_scope -> enforced: crime-line + scope fail-closed

**Operator context (ground-truth FACTS about the target — NOT permission to skip tests or hide findings):**
SCOPE (STRICT): test ONLY the host www.infinitycapital.bh. Do NOT test, crawl, brute, or pivot to any other subdomain of infinitycapital.bh (no blog., no mail., no api. unless the rule below applies). You MAY follow a different host ONLY if this same web app directly serves/loads from it (e.g. an API or static-asset host the app itself calls in-page) and only to the extent needed to test that app's use of it. OBJECTIVE: find ALL vulnerabilities, prioritizing those that lead to SENSITIVE DATA EXPOSURE or INTERNAL / BACKEND ACCESS: authentication/authorization bypass, IDOR/BOLA, injection (SQLi/NoSQL/command/template), SSRF reaching internal services or cloud metadata, exposed admin/debug/config/backup endpoints, directory listing, leaked secrets/keys/credentials, insecure direct object references, and server/framework misconfigurations. Be thorough and evidence-driven; do not perform destructive actions (no data deletion, no DoS).

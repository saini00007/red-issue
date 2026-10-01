# WS-2 — Telemetry Forensics (research-agent-viper-01)

Sources: C (server JSONL files + DB). Read-only. Aggregates only; no prompts/secrets.

## Observed-failure catalog (aggregate counts)

| Failure mode | Evidence | Scale observed |
|---|---|---|
| Provider 502 "ChatCompletion response has no choices" killing workers | q06: 282/321 worker_runs status=error, identical error string, avg 2.9 min | dominates long scan |
| max_turns_exceeded at LOW recorded turn counts (turn1-7) while default MAX_TURNS=40 | decisions.log tail, 1f5fe7c8 workdir | waves 10 & 14, many workers; implies per-reprompt budgets or replay bloat |
| Guardrail honesty on drain: worker stops rather than fabricate (verbatim decision entry) | decisions.log tail: "The wrap-up guardrail has stopped me ... I am not going to fabricate sqlmap output" | ≥1 explicit, 84aea81a+1f5fe7c8 show close.json/finalizing.json markers |
| Ledger-update thrash: state stream dominated by 'testing' self-records | probe2: running scan ledger_updates.jsonl = 1818 testing vs 216 tested_clean vs 11 blocked vs 2 confirmed (2,047 total) | ~89% of updates non-terminal |
| Category-spelling fragmentation feeding resolve `unmatched` | probe3: findings.jsonl categories on running scan include sqli/sql_injection/'SQL Injection' (3 spellings), 'Reflected Cross-Site Scripting (CWE-79)', 'Unauthenticated open email relay / spam relay (CWE-284, CWE-20)' | 91 findings, 15+ distinct spellings on one scan |
| OOB: 379 raw callbacks on running scan (219 DNS / 160 HTTP), 1,089 on long scan | probe2 histograms; oob_interactions.jsonl has NO classification field (raw interactsh mirror) | correlation happens in oob/service.sync_oob (classify_oob, service.py:77-97) — honest class derived from protocol |
| agent.log NOT persisted in scan workdir (logs/ empty/absent) | probe3: `find logs/ -type f` → nothing on running scan | post-mortem observability gap vs directive C1 assumption; [CODE] contradiction — worker.py:555-556 docstring says poller writes agent.log to the volume; not landing |
| Usage telemetry gaps: long scan agent_messages mostly tokens_in=0/tokens_out=0 (bunny provider returns no usage) | q08 SQL | cost/token accounting unreliable on OpenRouter-ish models |
| tool.started/tool.done pairing exact (4327/4326 running scan; 7101/7101 long scan) — one orphan started | q08 | good signal integrity for tool events |
| worker_runs.findings_count inflated by errored workers (5088 findings on 282 errored runs — flushed-but-errored) vs DB findings=25 post-dedup | q06 vs q07 | DB-side dedup works; disk-side inflates |

## Questioned-but-resolved internals
- oob honest classification IS implemented: protocol-derived class (ldap/rmi→jndi; http/dns/smtp→ssrf unless label maps cleanly), qualifier-stripping, sink-cluster dedup (oob/service.py:59-97, 130-135), cap 12/scan (service.py:100-106), stale-callback gate via oob_health registration floor (151-166).
- Wave cadence corroborated: method_switch events every ~5s in poller log (probe4) = reconcile/cadence telemetry live.
- Provider instability independently corroborated at the proxy layer (which covers ONLY nvidia-routed calls): 24,630 calls over 2 days, 2,865 5xx + 3,578 429 responses; avg latency 9.6s on nemotron-ultra [QUERY probe8/9]. This is consistent with the 87.9% worker-502 mortality seen in worker_runs [QUERY q06].
- C4 blind spot CONFIRMED with numbers: proxy_log.db contains exactly 2 models, both nvidia/*; zero OpenRouter/bunny rows — those scans leave no prompt-level forensic trail [QUERY probe9].
- Executed-chain evidence: chain_node/chain_edge build fine (46 nodes / 77 edges on the running scan, 118 edges max), but `verification_method='executed_chain'` = 0 on ALL 8 recent scans — the deterministic chain floor is ON live (CHAIN_FLOOR=1) yet has never landed a composed executed-chain finding [QUERY probe6/7].
- OOB minting is prolific (790 registry tokens minted on the running scan) but DB-persisted deduped tokens are far fewer (59 rows in oob_token) — registry→sync persistence has heavy dedup/gating between mint and evidence [QUERY probe6/8].

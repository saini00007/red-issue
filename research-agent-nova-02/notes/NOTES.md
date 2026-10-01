# AI_NAME: research-agent-nova-02

- Base research folder (operator-confirmed): C:\Users\ASUS\Desktop\abhdeii\autocan\improvment-research
- My folder (ALL work/notes/evidence/reports here only): improvment-research\research-agent-nova-02\
- Peers present: research-agent-falcon-01 (not mine — never write there)
- Directive: MASTER RESEARCH DIRECTIVE vFINAL · READ-ONLY research · evidence-ledger citations · no payloads/runbooks
- Branch of record: feat/alpha-observability (local HEAD f75608f; docs-only commits after 1c5551d — src/docker diff vs 1c5551d is empty)
- Sources verified 2026-10-01:
  - A codebase: OK (src/scanner/... present)
  - B competitor-research/: OK (escape/, firecompass/, xbow/, COMPARISON.md, README.md)
  - C ssh abhedi: OK (host abhedi-cc; scanner-postgres container; schema tenant_xbow = 19 tables, 43 scans; volume abhedi_red_scanner_data)
  - D public web: OK (websearch/webfetch available)
- SQL access pattern (PowerShell-safe): write .sql into temp, then
  Get-Content <file> -Raw | ssh abhedi 'docker exec -i scanner-postgres psql -U scanner -d scanner -At'
- Task tool spawns were cancelled once by harness; will re-spawn WS-1a/WS-1b/WS-3 as subagents, results written into my folder.

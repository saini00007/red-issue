import sys
sys.path.insert(0, r"C:\Users\ASUS\Desktop\abhdeii\autocan\src")
from scanner.agent_runtime.oracle_map import required_oracle_for, GROUP_FOR_CLASS
from scanner.agent_runtime.taxonomy import VulnClass

for n in ("GRAPHQL", "WEBSOCKET", "WEBHOOK", "RATE_LIMIT", "AI_PROMPT_INJECTION",
          "AI_RAG_LEAK", "AI_TOOL_ABUSE", "SQLI", "IDOR_BOLA", "XSS_DOM", "PRICE_TAMPER"):
    vc = getattr(VulnClass, n)
    grp = GROUP_FOR_CLASS.get(vc.value, "config")
    print("%-24s group=%-10s required_oracle=%s" % (vc.value, grp, required_oracle_for(vc)))

# does the ledger skill-gate flag exist / default?
from scanner.config import get_settings
s = get_settings()
for f in ("scanner_graphql_authz_enabled", "scanner_channel_oracles_enabled",
          "scanner_ai_redteam_floor", "scanner_ledger_machine_close",
          "scanner_engine_chain_floor", "scanner_executed_chain_findings",
          "scanner_ssrf_cloud_exfil", "scanner_browser_enabled",
          "scanner_browser_instrument_enabled"):
    print("%-42s default=%s" % (f, getattr(s, f, "<absent>")))

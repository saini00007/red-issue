import os, glob
RAW = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\raw"
KEY = ["decisions.log", "ledger_updates.jsonl", "oob_interactions.jsonl", "oob_registry.jsonl",
       "exploit_floor_signals.jsonl", "findings.jsonl", "oob_health.json", "recon.json",
       "coverage_quality.json", "report.json", "scan_brief.md",
       "logs/agent.log", "logs/toolserver.log", "guard/decisions.log"]
for d in ["68a58881-ae3b-4f36-90a9-bf254da13fcb", "1f5fe7c8-5e28-45bc-8e08-a3e868bad87e"]:
    base = os.path.join(RAW, d)
    print("=" * 62)
    print(d)
    for k in KEY:
        p = os.path.join(base, k.replace("/", os.sep))
        if os.path.exists(p):
            print("   %-32s %10d bytes" % (k, os.path.getsize(p)))
        else:
            print("   %-32s %10s" % (k, "ABSENT"))
    n = len(glob.glob(os.path.join(base, "tool_outputs", "*")))
    print("   tool_outputs entries: %d" % n)

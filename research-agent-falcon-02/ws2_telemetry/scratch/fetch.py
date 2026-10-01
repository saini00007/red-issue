import subprocess, sys, os

CONTAINER = "scanner-agent-84aea81a7e43"
WD = "/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/84aea81a-7e43-495c-9974-ca064ddd3552"
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\raw"
os.makedirs(OUT, exist_ok=True)

FILES = ["decisions.log", "ledger_updates.jsonl", "oob_interactions.jsonl",
         "oob_registry.jsonl", "exploit_floor_signals.jsonl", "findings.jsonl"]

for f in FILES:
    remote = f"docker exec {CONTAINER} cat {WD}/{f}"
    p = subprocess.run(["ssh", "abhedi", remote], capture_output=True)
    path = os.path.join(OUT, "scan_84aea81a_" + f)
    with open(path, "wb") as fh:
        fh.write(p.stdout)
    print(f"{f}: rc={p.returncode} bytes={len(p.stdout)} -> {path}")

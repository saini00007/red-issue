import os, json, subprocess
ROOT="/var/lib/scanner"
print("=== H1 top-level ===")
tops=sorted(os.listdir(ROOT))
print("count:", len(tops))
for t in tops[:40]: print("  ", t)

rows=[]
for h in tops:
    hp=os.path.join(ROOT,h)
    if not os.path.isdir(hp): continue
    try: subs=sorted(os.listdir(hp))
    except Exception as e: continue
    for sid in subs:
        d=os.path.join(hp,sid)
        if not os.path.isdir(d): continue
        def nl(fn):
            p=os.path.join(d,fn)
            if not os.path.isfile(p): return None
            n=0
            with open(p,'rb') as f:
                for _ in f: n+=1
            return n
        def sz(fn):
            p=os.path.join(d,fn)
            return os.path.getsize(p) if os.path.isfile(p) else None
        to=0
        tod=os.path.join(d,"tool_outputs")
        if os.path.isdir(tod): to=len(os.listdir(tod))
        rows.append(dict(host=h, scan=sid,
            ledger=nl("ledger_updates.jsonl"), oob=nl("oob_interactions.jsonl"),
            reg=nl("oob_registry.jsonl"), dec=nl("decisions.log"),
            alog=nl("logs/agent.log"), toolserver=nl("logs/toolserver.log"),
            toolouts=to,
            findings=nl("findings.jsonl"), floor=nl("exploit_floor_signals.jsonl"),
            cq=sz("coverage_quality.json"), rj=sz("report.json"), brief=sz("scan_brief.md"),
            recon=sz("recon.json")))
print("=== H2 workdirs: %d ==="%len(rows))
hdr=("scan","ledger","oob","reg","dec","alog","tslog","toolouts","find","floor","cq","rj")
print("%-10s %-10s %7s %7s %7s %6s %7s %7s %8s %7s %7s %8s"%hdr)
for r in sorted(rows,key=lambda x:(x["ledger"] or 0),reverse=True):
    print("%-10s %-10s %7s %7s %7s %6s %7s %7s %8s %7s %7s %8s"%(
        r["scan"][:8], r["host"][:8], r["ledger"],r["oob"],r["reg"],r["dec"],r["alog"],r["toolserver"],r["toolouts"],r["findings"],r["floor"],r["cq"],r["rj"]))
json.dump(rows, open("/tmp/ws2_wd_inventory.json","w"))
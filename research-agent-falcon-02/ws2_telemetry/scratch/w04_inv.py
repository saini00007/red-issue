import os, json
ROOT="/var/lib/scanner"
rows=[]
for h in sorted(os.listdir(ROOT)):
    hp=os.path.join(ROOT,h)
    if not os.path.isdir(hp): continue
    for sid in sorted(os.listdir(hp)):
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
        tod=os.path.join(d,"tool_outputs")
        to=len(os.listdir(tod)) if os.path.isdir(tod) else 0
        rows.append(dict(host=h, scan=sid,
            ledger=nl("ledger_updates.jsonl"), oob=nl("oob_interactions.jsonl"),
            reg=nl("oob_registry.jsonl"), dec=nl("decisions.log"),
            alog=nl("logs/agent.log"), toolserver=nl("logs/toolserver.log"),
            toolouts=to, findings=nl("findings.jsonl"),
            floor=nl("exploit_floor_signals.jsonl"),
            cq=sz("coverage_quality.json"), rj=sz("report.json"),
            brief=sz("scan_brief.md"), recon=sz("recon.json")))
print("workdirs:",len(rows))
print("%-9s %-9s %7s %7s %7s %6s %7s %8s %8s %7s %6s %9s"%("scan","host","ledger","oob","reg","dec","alog","tslog","toolout","find","floor","rjson"))
for r in sorted(rows,key=lambda x:-(x["ledger"] or 0)):
    print("%-9s %-9s %7s %7s %7s %6s %7s %8s %8s %7s %6s %9s"%(
        r["scan"][:8], r["host"][:8], r["ledger"],r["oob"],r["reg"],r["dec"],
        r["alog"],r["toolserver"],r["toolouts"],r["findings"],r["floor"],r["rj"]))
json.dump(rows, open("/tmp/ws2_wd.json","w"))
print("saved /tmp/ws2_wd.json")
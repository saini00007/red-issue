import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,d,p))

PATS = {
 "context_reset/compact/summar": r"(context.{0,20}(reset|compact|truncat|summar|overflow)|compact|truncat)",
 "max_turns": r"max turns|max_turns",
 "no_choices": r"no choices",
 "rate_limit_429": r"(429|rate.?limit|too many requests)",
 "upstream_500": r"(error code: 500|internal server error)",
 "timeout": r"(timeout|timed out|readtimeout|connecttimeout)",
 "retry": r"\bretry|retries|retrying|attempt \d",
 "oom_137": r"(exit 137|oom|killed)",
 "lease/claim_conflict": r"(lease|claim_conflict|already claimed|stale lease)",
 "toolserver_error": r"(toolserver.{0,30}(error|fail|timeout|refused))",
 "json_decode": r"(jsondecode|decodeerror|expecting value)",
 "budget/limit_stop": r"(budget|turn limit|max_iterations|stop_reason)",
 "checkpoint_restore": r"(checkpoint|restore|resume)",
}
hits=collections.Counter(); scan_hits=collections.defaultdict(set)
tool_started=0; tool_done=0
per_scan_tools=collections.Counter(); per_scan_tool_done=collections.Counter()
stop_reasons=collections.Counter()
for sid,d,p in files:
    txt=open(p,encoding="utf-8",errors="replace").read()
    for k,pat in PATS.items():
        n=len(re.findall(pat,txt,re.I))
        if n: hits[k]+=n; scan_hits[k].add(sid[:8])
    for m in re.finditer(r'event_type=tool\.started',txt): tool_started+=1
    for m in re.finditer(r'event_type=tool\.done',txt): tool_done+=1
    per_scan_tools[sid[:8]]=txt.count("event_type=tool.started")
    per_scan_tool_done[sid[:8]]=txt.count("event_type=tool.done")
    for m in re.finditer(r'stop_reason[=: ]+"?([A-Za-z_ ]+)"?',txt): stop_reasons[m.group(1)[:24]]+=1
    for m in re.finditer(r'event_type=worker\.finished[^\n]*',txt):
        s=m.group(0)
        for k in ("ok","partial","error","running"):
            if "status="+k in s: stop_reasons["wf:"+k]+=1
print("=== SIGNAL CENSUS across 27 agent.log files (126,407 lines) ===")
for k in PATS:
    print("   %-28s %7d hits  scans=%2d"%(k,hits[k],len(scan_hits[k])))
print()
print("tool.started=%d  tool.done=%d  unpaired=%d"%(tool_started,tool_done,tool_started-tool_done))
print()
print("=== stop_reason / worker.finished status census ===")
for k,v in stop_reasons.most_common(20): print("   %-28s %7d"%(k,v))
print()
print("=== per-scan tool.started (top 15) ===")
for sid,n in per_scan_tools.most_common(15):
    print("   %-10s started=%-7d done=%-7d unpaired=%d"%(sid,n,per_scan_tool_done[sid],n-per_scan_tool_done[sid]))
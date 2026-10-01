import os, json, collections, datetime
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
UTC=datetime.timezone.utc
def jl(p):
    if not os.path.isfile(p): return []
    o=[]
    for ln in open(p,encoding="utf-8",errors="replace"):
        ln=ln.strip()
        if ln: 
            try: o.append(json.loads(ln))
            except Exception: pass
    return o
def iso(v):
    if not v: return None
    s=str(v).strip().replace("Z","+00:00")
    if "." in s:
        head,_,tail=s.partition(".");fr="";rest=""
        for i,ch in enumerate(tail):
            if ch.isdigit(): fr+=ch
            else: rest=tail[i:];break
        s=head+"."+fr[:6]+rest
    try:
        d=datetime.datetime.fromisoformat(s); return d if d.tzinfo else d.replace(tzinfo=UTC)
    except Exception: return None
def extract_token(fh,dom):
    host=(fh or "").strip().lower().rstrip("."); dom=(dom or "").strip().lower().rstrip(".")
    if not host or not dom: return None
    corr=dom.split(".",1)[0]
    for suf in (dom,corr):
        if suf and host.endswith("."+suf):
            pre=host[:-(len(suf)+1)]
            return pre.split(".",1)[0] if pre else None
    return None
_QUAL={"blind","vuln","stored","reflected","injection","oob","attack","confirmed","based","server","side","out","of","band"}
_DIRECT={"ssrf":"ssrf","xxe":"xxe"}
def classify(claim,proto):
    if (proto or "").strip().lower() in {"ldap","ldaps","rmi"}: return "jndi"
    toks=[t for t in __import__("re").split(r"[^a-z0-9]+",(claim or "").strip().lower()) if t and t not in _QUAL]
    m={_DIRECT.get(t) for t in toks}
    if toks and len(m)==1 and None not in m: return next(iter(m))
    return "ssrf"

# match tokens -> what finding (if any) references that oob_token
print("### Q2b  Does a linked OOB callback actually become a finding? Does class stay honest?")
tot=collections.Counter()
print("%-9s %6s %7s %7s %7s %7s %7s %7s %7s"%("scan","linked","fnd_oob","tk_in_fnd","honest","claimclass","delta_t_med_s","pre_floor","unmatched_tok"))
agg=dict(linked=0, fnd_oob=0, tk=0, demoted=0, pre=0)
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid)
    if not os.path.isdir(d): continue
    hp=os.path.join(d,"oob_health.json")
    dom=""; floor=None
    if os.path.isfile(hp):
        try:
            h=json.load(open(hp,encoding="utf-8")); dom=str(h.get("domain") or ""); floor=iso(h.get("checked_at"))
        except Exception: pass
    regs=jl(os.path.join(d,"oob_registry.jsonl")); ins=jl(os.path.join(d,"oob_interactions.jsonl"))
    by={str(r.get("token")).lower():r for r in regs if r.get("token")}
    seen=set(); linked=[]
    for it in ins:
        host=it.get("full-id") or it.get("full_id") or it.get("host") or it.get("hostname")
        iid=it.get("unique-id") or it.get("unique_id") or it.get("id")
        if not iid or not host: continue
        tok=extract_token(str(host),dom)
        if not tok: continue
        k=(tok,str(iid))
        if k in seen: continue
        seen.add(k)
        reg=by.get(tok)
        if reg is None: continue
        ident=str(it.get("unique-id") or it.get("unique_id") or it.get("full-id") or it.get("full_id") or "").strip()
        if not ident: continue
        ts=iso(it.get("timestamp") or it.get("time") or it.get("received-at"))
        if floor is not None and (ts is None or ts<floor): 
            tot["pre_rejected"]+=1; continue
        linked.append((tok,it,reg,ts))
    # findings referencing an oob token
    fnd=jl(os.path.join(d,"findings.jsonl"))
    ftk=set()
    for f in fnd:
        for k in ("oob_token","oobToken"):
            v=f.get(k)
            if v: ftk.add(str(v))
    honest=collections.Counter(); claimc=collections.Counter(); deltas=[]
    for tok,it,reg,ts in linked:
        hc=classify(reg.get("vuln_class"), it.get("protocol"))
        honest[hc]+=1; claimc[str(reg.get("vuln_class"))[:18]]+=1
        if reg.get("vuln_class") and classify(reg.get("vuln_class"),it.get("protocol"))!=str(reg.get("vuln_class")).lower():
            tot["demoted"]+=1
        if ts and floor: deltas.append((ts-floor).total_seconds())
    deltas.sort()
    pre=sum(1 for x in deltas if x<0)
    matched=sum(1 for tok,_,_,_ in linked if tok in ftk)
    agg["linked"]+=len(linked); agg["fnd_oob"]+=len(ftk); agg["tk"]+=matched; agg["pre"]+=pre
    dm = deltas[len(deltas)//2] if deltas else None
    print("%-9s %6d %7d %7d %7s %7s %7s %7s %7d"%(
        sid[:8], len(linked), len(ftk), matched,
        ",".join("%s:%d"%(k,v) for k,v in honest.most_common(3)) or "-",
        ",".join("%s:%d"%(k,v) for k,v in claimc.most_common(2)) or "-",
        ("%.0f"%dm if dm is not None else "-"), pre,
        max(0,len(linked)-matched)))
print()
print("AGG linked=%d  distinct_oob_tokens_in_findings=%d  linked_tokens_referenced_by_a_finding=%d  demoted_class=%d"%(
    agg["linked"],agg["fnd_oob"],agg["tk"],tot["demoted"]))
print("link rate: %.4f of all interactions"%(agg["linked"]/96765.0))
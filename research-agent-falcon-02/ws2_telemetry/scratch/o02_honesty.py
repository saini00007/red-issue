import os, json, collections, datetime
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
UTC=datetime.timezone.utc

def wdlist():
    out=[]
    for sid in sorted(os.listdir(HOST)):
        d=os.path.join(HOST,sid)
        if os.path.isdir(d): out.append((sid,d))
    return out

def jl(p):
    if not os.path.isfile(p): return []
    o=[]
    with open(p,encoding="utf-8",errors="replace") as f:
        for ln in f:
            ln=ln.strip()
            if not ln: continue
            try: o.append(json.loads(ln))
            except Exception: pass
    return o

def iso(v):
    if not v: return None
    s=str(v).strip().replace("Z","+00:00")
    if "." in s:
        head,_,tail=s.partition(".")
        fr="";rest=""
        for i,ch in enumerate(tail):
            if ch.isdigit(): fr+=ch
            else: rest=tail[i:]; break
        s=head+"."+fr[:6]+rest
    try:
        d=datetime.datetime.fromisoformat(s)
        return d if d.tzinfo else d.replace(tzinfo=UTC)
    except Exception: return None

def extract_token(full_host, dom):
    host=(full_host or "").strip().lower().rstrip(".")
    dom=(dom or "").strip().lower().rstrip(".")
    if not host or not dom: return None
    corr=dom.split(".",1)[0]
    for suf in (dom,corr):
        if suf and host.endswith("."+suf):
            pre=host[:-(len(suf)+1)]
            if pre: return pre.split(".",1)[0]
            return None
    return None

print("### Q2  OOB HONESTY  — all %d workdirs, deterministic re-run of registry.correlate"%len(wdlist()))
print()
hdr=("scan","oobhealth","checked_at","dom#","regs","ins","tokhit","ident_ok","since_ok","unlink_pre","unlink_noident","LINKED")
print("%-9s %-9s %-11s %5s %6s %7s %7s %9s %9s %11s %13s %7s"%hdr)
T=dict(health=collections.Counter(), regs=0, ins=0, tokhit=0, ident_ok=0,
       since_rej=0, pre_unlinked=0, noident_unlinked=0, linked=0, linked_pre=0)
scan_with_linked=[]; scan_with_pre=[]
for sid,d in wdlist():
    hp=os.path.join(d,"oob_health.json")
    health="MISSING"; checked=""; dom=""
    if os.path.isfile(hp):
        try:
            h=json.load(open(hp,encoding="utf-8"))
            health=str(h.get("status","")); checked=str(h.get("checked_at") or ""); dom=str(h.get("domain") or "")
        except Exception: health="UNPARSEABLE"
    T["health"][health if health else "BLANK"]+=1
    floor=iso(checked) if checked else None
    regs=jl(os.path.join(d,"oob_registry.jsonl"))
    ins=jl(os.path.join(d,"oob_interactions.jsonl"))
    by_tok={str(r.get("token")).lower():r for r in regs if r.get("token")}
    seen=set(); tokhit=0; ident_ok=0; since_rej=0; noident=0; linked=0; linked_pre=0
    for it in ins:
        host=it.get("full-id") or it.get("full_id") or it.get("host") or it.get("hostname")
        iid=it.get("unique-id") or it.get("unique_id") or it.get("id")
        if not iid or not host: continue
        tok=extract_token(str(host),dom)
        if not tok: continue
        key=(tok,str(iid))
        if key in seen: continue
        seen.add(key)
        tokhit+=1
        reg=by_tok.get(tok)
        if reg is None: continue
        identity=str(it.get("unique-id") or it.get("unique_id") or it.get("full-id") or it.get("full_id") or "").strip()
        if not identity:
            noident+=1; continue
        ident_ok+=1
        ts=iso(it.get("timestamp") or it.get("time") or it.get("received-at"))
        ok = True if floor is None else (ts is not None and ts>=floor)
        if not ok:
            since_rej+=1
            if ts is not None and ts < floor: linked_pre+=1
            continue
        linked+=1
    T["regs"]+=len(regs); T["ins"]+=len(ins); T["tokhit"]+=tokhit
    T["ident_ok"]+=ident_ok; T["since_rej"]+=since_rej
    T["noident_unlinked"]+=noident; T["linked"]+=linked; T["linked_pre"]+=linked_pre
    if linked: scan_with_linked.append(sid[:8])
    if since_rej: scan_with_pre.append(sid[:8])
    print("%-9s %-9s %-11s %5s %6d %7d %7d %9d %9d %11d %13d %7d"%(
        sid[:8], health[:9], (checked[:10] or "<EMPTY>"), ("Y" if dom else "N"),
        len(regs), len(ins), tokhit, ident_ok,
        (linked if floor else -linked), since_rej, noident, linked))
print()
print("TOTAL interactions=%d  token-hits=%d  ident_ok=%d  linked=%d  rejected_since=%d  rejected_noident=%d"%(
    T["ins"],T["tokhit"],T["ident_ok"],T["linked"],T["since_rej"],T["noident_unlinked"]))
print("oob_health status census:", dict(T["health"]))
print("scans with >=1 LINKED (confirmed-capable) OOB:", len(scan_with_linked), scan_with_linked)
print("scans with >=1 since-gate rejection (stale/pre-scan callbacks present):", len(scan_with_pre), scan_with_pre)
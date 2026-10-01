import sqlite3, json, collections, re
DB="/home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db"
con=sqlite3.connect("file:%s?mode=ro"%DB, uri=True); c=con.cursor()

print("=== E1 request_json top-level key census (structure only) ===")
kc=collections.Counter(); bad=0; sizes=[]
for (rj,) in c.execute("select request_json from calls"):
    sizes.append(len(rj or ""))
    try:
        d=json.loads(rj)
    except Exception:
        bad+=1; continue
    if isinstance(d,dict): kc.update(d.keys())
    else: kc["<non-dict:%s>"%type(d).__name__]+=1
print("unparseable:",bad)
for k,v in kc.most_common(30): print("  ",k,v)
sizes.sort()
if sizes: print("req_json bytes: min=%d p50=%d p90=%d p99=%d max=%d total=%d"%(sizes[0],sizes[len(sizes)//2],sizes[int(len(sizes)*.9)],sizes[int(len(sizes)*.99)],sizes[-1],sum(sizes)))

print("=== E2 response_json key census ===")
kc2=collections.Counter(); sz2=[]
for (rj,) in c.execute("select response_json from calls where response_json is not null and response_json<>''"):
    sz2.append(len(rj))
    try: d=json.loads(rj)
    except Exception: kc2["<unparseable>"]+=1; continue
    if isinstance(d,dict): kc2.update(d.keys())
    else: kc2["<non-dict>"]+=1
for k,v in kc2.most_common(20): print("  ",k,v)
sz2.sort()
if sz2: print("resp_json bytes: min=%d p50=%d p90=%d max=%d total=%d"%(sz2[0],sz2[len(sz2)//2],sz2[int(len(sz2)*.9)],sz2[-1],sum(sz2)))

print("=== E3 does ANY row carry a scan identifier? (presence-only scan) ===")
# presence-only: we count rows whose text matches a uuid-ish token, no values printed
pat_uuid=re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)
pat_workdir=re.compile(r'/var/lib/scanner/', re.I)
pat_proxyhdr=re.compile(r'x-scan-id|x-request-id|scan_id|tenant', re.I)
n_uuid=n_wd=n_hdr=0
for (rj,rsj) in c.execute("select request_json, response_json from calls"):
    blob=(rj or "")+ (rsj or "")
    if pat_uuid.search(blob): n_uuid+=1
    if pat_workdir.search(blob): n_wd+=1
    if pat_proxyhdr.search(blob): n_hdr+=1
print("rows containing a uuid token:", n_uuid)
print("rows containing /var/lib/scanner path:", n_wd)
print("rows containing scan/tenant header-ish token:", n_hdr)
con.close()
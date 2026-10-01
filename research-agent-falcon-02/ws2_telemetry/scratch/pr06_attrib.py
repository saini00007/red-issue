import sqlite3, collections
DB="/home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db"
con=sqlite3.connect("file:%s?mode=ro"%DB, uri=True); c=con.cursor()
print("=== F1 max ts / freshest row (confirm WAL read) ===")
print(c.execute("select max(ts), min(ts), count(*) from calls").fetchone())

# Scan ids that we KNOW routed via logging-proxy (from postgres). We test presence-only.
PROXY_SCANS = {
 "68a58881-":"68a58881 completed",
 "373bff88":"373bff88 completed",
 "05ba4cad":"05ba4cad cancelled",
 "0c33cffd":"0c33cffd cancelled",
 "1397908a":"1397908a completed",
}
print("=== F2 attribution: rows whose payload mentions a known proxy-routed scan prefix ===")
tot=0; matched=collections.Counter()
rows=c.execute("select request_json, response_json, model_req, status from calls").fetchall()
for rj,rsj,mr,st in rows:
    tot+=1
    blob=(rj or "")+(rsj or "")
    hit=[v for k,v in PROXY_SCANS.items() if k in blob]
    for h in hit: matched[h]+=1
print("total rows scanned:", tot)
for k,v in PROXY_SCANS.items():
    print("  %-46s rows_containing=%d"%(v, matched[k]))
con.close()
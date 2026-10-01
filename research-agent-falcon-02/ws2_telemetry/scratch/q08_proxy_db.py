import sqlite3
c = sqlite3.connect("file:/data/proxy_log.db?mode=ro", uri=True)
print("SCHEMA:")
for r in c.execute("select name, sql from sqlite_master"):
    print(" ", r[0], "|", (r[1] or "").replace("\n", " ")[:300])
print("TOTAL_CALLS:", c.execute("select count(*) from calls").fetchone()[0])
print("TS_RANGE:", c.execute("select min(ts), max(ts) from calls").fetchone())
print("BY_MODEL_REQ:")
for r in c.execute("select model_req, model_fwd, count(*), min(ts), max(ts) from calls group by 1,2 order by 3 desc limit 40"):
    print("  ", r)

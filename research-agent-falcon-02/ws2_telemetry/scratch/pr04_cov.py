import sqlite3, json, collections, re, sys
DB="/home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db"
con=sqlite3.connect("file:%s?mode=ro"%DB, uri=True)
c=con.cursor()

def show(label, sql, args=()):
    print("=== %s ==="%label)
    try:
        rows=c.execute(sql,args).fetchall()
    except Exception as e:
        print("ERR", e); return
    if not rows: print("(no rows)")
    for r in rows: print(" | ".join("" if v is None else str(v) for v in r))

show("A1 range", "select min(ts), max(ts), count(*) from calls")
show("A2 endpoint", "select endpoint, count(*) from calls group by 1 order by 2 desc")
show("A3 model_req/fwd", "select coalesce(model_req,'<NULL>'), coalesce(model_fwd,'<NULL>'), count(*) from calls group by 1,2 order by 3 desc limit 40")
show("A4 distinct models", "select count(distinct model_req), count(distinct model_fwd) from calls")
show("A5 status", "select status, count(*) from calls group by 1 order by 2 desc")
show("A6 errors", "select substr(coalesce(error,''),1,100), count(*) from calls where error is not null and error<>'' group by 1 order by 2 desc limit 25")
show("A7 emptiness", """select
  sum(case when request_json is null or request_json='' then 1 else 0 end),
  sum(case when response_json is null or response_json='' then 1 else 0 end),
  sum(case when model_req is null then 1 else 0 end),
  sum(case when prompt_tokens is null then 1 else 0 end),
  sum(prompt_tokens), sum(completion_tokens), sum(total_tokens)
 from calls""")
show("A8 per-hour volume", "select substr(ts,1,13) h, count(*) from calls group by 1 order by 1")
con.close()
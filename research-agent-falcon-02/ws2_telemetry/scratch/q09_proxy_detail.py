import sqlite3
c = sqlite3.connect("file:/data/proxy_log.db?mode=ro", uri=True)
print("BY_ENDPOINT:", c.execute("select endpoint, count(*) from calls group by 1 order by 2 desc").fetchall())
print("MODEL_REQ_NULL_COUNT:", c.execute("select count(*) from calls where model_req is null").fetchone()[0])
print("STATUS:", c.execute("select status, count(*) from calls group by 1 order by 2 desc").fetchall())
print("STREAMED:", c.execute("select streamed, count(*) from calls group by 1").fetchall())
print("HAS_RESPONSE_JSON:", c.execute("select count(*) from calls where response_json is not null and length(response_json)>2").fetchone()[0])
print("HAS_REQUEST_JSON:", c.execute("select count(*) from calls where request_json is not null and length(request_json)>2").fetchone()[0])
print("TOKENS_NULL(streams):", c.execute("select count(*) from calls where total_tokens is null").fetchone()[0], "of", c.execute("select count(*) from calls").fetchone()[0])
print()
print("DAILY_TS:")
for r in c.execute("select substr(ts,1,13) h, model_req, count(*) from calls group by 1,2 order by 1"):
    print("  ", r)

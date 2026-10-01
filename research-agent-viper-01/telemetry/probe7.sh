#!/bin/bash
echo "=== chain evidence in DB ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SET search_path TO tenant_xbow, public;
SELECT scan_id, count(*) AS chain_nodes FROM chain_node GROUP BY scan_id ORDER BY 2 DESC LIMIT 6;
SELECT scan_id, count(*) AS chain_edges FROM chain_edge GROUP BY scan_id ORDER BY 2 DESC LIMIT 6;
SELECT scan_id, count(*) FILTER (WHERE verification_method='executed_chain') AS vm_exec_chain, count(*) AS total
FROM findings GROUP BY scan_id ORDER BY total DESC LIMIT 8;
SQL
echo "=== running scan: oob registry + fired tokens ==="
B=/var/lib/docker/volumes/abhedi_red_scanner_data/_data/16e69f07-f908-482b-8fc5-492852a61a91/84aea81a-7e43-495c-9974-ca064ddd3552
sudo cat "$B/oob_registry.jsonl" 2>/dev/null | python3 -c "
import sys, json, collections
c=collections.Counter(); n=0
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: o=json.loads(line)
    except Exception: continue
    n+=1; c[str(o.get('vuln_class') or '?')]+=1
print('registry tokens:', n, '| classes:', c.most_common(12))
"
echo "=== proxy_log.db: schema + row counts ONLY (no prompt/response bodies) ==="
ls -la /home/admin/research/2026-09-29-deepdive/proxy/data/ 2>/dev/null || sudo ls -la /home/admin/research/2026-09-29-deepdive/proxy/data/
command -v sqlite3 >/dev/null && sqlite3 /home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db ".tables" || python3 - <<'PY'
import sqlite3
con = sqlite3.connect('file:/home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db?mode=ro', uri=True)
cur = con.cursor()
tabs = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print('tables:', tabs)
for t in tabs:
    cols = [r[1] for r in cur.execute(f'PRAGMA table_info({t})')]
    n = cur.execute(f'SELECT count(*) FROM {t}').fetchone()[0]
    print(f'table={t} rows={n} cols={cols}')
# provider/model distribution only if a safe column exists
for t in tabs:
    cols = [r[1] for r in cur.execute(f'PRAGMA table_info({t})')]
    if 'model' in cols:
        for row in cur.execute(f'SELECT model, count(*) FROM {t} GROUP BY model LIMIT 15'):
            print('model_dist:', row)
PY

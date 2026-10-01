#!/bin/bash
echo "=== remaining CP flags ==="
docker exec scanner-cp printenv | grep -E '^(SCANNER_ENGINE_CHAIN_FLOOR|SCANNER_ENGINE_CHAIN_MAX_DEPTH|SCANNER_ENGINE_PLAYBOOK|SCANNER_ENGINE_MAX_TURNS|SCANNER_BROWSER_AUTHED_CRAWL|SCANNER_SSO_LOGIN|SCANNER_BROWSER_REAUTH|SCANNER_TEMPLATE_REACHABILITY_LABELS|SCANNER_TWO_IDENTITY_AUTHZ_ENABLED|SCANNER_CROSS_TENANT_ENABLED|SCANNER_DEFERRED_CONFIRMATION|SCANNER_ENGINE_VERIFY|SCANNER_ENGINE_RESUME)='
echo "=== logging-proxy presence + DB schema (no prompt bodies) ==="
docker exec -i logging-proxy sqlite3 /data/proxy_log.db ".tables" 2>/dev/null || docker inspect logging-proxy --format '{{json .Mounts}}' | head -c 400
echo
echo "=== scan workdirs with chain evidence (executed_chain category or chain findings) ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SET search_path TO tenant_xbow, public;
SELECT scan_id, count(*) FILTER (WHERE category='executed_chain') AS executed_chain,
       count(*) FILTER (WHERE verification_method='executed_chain') AS vm_exec_chain,
       count(*) AS total
FROM findings GROUP BY scan_id ORDER BY total DESC LIMIT 8;
SELECT scan_id, count(*) AS chain_nodes FROM chain_node GROUP BY scan_id ORDER BY 2 DESC LIMIT 5;
SELECT scan_id, count(*) AS chain_edges FROM chain_edge GROUP BY scan_id ORDER BY 2 DESC LIMIT 5;
SQL
echo "=== oob honest-classification outcome (running scan): matched vs unlinked, honest classes ==="
B=/var/lib/docker/volumes/abhedi_red_scanner_data/_data/16e69f07-f908-482b-8fc5-492852a61a91/84aea81a-7e43-495c-9974-ca064ddd3552
sudo cat "$B/oob_registry.jsonl" 2>/dev/null | python3 -c "
import sys, json, collections
c=collections.Counter(); n=0
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: o=json.loads(line)
    except Exception: continue
    n+=1
    c[str(o.get('vuln_class') or '?')]+=1
print('registry tokens:',n,'| classes:',c.most_common(12))
" 2>/dev/null
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SET search_path TO tenant_xbow, public;
SELECT count(*) AS oob_tokens, count(*) FILTER (WHERE fired_at IS NOT NULL) AS fired
FROM oob_token WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552';
SQL

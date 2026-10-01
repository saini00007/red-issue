L=scanner-agent-84aea81a7e43
echo "== agent log event histogram (floor/chain/channel/graphql) =="
docker logs "$L" 2>&1 | grep -oE 'exploit_floor\.[a-z_]+|chain_floor\.[a-z_]+|channels\.[a-z_]+|floor\.tick|graphql|reconcile\.tick|father\.[a-z_]+' | uniq -c
echo "== agent log: does exploit_floor.complete appear at all? =="
docker logs "$L" 2>&1 | grep -c 'exploit_floor'
echo "== sample of first 5 structured log lines (keys only, no values) =="
docker logs "$L" 2>&1 | head -5 | cut -c1-200
echo "== CP log event histogram (floor/chain/graphql) =="
docker logs scanner-cp 2>&1 | grep -oE 'exploit_floor\.[a-z_]+|chain_floor\.[a-z_]+|channels\.[a-z_]+|graphql' | uniq -c

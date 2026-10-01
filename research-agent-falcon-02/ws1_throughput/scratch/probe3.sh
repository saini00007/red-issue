#!/bin/sh
echo "===== sample lines ====="
docker logs scanner-agent-84aea81a7e43 2>&1 | sed -n '1,3p;500,503p'
echo "===== event histogram ====="
docker logs scanner-agent-84aea81a7e43 2>&1 \
 | grep -oE 'event=[A-Za-z0-9_.]+' | sort | uniq -c | sort -rn | sed -n '1,45p'
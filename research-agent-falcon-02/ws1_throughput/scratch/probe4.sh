#!/bin/sh
L=/tmp/agentlog.$$
docker logs scanner-agent-84aea81a7e43 > $L 2>&1
echo "===== total lines ====="
wc -l < $L
echo "===== event_type histogram (top 40) ====="
grep -oE 'event_type=[A-Za-z0-9_.]+' $L | sort | uniq -c | sort -rn | head -n 40
echo "===== phase / lifecycle markers ====="
grep -nE 'phase|reconnaissance|exploitation|finalize|soft_cap|governor|coverage.quality' $L | head -n 40
echo "===== floor events ====="
grep -cE 'exploit_floor|floor' $L
grep -oE 'exploit_floor[A-Za-z0-9_.]*' $L | sort | uniq -c | sort -rn | head -n 20
rm -f $L
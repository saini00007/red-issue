#!/bin/sh
echo "===== agent log line count ====="
docker logs scanner-agent-84aea81a7e43 2>&1 | wc -l
echo "===== event name histogram ====="
docker logs scanner-agent-84aea81a7e43 2>&1 \
 | grep -oE '"event": *"[^"]+"' | sed 's/.*: *"//; s/"$//' | sort | uniq -c | sort -rn | head -50
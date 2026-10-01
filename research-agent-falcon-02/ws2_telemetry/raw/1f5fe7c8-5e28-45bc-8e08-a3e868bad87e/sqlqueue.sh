#!/bin/bash
# Single-writer sqlmap queue runner.
O=/work/tool_outputs
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
while read -r name; do
  [ -z "$name" ] && continue
  args=$(cat $O/sqout/$name.args)
  echo "START $name $(date +%T)" >> $O/sq_progress.txt
  sqlmap $args --batch --level=5 --risk=3 --dbs --threads=1 --flush-session \
    -H "User-Agent: $UA" -H "Accept: */*" -H "Accept-Encoding: identity" \
    -H "Connection: close" --timeout=20 --retries=1 \
    --output-dir=$O/sqout/$name > $O/sq_$name.log 2>&1
  echo "DONE  $name $(date +%T)" >> $O/sq_progress.txt
done < /work/sqlqueue_list.txt
echo "QUEUE FINISHED $(date)" >> $O/sq_progress.txt

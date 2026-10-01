set -u
echo "=== G1 volume ==="
docker volume inspect abhedi_red_scanner_data --format '{{.Mountpoint}}' 2>&1
echo "=== G2 count of scan workdirs (depth-3 uuid dirs) ==="
V=$(docker volume inspect abhedi_red_scanner_data --format '{{.Mountpoint}}')
echo "V=$V"
ls -1 "$V" 2>&1 | head -50
echo "--- total top-level ---"
ls -1 "$V" 2>/dev/null | wc -l
echo "=== G3 all workdirs, with size + mtime + key artifact presence ==="
for h in $(ls -1 "$V" 2>/dev/null); do
  for d in "$V/$h"/*/; do
    [ -d "$d" ] || continue
    sid=$(basename "$d")
    lu=""; oi=""; dm=""; rg=""; al=""
    [ -f "$d/ledger_updates.jsonl" ] && lu=$(wc -l < "$d/ledger_updates.jsonl")
    [ -f "$d/oob_interactions.jsonl" ] && oi=$(wc -l < "$d/oob_interactions.jsonl")
    [ -f "$d/oob_registry.jsonl" ] && rg=$(wc -l < "$d/oob_registry.jsonl")
    [ -f "$d/decisions.log" ] && dm=$(wc -l < "$d/decisions.log")
    [ -f "$d/logs/agent.log" ] && al=$(wc -l < "$d/logs/agent.log")
    sz=$(du -sm "$d" 2>/dev/null | cut -f1)
    echo "$h/$sid | MB=$sz | ledger=$lu oob=$oi reg=$rg dec=$dm agentlog=$al | $(stat -c %y "$d" 2>/dev/null | cut -c1-16)"
  done
done
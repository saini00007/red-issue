#!/bin/bash
echo "=== poller tail ==="
docker logs scanner-cp --since 3h 2>&1 | grep -Ei "poller|spawn|finaliz|sigkill|sigterm|claim|heartbeat" | tail -30
echo "=== running scan workdir meta ==="
D=/var/lib/docker/volumes/abhedi_red_scanner_data/_data/16e69f07-f908-482b-8fc5-492852a61a91/84aea81a-7e43-495c-9974-ca064ddd3552
sudo ls "$D" 2>/dev/null | head -40
echo "--- key file sizes/lines ---"
for f in decisions.log ledger_updates.jsonl oob_interactions.jsonl findings.jsonl exploit_floor_signals.jsonl logs/agent.log; do
  if sudo test -f "$D/$f"; then sudo wc -l "$D/$f"; fi
done
echo "=== long scan decisions.log tail ==="
sudo tail -30 /var/lib/docker/volumes/abhedi_red_scanner_data/_data/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/decisions.log 2>/dev/null

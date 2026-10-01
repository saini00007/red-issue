#!/bin/bash
# Validate the OOB oracle: mint a token NEVER sent to the target.
# If it still "fires", the oracle is unreliable and no callback finding can be trusted.
W="$WORK_PATH/tool_outputs/sqlmap"
mkdir -p "$W"
D="dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

echo "=== DNS: random control host (never sent to target)"
for h in "totallyrandomctl99$RANDOM" "zzznotreal$RANDOM" "ctrlsqli$SANDOM"; do
  getent hosts "$h.$D" | head -2
done

echo "=== HTTP: control host with random Host header"
for h in "ctlhost$RANDOM.zzz"; do
  curl -s -m 8 -o /dev/null -w "host=$h code=%{http_code} size=%{size_download}\n" \
    "http://$h.$D/" || echo "curl failed $h"
done
echo "=== dig any random label"
dig +short "ctl$RANDOM.$D" A 2>/dev/null | head -3
echo "=== registered tokens (if any)"
ls -la /work/oob_registry.jsonl "$WORK_PATH/oob_registry.jsonl" 2>/dev/null

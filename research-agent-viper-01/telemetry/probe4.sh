#!/bin/bash
echo "=== runtime_settings (redacted values) ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SELECT key, CASE WHEN key ILIKE '%key%' OR key ILIKE '%token%' OR key ILIKE '%secret%' OR key ILIKE '%password%' THEN '[redacted]' ELSE "value" END AS value
FROM public.runtime_settings ORDER BY key;
SQL
echo "=== scan_events for long completed scan ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SET search_path TO tenant_xbow, public;
SELECT event_type, count(*) FROM scan_events WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' GROUP BY 1 ORDER BY 2 DESC LIMIT 16;
SELECT agent_id, count(*) AS turns, sum(tokens_in) AS tin, sum(tokens_out) AS tout
FROM agent_messages WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' GROUP BY agent_id ORDER BY turns DESC LIMIT 12;
SQL
echo "=== poller logs (last 6h, spawn/finalize/heartbeat) ==="
docker logs scanner-cp --since 6h 2>&1 | grep -Ei "scan\.|spawn|finali|sigterm|sigkill|poll" | tail -n 30

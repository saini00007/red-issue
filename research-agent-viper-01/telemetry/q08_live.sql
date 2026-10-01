SET search_path TO tenant_xbow, public;
-- live operator overrides (non-secret flags only; redact anything looking like a key)
SELECT key, CASE WHEN key ~* '(key|token|secret|password)' THEN '<redacted>' ELSE value END AS value
FROM public.runtime_settings ORDER BY key;
-- agent_messages: roles, turns, cost for running scan
SELECT role, count(*), sum(tokens_in) AS tin, sum(tokens_out) AS tout FROM agent_messages
WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552' GROUP BY role ORDER BY 2 DESC;
SELECT count(*) AS msgs, count(DISTINCT agent_id) AS agents, max(turn_index) AS max_turn
FROM agent_messages WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552';
-- scan_events: reconcile census + plan events if recorded
SELECT column_name FROM information_schema.columns WHERE table_schema='tenant_xbow' AND table_name='scan_events' ORDER BY ordinal_position;
SELECT event_type, count(*) FROM scan_events WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552' GROUP BY 1 ORDER BY 2 DESC LIMIT 20;

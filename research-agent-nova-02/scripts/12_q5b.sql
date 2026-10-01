select scan_id, max(turn_index)::text, count(*)::text from tenant_xbow.agent_messages group by scan_id order by max(turn_index) desc nulls last limit 8;
select s.status, count(distinct m.scan_id) from tenant_xbow.scans s left join tenant_xbow.agent_messages m on m.scan_id=s.scan_id group by s.status;

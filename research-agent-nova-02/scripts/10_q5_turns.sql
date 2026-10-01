select 'turns_per_scan', count(*), round(avg(n),1), max(n), min(n) from (select scan_id, count(*) n from tenant_xbow.agent_messages where role='assistant' group by 1) t;
select 'msgs_per_scan', count(*), round(avg(n),1), max(n) from (select scan_id, count(*) n from tenant_xbow.agent_messages group by 1) t;
select 'role', role, count(*) from tenant_xbow.agent_messages group by 2 order by 3 desc;
select 'max_turn_per_scan', scan_id, max(turn_index) from tenant_xbow.agent_messages group by 1 order by 2 desc nulls last limit 10;
select 'msgs_with_null_turn', count(*) from tenant_xbow.agent_messages where turn_index is null;
select 'distinct_scans_with_msgs', count(distinct scan_id) from tenant_xbow.agent_messages;

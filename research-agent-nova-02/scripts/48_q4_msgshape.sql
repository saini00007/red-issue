select scan_id, count(*) msgs, max(turn_index) max_turn, count(distinct agent_id) agents from tenant_xbow.agent_messages where role='assistant' group by 1 order by 2 desc limit 6;
select 'total_msgs', count(*), 'assistant', count(*) filter (where role='assistant'), 'turn_max_overall', max(turn_index) from tenant_xbow.agent_messages;
select role, count(*) from tenant_xbow.agent_messages group by 1;
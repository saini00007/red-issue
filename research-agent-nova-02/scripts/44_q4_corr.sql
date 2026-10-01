with t as (select scan_id, max(turn_index)+1 turns from tenant_xbow.agent_messages where role='assistant' group by 1),
     f as (select scan_id, count(*) n from tenant_xbow.findings group by 1),
     j as (select t.scan_id, t.turns, coalesce(f.n,0) finds from t left join f using (scan_id))
select 'corr', count(*), round(corr(turns, finds)::numeric,3), round(avg(turns)::numeric,2), round(avg(finds)::numeric,2) from j;
select 'scans_with_msgs', (select count(distinct scan_id) from tenant_xbow.agent_messages), 'total_scans', count(*) from tenant_xbow.scans;
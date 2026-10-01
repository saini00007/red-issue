select 'model_counts', model, count(*), count(distinct scan_id) from tenant_xbow.agent_messages group by 2 order by 3 desc;
select 'role_counts', role, count(*) from tenant_xbow.agent_messages group by 2 order by 3 desc;
select 'tok_in_turn', count(*), round(avg(tokens_in),0), max(tokens_in), min(tokens_in) from tenant_xbow.agent_messages where role='assistant' and tokens_in is not null;
select 'tok_out_turn', count(*), round(avg(tokens_out),0), max(tokens_out), min(tokens_out) from tenant_xbow.agent_messages where role='assistant' and tokens_out is not null;
select 'tok_bucket', case when turn_index<=2 then 't0-2' when turn_index<=6 then 't3-6' when turn_index<=20 then 't7-20' else 't21+' end b,
       count(*), round(avg(tokens_in),0), round(avg(tokens_out),0), sum(tokens_in), sum(tokens_out)
from tenant_xbow.agent_messages where role='assistant' group by 2 order by 2;
select 'cost', count(*), round(sum(cost_usd)::numeric,4), round(avg(cost_usd)::numeric,6), max(cost_usd) from tenant_xbow.agent_messages;
select 'cost_nonzero', count(*) from tenant_xbow.agent_messages where cost_usd is not null and cost_usd<>0;
select 'turns_vs_findings', t.maxturn, count(*), coalesce(sum(f.n),0) from (select scan_id, max(turn_index) maxturn from tenant_xbow.agent_messages where role='assistant' group by 1) t left join (select scan_id, count(*) n from tenant_xbow.findings group by 1) f using (scan_id) group by 2 order by 2;
select 'turns_bucket_findings', case when t.maxturn<=2 then 'lt3' when t.maxturn<=7 then '3-7' else '8+' end b, count(*) scans, round(avg(coalesce(f.n,0)),1) avg_findings, coalesce(sum(f.n),0) tot_findings from (select scan_id, max(turn_index) maxturn from tenant_xbow.agent_messages where role='assistant' group by 1) t left join (select scan_id, count(*) n from tenant_xbow.findings group by 1) f using (scan_id) group by 2 order by 2;

select time_cap_seconds, count(*) from tenant_xbow.scans group by time_cap_seconds order by 1 desc nulls last;
select cost_cap_usd::text, count(*), round(avg(cost_spent_usd),3) from tenant_xbow.scans group by cost_cap_usd order by 1 desc nulls last limit 8;
select scan_id, count(*) from tenant_xbow.findings group by scan_id order by 2 desc;
select round(avg(cost_spent_usd),3), max(cost_spent_usd) from tenant_xbow.scans;

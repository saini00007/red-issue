select event_type, count(*) from tenant_xbow.scan_events where event_type ilike '%cancel%' or event_type ilike '%kill%' or event_type ilike '%error%' or event_type ilike '%fail%' group by 1 order by 2 desc;
select action, count(*) from tenant_xbow.audit_log group by 1 order by 2 desc limit 15;
select event_type, count(*) from tenant_xbow.scan_events where event_type ilike '%method%' or event_type ilike '%governor%' or event_type ilike '%spawn%' or event_type ilike '%resume%' group by 1 order by 2 desc;

select 'first_ledger_lag_s_min_med_max',
  round(min(lag))::text, round((percentile_cont(0.5) within group (order by lag))::numeric)::text, round(max(lag))::text
from (select extract(epoch from (min(c.updated_at)-s.created_at)) lag
      from tenant_xbow.scans s join tenant_xbow.ledger_cell c on c.scan_id=s.scan_id
      group by s.scan_id, s.created_at) t;
select 'active_window_s_min_med_max',
  round(min(w))::text, round((percentile_cont(0.5) within group (order by w))::numeric)::text, round(max(w))::text
from (select extract(epoch from (max(c.updated_at)-min(c.updated_at))) w
      from tenant_xbow.ledger_cell c group by scan_id) t;
select 'all_cells_state_pct', state, count(*), round(100.0*count(*)/sum(count(*)) over (),1) from tenant_xbow.ledger_cell group by state order by 3 desc;
select 'resolved_vs_applicable', count(*) filter (where applicable) , count(*) filter (where applicable and state in ('confirmed','tested_clean','blocked'));

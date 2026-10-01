select s.scan_id, s.status,
  round(extract(epoch from s.created_at))::text as created_epoch,
  round(extract(epoch from min(c.updated_at)))::text as first_cell_upd,
  round(extract(epoch from max(c.updated_at)))::text as last_cell_upd,
  round(extract(epoch from max(c.last_progress)))::text as last_progress,
  count(*) filter (where c.updated_at is not null) cells_touched
from tenant_xbow.scans s left join tenant_xbow.ledger_cell c on c.scan_id=s.scan_id
group by 1,2 order by s.created_at;

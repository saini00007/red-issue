select scan_id, left(coalesce(status,''),14) as status, left(coalesce(model,''),26) as model,
       left(coalesce(created_at::text,''),19) as created, left(coalesce(completed_at::text,''),19) as completed
from tenant_xbow.scans order by created_at;

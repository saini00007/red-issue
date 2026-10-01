select scan_id, coalesce(status,'') as status, coalesce(mode,'') as mode,
       left(coalesce(engine_models,''),34) as models,
       left(coalesce(created_at::text,''),19) as created,
       left(coalesce(completed_at::text,''),19) as done,
       coalesce(failure_reason,'') as fail
from tenant_xbow.scans order by created_at;

select count(*) from tenant_xbow.audit_log;
select count(*) from tenant_xbow.checkpoints;
select count(*) from tenant_xbow.worker_runs;
select status, count(*) from tenant_xbow.worker_runs group by 1 order by 2 desc;
select count(*) from tenant_xbow.scan_approvals;

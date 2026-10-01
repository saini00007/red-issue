select phase, status, count(*) from tenant_xbow.worker_runs group by 1,2 order by 3 desc limit 20;
select count(distinct scan_id) from tenant_xbow.worker_runs;
select round(avg(n),1), max(n) from (select scan_id, count(*) n from tenant_xbow.worker_runs group by 1) t;

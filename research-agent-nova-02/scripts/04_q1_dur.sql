select 'terminal', status, count(*), count(completed_at) from tenant_xbow.scans where status<>'running' group by 2 order by 3 desc;
select 'dur_s_min_med_max', count(*)::text,
  round(min(extract(epoch from (completed_at-created_at))))::text,
  round((percentile_cont(0.5) within group (order by extract(epoch from (completed_at-created_at))))::numeric)::text,
  round(max(extract(epoch from (completed_at-created_at))))::text
  from tenant_xbow.scans where completed_at is not null;
select 'dur_by_status', status,
  round(min(extract(epoch from (completed_at-created_at))))::text||'/'||
  round((percentile_cont(0.5) within group (order by extract(epoch from (completed_at-created_at))))::numeric)::text||'/'||
  round(max(extract(epoch from (completed_at-created_at))))::text
  from tenant_xbow.scans where completed_at is not null group by status order by 1,2;
select 'running_age_s', round(extract(epoch from now()-created_at)) from tenant_xbow.scans where status='running';

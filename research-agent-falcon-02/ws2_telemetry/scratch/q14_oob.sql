select 'OOB_TOTAL_TOKENS', count(*)::text from tenant_xbow.oob_token;
select 'OOB_BY_METHOD', method, count(*)::text from tenant_xbow.oob_token group by method order by 2 desc limit 15;
select 'OOB_FIRED_NOTNULL', count(*)::text from tenant_xbow.oob_token where fired_at is not null;
select 'OOB_FIRED_NULL', count(*)::text from tenant_xbow.oob_token where fired_at is null;
select 'OOB_IMPOSSIBLE_fired_lt_created', count(*)::text from tenant_xbow.oob_token
  where fired_at is not null and created_at is not null and fired_at < created_at;
select 'OOB_EQ_fired_eq_created', count(*)::text from tenant_xbow.oob_token
  where fired_at is not null and created_at is not null and fired_at = created_at;
select 'OOB_MIN_LEAD_SECONDS', min(extract(epoch from (fired_at - created_at)))::text from tenant_xbow.oob_token
  where fired_at is not null and created_at is not null;
select 'OOB_DISTINCT_SCANS', count(distinct scan_id)::text from tenant_xbow.oob_token;
select 'OOB_FIRED_DISTINCT_SCANS', count(distinct scan_id)::text from tenant_xbow.oob_token where fired_at is not null;
select 'OOB_HOST_PREFIX', left(full_host, instr(full_host,'.')-1) as pfx, count(*)::text
  from tenant_xbow.oob_token group by 2 order by 3 desc limit 12;
select 'OOB_INTERACTION_KEYS', k, count(*)::text from (
  select jsonb_object_keys(coalesce(interaction,'{}'::jsonb)) k from tenant_xbow.oob_token where interaction is not null
) t group by 1 order by 2 desc;
select 'OOB_LEAD_BUCKET_SEC', least(60, floor(extract(epoch from (fired_at-created_at))))::int::text, count(*)::text
  from tenant_xbow.oob_token where fired_at is not null and created_at is not null group by 1 order by 1::int;

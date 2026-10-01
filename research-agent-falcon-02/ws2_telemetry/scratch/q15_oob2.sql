select 'LEAD_BUCKET', b, count(*)::text from (
  select case when lead < 0.1 then 'a_<0.1s' when lead < 1 then 'b_0.1-1s' when lead < 10 then 'c_1-10s'
              when lead < 60 then 'd_10-60s' when lead < 300 then 'e_1-5min' when lead < 3600 then 'f_5-60min'
              else 'g_>1h' end as b,
         extract(epoch from (fired_at-created_at)) as lead
  from tenant_xbow.oob_token where fired_at is not null and created_at is not null) t
group by 1 order by 1;
select 'LEAD_PCT_LT_1S', round(100.0*count(*) filter (where extract(epoch from (fired_at-created_at))<1)/count(*),2)::text,
       'OF', count(*)::text from tenant_xbow.oob_token where fired_at is not null and created_at is not null;
select 'LEAD_PCT_LT_10S', round(100.0*count(*) filter (where extract(epoch from (fired_at-created_at))<10)/count(*),2)::text,
       'OF', count(*)::text from tenant_xbow.oob_token where fired_at is not null and created_at is not null;
select 'LEAD_MEDIAN', percentile_cont(0.5) within group (order by extract(epoch from (fired_at-created_at)))::text
  from tenant_xbow.oob_token where fired_at is not null and created_at is not null;
select 'INTERACTION_KEYS', k, count(*)::text from (
  select jsonb_object_keys(coalesce(interaction,'{}'::jsonb)) k from tenant_xbow.oob_token where interaction is not null
) t group by 1 order by 2 desc;
select 'FULLHOST_PFX', split_part(full_host,'.',1) as pfx, count(*)::text from tenant_xbow.oob_token group by 1 order by 2 desc limit 12;
select 'METHOD_EMPTY_COUNT', count(*)::text from tenant_xbow.oob_token where coalesce(method,'')='';
select 'CELLID_NULL', count(*)::text from tenant_xbow.oob_token where cell_id is null;

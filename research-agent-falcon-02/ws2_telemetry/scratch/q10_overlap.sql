with parsed as (
  select s.scan_id, s.status, s.created_at, s.completed_at,
         case when coalesce(s.engine_models,'') like '{%'
              then (s.engine_models::jsonb) #> '{models}'
              when coalesce(s.engine_models,'') like '[%'
              then s.engine_models::jsonb
              else '[]'::jsonb end as arr
  from tenant_xbow.scans s
), agg as (
  select p.scan_id, p.status, p.created_at, p.completed_at,
         string_agg(coalesce(m #>> '{id}','?')||'@'||coalesce(m #>> '{provider}','?'),',' order by ord) as models
  from parsed p cross join lateral jsonb_array_elements(p.arr) with ordinality as t(m,ord)
  group by 1,2,3,4
)
select a.scan_id, a.status, a.models,
       to_char(a.created_at at time zone 'UTC','MM-DD HH24:MI') as start_utc,
       to_char(coalesce(a.completed_at,a.created_at) at time zone 'UTC','MM-DD HH24:MI') as end_utc,
       case when a.created_at <= '2026-09-29T23:06:55Z'::timestamptz
             and coalesce(a.completed_at, a.created_at) >= '2026-09-28T22:58:54Z'::timestamptz
            then 'IN_PROXY_WINDOW' else 'outside' end as overlap
from agg a order by overlap desc, a.created_at;

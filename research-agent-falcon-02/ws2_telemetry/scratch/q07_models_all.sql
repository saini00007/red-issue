with parsed as (
  select s.scan_id, s.status,
         case when coalesce(s.engine_models,'') like '{%'
              then (s.engine_models::jsonb) #> '{models}'
              when coalesce(s.engine_models,'') like '[%'
              then s.engine_models::jsonb
              else '[]'::jsonb end as arr
  from tenant_xbow.scans s
)
select p.scan_id, p.status,
       string_agg(coalesce(m #>> '{id}','?')||'@'||coalesce(m #>> '{provider}','?'), ',' order by ord) as models,
       count(*) as n_models
from parsed p
cross join lateral jsonb_array_elements(p.arr) with ordinality as t(m,ord)
group by 1,2 order by 2,1;

select s.scan_id, s.status,
       (s.engine_models::jsonb) #>> '{workers}' as workers,
       string_agg(
         coalesce(m #>> '{id}','?') || '@' || coalesce(m #>> '{provider}','?'), ','
         order by ord
       ) as models
from tenant_xbow.scans s
cross join lateral jsonb_array_elements(
   case when coalesce(s.engine_models,'') like '{%'
        then (s.engine_models::jsonb) #> '{models}'
        else '[]'::jsonb end
) with ordinality as t(m, ord)
where coalesce(s.engine_models,'') like '{%'
group by 1,2,3 order by 3;

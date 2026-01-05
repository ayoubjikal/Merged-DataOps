select
  date_key as date,
  count(distinct customer_key) as dau
from {{ ref('fact_sales') }}
group by 1
order by 1

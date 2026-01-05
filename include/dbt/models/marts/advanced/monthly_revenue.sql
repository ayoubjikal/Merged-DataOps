select
  date_trunc('month', date_key) as month,
  sum(case when is_return then -line_amount else line_amount end) as revenue,
  count(distinct customer_key) as active_customers,
  sum(quantity) as units_sold
from {{ ref('fact_sales') }}
group by 1
order by 1

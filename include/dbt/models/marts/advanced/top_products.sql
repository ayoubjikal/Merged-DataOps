select
  p.product_key,
  p.product_name,
  p.product_category,
  sum(case when is_return then -quantity else quantity end) as total_units,
  sum(case when is_return then -line_amount else line_amount end) as total_revenue
from {{ ref('fact_sales') }} f
left join {{ ref('dim_product') }} p on f.product_key = p.product_key
group by 1,2,3
order by total_revenue desc

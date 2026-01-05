-- Customer Lifetime Value
with customer_revenue as (
  select
    customer_key,
    sum(case when is_return then -line_amount else line_amount end) as total_revenue,
    min(date_key) as first_purchase,
    max(date_key) as last_purchase,
    count(distinct InvoiceNo) as orders_count
  from {{ ref('fact_sales') }}
  group by 1
)

select
  customer_key,
  total_revenue,
  orders_count,
  first_purchase,
  last_purchase,
  total_revenue / nullif(orders_count,0) as avg_order_value
from customer_revenue

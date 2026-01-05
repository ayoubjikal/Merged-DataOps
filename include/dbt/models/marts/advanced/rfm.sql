-- models/marts/advanced/rfm.sql
with base as (
  select
    customer_key,
    max(date_key) as last_purchase_date,
    count(distinct InvoiceNo) as frequency,
    sum(case when is_return then -line_amount else line_amount end) as monetary
  from {{ ref('fact_sales') }}
  group by 1
),

metrics as (
  select
    customer_key,
    last_purchase_date,
    datediff('day', last_purchase_date, current_timestamp()) as recency_days,
    frequency,
    monetary
  from base
)

select
  customer_key,
  recency_days,
  frequency,
  monetary,
  case
    when recency_days <= 30 then 5
    when recency_days <= 60 then 4
    when recency_days <= 120 then 3
    when recency_days <= 240 then 2
    else 1
  end as r_score,
  case
    when frequency >= 10 then 5
    when frequency >= 5 then 4
    when frequency >= 3 then 3
    when frequency >= 2 then 2
    else 1
  end as f_score,
  case
    when monetary >= 1000 then 5
    when monetary >= 500 then 4
    when monetary >= 200 then 3
    when monetary >= 100 then 2
    else 1
  end as m_score
from metrics

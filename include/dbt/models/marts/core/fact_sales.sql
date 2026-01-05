
with sales as (
  select
    line_id,
    InvoiceNo,
    customer_id,
    invoice_ts,
    invoice_date,
    quantity,
    unit_price,
    line_amount,
    is_return,
    StockCode
  from {{ ref('int_sales_lines') }}
)

select
  distinct s.line_id,
  s.InvoiceNo,

  p.product_key,
  s.customer_id as customer_key,
  d.date_key,

  s.quantity,
  s.unit_price,
  s.line_amount,
  s.is_return,

  s.invoice_ts

from sales s
left join {{ ref('dim_product') }} p 
  on s.StockCode = p.product_key

left join {{ ref('dim_date') }} d 
  on s.invoice_date = d.date_key

-- préparer la table de faits
select
  md5(InvoiceNo || '-' || StockCode || '-' || to_varchar(invoice_ts)) as line_id,
  InvoiceNo,
  StockCode,
  description_clean,
  customer_id,
  invoice_ts,
  invoice_date,
  quantity,
  unit_price,
  line_amount,
  is_return
from {{ ref('stg_orders') }}

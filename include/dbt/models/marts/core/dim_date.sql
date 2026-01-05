--dimension date
with d as (
  select
    invoice_date
  from {{ ref('int_dates') }}
)

select
  invoice_date as date_key,
  invoice_date as full_date,
  date_part('year', invoice_date) as year,
  date_part('quarter', invoice_date) as quarter,
  date_part('month', invoice_date) as month,
  date_part('week', invoice_date) as week,
  date_part('day', invoice_date) as day,
  to_varchar(invoice_date, 'YYYY-MM-DD') as date_iso
from d

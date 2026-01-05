-- extrait toutes les dates de transactions uniques.
select distinct
  invoice_date
from {{ ref('stg_orders') }}
where invoice_date is not null

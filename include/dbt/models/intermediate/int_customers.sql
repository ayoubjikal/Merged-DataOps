--lister les clients uniques
select distinct
  customer_id,
  country_clean
from {{ ref('stg_orders') }}
where customer_id is not null

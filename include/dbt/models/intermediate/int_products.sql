-- identifier la liste unique de produits
select distinct
  StockCode,
  description_clean
from {{ ref('stg_orders') }}
where StockCode is not null

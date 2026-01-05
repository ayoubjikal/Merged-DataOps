select
  product_key,
  product_name,
  product_category
from {{ ref('dim_product') }}

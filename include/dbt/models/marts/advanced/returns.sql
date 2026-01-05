select
  *
from {{ ref('int_sales_lines') }}
where is_return = true

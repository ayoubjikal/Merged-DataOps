with ranked as (
    select
        customer_id as customer_key,
        country_clean as country,
        count(*) over (partition by customer_id, country_clean) as cnt
    from {{ ref('int_customers') }}
)

select
    customer_key,
    country
from ranked
qualify row_number() over (partition by customer_key order by cnt desc) = 1

with ranked as (
    select
        StockCode as product_key,
        description_clean as product_name,
        case
            when description_clean ilike '%HEART%' then 'Decor'
            when description_clean ilike '%LANTERN%' then 'Decor'
            when description_clean ilike '%CLOCK%' then 'Homeware'
            when description_clean ilike '%CUPID%' then 'Decor'
            else 'Other'
        end as product_category,
        count(*) over (partition by StockCode, description_clean) as cnt
    from {{ ref('int_products') }}
)

select
    product_key,
    product_name,
    product_category
from ranked
qualify row_number() over (partition by product_key order by cnt desc) = 1

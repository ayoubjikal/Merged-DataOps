with raw as (
  select
    InvoiceNo,
    StockCode,
    Description,
    Quantity,
    InvoiceDate,
    UnitPrice,
    CustomerID,
    Country
  from {{ source('raw_data', 'ecommerce_table') }}
),

typed as (
  select
    InvoiceNo,
    StockCode,
    Description,
    try_cast(Quantity as integer) as quantity,
    try_cast(UnitPrice as float) as unit_price,
    try_cast(CustomerID as integer) as customer_id,
    to_timestamp(InvoiceDate) as invoice_ts,   
    Country
  from raw
),

clean as (
  select
    InvoiceNo,
    StockCode,
    upper(trim(coalesce(Description, ''))) as description_clean,
    coalesce(quantity, 0) as quantity,
    coalesce(unit_price, 0) as unit_price,
    customer_id,
    invoice_ts,
    date_trunc('day', invoice_ts) as invoice_date,
    trim(coalesce(Country, '')) as country_clean,
    (coalesce(quantity,0) * coalesce(unit_price,0)) as line_amount,
    case when quantity < 0 then true else false end as is_return
  from typed
)

select * from clean

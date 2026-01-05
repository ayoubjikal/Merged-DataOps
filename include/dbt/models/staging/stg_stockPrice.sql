SELECT DISTINCT
    INVOICENO as product_id,
	StockCode AS stock_code,
    Description AS description,
    UnitPrice AS price
FROM {{ source('raw_data', 'ecommerce_table') }}
WHERE StockCode IS NOT NULL
AND UnitPrice > 0
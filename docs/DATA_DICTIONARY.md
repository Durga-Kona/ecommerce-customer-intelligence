# Data Dictionary (Warehouse Overview)

## Fact table

### `fact_sales`
One row per order-item sales line. Measures include quantity, sales amount, discount and profit; foreign keys connect to date, customer, product, location and payment dimensions. Use `COUNT(DISTINCT order_id)` for order counts because an order can contain multiple items.

## Dimensions

- `dim_date`: date attributes such as full date, year, quarter and month for time-series analysis.
- `dim_customer`: customer identifier and descriptive customer attributes used for segmentation.
- `dim_product`: product, brand, category and sub-category attributes.
- `dim_location`: city, state and region for geographic analysis.
- `dim_payment`: payment method attributes.

## Source CSVs

- `customers.csv`: customer master data and location/customer attributes.
- `orders.csv`: order header, customer reference, date and status.
- `order_items.csv`: product lines, quantity, unit price and discount.
- `payments.csv`: payment amount, method and status.
- `products.csv`: product catalogue and unit cost/price.
- `returns.csv`: return records and reasons.

Refer to the CSV headers for exact source fields. The import feature requires linked IDs to be consistent across the six files.

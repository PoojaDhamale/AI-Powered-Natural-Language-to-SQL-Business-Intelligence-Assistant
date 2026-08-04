-- 1. Total Revenue
SELECT
    SUM(s.order_quantity * p.product_price) AS total_revenue
FROM sales_data s
JOIN product_lookup p
    ON s.product_key = p.product_key;


-- 2. Revenue by Country
SELECT
    t.country,
    SUM(s.order_quantity * p.product_price) AS revenue
FROM sales_data s
JOIN product_lookup p
    ON s.product_key = p.product_key
JOIN territory_lookup t
    ON s.territory_key = t.territory_key
GROUP BY t.country
ORDER BY revenue DESC;


-- 3. Monthly Revenue Trend
SELECT
    DATE_TRUNC('month', s.order_date) AS month,
    SUM(s.order_quantity * p.product_price) AS revenue
FROM sales_data s
JOIN product_lookup p
    ON s.product_key = p.product_key
GROUP BY DATE_TRUNC('month', s.order_date)
ORDER BY month;


-- 4. Top 10 Products by Revenue
SELECT
    p.product_name,
    SUM(s.order_quantity * p.product_price) AS revenue
FROM sales_data s
JOIN product_lookup p
    ON s.product_key = p.product_key
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 10;


-- 5. Top 10 Customers by Total Spend
SELECT
    c.first_name,
    c.last_name,
    SUM(s.order_quantity * p.product_price) AS total_spent
FROM sales_data s
JOIN customer_lookup c
    ON s.customer_key = c.customer_key
JOIN product_lookup p
    ON s.product_key = p.product_key
GROUP BY c.customer_key, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 10;


-- 6. Revenue by Product Category
SELECT
    cat.category_name,
    SUM(s.order_quantity * p.product_price) AS revenue
FROM sales_data s
JOIN product_lookup p
    ON s.product_key = p.product_key
JOIN product_subcategory_lookup sc
    ON p.product_subcategory_key = sc.product_subcategory_key
JOIN product_category_lookup cat
    ON sc.product_category_key = cat.product_category_key
GROUP BY cat.category_name
ORDER BY revenue DESC;


-- 7. Average Order Value

SELECT
    ROUND(
        SUM(s.order_quantity * p.product_price) / COUNT(DISTINCT s.order_number), 2
    ) AS average_order_value
FROM sales_data s
JOIN product_lookup p
    ON s.product_key = p.product_key;


-- 8. Products with the Highest Returns
SELECT
    p.product_name,
    SUM(r.return_quantity) AS total_returns
FROM returns_data r
JOIN product_lookup p
    ON r.product_key = p.product_key
GROUP BY p.product_name
ORDER BY total_returns DESC
LIMIT 10;


-- 9. Customer Lifetime Value (CLV)

SELECT
    c.customer_key,
    c.first_name,
    c.last_name,
    COUNT(DISTINCT s.order_number) AS total_orders,
    SUM(s.order_quantity * p.product_price) AS lifetime_value
FROM sales_data s
JOIN customer_lookup c
    ON s.customer_key = c.customer_key
JOIN product_lookup p
    ON s.product_key = p.product_key
GROUP BY c.customer_key, c.first_name, c.last_name
ORDER BY lifetime_value DESC;


-- 10. Sales vs Returns Analysis

WITH sales AS (
    SELECT product_key, SUM(order_quantity) AS units_sold
    FROM sales_data
    GROUP BY product_key
),
returns AS (
    SELECT product_key, SUM(return_quantity) AS units_returned
    FROM returns_data
    GROUP BY product_key
)
SELECT
    p.product_name,
    COALESCE(s.units_sold, 0) AS units_sold,
    COALESCE(r.units_returned, 0) AS units_returned,
    ROUND(
        COALESCE(r.units_returned, 0)::NUMERIC / NULLIF(s.units_sold, 0) * 100, 2
    ) AS return_rate_percent
FROM product_lookup p
LEFT JOIN sales s
    ON p.product_key = s.product_key
LEFT JOIN returns r
    ON p.product_key = r.product_key
ORDER BY return_rate_percent DESC NULLS LAST;


-- 11. Monthly Growth Rate 
.
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', s.order_date) AS month,
        SUM(s.order_quantity * p.product_price) AS revenue
    FROM sales_data s
    JOIN product_lookup p
        ON s.product_key = p.product_key
    GROUP BY DATE_TRUNC('month', s.order_date)
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month))
        / LAG(revenue) OVER (ORDER BY month) * 100, 2
    ) AS growth_rate_percent
FROM monthly_revenue
ORDER BY month;


-- 12. Top 5 Products in Each Category

WITH ranked_products AS (
    SELECT
        cat.category_name,
        p.product_name,
        SUM(s.order_quantity * p.product_price) AS revenue,
        RANK() OVER (
            PARTITION BY cat.category_name
            ORDER BY SUM(s.order_quantity * p.product_price) DESC
        ) AS category_rank
    FROM sales_data s
    JOIN product_lookup p
        ON s.product_key = p.product_key
    JOIN product_subcategory_lookup sc
        ON p.product_subcategory_key = sc.product_subcategory_key
    JOIN product_category_lookup cat
        ON sc.product_category_key = cat.product_category_key
    GROUP BY cat.category_name, p.product_name
)
SELECT category_name, product_name, revenue, category_rank
FROM ranked_products
WHERE category_rank <= 5
ORDER BY category_name, category_rank;
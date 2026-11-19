/*
=============================================================================
E-Commerce Analytics Queries
=============================================================================
Collection of business intelligence queries for Power BI and analysis
=============================================================================
*/

USE ECommerceAnalytics;
GO

-- ============================================================================
-- SALES PERFORMANCE QUERIES
-- ============================================================================

-- 1. Sales Overview - Daily/Monthly/Yearly
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total) AS total_revenue,
    AVG(o.total) AS avg_order_value,
    SUM(o.subtotal) AS subtotal,
    SUM(o.shipping_cost) AS shipping_revenue,
    SUM(o.tax) AS tax_collected
FROM fact_orders o
JOIN dim_date d ON o.order_date_key = d.date_key
WHERE o.order_status NOT IN ('Cancelled', 'Returned')
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- 2. Sales by Product Category
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS orders,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.subtotal) AS revenue,
    SUM(oi.profit) AS profit,
    AVG(oi.unit_price) AS avg_price,
    SUM(oi.profit) / NULLIF(SUM(oi.subtotal), 0) * 100 AS profit_margin_pct
FROM fact_order_items oi
JOIN dim_products p ON oi.product_key = p.product_key
JOIN fact_orders o ON oi.order_key = o.order_key
WHERE o.order_status NOT IN ('Cancelled', 'Returned')
GROUP BY p.category
ORDER BY revenue DESC;

-- 3. Top 10 Products by Revenue
SELECT TOP 10
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    COUNT(oi.order_item_id) AS times_ordered,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.subtotal) AS total_revenue,
    SUM(oi.profit) AS total_profit,
    AVG(p.rating) AS avg_rating
FROM dim_products p
JOIN fact_order_items oi ON p.product_key = oi.product_key
JOIN fact_orders o ON oi.order_key = o.order_key
WHERE o.order_status NOT IN ('Cancelled', 'Returned')
GROUP BY p.product_id, p.product_name, p.category, p.brand
ORDER BY total_revenue DESC;

-- 4. Sales by Region
SELECT 
    o.region,
    COUNT(DISTINCT o.customer_key) AS unique_customers,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total) AS total_revenue,
    AVG(o.total) AS avg_order_value,
    SUM(o.total) / NULLIF(COUNT(DISTINCT o.customer_key), 0) AS revenue_per_customer
FROM fact_orders o
WHERE o.order_status NOT IN ('Cancelled', 'Returned')
GROUP BY o.region
ORDER BY total_revenue DESC;

-- 5. Monthly Sales Trend with Year-over-Year Comparison
WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month,
        d.month_name,
        SUM(o.total) AS revenue
    FROM fact_orders o
    JOIN dim_date d ON o.order_date_key = d.date_key
    WHERE o.order_status NOT IN ('Cancelled', 'Returned')
    GROUP BY d.year, d.month, d.month_name
)
SELECT 
    ms.month,
    ms.month_name,
    ms.year,
    ms.revenue AS current_year_revenue,
    LAG(ms.revenue, 12) OVER (ORDER BY ms.year, ms.month) AS previous_year_revenue,
    ms.revenue - LAG(ms.revenue, 12) OVER (ORDER BY ms.year, ms.month) AS yoy_change,
    CASE 
        WHEN LAG(ms.revenue, 12) OVER (ORDER BY ms.year, ms.month) > 0 
        THEN (ms.revenue - LAG(ms.revenue, 12) OVER (ORDER BY ms.year, ms.month)) 
             / LAG(ms.revenue, 12) OVER (ORDER BY ms.year, ms.month) * 100
        ELSE NULL 
    END AS yoy_change_pct
FROM monthly_sales ms
ORDER BY ms.year, ms.month;

-- ============================================================================
-- CUSTOMER ANALYTICS
-- ============================================================================

-- 6. Customer Segmentation by Purchase Behavior
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    AVG(c.lifetime_value) AS avg_lifetime_value,
    SUM(o.total) AS total_revenue,
    COUNT(o.order_id) AS total_orders,
    COUNT(o.order_id) * 1.0 / COUNT(DISTINCT c.customer_id) AS orders_per_customer,
    SUM(o.total) / NULLIF(COUNT(DISTINCT c.customer_id), 0) AS revenue_per_customer
FROM dim_customers c
LEFT JOIN fact_orders o ON c.customer_key = o.customer_key 
    AND o.order_status NOT IN ('Cancelled', 'Returned')
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;

-- 7. Customer Cohort Analysis (by Registration Month)
WITH cohorts AS (
    SELECT 
        c.customer_key,
        DATEFROMPARTS(YEAR(c.registration_date), MONTH(c.registration_date), 1) AS cohort_month,
        o.order_date
    FROM dim_customers c
    LEFT JOIN fact_orders o ON c.customer_key = o.customer_key
    WHERE o.order_status NOT IN ('Cancelled', 'Returned')
),
cohort_metrics AS (
    SELECT 
        cohort_month,
        DATEDIFF(MONTH, cohort_month, order_date) AS months_since_reg,
        COUNT(DISTINCT customer_key) AS active_customers
    FROM cohorts
    GROUP BY cohort_month, DATEDIFF(MONTH, cohort_month, order_date)
)
SELECT 
    cohort_month,
    months_since_reg,
    active_customers,
    FIRST_VALUE(active_customers) OVER (
        PARTITION BY cohort_month 
        ORDER BY months_since_reg
    ) AS cohort_size,
    active_customers * 100.0 / FIRST_VALUE(active_customers) OVER (
        PARTITION BY cohort_month 
        ORDER BY months_since_reg
    ) AS retention_rate
FROM cohort_metrics
ORDER BY cohort_month, months_since_reg;

-- 8. Top 20 Customers by Lifetime Value
SELECT TOP 20
    c.customer_id,
    c.first_name + ' ' + c.last_name AS customer_name,
    c.region,
    c.customer_segment,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total) AS lifetime_revenue,
    AVG(o.total) AS avg_order_value,
    MAX(o.order_date) AS last_order_date,
    DATEDIFF(DAY, MAX(o.order_date), GETDATE()) AS days_since_last_order
FROM dim_customers c
JOIN fact_orders o ON c.customer_key = o.customer_key
WHERE o.order_status NOT IN ('Cancelled', 'Returned')
GROUP BY c.customer_id, c.first_name, c.last_name, c.region, c.customer_segment
ORDER BY lifetime_revenue DESC;

-- 9. Customer Churn Risk Analysis
WITH customer_metrics AS (
    SELECT 
        c.customer_key,
        c.customer_id,
        c.first_name + ' ' + c.last_name AS customer_name,
        c.region,
        COUNT(o.order_id) AS total_orders,
        MAX(o.order_date) AS last_order_date,
        DATEDIFF(DAY, MAX(o.order_date), GETDATE()) AS days_since_last_order,
        SUM(o.total) AS lifetime_value
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_key = o.customer_key
    WHERE o.order_status NOT IN ('Cancelled', 'Returned')
    GROUP BY c.customer_key, c.customer_id, c.first_name, c.last_name, c.region
)
SELECT 
    customer_id,
    customer_name,
    region,
    total_orders,
    lifetime_value,
    last_order_date,
    days_since_last_order,
    CASE 
        WHEN days_since_last_order > 180 THEN 'High Risk'
        WHEN days_since_last_order > 90 THEN 'Medium Risk'
        WHEN days_since_last_order > 30 THEN 'Low Risk'
        ELSE 'Active'
    END AS churn_risk
FROM customer_metrics
WHERE days_since_last_order > 30
ORDER BY days_since_last_order DESC;

-- ============================================================================
-- PRODUCT & INVENTORY ANALYTICS
-- ============================================================================

-- 10. Inventory Status with Reorder Alerts
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.stock_quantity,
    p.reorder_level,
    CASE 
        WHEN p.stock_quantity = 0 THEN 'Out of Stock'
        WHEN p.stock_quantity <= p.reorder_level THEN 'Reorder Needed'
        WHEN p.stock_quantity <= p.reorder_level * 2 THEN 'Low Stock'
        ELSE 'Adequate Stock'
    END AS stock_status,
    p.price,
    p.cost,
    p.margin,
    p.rating
FROM dim_products p
ORDER BY 
    CASE 
        WHEN p.stock_quantity = 0 THEN 1
        WHEN p.stock_quantity <= p.reorder_level THEN 2
        ELSE 3
    END,
    p.stock_quantity;

-- 11. Product Performance Matrix (ABC Analysis)
WITH product_metrics AS (
    SELECT 
        p.product_key,
        p.product_id,
        p.product_name,
        p.category,
        SUM(oi.subtotal) AS total_revenue,
        SUM(oi.profit) AS total_profit,
        SUM(oi.quantity) AS units_sold,
        COUNT(DISTINCT oi.order_id) AS order_frequency
    FROM dim_products p
    JOIN fact_order_items oi ON p.product_key = oi.product_key
    JOIN fact_orders o ON oi.order_key = o.order_key
    WHERE o.order_status NOT IN ('Cancelled', 'Returned')
    GROUP BY p.product_key, p.product_id, p.product_name, p.category
),
ranked_products AS (
    SELECT 
        *,
        NTILE(3) OVER (ORDER BY total_revenue DESC) AS revenue_rank,
        NTILE(3) OVER (ORDER BY order_frequency DESC) AS frequency_rank
    FROM product_metrics
)
SELECT 
    product_id,
    product_name,
    category,
    total_revenue,
    total_profit,
    units_sold,
    order_frequency,
    CASE revenue_rank
        WHEN 1 THEN 'A - High Value'
        WHEN 2 THEN 'B - Medium Value'
        ELSE 'C - Low Value'
    END AS abc_classification
FROM ranked_products
ORDER BY total_revenue DESC;

-- 12. Product Reviews Summary
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    COUNT(r.review_id) AS review_count,
    AVG(CAST(r.rating AS FLOAT)) AS avg_rating,
    SUM(CASE WHEN r.rating = 5 THEN 1 ELSE 0 END) AS five_star,
    SUM(CASE WHEN r.rating = 4 THEN 1 ELSE 0 END) AS four_star,
    SUM(CASE WHEN r.rating = 3 THEN 1 ELSE 0 END) AS three_star,
    SUM(CASE WHEN r.rating = 2 THEN 1 ELSE 0 END) AS two_star,
    SUM(CASE WHEN r.rating = 1 THEN 1 ELSE 0 END) AS one_star,
    SUM(r.helpful_votes) AS total_helpful_votes
FROM dim_products p
LEFT JOIN customer_reviews r ON p.product_key = r.product_key
GROUP BY p.product_id, p.product_name, p.category
HAVING COUNT(r.review_id) > 0
ORDER BY avg_rating DESC, review_count DESC;

-- ============================================================================
-- WEB ANALYTICS
-- ============================================================================

-- 13. Traffic Sources Analysis
SELECT 
    wa.source,
    COUNT(wa.session_id) AS total_sessions,
    SUM(CASE WHEN wa.converted = 1 THEN 1 ELSE 0 END) AS conversions,
    SUM(CASE WHEN wa.converted = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(wa.session_id) AS conversion_rate,
    AVG(wa.pages_viewed) AS avg_pages_per_session,
    AVG(wa.session_duration_sec) AS avg_session_duration,
    SUM(CASE WHEN wa.bounce = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(wa.session_id) AS bounce_rate
FROM web_analytics wa
GROUP BY wa.source
ORDER BY total_sessions DESC;

-- 14. Device Type Performance
SELECT 
    wa.device_type,
    COUNT(wa.session_id) AS sessions,
    SUM(CASE WHEN wa.converted = 1 THEN 1 ELSE 0 END) AS conversions,
    SUM(CASE WHEN wa.converted = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(wa.session_id) AS conversion_rate,
    AVG(wa.session_duration_sec) AS avg_duration_sec
FROM web_analytics wa
GROUP BY wa.device_type
ORDER BY sessions DESC;

-- ============================================================================
-- KEY PERFORMANCE INDICATORS (KPIs)
-- ============================================================================

-- 15. Executive Dashboard KPIs
WITH kpis AS (
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.total) AS total_revenue,
        AVG(o.total) AS avg_order_value,
        COUNT(DISTINCT o.customer_key) AS unique_customers,
        SUM(oi.profit) AS total_profit,
        SUM(oi.profit) / NULLIF(SUM(oi.subtotal), 0) * 100 AS overall_margin_pct
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_key = oi.order_key
    WHERE o.order_status NOT IN ('Cancelled', 'Returned')
)
SELECT 
    FORMAT(total_revenue, 'C', 'en-US') AS [Total Revenue],
    total_orders AS [Total Orders],
    FORMAT(avg_order_value, 'C', 'en-US') AS [Avg Order Value],
    unique_customers AS [Unique Customers],
    FORMAT(total_profit, 'C', 'en-US') AS [Total Profit],
    FORMAT(overall_margin_pct, 'N2') + '%' AS [Profit Margin]
FROM kpis;

GO

PRINT 'Analytics queries ready for execution';

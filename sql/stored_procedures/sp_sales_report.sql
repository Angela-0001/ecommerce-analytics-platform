/*
=============================================================================
Stored Procedure: Sales Report Generator
=============================================================================
Purpose: Generate customizable sales reports with date filters
=============================================================================
*/

USE ECommerceAnalytics;
GO

CREATE OR ALTER PROCEDURE sp_sales_report
    @StartDate DATE = NULL,
    @EndDate DATE = NULL,
    @Region VARCHAR(50) = NULL,
    @Category VARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Set default dates if not provided
    IF @StartDate IS NULL
        SET @StartDate = DATEADD(MONTH, -3, GETDATE());
    
    IF @EndDate IS NULL
        SET @EndDate = GETDATE();
    
    -- Main sales report
    SELECT 
        d.date,
        d.day_name,
        d.month_name,
        d.year,
        o.order_id,
        c.customer_id,
        c.first_name + ' ' + c.last_name AS customer_name,
        c.region,
        o.order_status,
        p.product_name,
        p.category,
        p.brand,
        oi.quantity,
        oi.unit_price,
        oi.discount_percent,
        oi.subtotal,
        oi.profit,
        o.total AS order_total,
        o.payment_method,
        o.shipping_method
    FROM fact_orders o
    JOIN dim_date d ON o.order_date_key = d.date_key
    JOIN dim_customers c ON o.customer_key = c.customer_key
    JOIN fact_order_items oi ON o.order_key = oi.order_key
    JOIN dim_products p ON oi.product_key = p.product_key
    WHERE 
        d.date BETWEEN @StartDate AND @EndDate
        AND (@Region IS NULL OR c.region = @Region)
        AND (@Category IS NULL OR p.category = @Category)
        AND o.order_status NOT IN ('Cancelled', 'Returned')
    ORDER BY d.date DESC, o.order_id;
    
    -- Summary statistics
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.total) AS total_revenue,
        AVG(o.total) AS avg_order_value,
        COUNT(DISTINCT o.customer_key) AS unique_customers,
        SUM(oi.profit) AS total_profit,
        SUM(oi.profit) / NULLIF(SUM(oi.subtotal), 0) * 100 AS profit_margin_pct
    FROM fact_orders o
    JOIN dim_date d ON o.order_date_key = d.date_key
    JOIN dim_customers c ON o.customer_key = c.customer_key
    JOIN fact_order_items oi ON o.order_key = oi.order_key
    JOIN dim_products p ON oi.product_key = p.product_key
    WHERE 
        d.date BETWEEN @StartDate AND @EndDate
        AND (@Region IS NULL OR c.region = @Region)
        AND (@Category IS NULL OR p.category = @Category)
        AND o.order_status NOT IN ('Cancelled', 'Returned');
END;
GO

PRINT 'Stored procedure sp_sales_report created';

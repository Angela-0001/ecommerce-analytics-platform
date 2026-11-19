/*
=============================================================================
E-Commerce Analytics Database Schema
=============================================================================
Author: Data Analytics Team
Purpose: Star schema design for e-commerce sales analytics
Database: SQL Server / PostgreSQL compatible
=============================================================================
*/

-- Create Database (SQL Server syntax)
-- For PostgreSQL, create database via psql or pgAdmin
CREATE DATABASE ECommerceAnalytics;
GO

USE ECommerceAnalytics;
GO

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- Dimension: Customers
-- Contains all customer information for analysis
CREATE TABLE dim_customers (
    customer_key INT IDENTITY(1,1) PRIMARY KEY,
    customer_id VARCHAR(10) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'USA',
    region VARCHAR(50),
    registration_date DATE NOT NULL,
    customer_segment VARCHAR(20),
    lifetime_value DECIMAL(10,2),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_customers_id ON dim_customers(customer_id);
CREATE INDEX idx_customers_segment ON dim_customers(customer_segment);
CREATE INDEX idx_customers_region ON dim_customers(region);

-- Dimension: Products
-- Product catalog with pricing and inventory
CREATE TABLE dim_products (
    product_key INT IDENTITY(1,1) PRIMARY KEY,
    product_id VARCHAR(10) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    margin AS (price - cost) PERSISTED,
    margin_percent AS (CASE WHEN price > 0 THEN ((price - cost) / price) * 100 ELSE 0 END) PERSISTED,
    stock_quantity INT DEFAULT 0,
    reorder_level INT DEFAULT 10,
    supplier VARCHAR(255),
    weight_kg DECIMAL(8,2),
    rating DECIMAL(2,1),
    review_count INT DEFAULT 0,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_products_id ON dim_products(product_id);
CREATE INDEX idx_products_category ON dim_products(category);
CREATE INDEX idx_products_brand ON dim_products(brand);

-- Dimension: Date
-- Date dimension for time-based analysis
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    day_of_week TINYINT NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    day_of_month TINYINT NOT NULL,
    day_of_year SMALLINT NOT NULL,
    week_of_year TINYINT NOT NULL,
    month TINYINT NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    quarter TINYINT NOT NULL,
    year SMALLINT NOT NULL,
    is_weekend BIT NOT NULL,
    is_holiday BIT DEFAULT 0,
    holiday_name VARCHAR(50),
    fiscal_year SMALLINT,
    fiscal_quarter TINYINT
);

CREATE INDEX idx_date_date ON dim_date(date);
CREATE INDEX idx_date_year_month ON dim_date(year, month);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- Fact: Orders (Grain: One row per order)
CREATE TABLE fact_orders (
    order_key INT IDENTITY(1,1) PRIMARY KEY,
    order_id VARCHAR(15) UNIQUE NOT NULL,
    customer_key INT NOT NULL,
    order_date_key INT NOT NULL,
    order_date DATETIME NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    payment_method VARCHAR(50),
    shipping_address VARCHAR(500),
    shipping_method VARCHAR(50),
    region VARCHAR(50),
    subtotal DECIMAL(10,2) NOT NULL,
    shipping_cost DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_key) 
        REFERENCES dim_customers(customer_key),
    CONSTRAINT fk_orders_date FOREIGN KEY (order_date_key) 
        REFERENCES dim_date(date_key)
);

CREATE INDEX idx_orders_id ON fact_orders(order_id);
CREATE INDEX idx_orders_customer ON fact_orders(customer_key);
CREATE INDEX idx_orders_date ON fact_orders(order_date_key);
CREATE INDEX idx_orders_status ON fact_orders(order_status);

-- Fact: Order Items (Grain: One row per product per order)
CREATE TABLE fact_order_items (
    order_item_key INT IDENTITY(1,1) PRIMARY KEY,
    order_item_id VARCHAR(15) UNIQUE NOT NULL,
    order_key INT NOT NULL,
    order_id VARCHAR(15) NOT NULL,
    product_key INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    subtotal DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    profit AS (subtotal - (cost * quantity)) PERSISTED,
    created_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_key) 
        REFERENCES fact_orders(order_key),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_key) 
        REFERENCES dim_products(product_key)
);

CREATE INDEX idx_order_items_order ON fact_order_items(order_key);
CREATE INDEX idx_order_items_product ON fact_order_items(product_key);

-- ============================================================================
-- SUPPORTING TABLES
-- ============================================================================

-- Customer Reviews
CREATE TABLE customer_reviews (
    review_key INT IDENTITY(1,1) PRIMARY KEY,
    review_id VARCHAR(10) UNIQUE NOT NULL,
    order_id VARCHAR(15) NOT NULL,
    product_key INT NOT NULL,
    customer_key INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_title VARCHAR(255),
    review_text TEXT,
    review_date DATE NOT NULL,
    verified_purchase BIT DEFAULT 1,
    helpful_votes INT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_key) 
        REFERENCES dim_products(product_key),
    CONSTRAINT fk_reviews_customer FOREIGN KEY (customer_key) 
        REFERENCES dim_customers(customer_key)
);

CREATE INDEX idx_reviews_product ON customer_reviews(product_key);
CREATE INDEX idx_reviews_rating ON customer_reviews(rating);

-- Web Analytics
CREATE TABLE web_analytics (
    session_key INT IDENTITY(1,1) PRIMARY KEY,
    session_id VARCHAR(15) UNIQUE NOT NULL,
    customer_key INT,
    session_date DATETIME NOT NULL,
    session_date_key INT NOT NULL,
    device_type VARCHAR(20),
    browser VARCHAR(50),
    pages_viewed INT DEFAULT 0,
    session_duration_sec INT DEFAULT 0,
    bounce BIT DEFAULT 0,
    converted BIT DEFAULT 0,
    source VARCHAR(50),
    created_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT fk_web_customer FOREIGN KEY (customer_key) 
        REFERENCES dim_customers(customer_key),
    CONSTRAINT fk_web_date FOREIGN KEY (session_date_key) 
        REFERENCES dim_date(date_key)
);

CREATE INDEX idx_web_customer ON web_analytics(customer_key);
CREATE INDEX idx_web_date ON web_analytics(session_date_key);
CREATE INDEX idx_web_source ON web_analytics(source);

-- ============================================================================
-- AUDIT TABLE
-- ============================================================================

CREATE TABLE etl_audit_log (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    etl_process VARCHAR(100) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    rows_inserted INT DEFAULT 0,
    rows_updated INT DEFAULT 0,
    rows_failed INT DEFAULT 0,
    status VARCHAR(20),
    error_message TEXT,
    created_at DATETIME DEFAULT GETDATE()
);

-- ============================================================================
-- SUMMARY VIEWS
-- ============================================================================

GO

PRINT 'Database schema created successfully';
PRINT 'Tables created: 9';
PRINT 'Ready for ETL process';

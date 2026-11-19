"""
ETL Pipeline: Load CSV data into SQL Database
Handles data transformation and loading to star schema
"""

import pandas as pd
import pyodbc
from sqlalchemy import create_engine
import os
from datetime import datetime
import sys

# Configuration
DATA_DIR = '../data/sample/'
CONNECTION_STRING = (
    'Driver={SQL Server};'
    'Server=localhost;'
    'Database=ECommerceAnalytics;'
    'Trusted_Connection=yes;'
)

def log_etl_start(cursor, process_name):
    """Log ETL process start"""
    cursor.execute("""
        INSERT INTO etl_audit_log (etl_process, start_time, status)
        VALUES (?, GETDATE(), 'Running')
    """, process_name)
    cursor.commit()
    cursor.execute("SELECT SCOPE_IDENTITY()")
    return cursor.fetchone()[0]

def log_etl_end(cursor, log_id, rows_inserted, status='Success', error=None):
    """Log ETL process completion"""
    cursor.execute("""
        UPDATE etl_audit_log 
        SET end_time = GETDATE(), 
            rows_inserted = ?, 
            status = ?,
            error_message = ?
        WHERE log_id = ?
    """, rows_inserted, status, error, log_id)
    cursor.commit()

def load_customers(cursor, df_customers):
    """Load customers into dimension table"""
    print("\n1. Loading Customers...")
    log_id = log_etl_start(cursor, 'Load Customers')
    
    rows_inserted = 0
    try:
        for _, row in df_customers.iterrows():
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM dim_customers WHERE customer_id = ?)
                BEGIN
                    INSERT INTO dim_customers (
                        customer_id, first_name, last_name, email, phone,
                        address, city, state, zip_code, country, region,
                        registration_date, customer_segment, lifetime_value
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                END
            """, 
                row['customer_id'],
                row['customer_id'], row['first_name'], row['last_name'], 
                row['email'], row['phone'], row['address'], row['city'],
                row['state'], row['zip_code'], row['country'], row['region'],
                row['registration_date'], row['customer_segment'], 
                row['lifetime_value']
            )
            rows_inserted += cursor.rowcount
        
        cursor.commit()
        log_etl_end(cursor, log_id, rows_inserted)
        print(f"   ✓ Loaded {rows_inserted} customers")
        return rows_inserted
    
    except Exception as e:
        cursor.rollback()
        log_etl_end(cursor, log_id, 0, 'Failed', str(e))
        print(f"   ✗ Error loading customers: {e}")
        return 0

def load_products(cursor, df_products):
    """Load products into dimension table"""
    print("\n2. Loading Products...")
    log_id = log_etl_start(cursor, 'Load Products')
    
    rows_inserted = 0
    try:
        for _, row in df_products.iterrows():
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM dim_products WHERE product_id = ?)
                BEGIN
                    INSERT INTO dim_products (
                        product_id, product_name, category, subcategory, brand,
                        price, cost, stock_quantity, reorder_level, supplier,
                        weight_kg, rating, review_count
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                END
            """,
                row['product_id'],
                row['product_id'], row['product_name'], row['category'],
                row['subcategory'], row['brand'], row['price'], row['cost'],
                row['stock_quantity'], row['reorder_level'], row['supplier'],
                row['weight_kg'], row['rating'], row['review_count']
            )
            rows_inserted += cursor.rowcount
        
        cursor.commit()
        log_etl_end(cursor, log_id, rows_inserted)
        print(f"   ✓ Loaded {rows_inserted} products")
        return rows_inserted
    
    except Exception as e:
        cursor.rollback()
        log_etl_end(cursor, log_id, 0, 'Failed', str(e))
        print(f"   ✗ Error loading products: {e}")
        return 0

def load_orders(cursor, df_orders):
    """Load orders into fact table"""
    print("\n3. Loading Orders...")
    log_id = log_etl_start(cursor, 'Load Orders')
    
    rows_inserted = 0
    try:
        for _, row in df_orders.iterrows():
            # Get customer key
            cursor.execute("SELECT customer_key FROM dim_customers WHERE customer_id = ?", 
                         row['customer_id'])
            customer_key = cursor.fetchone()[0]
            
            # Get date key
            order_date = pd.to_datetime(row['order_date'])
            date_key = int(order_date.strftime('%Y%m%d'))
            
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM fact_orders WHERE order_id = ?)
                BEGIN
                    INSERT INTO fact_orders (
                        order_id, customer_key, order_date_key, order_date,
                        order_status, payment_method, shipping_address, 
                        shipping_method, region, subtotal, shipping_cost, tax, total
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                END
            """,
                row['order_id'],
                row['order_id'], customer_key, date_key, order_date,
                row['order_status'], row['payment_method'], row['shipping_address'],
                row['shipping_method'], row['region'], row['subtotal'],
                row['shipping_cost'], row['tax'], row['total']
            )
            rows_inserted += cursor.rowcount
        
        cursor.commit()
        log_etl_end(cursor, log_id, rows_inserted)
        print(f"   ✓ Loaded {rows_inserted} orders")
        return rows_inserted
    
    except Exception as e:
        cursor.rollback()
        log_etl_end(cursor, log_id, 0, 'Failed', str(e))
        print(f"   ✗ Error loading orders: {e}")
        return 0

def load_order_items(cursor, df_order_items, df_products):
    """Load order items into fact table"""
    print("\n4. Loading Order Items...")
    log_id = log_etl_start(cursor, 'Load Order Items')
    
    rows_inserted = 0
    try:
        for _, row in df_order_items.iterrows():
            # Get order key
            cursor.execute("SELECT order_key FROM fact_orders WHERE order_id = ?", 
                         row['order_id'])
            result = cursor.fetchone()
            if not result:
                continue
            order_key = result[0]
            
            # Get product key and cost
            cursor.execute("""
                SELECT product_key, cost FROM dim_products WHERE product_id = ?
            """, row['product_id'])
            result = cursor.fetchone()
            if not result:
                continue
            product_key, cost = result
            
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM fact_order_items WHERE order_item_id = ?)
                BEGIN
                    INSERT INTO fact_order_items (
                        order_item_id, order_key, order_id, product_key,
                        quantity, unit_price, discount_percent, subtotal, cost
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                END
            """,
                row['order_item_id'],
                row['order_item_id'], order_key, row['order_id'], product_key,
                row['quantity'], row['unit_price'], row['discount_percent'],
                row['subtotal'], cost
            )
            rows_inserted += cursor.rowcount
        
        cursor.commit()
        log_etl_end(cursor, log_id, rows_inserted)
        print(f"   ✓ Loaded {rows_inserted} order items")
        return rows_inserted
    
    except Exception as e:
        cursor.rollback()
        log_etl_end(cursor, log_id, 0, 'Failed', str(e))
        print(f"   ✗ Error loading order items: {e}")
        return 0

def load_reviews(cursor, df_reviews):
    """Load customer reviews"""
    print("\n5. Loading Reviews...")
    log_id = log_etl_start(cursor, 'Load Reviews')
    
    rows_inserted = 0
    try:
        for _, row in df_reviews.iterrows():
            # Get keys
            cursor.execute("SELECT customer_key FROM dim_customers WHERE customer_id = ?", 
                         row['customer_id'])
            result = cursor.fetchone()
            if not result:
                continue
            customer_key = result[0]
            
            cursor.execute("SELECT product_key FROM dim_products WHERE product_id = ?", 
                         row['product_id'])
            result = cursor.fetchone()
            if not result:
                continue
            product_key = result[0]
            
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM customer_reviews WHERE review_id = ?)
                BEGIN
                    INSERT INTO customer_reviews (
                        review_id, order_id, product_key, customer_key,
                        rating, review_title, review_text, review_date,
                        verified_purchase, helpful_votes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                END
            """,
                row['review_id'],
                row['review_id'], row['order_id'], product_key, customer_key,
                row['rating'], row['review_title'], row['review_text'],
                row['review_date'], row['verified_purchase'], row['helpful_votes']
            )
            rows_inserted += cursor.rowcount
        
        cursor.commit()
        log_etl_end(cursor, log_id, rows_inserted)
        print(f"   ✓ Loaded {rows_inserted} reviews")
        return rows_inserted
    
    except Exception as e:
        cursor.rollback()
        log_etl_end(cursor, log_id, 0, 'Failed', str(e))
        print(f"   ✗ Error loading reviews: {e}")
        return 0

def load_web_analytics(cursor, df_web):
    """Load web analytics data"""
    print("\n6. Loading Web Analytics...")
    log_id = log_etl_start(cursor, 'Load Web Analytics')
    
    rows_inserted = 0
    try:
        for _, row in df_web.iterrows():
            # Get customer key (can be NULL for anonymous sessions)
            customer_key = None
            if pd.notna(row['customer_id']):
                cursor.execute("SELECT customer_key FROM dim_customers WHERE customer_id = ?", 
                             row['customer_id'])
                result = cursor.fetchone()
                if result:
                    customer_key = result[0]
            
            # Get date key
            session_date = pd.to_datetime(row['session_date'])
            date_key = int(session_date.strftime('%Y%m%d'))
            
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM web_analytics WHERE session_id = ?)
                BEGIN
                    INSERT INTO web_analytics (
                        session_id, customer_key, session_date, session_date_key,
                        device_type, browser, pages_viewed, session_duration_sec,
                        bounce, converted, source
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                END
            """,
                row['session_id'],
                row['session_id'], customer_key, session_date, date_key,
                row['device_type'], row['browser'], row['pages_viewed'],
                row['session_duration_sec'], row['bounce'], row['converted'],
                row['source']
            )
            rows_inserted += cursor.rowcount
        
        cursor.commit()
        log_etl_end(cursor, log_id, rows_inserted)
        print(f"   ✓ Loaded {rows_inserted} web sessions")
        return rows_inserted
    
    except Exception as e:
        cursor.rollback()
        log_etl_end(cursor, log_id, 0, 'Failed', str(e))
        print(f"   ✗ Error loading web analytics: {e}")
        return 0

def main():
    """Main ETL execution"""
    print("=" * 60)
    print("E-COMMERCE ETL PIPELINE")
    print("=" * 60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load CSV files
    print("\nLoading CSV files...")
    try:
        df_customers = pd.read_csv(DATA_DIR + 'customers.csv')
        df_products = pd.read_csv(DATA_DIR + 'products.csv')
        df_orders = pd.read_csv(DATA_DIR + 'orders.csv')
        df_order_items = pd.read_csv(DATA_DIR + 'order_items.csv')
        df_reviews = pd.read_csv(DATA_DIR + 'reviews.csv')
        df_web = pd.read_csv(DATA_DIR + 'web_analytics.csv')
        print("   ✓ All CSV files loaded")
    except Exception as e:
        print(f"   ✗ Error loading CSV files: {e}")
        sys.exit(1)
    
    # Connect to database
    print("\nConnecting to database...")
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        print("   ✓ Database connection established")
    except Exception as e:
        print(f"   ✗ Database connection failed: {e}")
        print("\nPlease ensure:")
        print("   1. SQL Server is running")
        print("   2. Database 'ECommerceAnalytics' exists")
        print("   3. Schema has been created (run 01_create_database.sql)")
        sys.exit(1)
    
    # Execute ETL
    total_rows = 0
    total_rows += load_customers(cursor, df_customers)
    total_rows += load_products(cursor, df_products)
    total_rows += load_orders(cursor, df_orders)
    total_rows += load_order_items(cursor, df_order_items, df_products)
    total_rows += load_reviews(cursor, df_reviews)
    total_rows += load_web_analytics(cursor, df_web)
    
    # Close connection
    cursor.close()
    conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("ETL PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Total Rows Loaded: {total_rows:,}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("✓ ETL Pipeline completed successfully")
    print("=" * 60)

if __name__ == '__main__':
    main()

"""
Data Cleaning and Validation Pipeline
Handles missing values, duplicates, outliers, and data quality issues
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

print("=" * 70)
print("DATA CLEANING & VALIDATION PIPELINE")
print("=" * 70)

# Configuration
INPUT_DIR = '../data/sample/'
OUTPUT_DIR = '../data/processed/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# 1. LOAD RAW DATA
# ============================================================================
print("\n1. Loading raw data files...")

try:
    df_customers = pd.read_csv(INPUT_DIR + 'customers.csv')
    df_products = pd.read_csv(INPUT_DIR + 'products.csv')
    df_orders = pd.read_csv(INPUT_DIR + 'orders.csv')
    df_order_items = pd.read_csv(INPUT_DIR + 'order_items.csv')
    df_reviews = pd.read_csv(INPUT_DIR + 'reviews.csv')
    df_web = pd.read_csv(INPUT_DIR + 'web_analytics.csv')
    print("   ✓ All files loaded successfully")
except Exception as e:
    print(f"   ✗ Error loading files: {e}")
    exit(1)

# ============================================================================
# 2. DATA QUALITY ASSESSMENT
# ============================================================================
print("\n2. Assessing Data Quality...")

def assess_quality(df, name):
    """Generate data quality report"""
    print(f"\n   {name}:")
    print(f"   - Total Rows: {len(df):,}")
    print(f"   - Total Columns: {len(df.columns)}")
    print(f"   - Missing Values: {df.isnull().sum().sum()}")
    print(f"   - Duplicate Rows: {df.duplicated().sum()}")
    print(f"   - Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

assess_quality(df_customers, "CUSTOMERS")
assess_quality(df_products, "PRODUCTS")
assess_quality(df_orders, "ORDERS")
assess_quality(df_order_items, "ORDER ITEMS")
assess_quality(df_reviews, "REVIEWS")
assess_quality(df_web, "WEB ANALYTICS")

# ============================================================================
# 3. CLEAN CUSTOMERS DATA
# ============================================================================
print("\n3. Cleaning Customers Data...")

# Remove duplicates
df_customers_clean = df_customers.drop_duplicates(subset=['customer_id'])
print(f"   ✓ Removed {len(df_customers) - len(df_customers_clean)} duplicate customers")

# Standardize email (lowercase)
df_customers_clean['email'] = df_customers_clean['email'].str.lower().str.strip()

# Validate email format
invalid_emails = ~df_customers_clean['email'].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False, regex=True)
print(f"   ✓ Found {invalid_emails.sum()} invalid email addresses")
df_customers_clean = df_customers_clean[~invalid_emails]

# Clean phone numbers (remove non-numeric)
df_customers_clean['phone'] = df_customers_clean['phone'].str.replace(r'[^\d]', '', regex=True)

# Handle missing values
df_customers_clean['phone'].fillna('', inplace=True)
df_customers_clean['address'].fillna('Unknown', inplace=True)

# Standardize state codes (uppercase)
df_customers_clean['state'] = df_customers_clean['state'].str.upper()

# Convert dates
df_customers_clean['registration_date'] = pd.to_datetime(df_customers_clean['registration_date'])

print(f"   ✓ Cleaned customers: {len(df_customers_clean)} records")

# ============================================================================
# 4. CLEAN PRODUCTS DATA
# ============================================================================
print("\n4. Cleaning Products Data...")

df_products_clean = df_products.drop_duplicates(subset=['product_id'])

# Remove products with invalid prices
df_products_clean = df_products_clean[
    (df_products_clean['price'] > 0) & 
    (df_products_clean['cost'] > 0) &
    (df_products_clean['price'] >= df_products_clean['cost'])
]

# Handle negative stock
df_products_clean.loc[df_products_clean['stock_quantity'] < 0, 'stock_quantity'] = 0

# Clean ratings (must be between 0-5)
df_products_clean = df_products_clean[
    (df_products_clean['rating'] >= 0) & 
    (df_products_clean['rating'] <= 5)
]

# Fill missing categories
df_products_clean['category'].fillna('Uncategorized', inplace=True)
df_products_clean['brand'].fillna('Generic', inplace=True)

# Calculate profit margin
df_products_clean['profit_margin'] = (
    (df_products_clean['price'] - df_products_clean['cost']) / 
    df_products_clean['price'] * 100
).round(2)

print(f"   ✓ Cleaned products: {len(df_products_clean)} records")

# ============================================================================
# 5. CLEAN ORDERS DATA
# ============================================================================
print("\n5. Cleaning Orders Data...")

df_orders_clean = df_orders.drop_duplicates(subset=['order_id'])

# Convert dates
df_orders_clean['order_date'] = pd.to_datetime(df_orders_clean['order_date'])

# Remove orders with invalid totals
df_orders_clean = df_orders_clean[df_orders_clean['total'] > 0]

# Validate total calculation
df_orders_clean['calculated_total'] = (
    df_orders_clean['subtotal'] + 
    df_orders_clean['shipping_cost'] + 
    df_orders_clean['tax']
).round(2)

# Flag inconsistent totals
tolerance = 0.05  # 5 cents tolerance
df_orders_clean['total_mismatch'] = (
    abs(df_orders_clean['total'] - df_orders_clean['calculated_total']) > tolerance
)

inconsistent_orders = df_orders_clean['total_mismatch'].sum()
print(f"   ⚠ Found {inconsistent_orders} orders with total calculation mismatches")

# Fix the totals
df_orders_clean['total'] = df_orders_clean['calculated_total']
df_orders_clean.drop(['calculated_total', 'total_mismatch'], axis=1, inplace=True)

# Standardize status values
valid_statuses = ['Processing', 'Shipped', 'Delivered', 'Cancelled', 'Returned']
df_orders_clean['order_status'] = df_orders_clean['order_status'].str.title()
df_orders_clean = df_orders_clean[df_orders_clean['order_status'].isin(valid_statuses)]

print(f"   ✓ Cleaned orders: {len(df_orders_clean)} records")

# ============================================================================
# 6. CLEAN ORDER ITEMS DATA
# ============================================================================
print("\n6. Cleaning Order Items Data...")

df_order_items_clean = df_order_items.drop_duplicates(subset=['order_item_id'])

# Remove items with invalid quantities or prices
df_order_items_clean = df_order_items_clean[
    (df_order_items_clean['quantity'] > 0) &
    (df_order_items_clean['unit_price'] > 0)
]

# Validate subtotal calculation
df_order_items_clean['calculated_subtotal'] = (
    df_order_items_clean['quantity'] * 
    df_order_items_clean['unit_price'] * 
    (1 - df_order_items_clean['discount_percent'] / 100)
).round(2)

# Fix subtotals
df_order_items_clean['subtotal'] = df_order_items_clean['calculated_subtotal']
df_order_items_clean.drop('calculated_subtotal', axis=1, inplace=True)

# Remove orphaned items (orders/products that don't exist)
df_order_items_clean = df_order_items_clean[
    df_order_items_clean['order_id'].isin(df_orders_clean['order_id']) &
    df_order_items_clean['product_id'].isin(df_products_clean['product_id'])
]

print(f"   ✓ Cleaned order items: {len(df_order_items_clean)} records")

# ============================================================================
# 7. CLEAN REVIEWS DATA
# ============================================================================
print("\n7. Cleaning Reviews Data...")

df_reviews_clean = df_reviews.drop_duplicates(subset=['review_id'])

# Validate ratings (1-5)
df_reviews_clean = df_reviews_clean[
    (df_reviews_clean['rating'] >= 1) & 
    (df_reviews_clean['rating'] <= 5)
]

# Remove reviews for non-existent products/customers/orders
df_reviews_clean = df_reviews_clean[
    df_reviews_clean['order_id'].isin(df_orders_clean['order_id']) &
    df_reviews_clean['product_id'].isin(df_products_clean['product_id']) &
    df_reviews_clean['customer_id'].isin(df_customers_clean['customer_id'])
]

# Convert dates
df_reviews_clean['review_date'] = pd.to_datetime(df_reviews_clean['review_date'])

# Clean text (remove excessive whitespace)
df_reviews_clean['review_text'] = df_reviews_clean['review_text'].str.strip()
df_reviews_clean['review_title'] = df_reviews_clean['review_title'].str.strip()

print(f"   ✓ Cleaned reviews: {len(df_reviews_clean)} records")

# ============================================================================
# 8. CLEAN WEB ANALYTICS DATA
# ============================================================================
print("\n8. Cleaning Web Analytics Data...")

df_web_clean = df_web.drop_duplicates(subset=['session_id'])

# Convert dates
df_web_clean['session_date'] = pd.to_datetime(df_web_clean['session_date'])

# Validate numeric fields
df_web_clean = df_web_clean[
    (df_web_clean['pages_viewed'] >= 0) &
    (df_web_clean['session_duration_sec'] >= 0)
]

# Standardize device types
df_web_clean['device_type'] = df_web_clean['device_type'].str.title()

# Handle missing customer_id (anonymous sessions are OK)
# Just ensure valid customer_ids reference existing customers
df_web_clean.loc[
    ~df_web_clean['customer_id'].isin(df_customers_clean['customer_id']) & 
    df_web_clean['customer_id'].notna(),
    'customer_id'
] = np.nan

print(f"   ✓ Cleaned web analytics: {len(df_web_clean)} records")

# ============================================================================
# 9. OUTLIER DETECTION & HANDLING
# ============================================================================
print("\n9. Detecting and Handling Outliers...")

def detect_outliers_iqr(df, column):
    """Detect outliers using IQR method"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR
    outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
    return outliers, lower_bound, upper_bound

# Detect outliers in order totals
outliers_orders, lower, upper = detect_outliers_iqr(df_orders_clean, 'total')
print(f"   ⚠ Found {outliers_orders.sum()} outlier orders (total < ${lower:.2f} or > ${upper:.2f})")
print(f"   ℹ Keeping outliers as they may be legitimate large/small orders")

# Detect outliers in product prices
outliers_prices, lower, upper = detect_outliers_iqr(df_products_clean, 'price')
print(f"   ⚠ Found {outliers_prices.sum()} outlier product prices")

# ============================================================================
# 10. CREATE DERIVED FEATURES
# ============================================================================
print("\n10. Creating Derived Features...")

# Customer features
df_customers_clean['account_age_days'] = (
    pd.Timestamp.now() - df_customers_clean['registration_date']
).dt.days

# Order features
df_orders_clean['order_year'] = df_orders_clean['order_date'].dt.year
df_orders_clean['order_month'] = df_orders_clean['order_date'].dt.month
df_orders_clean['order_day_of_week'] = df_orders_clean['order_date'].dt.day_name()
df_orders_clean['order_hour'] = df_orders_clean['order_date'].dt.hour

# Product features
df_products_clean['is_low_stock'] = df_products_clean['stock_quantity'] <= df_products_clean['reorder_level']
df_products_clean['is_out_of_stock'] = df_products_clean['stock_quantity'] == 0

print("   ✓ Derived features created")

# ============================================================================
# 11. SAVE CLEANED DATA
# ============================================================================
print("\n11. Saving cleaned datasets...")

df_customers_clean.to_csv(OUTPUT_DIR + 'customers_cleaned.csv', index=False)
df_products_clean.to_csv(OUTPUT_DIR + 'products_cleaned.csv', index=False)
df_orders_clean.to_csv(OUTPUT_DIR + 'orders_cleaned.csv', index=False)
df_order_items_clean.to_csv(OUTPUT_DIR + 'order_items_cleaned.csv', index=False)
df_reviews_clean.to_csv(OUTPUT_DIR + 'reviews_cleaned.csv', index=False)
df_web_clean.to_csv(OUTPUT_DIR + 'web_analytics_cleaned.csv', index=False)

print("   ✓ All cleaned files saved to", OUTPUT_DIR)

# ============================================================================
# 12. DATA QUALITY REPORT
# ============================================================================
print("\n" + "=" * 70)
print("DATA CLEANING SUMMARY REPORT")
print("=" * 70)

summary = {
    'Dataset': ['Customers', 'Products', 'Orders', 'Order Items', 'Reviews', 'Web Analytics'],
    'Original': [len(df_customers), len(df_products), len(df_orders), 
                len(df_order_items), len(df_reviews), len(df_web)],
    'Cleaned': [len(df_customers_clean), len(df_products_clean), len(df_orders_clean),
               len(df_order_items_clean), len(df_reviews_clean), len(df_web_clean)],
    'Removed': [
        len(df_customers) - len(df_customers_clean),
        len(df_products) - len(df_products_clean),
        len(df_orders) - len(df_orders_clean),
        len(df_order_items) - len(df_order_items_clean),
        len(df_reviews) - len(df_reviews_clean),
        len(df_web) - len(df_web_clean)
    ]
}

df_summary = pd.DataFrame(summary)
df_summary['Removal %'] = (df_summary['Removed'] / df_summary['Original'] * 100).round(2)

print("\n", df_summary.to_string(index=False))

print("\n" + "=" * 70)
print("✓ DATA CLEANING COMPLETE")
print("=" * 70)

# Export summary report
df_summary.to_csv(OUTPUT_DIR + 'cleaning_report.csv', index=False)
print(f"\nCleaning report saved to: {OUTPUT_DIR}cleaning_report.csv")

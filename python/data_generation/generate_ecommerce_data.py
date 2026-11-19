"""
E-Commerce Data Generator
Generates realistic e-commerce transaction data for analytics
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Configuration
NUM_CUSTOMERS = 5000
NUM_PRODUCTS = 200
NUM_ORDERS = 15000
DATE_START = datetime(2022, 1, 1)
DATE_END = datetime(2024, 12, 31)

# Product Categories
CATEGORIES = [
    'Electronics', 'Clothing', 'Home & Kitchen', 'Books', 
    'Sports & Outdoors', 'Beauty & Personal Care', 'Toys & Games',
    'Automotive', 'Health & Wellness', 'Office Supplies'
]

# Regions
REGIONS = ['North', 'South', 'East', 'West', 'Central']

print("Generating E-Commerce Dataset...")
print("=" * 60)

# ==================== CUSTOMERS ====================
print("\n1. Generating Customers...")

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    customer = {
        'customer_id': f'C{i:05d}',
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'zip_code': fake.zipcode(),
        'country': 'USA',
        'region': random.choice(REGIONS),
        'registration_date': fake.date_between(start_date=DATE_START, end_date=DATE_END),
        'customer_segment': random.choices(
            ['VIP', 'Regular', 'Occasional'], 
            weights=[0.1, 0.6, 0.3]
        )[0],
        'lifetime_value': round(random.uniform(50, 5000), 2)
    }
    customers.append(customer)

df_customers = pd.DataFrame(customers)
print(f"   ✓ Created {len(df_customers)} customers")

# ==================== PRODUCTS ====================
print("\n2. Generating Products...")

products = []
for i in range(1, NUM_PRODUCTS + 1):
    category = random.choice(CATEGORIES)
    base_price = random.uniform(10, 500)
    
    product = {
        'product_id': f'P{i:05d}',
        'product_name': fake.catch_phrase(),
        'category': category,
        'subcategory': f'{category} - {random.choice(["Premium", "Standard", "Budget"])}',
        'brand': fake.company(),
        'price': round(base_price, 2),
        'cost': round(base_price * random.uniform(0.4, 0.7), 2),
        'stock_quantity': random.randint(0, 500),
        'reorder_level': random.randint(10, 50),
        'supplier': fake.company(),
        'weight_kg': round(random.uniform(0.1, 10), 2),
        'rating': round(random.uniform(3.0, 5.0), 1),
        'review_count': random.randint(0, 1000)
    }
    products.append(product)

df_products = pd.DataFrame(products)
print(f"   ✓ Created {len(df_products)} products")

# ==================== ORDERS ====================
print("\n3. Generating Orders...")

orders = []
order_items = []
order_id_counter = 1

for _ in range(NUM_ORDERS):
    customer = df_customers.sample(n=1).iloc[0]
    order_date = fake.date_time_between(start_date=DATE_START, end_date=DATE_END)
    
    # Number of items in order (weighted toward smaller orders)
    num_items = random.choices([1, 2, 3, 4, 5], weights=[0.5, 0.25, 0.15, 0.07, 0.03])[0]
    
    # Select products for this order
    order_products = df_products.sample(n=num_items)
    
    order_total = 0
    order_id = f'O{order_id_counter:06d}'
    
    for idx, product in order_products.iterrows():
        quantity = random.randint(1, 3)
        unit_price = product['price']
        discount = random.choices([0, 0.05, 0.10, 0.15, 0.20], weights=[0.6, 0.2, 0.1, 0.05, 0.05])[0]
        
        subtotal = quantity * unit_price * (1 - discount)
        order_total += subtotal
        
        order_item = {
            'order_item_id': f'OI{len(order_items) + 1:08d}',
            'order_id': order_id,
            'product_id': product['product_id'],
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'discount_percent': discount * 100,
            'subtotal': round(subtotal, 2)
        }
        order_items.append(order_item)
    
    # Calculate shipping
    shipping_cost = round(random.uniform(0, 15), 2) if order_total < 50 else 0
    tax = round(order_total * 0.08, 2)
    total = round(order_total + shipping_cost + tax, 2)
    
    # Order status based on date
    days_since_order = (DATE_END - order_date).days
    if days_since_order > 30:
        status = random.choices(
            ['Delivered', 'Cancelled', 'Returned'],
            weights=[0.85, 0.10, 0.05]
        )[0]
    elif days_since_order > 7:
        status = random.choices(
            ['Delivered', 'Shipped', 'Cancelled'],
            weights=[0.80, 0.15, 0.05]
        )[0]
    else:
        status = random.choices(
            ['Processing', 'Shipped', 'Delivered'],
            weights=[0.3, 0.5, 0.2]
        )[0]
    
    order = {
        'order_id': order_id,
        'customer_id': customer['customer_id'],
        'order_date': order_date,
        'order_status': status,
        'payment_method': random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Gift Card']),
        'shipping_address': fake.address().replace('\n', ', '),
        'shipping_method': random.choice(['Standard', 'Express', 'Next Day']),
        'subtotal': round(order_total, 2),
        'shipping_cost': shipping_cost,
        'tax': tax,
        'total': total,
        'region': customer['region']
    }
    orders.append(order)
    order_id_counter += 1

df_orders = pd.DataFrame(orders)
df_order_items = pd.DataFrame(order_items)

print(f"   ✓ Created {len(df_orders)} orders")
print(f"   ✓ Created {len(df_order_items)} order items")

# ==================== CUSTOMER REVIEWS ====================
print("\n4. Generating Customer Reviews...")

reviews = []
review_sentiments = {
    5: ['Excellent', 'Amazing', 'Perfect', 'Love it'],
    4: ['Good', 'Satisfied', 'Nice', 'Worth it'],
    3: ['Okay', 'Average', 'Decent', 'Fair'],
    2: ['Disappointed', 'Not great', 'Issues', 'Below expectations'],
    1: ['Terrible', 'Poor quality', 'Waste of money', 'Do not buy']
}

# Generate reviews for ~30% of order items
sample_items = df_order_items.sample(n=int(len(df_order_items) * 0.3))

for idx, item in sample_items.iterrows():
    order = df_orders[df_orders['order_id'] == item['order_id']].iloc[0]
    
    if order['order_status'] == 'Delivered':
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.15, 0.35, 0.35])[0]
        
        review = {
            'review_id': f'R{len(reviews) + 1:06d}',
            'order_id': item['order_id'],
            'product_id': item['product_id'],
            'customer_id': order['customer_id'],
            'rating': rating,
            'review_title': random.choice(review_sentiments[rating]),
            'review_text': fake.text(max_nb_chars=200),
            'review_date': order['order_date'] + timedelta(days=random.randint(7, 30)),
            'verified_purchase': True,
            'helpful_votes': random.randint(0, 50)
        }
        reviews.append(review)

df_reviews = pd.DataFrame(reviews)
print(f"   ✓ Created {len(df_reviews)} customer reviews")

# ==================== WEB ANALYTICS ====================
print("\n5. Generating Web Analytics...")

page_views = []
sessions = random.randint(20000, 30000)

for i in range(sessions):
    session_date = fake.date_time_between(start_date=DATE_START, end_date=DATE_END)
    customer_id = random.choice([None] + df_customers['customer_id'].tolist()[:1000])  # Some anonymous
    
    page_view = {
        'session_id': f'S{i+1:08d}',
        'customer_id': customer_id,
        'session_date': session_date,
        'device_type': random.choices(['Desktop', 'Mobile', 'Tablet'], weights=[0.5, 0.4, 0.1])[0],
        'browser': random.choice(['Chrome', 'Safari', 'Firefox', 'Edge']),
        'pages_viewed': random.randint(1, 15),
        'session_duration_sec': random.randint(30, 3600),
        'bounce': random.choice([True, False]),
        'converted': random.choice([True, False]),
        'source': random.choice(['Organic Search', 'Direct', 'Social Media', 'Email', 'Paid Ads'])
    }
    page_views.append(page_view)

df_web_analytics = pd.DataFrame(page_views)
print(f"   ✓ Created {len(df_web_analytics)} web sessions")

# ==================== SAVE DATA ====================
print("\n6. Saving Data Files...")

output_dir = '../data/sample/'
os.makedirs(output_dir, exist_ok=True)

df_customers.to_csv(output_dir + 'customers.csv', index=False)
df_products.to_csv(output_dir + 'products.csv', index=False)
df_orders.to_csv(output_dir + 'orders.csv', index=False)
df_order_items.to_csv(output_dir + 'order_items.csv', index=False)
df_reviews.to_csv(output_dir + 'reviews.csv', index=False)
df_web_analytics.to_csv(output_dir + 'web_analytics.csv', index=False)

print(f"\n   ✓ All files saved to '{output_dir}'")

# ==================== SUMMARY STATISTICS ====================
print("\n" + "=" * 60)
print("DATA GENERATION SUMMARY")
print("=" * 60)
print(f"\nCustomers: {len(df_customers):,}")
print(f"Products: {len(df_products):,}")
print(f"Orders: {len(df_orders):,}")
print(f"Order Items: {len(df_order_items):,}")
print(f"Reviews: {len(df_reviews):,}")
print(f"Web Sessions: {len(df_web_analytics):,}")

print(f"\nDate Range: {DATE_START.date()} to {DATE_END.date()}")
print(f"Total Revenue: ${df_orders['total'].sum():,.2f}")
print(f"Average Order Value: ${df_orders['total'].mean():.2f}")

print("\nTop 5 Product Categories by Order Count:")
category_counts = df_order_items.merge(df_products, on='product_id')['category'].value_counts().head()
for cat, count in category_counts.items():
    print(f"   {cat}: {count:,} items")

print("\n" + "=" * 60)
print("✓ Data generation complete!")
print("=" * 60)

"""
Export Analysis to Excel with Formatting
Creates professional Excel workbooks for Business Analyst reporting
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.chart import BarChart, LineChart, PieChart, Reference
    from openpyxl.utils.dataframe import dataframe_to_rows
    EXCEL_AVAILABLE = True
except ImportError:
    print("⚠ openpyxl not installed. Install with: pip install openpyxl")
    EXCEL_AVAILABLE = False

print("=" * 70)
print("EXPORT ANALYSIS TO EXCEL")
print("=" * 70)

if not EXCEL_AVAILABLE:
    print("\n✗ Excel export requires openpyxl library")
    print("Run: pip install openpyxl")
    exit(1)

# ============================================================================
# 1. LOAD PROCESSED DATA
# ============================================================================
print("\n1. Loading processed data...")

try:
    df_orders = pd.read_csv('../data/processed/orders_cleaned.csv', parse_dates=['order_date'])
    df_order_items = pd.read_csv('../data/processed/order_items_cleaned.csv')
    df_products = pd.read_csv('../data/processed/products_cleaned.csv')
    df_customers = pd.read_csv('../data/processed/customers_cleaned.csv')
    print("   ✓ Cleaned data loaded")
except:
    print("   ⚠ Using sample data")
    df_orders = pd.read_csv('../data/sample/orders.csv', parse_dates=['order_date'])
    df_order_items = pd.read_csv('../data/sample/order_items.csv')
    df_products = pd.read_csv('../data/sample/products.csv')
    df_customers = pd.read_csv('../data/sample/customers.csv')

# Filter valid orders
df_orders = df_orders[~df_orders['order_status'].isin(['Cancelled', 'Returned'])]

# ============================================================================
# 2. PREPARE ANALYSIS DATA
# ============================================================================
print("\n2. Preparing analysis datasets...")

# Sales Summary
sales_summary = pd.DataFrame({
    'Metric': [
        'Total Orders',
        'Total Revenue',
        'Average Order Value',
        'Total Customers',
        'Revenue per Customer'
    ],
    'Value': [
        len(df_orders),
        f"${df_orders['total'].sum():,.2f}",
        f"${df_orders['total'].mean():,.2f}",
        df_orders['customer_id'].nunique(),
        f"${df_orders['total'].sum() / df_orders['customer_id'].nunique():,.2f}"
    ]
})

# Sales by Month
df_orders['year_month'] = df_orders['order_date'].dt.to_period('M').astype(str)
monthly_sales = df_orders.groupby('year_month').agg({
    'order_id': 'count',
    'total': 'sum',
    'customer_id': 'nunique'
}).reset_index()
monthly_sales.columns = ['Month', 'Orders', 'Revenue', 'Unique Customers']

# Sales by Category
category_sales = df_order_items.merge(
    df_products[['product_id', 'category']], 
    on='product_id'
).groupby('category').agg({
    'quantity': 'sum',
    'subtotal': 'sum'
}).reset_index()
category_sales.columns = ['Category', 'Units Sold', 'Revenue']
category_sales = category_sales.sort_values('Revenue', ascending=False)

# Top 20 Products
top_products = df_order_items.merge(
    df_products[['product_id', 'product_name', 'category', 'price']], 
    on='product_id'
).groupby(['product_id', 'product_name', 'category']).agg({
    'quantity': 'sum',
    'subtotal': 'sum'
}).reset_index()
top_products.columns = ['Product ID', 'Product Name', 'Category', 'Units Sold', 'Revenue']
top_products = top_products.sort_values('Revenue', ascending=False).head(20)

# Customer Analysis
customer_analysis = df_orders.groupby('customer_id').agg({
    'order_id': 'count',
    'total': 'sum'
}).reset_index()
customer_analysis.columns = ['Customer ID', 'Order Count', 'Total Spent']

# Segment customers
customer_analysis['Segment'] = pd.cut(
    customer_analysis['Total Spent'],
    bins=[0, 200, 500, 1000, float('inf')],
    labels=['Low Value', 'Medium Value', 'High Value', 'VIP']
)

segment_summary = customer_analysis.groupby('Segment').agg({
    'Customer ID': 'count',
    'Total Spent': ['sum', 'mean']
}).reset_index()
segment_summary.columns = ['Segment', 'Customer Count', 'Total Revenue', 'Avg Spent per Customer']

print("   ✓ Analysis datasets prepared")

# ============================================================================
# 3. CREATE EXCEL WORKBOOK
# ============================================================================
print("\n3. Creating Excel workbook...")

output_file = '../../excel/ad_hoc_analysis/Ecommerce_Analysis.xlsx'

# Create Excel writer
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    
    # Sheet 1: Executive Summary
    sales_summary.to_excel(writer, sheet_name='Executive Summary', index=False, startrow=2)
    
    # Sheet 2: Monthly Sales
    monthly_sales.to_excel(writer, sheet_name='Monthly Sales', index=False)
    
    # Sheet 3: Category Analysis
    category_sales.to_excel(writer, sheet_name='Category Analysis', index=False)
    
    # Sheet 4: Top Products
    top_products.to_excel(writer, sheet_name='Top Products', index=False)
    
    # Sheet 5: Customer Segments
    segment_summary.to_excel(writer, sheet_name='Customer Segments', index=False)
    
    # Sheet 6: Raw Data (Orders)
    df_orders[['order_id', 'customer_id', 'order_date', 'order_status', 
               'subtotal', 'shipping_cost', 'tax', 'total', 'region']].head(1000).to_excel(
        writer, sheet_name='Orders Data', index=False
    )

print(f"   ✓ Basic workbook created")

# ============================================================================
# 4. FORMAT EXCEL WORKBOOK
# ============================================================================
print("\n4. Formatting workbook...")

wb = load_workbook(output_file)

# Define styles
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(color="FFFFFF", bold=True, size=12)
title_font = Font(bold=True, size=16, color="2F5597")
border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

def format_header_row(ws, row_num=1):
    """Format header row"""
    for cell in ws[row_num]:
        if cell.value:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

def add_title(ws, title, row=1):
    """Add title to worksheet"""
    ws.merge_cells(f'A{row}:E{row}')
    title_cell = ws[f'A{row}']
    title_cell.value = title
    title_cell.font = title_font
    title_cell.alignment = Alignment(horizontal='center')

# Format Executive Summary
ws_summary = wb['Executive Summary']
add_title(ws_summary, 'E-Commerce Executive Summary', 1)
format_header_row(ws_summary, 3)

# Auto-size columns
for column in ws_summary.columns:
    max_length = 0
    column_letter = column[0].column_letter
    for cell in column:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws_summary.column_dimensions[column_letter].width = min(max_length + 2, 50)

# Format Monthly Sales
ws_monthly = wb['Monthly Sales']
format_header_row(ws_monthly)

# Add a chart
chart = LineChart()
chart.title = "Monthly Revenue Trend"
chart.style = 10
chart.y_axis.title = 'Revenue'
chart.x_axis.title = 'Month'

data = Reference(ws_monthly, min_col=3, min_row=1, max_row=len(monthly_sales)+1)
cats = Reference(ws_monthly, min_col=1, min_row=2, max_row=len(monthly_sales)+1)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
ws_monthly.add_chart(chart, "F2")

# Format Category Analysis
ws_category = wb['Category Analysis']
format_header_row(ws_category)

# Add pie chart
pie = PieChart()
pie.title = "Revenue by Category"
labels = Reference(ws_category, min_col=1, min_row=2, max_row=len(category_sales)+1)
data = Reference(ws_category, min_col=3, min_row=1, max_row=len(category_sales)+1)
pie.add_data(data, titles_from_data=True)
pie.set_categories(labels)
ws_category.add_chart(pie, "E2")

# Format Top Products
ws_products = wb['Top Products']
format_header_row(ws_products)

# Format Customer Segments
ws_segments = wb['Customer Segments']
format_header_row(ws_segments)

# Format Orders Data
ws_orders = wb['Orders Data']
format_header_row(ws_orders)

# Save formatted workbook
wb.save(output_file)
print(f"   ✓ Workbook formatted and saved")

# ============================================================================
# 5. CREATE PIVOT TABLE TEMPLATE
# ============================================================================
print("\n5. Creating pivot table template...")

pivot_file = '../../excel/ad_hoc_analysis/Pivot_Analysis_Template.xlsx'

with pd.ExcelWriter(pivot_file, engine='openpyxl') as writer:
    # Export data for pivot analysis
    orders_for_pivot = df_orders.merge(
        df_order_items, left_on='order_id', right_on='order_id'
    ).merge(
        df_products[['product_id', 'product_name', 'category', 'brand']], 
        on='product_id'
    )
    
    orders_for_pivot['Year'] = orders_for_pivot['order_date'].dt.year
    orders_for_pivot['Quarter'] = orders_for_pivot['order_date'].dt.quarter
    orders_for_pivot['Month'] = orders_for_pivot['order_date'].dt.month_name()
    
    orders_for_pivot[[
        'order_id', 'order_date', 'Year', 'Quarter', 'Month',
        'customer_id', 'region', 'order_status',
        'product_id', 'product_name', 'category', 'brand',
        'quantity', 'unit_price', 'subtotal_y', 'total'
    ]].to_excel(writer, sheet_name='Pivot Source Data', index=False)
    
    # Instructions sheet
    instructions = pd.DataFrame({
        'Instructions': [
            '1. Select the "Pivot Source Data" sheet',
            '2. Go to Insert > PivotTable',
            '3. Create pivot table in new worksheet',
            '4. Example pivots to create:',
            '   - Sales by Category and Month',
            '   - Revenue by Region and Quarter',
            '   - Top Products by Revenue',
            '   - Customer Analysis by Segment',
            '',
            'Suggested Pivot Configurations:',
            '',
            'Pivot 1: Sales by Time Period',
            '- Rows: Year, Quarter, Month',
            '- Values: Sum of total, Count of order_id',
            '',
            'Pivot 2: Category Performance',
            '- Rows: category',
            '- Columns: Year',
            '- Values: Sum of subtotal',
            '',
            'Pivot 3: Regional Analysis',
            '- Rows: region',
            '- Values: Sum of total, Count of customer_id (distinct)'
        ]
    })
    instructions.to_excel(writer, sheet_name='Instructions', index=False)

wb_pivot = load_workbook(pivot_file)
ws_instructions = wb_pivot['Instructions']
for cell in ws_instructions['A']:
    cell.alignment = Alignment(wrap_text=True)
ws_instructions.column_dimensions['A'].width = 70

wb_pivot.save(pivot_file)
print(f"   ✓ Pivot template saved")

# ============================================================================
# 6. SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("EXCEL EXPORT COMPLETE")
print("=" * 70)
print(f"\n📁 Files Created:")
print(f"   1. {output_file}")
print(f"   2. {pivot_file}")
print(f"\n📊 Sheets in Analysis Workbook:")
print(f"   - Executive Summary (KPIs)")
print(f"   - Monthly Sales (with trend chart)")
print(f"   - Category Analysis (with pie chart)")
print(f"   - Top Products")
print(f"   - Customer Segments")
print(f"   - Orders Data (sample)")
print(f"\n💡 Next Steps:")
print(f"   1. Open the Excel files")
print(f"   2. Review the pre-built analysis")
print(f"   3. Create custom pivot tables using the template")
print(f"   4. Add slicers and filters for interactive analysis")
print("\n" + "=" * 70)
print("✓ EXCEL ANALYSIS READY")
print("=" * 70)

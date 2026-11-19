# Power BI Dashboard Setup Guide
## E-Commerce Analytics Platform

---

## Overview

This guide walks you through creating comprehensive Power BI dashboards connected to your e-commerce database. The dashboards provide real-time business intelligence for executives, sales managers, marketing teams, and operations.

---

## Prerequisites

- **Power BI Desktop** installed (free download from Microsoft)
- **Database** populated with data (either PostgreSQL or SQL Server)
- **Database credentials** (connection string, username, password)

---

## Step 1: Connect Power BI to Database

### Option A: SQL Server Connection

1. Open Power BI Desktop
2. Click **Get Data** → **SQL Server**
3. Enter connection details:
   - **Server**: `localhost` (or your server address)
   - **Database**: `ECommerceAnalytics`
4. Choose **DirectQuery** or **Import** mode:
   - **Import**: Faster, refresh manually/scheduled
   - **DirectQuery**: Real-time data, slower performance
5. Click **OK**

### Option B: PostgreSQL Connection

1. Click **Get Data** → **PostgreSQL database**
2. Enter:
   - **Server**: `localhost`
   - **Database**: `ecommerce_db`
3. Enter credentials
4. Click **OK**

---

## Step 2: Import Required Tables

Select and load these tables:

### Fact Tables:
- ✅ `fact_orders`
- ✅ `fact_order_items`

### Dimension Tables:
- ✅ `dim_customers`
- ✅ `dim_products`
- ✅ `dim_date`

### Supporting Tables (Optional):
- ⭕ `customer_reviews`
- ⭕ `web_analytics`

Click **Load** to import the tables.

---

## Step 3: Create Relationships (Data Model)

Power BI should auto-detect relationships, but verify:

### Relationships to Create:

```
dim_customers (customer_key) ----< fact_orders (customer_key)
dim_products (product_key) ----< fact_order_items (product_key)
dim_date (date_key) ----< fact_orders (order_date_key)
fact_orders (order_key) ----< fact_order_items (order_key)
```

**To create relationships:**
1. Click **Model** view (left sidebar)
2. Drag from primary key to foreign key
3. Set cardinality: **One to Many (1:*)**
4. Set cross-filter direction: **Single** (or **Both** for some use cases)

---

## Step 4: Create DAX Measures

Click **Data** view → Right-click table → **New Measure**

### Core Measures:

```dax
// Total Revenue
Total Revenue = SUM(fact_orders[total])

// Total Orders
Total Orders = COUNTROWS(fact_orders)

// Average Order Value
Avg Order Value = DIVIDE([Total Revenue], [Total Orders], 0)

// Total Customers
Total Customers = DISTINCTCOUNT(fact_orders[customer_id])

// Revenue per Customer
Revenue per Customer = DIVIDE([Total Revenue], [Total Customers], 0)

// Total Profit
Total Profit = SUMX(
    fact_order_items,
    fact_order_items[subtotal] - (fact_order_items[cost] * fact_order_items[quantity])
)

// Profit Margin %
Profit Margin % = DIVIDE([Total Profit], SUM(fact_order_items[subtotal]), 0) * 100

// Units Sold
Units Sold = SUM(fact_order_items[quantity])
```

### Time Intelligence Measures:

```dax
// Revenue Last Year
Revenue LY = CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR(dim_date[date])
)

// Revenue Year-over-Year Growth
Revenue YoY Growth = 
DIVIDE([Total Revenue] - [Revenue LY], [Revenue LY], 0)

// Revenue YoY Growth %
Revenue YoY % = [Revenue YoY Growth] * 100

// Month-to-Date Revenue
Revenue MTD = TOTALMTD([Total Revenue], dim_date[date])

// Year-to-Date Revenue
Revenue YTD = TOTALYTD([Total Revenue], dim_date[date])

// Revenue Previous Month
Revenue PM = CALCULATE(
    [Total Revenue],
    DATEADD(dim_date[date], -1, MONTH)
)

// Month-over-Month Growth %
Revenue MoM % = 
DIVIDE([Total Revenue] - [Revenue PM], [Revenue PM], 0) * 100
```

### Customer Metrics:

```dax
// New Customers
New Customers = 
CALCULATE(
    DISTINCTCOUNT(fact_orders[customer_id]),
    FILTER(
        ALL(dim_date),
        dim_date[date] = 
        CALCULATE(MIN(fact_orders[order_date]))
    )
)

// Repeat Customers
Repeat Customers = 
CALCULATE(
    DISTINCTCOUNT(fact_orders[customer_id]),
    FILTER(
        fact_orders,
        CALCULATE(COUNTROWS(fact_orders)) > 1
    )
)

// Customer Retention Rate
Retention Rate = 
DIVIDE([Repeat Customers], [Total Customers], 0) * 100

// Average Customer Lifetime Value
Avg CLV = 
AVERAGEX(
    VALUES(fact_orders[customer_id]),
    CALCULATE([Total Revenue])
)
```

### Product Metrics:

```dax
// Top Product by Revenue
Top Product = 
CALCULATE(
    FIRSTNONBLANK(dim_products[product_name], 1),
    TOPN(1, ALL(dim_products), [Total Revenue], DESC)
)

// Product Stock Status
Stock Status = 
IF(
    SELECTEDVALUE(dim_products[stock_quantity]) = 0,
    "Out of Stock",
    IF(
        SELECTEDVALUE(dim_products[stock_quantity]) <= SELECTEDVALUE(dim_products[reorder_level]),
        "Low Stock",
        "In Stock"
    )
)
```

---

## Step 5: Dashboard 1 - Executive Summary

### Page Layout:

**Top Row: KPI Cards**
- Total Revenue (with YoY %)
- Total Orders (with MoM %)
- Average Order Value (with trend)
- Total Customers (with retention rate)

**Middle Row: Charts**
- **Line Chart**: Revenue trend over time (daily/monthly)
  - X-axis: Date
  - Y-axis: Total Revenue
  - Add forecast line

- **Bar Chart**: Revenue by Category
  - X-axis: Category
  - Y-axis: Total Revenue
  - Sort: Descending

**Bottom Row: Tables & Details**
- **Table**: Top 10 Products by Revenue
  - Columns: Product Name, Revenue, Units Sold, Profit Margin %

- **Map Visual**: Revenue by Region
  - Location: Region
  - Size: Total Revenue

### Slicers (Filters):
- Date Range (slider)
- Order Status (dropdown)
- Region (multi-select)

---

## Step 6: Dashboard 2 - Sales Analysis

### Visuals to Create:

1. **Monthly Sales Trend**
   - Line chart: Month vs Revenue
   - Add another line for Orders
   - Dual Y-axis

2. **Sales by Day of Week**
   - Column chart: Day Name vs Revenue
   - Sort by day order

3. **Sales by Region (Detailed)**
   - Clustered bar chart:
     - X-axis: Region
     - Y-axis: Revenue, Orders, AOV (three bars)

4. **Revenue Heatmap (Matrix)**
   - Rows: Year, Quarter, Month
   - Values: Revenue
   - Conditional formatting: Color scale

5. **Top 5 vs Bottom 5 Products**
   - Two separate tables side-by-side

6. **Category Performance Matrix**
   - Table: Category, Revenue, Units Sold, Profit Margin %, YoY Growth %
   - Conditional formatting on growth

---

## Step 7: Dashboard 3 - Customer Insights

### Visuals:

1. **Customer Segmentation (Pie/Donut Chart)**
   - Segments: VIP, Loyal, Occasional, At Risk
   - Values: Customer Count
   - Add tooltip with avg revenue per segment

2. **Customer Acquisition Trend**
   - Area chart: Month vs New Customers

3. **Customer Lifetime Value Distribution**
   - Histogram: CLV ranges vs Customer Count

4. **Top 20 Customers Table**
   - Columns: Customer Name, Total Spent, Order Count, Last Order Date

5. **Cohort Retention Analysis**
   - Matrix: Registration Month (rows) vs Months Since Registration (columns)
   - Values: % of customers still active

6. **Churn Risk Gauge**
   - Gauge chart: % of customers inactive >90 days
   - Red zone: >30%, Yellow: 20-30%, Green: <20%

---

## Step 8: Dashboard 4 - Product & Inventory

### Visuals:

1. **Inventory Alerts (Card Grid)**
   - Out of Stock count (red)
   - Low Stock count (orange)
   - Adequate Stock count (green)

2. **Stock Status Table**
   - Product Name, Category, Stock Quantity, Reorder Level, Status
   - Conditional formatting: Red/Orange/Green based on status

3. **Inventory Turnover by Category**
   - Bar chart: Category vs Turnover Ratio
   - Add benchmark line (industry standard)

4. **Product Performance Quadrant (Scatter Plot)**
   - X-axis: Units Sold
   - Y-axis: Profit Margin %
   - Size: Revenue
   - Color: Category

5. **Low Performers (Needs Action)**
   - Table: Products with <5 sales in last 30 days
   - Show: Stock Value, Days in Stock

6. **Product Rating vs Sales**
   - Scatter: Rating (X) vs Revenue (Y)
   - Trend line to show correlation

---

## Step 9: Dashboard 5 - Marketing & Web Analytics

### Visuals:

1. **Traffic Source Performance**
   - Stacked column chart:
     - X-axis: Traffic Source
     - Y-axis: Sessions
     - Legend: Converted (Yes/No)

2. **Conversion Rate by Source**
   - Bar chart: Source vs Conversion Rate %
   - Sort descending

3. **Device Type Analysis**
   - Pie chart: Sessions by device
   - Table: Device, Sessions, Conversion %, AOV

4. **Conversion Funnel**
   - Funnel chart:
     - Visits → Product Views → Cart Adds → Checkouts → Purchases

5. **Campaign Performance (if data available)**
   - Table: Campaign, Spend, Revenue, ROI

---

## Step 10: Add Interactivity

### Cross-Filtering:
1. Enable cross-filtering between visuals
2. Click visual → Format → Edit Interactions
3. Set visuals to filter/highlight/no effect

### Bookmarks:
1. Create bookmarks for different views:
   - "Overview"
   - "Deep Dive"
   - "Weekly Review"

### Buttons:
1. Add navigation buttons between pages
2. Insert → Buttons → Choose style
3. Action: Page Navigation

### Tooltips:
1. Create custom tooltip pages
2. Assign to main visuals for rich hover details

---

## Step 11: Formatting & Branding

### Theme:
1. View → Themes → Choose or customize
2. Set brand colors

### Consistent Styling:
- Font: Segoe UI (or your brand font)
- Title size: 14pt, bold
- Card background: Light gray
- Border: 1px solid light gray

### Mobile Layout:
1. View → Mobile Layout
2. Rearrange visuals for phone view
3. Prioritize key metrics

---

## Step 12: Publish & Share

### Publish to Power BI Service:

1. Click **Publish** (top ribbon)
2. Sign in to Power BI account
3. Choose workspace
4. Click **Open in Power BI**

### Set Up Refresh Schedule:

1. In Power BI Service, go to dataset settings
2. **Scheduled refresh** → Configure:
   - Daily refresh at 6 AM
   - Enter database credentials

### Share Dashboard:

1. Click **Share** on dashboard
2. Enter email addresses
3. Set permissions:
   - View only
   - View + Share
   - Edit

### Embed in Website (Optional):

1. File → Publish to web → Get embed code
2. Copy iframe code
3. Paste in your website HTML

---

## Sample Dashboard Layouts

### Executive Dashboard (Page 1):
```
┌─────────────────────────────────────────────────┐
│  📊 E-Commerce Executive Dashboard              │
├──────────┬──────────┬──────────┬────────────────┤
│ Revenue  │ Orders   │ AOV      │ Customers      │
│ $2.1M    │ 15,000   │ $142     │ 5,000          │
│ ↑ 12% YoY│ ↑ 8% MoM │ ↑ 5%     │ ↑ 15%          │
├──────────┴──────────┴──────────┴────────────────┤
│                                                  │
│  📈 Revenue Trend (Line Chart)                  │
│                                                  │
├────────────────────────┬─────────────────────────┤
│ Top Categories         │ Regional Performance    │
│ (Bar Chart)            │ (Map)                   │
├────────────────────────┴─────────────────────────┤
│ Top 10 Products (Table)                          │
└──────────────────────────────────────────────────┘
```

---

## DAX Formula Reference Sheet

### Quick Copy-Paste Formulas:

```dax
// Percentage of Total
% of Total Revenue = 
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL(dim_products)),
    0
) * 100

// Running Total
Running Total Revenue = 
CALCULATE(
    [Total Revenue],
    FILTER(
        ALL(dim_date),
        dim_date[date] <= MAX(dim_date[date])
    )
)

// Rank Products
Product Rank = 
RANKX(
    ALL(dim_products[product_name]),
    [Total Revenue],
    ,
    DESC,
    DENSE
)

// Moving Average (7 days)
Revenue MA7 = 
AVERAGEX(
    DATESINPERIOD(dim_date[date], LASTDATE(dim_date[date]), -7, DAY),
    [Total Revenue]
)

// Custom Sorting
Month Sort = 
SWITCH(
    dim_date[month_name],
    "January", 1, "February", 2, "March", 3,
    "April", 4, "May", 5, "June", 6,
    "July", 7, "August", 8, "September", 9,
    "October", 10, "November", 11, "December", 12
)
```

---

## Troubleshooting

### Issue: Relationships not working
**Solution**: Check data types match (both INT, both VARCHAR, etc.)

### Issue: Time intelligence not working
**Solution**: Mark `dim_date[date]` as Date Table in Model view

### Issue: Slow performance
**Solution**: 
- Use DirectQuery instead of Import
- Reduce visual count per page
- Optimize DAX (avoid nested CALCULATE)

### Issue: Data not refreshing
**Solution**: 
- Check gateway connection
- Verify database credentials
- Ensure scheduled refresh is enabled

---

## Best Practices

1. **Performance**:
   - Limit visuals to 10-15 per page
   - Use measures instead of calculated columns when possible
   - Aggregate data in SQL before importing

2. **Design**:
   - Keep consistent color scheme
   - Use white space effectively
   - Prioritize key metrics at top

3. **Usability**:
   - Add clear titles and labels
   - Include tooltips for guidance
   - Test on mobile view

4. **Maintenance**:
   - Document all custom measures
   - Version control .pbix files
   - Regular data quality checks

---

## Next Steps

1. ✅ Build Executive Dashboard first
2. ✅ Get stakeholder feedback
3. ✅ Iterate on design
4. ✅ Build remaining dashboards
5. ✅ Train end users
6. ✅ Set up monitoring alerts

---

**Created by**: Business Analytics Team  
**Last Updated**: January 2025  
**Power BI Version**: Power BI Desktop (Latest)

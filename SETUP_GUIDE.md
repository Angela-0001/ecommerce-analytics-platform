# Complete Setup Guide
## E-Commerce Analytics Platform - Business Analyst Portfolio

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (30 minutes)](#quick-start)
3. [Full Setup (2-3 hours)](#full-setup)
4. [Database Setup](#database-setup)
5. [Data Generation & ETL](#data-generation--etl)
6. [Data Cleaning](#data-cleaning)
7. [Analytics & Machine Learning](#analytics--machine-learning)
8. [Power BI Dashboards](#power-bi-dashboards)
9. [Excel Analysis](#excel-analysis)
10. [SQL Analytics Queries](#sql-analytics-queries)
11. [Business Analysis Documents](#business-analysis-documents)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software:

✅ **Python 3.8+** - [Download](https://www.python.org/downloads/)  
✅ **SQL Server** or **PostgreSQL** - [SQL Server Express (Free)](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)  
✅ **Power BI Desktop** - [Download (Free)](https://powerbi.microsoft.com/desktop/)  
✅ **Excel** - Microsoft 365 or standalone  
✅ **Git** (optional) - [Download](https://git-scm.com/)  
✅ **SQL Server Management Studio** or **Azure Data Studio** - [Download](https://docs.microsoft.com/sql/ssms/)

**Estimated Total Setup Time**: 2-3 hours  
**Disk Space Required**: ~2 GB

---

## Quick Start (30 minutes)

**Goal**: Get core analytics running quickly

### Step 1: Install Python Dependencies

```bash
cd python
pip install -r requirements.txt
```

### Step 2: Generate Sample Data

```bash
cd data_generation
python generate_ecommerce_data.py
```

**Output**: 6 CSV files in `data/sample/`
- customers.csv (5,000 records)
- products.csv (200 records)
- orders.csv (15,000 records)
- order_items.csv (45,000+ records)
- reviews.csv (4,500+ records)
- web_analytics.csv (25,000+ records)

### Step 3: Run Data Cleaning

```bash
cd ../data_cleaning
python clean_and_validate.py
```

**Output**: Cleaned CSVs in `data/processed/`

### Step 4: Customer Segmentation Analysis

```bash
cd ../analysis
python customer_segmentation.py
```

**Output**: 
- Customer segments with RFM analysis
- Visualizations saved as PNG files
- Segmented customer list CSV

### Step 5: Sales Forecasting

```bash
python sales_forecasting.py
```

**Output**:
- 30-day revenue forecast
- Model accuracy metrics
- Forecast visualization charts

### Step 6: Export to Excel

```bash
python export_to_excel.py
```

**Output**: Excel workbooks in `excel/ad_hoc_analysis/`

✅ **Done! You now have:**
- Cleaned datasets
- Customer segments
- Sales forecasts
- Excel reports ready for analysis

---

## Full Setup (2-3 hours)

**Goal**: Complete end-to-end platform with database and Power BI

---

## Database Setup

### Option A: SQL Server

#### 1. Create Database

Open **SQL Server Management Studio (SSMS)** or **Azure Data Studio**

```sql
-- Run this first
CREATE DATABASE ECommerceAnalytics;
GO
```

#### 2. Run Schema Scripts

Execute in order:
1. `sql/schema/01_create_database.sql`
2. `sql/schema/02_populate_date_dimension.sql`

#### 3. Verify Setup

```sql
USE ECommerceAnalytics;

-- Check tables created
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE';

-- Check date dimension populated
SELECT COUNT(*) as DateCount FROM dim_date;
-- Should return ~1,461 rows (4 years of dates)
```

---

### Option B: PostgreSQL

#### 1. Create Database

```bash
# Command line
createdb ecommerce_db

# Or in psql
CREATE DATABASE ecommerce_db;
```

#### 2. Adjust SQL Scripts for PostgreSQL

Some syntax differences to change:

**SQL Server → PostgreSQL conversions:**
- `IDENTITY(1,1)` → `SERIAL`
- `GETDATE()` → `CURRENT_TIMESTAMP`
- `DATEADD()` → Use interval: `date + INTERVAL '1 day'`
- `VARCHAR(MAX)` → `TEXT`

#### 3. Run Modified Scripts

```bash
psql -d ecommerce_db -f sql/schema/01_create_database_pg.sql
psql -d ecommerce_db -f sql/schema/02_populate_date_dimension_pg.sql
```

---

## Data Generation & ETL

### Step 1: Configure Database Connection

**For SQL Server:**

Edit `python/etl/load_data_to_sql.py`:

```python
CONNECTION_STRING = (
    'Driver={SQL Server};'
    'Server=localhost;'  # Change if remote
    'Database=ECommerceAnalytics;'
    'Trusted_Connection=yes;'  # Windows Authentication
)

# Or with username/password:
CONNECTION_STRING = (
    'Driver={SQL Server};'
    'Server=localhost;'
    'Database=ECommerceAnalytics;'
    'UID=your_username;'
    'PWD=your_password;'
)
```

**For PostgreSQL:**

```python
CONNECTION_STRING = (
    'host=localhost '
    'dbname=ecommerce_db '
    'user=postgres '
    'password=your_password'
)
```

### Step 2: Generate Data (if not done already)

```bash
cd python/data_generation
python generate_ecommerce_data.py
```

### Step 3: Run ETL Pipeline

```bash
cd ../etl
python load_data_to_sql.py
```

**Expected Output:**
```
✓ Database connection established
✓ Loaded 5000 customers
✓ Loaded 200 products
✓ Loaded 15000 orders
✓ Loaded 45000+ order items
✓ Loaded 4500+ reviews
✓ Loaded 25000+ web sessions
```

### Step 4: Verify Data Loaded

```sql
-- Check record counts
SELECT 'Customers' as TableName, COUNT(*) as RecordCount FROM dim_customers
UNION ALL
SELECT 'Products', COUNT(*) FROM dim_products
UNION ALL
SELECT 'Orders', COUNT(*) FROM fact_orders
UNION ALL
SELECT 'Order Items', COUNT(*) FROM fact_order_items;
```

---

## Analytics & Machine Learning

### 1. Data Cleaning & Validation

```bash
cd python/data_cleaning
python clean_and_validate.py
```

**Check outputs:**
- `data/processed/customers_cleaned.csv`
- `data/processed/products_cleaned.csv`
- `data/processed/orders_cleaned.csv`
- `data/processed/cleaning_report.csv` ← Review this!

### 2. Customer Segmentation

```bash
cd ../analysis
python customer_segmentation.py
```

**Review outputs:**
- Console: Segment summary and recommendations
- `analysis/elbow_curve.png` - Optimal cluster count
- `analysis/cluster_metrics.png` - Segment characteristics
- `analysis/segmentation_scatter.png` - Visual clusters
- `analysis/segmentation_3d.png` - 3D RFM view
- `data/processed/customer_segments.csv` - Full segment list

### 3. Sales Forecasting

```bash
python sales_forecasting.py
```

**Review outputs:**
- Console: Model performance metrics (R², MAE, RMSE)
- `analysis/sales_analysis.png` - Historical trends
- `analysis/moving_averages.png` - Smoothed trends
- `analysis/revenue_forecast.png` - 30-day prediction
- `data/processed/revenue_forecast_30days.csv` - Forecast data
- `data/processed/model_comparison.csv` - Model accuracy

### 4. Export to Excel

```bash
python export_to_excel.py
```

**Created files:**
- `excel/ad_hoc_analysis/Ecommerce_Analysis.xlsx` - Pre-built analysis
- `excel/ad_hoc_analysis/Pivot_Analysis_Template.xlsx` - DIY pivots

---

## Power BI Dashboards

See detailed guide: **`docs/PowerBI_Dashboard_Guide.md`**

### Quick Setup:

1. **Open Power BI Desktop**

2. **Get Data** → **SQL Server** (or PostgreSQL)
   - Server: `localhost`
   - Database: `ECommerceAnalytics`

3. **Select Tables:**
   - dim_customers
   - dim_products
   - dim_date
   - fact_orders
   - fact_order_items

4. **Load Data** (choose Import or DirectQuery)

5. **Create Relationships** (should auto-detect):
   - dim_customers → fact_orders (customer_key)
   - dim_products → fact_order_items (product_key)
   - dim_date → fact_orders (date_key)
   - fact_orders → fact_order_items (order_key)

6. **Create DAX Measures:**

```dax
Total Revenue = SUM(fact_orders[total])
Total Orders = COUNTROWS(fact_orders)
Avg Order Value = DIVIDE([Total Revenue], [Total Orders], 0)
Total Customers = DISTINCTCOUNT(fact_orders[customer_id])
```

7. **Build Dashboards** (see guide for layouts):
   - Page 1: Executive Summary
   - Page 2: Sales Analysis
   - Page 3: Customer Insights
   - Page 4: Product & Inventory
   - Page 5: Web Analytics

8. **Save** as `powerbi/dashboards/Ecommerce_Analytics.pbix`

---

## Excel Analysis

### Pre-built Analysis Workbook

1. Open `excel/ad_hoc_analysis/Ecommerce_Analysis.xlsx`

2. **Sheets available:**
   - Executive Summary (KPIs)
   - Monthly Sales (with chart)
   - Category Analysis (with pie chart)
   - Top Products
   - Customer Segments
   - Orders Data (sample)

3. **Explore & Customize:**
   - Change date filters
   - Add your own calculations
   - Create additional charts

### DIY Pivot Tables

1. Open `excel/ad_hoc_analysis/Pivot_Analysis_Template.xlsx`

2. Select **Pivot Source Data** sheet

3. **Insert → PivotTable** → New Worksheet

4. **Example Pivots to Create:**

**Pivot 1: Sales by Time**
- Rows: Year, Quarter, Month
- Values: Sum of total

**Pivot 2: Category Performance**
- Rows: category
- Columns: Year
- Values: Sum of subtotal

**Pivot 3: Regional Analysis**
- Rows: region
- Values: Sum of total, Count of customer_id

5. **Add Slicers:**
   - Insert → Slicer
   - Choose: Year, Category, Region

---

## SQL Analytics Queries

### Run Analytical Queries

Open `sql/queries/analytics_queries.sql` in SSMS or Azure Data Studio

**Key queries included:**

1. **Sales Overview** - Daily/Monthly/Yearly performance
2. **Top Products** - By revenue, units, profit
3. **Customer Segments** - RFM-based grouping
4. **Regional Analysis** - Performance by geography
5. **Inventory Alerts** - Low stock warnings
6. **Cohort Analysis** - Customer retention by registration cohort
7. **YoY Comparisons** - Growth trends

**Run Stored Procedure:**

```sql
-- Sales report for specific period and filters
EXEC sp_sales_report 
    @StartDate = '2024-01-01',
    @EndDate = '2024-12-31',
    @Region = 'North',  -- NULL for all regions
    @Category = NULL;   -- NULL for all categories
```

---

## Business Analysis Documentation

### Review Documents Created:

1. **Business Requirements Document (BRD)**
   - `web/business_analysis/requirements/BRD_Business_Requirements_Document.md`
   - Requirements, user stories, success criteria

2. **User Stories Backlog**
   - `web/business_analysis/user_stories/User_Stories_Backlog.md`
   - 22 user stories across 7 epics, with story points

3. **Business Insights Report**
   - `docs/Business_Insights_Report.md`
   - 30+ pages of analysis, recommendations, ROI projections

4. **Power BI Dashboard Guide**
   - `docs/PowerBI_Dashboard_Guide.md`
   - Step-by-step dashboard creation with DAX formulas

---

## Troubleshooting

### Issue: Python packages won't install

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install packages one by one to identify problem
pip install pandas
pip install numpy
pip install scikit-learn
# etc.
```

---

### Issue: Can't connect to SQL Server

**Solutions:**
1. Check SQL Server is running:
   - Windows: Services → SQL Server (MSSQLSERVER) → Running
   
2. Enable TCP/IP protocol:
   - SQL Server Configuration Manager → SQL Server Network Configuration → Protocols → TCP/IP → Enable

3. Check firewall:
   - Allow port 1433 for SQL Server

4. Try different connection string:
```python
# Try with explicit port
CONNECTION_STRING = (
    'Driver={SQL Server};'
    'Server=localhost,1433;'  # Note the comma
    'Database=ECommerceAnalytics;'
    'Trusted_Connection=yes;'
)
```

---

### Issue: PostgreSQL authentication failed

**Solution:**
Edit `pg_hba.conf`:

```conf
# Change from peer to md5
local   all    all    md5
host    all    all    127.0.0.1/32    md5
```

Restart PostgreSQL:
```bash
# Windows
net stop postgresql-x64-14
net start postgresql-x64-14

# Linux
sudo service postgresql restart
```

---

### Issue: Power BI relationships not working

**Solutions:**
1. Check data types match in both tables
2. Mark `dim_date[date]` as Date Table:
   - Table Tools → Mark as Date Table
3. Remove duplicate keys in dimension tables
4. Set proper cardinality (1:Many)

---

### Issue: Excel file too large / slow

**Solutions:**
1. Reduce data size - export subset of rows
2. Remove calculated columns, use formulas instead
3. Turn off auto-calculation: Formulas → Calculation Options → Manual
4. Save as binary format (.xlsb) instead of .xlsx

---

### Issue: Python script "ModuleNotFoundError"

**Solution:**
```bash
# Make sure you're in the right directory
cd python

# Check Python path
python -c "import sys; print(sys.path)"

# Install in user directory if permission issues
pip install --user -r requirements.txt
```

---

## Verification Checklist

Use this to confirm everything is working:

### Data Layer:
- [ ] Database created and accessible
- [ ] All tables created (9 tables total)
- [ ] Date dimension populated (1,461 rows)
- [ ] Sample data generated (6 CSV files)
- [ ] Data loaded to database via ETL

### Analytics Layer:
- [ ] Data cleaning completed successfully
- [ ] Customer segmentation run (4 segments identified)
- [ ] Sales forecasting completed (30-day forecast generated)
- [ ] Excel exports created (2 workbooks)

### Visualization Layer:
- [ ] Power BI connects to database
- [ ] Relationships configured correctly
- [ ] DAX measures created
- [ ] At least 1 dashboard built

### Documentation Layer:
- [ ] BRD document reviewed
- [ ] User stories reviewed
- [ ] Business insights report reviewed
- [ ] Setup guide followed (this document!)

---

## Next Steps

### For Portfolio/Interview:

1. **Create Screenshots:**
   - Power BI dashboards
   - Excel pivot tables
   - Python visualizations

2. **Prepare Talking Points:**
   - "I analyzed 15K orders to identify 4 customer segments..."
   - "Built ML model with 84% accuracy for sales forecasting..."
   - "Recommended actions that could increase revenue by $185K..."

3. **Demo Script:**
   - 5-minute walkthrough of key insights
   - Show BRD and requirements process
   - Demonstrate Power BI dashboard interactivity

4. **GitHub Repository:**
   - Push code to GitHub
   - Write clear README
   - Add screenshots to repo

5. **LinkedIn Post:**
   - Share project highlights
   - Include visuals and key findings

---

## Support & Resources

- **Project GitHub**: [Your Repo URL]
- **LinkedIn**: [Your Profile]
- **Email**: [Your Email]

**Documentation:**
- Power BI: https://docs.microsoft.com/power-bi/
- Pandas: https://pandas.pydata.org/docs/
- Scikit-learn: https://scikit-learn.org/
- SQL Server: https://docs.microsoft.com/sql/

---

**Setup Complete! 🎉**

You now have a complete Business Analyst portfolio project demonstrating:
✅ Requirements gathering (BRD, user stories)  
✅ Data engineering (ETL, cleaning)  
✅ Analytics (segmentation, forecasting)  
✅ Visualization (Power BI, Excel, Python)  
✅ Business insights & recommendations

---

**Last Updated**: January 2025  
**Project Version**: 1.0

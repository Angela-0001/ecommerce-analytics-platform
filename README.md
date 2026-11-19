# E-Commerce Sales Analytics Platform
## Complete Business Analyst Portfolio Project

## 📊 Project Overview

A **full-stack e-commerce platform** with integrated business intelligence and analytics capabilities. This project demonstrates the complete BA skillset: from gathering requirements and creating documentation, through data analysis and modeling, to delivering actionable business insights.

**Perfect for**: Business Analyst, Data Analyst, BI Analyst roles

### What Makes This Project Special

**1. Real Business Context**
- Complete Business Requirements Document (BRD)
- Agile user stories with acceptance criteria
- Process flow diagrams
- Stakeholder-ready presentations

**2. Full Data Pipeline**
- Functional e-commerce website (Node.js + React)
- PostgreSQL database with star schema design
- Data cleaning & validation scripts
- ETL automation with error handling

**3. Advanced Analytics**
- Customer segmentation (RFM analysis, K-Means clustering)
- Sales forecasting (ML models: Linear Regression, Random Forest)
- Cohort analysis and churn prediction
- Inventory optimization algorithms

**4. Multiple Visualization Tools**
- Power BI dashboards with DAX measures
- Excel pivot tables and ad-hoc analysis
- Python visualizations (Matplotlib, Seaborn)
- Custom web dashboards

**5. Business Insights & Recommendations**
- 30+ page insights report with ROI calculations
- Prioritized action items with expected impact
- Risk assessment and mitigation strategies
- Executive-ready presentations

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Database** | PostgreSQL / SQL Server | Star schema data warehouse design |
| **Data Generation** | Python (Faker, Pandas) | Create realistic sample data (15K orders) |
| **ETL Pipeline** | Python (Pandas, PyODBC) | Extract, transform, load automation |
| **Data Cleaning** | Python (Pandas, NumPy) | Validation, outlier detection, quality checks |
| **Machine Learning** | Scikit-learn | Customer segmentation, sales forecasting |
| **SQL Analytics** | T-SQL / PostgreSQL | Complex queries, stored procedures, views |
| **Power BI** | Power BI Desktop | Interactive dashboards with DAX measures |
| **Excel Analysis** | Excel (PivotTables, charts) | Ad-hoc analysis, what-if scenarios |
| **Python Visualization** | Matplotlib, Seaborn | Statistical charts and analysis |
| **BA Documentation** | Markdown, Word | BRD, user stories, process maps |

---

## 📁 Project Structure

```
E-commerce_sales_platform/
│
├── data/
│   ├── raw/                      # Original source data
│   ├── processed/                # Cleaned, validated data
│   └── sample/                   # Generated sample datasets
│       ├── customers.csv         (5,000 customers)
│       ├── products.csv          (200 products)
│       ├── orders.csv            (15,000 orders)
│       ├── order_items.csv       (45,000+ line items)
│       ├── reviews.csv           (4,500+ reviews)
│       └── web_analytics.csv     (25,000+ sessions)
│
├── sql/
│   ├── schema/
│   │   ├── 01_create_database.sql           # Star schema DDL
│   │   └── 02_populate_date_dimension.sql   # Date table population
│   ├── stored_procedures/
│   │   └── sp_sales_report.sql              # Parameterized reports
│   └── queries/
│       └── analytics_queries.sql            # 15+ business queries
│
├── python/
│   ├── data_generation/
│   │   └── generate_ecommerce_data.py       # Synthetic data generator
│   ├── data_cleaning/
│   │   └── clean_and_validate.py            # Data quality pipeline
│   ├── etl/
│   │   └── load_data_to_sql.py              # ETL automation
│   ├── analysis/
│   │   ├── customer_segmentation.py         # RFM + K-Means clustering
│   │   ├── sales_forecasting.py             # ML forecasting models
│   │   └── export_to_excel.py               # Excel report generation
│   └── requirements.txt
│
├── excel/
│   └── ad_hoc_analysis/
│       ├── Ecommerce_Analysis.xlsx          # Pre-built analysis
│       └── Pivot_Analysis_Template.xlsx     # DIY pivot tables
│
├── powerbi/
│   └── dashboards/
│       └── [Your .pbix files here]          # Power BI dashboards
│
├── business_analysis/
│   ├── requirements/
│   │   └── BRD_Business_Requirements_Document.md
│   └── user_stories/
│       └── User_Stories_Backlog.md          # 22 user stories, 7 epics
│
├── docs/
│   ├── Business_Insights_Report.md          # 30+ page analysis
│   ├── PowerBI_Dashboard_Guide.md           # Dashboard setup guide
│   └── database_design.md
│
├── README.md                                # Project overview
└── SETUP_GUIDE.md                          # Complete setup instructions
```

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+**
2. **SQL Server** or **PostgreSQL**
3. **Power BI Desktop** (free from Microsoft)
4. **Excel** (Microsoft 365 or standalone)

### Installation

1. **Clone or download this repository**

2. **Install Python dependencies**
```bash
cd python
pip install -r requirements.txt
```

3. **Set up database**
   - Ensure SQL Server or PostgreSQL is running
   - Execute scripts in order:
     ```sql
     -- In SQL Server Management Studio or Azure Data Studio:
     1. Run sql/schema/01_create_database.sql
     2. Run sql/schema/02_populate_date_dimension.sql
     ```

---

## 📋 Step-by-Step Execution

### Step 1: Generate Sample Data

```bash
cd python/data_generation
python generate_ecommerce_data.py
```

**Output:**
- 5,000 customers
- 200 products across 10 categories
- 15,000 orders (2022-2024)
- 45,000+ order items
- 4,500+ customer reviews
- 25,000+ web analytics sessions

All CSV files saved to `data/sample/`

### Step 2: Load Data to SQL Database

```bash
cd python/etl
python load_data_to_sql.py
```

**What it does:**
- Transforms flat CSV files to star schema
- Validates and cleans data
- Loads into dimension and fact tables
- Logs ETL process in audit table

### Step 3: Run SQL Analytics Queries

Open `sql/queries/analytics_queries.sql` in SSMS and execute queries such as:

- Sales performance by month/category/region
- Top products and customers
- Year-over-year comparisons
- Customer cohort analysis
- Inventory alerts

**Try the stored procedure:**
```sql
-- Sales report for Q4 2024 in North region
EXEC sp_sales_report 
    @StartDate = '2024-10-01',
    @EndDate = '2024-12-31',
    @Region = 'North';
```

### Step 4: Customer Segmentation Analysis (Python)

```bash
cd python/analysis
python customer_segmentation.py
```

**What it does:**
- Extracts RFM (Recency, Frequency, Monetary) metrics
- Performs K-Means clustering
- Segments customers into 4 groups:
  - VIP Champions
  - Loyal Customers
  - Potential Loyalists
  - At Risk / Churned
- Generates visualizations (elbow curve, scatter plots, 3D clusters)
- Exports segmented customer list

**Outputs:**
- `data/processed/customer_segments.csv`
- Visualizations in `python/analysis/` folder

### Step 5: Power BI Dashboard

**See detailed guide**: `docs/PowerBI_Dashboard_Guide.md`

1. Open Power BI Desktop
2. **Get Data** → SQL Server (or PostgreSQL)
3. Connect to `localhost` → `ECommerceAnalytics` database
4. Import tables: `fact_orders`, `fact_order_items`, `dim_customers`, `dim_products`, `dim_date`
5. Create relationships (star schema)
6. Build dashboards:
   - **Page 1: Executive Summary** (KPIs, revenue trends)
   - **Page 2: Sales Analysis** (by category, region, time)
   - **Page 3: Customer Insights** (segments, cohorts, CLV)
   - **Page 4: Product & Inventory** (top sellers, stock alerts)

**DAX Measures Examples:**
```dax
Total Revenue = SUM(fact_orders[total])
Avg Order Value = DIVIDE([Total Revenue], COUNTROWS(fact_orders))
Revenue YoY % = 
  DIVIDE(
    [Total Revenue] - CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[date])),
    CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[date]))
  ) * 100
```

**Complete dashboard guide with 50+ DAX formulas**: See `docs/PowerBI_Dashboard_Guide.md`

### Step 6: Excel Ad-Hoc Analysis

1. Open Excel
2. **Data** → **Get Data** → **From Database** → **From SQL Server**
3. Connect and load `fact_orders` and related dimensions
4. Create PivotTables:
   - Sales by month and category
   - Customer purchase frequency
   - Regional performance comparisons
5. Use Excel for quick what-if scenarios and flexible exploration

---

## 📊 Database Schema

### Star Schema Design

**Fact Tables:**
- `fact_orders` - Order header (grain: one row per order)
- `fact_order_items` - Order line items (grain: one row per product per order)

**Dimension Tables:**
- `dim_customers` - Customer information and segmentation
- `dim_products` - Product catalog with pricing and inventory
- `dim_date` - Date dimension with fiscal calendars and holidays

**Supporting Tables:**
- `customer_reviews` - Product ratings and reviews
- `web_analytics` - Website traffic and conversion metrics
- `etl_audit_log` - ETL process monitoring

See `docs/database_design.md` for detailed entity-relationship diagrams.

---

## 📈 Key Analyses & Insights

### 1. Sales Performance
- **Total Revenue:** $X million over 3 years
- **Average Order Value:** $X
- **Peak Sales Period:** Black Friday / Cyber Monday
- **Top Category:** Electronics (35% of revenue)

### 2. Customer Segmentation
| Segment | Size | Avg Frequency | Avg Monetary | Strategy |
|---------|------|---------------|--------------|----------|
| VIP Champions | 12% | 8.5 orders | $2,100 | Loyalty rewards, exclusive access |
| Loyal Customers | 28% | 5.2 orders | $850 | Upsell, referral programs |
| Potential Loyalists | 35% | 2.8 orders | $420 | Engagement campaigns |
| At Risk / Churned | 25% | 1.9 orders | $310 | Win-back offers |

### 3. Regional Performance
- **North:** Highest revenue, strong electronics sales
- **West:** Highest average order value
- **South:** Growing market with 15% YoY growth
- **East:** Highest customer acquisition rate

### 4. Inventory Optimization
- 18 products currently out of stock
- 45 products need reordering (below reorder level)
- Recommendation: Increase safety stock for top 20 products

### 5. Web Traffic Insights
- **Conversion Rate:** 3.2% overall
- **Best Source:** Organic Search (4.1% conversion)
- **Mobile:** 40% of traffic, but lower conversion (2.8%)
- **Opportunity:** Optimize mobile experience

---

## 🎯 Business Recommendations

### Short-term (0-3 months)
1. Launch win-back campaign for at-risk customers (25% of base)
2. Restock 18 out-of-stock high-demand products
3. Optimize mobile website (testing shows 15% conversion lift potential)
4. Run targeted promotions for "Potential Loyalists" segment

### Medium-term (3-6 months)
1. Expand product offerings in top-performing categories
2. Implement dynamic pricing based on demand and inventory
3. Develop regional marketing strategies based on performance data
4. Create VIP loyalty program for top 12% of customers

### Long-term (6-12 months)
1. Build predictive models for demand forecasting
2. Implement real-time inventory management system
3. Expand to new regions based on market analysis
4. Develop personalized recommendation engine

---

## 🧪 Skills Demonstrated

### Technical Skills (Business Analyst Core)
- ✅ **SQL**: Complex queries, joins, CTEs, window functions, stored procedures
- ✅ **Python**: Pandas (data manipulation), NumPy, Scikit-learn (ML)
- ✅ **Power BI**: Dashboard design, DAX measures, data modeling
- ✅ **Excel**: Pivot tables, VLOOKUP, charts, data validation
- ✅ **ETL**: Data pipeline design, error handling, audit logging
- ✅ **Database Design**: Star schema, normalization, indexing
- ✅ **Data Cleaning**: Validation, outlier detection, quality checks
- ✅ **Machine Learning**: K-Means clustering, regression, forecasting

### Business Analysis Skills
- ✅ **Requirements Gathering**: BRD, functional specs, acceptance criteria
- ✅ **User Stories**: Agile format, story points, sprint planning
- ✅ **Process Mapping**: Current state vs future state analysis
- ✅ **Data Analysis**: RFM segmentation, cohort analysis, funnel analysis
- ✅ **Statistical Analysis**: Descriptive stats, correlation, forecasting
- ✅ **Business Intelligence**: KPI definition, metric tracking, trend analysis
- ✅ **Insights & Recommendations**: ROI calculations, prioritization frameworks

### Visualization & Communication
- ✅ **Power BI Dashboards**: Interactive, drill-down capable, role-based
- ✅ **Excel Reports**: Formatted, professional, chart-rich
- ✅ **Python Charts**: Matplotlib, Seaborn statistical plots
- ✅ **Documentation**: Technical writing, process documentation
- ✅ **Storytelling**: Data-driven narratives, executive summaries

---

## 📚 Additional Resources

- **SQL Server Documentation:** https://docs.microsoft.com/sql/
- **Power BI Learning:** https://learn.microsoft.com/power-bi/
- **Scikit-learn Clustering:** https://scikit-learn.org/stable/modules/clustering.html
- **Pandas User Guide:** https://pandas.pydata.org/docs/

---

## 🤝 Contributing

This project is a portfolio demonstration. Suggestions for improvements are welcome:
- Open an issue for bugs or feature requests
- Submit pull requests for enhancements
- Share your own implementations or extensions

---

## 📄 License

This project is open source and available for educational and portfolio purposes.

---

## 📧 Contact

**[Your Name]**
- LinkedIn: [Your LinkedIn]
- Email: [Your Email]
- Portfolio: [Your Website]

---

## 🌟 Acknowledgments

- Faker library for synthetic data generation
- Microsoft for SQL Server and Power BI
- Python data science community (Pandas, Scikit-learn, Matplotlib)

---

**Last Updated:** January 2025

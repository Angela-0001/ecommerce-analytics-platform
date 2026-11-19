"""
Sales Forecasting Model
Time series analysis and revenue prediction using multiple methods
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)

print("=" * 70)
print("SALES FORECASTING & PREDICTION MODEL")
print("=" * 70)

# ============================================================================
# 1. LOAD AND PREPARE DATA
# ============================================================================
print("\n1. Loading cleaned data...")

try:
    df_orders = pd.read_csv('../data/processed/orders_cleaned.csv', parse_dates=['order_date'])
    df_order_items = pd.read_csv('../data/processed/order_items_cleaned.csv')
    df_products = pd.read_csv('../data/processed/products_cleaned.csv')
    print(f"   ✓ Loaded {len(df_orders)} orders")
except:
    print("   ⚠ Using sample data instead")
    df_orders = pd.read_csv('../data/sample/orders.csv', parse_dates=['order_date'])
    df_order_items = pd.read_csv('../data/sample/order_items.csv')
    df_products = pd.read_csv('../data/sample/products.csv')

# Filter out cancelled/returned orders
df_orders = df_orders[~df_orders['order_status'].isin(['Cancelled', 'Returned'])]

# ============================================================================
# 2. DAILY SALES AGGREGATION
# ============================================================================
print("\n2. Aggregating daily sales...")

# Group by date
daily_sales = df_orders.groupby(df_orders['order_date'].dt.date).agg({
    'order_id': 'count',
    'total': 'sum',
    'subtotal': 'sum',
    'customer_id': 'nunique'
}).reset_index()

daily_sales.columns = ['date', 'order_count', 'revenue', 'subtotal', 'unique_customers']
daily_sales['date'] = pd.to_datetime(daily_sales['date'])
daily_sales['avg_order_value'] = daily_sales['revenue'] / daily_sales['order_count']

print(f"   ✓ Aggregated to {len(daily_sales)} days of sales data")

# Create time-based features
daily_sales['day_of_week'] = daily_sales['date'].dt.dayofweek
daily_sales['day_name'] = daily_sales['date'].dt.day_name()
daily_sales['month'] = daily_sales['date'].dt.month
daily_sales['quarter'] = daily_sales['date'].dt.quarter
daily_sales['day_of_month'] = daily_sales['date'].dt.day
daily_sales['week_of_year'] = daily_sales['date'].dt.isocalendar().week
daily_sales['is_weekend'] = daily_sales['day_of_week'].isin([5, 6]).astype(int)
daily_sales['is_month_start'] = (daily_sales['day_of_month'] <= 7).astype(int)
daily_sales['is_month_end'] = (daily_sales['day_of_month'] >= 24).astype(int)

# Add day number for regression
daily_sales['day_number'] = (daily_sales['date'] - daily_sales['date'].min()).dt.days

# ============================================================================
# 3. EXPLORATORY ANALYSIS
# ============================================================================
print("\n3. Analyzing sales patterns...")

print("\n   Sales Statistics:")
print(f"   - Total Revenue: ${daily_sales['revenue'].sum():,.2f}")
print(f"   - Average Daily Revenue: ${daily_sales['revenue'].mean():,.2f}")
print(f"   - Median Daily Revenue: ${daily_sales['revenue'].median():,.2f}")
print(f"   - Std Dev: ${daily_sales['revenue'].std():,.2f}")

# Day of week analysis
dow_sales = daily_sales.groupby('day_name')['revenue'].mean().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
])

print("\n   Average Revenue by Day of Week:")
for day, revenue in dow_sales.items():
    print(f"   - {day}: ${revenue:,.2f}")

# ============================================================================
# 4. VISUALIZATION
# ============================================================================
print("\n4. Creating visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# 4.1 Daily Revenue Trend
axes[0, 0].plot(daily_sales['date'], daily_sales['revenue'], linewidth=1.5, color='steelblue')
axes[0, 0].set_title('Daily Revenue Trend', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('Date')
axes[0, 0].set_ylabel('Revenue ($)')
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].tick_params(axis='x', rotation=45)

# 4.2 Revenue by Day of Week
dow_sales.plot(kind='bar', ax=axes[0, 1], color='coral', alpha=0.7)
axes[0, 1].set_title('Average Revenue by Day of Week', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Day')
axes[0, 1].set_ylabel('Average Revenue ($)')
axes[0, 1].grid(axis='y', alpha=0.3)
axes[0, 1].tick_params(axis='x', rotation=45)

# 4.3 Monthly Revenue Trend
monthly_sales = daily_sales.groupby([daily_sales['date'].dt.to_period('M')])['revenue'].sum()
monthly_sales.index = monthly_sales.index.to_timestamp()
axes[1, 0].bar(range(len(monthly_sales)), monthly_sales.values, color='forestgreen', alpha=0.7)
axes[1, 0].set_title('Monthly Revenue', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('Month')
axes[1, 0].set_ylabel('Revenue ($)')
axes[1, 0].grid(axis='y', alpha=0.3)
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].set_xticks(range(len(monthly_sales)))
axes[1, 0].set_xticklabels([d.strftime('%Y-%m') for d in monthly_sales.index], rotation=45)

# 4.4 Revenue Distribution
axes[1, 1].hist(daily_sales['revenue'], bins=30, color='purple', alpha=0.7, edgecolor='black')
axes[1, 1].set_title('Daily Revenue Distribution', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Revenue ($)')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('../analysis/sales_analysis.png', dpi=300, bbox_inches='tight')
print("   ✓ Sales analysis charts saved")

# ============================================================================
# 5. MOVING AVERAGES
# ============================================================================
print("\n5. Calculating moving averages...")

daily_sales['ma_7'] = daily_sales['revenue'].rolling(window=7, min_periods=1).mean()
daily_sales['ma_30'] = daily_sales['revenue'].rolling(window=30, min_periods=1).mean()

plt.figure(figsize=(14, 6))
plt.plot(daily_sales['date'], daily_sales['revenue'], label='Daily Revenue', alpha=0.5, linewidth=1)
plt.plot(daily_sales['date'], daily_sales['ma_7'], label='7-Day MA', linewidth=2, color='orange')
plt.plot(daily_sales['date'], daily_sales['ma_30'], label='30-Day MA', linewidth=2, color='red')
plt.title('Revenue with Moving Averages', fontsize=14, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Revenue ($)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../analysis/moving_averages.png', dpi=300, bbox_inches='tight')
print("   ✓ Moving averages chart saved")

# ============================================================================
# 6. MACHINE LEARNING FORECASTING
# ============================================================================
print("\n6. Training forecasting models...")

# Prepare features
feature_columns = [
    'day_number', 'day_of_week', 'month', 'quarter',
    'is_weekend', 'is_month_start', 'is_month_end', 'week_of_year'
]

X = daily_sales[feature_columns]
y = daily_sales['revenue']

# Train-test split (80-20)
split_point = int(len(X) * 0.8)
X_train, X_test = X[:split_point], X[split_point:]
y_train, y_test = y[:split_point], y[split_point:]

print(f"   - Training set: {len(X_train)} days")
print(f"   - Test set: {len(X_test)} days")

# Model 1: Linear Regression
print("\n   Training Linear Regression...")
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
lr_pred_train = lr_model.predict(X_train)
lr_pred_test = lr_model.predict(X_test)

lr_mae = mean_absolute_error(y_test, lr_pred_test)
lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred_test))
lr_r2 = r2_score(y_test, lr_pred_test)

print(f"   ✓ Linear Regression Results:")
print(f"      MAE: ${lr_mae:,.2f}")
print(f"      RMSE: ${lr_rmse:,.2f}")
print(f"      R² Score: {lr_r2:.4f}")

# Model 2: Random Forest
print("\n   Training Random Forest...")
rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
rf_pred_train = rf_model.predict(X_train)
rf_pred_test = rf_model.predict(X_test)

rf_mae = mean_absolute_error(y_test, rf_pred_test)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred_test))
rf_r2 = r2_score(y_test, rf_pred_test)

print(f"   ✓ Random Forest Results:")
print(f"      MAE: ${rf_mae:,.2f}")
print(f"      RMSE: ${rf_rmse:,.2f}")
print(f"      R² Score: {rf_r2:.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n   Feature Importance (Random Forest):")
for idx, row in feature_importance.iterrows():
    print(f"      {row['feature']}: {row['importance']:.4f}")

# ============================================================================
# 7. FORECAST NEXT 30 DAYS
# ============================================================================
print("\n7. Forecasting next 30 days...")

last_date = daily_sales['date'].max()
forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=30, freq='D')

forecast_df = pd.DataFrame({
    'date': forecast_dates,
    'day_of_week': forecast_dates.dayofweek,
    'month': forecast_dates.month,
    'quarter': forecast_dates.quarter,
    'is_weekend': forecast_dates.dayofweek.isin([5, 6]).astype(int),
    'is_month_start': (forecast_dates.day <= 7).astype(int),
    'is_month_end': (forecast_dates.day >= 24).astype(int),
    'week_of_year': forecast_dates.isocalendar().week,
    'day_number': [(d - daily_sales['date'].min()).days for d in forecast_dates]
})

# Generate forecasts
forecast_df['lr_forecast'] = lr_model.predict(forecast_df[feature_columns])
forecast_df['rf_forecast'] = rf_model.predict(forecast_df[feature_columns])
forecast_df['ensemble_forecast'] = (forecast_df['lr_forecast'] + forecast_df['rf_forecast']) / 2

print(f"\n   Next 30 Days Forecast (Ensemble):")
print(f"   - Total Predicted Revenue: ${forecast_df['ensemble_forecast'].sum():,.2f}")
print(f"   - Average Daily Revenue: ${forecast_df['ensemble_forecast'].mean():,.2f}")
print(f"   - Minimum Day: ${forecast_df['ensemble_forecast'].min():,.2f}")
print(f"   - Maximum Day: ${forecast_df['ensemble_forecast'].max():,.2f}")

# ============================================================================
# 8. FORECAST VISUALIZATION
# ============================================================================
print("\n8. Creating forecast visualization...")

plt.figure(figsize=(16, 7))

# Historical data
plt.plot(daily_sales['date'], daily_sales['revenue'], 
         label='Historical Revenue', color='steelblue', linewidth=1.5)

# Forecast
plt.plot(forecast_df['date'], forecast_df['ensemble_forecast'], 
         label='Forecast (Ensemble)', color='red', linewidth=2, linestyle='--', marker='o', markersize=4)

plt.axvline(x=last_date, color='gray', linestyle=':', linewidth=2, label='Forecast Start')
plt.title('30-Day Revenue Forecast', fontsize=16, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Revenue ($)', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../analysis/revenue_forecast.png', dpi=300, bbox_inches='tight')
print("   ✓ Forecast chart saved")

# ============================================================================
# 9. EXPORT RESULTS
# ============================================================================
print("\n9. Exporting forecast results...")

# Export forecast
forecast_export = forecast_df[['date', 'lr_forecast', 'rf_forecast', 'ensemble_forecast']].copy()
forecast_export.columns = ['Date', 'Linear_Regression', 'Random_Forest', 'Ensemble_Forecast']
forecast_export.to_csv('../data/processed/revenue_forecast_30days.csv', index=False)

# Export model comparison
model_comparison = pd.DataFrame({
    'Model': ['Linear Regression', 'Random Forest'],
    'MAE': [lr_mae, rf_mae],
    'RMSE': [lr_rmse, rf_rmse],
    'R2_Score': [lr_r2, rf_r2]
})
model_comparison.to_csv('../data/processed/model_comparison.csv', index=False)

print("   ✓ Forecast exported to: ../data/processed/revenue_forecast_30days.csv")
print("   ✓ Model comparison exported")

# ============================================================================
# 10. BUSINESS INSIGHTS
# ============================================================================
print("\n" + "=" * 70)
print("FORECASTING INSIGHTS & RECOMMENDATIONS")
print("=" * 70)

current_avg = daily_sales['revenue'].tail(30).mean()
forecast_avg = forecast_df['ensemble_forecast'].mean()
change_pct = ((forecast_avg - current_avg) / current_avg) * 100

print(f"\n📊 Revenue Trend:")
print(f"   - Last 30 Days Average: ${current_avg:,.2f}")
print(f"   - Next 30 Days Forecast: ${forecast_avg:,.2f}")
print(f"   - Expected Change: {change_pct:+.2f}%")

best_day = forecast_df.loc[forecast_df['ensemble_forecast'].idxmax()]
worst_day = forecast_df.loc[forecast_df['ensemble_forecast'].idxmin()]

print(f"\n📅 Predicted Peak & Low Days:")
print(f"   - Highest Revenue: {best_day['date'].strftime('%Y-%m-%d')} (${best_day['ensemble_forecast']:,.2f})")
print(f"   - Lowest Revenue: {worst_day['date'].strftime('%Y-%m-%d')} (${worst_day['ensemble_forecast']:,.2f})")

print(f"\n💡 Recommendations:")
if change_pct > 5:
    print("   ✓ Revenue trending UP - prepare inventory for increased demand")
    print("   ✓ Consider promotional campaigns to capitalize on momentum")
elif change_pct < -5:
    print("   ⚠ Revenue trending DOWN - implement retention campaigns")
    print("   ⚠ Review pricing strategy and competitor activities")
else:
    print("   ℹ Revenue stable - maintain current strategies")
    print("   ℹ Focus on customer retention and upselling")

print("\n" + "=" * 70)
print("✓ SALES FORECASTING COMPLETE")
print("=" * 70)

plt.show()

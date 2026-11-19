"""
Customer Segmentation Analysis
Uses K-Means clustering to segment customers based on RFM metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import pyodbc

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)

# Database connection
CONNECTION_STRING = (
    'Driver={SQL Server};'
    'Server=localhost;'
    'Database=ECommerceAnalytics;'
    'Trusted_Connection=yes;'
)

print("=" * 70)
print("CUSTOMER SEGMENTATION ANALYSIS")
print("=" * 70)

# ============================================================================
# 1. EXTRACT RFM METRICS
# ============================================================================
print("\n1. Extracting RFM (Recency, Frequency, Monetary) metrics...")

query = """
SELECT 
    c.customer_id,
    c.customer_segment AS current_segment,
    c.region,
    COUNT(o.order_id) AS frequency,
    SUM(o.total) AS monetary,
    DATEDIFF(DAY, MAX(o.order_date), GETDATE()) AS recency_days,
    AVG(o.total) AS avg_order_value,
    MIN(o.order_date) AS first_purchase,
    MAX(o.order_date) AS last_purchase
FROM dim_customers c
LEFT JOIN fact_orders o ON c.customer_key = o.customer_key
    AND o.order_status NOT IN ('Cancelled', 'Returned')
GROUP BY c.customer_id, c.customer_segment, c.region
HAVING COUNT(o.order_id) > 0
"""

try:
    conn = pyodbc.connect(CONNECTION_STRING)
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"   ✓ Loaded data for {len(df)} customers")
except Exception as e:
    print(f"   ✗ Database error: {e}")
    print("\nMake sure:")
    print("   1. SQL Server is running")
    print("   2. Database and tables exist")
    print("   3. Data has been loaded")
    exit(1)

# Display basic statistics
print("\nRFM Metrics Summary:")
print(df[['recency_days', 'frequency', 'monetary']].describe())

# ============================================================================
# 2. PREPARE DATA FOR CLUSTERING
# ============================================================================
print("\n2. Preparing data for clustering...")

# Select features for clustering
features = ['recency_days', 'frequency', 'monetary', 'avg_order_value']
X = df[features].copy()

# Handle any missing values
X = X.fillna(X.median())

# Standardize features (important for K-Means)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"   ✓ Features scaled: {features}")

# ============================================================================
# 3. FIND OPTIMAL NUMBER OF CLUSTERS (ELBOW METHOD)
# ============================================================================
print("\n3. Finding optimal number of clusters...")

inertias = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

# Plot elbow curve
plt.figure(figsize=(10, 6))
plt.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
plt.xlabel('Number of Clusters (k)', fontsize=12)
plt.ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=12)
plt.title('Elbow Method: Finding Optimal K', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../analysis/elbow_curve.png', dpi=300, bbox_inches='tight')
print("   ✓ Elbow curve saved to 'elbow_curve.png'")

# ============================================================================
# 4. PERFORM K-MEANS CLUSTERING
# ============================================================================
print("\n4. Performing K-Means clustering...")

# Use 4 clusters based on business logic (can adjust based on elbow curve)
optimal_k = 4
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)

print(f"   ✓ Created {optimal_k} customer segments")

# ============================================================================
# 5. ANALYZE CLUSTERS
# ============================================================================
print("\n5. Analyzing customer segments...")

# Calculate cluster statistics
cluster_summary = df.groupby('cluster').agg({
    'customer_id': 'count',
    'recency_days': 'mean',
    'frequency': 'mean',
    'monetary': 'mean',
    'avg_order_value': 'mean'
}).round(2)

cluster_summary.columns = ['Customer Count', 'Avg Recency (days)', 
                           'Avg Frequency', 'Avg Monetary', 'Avg Order Value']

# Assign meaningful labels based on characteristics
def assign_segment_label(row):
    if row['Avg Frequency'] > df['frequency'].quantile(0.75) and \
       row['Avg Monetary'] > df['monetary'].quantile(0.75):
        return 'VIP Champions'
    elif row['Avg Frequency'] > df['frequency'].median() and \
         row['Avg Recency (days)'] < df['recency_days'].median():
        return 'Loyal Customers'
    elif row['Avg Recency (days)'] > df['recency_days'].quantile(0.75):
        return 'At Risk / Churned'
    else:
        return 'Potential Loyalists'

cluster_summary['Segment Label'] = cluster_summary.apply(assign_segment_label, axis=1)

print("\nCluster Summary:")
print(cluster_summary)

# ============================================================================
# 6. VISUALIZATIONS
# ============================================================================
print("\n6. Creating visualizations...")

# 6.1 Cluster Distribution
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Recency by Cluster
axes[0, 0].bar(cluster_summary.index, cluster_summary['Avg Recency (days)'], 
               color='steelblue', alpha=0.7)
axes[0, 0].set_xlabel('Cluster')
axes[0, 0].set_ylabel('Avg Recency (days)')
axes[0, 0].set_title('Average Recency by Cluster')
axes[0, 0].grid(axis='y', alpha=0.3)

# Frequency by Cluster
axes[0, 1].bar(cluster_summary.index, cluster_summary['Avg Frequency'], 
               color='forestgreen', alpha=0.7)
axes[0, 1].set_xlabel('Cluster')
axes[0, 1].set_ylabel('Avg Frequency')
axes[0, 1].set_title('Average Frequency by Cluster')
axes[0, 1].grid(axis='y', alpha=0.3)

# Monetary by Cluster
axes[1, 0].bar(cluster_summary.index, cluster_summary['Avg Monetary'], 
               color='coral', alpha=0.7)
axes[1, 0].set_xlabel('Cluster')
axes[1, 0].set_ylabel('Avg Monetary ($)')
axes[1, 0].set_title('Average Monetary Value by Cluster')
axes[1, 0].grid(axis='y', alpha=0.3)

# Customer Count by Cluster
axes[1, 1].bar(cluster_summary.index, cluster_summary['Customer Count'], 
               color='purple', alpha=0.7)
axes[1, 1].set_xlabel('Cluster')
axes[1, 1].set_ylabel('Customer Count')
axes[1, 1].set_title('Customer Distribution by Cluster')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('../analysis/cluster_metrics.png', dpi=300, bbox_inches='tight')
print("   ✓ Cluster metrics visualization saved")

# 6.2 Scatter Plot: Frequency vs Monetary colored by Cluster
plt.figure(figsize=(12, 8))
scatter = plt.scatter(df['frequency'], df['monetary'], 
                     c=df['cluster'], cmap='viridis', 
                     alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
plt.xlabel('Frequency (Number of Orders)', fontsize=12)
plt.ylabel('Monetary (Total Spend $)', fontsize=12)
plt.title('Customer Segmentation: Frequency vs Monetary Value', 
          fontsize=14, fontweight='bold')
plt.colorbar(scatter, label='Cluster')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../analysis/segmentation_scatter.png', dpi=300, bbox_inches='tight')
print("   ✓ Segmentation scatter plot saved")

# 6.3 3D Scatter (Recency, Frequency, Monetary)
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(df['recency_days'], df['frequency'], df['monetary'],
                    c=df['cluster'], cmap='viridis', s=50, alpha=0.6)

ax.set_xlabel('Recency (days)', fontsize=10)
ax.set_ylabel('Frequency', fontsize=10)
ax.set_zlabel('Monetary ($)', fontsize=10)
ax.set_title('3D Customer Segmentation (RFM)', fontsize=14, fontweight='bold')

plt.colorbar(scatter, label='Cluster', shrink=0.5)
plt.tight_layout()
plt.savefig('../analysis/segmentation_3d.png', dpi=300, bbox_inches='tight')
print("   ✓ 3D segmentation plot saved")

# ============================================================================
# 7. EXPORT RESULTS
# ============================================================================
print("\n7. Exporting results...")

# Add segment labels to dataframe
segment_labels = cluster_summary['Segment Label'].to_dict()
df['segment_label'] = df['cluster'].map(segment_labels)

# Export segmented customers to CSV
output_file = '../data/processed/customer_segments.csv'
df.to_csv(output_file, index=False)
print(f"   ✓ Customer segments exported to '{output_file}'")

# Export cluster summary
cluster_summary.to_csv('../data/processed/cluster_summary.csv')
print("   ✓ Cluster summary exported")

# ============================================================================
# 8. BUSINESS RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 70)
print("SEGMENTATION INSIGHTS & RECOMMENDATIONS")
print("=" * 70)

for cluster_id in sorted(df['cluster'].unique()):
    cluster_data = df[df['cluster'] == cluster_id]
    label = segment_labels[cluster_id]
    
    print(f"\n【 {label} (Cluster {cluster_id}) 】")
    print(f"   Size: {len(cluster_data)} customers ({len(cluster_data)/len(df)*100:.1f}%)")
    print(f"   Avg Recency: {cluster_data['recency_days'].mean():.0f} days")
    print(f"   Avg Frequency: {cluster_data['frequency'].mean():.1f} orders")
    print(f"   Avg Monetary: ${cluster_data['monetary'].mean():.2f}")
    
    # Recommendations based on segment
    if 'VIP' in label or 'Champion' in label:
        print("   💡 Strategy: VIP treatment, exclusive offers, loyalty rewards")
    elif 'Loyal' in label:
        print("   💡 Strategy: Upsell premium products, referral programs")
    elif 'Risk' in label or 'Churned' in label:
        print("   💡 Strategy: Win-back campaigns, personalized discounts")
    else:
        print("   💡 Strategy: Engagement campaigns, personalized recommendations")

print("\n" + "=" * 70)
print("✓ Customer Segmentation Analysis Complete")
print("=" * 70)

plt.show()

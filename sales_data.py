import pandas as pd
import numpy as np

def get_sales_data():
    """Returns a pandas DataFrame with sample sales data"""
    data = {
        'sale_id': range(1, 21),
        'product': [
            'Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Laptop',
            'Headphones', 'Mouse', 'Keyboard', 'Monitor', 'Laptop',
            'USB Cable', 'Headphones', 'Monitor', 'Keyboard', 'Mouse',
            'Laptop', 'Headphones', 'USB Cable', 'Monitor', 'Keyboard'
        ],
        'region': [
            'North', 'South', 'East', 'West', 'North',
            'South', 'East', 'West', 'North', 'South',
            'East', 'West', 'North', 'South', 'East',
            'West', 'North', 'South', 'East', 'West'
        ],
        'revenue': [
            45000, 500, 1500, 12000, 48000,
            2500, 450, 1600, 11000, 47000,
            200, 2400, 11500, 1550, 480,
            46000, 2600, 210, 12500, 1580
        ],
        'quantity': [
            1, 2, 1, 1, 1,
            1, 3, 1, 1, 1,
            4, 1, 1, 1, 2,
            1, 1, 5, 1, 1
        ]
    }
    
    df = pd.DataFrame(data)
    return df

def get_data_summary(df):
    """Generate summary statistics from the sales data"""
    summary = {
        'total_revenue': float(df['revenue'].sum()),
        'total_sales': int(len(df)),
        'average_revenue': float(df['revenue'].mean()),
        'top_product': str(df.groupby('product')['revenue'].sum().idxmax()),
        'top_product_revenue': float(df.groupby('product')['revenue'].sum().max()),
        'sales_by_region': {str(k): float(v) for k, v in df.groupby('region')['revenue'].sum().to_dict().items()},
        'products': df['product'].astype(str).unique().tolist(),
        'regions': df['region'].astype(str).unique().tolist()
    }
    return summary

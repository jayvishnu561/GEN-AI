import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.helpers import parse_date, safe_divide, calculate_days_difference

def load_supply_chain_data(file_path):
    """Load supply chain data from CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        raise Exception(f"Dataset file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading dataset: {str(e)}")

def validate_required_columns(df):
    """Validate that all required columns exist in the dataset."""
    required_columns = [
        'shipment_id', 'order_id', 'product_id', 'supplier', 'warehouse',
        'destination', 'order_date', 'ship_date', 'expected_delivery',
        'actual_delivery', 'quantity', 'inventory_level', 'reorder_point',
        'safety_stock', 'supplier_lead_time', 'actual_lead_time',
        'transport_mode', 'shipping_cost', 'distance_km', 'weather_condition', 'status'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise Exception(f"Missing required columns: {', '.join(missing_columns)}")
    
    return True

def preprocess_data(df):
    """Clean and preprocess the data."""
    df = df.copy()
    
    # Convert date columns
    date_columns = ['order_date', 'ship_date', 'expected_delivery', 'actual_delivery']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['shipment_id'], keep='first')
    
    # Handle missing values for numerical columns
    numerical_cols = ['quantity', 'inventory_level', 'reorder_point', 'safety_stock',
                      'supplier_lead_time', 'actual_lead_time', 'shipping_cost', 'distance_km']
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill with median of column if missing
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val if not pd.isna(median_val) else 0)
    
    # Ensure status is valid
    valid_statuses = ['Delivered', 'In Transit', 'Pending']
    df['status'] = df['status'].apply(lambda x: x if x in valid_statuses else 'Pending')
    
    return df

def engineer_features(df):
    """Create engineered features for analysis."""
    df = df.copy()
    
    # Delivery delay calculation
    def calculate_delay():
        delays = []
        for idx, row in df.iterrows():
            if pd.notna(row['actual_delivery']) and pd.notna(row['expected_delivery']):
                delay_days = (row['actual_delivery'] - row['expected_delivery']).days
                delays.append(delay_days)
            elif pd.isna(row['actual_delivery']) and row['status'] == 'In Transit':
                # For in-transit shipments, calculate current delay
                days_since_ship = (datetime.now() - row['ship_date']).days
                expected_days = (row['expected_delivery'] - row['ship_date']).days
                current_delay = days_since_ship - expected_days
                delays.append(max(0, current_delay))
            else:
                delays.append(0)
        return delays
    
    df['delay_days'] = calculate_delay()
    
    # Delivery delay category
    def categorize_delay(days):
        if pd.isna(days) or days is None:
            return 'Unknown'
        days = int(days)
        if days <= 0:
            return 'On Time'
        elif days <= 2:
            return 'Minor Delay'
        elif days <= 5:
            return 'Major Delay'
        else:
            return 'Critical Delay'
    
    df['delivery_delay_category'] = df['delay_days'].apply(categorize_delay)
    
    # Inventory status
    def categorize_inventory(row):
        try:
            inv = float(row['inventory_level'])
            reorder = float(row['reorder_point'])
            safety = float(row['safety_stock'])
            
            if inv < safety:
                return 'Critical'
            elif inv < reorder:
                return 'Low'
            else:
                return 'Normal'
        except:
            return 'Unknown'
    
    df['inventory_status'] = df.apply(categorize_inventory, axis=1)
    
    # Lead time deviation
    def calculate_lead_time_deviation(row):
        try:
            actual = float(row['actual_lead_time'])
            expected = float(row['supplier_lead_time'])
            if expected == 0:
                return 0
            return ((actual - expected) / expected) * 100
        except:
            return 0
    
    df['lead_time_deviation_pct'] = df.apply(calculate_lead_time_deviation, axis=1)
    
    # Cost deviation (using IQR)
    q1 = df['shipping_cost'].quantile(0.25)
    q3 = df['shipping_cost'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    df['cost_anomaly'] = df['shipping_cost'].apply(
        lambda x: 'High' if x > upper_bound else ('Low' if x < lower_bound else 'Normal')
    )
    
    # Lead time category
    def categorize_lead_time(row):
        try:
            deviation = float(row['lead_time_deviation_pct'])
            if deviation > 50:
                return 'High Deviation'
            elif deviation > 20:
                return 'Moderate Deviation'
            else:
                return 'Normal'
        except:
            return 'Unknown'
    
    df['lead_time_category'] = df.apply(categorize_lead_time, axis=1)
    
    return df

def get_supplier_stats(df):
    """Calculate supplier statistics."""
    supplier_stats = []
    
    for supplier in df['supplier'].unique():
        supplier_df = df[df['supplier'] == supplier]
        
        total_shipments = len(supplier_df)
        
        # Count delayed shipments
        delayed = supplier_df[supplier_df['delivery_delay_category'].isin(['Minor Delay', 'Major Delay', 'Critical Delay'])]
        delayed_shipments = len(delayed)
        
        on_time = len(supplier_df[supplier_df['delivery_delay_category'] == 'On Time'])
        
        on_time_pct = (on_time / total_shipments * 100) if total_shipments > 0 else 0
        
        avg_delay = supplier_df['delay_days'].mean()
        avg_lead_time = supplier_df['actual_lead_time'].mean()
        
        reliability_score = on_time_pct  # 0-100, higher is better
        
        supplier_stats.append({
            'supplier': supplier,
            'total_shipments': total_shipments,
            'delayed_shipments': delayed_shipments,
            'on_time_shipments': on_time,
            'on_time_percentage': round(on_time_pct, 2),
            'avg_delay_days': round(avg_delay, 2),
            'avg_lead_time_days': round(avg_lead_time, 2),
            'reliability_score': round(reliability_score, 2)
        })
    
    return pd.DataFrame(supplier_stats)

def get_inventory_analysis(df):
    """Analyze inventory status."""
    inventory_analysis = df.groupby(['product_id', 'warehouse']).agg({
        'inventory_level': 'first',
        'reorder_point': 'first',
        'safety_stock': 'first',
        'inventory_status': 'first'
    }).reset_index()
    
    return inventory_analysis

def clean_and_prepare_data(file_path):
    """Complete data pipeline: load, validate, clean, and engineer features."""
    df = load_supply_chain_data(file_path)
    validate_required_columns(df)
    df = preprocess_data(df)
    df = engineer_features(df)
    return df

if __name__ == "__main__":
    # Test the data processing pipeline
    df = clean_and_prepare_data('data/supply_chain_data.csv')
    print(f"Processed {len(df)} records")
    print(df.head())

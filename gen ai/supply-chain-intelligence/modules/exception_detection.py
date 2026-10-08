import pandas as pd
import numpy as np

def detect_delivery_exceptions(df):
    """Detect delivery-related exceptions."""
    exceptions = []
    
    for idx, row in df.iterrows():
        delay = row.get('delay_days', 0)
        category = row.get('delivery_delay_category', 'Unknown')
        
        if category == 'On Time':
            severity = 'None'
            points = 0
        elif category == 'Minor Delay':
            severity = 'Low'
            points = 5
        elif category == 'Major Delay':
            severity = 'Medium'
            points = 15
        elif category == 'Critical Delay':
            severity = 'High'
            points = 30
        else:
            severity = 'Unknown'
            points = 0
        
        if severity != 'None':
            exceptions.append({
                'shipment_id': row['shipment_id'],
                'exception_type': 'Delivery Delay',
                'severity': severity,
                'details': f"{category} ({int(delay)} days)",
                'risk_points': points
            })
    
    return exceptions

def detect_inventory_exceptions(df):
    """Detect inventory-related exceptions."""
    exceptions = []
    
    for idx, row in df.iterrows():
        inv_status = row.get('inventory_status', 'Normal')
        inv_level = row.get('inventory_level', 0)
        reorder = row.get('reorder_point', 0)
        safety = row.get('safety_stock', 0)
        
        if inv_status == 'Critical':
            severity = 'High'
            points = 25
            details = f"Critical: {inv_level} < Safety Stock {safety}"
        elif inv_status == 'Low':
            severity = 'Medium'
            points = 15
            details = f"Low: {inv_level} < Reorder Point {reorder}"
        else:
            severity = None
            points = 0
            details = None
        
        if severity:
            exceptions.append({
                'shipment_id': row['shipment_id'],
                'exception_type': 'Inventory Shortage',
                'severity': severity,
                'details': details,
                'risk_points': points
            })
    
    return exceptions

def detect_supplier_exceptions(df, supplier_stats):
    """Detect supplier performance exceptions."""
    exceptions = []
    
    # Identify poorly performing suppliers (< 80% on-time rate)
    poor_suppliers = supplier_stats[supplier_stats['on_time_percentage'] < 80]['supplier'].tolist()
    
    for idx, row in df.iterrows():
        supplier = row.get('supplier', '')
        
        if supplier in poor_suppliers:
            supplier_info = supplier_stats[supplier_stats['supplier'] == supplier].iloc[0]
            on_time_pct = supplier_info['on_time_percentage']
            avg_delay = supplier_info['avg_delay_days']
            
            if on_time_pct < 60:
                severity = 'High'
                points = 20
            elif on_time_pct < 80:
                severity = 'Medium'
                points = 15
            else:
                severity = 'Low'
                points = 10
            
            exceptions.append({
                'shipment_id': row['shipment_id'],
                'exception_type': 'Supplier Performance',
                'severity': severity,
                'details': f"{supplier}: {on_time_pct}% on-time, Avg Delay: {avg_delay} days",
                'risk_points': points
            })
    
    return exceptions

def detect_cost_exceptions(df):
    """Detect transportation cost anomalies."""
    exceptions = []
    
    for idx, row in df.iterrows():
        cost_anomaly = row.get('cost_anomaly', 'Normal')
        
        if cost_anomaly == 'High':
            severity = 'Medium'
            points = 10
            details = f"Shipping cost anomaly detected (high)"
        else:
            severity = None
            points = 0
            details = None
        
        if severity:
            exceptions.append({
                'shipment_id': row['shipment_id'],
                'exception_type': 'Transportation Cost',
                'severity': severity,
                'details': details,
                'risk_points': points
            })
    
    return exceptions

def detect_lead_time_exceptions(df):
    """Detect lead time anomalies."""
    exceptions = []
    
    for idx, row in df.iterrows():
        lead_time_category = row.get('lead_time_category', 'Normal')
        deviation = row.get('lead_time_deviation_pct', 0)
        
        if lead_time_category == 'High Deviation':
            severity = 'Medium'
            points = 10
            details = f"High lead time deviation: +{deviation:.1f}%"
        elif lead_time_category == 'Moderate Deviation':
            severity = 'Low'
            points = 5
            details = f"Moderate lead time deviation: +{deviation:.1f}%"
        else:
            severity = None
            points = 0
            details = None
        
        if severity:
            exceptions.append({
                'shipment_id': row['shipment_id'],
                'exception_type': 'Lead Time Deviation',
                'severity': severity,
                'details': details,
                'risk_points': points
            })
    
    return exceptions

def consolidate_exceptions(df, supplier_stats):
    """Consolidate all exceptions for each shipment."""
    exceptions_by_shipment = {}
    
    # Detect all types of exceptions
    delivery_exc = detect_delivery_exceptions(df)
    inventory_exc = detect_inventory_exceptions(df)
    supplier_exc = detect_supplier_exceptions(df, supplier_stats)
    cost_exc = detect_cost_exceptions(df)
    lead_time_exc = detect_lead_time_exceptions(df)
    
    all_exceptions = delivery_exc + inventory_exc + supplier_exc + cost_exc + lead_time_exc
    
    # Group by shipment
    for exc in all_exceptions:
        shipment_id = exc['shipment_id']
        if shipment_id not in exceptions_by_shipment:
            exceptions_by_shipment[shipment_id] = []
        exceptions_by_shipment[shipment_id].append(exc)
    
    return exceptions_by_shipment

def get_exception_summary(exceptions_by_shipment):
    """Get summary of all exceptions."""
    summary = {
        'total_shipments_with_exceptions': len(exceptions_by_shipment),
        'total_exceptions': sum(len(exc_list) for exc_list in exceptions_by_shipment.values()),
        'exception_types': {}
    }
    
    for exc_list in exceptions_by_shipment.values():
        for exc in exc_list:
            exc_type = exc['exception_type']
            summary['exception_types'][exc_type] = summary['exception_types'].get(exc_type, 0) + 1
    
    return summary

if __name__ == "__main__":
    # Test exception detection
    from data_processing import clean_and_prepare_data, get_supplier_stats
    
    df = clean_and_prepare_data('../data/supply_chain_data.csv')
    supplier_stats = get_supplier_stats(df)
    
    exceptions = consolidate_exceptions(df, supplier_stats)
    summary = get_exception_summary(exceptions)
    
    print(f"Exception Summary:")
    print(summary)

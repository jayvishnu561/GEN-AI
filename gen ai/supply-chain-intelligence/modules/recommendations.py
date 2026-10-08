import pandas as pd
import numpy as np

class RecommendationEngine:
    """Generate actionable recommendations for supply chain exceptions."""
    
    @staticmethod
    def generate_recommendations(row, risk_level):
        """Generate recommendations based on shipment data and risk level."""
        recommendations = []
        
        # Delivery delay recommendations
        delay_category = row.get('delivery_delay_category', 'On Time')
        if delay_category == 'Critical Delay':
            recommendations.append({
                'action': 'Expedite shipment immediately',
                'priority': 'URGENT',
                'reason': f"Critical delay detected ({row.get('delay_days', 0)} days). Escalate to carrier.",
                'category': 'Delivery'
            })
        elif delay_category == 'Major Delay':
            recommendations.append({
                'action': 'Contact carrier and shipper to investigate delay',
                'priority': 'HIGH',
                'reason': f"Major delay detected ({row.get('delay_days', 0)} days). Determine root cause.",
                'category': 'Delivery'
            })
        
        # Inventory recommendations
        inv_status = row.get('inventory_status', 'Normal')
        if inv_status == 'Critical':
            recommendations.append({
                'action': 'Emergency replenish inventory or transfer stock from nearby warehouse',
                'priority': 'URGENT',
                'reason': f"Critical inventory level ({row.get('inventory_level', 0)}) below safety stock ({row.get('safety_stock', 0)})",
                'category': 'Inventory'
            })
        elif inv_status == 'Low':
            recommendations.append({
                'action': 'Schedule inventory replenishment from supplier',
                'priority': 'HIGH',
                'reason': f"Inventory level ({row.get('inventory_level', 0)}) is below reorder point ({row.get('reorder_point', 0)})",
                'category': 'Inventory'
            })
        
        # Supplier recommendations (from risk scoring)
        supplier_score = row.get('supplier_score', 0)
        if supplier_score >= 15:
            recommendations.append({
                'action': 'Schedule supplier performance review meeting',
                'priority': 'HIGH',
                'reason': f"Supplier {row.get('supplier', 'Unknown')} showing poor performance metrics",
                'category': 'Supplier'
            })
        
        # Cost anomaly recommendations
        cost_anomaly = row.get('cost_anomaly', 'Normal')
        if cost_anomaly == 'High':
            recommendations.append({
                'action': 'Review transportation route and negotiate with carrier',
                'priority': 'MEDIUM',
                'reason': f"Shipping cost (${row.get('shipping_cost', 0):.2f}) is anomalously high",
                'category': 'Cost'
            })
        
        # Lead time recommendations
        lead_time_category = row.get('lead_time_category', 'Normal')
        if lead_time_category == 'High Deviation':
            recommendations.append({
                'action': 'Investigate lead time variability with supplier',
                'priority': 'MEDIUM',
                'reason': f"Lead time deviation of {row.get('lead_time_deviation_pct', 0):.1f}% detected",
                'category': 'Lead Time'
            })
        
        # ML Anomaly recommendations
        anomaly_score = row.get('anomaly_score', 0)
        if anomaly_score > 3:
            recommendations.append({
                'action': 'Investigate shipment parameters for anomalies',
                'priority': 'MEDIUM',
                'reason': 'Machine learning model detected unusual patterns in this shipment',
                'category': 'Anomaly'
            })
        
        # Overall risk level recommendations
        if risk_level == 'CRITICAL':
            recommendations.append({
                'action': 'Escalate for immediate operational review',
                'priority': 'URGENT',
                'reason': 'Critical risk level requires immediate management attention',
                'category': 'Overall'
            })
        elif risk_level == 'HIGH':
            recommendations.append({
                'action': 'Schedule for review and mitigation planning',
                'priority': 'HIGH',
                'reason': 'High risk level requires prompt attention',
                'category': 'Overall'
            })
        
        return recommendations

def get_recommendations_for_shipment(df, shipment_id):
    """Get recommendations for a specific shipment."""
    shipment = df[df['shipment_id'] == shipment_id]
    
    if shipment.empty:
        return []
    
    row = shipment.iloc[0]
    risk_level = row.get('risk_level', 'LOW')
    
    recommendations = RecommendationEngine.generate_recommendations(row, risk_level)
    
    return recommendations

def get_high_priority_actions(df, limit=10):
    """Get all high-priority or urgent actions."""
    all_actions = []
    
    for idx, row in df.iterrows():
        risk_level = row.get('risk_level', 'LOW')
        recommendations = RecommendationEngine.generate_recommendations(row, risk_level)
        
        for rec in recommendations:
            if rec['priority'] in ['URGENT', 'HIGH']:
                all_actions.append({
                    'shipment_id': row['shipment_id'],
                    'supplier': row.get('supplier', 'Unknown'),
                    'warehouse': row.get('warehouse', 'Unknown'),
                    'destination': row.get('destination', 'Unknown'),
                    'action': rec['action'],
                    'priority': rec['priority'],
                    'reason': rec['reason'],
                    'category': rec['category'],
                    'risk_score': row.get('total_risk_score', 0)
                })
    
    # Sort by priority and risk score
    priority_order = {'URGENT': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    all_actions.sort(key=lambda x: (priority_order.get(x['priority'], 4), -x['risk_score']))
    
    return all_actions[:limit]

def get_actions_by_category(df):
    """Get actions grouped by category."""
    all_actions = []
    
    for idx, row in df.iterrows():
        risk_level = row.get('risk_level', 'LOW')
        recommendations = RecommendationEngine.generate_recommendations(row, risk_level)
        
        for rec in recommendations:
            all_actions.append({
                'shipment_id': row['shipment_id'],
                'category': rec['category'],
                'action': rec['action'],
                'priority': rec['priority'],
                'reason': rec['reason']
            })
    
    # Group by category
    actions_by_category = {}
    for action in all_actions:
        category = action['category']
        if category not in actions_by_category:
            actions_by_category[category] = []
        actions_by_category[category].append(action)
    
    return actions_by_category

if __name__ == "__main__":
    # Test recommendations
    from data_processing import clean_and_prepare_data, get_supplier_stats
    from risk_scoring import calculate_risk_scores
    
    df = clean_and_prepare_data('../data/supply_chain_data.csv')
    supplier_stats = get_supplier_stats(df)
    df = calculate_risk_scores(df, supplier_stats)
    
    high_priority = get_high_priority_actions(df)
    print("High Priority Actions:")
    for action in high_priority[:5]:
        print(f"  {action['shipment_id']}: {action['action']}")

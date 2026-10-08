import pandas as pd
import numpy as np

class RiskScorer:
    """Calculate transparent risk scores for shipments."""
    
    # Scoring weights
    WEIGHTS = {
        'delivery_delay': 30,
        'inventory_shortage': 25,
        'supplier_risk': 20,
        'transportation_cost': 10,
        'lead_time_risk': 10,
        'ml_anomaly': 5
    }
    
    MAX_SCORE = 100
    
    @staticmethod
    def score_delivery_delay(row):
        """Score delivery delay (0-30 points)."""
        delay_category = row.get('delivery_delay_category', 'On Time')
        
        scores = {
            'On Time': 0,
            'Minor Delay': 5,
            'Major Delay': 15,
            'Critical Delay': 30,
            'Unknown': 0
        }
        
        return scores.get(delay_category, 0)
    
    @staticmethod
    def score_inventory_shortage(row):
        """Score inventory shortage (0-25 points)."""
        inv_status = row.get('inventory_status', 'Normal')
        
        scores = {
            'Normal': 0,
            'Low': 10,
            'Critical': 25,
            'Unknown': 0
        }
        
        return scores.get(inv_status, 0)
    
    @staticmethod
    def score_supplier_risk(row, supplier_stats_dict):
        """Score supplier performance risk (0-20 points)."""
        supplier = row.get('supplier', '')
        
        if supplier not in supplier_stats_dict:
            return 0
        
        stats = supplier_stats_dict[supplier]
        on_time_pct = stats['on_time_percentage']
        
        if on_time_pct >= 95:
            return 0
        elif on_time_pct >= 90:
            return 5
        elif on_time_pct >= 80:
            return 10
        elif on_time_pct >= 60:
            return 15
        else:
            return 20
    
    @staticmethod
    def score_transportation_cost(row, cost_lower_bound=None, cost_upper_bound=None):
        """Score transportation cost anomaly (0-10 points)."""
        cost_anomaly = row.get('cost_anomaly', 'Normal')
        
        if cost_anomaly == 'High':
            return 10
        elif cost_anomaly == 'Low':
            return 2
        else:
            return 0
    
    @staticmethod
    def score_lead_time_risk(row):
        """Score lead time deviation risk (0-10 points)."""
        lead_time_category = row.get('lead_time_category', 'Normal')
        
        scores = {
            'Normal': 0,
            'Moderate Deviation': 3,
            'High Deviation': 10,
            'Unknown': 0
        }
        
        return scores.get(lead_time_category, 0)
    
    @staticmethod
    def score_ml_anomaly(anomaly_label, anomaly_score=None):
        """Score ML-detected anomaly (0-5 points)."""
        if anomaly_label == 'Anomaly':
            if anomaly_score is not None:
                # Scale anomaly score (0-1) to 0-5 points
                return min(5, anomaly_score * 5)
            return 5
        return 0
    
    @staticmethod
    def calculate_risk_score(row, supplier_stats_dict, anomaly_label='Normal', anomaly_score=None):
        """Calculate total risk score for a shipment."""
        
        delay_score = RiskScorer.score_delivery_delay(row)
        inventory_score = RiskScorer.score_inventory_shortage(row)
        supplier_score = RiskScorer.score_supplier_risk(row, supplier_stats_dict)
        cost_score = RiskScorer.score_transportation_cost(row)
        lead_time_score = RiskScorer.score_lead_time_risk(row)
        anomaly_score_val = RiskScorer.score_ml_anomaly(anomaly_label, anomaly_score)
        
        # Calculate total
        total_risk = min(
            RiskScorer.MAX_SCORE,
            delay_score + inventory_score + supplier_score + 
            cost_score + lead_time_score + anomaly_score_val
        )
        
        return {
            'delay_score': delay_score,
            'inventory_score': inventory_score,
            'supplier_score': supplier_score,
            'cost_score': cost_score,
            'lead_time_score': lead_time_score,
            'anomaly_score': anomaly_score_val,
            'total_risk_score': round(total_risk, 2)
        }
    
    @staticmethod
    def categorize_risk(risk_score):
        """Categorize risk level based on score."""
        if risk_score <= 30:
            return 'LOW'
        elif risk_score <= 60:
            return 'MEDIUM'
        elif risk_score <= 80:
            return 'HIGH'
        else:
            return 'CRITICAL'

def calculate_risk_scores(df, supplier_stats, anomaly_labels=None, anomaly_scores=None):
    """Calculate risk scores for all shipments."""
    
    # Convert supplier stats to dict for faster lookup
    supplier_stats_dict = {}
    if not supplier_stats.empty:
        for idx, row in supplier_stats.iterrows():
            supplier_stats_dict[row['supplier']] = row.to_dict()
    
    # Initialize score columns
    score_data = []
    
    for idx, row in df.iterrows():
        anomaly_label = 'Normal'
        anomaly_score = 0
        
        if anomaly_labels is not None and idx < len(anomaly_labels):
            anomaly_label = anomaly_labels[idx]
        
        if anomaly_scores is not None and idx < len(anomaly_scores):
            anomaly_score = anomaly_scores[idx]
        
        scores = RiskScorer.calculate_risk_score(
            row, 
            supplier_stats_dict,
            anomaly_label,
            anomaly_score
        )
        
        scores['risk_level'] = RiskScorer.categorize_risk(scores['total_risk_score'])
        scores['shipment_id'] = row['shipment_id']
        
        score_data.append(scores)
    
    scores_df = pd.DataFrame(score_data)
    
    # Merge with original data
    df = df.merge(scores_df[['shipment_id', 'delay_score', 'inventory_score', 
                               'supplier_score', 'cost_score', 'lead_time_score',
                               'anomaly_score', 'total_risk_score', 'risk_level']],
                   on='shipment_id', how='left')
    
    return df

def get_risk_distribution(df):
    """Get distribution of risk levels."""
    if 'risk_level' not in df.columns:
        return None
    
    distribution = df['risk_level'].value_counts().to_dict()
    return distribution

def get_critical_shipments(df, limit=10):
    """Get critical and high-risk shipments."""
    if 'risk_level' not in df.columns:
        return pd.DataFrame()
    
    critical = df[df['risk_level'].isin(['CRITICAL', 'HIGH'])].copy()
    critical = critical.sort_values('total_risk_score', ascending=False)
    
    return critical.head(limit)

if __name__ == "__main__":
    # Test risk scoring
    from data_processing import clean_and_prepare_data, get_supplier_stats
    
    df = clean_and_prepare_data('../data/supply_chain_data.csv')
    supplier_stats = get_supplier_stats(df)
    
    df_with_scores = calculate_risk_scores(df, supplier_stats)
    
    print("Risk Score Summary:")
    print(df_with_scores[['shipment_id', 'total_risk_score', 'risk_level']].head(10))

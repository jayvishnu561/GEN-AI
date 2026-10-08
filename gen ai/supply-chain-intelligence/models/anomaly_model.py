import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os

class AnomalyDetectionModel:
    """Isolation Forest model for detecting supply chain anomalies."""
    
    def __init__(self, contamination=0.05, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.is_fitted = False
    
    def prepare_features(self, df):
        """Prepare features for anomaly detection."""
        # Select numeric features for anomaly detection
        features = ['quantity', 'shipping_cost', 'distance_km', 'actual_lead_time', 'inventory_level', 'supplier_lead_time']
        
        # Check which features exist
        available_features = [f for f in features if f in df.columns]
        
        X = df[available_features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        self.feature_names = available_features
        return X
    
    def fit(self, df):
        """Fit the Isolation Forest model on the data."""
        X = self.prepare_features(df)
        
        if len(X) == 0:
            raise ValueError("No valid data to fit model")
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples='auto'
        )
        self.model.fit(X_scaled)
        self.is_fitted = True
        
        return self
    
    def predict(self, df):
        """Predict anomalies for new data."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self.prepare_features(df)
        X = X.fillna(X.mean())
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        
        # Convert to labels: 1 = Normal, -1 = Anomaly
        anomaly_labels = ['Anomaly' if pred == -1 else 'Normal' for pred in predictions]
        
        return anomaly_labels
    
    def predict_with_scores(self, df):
        """Predict anomalies and return anomaly scores."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self.prepare_features(df)
        X = X.fillna(X.mean())
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get predictions and scores
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        # Normalize scores to 0-1 range (lower scores = more anomalous)
        # Invert so higher = more anomalous
        anomaly_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min())
        
        anomaly_labels = ['Anomaly' if pred == -1 else 'Normal' for pred in predictions]
        
        return anomaly_labels, anomaly_scores
    
    def save_model(self, file_path):
        """Save the trained model to a file."""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'contamination': self.contamination,
            'random_state': self.random_state
        }
        
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, file_path):
        """Load a trained model from a file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.contamination = model_data['contamination']
        self.random_state = model_data['random_state']
        self.is_fitted = True

def create_and_fit_model(df, contamination=0.05):
    """Create and fit anomaly detection model."""
    model = AnomalyDetectionModel(contamination=contamination)
    model.fit(df)
    return model

if __name__ == "__main__":
    # Test the model
    from data_processing import clean_and_prepare_data
    
    df = clean_and_prepare_data('../data/supply_chain_data.csv')
    model = create_and_fit_model(df)
    
    predictions = model.predict(df)
    print(f"Predictions: {len(predictions)} records")
    print(f"Anomalies found: {sum(1 for p in predictions if p == 'Anomaly')}")

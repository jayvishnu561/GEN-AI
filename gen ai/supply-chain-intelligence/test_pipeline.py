#!/usr/bin/env python
"""Test script to validate the complete pipeline"""

from modules.data_processing import clean_and_prepare_data, get_supplier_stats
from models.anomaly_model import create_and_fit_model
from modules.risk_scoring import calculate_risk_scores
from modules.exception_detection import consolidate_exceptions
import pandas as pd

print('[TEST] Loading data...')
df = clean_and_prepare_data('data/supply_chain_data.csv')
print(f'[OK] Loaded {len(df)} records')

print('[TEST] Getting supplier stats...')
supplier_stats = get_supplier_stats(df)
print(f'[OK] Analyzed {len(supplier_stats)} suppliers')

print('[TEST] Training anomaly model...')
model = create_and_fit_model(df)
anomaly_labels, anomaly_scores = model.predict_with_scores(df)
anomaly_count = sum(1 for x in anomaly_labels if x == "Anomaly")
print(f'[OK] Anomalies detected: {anomaly_count}')

print('[TEST] Calculating risk scores...')
df = calculate_risk_scores(df, supplier_stats, anomaly_labels, anomaly_scores)
print('[OK] Risk scores calculated:')
print(f'    - Critical: {len(df[df["risk_level"] == "CRITICAL"])}')
print(f'    - High: {len(df[df["risk_level"] == "HIGH"])}')
print(f'    - Medium: {len(df[df["risk_level"] == "MEDIUM"])}')
print(f'    - Low: {len(df[df["risk_level"] == "LOW"])}')

print('[TEST] Consolidating exceptions...')
exceptions = consolidate_exceptions(df, supplier_stats)
print(f'[OK] Exceptions consolidated for {len(exceptions)} shipments')

print('\n[SUCCESS] All pipeline tests passed!')
print('\nYou can now run: streamlit run app.py')

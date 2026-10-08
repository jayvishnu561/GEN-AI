import pandas as pd
import numpy as np
from datetime import datetime

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0 or pd.isna(denominator):
        return default
    return numerator / denominator

def safe_subtract(a, b, default=0):
    """Safely subtract, handling NaN values."""
    if pd.isna(a) or pd.isna(b):
        return default
    return a - b

def safe_max(values, default=0):
    """Safely get max from a list, handling empty or NaN-only lists."""
    if not values or all(pd.isna(v) for v in values):
        return default
    return np.nanmax(values)

def parse_date(date_val):
    """Parse date string or datetime object."""
    if pd.isna(date_val) or date_val is None:
        return None
    if isinstance(date_val, str):
        try:
            return pd.to_datetime(date_val)
        except:
            return None
    return date_val

def calculate_days_difference(start_date, end_date):
    """Calculate days between two dates, handling NaN values."""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    if start is None or end is None:
        return None
    
    try:
        return (end - start).days
    except:
        return None

def format_currency(value):
    """Format value as currency."""
    if pd.isna(value):
        return "$0.00"
    return f"${value:,.2f}"

def format_percentage(value):
    """Format value as percentage."""
    if pd.isna(value):
        return "0%"
    return f"{value:.1f}%"

def get_risk_color(risk_level):
    """Get color code for risk level."""
    colors = {
        'LOW': '🟢',
        'MEDIUM': '🟡',
        'HIGH': '🟠',
        'CRITICAL': '🔴'
    }
    return colors.get(risk_level, '⚪')

def get_status_icon(status):
    """Get icon for status."""
    icons = {
        'Delivered': '✅',
        'In Transit': '🚚',
        'Pending': '⏳'
    }
    return icons.get(status, '❓')

def truncate_string(s, length=50):
    """Truncate string to specified length."""
    if len(str(s)) > length:
        return str(s)[:length] + "..."
    return str(s)

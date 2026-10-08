import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from pathlib import Path

# Import custom modules
from modules.data_processing import clean_and_prepare_data, get_supplier_stats, get_inventory_analysis
from modules.exception_detection import consolidate_exceptions, get_exception_summary
from modules.risk_scoring import calculate_risk_scores, get_critical_shipments
from modules.recommendations import get_recommendations_for_shipment, get_high_priority_actions, get_actions_by_category
from modules.llm_assistant import get_llm_assistant
from models.anomaly_model import create_and_fit_model
from utils.helpers import get_risk_color, get_status_icon, format_currency, format_percentage

# ============================================================================
# PAGE CONFIGURATION & STYLING
# ============================================================================

st.set_page_config(
    page_title="Supply Chain Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    /* Global Color Palette */
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-dark: #1e40af;
        --danger: #dc2626;
        --warning: #ea580c;
        --success: #16a34a;
        --info: #0284c7;
        --light: #f8f9fa;
        --gray: #6b7280;
    }
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Section title with gradient text */
    .section-title {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 3px solid #2563eb;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        padding: 20px;
        border-radius: 12px;
        background: white;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #2563eb;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 10px;
    }
    
    .metric-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-4px);
        border-left-color: #0284c7;
    }
    
    .metric-card-critical {
        border-left-color: #dc2626;
    }
    
    .metric-card-critical:hover {
        border-left-color: #b91c1c;
    }
    
    .metric-card-high {
        border-left-color: #ea580c;
    }
    
    .metric-card-high:hover {
        border-left-color: #c2410c;
    }
    
    .metric-card-medium {
        border-left-color: #eab308;
    }
    
    .metric-card-medium:hover {
        border-left-color: #b8860b;
    }
    
    .metric-card-low {
        border-left-color: #16a34a;
    }
    
    .metric-card-low:hover {
        border-left-color: #15803d;
    }
    
    /* Risk level badges */
    .risk-critical {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        color: #7f1d1d;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
    }
    
    .risk-high {
        background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
        color: #7c2d12;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(234, 88, 12, 0.2);
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #fef08a 0%, #fde047 100%);
        color: #713f12;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(235, 179, 8, 0.2);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #15803d;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(22, 163, 74, 0.2);
    }
    
    /* Alert boxes */
    .info-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #0284c7;
        padding: 14px 16px;
        border-radius: 8px;
        color: #0c4a6e;
        margin: 10px 0;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
        border-left: 4px solid #ea580c;
        padding: 14px 16px;
        border-radius: 8px;
        color: #7c2d12;
        margin: 10px 0;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .success-box {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border-left: 4px solid #16a34a;
        padding: 14px 16px;
        border-radius: 8px;
        color: #15803d;
        margin: 10px 0;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .error-box {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 4px solid #dc2626;
        padding: 14px 16px;
        border-radius: 8px;
        color: #7f1d1d;
        margin: 10px 0;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%);
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4);
        transform: translateY(-2px);
    }
    
    /* DataFrames */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Dividers */
    .stDivider {
        margin: 20px 0;
    }
    
    /* Custom styles for headers */
    h2 {
        color: #1e293b;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    h3 {
        color: #1e293b;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

@st.cache_resource
def initialize_app():
    """Initialize the application with data."""
    data_file = 'data/supply_chain_data.csv'
    
    if not os.path.exists(data_file):
        return None, None
    
    try:
        df = clean_and_prepare_data(data_file)
        supplier_stats = get_supplier_stats(df)
        anomaly_model = create_and_fit_model(df)
        anomaly_labels, anomaly_scores = anomaly_model.predict_with_scores(df)
        df = calculate_risk_scores(df, supplier_stats, anomaly_labels, anomaly_scores)
        exceptions = consolidate_exceptions(df, supplier_stats)
        
        return df, {
            'supplier_stats': supplier_stats,
            'exceptions': exceptions,
            'anomaly_model': anomaly_model
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

df, metadata = initialize_app()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%); 
                padding: 24px; border-radius: 12px; margin-bottom: 25px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 28px; font-weight: 700;">🚚</h1>
        <h2 style="margin: 10px 0 0 0; font-size: 20px; font-weight: 700;">Supply Chain</h2>
        <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9; font-weight: 500;">Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation
    st.markdown("**📍 Navigation**")
    page = st.radio(
        "Select Page:",
        ["📊 Overview", "🚨 Exceptions", "🚛 Shipments", "📦 Inventory", 
         "🏭 Suppliers", "🗺️ Map", "🤖 AI Assistant", "📈 Analytics"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # System Status
    st.markdown("**⚙️ System Status**")
    if df is not None and not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Shipments", f"{len(df):,}")
        with col2:
            critical_count = len(df[df['risk_level'] == 'CRITICAL'])
            st.metric("Critical Alerts", critical_count)
        
        # Last updated
        st.markdown(f"""
        <div class="info-box">
        ✅ <b>Status:</b> All systems operational<br>
        📅 <b>Last Updated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================

def page_overview():
    st.markdown('<div class="section-title">📊 Supply Chain Overview</div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown("""
        <div class="error-box">
        <b>⚠️ No Data Available</b><br>
        Please ensure data/supply_chain_data.csv exists in the data directory.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # KPI Cards
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    total_shipments = len(df)
    exceptions_count = len(df[df['risk_level'].isin(['HIGH', 'CRITICAL'])])
    critical_count = len(df[df['risk_level'] == 'CRITICAL'])
    avg_delay = df['delay_days'].mean()
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Total Shipments</p>
                    <h3 style="margin: 8px 0 0 0; font-size: 36px; color: #2563eb; font-weight: 700;">{total_shipments:,}</h3>
                </div>
                <div style="font-size: 48px;">📦</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card metric-card-high">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Active Exceptions</p>
                    <h3 style="margin: 8px 0 0 0; font-size: 36px; color: #ea580c; font-weight: 700;">{exceptions_count}</h3>
                </div>
                <div style="font-size: 48px;">🚨</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card metric-card-critical">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Critical Shipments</p>
                    <h3 style="margin: 8px 0 0 0; font-size: 36px; color: #dc2626; font-weight: 700;">{critical_count}</h3>
                </div>
                <div style="font-size: 48px;">🔴</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Average Delay</p>
                    <h3 style="margin: 8px 0 0 0; font-size: 36px; color: #2563eb; font-weight: 700;">{avg_delay:.1f}d</h3>
                </div>
                <div style="font-size: 48px;">⏰</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional metrics
    st.markdown("### Additional Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    inventory_critical = len(df[df['inventory_status'] == 'Critical'])
    high_cost = len(df[df['cost_anomaly'] == 'High'])
    in_transit = len(df[df['status'] == 'In Transit'])
    delivered = len(df[df['status'] == 'Delivered'])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card metric-card-critical">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Inventory Risks</p>
            <h4 style="margin: 10px 0 0 0; font-size: 32px; color: #dc2626; font-weight: 700;">{inventory_critical}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card metric-card-medium">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Cost Anomalies</p>
            <h4 style="margin: 10px 0 0 0; font-size: 32px; color: #eab308; font-weight: 700;">{high_cost}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">In Transit</p>
            <h4 style="margin: 10px 0 0 0; font-size: 32px; color: #0284c7; font-weight: 700;">{in_transit}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card metric-card-low">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Delivered</p>
            <h4 style="margin: 10px 0 0 0; font-size: 32px; color: #16a34a; font-weight: 700;">{delivered}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("### Data Visualization")
    col1, col2 = st.columns(2)
    
    with col1:
        status_dist = df['status'].value_counts()
        fig = px.pie(values=status_dist.values, names=status_dist.index, 
                     title="Shipment Status Distribution",
                     color_discrete_sequence=['#16a34a', '#0284c7', '#ea580c'])
        fig.update_traces(textposition='inside', textinfo='percent+label', 
                         textfont=dict(size=12))
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0),
                         font=dict(family="sans-serif", size=11))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        risk_dist = df['risk_level'].value_counts()
        colors = {'CRITICAL': '#dc2626', 'HIGH': '#ea580c', 'MEDIUM': '#eab308', 'LOW': '#16a34a'}
        fig = px.pie(values=risk_dist.values, names=risk_dist.index,
                     title="Risk Level Distribution",
                     color_discrete_map=colors)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                         textfont=dict(size=12))
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0),
                         font=dict(family="sans-serif", size=11))
        st.plotly_chart(fig, use_container_width=True)
    
    # Delivery and Inventory
    col1, col2 = st.columns(2)
    
    with col1:
        delay_dist = df['delivery_delay_category'].value_counts()
        fig = px.bar(x=delay_dist.index, y=delay_dist.values,
                     title="Delivery Performance",
                     labels={'x': 'Category', 'y': 'Count'},
                     color_discrete_sequence=['#16a34a', '#0284c7', '#ea580c', '#dc2626'])
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0), 
                         showlegend=False, font=dict(family="sans-serif", size=11))
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        inventory_dist = df['inventory_status'].value_counts()
        fig = px.bar(x=inventory_dist.index, y=inventory_dist.values,
                     title="Inventory Status",
                     labels={'x': 'Status', 'y': 'Count'},
                     color_discrete_sequence=['#16a34a', '#eab308', '#dc2626'])
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0), 
                         showlegend=False, font=dict(family="sans-serif", size=11))
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
        st.plotly_chart(fig, use_container_width=True)
    
    # Supplier Performance
    st.markdown("### Top Supplier Performance")
    if metadata:
        supplier_stats = metadata['supplier_stats']
        top_suppliers = supplier_stats.nlargest(5, 'on_time_percentage')
        
        fig = px.bar(top_suppliers, x='supplier', y='on_time_percentage',
                     title="Top 5 Suppliers by On-Time Performance",
                     labels={'supplier': 'Supplier', 'on_time_percentage': 'On-Time %'},
                     color='on_time_percentage',
                     color_continuous_scale=['#dc2626', '#eab308', '#16a34a'],
                     range_color=[0, 100])
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0),
                         font=dict(family="sans-serif", size=11))
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
        st.plotly_chart(fig, use_container_width=True)


def page_exceptions():
    st.markdown('<div class="section-title">🚨 Supply Chain Exceptions</div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown("<div class='error-box'>No data available</div>", unsafe_allow_html=True)
        return
    
    # Filters
    st.markdown("### Filter Options")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_filter = st.multiselect("Risk Level", df['risk_level'].unique(), 
                                    default=df['risk_level'].unique(),
                                    key="risk_filter")
    with col2:
        delivery_filter = st.multiselect("Delivery Status", df['delivery_delay_category'].unique(), 
                                        default=df['delivery_delay_category'].unique(),
                                        key="delivery_filter")
    with col3:
        supplier_filter = st.multiselect("Supplier", df['supplier'].unique(), 
                                        default=df['supplier'].unique()[:3],
                                        key="supplier_filter")
    with col4:
        warehouse_filter = st.multiselect("Warehouse", df['warehouse'].unique(), 
                                         default=df['warehouse'].unique(),
                                         key="warehouse_filter")
    
    filtered_df = df[
        (df['risk_level'].isin(risk_filter)) &
        (df['delivery_delay_category'].isin(delivery_filter)) &
        (df['supplier'].isin(supplier_filter)) &
        (df['warehouse'].isin(warehouse_filter))
    ]
    
    # Statistics
    st.markdown("### Exception Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Exceptions Found</p>
            <h3 style="margin: 10px 0 0 0; font-size: 36px; color: #2563eb; font-weight: 700;">{len(filtered_df)}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        critical = len(filtered_df[filtered_df['risk_level'] == 'CRITICAL'])
        st.markdown(f"""
        <div class="metric-card metric-card-critical">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Critical</p>
            <h3 style="margin: 10px 0 0 0; font-size: 36px; color: #dc2626; font-weight: 700;">{critical}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        high = len(filtered_df[filtered_df['risk_level'] == 'HIGH'])
        st.markdown(f"""
        <div class="metric-card metric-card-high">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">High Risk</p>
            <h3 style="margin: 10px 0 0 0; font-size: 36px; color: #ea580c; font-weight: 700;">{high}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Details
    st.markdown("### Exception Details")
    display_df = filtered_df[[
        'shipment_id', 'order_id', 'supplier', 'warehouse', 'destination',
        'delivery_delay_category', 'delay_days', 'inventory_status', 'total_risk_score', 'risk_level'
    ]].copy()
    
    display_df.columns = ['Shipment ID', 'Order ID', 'Supplier', 'Warehouse', 'Destination',
                          'Delay Category', 'Delay (Days)', 'Inventory', 'Risk Score', 'Risk Level']
    
    display_df['Risk Score'] = display_df['Risk Score'].apply(lambda x: f"{x:.1f}")
    display_df['Delay (Days)'] = display_df['Delay (Days)'].apply(lambda x: f"{int(x)}")
    
    st.dataframe(display_df, use_container_width=True)
    
    # Download
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Exception Report",
        data=csv,
        file_name=f"exceptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def page_shipments():
    st.markdown('<div class="section-title">🚛 Shipment Management</div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown("<div class='error-box'>No data available</div>", unsafe_allow_html=True)
        return
    
    st.markdown("### Search & Filter")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_shipment = st.text_input("🔍 Search by Shipment ID or Order ID")
    with col2:
        sort_by = st.selectbox("Sort By", ['Delay Days', 'Risk Score', 'Cost', 'Date Created'])
    
    search_df = df.copy()
    if search_shipment:
        search_df = search_df[
            (search_df['shipment_id'].str.contains(search_shipment, case=False)) |
            (search_df['order_id'].str.contains(search_shipment, case=False))
        ]
    
    if sort_by == 'Delay Days':
        search_df = search_df.sort_values('delay_days', ascending=False)
    elif sort_by == 'Risk Score':
        search_df = search_df.sort_values('total_risk_score', ascending=False)
    elif sort_by == 'Cost':
        search_df = search_df.sort_values('total_cost', ascending=False)
    
    # Statistics
    st.markdown("### Shipment Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Total Shipments</p>
            <h3 style="margin: 10px 0 0 0; font-size: 32px; color: #2563eb; font-weight: 700;">{len(search_df)}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_value = search_df['total_cost'].sum()
        st.markdown(f"""
        <div class="metric-card metric-card-low">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Total Value</p>
            <h3 style="margin: 10px 0 0 0; font-size: 32px; color: #16a34a; font-weight: 700;">${total_value:,.0f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_days = search_df['delay_days'].mean()
        st.markdown(f"""
        <div class="metric-card metric-card-high">
            <p style="margin: 0; font-size: 13px; color: #888; font-weight: 500;">Avg Delay</p>
            <h3 style="margin: 10px 0 0 0; font-size: 32px; color: #ea580c; font-weight: 700;">{avg_days:.1f}d</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Table
    st.markdown("### Shipment Details")
    display_df = search_df[[
        'shipment_id', 'order_id', 'supplier', 'destination', 'status',
        'scheduled_delivery_date', 'delay_days', 'total_cost', 'total_risk_score', 'risk_level'
    ]].copy().head(100)
    
    display_df.columns = ['Shipment ID', 'Order ID', 'Supplier', 'Destination', 'Status',
                          'Scheduled Delivery', 'Delay (Days)', 'Cost', 'Risk Score', 'Risk Level']
    
    display_df['Cost'] = display_df['Cost'].apply(lambda x: f"${x:,.0f}")
    display_df['Risk Score'] = display_df['Risk Score'].apply(lambda x: f"{x:.1f}")
    display_df['Delay (Days)'] = display_df['Delay (Days)'].apply(lambda x: f"{int(x)}")
    
    st.dataframe(display_df, use_container_width=True)


def page_inventory():
    st.markdown('<div class="section-title">📦 Inventory Management</div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown("<div class='error-box'>No data available</div>", unsafe_allow_html=True)
        return
    
    col1, col2 = st.columns(2)
    with col1:
        inventory_analysis = get_inventory_analysis(df)
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888;">Critical Inventory</p>
            <h3 style="margin: 10px 0 0 0; font-size: 28px; color: #dc2626;">{len(df[df['inventory_status'] == 'Critical'])}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888;">Low Inventory</p>
            <h3 style="margin: 10px 0 0 0; font-size: 28px; color: #eab308;">{len(df[df['inventory_status'] == 'Low'])}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Inventory Status Distribution")
    inventory_dist = df['inventory_status'].value_counts()
    fig = px.bar(x=inventory_dist.index, y=inventory_dist.values,
                 title="Inventory Levels",
                 color_discrete_sequence=['#16a34a', '#eab308', '#dc2626'])
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def page_suppliers():
    st.markdown('<div class="section-title">🏭 Supplier Performance</div>', unsafe_allow_html=True)
    
    if df is None or df.empty or not metadata:
        st.markdown("<div class='error-box'>No data available</div>", unsafe_allow_html=True)
        return
    
    supplier_stats = metadata['supplier_stats']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888;">Total Suppliers</p>
            <h3 style="margin: 10px 0 0 0; font-size: 28px; color: #2563eb;">{len(supplier_stats)}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_performance = supplier_stats['on_time_percentage'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888;">Avg Performance</p>
            <h3 style="margin: 10px 0 0 0; font-size: 28px; color: #16a34a;">{avg_performance:.1f}%</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        worst_supplier = supplier_stats.nsmallest(1, 'on_time_percentage')
        st.markdown(f"""
        <div class="metric-card metric-card-critical">
            <p style="margin: 0; font-size: 13px; color: #888;">Worst Performer</p>
            <h3 style="margin: 10px 0 0 0; font-size: 18px; color: #dc2626;">{worst_supplier.iloc[0]['supplier']}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Supplier Performance Analysis")
    fig = px.bar(supplier_stats.sort_values('on_time_percentage', ascending=False), 
                 x='supplier', y='on_time_percentage',
                 title="On-Time Delivery Performance by Supplier",
                 color='on_time_percentage',
                 color_continuous_scale=['#dc2626', '#ea580c', '#eab308', '#16a34a'],
                 range_color=[0, 100])
    fig.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)


def page_map():
    st.markdown('<div class="section-title">🗺️ Supply Chain Map</div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown("<div class='error-box'>Map visualization requires geographic data</div>", unsafe_allow_html=True)
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888;">Unique Routes</p>
            <h3 style="margin: 10px 0 0 0; font-size: 28px; color: #2563eb;">{df[['warehouse', 'destination']].drop_duplicates().shape[0]}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_distance = df['distance_km'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0; font-size: 13px; color: #888;">Avg Distance</p>
            <h3 style="margin: 10px 0 0 0; font-size: 28px; color: #2563eb;">{avg_distance:.0f} km</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("📍 Interactive map visualization would go here with shipment routes and locations")


def page_ai_assistant():
    st.markdown('<div class="section-title">🤖 AI Assistant</div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown("<div class='error-box'>No data available</div>", unsafe_allow_html=True)
        return
    
    st.markdown("### Ask a Question About Your Supply Chain")
    
    llm_assistant = get_llm_assistant()
    user_question = st.text_area("Your Question:", height=100)
    
    if st.button("🔍 Get Analysis", use_container_width=True):
        if user_question:
            with st.spinner("Analyzing..."):
                response = llm_assistant.analyze_supply_chain_question(user_question, df)
                st.markdown(f"""
                <div class="info-box">
                <b>📊 Analysis:</b><br>
                {response}
                </div>
                """, unsafe_allow_html=True)


def page_analytics():
    st.markdown('<div class="section-title">📈 Advanced Analytics</div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown("<div class='error-box'>No data available</div>", unsafe_allow_html=True)
        return
    
    tab1, tab2, tab3 = st.tabs(["Risk Analysis", "Delay Analysis", "Cost Analysis"])
    
    with tab1:
        st.markdown("### Risk Score Distribution")
        fig = px.histogram(df, x='total_risk_score', nbins=20, 
                          title="Risk Score Distribution",
                          color_discrete_sequence=['#2563eb'])
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Delay Days Analysis")
        fig = px.box(df, y='delay_days', 
                     title="Delay Days Distribution",
                     color_discrete_sequence=['#ea580c'])
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Cost Analysis")
        fig = px.scatter(df, x='total_cost', y='total_risk_score',
                        title="Cost vs Risk Score",
                        color='risk_level',
                        color_discrete_map={'CRITICAL': '#dc2626', 'HIGH': '#ea580c', 
                                           'MEDIUM': '#eab308', 'LOW': '#16a34a'})
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE ROUTER
# ============================================================================

if page == "📊 Overview":
    page_overview()
elif page == "🚨 Exceptions":
    page_exceptions()
elif page == "🚛 Shipments":
    page_shipments()
elif page == "📦 Inventory":
    page_inventory()
elif page == "🏭 Suppliers":
    page_suppliers()
elif page == "🗺️ Map":
    page_map()
elif page == "🤖 AI Assistant":
    page_ai_assistant()
elif page == "📈 Analytics":
    page_analytics()

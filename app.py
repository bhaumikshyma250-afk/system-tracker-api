# dashboard/app.py

import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import time
import psutil

# Page Configuration
st.set_page_config(
    page_title="AuraMonitor System Tracker",
    page_icon="🚀",
    layout="wide"
)

# Real-time auto-refresh every 2 seconds
st_autorefresh(interval=2000, limit=None, key="datarefresh")

# Session State Initialization for Interactive Cards
if 'active_view' not in st.session_state:
    st.session_state.active_view = 'overview'

# Ultra-Modern Custom CSS Styling
st.markdown("""
    <style>
    .main {
        background: #090d16;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(31, 41, 55, 0.7) 0%, rgba(17, 24, 39, 0.9) 100%);
        border: 1px solid rgba(75, 85, 99, 0.4);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 13px;
        color: #94a3b8;
        letter-spacing: 1px;
        margin-bottom: 6px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 26px;
        color: #f8fafc;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    /* Attractive Control Panel Box */
    .control-panel-box {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.6) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        margin-top: 30px;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Database Path
DB_PATH = os.path.join(os.path.dirname(__file__), 'tracker_data.db')

def load_data(query):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def clear_database():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activity_logs")
        cursor.execute("DELETE FROM network_logs")
        cursor.execute("DELETE FROM uptime_logs")
        conn.commit()
        conn.close()

# Header Section
st.title("🚀 AuraMonitor System Intelligence Dashboard")
st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Interactive real-time telemetry dashboard. Click the metric cards below to filter specific views.</p>", unsafe_allow_html=True)
st.markdown("---")

# Fetch Data
activity_df = load_data("SELECT * FROM activity_logs ORDER BY id DESC")
network_df = load_data("SELECT * FROM network_logs ORDER BY id DESC")
uptime_df = load_data("SELECT * FROM uptime_logs ORDER BY id DESC")

# Calculate Metrics & Uptime
total_logs = len(activity_df)
total_data = network_df['mb_used'].sum() if not network_df.empty and 'mb_used' in network_df.columns else 0.0
unique_apps = activity_df['app_name'].nunique() if not activity_df.empty else 0

# Calculate System Uptime String
boot_timestamp = psutil.boot_time()
uptime_seconds = time.time() - boot_timestamp
uptime_hours = int(uptime_seconds // 3600)
uptime_mins = int((uptime_seconds % 3600) // 60)
uptime_str = f"{uptime_hours}h {uptime_mins}m"

# Interactive Metric Cards Layout with 4 Columns (Including Uptime)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Activity Logs</div>
            <div class="metric-value">{total_logs}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Inspect Activity", use_container_width=True):
        st.session_state.active_view = 'logs'

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Bandwidth Consumed</div>
            <div class="metric-value">{total_data:.2f} MB</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🌐 Inspect Bandwidth", use_container_width=True):
        st.session_state.active_view = 'network'

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Unique Apps</div>
            <div class="metric-value">{unique_apps}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("📱 Inspect Apps", use_container_width=True):
        st.session_state.active_view = 'apps'

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">System Uptime</div>
            <div class="metric-value">{uptime_str}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⏱️ Inspect Uptime", use_container_width=True):
        st.session_state.active_view = 'uptime'

st.markdown("<br>", unsafe_allow_html=True)

# Dynamic Display Based on Clicked Card (Toggle views)
if st.session_state.active_view == 'overview':
    # Default view showing both charts
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("🍩 App Share & Distribution")
        if not activity_df.empty:
            app_time = activity_df.groupby('app_name')['duration_sec'].sum().reset_index()
            app_time['time_spent_min'] = round(app_time['duration_sec'] / 60, 2)
            fig_app = px.pie(
                app_time.head(6), names='app_name', values='time_spent_min', hole=0.6,
                template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_app.update_traces(textposition='inside', textinfo='percent+label')
            fig_app.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
            st.plotly_chart(fig_app, use_container_width=True)
        else:
            st.info("Awaiting live activity logs...")

    with c_right:
        st.subheader("📈 Live Bandwidth Stream")
        if not network_df.empty:
            fig_net = px.area(
                network_df.tail(100), x='timestamp', y='mb_used',
                template="plotly_dark", color_discrete_sequence=['#6366f1']
            )
            fig_net.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_net, use_container_width=True)
        else:
            st.info("Awaiting live network metrics...")

elif st.session_state.active_view == 'logs':
    st.subheader("💻 Detailed Activity Logs Inspection")
    if st.button("⬅️ Back to Overview"):
        st.session_state.active_view = 'overview'
        st.rerun()
    if not activity_df.empty:
        st.dataframe(activity_df, use_container_width=True)
    else:
        st.warning("No activity records available.")

elif st.session_state.active_view == 'network':
    st.subheader("🌐 Detailed Bandwidth & Network Logs Inspection")
    if st.button("⬅️ Back to Overview"):
        st.session_state.active_view = 'overview'
        st.rerun()
    if not network_df.empty:
        st.dataframe(network_df, use_container_width=True)
    else:
        st.warning("No network records available.")

elif st.session_state.active_view == 'apps':
    st.subheader("📱 Unique Applications Analysis")
    if st.button("⬅️ Back to Overview"):
        st.session_state.active_view = 'overview'
        st.rerun()
    if not activity_df.empty:
        unique_app_df = activity_df[['app_name']].drop_duplicates().reset_index(drop=True)
        st.dataframe(unique_app_df, use_container_width=True)
    else:
        st.warning("No unique apps found.")

elif st.session_state.active_view == 'uptime':
    st.subheader("⏱️ System Uptime History Inspection")
    if st.button("⬅️ Back to Overview"):
        st.session_state.active_view = 'overview'
        st.rerun()
    st.markdown(f"### Current Active Session Uptime: {uptime_str}")
    if not uptime_df.empty:
        st.dataframe(uptime_df, use_container_width=True)
    else:
        st.warning("No uptime records available.")

# Bottom Section - Clean & Professional Control Panel
st.markdown("---")
st.subheader("🎛️ System Database Control Center")
st.markdown("<p style='color: #94a3b8; font-size: 14px;'>Manage and purge stored telemetry logs safely from the local SQLite database.</p>", unsafe_allow_html=True)

col_b1, col_b2 = st.columns([1, 2])

with col_b1:
    if st.button("🗑️ Wipe All Database Logs", use_container_width=True, type="primary"):
        clear_database()
        st.success("All database logs cleared successfully!")
        st.rerun()


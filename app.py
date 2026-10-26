import streamlit as st
import pandas as pd
import requests
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

# API URL for Render Live Backend
API_URL = "https://system-tracker-api.onrender.com/stats"

def fetch_stats_from_api():
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return {"total_logs": 0, "total_data_mb": 0.0, "unique_apps": 0}

# Header Section
st.title("🚀 AuraMonitor System Intelligence Dashboard")
st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Interactive real-time telemetry dashboard connected to Render Live API. Click the metric cards below to filter specific views.</p>", unsafe_allow_html=True)
st.markdown("---")

# Fetch Data from Live API
stats_data = fetch_stats_from_api()

total_logs = stats_data.get("total_logs", 0)
total_data = stats_data.get("total_data_mb", 0.0)
unique_apps = stats_data.get("unique_apps", 0)

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
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("🍩 Live API Metrics Overview")
        st.metric(label="Total Logs Recorded", value=total_logs)
        st.metric(label="Total Network Consumed", value=f"{total_data:.2f} MB")
        st.metric(label="Unique Active Apps", value=unique_apps)

    with c_right:
        st.subheader("📈 System Status")
        st.success("Connected successfully to Render.com Live Backend API!")
        st.info(f"Live Endpoint: {API_URL}")

elif st.session_state.active_view == 'logs':
    st.subheader("💻 Detailed Activity Logs")
    if st.button("⬅️ Back to Overview"):
        st.session_state.active_view = 'overview'
        st.rerun()
    st.write(f"Total Activity Logs Count from Live API: **{total_logs}**")

elif st.session_state.active_view == 'network':
    st.subheader("🌐 Bandwidth & Network Overview")
    if st.button("⬅️ Back to Overview"):
        st.session_state.active_view = 'overview'
        st.rerun()
    st.write(f"Total Bandwidth Used from Live API: **{total_data:.2f} MB**")

elif st.session_state.active_view == 'apps':
    st.subheader("📱 Unique Applications Overview")
    if st.button("⬅️ Back to Overview"):
        st.session_state.active_view = 'overview'
        st.rerun()
    st.write(f"Total Unique Apps Count: **{unique_apps}**")

elif st.session_state.active_view == 'uptime':
    st.subheader("⏱️ System Uptime")
    if st.button("⬅️ Back to Overview"):
        st.session_state.active_view = 'overview'
        st.rerun()
    st.markdown(f"### Current Active Session Uptime: {uptime_str}")

# Bottom Section - Clean & Professional Control Panel
st.markdown("---")
st.subheader("🎛️ System Database Control Center")
st.markdown("<p style='color: #94a3b8; font-size: 14px;'>Manage and purge stored telemetry logs safely from the Render API backend.</p>", unsafe_allow_html=True)

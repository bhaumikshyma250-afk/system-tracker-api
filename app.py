import os
import sqlite3
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psutil
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------------- page setup
st.set_page_config(page_title="Laptop Logbook", page_icon="📓", layout="wide")
st_autorefresh(interval=5000, limit=None, key="datarefresh")

# Palette
PAPER = "#EAF0EC"
GRID = "#CBD8D0"
INK = "#14213D"
MUTED = "#5B6B66"
COBALT = "#2F4BFF"
MARK = "#FFE45C"
CORAL = "#E5484D"
APP_COLORS = ["#2F4BFF", "#14213D", "#E5484D", "#1F9D8A", "#8A5CF6", "#C99A06", "#6B7C93"]

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Source+Sans+3:wght@400;600&display=swap');

.stApp {{
    background-color: {PAPER};
    background-image:
        linear-gradient({GRID} 1px, transparent 1px),
        linear-gradient(90deg, {GRID} 1px, transparent 1px);
    background-size: 28px 28px;
    color: {INK};
    font-family: 'Source Sans 3', sans-serif;
}}
header[data-testid="stHeader"], footer, #MainMenu {{ visibility: hidden; height: 0; }}
.block-container {{ max-width: 1150px; padding-top: 2.2rem; }}

h1, h2, h3, .lb-display {{
    font-family: 'Bricolage Grotesque', sans-serif !important;
    color: {INK} !important;
    letter-spacing: -0.02em;
}}

/* Title */
.lb-title {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: clamp(2.4rem, 6vw, 4rem);
    line-height: 1;
    margin: 0;
    color: {INK};
}}
.lb-title span {{
    background: linear-gradient(transparent 55%, {MARK} 55%);
    padding: 0 .12em;
}}
.lb-sub {{ color: {MUTED}; margin: .6rem 0 1.6rem; font-size: 1.05rem; max-width: 60ch; }}

/* "Right now" strip */
.lb-now {{
    background: {INK};
    color: {PAPER};
    padding: 1.4rem 1.6rem;
    border-radius: 4px 22px 4px 22px;
    margin-bottom: 1.6rem;
}}
.lb-now small {{ color: #9FB0C8; font-size: .95rem; }}
.lb-now .app {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: clamp(1.8rem, 4.5vw, 2.8rem);
    line-height: 1.1;
    margin: .2rem 0;
}}
.lb-now .win {{ color: #D6DEEA; font-size: 1.05rem; overflow-wrap: anywhere; }}

/* Figures row (no cards, ruled columns) */
.lb-fig {{ border-left: 3px solid {INK}; padding: .1rem 0 .1rem .9rem; margin-bottom: 1rem; }}
.lb-fig .n {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 2.1rem;
    line-height: 1.1;
    color: {INK};
}}
.lb-fig .l {{ color: {MUTED}; font-size: .98rem; }}

/* Tabs */
div[data-baseweb="tab-list"] {{ gap: 1.4rem; border-bottom: 2px solid {INK}; }}
button[data-baseweb="tab"] {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: {MUTED};
    background: transparent;
    padding: .5rem 0;
}}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {INK}; }}
div[data-baseweb="tab-highlight"] {{ background-color: {MARK} !important; height: 6px !important; }}

/* Chart + table frames */
.lb-note {{ color: {MUTED}; font-size: .98rem; margin: -.2rem 0 .6rem; }}
div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] {{
    background: rgba(255,255,255,.72);
    border: 2px solid {INK};
    border-radius: 4px 14px 4px 14px;
    padding: .4rem;
}}

/* Buttons */
.stButton > button {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    border: 2px solid {INK};
    border-radius: 4px 12px 4px 12px;
    background: {MARK};
    color: {INK};
}}
.stButton > button:hover {{ background: {INK}; color: {PAPER}; border-color: {INK}; }}
.stButton > button:focus-visible {{ outline: 3px solid {COBALT}; outline-offset: 2px; }}
.lb-danger {{ border-top: 2px dashed {CORAL}; margin-top: 2.2rem; padding-top: 1rem; }}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- data layer
DB_PATH = os.path.join(os.path.dirname(__file__), "tracker_data.db")


def load_data(query: str) -> pd.DataFrame:
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def clear_database():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        for table in ("activity_logs", "network_logs", "uptime_logs"):
            cur.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.close()


def chart_layout(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Source Sans 3, sans-serif", color=INK, size=14),
        margin=dict(t=16, b=16, l=8, r=16),
        legend=dict(orientation="h", y=-0.2),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, linecolor=INK)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, linecolor=INK)
    return fig


activity_df = load_data("SELECT * FROM activity_logs ORDER BY id DESC")
network_df = load_data("SELECT * FROM network_logs ORDER BY id DESC")
uptime_df = load_data("SELECT * FROM uptime_logs ORDER BY id DESC")

if not activity_df.empty:
    activity_df["timestamp"] = pd.to_datetime(activity_df["timestamp"])
if not network_df.empty:
    network_df["timestamp"] = pd.to_datetime(network_df["timestamp"])

total_logs = len(activity_df)
total_mb = float(network_df["mb_used"].sum()) if not network_df.empty else 0.0
unique_apps = int(activity_df["app_name"].nunique()) if not activity_df.empty else 0
active_min = float(activity_df["duration_sec"].sum() / 60) if not activity_df.empty else 0.0

up_sec = time.time() - psutil.boot_time()
uptime_str = f"{int(up_sec // 3600)}h {int((up_sec % 3600) // 60)}m"

# ---------------------------------------------------------------- header
st.markdown('<p class="lb-title">Laptop <span>Logbook</span></p>', unsafe_allow_html=True)
st.markdown(
    '<p class="lb-sub">What the laptop was doing, which apps got the time, and how much data went through.</p>',
    unsafe_allow_html=True,
)

# Right-now strip: the most recent record
if not activity_df.empty:
    last = activity_df.iloc[0]
    st.markdown(
        f"""
        <div class="lb-now">
            <small>Last thing recorded, {last['timestamp']:%d %b %Y, %H:%M:%S}</small>
            <div class="app">{last['app_name']}</div>
            <div class="win">{last['window_title'] or ''}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="lb-now"><div class="app">Nothing recorded yet</div>'
        '<div class="win">Start the tracker and entries will show up here.</div></div>',
        unsafe_allow_html=True,
    )

# Figures
figs = [
    (f"{total_logs}", "log entries"),
    (f"{total_mb:.2f} MB", "data used"),
    (f"{unique_apps}", "different apps"),
    (uptime_str, "this machine has been up"),
]
for col, (num, label) in zip(st.columns(4), figs):
    col.markdown(
        f'<div class="lb-fig"><div class="n">{num}</div><div class="l">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------------- tabs
tab_over, tab_act, tab_net, tab_apps, tab_up = st.tabs(
    ["Overview", "Activity", "Network", "Apps", "Uptime"]
)

with tab_over:
    st.subheader("Day strip")
    st.markdown('<p class="lb-note">Each bar is a stretch of time spent in one app.</p>', unsafe_allow_html=True)
    if not activity_df.empty:
        strip = activity_df.head(300).copy()
        strip["end"] = strip["timestamp"] + pd.to_timedelta(strip["duration_sec"], unit="s")
        fig_tl = px.timeline(
            strip, x_start="timestamp", x_end="end", y="app_name", color="app_name",
            color_discrete_sequence=APP_COLORS,
        )
        fig_tl.update_yaxes(autorange="reversed", title=None)
        fig_tl.update_xaxes(title=None)
        fig_tl.update_layout(showlegend=False)
        st.plotly_chart(chart_layout(fig_tl, 320), use_container_width=True)
    else:
        st.info("No activity yet.")

    left, right = st.columns(2)
    with left:
        st.subheader("Minutes per app")
        if not activity_df.empty:
            per_app = (
                activity_df.groupby("app_name")["duration_sec"].sum().div(60).round(1)
                .sort_values().tail(8).reset_index(name="minutes")
            )
            fig_bar = px.bar(per_app, x="minutes", y="app_name", orientation="h",
                             color_discrete_sequence=[COBALT])
            fig_bar.update_yaxes(title=None)
            fig_bar.update_xaxes(title="minutes")
            st.plotly_chart(chart_layout(fig_bar), use_container_width=True)
        else:
            st.info("No activity yet.")
    with right:
        st.subheader("Data over time")
        if not network_df.empty:
            net = network_df.sort_values("timestamp").tail(150)
            fig_net = go.Figure(go.Scatter(
                x=net["timestamp"], y=net["mb_used"], mode="lines",
                line=dict(color=INK, width=2, shape="spline"),
                fill="tozeroy", fillcolor="rgba(255,228,92,0.55)",
            ))
            fig_net.update_yaxes(title="MB per reading")
            st.plotly_chart(chart_layout(fig_net), use_container_width=True)
        else:
            st.info("No network data yet.")

with tab_act:
    st.subheader("All activity entries")
    if not activity_df.empty:
        st.dataframe(activity_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity records.")

with tab_net:
    st.subheader("Network readings")
    if not network_df.empty:
        st.dataframe(network_df, use_container_width=True, hide_index=True)
    else:
        st.info("No network records.")

with tab_apps:
    st.subheader("Apps seen so far")
    if not activity_df.empty:
        apps = (
            activity_df.groupby("app_name")
            .agg(entries=("id", "count"), minutes=("duration_sec", lambda s: round(s.sum() / 60, 1)),
                 last_seen=("timestamp", "max"))
            .sort_values("minutes", ascending=False).reset_index()
        )
        st.dataframe(apps, use_container_width=True, hide_index=True)
    else:
        st.info("No apps recorded.")

with tab_up:
    st.subheader("Uptime")
    st.markdown(f'<p class="lb-note">This machine has been running for {uptime_str}.</p>', unsafe_allow_html=True)
    if not uptime_df.empty:
        st.dataframe(uptime_df, use_container_width=True, hide_index=True)
    else:
        st.info("No uptime records.")

# ---------------------------------------------------------------- danger zone
st.markdown('<div class="lb-danger"></div>', unsafe_allow_html=True)
st.subheader("Clear the logbook")
st.markdown('<p class="lb-note">This deletes every stored log. It cannot be undone.</p>', unsafe_allow_html=True)
sure = st.checkbox("I understand, delete everything")
if st.button("Delete all logs", disabled=not sure):
    clear_database()
    st.success("All logs deleted.")
    st.rerun()

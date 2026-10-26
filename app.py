
import os
import sqlite3
import time
import pandas as pd
import plotly.express as px
import psutil
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="AuraMonitor System Tracker",
    page_icon="🚀",
    layout="wide",
)

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "tracker_data.db",
)

REFRESH_INTERVAL = 2000  # 2 seconds

# ==================== AUTO REFRESH ====================

st_autorefresh(
    interval=REFRESH_INTERVAL,
    limit=None,
    key="datarefresh",
)


# ==================== SESSION STATE ====================

if "active_view" not in st.session_state:
    st.session_state.active_view = "overview"

if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

# ==================== CUSTOM CSS ====================

st.markdown(
    """
    <style>
    .stApp {
        background: #090d16;
    }

    .metric-card {
        background: linear-gradient(
            135deg,
            rgba(31, 41, 55, 0.8),
            rgba(17, 24, 39, 0.95)
        );
        border: 1px solid rgba(99, 102, 241, 0.35);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        text-align: center;
        margin-bottom: 10px;
        min-height: 110px;
    }

    .metric-title {
        font-size: 13px;
        color: #94a3b8;
        letter-spacing: 1px;
        margin-bottom: 10px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .metric-value {
        font-size: 26px;
        color: #c4b5fd;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    h1, h2, h3 {
        color: #ffffff !important;
    }

    [data-testid="stMetricValue"] {
        color: #c4b5fd;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================== DATABASE HELPERS ====================

TABLES = ("activity_logs", "network_logs", "uptime_logs")


def get_connection():
    """Open the existing database without creating a new empty one."""
    if not os.path.isfile(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA query_only = ON")
    return conn


def load_data(table):
    """Safely load records from a known database table."""
    if table not in TABLES:
        return pd.DataFrame()

    conn = get_connection()

    if conn is None:
        return pd.DataFrame()

    try:
        tables_df = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """,
            conn,
        )

        if table not in tables_df["name"].tolist():
            return pd.DataFrame()

        df = pd.read_sql_query(
            f'SELECT * FROM "{table}" ORDER BY id DESC',
            conn,
        )

        return df

    except (sqlite3.Error, pd.errors.DatabaseError) as exc:
        st.error(f"Could not read {table}: {exc}")
        return pd.DataFrame()

    finally:
        conn.close()


def clear_database():
    """Delete log records from existing log tables only."""
    if not os.path.isfile(DB_PATH):
        return False, "Database file does not exist."

    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            existing = {
                row[0]
                for row in conn.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                    """
                ).fetchall()
            }

            for table in TABLES:
                if table in existing:
                    conn.execute(f'DELETE FROM "{table}"')

        return True, "Existing database logs cleared successfully."

    except sqlite3.Error as exc:
        return False, f"Database error: {exc}"


# ==================== LOAD LIVE DATA ====================

activity_df = load_data("activity_logs")
network_df = load_data("network_logs")
uptime_df = load_data("uptime_logs")


# ==================== METRICS ====================

total_logs = len(activity_df)

total_data = 0.0
if not network_df.empty and "mb_used" in network_df.columns:
    total_data = pd.to_numeric(
        network_df["mb_used"], errors="coerce"
    ).fillna(0).sum()

unique_apps = (
    activity_df["app_name"].nunique()
    if not activity_df.empty and "app_name" in activity_df.columns
    else 0
)

boot_timestamp = psutil.boot_time()
uptime_seconds = max(0, int(time.time() - boot_timestamp))

uptime_hours = uptime_seconds // 3600
uptime_mins = (uptime_seconds % 3600) // 60
uptime_str = f"{uptime_hours}h {uptime_mins}m"


# ==================== HEADER ====================

st.title("🚀 AuraMonitor System Intelligence Dashboard")

st.markdown(
    """
    <p style="color:#94a3b8;font-size:16px;">
    Real-time telemetry dashboard with automatic database refresh.
    </p>
    """,
    unsafe_allow_html=True,
)

st.caption(
    f"Refresh interval: 2 seconds | "
    f"Last dashboard refresh: {time.strftime('%H:%M:%S')}"
)

if not os.path.isfile(DB_PATH):
    st.warning(
        "Database file not found. Start your data collection script "
        "and verify the tracker_data.db path."
    )

st.divider()


# ==================== METRIC CARDS ====================

col1, col2, col3, col4 = st.columns(4)


def metric_card(column, title, value, button_label, view):
    with column:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            button_label,
            key=f"button_{view}",
            use_container_width=True,
        ):
            st.session_state.active_view = view
            st.rerun()


metric_card(
    col1, "Total Activity Logs", f"{total_logs:,}",
    "🔍 Inspect Activity", "logs"
)

metric_card(
    col2, "Bandwidth Consumed", f"{total_data:.2f} MB",
    "🌐 Inspect Bandwidth", "network"
)

metric_card(
    col3, "Active Unique Apps", f"{unique_apps:,}",
    "📱 Inspect Apps", "apps"
)

metric_card(
    col4, "System Uptime", uptime_str,
    "⏱️ Inspect Uptime", "uptime"
)


# ==================== NAVIGATION ====================

view = st.session_state.active_view

if view != "overview":
    if st.button("⬅️ Back to Overview", key="back_overview"):
        st.session_state.active_view = "overview"
        st.rerun()


# ==================== OVERVIEW CHARTS ====================

if view == "overview":
    c_left, c_right = st.columns(2)

    with c_left:
        st.subheader("🍩 App Share & Distribution")

        if (
            not activity_df.empty
            and {"app_name", "duration_sec"}.issubset(activity_df.columns)
        ):
            app_time = activity_df[["app_name", "duration_sec"]].copy()

            app_time["duration_sec"] = pd.to_numeric(
                app_time["duration_sec"], errors="coerce"
            ).fillna(0)

            app_time = (
                app_time.groupby("app_name", as_index=False)["duration_sec"]
                .sum()
                .sort_values("duration_sec", ascending=False)
                .head(6)
            )

            app_time["time_spent_min"] = (
                app_time["duration_sec"] / 60
            ).round(2)

            if app_time["time_spent_min"].sum() > 0:
                fig_app = px.pie(
                    app_time,
                    names="app_name",
                    values="time_spent_min",
                    hole=0.6,
                    template="plotly_dark",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )

                fig_app.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                )

                fig_app.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=20, l=20, r=20),
                    showlegend=False,
                )

                st.plotly_chart(
                    fig_app,
                    use_container_width=True,
                    key="app_distribution_chart",
                )
            else:
                st.info("No app duration data available yet.")
        else:
            st.info(
                "Waiting for activity logs with app_name "
                "and duration_sec columns..."
            )

    with c_right:
        st.subheader("📈 Live Bandwidth Stream")

        if (
            not network_df.empty
            and {"timestamp", "mb_used"}.issubset(network_df.columns)
        ):
            chart_df = network_df[["timestamp", "mb_used"]].copy()

            chart_df["mb_used"] = pd.to_numeric(
                chart_df["mb_used"], errors="coerce"
            )

            chart_df = chart_df.dropna(subset=["mb_used"])

            chart_df["timestamp"] = pd.to_datetime(
                chart_df["timestamp"], errors="coerce"
            )

            chart_df = (
                chart_df.dropna(subset=["timestamp"])
                .sort_values("timestamp")
                .tail(100)
            )

            if not chart_df.empty:
                fig_net = px.area(
                    chart_df,
                    x="timestamp",
                    y="mb_used",
                    template="plotly_dark",
                    color_discrete_sequence=["#818cf8"],
                    labels={
                        "timestamp": "Time",
                        "mb_used": "Data Used (MB)",
                    },
                )

                fig_net.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=20, l=20, r=20),
                )

                st.plotly_chart(
                    fig_net,
                    use_container_width=True,
                    key="bandwidth_chart",
                )
            else:
                st.info("Waiting for valid timestamp and bandwidth values.")
        else:
            st.info(
                "Waiting for network logs with timestamp "
                "and mb_used columns..."
            )


# ==================== ACTIVITY LOGS ====================

elif view == "logs":
    st.subheader("💻 Detailed Activity Logs")

    if not activity_df.empty:
        st.dataframe(activity_df, use_container_width=True)
    else:
        st.warning("No activity records available.")


# ==================== NETWORK LOGS ====================

elif view == "network":
    st.subheader("🌐 Bandwidth & Network Logs")

    if not network_df.empty:
        st.dataframe(network_df, use_container_width=True)
    else:
        st.warning("No network records available.")


# ==================== APPLICATIONS ====================

elif view == "apps":
    st.subheader("📱 Unique Applications Analysis")

    if not activity_df.empty and "app_name" in activity_df.columns:
        unique_app_df = (
            activity_df[["app_name"]]
            .dropna()
            .drop_duplicates()
            .reset_index(drop=True)
        )

        st.dataframe(unique_app_df, use_container_width=True)
    else:
        st.warning("No application records available.")


# ==================== UPTIME HISTORY ====================

elif view == "uptime":
    st.subheader("⏱️ System Uptime History")

    st.markdown(f"### Current System Uptime: {uptime_str}")

    if not uptime_df.empty:
        st.dataframe(uptime_df, use_container_width=True)
    else:
        st.warning("No uptime history records available.")


# ==================== DATABASE CONTROL ====================

st.divider()

st.subheader("🎛️ System Database Control Center")

st.caption(
    "Delete stored log records from the local SQLite database."
)

if st.button(
    "🗑️ Wipe All Database Logs",
    use_container_width=True,
    type="primary",
):
    st.session_state.confirm_clear = True

if st.session_state.confirm_clear:
    st.warning(
        "Are you sure? This will delete the existing activity, "
        "network and uptime log records."
    )

    yes_col, no_col = st.columns(2)

    with yes_col:
        if st.button(
            "Yes, delete all logs",
            type="primary",
            use_container_width=True,
        ):
            success, message = clear_database()
            st.session_state.confirm_clear = False

            if success:
                st.success(message)
            else:
                st.error(message)

            st.rerun()

    with no_col:
        if st.button(
            "Cancel",
            use_container_width=True,
        ):
            st.session_state.confirm_clear = False
            st.rerun()

import sys
from pathlib import Path

# Add project root to sys.path so src imports work regardless of working directory
_app_dir = Path(__file__).resolve().parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

import math
import calendar
from datetime import datetime, date, timedelta
import json
import uuid
import streamlit as st
import pandas as pd
import altair as alt

from src.data.dashboard import get_dashboard_data
from src.data.strava import get_strava_media_path
from src.training.swim_workouts import (
    endurance_workout,
    tempo_workout,
    interval_workout,
    recovery_workout,
    pyramid_workout,
    format_pace,
)
from src.training.run_workouts import (
    generate_run_workout,
    get_run_pace_targets,
)
from src.analytics.running import format_run_pace
from src.training.swim_paces import swim_pace_zones
from src.training.plan_store import save_plan, get_plans, delete_plan, delete_plans_by_date, clear_plans
from src.analytics.summary import training_summary


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personal Fitness & Training Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SOOTHING NORDIC DUSK ATHLETIC DESIGN SYSTEM (CSS)
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #0C1017;
        --bg-card: #141B26;
        --bg-card-hover: #182232;
        --bg-surface-elevated: #1A2436;
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-card: #1E283A;
        --border-focus: #2DD4BF;
        
        --color-brand: #2DD4BF;
        --color-brand-glow: rgba(45, 212, 191, 0.15);
        --color-swim: #38BDF8;
        --color-ride: #34D399;
        --color-run: #FB7185;
        --color-walk: #FBBF24;
        --color-sleep: #A78BFA;
        
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #0C1017 !important;
        color: #F1F5F9;
    }

    /* Preserve Streamlit Icons */
    [data-testid="stIconMaterial"],
    [data-testid="stExpanderToggleIcon"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [class*="material-symbols"],
    [class*="material-icons"],
    [data-testid="stExpander"] svg {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }

    /* Hide Streamlit default header, decoration bar, and menus */
    [data-testid="stHeader"], header[data-testid="stHeader"] {
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    #MainMenu, footer {
        display: none !important;
    }

    /* Main Container Spacing */
    .block-container {
        padding-top: 1.4rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1550px !important;
        margin: 0 auto;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #F1F5F9 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Top Brand Header */
    .brand-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 12px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .brand-identity {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-logo-badge {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, #2DD4BF 0%, #0D9488 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        box-shadow: 0 0 16px rgba(45, 212, 191, 0.2);
    }
    .brand-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #F1F5F9;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .brand-subtitle {
        font-size: 0.76rem;
        color: #8E9DAE;
        font-weight: 500;
        margin: 0;
    }

    /* Soothing Telemetry Status Pill */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #141B26;
        border: 1px solid #1E283A;
        color: #CBD5E1;
    }
    .live-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #2DD4BF;
        box-shadow: 0 0 6px rgba(45, 212, 191, 0.6);
        display: inline-block;
    }

    /* Card Containers */
    .f-card {
        background: #141B26;
        border: 1px solid #1E283A;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: border-color 0.15s ease, background 0.15s ease;
    }
    .f-card:hover {
        border-color: #29374E;
    }

    .f-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .f-card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.05rem;
        font-weight: 700;
        color: #F1F5F9;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .f-card-subtitle {
        font-size: 0.78rem;
        color: #8E9DAE;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Unified Modern KPI Grid */
    .kpi-row-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 12px;
        margin-bottom: 18px;
    }
    .clean-kpi-card {
        background: #141B26;
        border: 1px solid #1E283A;
        border-radius: 12px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 94px;
        transition: all 0.15s ease;
    }
    .clean-kpi-card:hover {
        border-color: #29374E;
        background: #172130;
    }
    .clean-kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .clean-kpi-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #8E9DAE;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .clean-kpi-icon {
        font-size: 0.9rem;
    }
    .clean-kpi-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.45rem;
        font-weight: 700;
        color: #F1F5F9;
        line-height: 1.15;
        letter-spacing: -0.03em;
        margin: 3px 0 1px 0;
    }
    .clean-kpi-sub {
        font-size: 0.72rem;
        color: #64748B;
        font-weight: 500;
    }

    /* Sport Summary Cards */
    .sport-summary-card {
        background: #141B26;
        border: 1px solid #1E283A;
        border-radius: 12px;
        padding: 16px 18px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .sport-summary-card:hover {
        transform: translateY(-2px);
        border-color: #29374E;
    }

    /* Soothing Streamlit Tab Navigation Bar */
    [data-baseweb="tab-list"] {
        gap: 6px !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        margin-bottom: 18px !important;
    }
    [data-baseweb="tab"] {
        padding: 7px 14px !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        border-radius: 8px !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: #8E9DAE !important;
        min-height: 36px !important;
        transition: all 0.15s ease !important;
    }
    [data-baseweb="tab"]:hover {
        background: #172130 !important;
        color: #CBD5E1 !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        background: #172130 !important;
        color: #2DD4BF !important;
        border-color: #1E283A !important;
        border-bottom: 2px solid #2DD4BF !important;
    }

    /* Sport Badge Chips (Muted & Restorative) */
    .sport-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 600;
    }
    .chip-swim { background: rgba(56, 189, 248, 0.1); color: #38BDF8 !important; border: 1px solid rgba(56, 189, 248, 0.22); }
    .chip-ride { background: rgba(52, 211, 153, 0.1); color: #34D399 !important; border: 1px solid rgba(52, 211, 153, 0.22); }
    .chip-walk { background: rgba(251, 191, 36, 0.1); color: #FBBF24 !important; border: 1px solid rgba(251, 191, 36, 0.22); }
    .chip-run { background: rgba(251, 113, 133, 0.1); color: #FB7185 !important; border: 1px solid rgba(251, 113, 133, 0.22); }
    .chip-workout { background: rgba(167, 139, 250, 0.1); color: #A78BFA !important; border: 1px solid rgba(167, 139, 250, 0.22); }
    .chip-rest { background: #1E283A; color: #8E9DAE !important; }

    /* Buttons */
    button[kind="primary"], button[kind="secondary"], .stButton > button {
        min-height: 36px !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        background: #141B26 !important;
        border: 1px solid #1E283A !important;
        color: #F1F5F9 !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        border-color: #2DD4BF !important;
        color: #2DD4BF !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #141B26 !important;
        border: 1px solid #1E283A !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #1E283A !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        .kpi-row-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 8px !important;
        }
        .clean-kpi-card {
            padding: 10px 12px !important;
            min-height: 80px !important;
        }
        .clean-kpi-val {
            font-size: 1.25rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_date_clean(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(str(date_str)[:10])
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(date_str)[:10]


def format_days_ago(days):
    if days is None:
        return "—"
    if days == 0:
        return "Today"
    return f"{days}d ago"


def format_duration_hm(minutes):
    if not minutes or minutes <= 0:
        return "0m"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if hours > 0:
        return f"{hours}h {mins:02d}m"
    return f"{mins}m"


def get_sport_icon(sport):
    icons = {
        "Swim": "🏊",
        "Ride": "🚴",
        "Walk": "🚶",
        "Run": "🏃",
        "Workout": "🏋️",
    }
    return icons.get(sport, "🏅")


def get_sport_chip_class(sport):
    classes = {
        "Swim": "chip-swim",
        "Ride": "chip-ride",
        "Walk": "chip-walk",
        "Run": "chip-run",
        "Workout": "chip-workout",
    }
    return classes.get(sport, "chip-rest")


def apply_forest_chart_theme(chart, height=240):
    return (
        chart.properties(height=height)
        .configure_axis(
            labelColor="#8E9DAE",
            titleColor="#8E9DAE",
            labelFontSize=10,
            titleFontSize=11,
            titleFontWeight="normal",
            gridColor="rgba(255, 255, 255, 0.04)",
            domainColor="#1E283A",
            tickColor="#1E283A",
        )
        .configure_legend(
            labelColor="#CBD5E1",
            titleColor="#8E9DAE",
            labelFontSize=10,
            titleFontSize=11,
        )
        .configure_view(
            strokeWidth=0
        )
    )


def calculate_sport_recovery_metric(sport_name, days_ago, acute_load, recent_dist_km, wellness):
    sleep_score = wellness.get("sleepScore") if isinstance(wellness, dict) else None
    hrv = wellness.get("hrv") if isinstance(wellness, dict) else None
    rhr = wellness.get("restingHR") if isinstance(wellness, dict) else None

    bio_mod = 0
    if sleep_score is not None:
        if sleep_score >= 80:
            bio_mod += 6
        elif sleep_score >= 65:
            bio_mod += 0
        elif sleep_score >= 50:
            bio_mod -= 12
        else:
            bio_mod -= 22

    if hrv is not None:
        if hrv >= 60:
            bio_mod += 5
        elif hrv < 45:
            bio_mod -= 10

    if rhr is not None and rhr > 65:
        bio_mod -= 5

    if days_ago == 0:
        if (acute_load or 0) > 50 or (recent_dist_km or 0) > 3.0:
            base_readiness = 40
            status_text = "Trained Today"
        else:
            base_readiness = 58
            status_text = "Trained Today"
    elif days_ago == 1:
        base_readiness = 78
        status_text = "Recovering"
    elif days_ago in (2, 3):
        base_readiness = 95
        status_text = "Optimal"
    elif days_ago in (4, 5, 6):
        base_readiness = 90
        status_text = "Ready"
    elif days_ago is not None and days_ago >= 7:
        base_readiness = max(65, 85 - (days_ago - 7) * 2)
        status_text = "Resting"
    else:
        base_readiness = 85
        status_text = "Ready"

    final_readiness = max(15, min(100, int(base_readiness + bio_mod)))
    return {
        "readiness_pct": final_readiness,
        "status_text": status_text,
    }


def get_set_badge_meta(purpose):
    pur = (purpose or "").lower()
    if "warm" in pur:
        return {"bg": "rgba(56, 189, 248, 0.1)", "border": "rgba(56, 189, 248, 0.22)", "color": "#38BDF8", "tag": "WARM-UP"}
    elif any(k in pur for k in ["tech", "drill", "rotation", "kick", "pull"]):
        return {"bg": "rgba(167, 139, 250, 0.1)", "border": "rgba(167, 139, 250, 0.22)", "color": "#A78BFA", "tag": "TECHNIQUE"}
    elif any(k in pur for k in ["speed", "interval", "vo2", "sprint"]):
        return {"bg": "rgba(251, 113, 133, 0.1)", "border": "rgba(251, 113, 133, 0.22)", "color": "#FB7185", "tag": "SPEED"}
    elif any(k in pur for k in ["tempo", "threshold", "pace"]):
        return {"bg": "rgba(251, 191, 36, 0.1)", "border": "rgba(251, 191, 36, 0.22)", "color": "#FBBF24", "tag": "TEMPO"}
    elif any(k in pur for k in ["recovery", "easy", "relax"]):
        return {"bg": "rgba(45, 212, 191, 0.1)", "border": "rgba(45, 212, 191, 0.22)", "color": "#2DD4BF", "tag": "RECOVERY"}
    elif any(k in pur for k in ["cool", "down"]):
        return {"bg": "rgba(148, 163, 184, 0.1)", "border": "rgba(148, 163, 184, 0.22)", "color": "#94A3B8", "tag": "COOL-DOWN"}
    else:
        return {"bg": "rgba(45, 212, 191, 0.1)", "border": "rgba(45, 212, 191, 0.22)", "color": "#2DD4BF", "tag": "ENDURANCE"}


# ============================================================
# TOP BRAND COMMAND HEADER & CONTROLS
# ============================================================

today_date = date.today()
now_hour = datetime.now().hour
is_night_cutoff = now_hour >= 21

top_c1, top_c2, top_c3 = st.columns([5, 3, 3])

with top_c1:
    st.markdown(
        """
        <div class="brand-identity">
            <div class="brand-logo-badge">⚡</div>
            <div>
                <div class="brand-title">ATHLETIC INTELLIGENCE</div>
                <div class="brand-subtitle">Garmin Forerunner 965 &amp; Strava Telemetry</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_c2:
    time_filter = st.selectbox(
        "Time Period",
        options=[
            "All Time",
            "Current Week",
            "Last Week",
            "30 Days",
            "90 Days",
            "180 Days",
            "Year to Date (2026)",
            "Custom Range",
        ],
        index=1,
        label_visibility="collapsed",
        key="top_time_filter"
    )

with top_c3:
    source_filter = st.selectbox(
        "Data Source",
        options=["all", "intervals", "strava"],
        format_func=lambda x: {
            "all": "⚡ Merged (Intervals + Strava)",
            "intervals": "🟢 Intervals.icu / Garmin",
            "strava": "🟠 Strava Archive",
        }[x],
        index=0,
        label_visibility="collapsed",
        key="top_source_filter"
    )

if time_filter == "Current Week":
    cur_week_monday = today_date - timedelta(days=today_date.weekday())
    start_date_str = str(cur_week_monday)
    end_date_str = str(today_date)
elif time_filter == "Last Week":
    cur_week_monday = today_date - timedelta(days=today_date.weekday())
    prev_week_monday = cur_week_monday - timedelta(days=7)
    prev_week_sunday = cur_week_monday - timedelta(days=1)
    start_date_str = str(prev_week_monday)
    end_date_str = str(prev_week_sunday)
elif time_filter == "30 Days":
    start_date_str = str(today_date - timedelta(days=29))
    end_date_str = str(today_date)
elif time_filter == "90 Days":
    start_date_str = str(today_date - timedelta(days=90))
    end_date_str = str(today_date)
elif time_filter == "180 Days":
    start_date_str = str(today_date - timedelta(days=180))
    end_date_str = str(today_date)
elif time_filter == "Year to Date (2026)":
    start_date_str = f"{today_date.year}-01-01"
    end_date_str = str(today_date)
elif time_filter == "All Time":
    start_date_str = "2024-01-01"
    end_date_str = str(today_date)
else:
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        s_date = st.date_input("Start Date", value=today_date - timedelta(days=30))
    with col_s2:
        e_date = st.date_input("End Date", value=today_date)
    start_date_str = str(s_date)
    end_date_str = str(e_date)


# ============================================================
# DATA CACHING & FETCHING
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def load_cached_dashboard_data(start_str, end_str, src_filter):
    return get_dashboard_data(start_str, end_str, source_filter=src_filter)


with st.spinner("Loading telemetry..."):
    data = load_cached_dashboard_data(start_date_str, end_date_str, source_filter)

activities = data.get("activities", [])
all_activities = data.get("all_activities", [])
swim_baseline = data.get("swim_baseline", [])
baseline_pace = data.get("baseline_pace", 154)
pace_zones = data.get("pace_zones", swim_pace_zones(baseline_pace))
running_baseline_pace = data.get("running_baseline_pace", 550)
running_pace_zones = data.get("running_pace_zones", [])
plan = data.get("next_swim_plan", {})
recommendation = data.get("recommendation", {})
summary = data.get("summary", {})
weekly_trends = data.get("weekly_trends", [])
wellness_records = data.get("wellness", [])
api_status = data.get("api_status", "cache")
tot_intervals = data.get("total_intervals_count", 0)
tot_strava = data.get("total_strava_count", 0)

# Check if today's swim activity is completed
today_swims = [
    a for a in all_activities
    if a.get("sport") == "Swim" and str(a.get("date", ""))[:10] == str(today_date)
]
today_swim_done = len(today_swims) > 0

show_next_day = is_night_cutoff or today_swim_done
end_val = datetime.fromisoformat(end_date_str).date()
if show_next_day:
    target_plan_date = end_val + timedelta(days=1)
    plan_timing_badge = "Tomorrow"
else:
    target_plan_date = end_val
    plan_timing_badge = "Today"

running_analytics = data.get("running_analytics", {})
cycling_analytics = data.get("cycling_analytics", {})
walking_analytics = data.get("walking_analytics", {})
sleep_analytics = data.get("sleep_analytics", {})
performance_analytics = data.get("performance_analytics", {})
personal_records = data.get("personal_records", {})

days_since_swim = data.get("days_since_swim")
days_since_ride = data.get("days_since_ride")
days_since_walk = data.get("days_since_walk")
days_since_run = data.get("days_since_run")

total_dist_all = sum(s.get("distance_km", 0) for s in summary.values())
total_time_all = sum(s.get("moving_time_min", 0) for s in summary.values())
total_load_all = sum(s.get("training_load", 0) for s in summary.values())
total_cals_all = sum(a.get("calories", 0) for a in activities if a.get("calories"))

# Status Pill Bar
st.markdown(
    f"""
    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin: 4px 0 16px 0;">
        <div class="status-pill">
            <span class="live-dot"></span> Garmin 965 Connected
        </div>
        <div class="status-pill">
            Strava: <strong>{tot_strava}</strong>
        </div>
        <div class="status-pill" style="color: #2DD4BF;">
            Activities: <strong>{len(activities)}</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# STREAMLINED NAVIGATION TABS (10 FOCUSED TABS)
# ============================================================

(
    tab_today,
    tab_overview,
    tab_swimming,
    tab_running,
    tab_cycling,
    tab_walking,
    tab_sleep,
    tab_calendar,
    tab_analytics,
    tab_settings,
) = st.tabs([
    "☀️ Today",
    "👁️ Overview",
    "🏊 Swimming",
    "🏃 Running",
    "🚴 Cycling",
    "🚶 Walking",
    "😴 Sleep & Recovery",
    "📅 Calendar & Planner",
    "📊 Analytics & Load",
    "⚙️ Settings",
])


# ============================================================
# TAB 1: ☀️ TODAY
# ============================================================

with tab_today:
    today_real_date = date.today()
    today_iso = str(today_real_date)
    today_formatted = format_date_clean(today_iso).upper()

    t_wellness = data.get("today_wellness")
    if not t_wellness:
        all_w = data.get("all_wellness", [])
        t_wellness = next((w for w in all_w if w.get("id") == today_iso or w.get("date") == today_iso), None)
        if not t_wellness and all_w:
            t_wellness = all_w[-1]

    t_sleep_sec = t_wellness.get("sleepSecs") if t_wellness else None
    t_sleep_score = t_wellness.get("sleepScore") if t_wellness else None
    t_rhr = t_wellness.get("restingHR") if t_wellness else None
    t_hrv = t_wellness.get("hrv") if t_wellness else None

    t_hours = int(t_sleep_sec // 3600) if t_sleep_sec else 0
    t_mins = int((t_sleep_sec % 3600) // 60) if t_sleep_sec else 0
    dur_display = f"{t_hours}h {t_mins:02d}m" if t_sleep_sec else "—"

    today_acts = data.get("today_activities")
    if today_acts is None:
        today_acts = [
            a for a in all_activities
            if a.get("date") and str(a["date"])[:10] == today_iso
        ]

    today_dist_all = sum(a.get("distance_km") or 0.0 for a in today_acts)
    today_time_all = sum(a.get("moving_time_min") or a.get("duration_min") or 0.0 for a in today_acts)
    today_cals_all = sum(a.get("calories") or 0 for a in today_acts)
    today_load_all = sum(a.get("training_load") or 0.0 for a in today_acts)

    # 1. Today's Readiness & Sleep Snapshot Card
    readiness_status = "Optimal" if (t_sleep_score or 75) >= 65 else "Moderate"
    readiness_color = "#2DD4BF" if (t_sleep_score or 75) >= 65 else "#FBBF24"

    st.markdown(
        f"""
        <div class="f-card" style="margin-bottom: 16px;">
            <div class="f-card-header" style="margin-bottom: 12px;">
                <div>
                    <div style="font-size: 0.72rem; font-weight: 700; color: #8E9DAE; text-transform: uppercase; letter-spacing: 0.04em;">
                        ☀️ DAILY READINESS &amp; TELEMETRY · {today_formatted}
                    </div>
                    <div class="f-card-title" style="margin-top: 2px;">
                        Today's Recovery Status: <span style="color: {readiness_color};">{readiness_status}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 6px;">
                    <span class="sport-chip chip-swim">Garmin 965</span>
                    <span class="sport-chip" style="background: rgba(45, 212, 191, 0.1); color: #2DD4BF;">{len(today_acts)} Sessions Logged</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;">
                <div class="clean-kpi-card" style="min-height: 80px; padding: 12px 14px;">
                    <div class="clean-kpi-label">🛌 Sleep Duration</div>
                    <div class="clean-kpi-val" style="font-size: 1.35rem;">{dur_display}</div>
                    <div class="clean-kpi-sub">Overnight log</div>
                </div>
                <div class="clean-kpi-card" style="min-height: 80px; padding: 12px 14px;">
                    <div class="clean-kpi-label">🎯 Sleep Score</div>
                    <div class="clean-kpi-val" style="font-size: 1.35rem; color: #38BDF8;">{f"{t_sleep_score:.0f}" if t_sleep_score else "—"}<span style="font-size: 0.8rem; color: #64748B;">/100</span></div>
                    <div class="clean-kpi-sub">Quality index</div>
                </div>
                <div class="clean-kpi-card" style="min-height: 80px; padding: 12px 14px;">
                    <div class="clean-kpi-label">💓 Overnight HRV</div>
                    <div class="clean-kpi-val" style="font-size: 1.35rem; color: #2DD4BF;">{f"{t_hrv:.0f}" if t_hrv else "—"}<span style="font-size: 0.8rem; color: #64748B;"> ms</span></div>
                    <div class="clean-kpi-sub">Autonomic tone</div>
                </div>
                <div class="clean-kpi-card" style="min-height: 80px; padding: 12px 14px;">
                    <div class="clean-kpi-label">❤️ Resting HR</div>
                    <div class="clean-kpi-val" style="font-size: 1.35rem; color: #FB7185;">{f"{t_rhr:.0f}" if t_rhr else "—"}<span style="font-size: 0.8rem; color: #64748B;"> bpm</span></div>
                    <div class="clean-kpi-sub">Basal heart rate</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Today's Completed Activity (if any)
    if today_acts:
        st.markdown("#### ⚡ Today's Completed Telemetry")
        for a in today_acts:
            sp = a.get("sport", "Workout")
            d_km = a.get("distance_km") or 0.0
            dur_m = a.get("moving_time_min") or a.get("duration_min") or 0.0
            pace_str = "—"
            if sp == "Swim" and d_km > 0 and dur_m > 0:
                p_sec = (dur_m * 60) / (d_km * 10)
                pace_str = f"{int(p_sec//60)}:{int(p_sec%60):02d} /100m"
            elif sp in ("Run", "Walk") and d_km > 0 and dur_m > 0:
                p_sec = (dur_m * 60) / d_km
                pace_str = f"{int(p_sec//60)}:{int(p_sec%60):02d} /km"
            elif sp == "Ride" and d_km > 0 and dur_m > 0:
                pace_str = f"{d_km / (dur_m / 60):.1f} km/h"

            st.markdown(
                f"""
                <div class="f-card" style="border-left: 3px solid #2DD4BF; padding: 16px 20px; margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span class="sport-chip {get_sport_chip_class(sp)}">{get_sport_icon(sp)} {sp}</span>
                            <span style="font-weight: 700; font-size: 1.05rem; color: #F1F5F9; margin-left: 6px;">{a.get('name', 'Session')}</span>
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: #CBD5E1;">
                            <strong>{d_km:.2f} km</strong> · {format_duration_hm(dur_m)} · {pace_str} · {a.get('avg_hr', '—')} bpm · Load: {a.get('training_load', 0):.0f}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 3. Today's Planned / Recommended Workout
    saved_plans_all = get_plans()
    today_scheduled = [p for p in saved_plans_all if p.get("planned_date") == today_iso]
    active_workout = today_scheduled[0] if today_scheduled else plan

    w_sport = active_workout.get("sport", "Swim")
    w_type = active_workout.get("workout_type") or active_workout.get("type", "Endurance")
    w_dist = active_workout.get("distance_m") or active_workout.get("target_distance") or (int(active_workout.get("distance_km", 5.0) * 1000))
    w_dur = active_workout.get("duration_est") or active_workout.get("duration", "45-55 min")
    w_goal = active_workout.get("goal", "Execute structured workout with consistent pacing.")
    w_sets = active_workout.get("sets", [])
    is_sched = bool(active_workout.get("planned_date"))

    st.markdown("#### 🎯 Today's Workout Focus")
    st.markdown(
        f"""
        <div class="f-card" style="border-left: 3px solid #38BDF8; margin-bottom: 16px;">
            <div class="f-card-header" style="margin-bottom: 8px;">
                <div>
                    <span class="sport-chip chip-swim">{'📅 Scheduled Plan' if is_sched else '🤖 AI Recommendation'}</span>
                    <div class="f-card-title" style="margin-top: 6px; font-size: 1.15rem;">
                        {w_type} Session · {w_dist:,}m ({w_dist // 25} Laps)
                    </div>
                </div>
                <div style="font-size: 0.82rem; color: #8E9DAE; font-weight: 600;">
                    ⏱️ {w_dur}
                </div>
            </div>
            <div style="font-size: 0.84rem; color: #94A3B8; margin-bottom: 14px;">
                <strong>Goal:</strong> {w_goal}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if w_sets:
        set_cards_html = []
        for i, s in enumerate(w_sets):
            p_text = s.get("purpose", "Swim")
            reps_cnt = s.get('reps', 1)
            dist_desc = f"{reps_cnt} × {s.get('distance')}m" if reps_cnt > 1 else f"{s.get('distance')}m"
            tot_laps = s.get('total_laps') or ((s.get('distance', 100) * reps_cnt) // 25)
            pattern_txt = s.get('stroke_pattern') or s.get('pattern') or s.get('stroke') or "Freestyle"
            target_pace = s.get('pace', 'Target Pace')
            rest_txt = s.get('rest', 'None')
            b_meta = get_set_badge_meta(p_text)

            card_item = (
                f"<div style='background: #0E141E; border: 1px solid #1E283A; border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;'>"
                f"<div>"
                f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>"
                f"<span style='font-size: 0.7rem; font-weight: 700; color: #64748B;'>SET {i+1}</span>"
                f"<span style='font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: {b_meta['bg']}; color: {b_meta['color']};'>{b_meta['tag']}</span>"
                f"</div>"
                f"<div style='font-family: JetBrains Mono, monospace; font-size: 1.1rem; font-weight: 700; color: #F1F5F9; margin-bottom: 2px;'>"
                f"{dist_desc} <span style='font-size: 0.75rem; color: #64748B;'>({tot_laps} laps)</span>"
                f"</div>"
                f"<div style='font-size: 0.78rem; color: #94A3B8; margin-bottom: 8px;'>"
                f"{pattern_txt}"
                f"</div>"
                f"</div>"
                f"<div style='border-top: 1px solid rgba(255,255,255,0.05); padding-top: 6px; font-size: 0.72rem; color: #64748B; display: flex; justify-content: space-between;'>"
                f"<span>Pace: <strong style='color: #2DD4BF;'>{target_pace}</strong></span>"
                f"<span>Rest: <strong style='color: #CBD5E1;'>{rest_txt}</strong></span>"
                f"</div>"
                f"</div>"
            )
            set_cards_html.append(card_item)

        grid_html = f"<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin-bottom: 18px;'>{''.join(set_cards_html)}</div>"
        st.markdown(grid_html, unsafe_allow_html=True)


# ============================================================
# TAB 2: 👁️ OVERVIEW
# ============================================================

with tab_overview:
    # 1. Clean KPI Strip
    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="clean-kpi-card">
                <div class="clean-kpi-top">
                    <span class="clean-kpi-label">Total Distance</span>
                    <span class="clean-kpi-icon">📍</span>
                </div>
                <div class="clean-kpi-val">{total_dist_all:.1f} <span style="font-size: 0.8rem; color: #64748B;">km</span></div>
                <div class="clean-kpi-sub">{len(activities)} total activities</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-top">
                    <span class="clean-kpi-label">Active Time</span>
                    <span class="clean-kpi-icon">⏱️</span>
                </div>
                <div class="clean-kpi-val">{total_time_all / 60:.1f} <span style="font-size: 0.8rem; color: #64748B;">hrs</span></div>
                <div class="clean-kpi-sub">{total_time_all:.0f} moving mins</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-top">
                    <span class="clean-kpi-label">Training Load</span>
                    <span class="clean-kpi-icon">⚡</span>
                </div>
                <div class="clean-kpi-val">{total_load_all:.0f}</div>
                <div class="clean-kpi-sub">ICU load accumulation</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-top">
                    <span class="clean-kpi-label">Active Energy</span>
                    <span class="clean-kpi-icon">🔥</span>
                </div>
                <div class="clean-kpi-val">{total_cals_all:,} <span style="font-size: 0.8rem; color: #64748B;">kcal</span></div>
                <div class="clean-kpi-sub">Verified energy burned</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Multi-Sport Breakdown
    swim_sum = summary.get("Swim", {})
    run_sum = summary.get("Run", {})
    ride_sum = summary.get("Ride", {})
    walk_sum = summary.get("Walk", {})

    b_speed = cycling_analytics.get("avg_speed_kmh")
    b_speed_str = f"{b_speed:.1f} km/h" if b_speed else "—"

    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 20px;">
            <div class="sport-summary-card" style="border-top: 3px solid #38BDF8;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.88rem; font-weight: 700; color: #38BDF8;">🏊 Swimming</span>
                    <span class="sport-chip chip-swim">{swim_sum.get('sessions', 0)} sessions</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 700; color: #F1F5F9;">{swim_sum.get('distance_km', 0):.2f} km</div>
                <div style="font-size: 0.76rem; color: #8E9DAE; margin-top: 4px;">{format_duration_hm(swim_sum.get('moving_time_min', 0))} · {swim_sum.get('pace_formatted', '—')} · Last: {format_days_ago(days_since_swim)}</div>
            </div>
            <div class="sport-summary-card" style="border-top: 3px solid #34D399;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.88rem; font-weight: 700; color: #34D399;">🚴 Cycling</span>
                    <span class="sport-chip chip-ride">{ride_sum.get('sessions', 0)} sessions</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 700; color: #F1F5F9;">{ride_sum.get('distance_km', 0):.2f} km</div>
                <div style="font-size: 0.76rem; color: #8E9DAE; margin-top: 4px;">{format_duration_hm(ride_sum.get('moving_time_min', 0))} · {b_speed_str} · Last: {format_days_ago(days_since_ride)}</div>
            </div>
            <div class="sport-summary-card" style="border-top: 3px solid #FB7185;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.88rem; font-weight: 700; color: #FB7185;">🏃 Running</span>
                    <span class="sport-chip chip-run">{run_sum.get('sessions', 0)} sessions</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 700; color: #F1F5F9;">{run_sum.get('distance_km', 0):.2f} km</div>
                <div style="font-size: 0.76rem; color: #8E9DAE; margin-top: 4px;">{format_duration_hm(run_sum.get('moving_time_min', 0))} · {run_sum.get('pace_formatted', '—')} · Last: {format_days_ago(days_since_run)}</div>
            </div>
            <div class="sport-summary-card" style="border-top: 3px solid #FBBF24;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.88rem; font-weight: 700; color: #FBBF24;">🚶 Walking</span>
                    <span class="sport-chip chip-walk">{walk_sum.get('sessions', 0)} sessions</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 700; color: #F1F5F9;">{walk_sum.get('distance_km', 0):.2f} km</div>
                <div style="font-size: 0.76rem; color: #8E9DAE; margin-top: 4px;">{format_duration_hm(walk_sum.get('moving_time_min', 0))} · {walking_analytics.get('avg_pace_formatted', '—')} · Last: {format_days_ago(days_since_walk)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Multi-Discipline Weekly Progression (Segmented Bar Graph)
    weekly_multi_sport = performance_analytics.get("weekly_multi_sport", [])
    st.markdown(
        """
        <div class="f-card">
            <div class="f-card-header">
                <div>
                    <div class="f-card-title">📈 Multi-Discipline Weekly Progression</div>
                    <div class="f-card-subtitle">Weekly training volume segmented by sport &amp; discipline</div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if weekly_multi_sport:
        wms_df = pd.DataFrame(weekly_multi_sport)
        wms_df = wms_df[wms_df["distance_km"] > 0]
        if not wms_df.empty:
            bars = alt.Chart(wms_df).mark_bar(
                cornerRadiusTopLeft=3,
                cornerRadiusTopRight=3,
                opacity=0.9
            ).encode(
                x=alt.X("week:N", title=None, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("distance_km:Q", title="Volume (km)", stack="zero"),
                color=alt.Color(
                    "sport:N",
                    scale=alt.Scale(
                        domain=["Swim", "Ride", "Run", "Walk", "Workout", "Other"],
                        range=["#38BDF8", "#34D399", "#FB7185", "#FBBF24", "#A78BFA", "#64748B"],
                    ),
                    legend=alt.Legend(orient="top", title=None, labelFontSize=11)
                ),
                order=alt.Order("sport:N"),
                tooltip=[
                    alt.Tooltip("week:N", title="Week"),
                    alt.Tooltip("sport:N", title="Sport"),
                    alt.Tooltip("distance_km:Q", title="Distance (km)", format=".2f"),
                    alt.Tooltip("hours:Q", title="Active Time (hrs)", format=".2f"),
                    alt.Tooltip("sessions:Q", title="Sessions"),
                    alt.Tooltip("load:Q", title="Training Load"),
                ]
            ).properties(height=240)
            st.altair_chart(apply_forest_chart_theme(bars, height=240), use_container_width=True)
        else:
            st.info("No volume trends available for the selected period.")
    elif weekly_trends:
        w_df = pd.DataFrame(weekly_trends)
        bars = alt.Chart(w_df).mark_bar(
            color="#38BDF8",
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
            opacity=0.85
        ).encode(
            x=alt.X("week:N", title=None, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("distance_km:Q", title="Volume (km)"),
            tooltip=[
                alt.Tooltip("week:N", title="Week"),
                alt.Tooltip("distance_km:Q", title="Distance (km)"),
                alt.Tooltip("sessions:Q", title="Sessions"),
            ]
        ).properties(height=240)
        st.altair_chart(apply_forest_chart_theme(bars, height=240), use_container_width=True)
    else:
        st.info("No volume trends available for the selected period.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Planned & Scheduled Sessions Management
    saved_plans_overview = get_plans()
    if saved_plans_overview:
        st.markdown(f"#### 📅 Scheduled Sessions & Planned Workouts ({len(saved_plans_overview)})")
        for p_idx, p_item in enumerate(saved_plans_overview):
            p_id = p_item.get("plan_id") or p_item.get("id") or str(uuid.uuid4())
            p_sport = p_item.get("sport", "Swim")
            p_type = p_item.get("workout_type") or p_item.get("type", "Workout")
            p_dist = p_item.get("distance_m") or p_item.get("target_distance") or (int(p_item.get("distance_km", 0) * 1000))
            p_dur = p_item.get("duration_est") or p_item.get("duration", "45-55 min")
            p_date_raw = p_item.get("planned_date") or (p_item.get("created_at") or "")[:10]
            p_date_formatted = format_date_clean(p_date_raw)
            p_goal = p_item.get("goal", "Execute structured workout with consistent pacing.")
            p_sets = p_item.get("sets", [])

            st.markdown(
                f"""
                <div class="f-card" style="border-left: 3px solid #38BDF8; margin-bottom: 10px; padding: 14px 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span class="sport-chip {get_sport_chip_class(p_sport)}">{get_sport_icon(p_sport)} {p_sport}</span>
                            <span style="font-weight: 700; font-size: 1.0rem; color: #F1F5F9; margin-left: 6px;">{p_type} Session · {p_dist:,}m</span>
                            <span style="font-size: 0.8rem; color: #8E9DAE; margin-left: 8px;">📅 {p_date_formatted}</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #8E9DAE; font-weight: 600;">
                            ⏱️ {p_dur}
                        </div>
                    </div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 6px;">
                        <strong>Goal:</strong> {p_goal}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_act1, col_act2, _ = st.columns([1.5, 2, 6])
            with col_act1:
                if st.button("🗑️ Delete Session", key=f"del_plan_ov_{p_id}_{p_idx}", use_container_width=True):
                    delete_plan(p_id)
                    st.success("Session deleted.")
                    st.rerun()
            with col_act2:
                with st.expander("🔍 View Sets", expanded=False):
                    for j, s in enumerate(p_sets):
                        st.markdown(f"- **Set {j+1}:** `{s.get('reps', 1)} × {s.get('distance', 100)}m` — `{s.get('stroke_pattern', s.get('stroke', 'Freestyle'))}` · Pace: `{s.get('pace', 'Target')}` · Rest: `{s.get('rest', 'None')}`")

        if len(saved_plans_overview) > 1:
            if st.button("🗑️ Clear All Scheduled Sessions", key="clear_all_plans_ov"):
                clear_plans()
                st.warning("All scheduled sessions cleared.")
                st.rerun()

    # 5. Recent Activities Feed
    st.markdown("#### 📋 Recent Activities Log")
    if activities:
        recent_rows = []
        for a in activities[:12]:
            sp = a.get("sport", "Other")
            d_km = a.get("distance_km") or 0.0
            dur_m = a.get("moving_time_min") or a.get("duration_min") or 0.0
            pace_speed = "—"
            if sp == "Swim" and d_km > 0 and dur_m > 0:
                p_sec = (dur_m * 60) / (d_km * 10)
                pace_speed = f"{int(p_sec//60)}:{int(p_sec%60):02d} /100m"
            elif sp in ("Run", "Walk") and d_km > 0 and dur_m > 0:
                p_sec = (dur_m * 60) / d_km
                pace_speed = f"{int(p_sec//60)}:{int(p_sec%60):02d} /km"
            elif sp == "Ride" and d_km > 0 and dur_m > 0:
                pace_speed = f"{d_km / (dur_m / 60):.1f} km/h"

            recent_rows.append({
                "Date": format_date_clean(a.get("date")),
                "Sport": f"{get_sport_icon(sp)} {sp}",
                "Activity Name": a.get("name", "Workout"),
                "Distance": f"{d_km:.2f} km" if d_km > 0 else "—",
                "Duration": format_duration_hm(dur_m),
                "Pace / Speed": pace_speed,
                "Avg HR": f"{a['avg_hr']:.0f} bpm" if a.get("avg_hr") else "—",
                "Load": f"{a['training_load']:.0f}" if a.get("training_load") else "—",
            })
        st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 3: 🏊 SWIMMING
# ============================================================

with tab_swimming:
    swim_activities = [a for a in activities if a.get("sport") == "Swim"]
    sw_dist = sum(s.get("distance_km") or 0.0 for s in swim_activities)
    sw_time = sum(s.get("moving_time_min") or 0.0 for s in swim_activities)
    sw_hrs = [s["avg_hr"] for s in swim_activities if s.get("avg_hr")]
    sw_avg_hr = round(sum(sw_hrs) / len(sw_hrs)) if sw_hrs else None

    # Swim KPIs
    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Swim Distance</div>
                <div class="clean-kpi-val" style="color: #38BDF8;">{sw_dist:.2f} <span style="font-size: 0.8rem; color: #64748B;">km</span></div>
                <div class="clean-kpi-sub">{len(swim_activities)} swim sessions</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Active Time</div>
                <div class="clean-kpi-val">{format_duration_hm(sw_time)}</div>
                <div class="clean-kpi-sub">{sw_time:.0f} moving mins</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Baseline Pace</div>
                <div class="clean-kpi-val" style="color: #2DD4BF;">{format_pace(baseline_pace)}</div>
                <div class="clean-kpi-sub">per 100m threshold</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Avg Heart Rate</div>
                <div class="clean-kpi-val">{f"{sw_avg_hr}" if sw_avg_hr else "—"} <span style="font-size: 0.8rem; color: #64748B;">bpm</span></div>
                <div class="clean-kpi-sub">underwater optical</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Active Swim Plan
    saved_plans = get_plans()
    dated_plans = [p for p in saved_plans if p.get("planned_date") and p.get("sport", "Swim") == "Swim"]
    calendar_matched_plan = next((p for p in dated_plans if p.get("planned_date") == str(target_plan_date)), None)
    active_swim_plan = calendar_matched_plan or plan

    p_type = active_swim_plan.get("workout_type") or active_swim_plan.get("type", "Endurance")
    p_dist = active_swim_plan.get("distance_m") or active_swim_plan.get("target_distance", 2000)
    p_dur = active_swim_plan.get("duration_est") or active_swim_plan.get("duration", "45-55 min")
    p_goal = active_swim_plan.get("goal", "Build aerobic endurance.")
    p_sets = active_swim_plan.get("sets", [])

    st.markdown("#### 🎯 Active Swim Workout")
    st.markdown(
        f"""
        <div class="f-card" style="border-left: 3px solid #38BDF8; margin-bottom: 16px;">
            <div class="f-card-header" style="margin-bottom: 8px;">
                <div>
                    <span class="sport-chip chip-swim">🏊 {p_type.upper()} WORKOUT</span>
                    <div class="f-card-title" style="margin-top: 6px;">{p_type} Session · {p_dist:,}m ({p_dist // 25} Laps)</div>
                </div>
                <div style="font-size: 0.84rem; color: #8E9DAE; font-weight: 600;">⏱️ {p_dur}</div>
            </div>
            <div style="font-size: 0.84rem; color: #94A3B8; margin-bottom: 12px;"><strong>Goal:</strong> {p_goal}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if p_sets:
        set_cards_html = []
        for i, s in enumerate(w_sets := p_sets):
            p_text = s.get("purpose", "Swim")
            reps_cnt = s.get('reps', 1)
            dist_desc = f"{reps_cnt} × {s.get('distance')}m" if reps_cnt > 1 else f"{s.get('distance')}m"
            tot_laps = s.get('total_laps') or ((s.get('distance', 100) * reps_cnt) // 25)
            pattern_txt = s.get('stroke_pattern') or s.get('pattern') or s.get('stroke') or "Freestyle"
            target_pace = s.get('pace', 'Target Pace')
            rest_txt = s.get('rest', 'None')
            b_meta = get_set_badge_meta(p_text)

            card_item = (
                f"<div style='background: #0E141E; border: 1px solid #1E283A; border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;'>"
                f"<div>"
                f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>"
                f"<span style='font-size: 0.7rem; font-weight: 700; color: #64748B;'>SET {i+1}</span>"
                f"<span style='font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: {b_meta['bg']}; color: {b_meta['color']};'>{b_meta['tag']}</span>"
                f"</div>"
                f"<div style='font-family: JetBrains Mono, monospace; font-size: 1.1rem; font-weight: 700; color: #F1F5F9; margin-bottom: 2px;'>"
                f"{dist_desc} <span style='font-size: 0.75rem; color: #64748B;'>({tot_laps} laps)</span>"
                f"</div>"
                f"<div style='font-size: 0.78rem; color: #94A3B8; margin-bottom: 8px;'>"
                f"{pattern_txt}"
                f"</div>"
                f"</div>"
                f"<div style='border-top: 1px solid rgba(255,255,255,0.05); padding-top: 6px; font-size: 0.72rem; color: #64748B; display: flex; justify-content: space-between;'>"
                f"<span>Pace: <strong style='color: #2DD4BF;'>{target_pace}</strong></span>"
                f"<span>Rest: <strong style='color: #CBD5E1;'>{rest_txt}</strong></span>"
                f"</div>"
                f"</div>"
            )
            set_cards_html.append(card_item)

        st.markdown(f"<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin-bottom: 20px;'>{''.join(set_cards_html)}</div>", unsafe_allow_html=True)

    # Swim Distance Progression Chart
    if swim_activities:
        sw_df_data = []
        for sa in reversed(swim_activities):
            d_val = sa.get("distance_km") or 0.0
            sw_df_data.append({
                "date": format_date_clean(sa.get("date")),
                "distance_m": int(d_val * 1000),
                "load": sa.get("training_load", 0),
            })
        c_sw_dist = alt.Chart(pd.DataFrame(sw_df_data)).mark_bar(color="#38BDF8", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("date:N", title="Date", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("distance_m:Q", title="Distance (Meters)"),
            tooltip=["date:N", "distance_m:Q", "load:Q"],
        ).properties(height=200)
        st.altair_chart(apply_forest_chart_theme(c_sw_dist, height=200), use_container_width=True)

        st.markdown("#### 📋 Swimming Session History")
        sw_table_rows = []
        for sa in swim_activities:
            d_km = sa.get("distance_km") or 0.0
            dur_m = sa.get("moving_time_min") or 0.0
            p_sec = (dur_m * 60) / (d_km * 10) if d_km > 0 and dur_m > 0 else None
            sw_table_rows.append({
                "Date": format_date_clean(sa.get("date")),
                "Session Name": sa.get("name", "Swim Session"),
                "Distance": f"{int(d_km * 1000):,} m ({d_km:.2f} km)",
                "Duration": format_duration_hm(dur_m),
                "Pace (/100m)": format_pace(p_sec) if p_sec else "—",
                "Avg HR": f"{sa.get('avg_hr', 0):.0f} bpm" if sa.get("avg_hr") else "—",
                "Load": f"{sa.get('training_load', 0):.0f}" if sa.get("training_load") else "—",
            })
        st.dataframe(pd.DataFrame(sw_table_rows), use_container_width=True, hide_index=True)

    with st.expander("🎯 5-Zone Swim Pace Guidelines (25m Pool)", expanded=False):
        z_easy = pace_zones.get("easy", {})
        z_end = pace_zones.get("endurance", {})
        z_tempo = pace_zones.get("tempo", {})
        z_int = pace_zones.get("interval", {})
        z_sprint = pace_zones.get("sprint", {})
        zone_rows = [
            {"Zone": "Zone 1 · Easy / Recovery", "Pace /100m": z_easy.get("formatted", "—"), "Purpose": z_easy.get("purpose", "Warm-up & recovery")},
            {"Zone": "Zone 2 · Aerobic Base", "Pace /100m": z_end.get("formatted", "—"), "Purpose": z_end.get("purpose", "Endurance conditioning")},
            {"Zone": "Zone 3 · Tempo", "Pace /100m": z_tempo.get("formatted", "—"), "Purpose": z_tempo.get("purpose", "Threshold speed endurance")},
            {"Zone": "Zone 4 · Threshold", "Pace /100m": z_int.get("formatted", "—"), "Purpose": z_int.get("purpose", "Speed repeats")},
            {"Zone": "Zone 5 · Sprint", "Pace /100m": z_sprint.get("formatted", "—"), "Purpose": z_sprint.get("purpose", "Max cadence & power")},
        ]
        st.dataframe(pd.DataFrame(zone_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 4: 🏃 RUNNING
# ============================================================

with tab_running:
    runs_list = running_analytics.get("runs", [])
    tot_run_dist = running_analytics.get("total_distance_km", 0.0)
    best_run_pace = running_analytics.get("fastest_pace_formatted", "—")
    longest_run = running_analytics.get("longest_run_km", 0.0)
    peak_run_hr = running_analytics.get("peak_hr")

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Run Distance</div>
                <div class="clean-kpi-val" style="color: #FB7185;">{tot_run_dist:.2f} <span style="font-size: 0.8rem; color: #64748B;">km</span></div>
                <div class="clean-kpi-sub">{len(runs_list)} completed runs</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Best Pace</div>
                <div class="clean-kpi-val">{best_run_pace}</div>
                <div class="clean-kpi-sub">fastest average pace</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Longest Run</div>
                <div class="clean-kpi-val">{longest_run:.2f} <span style="font-size: 0.8rem; color: #64748B;">km</span></div>
                <div class="clean-kpi-sub">max single session</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Peak Heart Rate</div>
                <div class="clean-kpi-val">{f"{peak_run_hr}" if peak_run_hr else "—"} <span style="font-size: 0.8rem; color: #64748B;">bpm</span></div>
                <div class="clean-kpi-sub">Garmin HR sensor</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if runs_list:
        st.markdown("#### 📋 Running History")
        run_table_rows = []
        for r in runs_list:
            run_table_rows.append({
                "Date": format_date_clean(r.get("date")),
                "Run Name": r.get("name", "Run"),
                "Distance": f"{r.get('distance_km', 0):.2f} km",
                "Duration": format_duration_hm(r.get("moving_time_min", 0)),
                "Pace (/km)": r.get("pace_formatted", "—"),
                "Avg HR": f"{r.get('avg_hr', 0):.0f} bpm" if r.get("avg_hr") else "—",
                "Load": f"{r.get('training_load', 0):.0f}" if r.get("training_load") else "—",
            })
        st.dataframe(pd.DataFrame(run_table_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No running sessions recorded during the selected period.")


# ============================================================
# TAB 5: 🚴 CYCLING
# ============================================================

with tab_cycling:
    rides_list = cycling_analytics.get("rides", [])
    tot_ride_dist = cycling_analytics.get("total_distance_km", 0.0)
    tot_ride_time = cycling_analytics.get("total_moving_min", 0.0)
    avg_ride_speed = cycling_analytics.get("avg_speed_kmh")
    tot_ride_elev = cycling_analytics.get("total_elevation_m", 0.0)

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Ride Distance</div>
                <div class="clean-kpi-val" style="color: #34D399;">{tot_ride_dist:.2f} <span style="font-size: 0.8rem; color: #64748B;">km</span></div>
                <div class="clean-kpi-sub">{len(rides_list)} rides completed</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Active Time</div>
                <div class="clean-kpi-val">{format_duration_hm(tot_ride_time)}</div>
                <div class="clean-kpi-sub">{tot_ride_time:.0f} moving mins</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Avg Speed</div>
                <div class="clean-kpi-val">{f"{avg_ride_speed:.1f}" if avg_ride_speed else "—"} <span style="font-size: 0.8rem; color: #64748B;">km/h</span></div>
                <div class="clean-kpi-sub">overall sustained</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Elevation Gain</div>
                <div class="clean-kpi-val">{tot_ride_elev:.0f} <span style="font-size: 0.8rem; color: #64748B;">m</span></div>
                <div class="clean-kpi-sub">total climbing</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if rides_list:
        st.markdown("#### 📋 Cycling History")
        r_table_rows = []
        for r in rides_list:
            r_table_rows.append({
                "Date": format_date_clean(r.get("date")),
                "Ride Name": r.get("name", "Ride"),
                "Distance": f"{r.get('distance_km', 0):.2f} km",
                "Duration": format_duration_hm(r.get("moving_time_min", 0)),
                "Avg Speed": f"{r.get('computed_speed_kmh', 0):.1f} km/h" if r.get("computed_speed_kmh") else "—",
                "Elevation": f"{r.get('elevation_m', 0):.0f} m" if r.get("elevation_m") else "—",
                "Avg HR": f"{r.get('avg_hr', 0):.0f} bpm" if r.get("avg_hr") else "—",
            })
        st.dataframe(pd.DataFrame(r_table_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No cycling sessions recorded during the selected period.")


# ============================================================
# TAB 6: 🚶 WALKING
# ============================================================

with tab_walking:
    walks_list = walking_analytics.get("walks", [])
    tot_walk_dist = walking_analytics.get("total_distance_km", 0.0)
    tot_walk_time = walking_analytics.get("total_moving_min", 0.0)
    avg_walk_pace = walking_analytics.get("avg_pace_formatted", "—")
    daily_steps_list = [w["steps"] for w in wellness_records if w.get("steps")]
    avg_steps = round(sum(daily_steps_list) / len(daily_steps_list)) if daily_steps_list else None

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Walk Distance</div>
                <div class="clean-kpi-val" style="color: #FBBF24;">{tot_walk_dist:.2f} <span style="font-size: 0.8rem; color: #64748B;">km</span></div>
                <div class="clean-kpi-sub">{len(walks_list)} recorded walks</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Active Time</div>
                <div class="clean-kpi-val">{format_duration_hm(tot_walk_time)}</div>
                <div class="clean-kpi-sub">{tot_walk_time:.0f} moving mins</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Average Pace</div>
                <div class="clean-kpi-val">{avg_walk_pace}</div>
                <div class="clean-kpi-sub">overall pace /km</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Avg Daily Steps</div>
                <div class="clean-kpi-val">{f"{avg_steps:,}" if avg_steps else "—"}</div>
                <div class="clean-kpi-sub">Garmin pedometer</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if walks_list:
        st.markdown("#### 📋 Walking History")
        w_table_rows = []
        for w in walks_list:
            w_table_rows.append({
                "Date": format_date_clean(w.get("date")),
                "Walk Name": w.get("name", "Walk"),
                "Distance": f"{w.get('distance_km', 0):.2f} km",
                "Duration": format_duration_hm(w.get("moving_time_min", 0)),
                "Pace (/km)": w.get("computed_pace_formatted", "—"),
                "Avg HR": f"{w.get('avg_hr', 0):.0f} bpm" if w.get("avg_hr") else "—",
            })
        st.dataframe(pd.DataFrame(w_table_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No walking sessions recorded during the selected period.")


# ============================================================
# TAB 7: 😴 SLEEP & RECOVERY
# ============================================================

with tab_sleep:
    sl_dur_fmt = sleep_analytics.get("avg_duration_formatted", "—")
    sl_score = sleep_analytics.get("avg_sleep_score")
    sl_hrv = sleep_analytics.get("avg_hrv")
    sl_rhr = sleep_analytics.get("avg_resting_hr")
    avg_deep = sleep_analytics.get("avg_deep_hours")
    avg_light = sleep_analytics.get("avg_light_hours")
    avg_rem = sleep_analytics.get("avg_rem_hours")

    avg_deep_fmt = format_duration_hm(avg_deep * 60) if avg_deep else "—"
    avg_light_fmt = format_duration_hm(avg_light * 60) if avg_light else "—"
    avg_rem_fmt = format_duration_hm(avg_rem * 60) if avg_rem else "—"

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Average Sleep</div>
                <div class="clean-kpi-val" style="color: #A78BFA;">{sl_dur_fmt}</div>
                <div class="clean-kpi-sub">Garmin total duration</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Deep Sleep (Physical)</div>
                <div class="clean-kpi-val" style="color: #818CF8;">{avg_deep_fmt}</div>
                <div class="clean-kpi-sub">Tissue repair &amp; recovery</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Light Sleep (Baseline)</div>
                <div class="clean-kpi-val" style="color: #60A5FA;">{avg_light_fmt}</div>
                <div class="clean-kpi-sub">Base rest &amp; transition</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">REM Sleep (Cognitive)</div>
                <div class="clean-kpi-val" style="color: #C084FC;">{avg_rem_fmt}</div>
                <div class="clean-kpi-sub">Neural restoration</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sl_trends = sleep_analytics.get("daily_trends", [])
    if sl_trends:
        stage_rows = []
        for s in sl_trends:
            if s.get("duration_hours"):
                d_str = str(s.get("date", ""))[:10]
                stage_rows.append({
                    "date": d_str,
                    "stage": "Deep Sleep",
                    "hours": s.get("deep_hours", 0.0),
                    "duration": s.get("deep_formatted", "—"),
                    "percentage": f"{s.get('deep_pct', 0)}%",
                    "total_sleep": s.get("duration_formatted", "—"),
                    "score": s.get("score"),
                    "hrv": s.get("hrv"),
                    "order": 1,
                })
                stage_rows.append({
                    "date": d_str,
                    "stage": "Light Sleep",
                    "hours": s.get("light_hours", 0.0),
                    "duration": s.get("light_formatted", "—"),
                    "percentage": f"{s.get('light_pct', 0)}%",
                    "total_sleep": s.get("duration_formatted", "—"),
                    "score": s.get("score"),
                    "hrv": s.get("hrv"),
                    "order": 2,
                })
                stage_rows.append({
                    "date": d_str,
                    "stage": "REM Sleep",
                    "hours": s.get("rem_hours", 0.0),
                    "duration": s.get("rem_formatted", "—"),
                    "percentage": f"{s.get('rem_pct', 0)}%",
                    "total_sleep": s.get("duration_formatted", "—"),
                    "score": s.get("score"),
                    "hrv": s.get("hrv"),
                    "order": 3,
                })

        if stage_rows:
            st.markdown(
                """
                <div class="f-card">
                    <div class="f-card-header">
                        <div>
                            <div class="f-card-title">🌙 Daily Sleep Stages Architecture (Garmin 965)</div>
                            <div class="f-card-subtitle">Breakdown of Deep, Light, and REM sleep cycles per night</div>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            stage_df = pd.DataFrame(stage_rows)
            c_sl_stages = alt.Chart(stage_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X("date:N", title="Date", sort=None, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("hours:Q", title="Sleep Duration (Hours)", stack="zero"),
                color=alt.Color(
                    "stage:N",
                    scale=alt.Scale(
                        domain=["Deep Sleep", "Light Sleep", "REM Sleep"],
                        range=["#4F46E5", "#60A5FA", "#A78BFA"],
                    ),
                    legend=alt.Legend(title="Stage", orient="top", labelFontSize=11)
                ),
                order=alt.Order("order:Q", sort="ascending"),
                tooltip=[
                    alt.Tooltip("date:N", title="Date"),
                    alt.Tooltip("stage:N", title="Stage"),
                    alt.Tooltip("duration:N", title="Stage Duration"),
                    alt.Tooltip("percentage:N", title="Stage %"),
                    alt.Tooltip("total_sleep:N", title="Total Sleep"),
                    alt.Tooltip("score:Q", title="Sleep Score"),
                ]
            ).properties(height=260)
            st.altair_chart(apply_forest_chart_theme(c_sl_stages, height=260), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("#### 📋 Sleep Telemetry & Stage Log")
        sl_table = []
        for st_item in reversed(sl_trends):
            if st_item.get("duration_hours") or st_item.get("resting_hr"):
                d_val = st_item.get("deep_formatted", "—")
                d_p = f" ({st_item.get('deep_pct')}%)" if st_item.get("deep_pct") is not None else ""
                l_val = st_item.get("light_formatted", "—")
                l_p = f" ({st_item.get('light_pct')}%)" if st_item.get("light_pct") is not None else ""
                r_val = st_item.get("rem_formatted", "—")
                r_p = f" ({st_item.get('rem_pct')}%)" if st_item.get("rem_pct") is not None else ""

                sl_table.append({
                    "Date": format_date_clean(st_item.get("date")),
                    "Total Sleep": st_item.get("duration_formatted", "—"),
                    "Deep Sleep": f"{d_val}{d_p}",
                    "Light Sleep": f"{l_val}{l_p}",
                    "REM Sleep": f"{r_val}{r_p}",
                    "Sleep Score": f"{st_item.get('score'):.0f} / 100" if st_item.get("score") else "—",
                    "Overnight HRV": f"{st_item.get('hrv'):.0f} ms" if st_item.get("hrv") else "—",
                    "Resting HR": f"{st_item.get('resting_hr'):.0f} bpm" if st_item.get("resting_hr") else "—",
                })
        st.dataframe(pd.DataFrame(sl_table), use_container_width=True, hide_index=True)


# ============================================================
# TAB 8: 📅 ACTIVITY CALENDAR & PLANNER
# ============================================================

with tab_calendar:
    saved_plans_list = get_plans()
    plans_by_date = {}
    for p in saved_plans_list:
        pd_key = (p.get("planned_date") or (p.get("created_at") or "")[:10])
        if pd_key:
            if pd_key not in plans_by_date:
                plans_by_date[pd_key] = []
            plans_by_date[pd_key].append(p)

    current_year = today_date.year
    current_month = today_date.month
    month_names = list(calendar.month_name)[1:]

    cal_sel_c1, cal_sel_c2, _ = st.columns([2, 2, 4])
    with cal_sel_c1:
        sel_month_name = st.selectbox("Select Month", month_names, index=current_month - 1, key="cal_sel_month")
        sel_month = month_names.index(sel_month_name) + 1
    with cal_sel_c2:
        year_options = [2024, 2025, 2026]
        y_idx = year_options.index(current_year) if current_year in year_options else len(year_options) - 1
        sel_year = st.selectbox("Select Year", year_options, index=y_idx, key="cal_sel_year")

    act_by_date = {}
    for a in all_activities:
        d = a.get("date")
        if d:
            k = d[:10]
            if k not in act_by_date:
                act_by_date[k] = []
            act_by_date[k].append(a)

    cal_matrix = calendar.monthcalendar(sel_year, sel_month)
    day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header_html = "".join(f"<div style='font-size: 0.74rem; font-weight: 700; color: #8E9DAE; text-align: center;'>{h}</div>" for h in day_headers)

    cells_list = []
    for week in cal_matrix:
        for day_num in week:
            if day_num == 0:
                cells_list.append("<div style='background: #0C1017; border: 1px dashed rgba(255,255,255,0.04); border-radius: 8px; height: 85px; opacity: 0.3;'></div>")
            else:
                d_str = f"{sel_year:04d}-{sel_month:02d}-{day_num:02d}"
                acts = act_by_date.get(d_str, [])
                p_items = plans_by_date.get(d_str, [])
                is_today = (d_str == str(today_date))
                border_s = "border: 2px solid #2DD4BF; background: #182232;" if is_today else "border: 1px solid #1E283A; background: #141B26;"

                badge_html = ""
                if acts:
                    for act_item in acts:
                        sp_name = act_item.get("sport", "Activity")
                        chip_cls = get_sport_chip_class(sp_name)
                        d_km = act_item.get("distance_km") or 0.0
                        dur_m = act_item.get("moving_time_min") or act_item.get("duration_min") or 0.0
                        label = f"{get_sport_icon(sp_name)} {d_km:.1f}k" if d_km > 0 else f"{get_sport_icon(sp_name)} {dur_m:.0f}m"
                        badge_html += f"<span class='sport-chip {chip_cls}' style='font-size: 0.65rem; padding: 1px 4px; display: block; margin-bottom: 2px; text-align: center;'>{label}</span>"

                if p_items:
                    for p_item in p_items:
                        p_dist_val = p_item.get("distance_m") or p_item.get("target_distance", 0)
                        badge_html += f"<span style='background: rgba(56, 189, 248, 0.15); color: #38BDF8; font-size: 0.65rem; padding: 1px 4px; border-radius: 4px; display: block; margin-bottom: 2px; text-align: center;'>🏊 {p_dist_val}m Plan</span>"

                if not acts and not p_items:
                    badge_html = "<span style='font-size: 0.66rem; color: #475569; display: block; text-align: center; margin-top: 14px;'>Rest</span>"

                cells_list.append(
                    f"<div style='{border_s} border-radius: 8px; padding: 6px; height: 85px; box-sizing: border-box; overflow-y: auto;'>"
                    f"<div style='font-family: JetBrains Mono; font-size: 0.78rem; font-weight: 700; color: {'#2DD4BF' if is_today else '#F1F5F9'}; margin-bottom: 3px;'>{day_num}</div>"
                    f"{badge_html}</div>"
                )

    cells_html = "".join(cells_list)
    st.markdown(
        f"""
        <div style='margin-bottom: 20px;'>
            <div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin-bottom: 6px;'>{header_html}</div>
            <div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px;'>{cells_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Workout Builder
    st.markdown("#### 🛠️ Workout Planner")
    b_col1, b_col2 = st.columns([1, 2])

    with b_col1:
        custom_focus = st.selectbox(
            "Swim Focus",
            ["Endurance", "Tempo", "Intervals", "Pyramid Ladder", "Recovery"],
            index=0,
            key="cal_plan_focus"
        )
        custom_dist = st.slider(
            "Target Distance (m)",
            min_value=1000,
            max_value=3500,
            value=2000,
            step=250,
            key="cal_plan_dist"
        )
        custom_date = st.date_input("Scheduled Date", value=target_plan_date, key="cal_plan_date")

        custom_swim_zones = swim_pace_zones(baseline_pace)
        if custom_focus == "Endurance":
            custom_plan = endurance_workout(target_distance=custom_dist, easy_min=custom_swim_zones["easy"]["min"], easy_max=custom_swim_zones["easy"]["max"], endurance_min=custom_swim_zones["endurance"]["min"], endurance_max=custom_swim_zones["endurance"]["max"])
        elif custom_focus == "Tempo":
            custom_plan = tempo_workout(target_distance=custom_dist, easy_min=custom_swim_zones["easy"]["min"], easy_max=custom_swim_zones["easy"]["max"], tempo_min=custom_swim_zones["tempo"]["min"], tempo_max=custom_swim_zones["tempo"]["max"])
        elif custom_focus == "Intervals":
            custom_plan = interval_workout(target_distance=custom_dist, easy_min=custom_swim_zones["easy"]["min"], easy_max=custom_swim_zones["easy"]["max"], interval_min=custom_swim_zones["interval"]["min"], interval_max=custom_swim_zones["interval"]["max"])
        elif custom_focus == "Pyramid Ladder":
            custom_plan = pyramid_workout(target_distance=custom_dist, easy_min=custom_swim_zones["easy"]["min"], easy_max=custom_swim_zones["easy"]["max"], tempo_min=custom_swim_zones["tempo"]["min"], tempo_max=custom_swim_zones["tempo"]["max"], interval_min=custom_swim_zones["interval"]["min"], interval_max=custom_swim_zones["interval"]["max"])
        else:
            custom_plan = recovery_workout(target_distance=custom_dist, easy_min=custom_swim_zones["easy"]["min"], easy_max=custom_swim_zones["easy"]["max"])

        custom_plan["plan_id"] = str(uuid.uuid4())
        custom_plan["sport"] = "Swim"
        custom_plan["planned_date"] = str(custom_date)
        custom_plan["distance_m"] = custom_plan.get("target_distance") or custom_dist

        if st.button("💾 Save Workout to Calendar", use_container_width=True, key="save_plan_cal_btn"):
            save_plan(custom_plan, target_date=str(custom_date))
            st.success(f"Saved {custom_focus} ({custom_dist}m) for {custom_date.strftime('%b %d')}!")
            st.rerun()

    with b_col2:
        st.markdown(f"**Preview:** `{custom_plan.get('type', custom_focus)}` · `{custom_dist}m` ({custom_dist // 25} Laps)")
        for j, cs in enumerate(custom_plan.get("sets", [])):
            st.markdown(f"- **Set {j+1}:** `{cs.get('reps')} × {cs.get('distance')}m` — `{cs.get('stroke_pattern', cs.get('stroke'))}` · Pace: `{cs.get('pace')}` · Rest: `{cs.get('rest')}`")

    if saved_plans_list:
        st.markdown("---")
        st.markdown(f"#### 🗄️ Saved Workout Plans Library ({len(saved_plans_list)})")
        for p_idx, p_item in enumerate(saved_plans_list):
            p_id = p_item.get("plan_id") or p_item.get("id") or str(uuid.uuid4())
            p_type = p_item.get("workout_type") or p_item.get("type", "Workout")
            p_dist = p_item.get("distance_m") or p_item.get("target_distance") or (int(p_item.get("distance_km", 0) * 1000))
            p_date_raw = p_item.get("planned_date") or (p_item.get("created_at") or "")[:10]
            with st.expander(f"🏊 {p_type} — {p_dist}m · 📅 {format_date_clean(p_date_raw)}"):
                st.markdown(f"**Goal:** {p_item.get('goal', '—')} · **Duration:** {p_item.get('duration_est', p_item.get('duration', '—'))}")
                for j, s in enumerate(p_item.get("sets", [])):
                    st.markdown(f"- **Set {j+1}:** `{s.get('reps', 1)} × {s.get('distance', 100)}m` — `{s.get('stroke_pattern', s.get('stroke', 'Freestyle'))}` · Pace: `{s.get('pace', 'Target')}` · Rest: `{s.get('rest', 'None')}`")
                if st.button("🗑️ Delete Plan", key=f"del_plan_cal_{p_id}_{p_idx}"):
                    delete_plan(p_id)
                    st.success("Plan deleted.")
                    st.rerun()


# ============================================================
# TAB 9: 📊 ANALYTICS & TRAINING LOAD
# ============================================================

with tab_analytics:
    # 1. ACWR & Form Stimulus
    cur_week_monday = today_date - timedelta(days=today_date.weekday())
    cur_week_sunday = cur_week_monday + timedelta(days=6)
    prev_week_monday = cur_week_monday - timedelta(days=7)
    prev_week_sunday = cur_week_monday - timedelta(days=1)

    cur_acts = [a for a in all_activities if a.get("date") and cur_week_monday <= datetime.fromisoformat(a["date"][:10]).date() <= cur_week_sunday]
    prev_acts = [a for a in all_activities if a.get("date") and prev_week_monday <= datetime.fromisoformat(a["date"][:10]).date() <= prev_week_sunday]

    cur_week_sum = training_summary(cur_acts)
    prev_week_sum = training_summary(prev_acts)

    tot_cur_load = sum(s.get("training_load", 0) for s in cur_week_sum.values())
    tot_prev_load = sum(s.get("training_load", 0) for s in prev_week_sum.values())

    acwr = tot_cur_load / max(1.0, tot_prev_load)
    form_status = "Optimal Base" if 0.8 <= acwr <= 1.3 else ("Fatigued" if acwr > 1.3 else "Fresh / Deload")

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Current Week Load</div>
                <div class="clean-kpi-val" style="color: #2DD4BF;">{tot_cur_load:.0f}</div>
                <div class="clean-kpi-sub">{sum(s.get('sessions', 0) for s in cur_week_sum.values())} sessions this week</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Previous Week Load</div>
                <div class="clean-kpi-val">{tot_prev_load:.0f}</div>
                <div class="clean-kpi-sub">baseline comparison</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Acute:Chronic Ratio</div>
                <div class="clean-kpi-val" style="color: #38BDF8;">{acwr:.2f}</div>
                <div class="clean-kpi-sub">ACWR ratio</div>
            </div>
            <div class="clean-kpi-card">
                <div class="clean-kpi-label">Form Status</div>
                <div class="clean-kpi-val">{form_status}</div>
                <div class="clean-kpi-sub">training stimulus</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Weekly Load Trends Chart
    if weekly_trends:
        w_tr_df = pd.DataFrame(weekly_trends)
        c_load = alt.Chart(w_tr_df).mark_area(
            line={"color": "#2DD4BF", "strokeWidth": 2},
            color="rgba(45, 212, 191, 0.12)"
        ).encode(
            x=alt.X("week:N", title="Training Week", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("training_load:Q", title="ICU Training Load"),
            tooltip=["week:N", "training_load:Q", "sessions:Q"],
        ).properties(height=200)
        st.altair_chart(apply_forest_chart_theme(c_load, height=200), use_container_width=True)

    # Personal Records
    st.markdown("#### 🏆 Personal Records")
    pr_tabs = st.tabs(["🏊 Swim Records", "🏃 Run Records", "🚴 Cycling Records", "🚶 Walk Records"])
    
    with pr_tabs[0]:
        pr_sw = personal_records.get("Swimming", [])
        if pr_sw:
            st.dataframe(pd.DataFrame(pr_sw), use_container_width=True, hide_index=True)
        else:
            st.info("No swimming records available.")

    with pr_tabs[1]:
        pr_rn = personal_records.get("Running", [])
        if pr_rn:
            st.dataframe(pd.DataFrame(pr_rn), use_container_width=True, hide_index=True)
        else:
            st.info("No running records available.")

    with pr_tabs[2]:
        pr_bk = personal_records.get("Cycling", [])
        if pr_bk:
            st.dataframe(pd.DataFrame(pr_bk), use_container_width=True, hide_index=True)
        else:
            st.info("No cycling records available.")

    with pr_tabs[3]:
        pr_wk = personal_records.get("Walking", [])
        if pr_wk:
            st.dataframe(pd.DataFrame(pr_wk), use_container_width=True, hide_index=True)
        else:
            st.info("No walking records available.")


# ============================================================
# TAB 10: ⚙️ SETTINGS
# ============================================================

with tab_settings:
    st.markdown("#### 🔌 Data Sources & Synchronization")
    st.markdown(
        f"""
        - **Garmin Forerunner 965:** Synced via Intervals.icu API (`{api_status.upper()}`)
        - **Total Master Activities:** `{len(all_activities)} sessions`
        - **Wellness & Sleep Records:** `{len(wellness_records)} days`
        """
    )

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🧹 Clear All Caches & Resync", use_container_width=True):
            st.cache_data.clear()
            st.success("Caches cleared! Reloading...")
            st.rerun()

    with c_btn2:
        if st.button("🗑️ Clear Saved Workout Plans", use_container_width=True):
            clear_plans()
            st.warning("All saved workout plans cleared.")
            st.rerun()
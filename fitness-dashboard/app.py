import sys
from pathlib import Path

# Add project root to sys.path so src imports work regardless of working directory
_app_dir = Path(__file__).resolve().parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

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
from src.training.swim_paces import swim_pace_zones
from src.training.plan_store import save_plan, get_plans, delete_plan, clear_plans


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personal Fitness & Training Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HIGH CONTRAST & RESPONSIVE CSS
# ============================================================

st.markdown(
    """
    <style>
    /* Global Typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Explicitly preserve Streamlit icons */
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
    
    /* Main Container Padding */
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100% !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    
    /* High-Contrast Metric Cards */
    .kpi-card {
        background: #151D2C;
        border: 1px solid #23324A;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.15s ease-in-out, border-color 0.15s ease-in-out;
    }
    .kpi-card:hover {
        border-color: #38BDF8;
    }
    .kpi-label {
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #FFFFFF !important;
        line-height: 1.15;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #94A3B8 !important;
        margin-top: 5px;
        font-weight: 500;
    }

    /* Sport Colors for KPI labels */
    .label-swim { color: #38BDF8 !important; }
    .label-ride { color: #4ADE80 !important; }
    .label-walk { color: #FBBF24 !important; }
    .label-run { color: #F472B6 !important; }
    .label-workout { color: #C084FC !important; }
    .label-load { color: #F87171 !important; }
    .label-total { color: #A78BFA !important; }

    /* High-Contrast Sport Badges */
    .sport-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .chip-swim { background: #0284C7; color: #FFFFFF !important; }
    .chip-ride { background: #059669; color: #FFFFFF !important; }
    .chip-walk { background: #D97706; color: #FFFFFF !important; }
    .chip-run { background: #DB2777; color: #FFFFFF !important; }
    .chip-workout { background: #7C3AED; color: #FFFFFF !important; }
    .chip-rest { background: #475569; color: #FFFFFF !important; }
    .chip-strava { background: #EA580C; color: #FFFFFF !important; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 5px; }
    .chip-intervals { background: #2563EB; color: #FFFFFF !important; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 5px; }
    .chip-merged { background: #0D9488; color: #FFFFFF !important; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 5px; }

    /* AI Coach Hero Banner */
    .hero-banner {
        background: #111827;
        border: 1px solid #1E293B;
        border-left: 6px solid #00D2FF;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 22px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 4px 0 8px 0;
    }
    .hero-text {
        font-size: 1.0rem;
        color: #E2E8F0 !important;
        line-height: 1.5;
        margin: 0;
    }

    /* Sport Summary Card */
    .sport-summary-card {
        background: #151D2C;
        border: 1px solid #23324A;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
        transition: transform 0.15s ease-in-out, border-color 0.15s ease-in-out;
    }
    .sport-summary-card:hover {
        border-color: #38BDF8;
        transform: translateY(-2px);
    }

    /* Calendar Grid Styling */
    .cal-grid-header {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-bottom: 8px;
    }
    .cal-header-cell {
        font-size: 0.85rem;
        font-weight: 800;
        color: #94A3B8;
        text-transform: uppercase;
        text-align: center;
        padding: 4px 0;
        letter-spacing: 0.05em;
    }
    .cal-grid-body {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-bottom: 24px;
    }
    .cal-cell {
        background: #151D2C;
        border: 1px solid #23324A;
        border-radius: 10px;
        padding: 8px 8px;
        height: 116px;
        min-height: 116px;
        max-height: 116px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        transition: border-color 0.15s ease-in-out;
    }
    .cal-cell:hover {
        border-color: #38BDF8;
    }
    .cal-cell-empty {
        background: rgba(15, 23, 42, 0.4);
        border: 1px dashed #1E293B;
        border-radius: 10px;
        height: 116px;
        min-height: 116px;
        max-height: 116px;
        box-sizing: border-box;
        opacity: 0.3;
    }
    .cal-cell-today {
        border: 2px solid #00D2FF !important;
        background: #132238;
    }
    .cal-date-num {
        font-size: 0.92rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 4px;
        line-height: 1.1;
    }
    .cal-badge {
        display: block;
        padding: 2px 4px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 3px;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.3;
    }
    .cal-rest {
        font-size: 0.75rem;
        color: #475569;
        font-weight: 600;
        margin-top: 2px;
    }

    /* Section Divider */
    hr {
        border-color: #23324A !important;
        margin: 1.5rem 0 !important;
    }

    /* Compact Gallery Thumbnail Styling */
    .stImage img {
        border-radius: 10px !important;
        border: 1px solid #23324A !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        object-fit: cover !important;
        max-height: 200px !important;
        max-width: 260px !important;
        transition: transform 0.2s ease-in-out;
    }
    .stImage img:hover {
        transform: scale(1.03);
    }

    /* Mobile Responsive Tab Navigation Bar */
    [data-baseweb="tab-list"] {
        gap: 6px !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid #23324A !important;
    }
    [data-baseweb="tab"] {
        padding: 8px 14px !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        border-radius: 8px !important;
        background: #151D2C !important;
        border: 1px solid #23324A !important;
        min-height: 40px !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        background: #0284C7 !important;
        color: #FFFFFF !important;
        border-color: #38BDF8 !important;
    }

    /* Touch-friendly buttons and inputs */
    button[kind="primary"], button[kind="secondary"], .stButton > button {
        min-height: 42px !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }

    /* Responsive DataFrames & Tables */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        max-width: 100% !important;
    }
    .vega-embed {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Mobile Screen Rules */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 2.2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }
        [data-testid="column"] {
            min-width: 47% !important;
            flex: 1 1 47% !important;
            margin-bottom: 6px !important;
        }
        h1 { font-size: 1.45rem !important; }
        h2 { font-size: 1.25rem !important; }
        h3 { font-size: 1.1rem !important; }
        .kpi-card { padding: 10px 12px !important; }
        .kpi-value { font-size: 1.4rem !important; }
        .hero-banner { padding: 14px 16px !important; }
        .hero-title { font-size: 1.2rem !important; }
        .hero-text { font-size: 0.88rem !important; }
        .cal-grid-header { gap: 4px !important; }
        .cal-grid-body { gap: 4px !important; }
        .cal-cell {
            height: 80px !important;
            min-height: 80px !important;
            max-height: 80px !important;
            padding: 4px 4px !important;
            border-radius: 6px !important;
        }
        .cal-cell-empty {
            height: 80px !important;
            min-height: 80px !important;
            max-height: 80px !important;
            border-radius: 6px !important;
        }
        .cal-date-num { font-size: 0.72rem !important; }
        .cal-badge { font-size: 0.60rem !important; padding: 1px 2px !important; margin-bottom: 2px !important; }
        .cal-header-cell { font-size: 0.70rem !important; }
        .stImage img { max-width: 100% !important; max-height: 160px !important; }
        [data-baseweb="tab"] { padding: 6px 10px !important; font-size: 0.8rem !important; min-height: 36px !important; }
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


def apply_chart_theme(chart, height=300):
    return (
        chart.properties(height=height)
        .configure_axis(
            labelColor="#E2E8F0",
            titleColor="#F8FAFC",
            labelFontSize=11,
            titleFontSize=12,
            titleFontWeight="bold",
            gridColor="rgba(255, 255, 255, 0.1)",
            domainColor="#475569",
            tickColor="#475569",
        )
        .configure_legend(
            labelColor="#E2E8F0",
            titleColor="#F8FAFC",
            labelFontSize=11,
            titleFontSize=12,
            titleFontWeight="bold",
        )
        .configure_title(
            color="#FFFFFF",
            fontSize=14,
            fontWeight="bold",
        )
        .configure_view(
            strokeWidth=0
        )
    )


# ============================================================
# SIDEBAR CONTROLS & GLOBAL FILTERS
# ============================================================

st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <span style="font-size: 2.0rem;">⚡</span>
        <div>
            <h2 style="margin: 0; font-weight: 800; color: #FFFFFF; font-size: 1.25rem;">FITNESS AI</h2>
            <span style="font-size: 0.78rem; color: #38BDF8; font-weight: 700; text-transform: uppercase;">Personal Training Engine</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### 🎛️ Data Source")
source_filter = st.sidebar.selectbox(
    "Select Source",
    options=["all", "intervals", "strava"],
    format_func=lambda x: {
        "all": "⚡ All Sources (Merged & Deduplicated)",
        "intervals": "🟢 Intervals.icu API / Garmin",
        "strava": "🟠 Strava Export Archive",
    }[x],
    index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown("### 📅 Time Window")
time_filter = st.sidebar.selectbox(
    "Select Period",
    options=[
        "7 Days",
        "30 Days",
        "3 Months",
        "Year to Date (2026)",
        "1 Year",
        "All Time",
        "Custom Range",
    ],
    index=0,
    label_visibility="collapsed",
)

today_date = date.today()
now_hour = datetime.now().hour
is_night_cutoff = now_hour >= 20

if time_filter == "7 Days":
    start_date_str = str(today_date - timedelta(days=6))
    end_date_str = str(today_date)
elif time_filter == "30 Days":
    start_date_str = str(today_date - timedelta(days=29))
    end_date_str = str(today_date)
elif time_filter == "3 Months":
    start_date_str = str(today_date - timedelta(days=90))
    end_date_str = str(today_date)
elif time_filter == "Year to Date (2026)":
    start_date_str = f"{today_date.year}-01-01"
    end_date_str = str(today_date)
elif time_filter == "1 Year":
    start_date_str = str(today_date - timedelta(days=365))
    end_date_str = str(today_date)
elif time_filter == "All Time":
    start_date_str = "2024-01-01"
    end_date_str = str(today_date)
else:
    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        s_date = st.date_input("Start", value=today_date - timedelta(days=30))
    with col_s2:
        e_date = st.date_input("End", value=today_date)
    start_date_str = str(s_date)
    end_date_str = str(e_date)

end_val = datetime.fromisoformat(end_date_str).date()
if is_night_cutoff:
    target_plan_date = end_val + timedelta(days=1)
    plan_timing_label = "Tomorrow's"
    plan_timing_badge = "Tomorrow"
else:
    target_plan_date = end_val
    plan_timing_label = "Today's"
    plan_timing_badge = "Today"

target_plan_date_str = target_plan_date.strftime("%A, %b %d, %Y")


# ============================================================
# DATA CACHING & FETCHING
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def load_cached_dashboard_data(start_str, end_str, src_filter):
    return get_dashboard_data(start_str, end_str, source_filter=src_filter)


if st.sidebar.button("🔄 Refresh / Sync Live Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

with st.spinner("Loading athlete training telemetry from Garmin, Intervals & Strava..."):
    data = load_cached_dashboard_data(start_date_str, end_date_str, source_filter)

activities = data.get("activities", [])
all_activities = data.get("all_activities", [])
current_week = data.get("current_week", {})
previous_week = data.get("previous_week", {})
swim_baseline = data.get("swim_baseline", [])
baseline_pace = data.get("baseline_pace", 154)
pace_zones = data.get("pace_zones", swim_pace_zones(baseline_pace))
plan = data.get("next_swim_plan", {})
recommendation = data.get("recommendation", {})
summary = data.get("summary", {})
weekly_trends = data.get("weekly_trends", [])
wellness_records = data.get("wellness", [])
api_status = data.get("api_status", "cache")
strava_found = data.get("strava_found", False)
strava_matched = data.get("strava_matched", 0)
strava_added = data.get("strava_added", 0)
tot_intervals = data.get("total_intervals_count", 0)
tot_strava = data.get("total_strava_count", 0)

# Analytics dictionaries
running_analytics = data.get("running_analytics", {})
cycling_analytics = data.get("cycling_analytics", {})
walking_analytics = data.get("walking_analytics", {})
sleep_analytics = data.get("sleep_analytics", {})
performance_analytics = data.get("performance_analytics", {})
personal_records = data.get("personal_records", {})

# Sidebar Status Badges
if source_filter == "all":
    st.sidebar.success(f"🟢 Intervals.icu ({tot_intervals}) + 🟠 Strava ({tot_strava})")
    st.sidebar.caption(f"⚡ Merged: **{strava_matched} synced** · **{strava_added} archive**")
elif source_filter == "strava":
    st.sidebar.warning(f"🟠 Strava Export Archive ({tot_strava} sessions)")
else:
    if api_status == "connected":
        st.sidebar.success(f"🟢 Connected to Intervals.icu ({tot_intervals})")
    else:
        st.sidebar.info(f"🟡 Using Cached Intervals ({tot_intervals})")

st.sidebar.markdown(f"**Selected Window:** `{format_date_clean(start_date_str)}` – `{format_date_clean(end_date_str)}`")
st.sidebar.markdown(f"**Activities in Window:** **{len(activities)} sessions** (of {len(all_activities)} total)")

total_dist_all = sum(s.get("distance_km", 0) for s in summary.values())
total_time_all = sum(s.get("moving_time_min", 0) for s in summary.values())
total_load_all = sum(s.get("training_load", 0) for s in summary.values())
total_cals_all = sum(a.get("calories", 0) for a in activities if a.get("calories"))

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Window Totals")
st.sidebar.markdown(f"**Total Distance:** `{total_dist_all:.1f} km`")
st.sidebar.markdown(f"**Total Active Time:** `{total_time_all / 60:.1f} hours`")
st.sidebar.markdown(f"**Total Active Calories:** `{total_cals_all:,} kcal`")
st.sidebar.markdown(f"**Total Training Load:** `{total_load_all:.0f}`")
st.sidebar.markdown("---")
st.sidebar.caption("🚀 Double-click desktop shortcut anytime to open.")


# ============================================================
# MAIN TOP HEADER
# ============================================================

header_html = f"""<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; margin-bottom: 20px; padding-top: 4px;">
    <h1 style="margin: 0; padding: 0; font-size: 2.1rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; line-height: 1.2;">⚡ Personal Fitness &amp; Training Command Center</h1>
    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
        <span class="sport-chip chip-swim">Garmin 965</span>
        <span class="sport-chip chip-ride">25m Pool</span>
        <span class="sport-chip chip-strava">Strava Connected ({tot_strava} activities)</span>
    </div>
</div>"""
if hasattr(st, "html"):
    st.html(header_html)
else:
    st.markdown(header_html, unsafe_allow_html=True)


# ============================================================
# AI COACH HERO CARD
# ============================================================

rec_sport = recommendation.get("sport", "Rest")
rec_intensity = recommendation.get("intensity", "Easy")
rec_reason = recommendation.get("reason", "Maintain consistency.")

chip_class = get_sport_chip_class(rec_sport)
sport_icon = get_sport_icon(rec_sport) if rec_sport != "Rest" else "🛌"

days_since_swim = data.get("days_since_swim")
days_since_ride = data.get("days_since_ride")
days_since_walk = data.get("days_since_walk")
days_since_run = data.get("days_since_run")

st.markdown(
    f"""
    <div class="hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div style="flex: 1; min-width: 300px;">
                <span style="font-size: 0.82rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.06em; text-transform: uppercase;">
                    ⚡ AI COACH RECOMMENDATION FOR {plan_timing_label.upper()} · {target_plan_date_str.upper()} ({plan_timing_badge.upper()})
                </span>
                <div class="hero-title">
                    {sport_icon} Recommended Workout: {rec_sport} 
                    <span class="sport-chip {chip_class}" style="vertical-align: middle; margin-left: 8px;">{rec_intensity} Intensity</span>
                </div>
                <p class="hero-text">
                    {rec_reason}
                </p>
            </div>
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <div style="text-align: center; background: #1F293D; padding: 8px 14px; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Last Swim</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #38BDF8;">{f"{days_since_swim}d ago" if days_since_swim is not None else "—"}</div>
                </div>
                <div style="text-align: center; background: #1F293D; padding: 8px 14px; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Last Ride</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #4ADE80;">{f"{days_since_ride}d ago" if days_since_ride is not None else "—"}</div>
                </div>
                <div style="text-align: center; background: #1F293D; padding: 8px 14px; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Last Walk</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #FBBF24;">{f"{days_since_walk}d ago" if days_since_walk is not None else "—"}</div>
                </div>
                <div style="text-align: center; background: #1F293D; padding: 8px 14px; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Last Run</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #F472B6;">{f"{days_since_run}d ago" if days_since_run is not None else "—"}</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# APPLICATION NAVIGATION TABS (11 TABS)
# ============================================================

(
    tab_overview,
    tab_swimming,
    tab_running,
    tab_cycling,
    tab_walking,
    tab_sleep,
    tab_performance,
    tab_calendar,
    tab_load,
    tab_records,
    tab_settings,
) = st.tabs([
    "🏠 Overview",
    "🏊 Swimming",
    "🏃 Running",
    "🚴 Cycling",
    "🚶 Walking",
    "😴 Sleep & Recovery",
    "📊 Performance",
    "📅 Calendar",
    "📈 Training Load",
    "🏆 Personal Records",
    "⚙️ Data & Settings",
])


# ============================================================
# TAB 1: 🏠 OVERVIEW
# ============================================================

with tab_overview:
    # 1. Today's Garmin Sleep & Recovery Card
    today_iso = str(today_date)
    today_wellness = next((w for w in wellness_records if w.get("id") == today_iso or w.get("date") == today_iso), None)
    if not today_wellness and wellness_records:
        today_wellness = wellness_records[-1]

    if today_wellness:
        t_sleep_sec = today_wellness.get("sleepSecs")
        t_sleep_score = today_wellness.get("sleepScore")
        t_rhr = today_wellness.get("restingHR")
        t_hrv = today_wellness.get("hrv")
        if t_sleep_sec or t_rhr or t_hrv:
            t_hours = int(t_sleep_sec // 3600) if t_sleep_sec else 0
            t_mins = int((t_sleep_sec % 3600) // 60) if t_sleep_sec else 0
            dur_display = f"{t_hours}h {t_mins:02d}m" if t_sleep_sec else "—"
            score_badge = f"{t_sleep_score:.0f}/100" if t_sleep_score else "Tracked"

            st.markdown(
                f"""
                <div style="background: #111827; border: 1px solid #23324A; border-left: 6px solid #8B5CF6; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                        <div>
                            <span style="font-size: 0.8rem; font-weight: 800; color: #A78BFA; text-transform: uppercase; letter-spacing: 0.05em;">
                                🌙 TODAY'S GARMIN SLEEP & RECOVERY TELEMETRY · {format_date_clean(today_wellness.get('id', today_iso)).upper()}
                            </span>
                            <h3 style="margin: 2px 0 0 0; color: #FFFFFF; font-size: 1.25rem; font-weight: 800;">
                                Sleep Quality, HRV & Recovery State
                            </h3>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <span class="sport-chip chip-workout" style="background: #6D28D9;">Score: {score_badge}</span>
                            <span class="sport-chip chip-swim" style="background: #0284C7;">HRV: {f"{t_hrv:.0f} ms" if t_hrv else "—"}</span>
                            <span class="sport-chip chip-ride" style="background: #059669;">RHR: {f"{t_rhr:.0f} bpm" if t_rhr else "—"}</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;">
                        <div style="background: #151D2C; border: 1px solid #23324A; border-radius: 8px; padding: 10px 14px;">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #A78BFA; text-transform: uppercase;">🛌 Sleep Duration</div>
                            <div style="font-size: 1.45rem; font-weight: 800; color: #FFFFFF;">{dur_display}</div>
                            <div style="font-size: 0.75rem; color: #94A3B8;">{f"{t_sleep_sec:,}s log" if t_sleep_sec else "No duration"}</div>
                        </div>
                        <div style="background: #151D2C; border: 1px solid #23324A; border-radius: 8px; padding: 10px 14px;">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #F472B6; text-transform: uppercase;">🎯 Sleep Score</div>
                            <div style="font-size: 1.45rem; font-weight: 800; color: #FFFFFF;">{f"{t_sleep_score:.0f}" if t_sleep_score else "—"} <span style="font-size: 0.85rem; color: #94A3B8;">/ 100</span></div>
                            <div style="font-size: 0.75rem; color: #34D399; font-weight: 600;">Restful</div>
                        </div>
                        <div style="background: #151D2C; border: 1px solid #23324A; border-radius: 8px; padding: 10px 14px;">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">💓 Overnight HRV</div>
                            <div style="font-size: 1.45rem; font-weight: 800; color: #FFFFFF;">{f"{t_hrv:.0f}" if t_hrv else "—"} <span style="font-size: 0.85rem; color: #94A3B8;">ms</span></div>
                            <div style="font-size: 0.75rem; color: #38BDF8;">Balanced</div>
                        </div>
                        <div style="background: #151D2C; border: 1px solid #23324A; border-radius: 8px; padding: 10px 14px;">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #4ADE80; text-transform: uppercase;">❤️ Resting HR</div>
                            <div style="font-size: 1.45rem; font-weight: 800; color: #FFFFFF;">{f"{t_rhr:.0f}" if t_rhr else "—"} <span style="font-size: 0.85rem; color: #94A3B8;">bpm</span></div>
                            <div style="font-size: 0.75rem; color: #4ADE80;">Garmin 965</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 2. Window Primary KPI Cards (7 Cards)
    st.markdown("### 📊 Activity Telemetry Overview")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6, kpi_col7 = st.columns(7)

    with kpi_col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-total">🏃 Total Distance</div>
                <div class="kpi-value">{total_dist_all:.1f} <span style="font-size: 1rem; font-weight: 600; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">{len(activities)} total sessions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">⏱️ Active Time</div>
                <div class="kpi-value">{total_time_all / 60:.1f} <span style="font-size: 1rem; font-weight: 600; color: #94A3B8;">hrs</span></div>
                <div class="kpi-sub">{total_time_all:.0f} moving mins</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">🔥 Active Calories</div>
                <div class="kpi-value">{total_cals_all:,} <span style="font-size: 1rem; font-weight: 600; color: #94A3B8;">kcal</span></div>
                <div class="kpi-sub">Verified energy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-load">📈 Training Load</div>
                <div class="kpi-value">{total_load_all:.0f}</div>
                <div class="kpi-sub">ICU Training Load</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col5:
        # Steps from wellness or walks
        daily_steps_list = [w["steps"] for w in wellness_records if w.get("steps")]
        avg_steps = round(sum(daily_steps_list) / len(daily_steps_list)) if daily_steps_list else None
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-walk">👟 Avg Daily Steps</div>
                <div class="kpi-value">{f"{avg_steps:,}" if avg_steps else "—"}</div>
                <div class="kpi-sub">Garmin pedometer</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col6:
        avg_sleep_f = sleep_analytics.get("avg_duration_formatted", "—")
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-workout">😴 Avg Sleep</div>
                <div class="kpi-value">{avg_sleep_f}</div>
                <div class="kpi-sub">{sleep_analytics.get('total_days_tracked', 0)} nights tracked</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col7:
        streak_days = performance_analytics.get("current_streak", 0)
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label" style="color: #F59E0B;">🔥 Activity Streak</div>
                <div class="kpi-value">{streak_days} <span style="font-size: 1rem; font-weight: 600; color: #94A3B8;">days</span></div>
                <div class="kpi-sub">Consecutive active</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Sport Summary Cards Section (Swim, Run, Bike, Walk)
    st.markdown("### 🏅 Multi-Sport Breakdown")
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)

    swim_sum = summary.get("Swim", {})
    run_sum = summary.get("Run", {})
    ride_sum = summary.get("Ride", {})
    walk_sum = summary.get("Walk", {})

    with s_col1:
        s_pace = swim_sum.get("pace_formatted", "—")
        st.markdown(
            f"""
            <div class="sport-summary-card" style="border-top: 4px solid #0284C7;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.1rem; font-weight: 800; color: #38BDF8;">🏊 SWIMMING</span>
                    <span class="sport-chip chip-swim">{swim_sum.get('sessions', 0)} sessions</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF;">{swim_sum.get('distance_km', 0):.2f} km</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                    ⏱️ {format_duration_hm(swim_sum.get('moving_time_min', 0))} · ⚡ {s_pace}
                </div>
                <div style="font-size: 0.78rem; color: #38BDF8; margin-top: 6px; font-weight: 600;">
                    Last: {f"{days_since_swim}d ago" if days_since_swim is not None else "—"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s_col2:
        r_pace = run_sum.get("pace_formatted", "—")
        st.markdown(
            f"""
            <div class="sport-summary-card" style="border-top: 4px solid #DB2777;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.1rem; font-weight: 800; color: #F472B6;">🏃 RUNNING</span>
                    <span class="sport-chip chip-run">{run_sum.get('sessions', 0)} sessions</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF;">{run_sum.get('distance_km', 0):.2f} km</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                    ⏱️ {format_duration_hm(run_sum.get('moving_time_min', 0))} · ⚡ {r_pace}
                </div>
                <div style="font-size: 0.78rem; color: #F472B6; margin-top: 6px; font-weight: 600;">
                    Last: {f"{days_since_run}d ago" if days_since_run is not None else "—"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s_col3:
        b_speed = cycling_analytics.get("avg_speed_kmh")
        b_speed_str = f"{b_speed:.1f} km/h" if b_speed else "—"
        st.markdown(
            f"""
            <div class="sport-summary-card" style="border-top: 4px solid #059669;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.1rem; font-weight: 800; color: #4ADE80;">🚴 CYCLING</span>
                    <span class="sport-chip chip-ride">{ride_sum.get('sessions', 0)} sessions</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF;">{ride_sum.get('distance_km', 0):.2f} km</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                    ⏱️ {format_duration_hm(ride_sum.get('moving_time_min', 0))} · ⚡ {b_speed_str}
                </div>
                <div style="font-size: 0.78rem; color: #4ADE80; margin-top: 6px; font-weight: 600;">
                    Last: {f"{days_since_ride}d ago" if days_since_ride is not None else "—"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s_col4:
        w_pace = walking_analytics.get("avg_pace_formatted", "—")
        st.markdown(
            f"""
            <div class="sport-summary-card" style="border-top: 4px solid #D97706;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.1rem; font-weight: 800; color: #FBBF24;">🚶 WALKING</span>
                    <span class="sport-chip chip-walk">{walk_sum.get('sessions', 0)} sessions</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF;">{walk_sum.get('distance_km', 0):.2f} km</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                    ⏱️ {format_duration_hm(walk_sum.get('moving_time_min', 0))} · ⚡ {w_pace}
                </div>
                <div style="font-size: 0.78rem; color: #FBBF24; margin-top: 6px; font-weight: 600;">
                    Last: {f"{days_since_walk}d ago" if days_since_walk is not None else "—"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Recent Activities Feed
    st.markdown("### 📋 Recent Training Activities")
    if activities:
        recent_rows = []
        for a in activities[:15]:
            sp = a.get("sport", "Other")
            d_km = a.get("distance_km") or 0.0
            dur_m = a.get("moving_time_min") or a.get("duration_min") or 0.0
            hr_val = f"{a['avg_hr']:.0f} bpm" if a.get("avg_hr") else "—"
            cals_val = f"{a['calories']} kcal" if a.get("calories") else "—"
            load_val = f"{a['training_load']:.0f}" if a.get("training_load") else "—"

            pace_speed = "—"
            if sp == "Swim" and d_km > 0 and dur_m > 0:
                p_sec = (dur_m * 60) / (d_km * 10)
                pace_speed = f"{int(p_sec//60)}:{int(p_sec%60):02d} /100m"
            elif sp == "Run" and d_km > 0 and dur_m > 0:
                p_sec = (dur_m * 60) / d_km
                pace_speed = f"{int(p_sec//60)}:{int(p_sec%60):02d} /km"
            elif sp == "Ride" and d_km > 0 and dur_m > 0:
                spd = d_km / (dur_m / 60)
                pace_speed = f"{spd:.1f} km/h"
            elif sp == "Walk" and d_km > 0 and dur_m > 0:
                p_sec = (dur_m * 60) / d_km
                pace_speed = f"{int(p_sec//60)}:{int(p_sec%60):02d} /km"

            recent_rows.append({
                "Date": format_date_clean(a.get("date")),
                "Sport": f"{get_sport_icon(sp)} {sp}",
                "Activity Name": a.get("name", "Workout"),
                "Distance (km)": f"{d_km:.2f} km" if d_km > 0 else "—",
                "Duration": format_duration_hm(dur_m),
                "Pace / Speed": pace_speed,
                "Avg HR": hr_val,
                "Calories": cals_val,
                "Training Load": load_val,
                "Source": a.get("source", "Garmin"),
            })
        st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No activities recorded in the selected time window. Expand your time window in the sidebar.")


# ============================================================
# TAB 2: 🏊 SWIMMING
# ============================================================

with tab_swimming:
    swim_activities = [a for a in activities if a.get("sport") == "Swim"]
    all_swims = [a for a in all_activities if a.get("sport") == "Swim"]

    st.markdown("## 🏊 Swimming Analytics & AI Workout Engine")
    st.markdown("Deep swim pacing, 5-zone distribution, baseline speed, dynamic workout builder, and accordion sets.")

    # 1. Swim KPIs
    sw_dist = sum(s.get("distance_km") or 0.0 for s in swim_activities)
    sw_time = sum(s.get("moving_time_min") or 0.0 for s in swim_activities)
    sw_hrs = [s["avg_hr"] for s in swim_activities if s.get("avg_hr")]
    sw_avg_hr = round(sum(sw_hrs) / len(sw_hrs)) if sw_hrs else None
    sw_cals = sum(s.get("calories") or 0 for s in swim_activities if s.get("calories"))

    c_sw1, c_sw2, c_sw3, c_sw4, c_sw5, c_sw6 = st.columns(6)
    with c_sw1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">Total Swim Distance</div>
                <div class="kpi-value">{sw_dist:.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">{len(swim_activities)} swim sessions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sw2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">Active Swim Time</div>
                <div class="kpi-value">{format_duration_hm(sw_time)}</div>
                <div class="kpi-sub">{sw_time:.0f} moving mins</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sw3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">Baseline Pace</div>
                <div class="kpi-value">{format_pace(baseline_pace)}</div>
                <div class="kpi-sub">per 100m threshold</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sw4:
        est_1000m_sec = baseline_pace * 10
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">Est. 1,000m Time</div>
                <div class="kpi-value">{int(est_1000m_sec // 60)}:{int(est_1000m_sec % 60):02d}</div>
                <div class="kpi-sub">at baseline pace</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sw5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">Avg Heart Rate</div>
                <div class="kpi-value">{f"{sw_avg_hr}" if sw_avg_hr else "—"} <span style="font-size: 1rem; color: #94A3B8;">bpm</span></div>
                <div class="kpi-sub">Underwater optical</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sw6:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">Pool Length</div>
                <div class="kpi-value">25 <span style="font-size: 1rem; color: #94A3B8;">m</span></div>
                <div class="kpi-sub">Standard short course</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. AI Next Swim Workout Plan (with Accordion Sets & Lap Terminology)
    st.markdown(f"### 🎯 {plan_timing_label} AI Recommended Swim Workout Plan")

    plan_type = plan.get("workout_type", "Endurance")
    plan_dist = plan.get("distance_m", 2000)
    plan_dur = plan.get("duration_est", "45-55 min")
    plan_goal = plan.get("goal", "Build aerobic endurance.")
    plan_sets = plan.get("sets", [])
    plan_readiness = plan.get("readiness_score", 85)
    plan_rationale = plan.get("coach_rationale", "Optimized from your recent Garmin training load and recovery.")

    st.markdown(
        f"""
        <div class="hero-banner" style="border-left-color: #00D2FF; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <span style="font-size: 0.82rem; font-weight: 800; color: #38BDF8; text-transform: uppercase;">
                        🏊 {plan_type.upper()} WORKOUT · {plan_timing_badge.upper()} ({target_plan_date_str})
                    </span>
                    <h3 style="margin: 2px 0 4px 0; color: #FFFFFF; font-size: 1.35rem;">
                        {plan_type} Session — {plan_dist:,} m ({plan_dist // 25} Laps)
                    </h3>
                    <p style="margin: 0; color: #E2E8F0; font-size: 0.95rem;">
                        <strong>Estimated Duration:</strong> {plan_dur} · <strong>Target Goal:</strong> {plan_goal}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 700; text-transform: uppercase;">Readiness Score</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #34D399;">{plan_readiness}/100</div>
                </div>
            </div>
            <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #1E293B; font-size: 0.88rem; color: #94A3B8;">
                💡 <strong>AI Coach Rationale:</strong> {plan_rationale}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Accordion Sets
    st.markdown("#### 📋 Structured Workout Sets (25m Pool — Lap Terminology)")
    for i, s in enumerate(plan_sets):
        reps = s.get("reps", 1)
        dist = s.get("distance", 100)
        tot_dist = s.get("total_distance", reps * dist)
        laps_per_rep = s.get("laps", dist // 25)
        tot_laps = s.get("total_laps", reps * laps_per_rep)
        purpose = s.get("purpose", "Swim")
        pattern = s.get("stroke_pattern", s.get("stroke", "Freestyle"))
        pace_str = s.get("pace", "Controlled")
        rest_str = s.get("rest", "None")

        exp_title = f"{'▾' if i == 1 else '▸'} Set {i+1}: {purpose.upper()} — {tot_dist}m ({tot_laps} Laps) · {reps} × {dist}m"
        with st.expander(exp_title, expanded=(i == 1)):
            st.markdown(
                f"""
                - **Repetition:** `{reps} × {dist}m` ({laps_per_rep} Laps per rep)
                - **Stroke Pattern:** `{pattern}`
                - **Target Pace:** `{pace_str}`
                - **Rest Interval:** `{rest_str}`
                - **Set Purpose:** {purpose}
                """
            )

    # 3. 5-Zone Pace Guidelines
    st.markdown("---")
    st.markdown("### 🎯 5-Zone Swim Pace Guidelines (25m Pool)")
    z_easy = pace_zones.get("easy", {})
    z_end = pace_zones.get("endurance", {})
    z_tempo = pace_zones.get("tempo", {})
    z_int = pace_zones.get("interval", {})
    z_sprint = pace_zones.get("sprint", {})

    zone_rows = [
        {
            "Zone": "Zone 1 · Easy / Recovery",
            "Pace /100m": z_easy.get("formatted", f"{format_pace(baseline_pace + 15)} – {format_pace(baseline_pace + 30)}"),
            "200m (8 Laps)": f"{format_pace((z_easy.get('min', baseline_pace + 15)) * 2)}",
            "400m (16 Laps)": f"{format_pace((z_easy.get('min', baseline_pace + 15)) * 4)}",
            "Purpose": z_easy.get("purpose", "Warm-up, cool-down, active recovery & drills"),
        },
        {
            "Zone": "Zone 2 · Aerobic Base (Cruise)",
            "Pace /100m": z_end.get("formatted", f"{format_pace(baseline_pace)} – {format_pace(baseline_pace + 10)}"),
            "200m (8 Laps)": f"{format_pace((z_end.get('min', baseline_pace)) * 2)}",
            "400m (16 Laps)": f"{format_pace((z_end.get('min', baseline_pace)) * 4)}",
            "Purpose": z_end.get("purpose", "Aerobic conditioning, continuous mixed sets"),
        },
        {
            "Zone": "Zone 3 · Tempo (Lactate Threshold)",
            "Pace /100m": z_tempo.get("formatted", f"{format_pace(baseline_pace - 10)} – {format_pace(baseline_pace)}"),
            "200m (8 Laps)": f"{format_pace((z_tempo.get('min', baseline_pace - 10)) * 2)}",
            "400m (16 Laps)": f"{format_pace((z_tempo.get('min', baseline_pace - 10)) * 4)}",
            "Purpose": z_tempo.get("purpose", "Lactate threshold & sustainable speed endurance"),
        },
        {
            "Zone": "Zone 4 · Threshold & Speed Intervals",
            "Pace /100m": z_int.get("formatted", f"{format_pace(baseline_pace - 20)} – {format_pace(baseline_pace - 10)}"),
            "200m (8 Laps)": f"{format_pace((z_int.get('min', baseline_pace - 20)) * 2)}",
            "400m (16 Laps)": f"{format_pace((z_int.get('min', baseline_pace - 20)) * 4)}",
            "Purpose": z_int.get("purpose", "100m freestyle speed repeats with rest"),
        },
        {
            "Zone": "Zone 5 · Anaerobic Power / Sprint",
            "Pace /100m": z_sprint.get("formatted", f"{format_pace(baseline_pace - 30)} – {format_pace(baseline_pace - 20)}"),
            "200m (8 Laps)": f"{format_pace((z_sprint.get('min', baseline_pace - 30)) * 2)}",
            "400m (16 Laps)": f"{format_pace((z_sprint.get('min', baseline_pace - 30)) * 4)}",
            "Purpose": z_sprint.get("purpose", "25m-50m max cadence & explosive push-offs"),
        },
    ]
    st.dataframe(pd.DataFrame(zone_rows), use_container_width=True, hide_index=True)

    # 4. Swimming Charts
    st.markdown("### 📈 Swimming Trends")
    sw_chart_col1, sw_chart_col2 = st.columns(2)

    with sw_chart_col1:
        if weekly_trends:
            w_df = pd.DataFrame(weekly_trends)
            c_dist = alt.Chart(w_df).mark_bar(color="#0284C7", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("week:N", title="Training Week"),
                y=alt.Y("distance_km:Q", title="Volume (km)"),
                tooltip=[
                    alt.Tooltip("week:N", title="Week"),
                    alt.Tooltip("distance_km:Q", title="Distance (km)"),
                    alt.Tooltip("sessions:Q", title="Sessions"),
                    alt.Tooltip("time_min:Q", title="Time (min)"),
                ],
            ).properties(title="Weekly Swim Volume Progression")
            st.altair_chart(apply_chart_theme(c_dist), use_container_width=True)

    with sw_chart_col2:
        if swim_baseline:
            b_df = pd.DataFrame(swim_baseline)
            b_df["date_clean"] = b_df["date"].apply(lambda d: str(d)[:10])
            b_df["pace_min"] = b_df["pace_seconds"] / 60.0
            c_pace = alt.Chart(b_df).mark_line(point=True, color="#38BDF8").encode(
                x=alt.X("date_clean:N", title="Swim Date"),
                y=alt.Y("pace_seconds:Q", title="Pace (seconds /100m)", scale=alt.Scale(zero=False)),
                tooltip=[
                    alt.Tooltip("date_clean:N", title="Date"),
                    alt.Tooltip("distance_km:Q", title="Distance (km)"),
                    alt.Tooltip("time_min:Q", title="Time (min)"),
                    alt.Tooltip("pace_formatted:N", title="Pace"),
                ],
            ).properties(title="Pace Progression /100m (Continuous Swims)")
            st.altair_chart(apply_chart_theme(c_pace), use_container_width=True)

    # 5. Interactive Swim Workout Builder & Customizer
    st.markdown("---")
    st.markdown("### 🛠️ Interactive Swim Workout Builder & Customizer")
    b_col1, b_col2 = st.columns([1, 2])

    with b_col1:
        custom_focus = st.selectbox("Workout Focus", ["Endurance", "Tempo", "Intervals", "Pyramid Ladder", "Recovery"], index=0)
        custom_dist = st.slider("Target Distance (m)", min_value=1000, max_value=3500, value=plan_dist, step=250)
        custom_date = st.date_input("Target / Planned Date", value=target_plan_date, key="custom_swim_workout_date")

        # Generate dynamically with user's baseline pace zones
        if custom_focus == "Endurance":
            custom_plan = endurance_workout(
                target_distance=custom_dist,
                easy_min=pace_zones["easy"]["min"],
                easy_max=pace_zones["easy"]["max"],
                endurance_min=pace_zones["endurance"]["min"],
                endurance_max=pace_zones["endurance"]["max"],
            )
        elif custom_focus == "Tempo":
            custom_plan = tempo_workout(
                target_distance=custom_dist,
                easy_min=pace_zones["easy"]["min"],
                easy_max=pace_zones["easy"]["max"],
                tempo_min=pace_zones["tempo"]["min"],
                tempo_max=pace_zones["tempo"]["max"],
            )
        elif custom_focus == "Intervals":
            custom_plan = interval_workout(
                target_distance=custom_dist,
                easy_min=pace_zones["easy"]["min"],
                easy_max=pace_zones["easy"]["max"],
                interval_min=pace_zones["interval"]["min"],
                interval_max=pace_zones["interval"]["max"],
            )
        elif custom_focus == "Pyramid Ladder":
            custom_plan = pyramid_workout(
                target_distance=custom_dist,
                easy_min=pace_zones["easy"]["min"],
                easy_max=pace_zones["easy"]["max"],
                tempo_min=pace_zones["tempo"]["min"],
                tempo_max=pace_zones["tempo"]["max"],
                interval_min=pace_zones["interval"]["min"],
                interval_max=pace_zones["interval"]["max"],
            )
        else:
            custom_plan = recovery_workout(
                target_distance=custom_dist,
                easy_min=pace_zones["easy"]["min"],
                easy_max=pace_zones["easy"]["max"],
            )

        cust_target_d = custom_plan.get("target_distance") or custom_dist
        cust_laps = custom_plan.get("total_laps") or (cust_target_d // 25)
        cust_dur = custom_plan.get("duration") or "45-55 min"
        cust_goal = custom_plan.get("goal") or "Maintain swimming consistency."

        # Attach metadata to custom plan
        custom_plan["plan_id"] = str(uuid.uuid4())
        custom_plan["planned_date"] = str(custom_date)
        custom_plan["created_at"] = datetime.now().isoformat()
        custom_plan["name"] = f"Custom {custom_focus} Session"
        custom_plan["distance_m"] = cust_target_d

        if st.button("💾 Save Custom Plan to Library", use_container_width=True):
            save_plan(custom_plan, target_date=str(custom_date))
            st.success(f"Saved {custom_focus} ({cust_target_d}m) for {custom_date.strftime('%A, %b %d, %Y')} to your Library!")

    with b_col2:
        custom_date_str = custom_date.strftime("%A, %b %d, %Y")
        st.markdown(f"**Custom Plan Preview:** `{custom_plan.get('type', custom_focus)}` · `{cust_target_d}m` ({cust_laps} Laps) · 📅 `{custom_date_str}`")
        st.caption(f"Estimated Time: **{cust_dur}** · Goal: **{cust_goal}**")
        for j, cs in enumerate(custom_plan.get("sets", [])):
            st.markdown(
                f"- **Set {j+1}:** `{cs.get('reps')} × {cs.get('distance')}m` ({cs.get('total_laps')} total laps) — `{cs.get('stroke_pattern', cs.get('stroke'))}` · Pace: `{cs.get('pace')}` · Rest: `{cs.get('rest')}`"
            )


# ============================================================
# TAB 3: 🏃 RUNNING
# ============================================================

with tab_running:
    st.markdown("## 🏃 Running Analytics, Splits & Race Guidelines")
    st.markdown("Extracted from your Garmin & Strava GPS running sessions, including 1-km split telemetry.")

    runs_list = running_analytics.get("runs", [])
    tot_run_dist = running_analytics.get("total_distance_km", 0.0)
    best_run_pace = running_analytics.get("fastest_pace_formatted", "—")
    longest_run = running_analytics.get("longest_run_km", 0.0)
    peak_run_hr = running_analytics.get("peak_hr")
    tot_run_load = running_analytics.get("total_load", 0)

    # 1. Running KPIs
    c_r1, c_r2, c_r3, c_r4, c_r5 = st.columns(5)
    with c_r1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-run">🏃 Total Distance</div>
                <div class="kpi-value">{tot_run_dist:.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">{len(runs_list)} completed runs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_r2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-run">⚡ Best Pace</div>
                <div class="kpi-value">{best_run_pace}</div>
                <div class="kpi-sub">Fastest average pace</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_r3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-run">📍 Longest Run</div>
                <div class="kpi-value">{longest_run:.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">Max single session</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_r4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-run">❤️ Peak Heart Rate</div>
                <div class="kpi-value">{f"{peak_run_hr}" if peak_run_hr else "—"} <span style="font-size: 1rem; color: #94A3B8;">bpm</span></div>
                <div class="kpi-sub">Garmin HR monitor</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_r5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-run">🔥 Total Run Load</div>
                <div class="kpi-value">{tot_run_load:.0f}</div>
                <div class="kpi-sub">Cardiovascular load</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Running Pace Zones
    st.markdown("### 🎯 5-Zone Running Pace Guidelines")
    r_zones = running_analytics.get("pace_zones", [])
    if r_zones:
        st.dataframe(pd.DataFrame(r_zones), use_container_width=True, hide_index=True)

    # 3. Running Charts
    if runs_list:
        st.markdown("### 📈 Running Progression")
        r_df = pd.DataFrame(runs_list)
        r_df["date_clean"] = r_df["date"].apply(lambda d: str(d)[:10])
        r_c1, r_c2 = st.columns(2)
        with r_c1:
            c_r_dist = alt.Chart(r_df).mark_bar(color="#DB2777", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("date_clean:N", title="Run Date"),
                y=alt.Y("distance_km:Q", title="Distance (km)"),
                tooltip=[
                    alt.Tooltip("date_clean:N", title="Date"),
                    alt.Tooltip("name:N", title="Name"),
                    alt.Tooltip("distance_km:Q", title="Distance (km)"),
                    alt.Tooltip("duration_min:Q", title="Duration (min)"),
                    alt.Tooltip("pace_formatted:N", title="Pace"),
                ],
            ).properties(title="Running Sessions Progression")
            st.altair_chart(apply_chart_theme(c_r_dist), use_container_width=True)

        with r_c2:
            c_r_hr = alt.Chart(r_df).mark_line(point=True, color="#F87171").encode(
                x=alt.X("date_clean:N", title="Run Date"),
                y=alt.Y("avg_hr:Q", title="Avg HR (bpm)", scale=alt.Scale(zero=False)),
                tooltip=[
                    alt.Tooltip("date_clean:N", title="Date"),
                    alt.Tooltip("name:N", title="Name"),
                    alt.Tooltip("avg_hr:Q", title="Avg HR"),
                    alt.Tooltip("max_hr:Q", title="Max HR"),
                ],
            ).properties(title="Cardiovascular Load & Heart Rate")
            st.altair_chart(apply_chart_theme(c_r_hr), use_container_width=True)

    # 4. GPS 1-km Splits Inspector
    st.markdown("---")
    st.markdown("### ⏱️ GPS Kilometer Splits Breakdown")
    splits_found = False
    for r_act in runs_list:
        s_list = r_act.get("splits", [])
        if s_list:
            splits_found = True
            with st.expander(f"🏃 {r_act.get('name', 'Run')} — {format_date_clean(r_act.get('date'))} ({r_act.get('distance_km', 0):.2f} km @ {r_act.get('pace_formatted', '—')})", expanded=True):
                split_rows = []
                for sp in s_list:
                    split_rows.append({
                        "Kilometer": f"Km {sp.get('split_km')}",
                        "Split Time": sp.get("split_time_formatted"),
                        "Pace (/km)": sp.get("pace_formatted"),
                        "Elapsed Time": sp.get("elapsed_time_formatted"),
                        "Elev Gain": f"+{sp.get('elevation_gain_m', 0):.0f} m",
                        "Diff vs Avg": sp.get("pace_diff_formatted"),
                    })
                st.dataframe(pd.DataFrame(split_rows), use_container_width=True, hide_index=True)

    # 5. Media Gallery (Photos)
    st.markdown("---")
    st.markdown("### 📸 Race & Workout Gallery")
    media_runs = [r for r in runs_list if r.get("media")]
    if media_runs:
        g_cols = st.columns(4)
        col_idx = 0
        for m_act in media_runs:
            for m_item in m_act.get("media", []):
                fn = m_item.get("filename") if isinstance(m_item, dict) else str(m_item)
                p_file = get_strava_media_path(fn)
                if p_file and p_file.exists():
                    with g_cols[col_idx % 4]:
                        st.image(str(p_file), caption=f"{m_act.get('name')} ({format_date_clean(m_act.get('date'))})", use_container_width=True)
                    col_idx += 1


# ============================================================
# TAB 4: 🚴 CYCLING
# ============================================================

with tab_cycling:
    st.markdown("## 🚴 Cycling Analytics & Power Telemetry")
    st.markdown("Aggregated from Garmin & Strava cycling sessions.")

    rides_list = cycling_analytics.get("rides", [])
    tot_ride_dist = cycling_analytics.get("total_distance_km", 0.0)
    tot_ride_time = cycling_analytics.get("total_moving_min", 0.0)
    avg_ride_speed = cycling_analytics.get("avg_speed_kmh")
    fastest_ride_speed = cycling_analytics.get("fastest_speed_kmh")
    tot_ride_elev = cycling_analytics.get("total_elevation_m", 0.0)
    longest_ride_val = cycling_analytics.get("longest_ride_km", 0.0)

    # 1. Cycling KPIs
    c_b1, c_b2, c_b3, c_b4, c_b5, c_b6 = st.columns(6)
    with c_b1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">Total Distance</div>
                <div class="kpi-value">{tot_ride_dist:.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">{len(rides_list)} rides completed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_b2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">Active Time</div>
                <div class="kpi-value">{format_duration_hm(tot_ride_time)}</div>
                <div class="kpi-sub">{tot_ride_time:.0f} moving mins</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_b3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">Avg Speed</div>
                <div class="kpi-value">{f"{avg_ride_speed:.1f}" if avg_ride_speed else "—"} <span style="font-size: 1rem; color: #94A3B8;">km/h</span></div>
                <div class="kpi-sub">Overall average</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_b4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">Fastest Speed</div>
                <div class="kpi-value">{f"{fastest_ride_speed:.1f}" if fastest_ride_speed else "—"} <span style="font-size: 1rem; color: #94A3B8;">km/h</span></div>
                <div class="kpi-sub">Top sustained avg</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_b5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">Elevation Gain</div>
                <div class="kpi-value">{tot_ride_elev:.0f} <span style="font-size: 1rem; color: #94A3B8;">m</span></div>
                <div class="kpi-sub">Climbing elevation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_b6:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">Longest Ride</div>
                <div class="kpi-value">{longest_ride_val:.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">Single session record</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Cycling Charts
    if rides_list:
        st.markdown("### 📈 Cycling Progression")
        ride_df = pd.DataFrame(rides_list)
        ride_df["date_clean"] = ride_df["date"].apply(lambda d: str(d)[:10])
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            c_b_dist = alt.Chart(ride_df).mark_bar(color="#059669", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("date_clean:N", title="Ride Date"),
                y=alt.Y("distance_km:Q", title="Distance (km)"),
                tooltip=[
                    alt.Tooltip("date_clean:N", title="Date"),
                    alt.Tooltip("name:N", title="Name"),
                    alt.Tooltip("distance_km:Q", title="Distance (km)"),
                    alt.Tooltip("moving_time_min:Q", title="Moving Time (min)"),
                ],
            ).properties(title="Ride Distance Progression")
            st.altair_chart(apply_chart_theme(c_b_dist), use_container_width=True)

        with b_c2:
            c_b_spd = alt.Chart(ride_df).mark_line(point=True, color="#4ADE80").encode(
                x=alt.X("date_clean:N", title="Ride Date"),
                y=alt.Y("computed_speed_kmh:Q", title="Speed (km/h)", scale=alt.Scale(zero=False)),
                tooltip=[
                    alt.Tooltip("date_clean:N", title="Date"),
                    alt.Tooltip("name:N", title="Name"),
                    alt.Tooltip("computed_speed_kmh:Q", title="Speed (km/h)"),
                ],
            ).properties(title="Speed (km/h) Progression")
            st.altair_chart(apply_chart_theme(c_b_spd), use_container_width=True)

    # 3. Cycling Activity Log
    st.markdown("### 📋 Cycling Activity History")
    if rides_list:
        r_table_rows = []
        for r in rides_list:
            r_table_rows.append({
                "Date": format_date_clean(r.get("date")),
                "Ride Name": r.get("name", "Ride"),
                "Distance (km)": f"{r.get('distance_km', 0):.2f} km",
                "Duration": format_duration_hm(r.get("moving_time_min", 0)),
                "Avg Speed": f"{r.get('computed_speed_kmh', 0):.1f} km/h" if r.get("computed_speed_kmh") else "—",
                "Elevation Gain": f"{r.get('elevation_m', 0):.0f} m" if r.get("elevation_m") else "—",
                "Avg HR": f"{r.get('avg_hr', 0):.0f} bpm" if r.get("avg_hr") else "—",
                "Calories": f"{r.get('calories', 0):,} kcal" if r.get("calories") else "—",
            })
        st.dataframe(pd.DataFrame(r_table_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 5: 🚶 WALKING
# ============================================================

with tab_walking:
    st.markdown("## 🚶 Walking Analytics & Consistency")
    st.markdown("Tracked walking sessions and daily step telemetry from Garmin.")

    walks_list = walking_analytics.get("walks", [])
    tot_walk_dist = walking_analytics.get("total_distance_km", 0.0)
    tot_walk_time = walking_analytics.get("total_moving_min", 0.0)
    avg_walk_pace = walking_analytics.get("avg_pace_formatted", "—")
    longest_walk_val = walking_analytics.get("longest_walk_km", 0.0)
    active_walk_days = walking_analytics.get("active_days", 0)
    avg_daily_walk_km = walking_analytics.get("avg_daily_km", 0.0)

    # 1. Walking KPIs
    c_w1, c_w2, c_w3, c_w4, c_w5 = st.columns(5)
    with c_w1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-walk">Total Distance</div>
                <div class="kpi-value">{tot_walk_dist:.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">{len(walks_list)} recorded walks</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_w2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-walk">Active Time</div>
                <div class="kpi-value">{format_duration_hm(tot_walk_time)}</div>
                <div class="kpi-sub">{tot_walk_time:.0f} moving mins</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_w3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-walk">Average Pace</div>
                <div class="kpi-value">{avg_walk_pace}</div>
                <div class="kpi-sub">Overall pace /km</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_w4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-walk">Longest Walk</div>
                <div class="kpi-value">{longest_walk_val:.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">Max single session</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_w5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-walk">Daily Average</div>
                <div class="kpi-value">{avg_daily_walk_km:.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">across {active_walk_days} active days</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Walking Charts
    if walks_list:
        st.markdown("### 📈 Walking Progression")
        w_df = pd.DataFrame(walks_list)
        w_df["date_clean"] = w_df["date"].apply(lambda d: str(d)[:10])
        w_c1, w_c2 = st.columns(2)
        with w_c1:
            c_w_dist = alt.Chart(w_df).mark_bar(color="#D97706", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("date_clean:N", title="Walk Date"),
                y=alt.Y("distance_km:Q", title="Distance (km)"),
                tooltip=[
                    alt.Tooltip("date_clean:N", title="Date"),
                    alt.Tooltip("name:N", title="Name"),
                    alt.Tooltip("distance_km:Q", title="Distance (km)"),
                    alt.Tooltip("duration_min:Q", title="Duration (min)"),
                ],
            ).properties(title="Walk Distance Progression")
            st.altair_chart(apply_chart_theme(c_w_dist), use_container_width=True)

        with w_c2:
            c_w_hr = alt.Chart(w_df).mark_line(point=True, color="#FBBF24").encode(
                x=alt.X("date_clean:N", title="Walk Date"),
                y=alt.Y("avg_hr:Q", title="Avg HR (bpm)", scale=alt.Scale(zero=False)),
                tooltip=[
                    alt.Tooltip("date_clean:N", title="Date"),
                    alt.Tooltip("name:N", title="Name"),
                    alt.Tooltip("avg_hr:Q", title="Avg HR"),
                ],
            ).properties(title="Heart Rate & Exertion")
            st.altair_chart(apply_chart_theme(c_w_hr), use_container_width=True)


# ============================================================
# TAB 6: 😴 SLEEP & RECOVERY
# ============================================================

with tab_sleep:
    st.markdown("## 😴 Garmin Sleep & Recovery Telemetry")
    st.markdown("Comprehensive sleep duration, sleep scores, overnight HRV, and resting heart rate trends.")

    sl_dur_fmt = sleep_analytics.get("avg_duration_formatted", "—")
    sl_score = sleep_analytics.get("avg_sleep_score")
    sl_hrv = sleep_analytics.get("avg_hrv")
    sl_rhr = sleep_analytics.get("avg_resting_hr")
    sl_days = sleep_analytics.get("total_days_tracked", 0)
    sl_dur_diff = sleep_analytics.get("duration_vs_prev_min")
    sl_score_diff = sleep_analytics.get("score_vs_prev")

    # 1. Sleep KPIs
    c_sl1, c_sl2, c_sl3, c_sl4, c_sl5 = st.columns(5)
    with c_sl1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-workout">Average Sleep</div>
                <div class="kpi-value">{sl_dur_fmt}</div>
                <div class="kpi-sub">{f"{sl_dur_diff:+d} min vs prior" if sl_dur_diff is not None else "Baseline period"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sl2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-workout">Avg Sleep Score</div>
                <div class="kpi-value">{f"{sl_score:.0f}" if sl_score else "—"} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span></div>
                <div class="kpi-sub">{f"{sl_score_diff:+.1f} pts vs prior" if sl_score_diff is not None else "Garmin Score"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sl3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">Avg Overnight HRV</div>
                <div class="kpi-value">{f"{sl_hrv:.0f}" if sl_hrv else "—"} <span style="font-size: 1rem; color: #94A3B8;">ms</span></div>
                <div class="kpi-sub">Autonomic recovery</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sl4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">Avg Resting HR</div>
                <div class="kpi-value">{f"{sl_rhr:.0f}" if sl_rhr else "—"} <span style="font-size: 1rem; color: #94A3B8;">bpm</span></div>
                <div class="kpi-sub">Cardiovascular rest</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sl5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-total">Tracked Nights</div>
                <div class="kpi-value">{sl_days}</div>
                <div class="kpi-sub">Garmin 965 sensor</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Sleep Charts
    sl_trends = sleep_analytics.get("daily_trends", [])
    if sl_trends:
        st.markdown("### 📈 Sleep & Recovery Progression")
        sl_df = pd.DataFrame(sl_trends)
        sl_c1, sl_c2 = st.columns(2)
        with sl_c1:
            c_sl_dur = alt.Chart(sl_df).mark_bar(color="#8B5CF6", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("date:N", title="Date"),
                y=alt.Y("duration_hours:Q", title="Sleep Duration (hours)"),
                tooltip=[
                    alt.Tooltip("date:N", title="Date"),
                    alt.Tooltip("duration_formatted:N", title="Duration"),
                    alt.Tooltip("score:Q", title="Score"),
                ],
            ).properties(title="Daily Sleep Duration (Hours)")
            st.altair_chart(apply_chart_theme(c_sl_dur), use_container_width=True)

        with sl_c2:
            c_sl_hrv = alt.Chart(sl_df).mark_line(point=True, color="#00D2FF").encode(
                x=alt.X("date:N", title="Date"),
                y=alt.Y("hrv:Q", title="Overnight HRV (ms)", scale=alt.Scale(zero=False)),
                tooltip=[
                    alt.Tooltip("date:N", title="Date"),
                    alt.Tooltip("hrv:Q", title="HRV (ms)"),
                    alt.Tooltip("resting_hr:Q", title="Resting HR"),
                ],
            ).properties(title="Overnight HRV & Resting HR Progression")
            st.altair_chart(apply_chart_theme(c_sl_hrv), use_container_width=True)

        st.markdown("### 📋 Sleep & Recovery Telemetry Log")
        sl_table = []
        for st_item in reversed(sl_trends):
            if st_item.get("duration_hours") or st_item.get("resting_hr"):
                sl_table.append({
                    "Date": format_date_clean(st_item.get("date")),
                    "Sleep Duration": st_item.get("duration_formatted", "—"),
                    "Sleep Score": f"{st_item.get('score'):.0f} / 100" if st_item.get("score") else "—",
                    "Overnight HRV": f"{st_item.get('hrv'):.0f} ms" if st_item.get("hrv") else "—",
                    "Resting HR": f"{st_item.get('resting_hr'):.0f} bpm" if st_item.get("resting_hr") else "—",
                    "Daily Steps": f"{st_item.get('steps'):,}" if st_item.get("steps") else "—",
                })
        st.dataframe(pd.DataFrame(sl_table), use_container_width=True, hide_index=True)


# ============================================================
# TAB 7: 📊 PERFORMANCE
# ============================================================

with tab_performance:
    st.markdown("## 📊 Cross-Sport Performance & Volume")
    st.markdown("Multi-sport training distribution, cross-training volume, and cardiovascular progression.")

    # 1. Multi-Sport Stacked Weekly Volume
    w_multi = performance_analytics.get("weekly_multi_sport", [])
    if w_multi:
        st.markdown("### 📈 Weekly Multi-Sport Volume Breakdown")
        w_m_df = pd.DataFrame(w_multi)
        c_multi = alt.Chart(w_m_df).mark_bar().encode(
            x=alt.X("week:N", title="Training Week"),
            y=alt.Y("hours:Q", title="Active Volume (Hours)"),
            color=alt.Color(
                "sport:N",
                scale=alt.Scale(
                    domain=["Swim", "Run", "Ride", "Walk", "Workout", "Other"],
                    range=["#0284C7", "#DB2777", "#059669", "#D97706", "#7C3AED", "#94A3B8"],
                ),
                title="Sport",
            ),
            tooltip=[
                alt.Tooltip("week:N", title="Week"),
                alt.Tooltip("sport:N", title="Sport"),
                alt.Tooltip("hours:Q", title="Hours"),
                alt.Tooltip("distance_km:Q", title="Distance (km)"),
            ],
        ).properties(title="Weekly Active Hours by Sport (Stacked)")
        st.altair_chart(apply_chart_theme(c_multi), use_container_width=True)

    # 2. Sport Distribution & Time Split
    st.markdown("### 🍰 Sport Distribution & Training Allocation")
    dist_map = performance_analytics.get("sport_distribution", {})
    if dist_map:
        dist_rows = []
        for sp_k, sp_v in dist_map.items():
            dist_rows.append({
                "Sport": f"{get_sport_icon(sp_k)} {sp_k}",
                "Sessions": sp_v.get("count"),
                "Total Distance": f"{sp_v.get('distance_km', 0):.2f} km",
                "Total Time": f"{sp_v.get('hours', 0):.1f} hours",
                "Training Load": f"{sp_v.get('load', 0):.0f}",
                "Energy (Calories)": f"{sp_v.get('calories', 0):,} kcal",
                "% of Total Time": f"{sp_v.get('percentage_time', 0):.1f}%",
            })
        st.dataframe(pd.DataFrame(dist_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 8: 📅 CALENDAR
# ============================================================

with tab_calendar:
    st.markdown("## 📅 Interactive Fitness Calendar")
    st.markdown("Color-coded activity calendar with multi-sport session inspector.")

    # Month selector
    cal_col1, cal_col2 = st.columns([1, 3])
    with cal_col1:
        current_year = today_date.year
        current_month = today_date.month
        month_names = list(calendar.month_name)[1:]
        sel_month_name = st.selectbox("Select Month", month_names, index=current_month - 1)
        sel_month = month_names.index(sel_month_name) + 1
        sel_year = st.selectbox("Select Year", [2024, 2025, 2026], index=2)

    # Activity map by date
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

    # Header row HTML
    header_html = "".join(f"<div class='cal-header-cell'>{h}</div>" for h in day_headers)

    # All calendar cells in a single uniform CSS grid
    cells_list = []
    for week in cal_matrix:
        for day_num in week:
            if day_num == 0:
                cells_list.append("<div class='cal-cell-empty'></div>")
            else:
                d_str = f"{sel_year:04d}-{sel_month:02d}-{day_num:02d}"
                acts = act_by_date.get(d_str, [])
                is_today = (d_str == str(today_date))
                cell_class = "cal-cell cal-cell-today" if is_today else "cal-cell"
                num_style = "color: #00D2FF !important;" if is_today else ""

                badge_html = ""
                if acts:
                    for act_item in acts:
                        sp_name = act_item.get("sport", "Activity")
                        chip_cls = get_sport_chip_class(sp_name)
                        d_km = act_item.get("distance_km") or 0.0
                        dur_m = act_item.get("moving_time_min") or act_item.get("duration_min") or 0.0
                        label = f"{get_sport_icon(sp_name)} {d_km:.1f}k" if d_km > 0 else f"{get_sport_icon(sp_name)} {dur_m:.0f}m"
                        badge_html += f"<span class='cal-badge {chip_cls}'>{label}</span>"
                else:
                    badge_html = "<span class='cal-rest'>Rest</span>"

                cells_list.append(
                    f"<div class='{cell_class}'><div class='cal-date-num' style='{num_style}'>{day_num}</div>{badge_html}</div>"
                )

    cells_html = "".join(cells_list)
    full_calendar_html = (
        f"<div style='width: 100%; margin-top: 10px;'>"
        f"<div class='cal-grid-header'>{header_html}</div>"
        f"<div class='cal-grid-body'>{cells_html}</div>"
        f"</div>"
    )
    if hasattr(st, "html"):
        st.html(full_calendar_html)
    else:
        st.markdown(full_calendar_html, unsafe_allow_html=True)

    # Interactive Day Inspector
    st.markdown("---")
    st.markdown("### 🔍 Day Inspector")
    insp_date = st.date_input("Select Date to Inspect", value=today_date)
    insp_str = str(insp_date)
    day_acts = act_by_date.get(insp_str, [])
    day_wel = next((w for w in wellness_records if str(w.get("id") or w.get("date") or "")[:10] == insp_str), None)

    if day_acts or day_wel:
        st.markdown(f"#### Activities & Sleep on `{format_date_clean(insp_str)}`")
        if day_wel and day_wel.get("sleepSecs"):
            sl_s = day_wel.get("sleepSecs", 0)
            st.info(f"🛌 **Garmin Sleep Log:** `{sl_s//3600}h {(sl_s%3600)//60:02d}m` · Score: `{day_wel.get('sleepScore', '—')}/100` · HRV: `{day_wel.get('hrv', '—')} ms` · RHR: `{day_wel.get('restingHR', '—')} bpm`")

        if day_acts:
            for da in day_acts:
                sp = da.get("sport", "Activity")
                with st.expander(f"{get_sport_icon(sp)} {da.get('name', sp)} ({sp}) — {da.get('distance_km', 0):.2f} km in {format_duration_hm(da.get('moving_time_min', 0))}", expanded=True):
                    st.markdown(
                        f"""
                        - **Distance:** `{da.get('distance_km', 0):.2f} km`
                        - **Moving Time:** `{da.get('moving_time_min', 0):.1f} min` (Elapsed: `{da.get('duration_min', 0):.1f} min`)
                        - **Average Heart Rate:** `{da.get('avg_hr', '—')} bpm` (Max: `{da.get('max_hr', '—')} bpm`)
                        - **Active Energy:** `{da.get('calories', '—')} kcal`
                        - **Training Load:** `{da.get('training_load', '—')}`
                        - **Source:** `{da.get('source', 'Garmin')}`
                        """
                    )
        else:
            st.info("Rest day — no workout sessions logged.")
    else:
        st.info(f"No activities or sleep records on {format_date_clean(insp_str)}.")


# ============================================================
# TAB 9: 📈 TRAINING LOAD
# ============================================================

with tab_load:
    st.markdown("## 📈 Training Load, Volume & Form")
    st.markdown("Physiological load, weekly stress progression, and recovery balance.")

    # Current vs Previous Week Comparison
    c_wk1, c_wk2 = st.columns(2)
    with c_wk1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 6px solid #00D2FF;">
                <div class="kpi-label label-swim">Current 7-Day Window</div>
                <div class="kpi-value">{sum(s.get('distance_km', 0) for s in current_week.values()):.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">Load: {sum(s.get('training_load', 0) for s in current_week.values()):.0f} · {sum(s.get('sessions', 0) for s in current_week.values())} sessions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_wk2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 6px solid #F59E0B;">
                <div class="kpi-label" style="color: #F59E0B;">Previous 7-Day Window</div>
                <div class="kpi-value">{sum(s.get('distance_km', 0) for s in previous_week.values()):.2f} <span style="font-size: 1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">Load: {sum(s.get('training_load', 0) for s in previous_week.values()):.0f} · {sum(s.get('sessions', 0) for s in previous_week.values())} sessions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Weekly Load Comparison Table
    st.markdown("### 📊 Sport-by-Sport 7-Day Comparison")
    comp_rows = []
    for sp_name in ["Swim", "Ride", "Walk", "Run"]:
        curr = current_week.get(sp_name, {})
        prev = previous_week.get(sp_name, {})
        c_dist = curr.get("distance_km", 0.0)
        p_dist = prev.get("distance_km", 0.0)
        c_load = curr.get("training_load", 0.0)
        p_load = prev.get("training_load", 0.0)

        comp_rows.append({
            "Sport": f"{get_sport_icon(sp_name)} {sp_name}",
            "Current Dist": f"{c_dist:.2f} km",
            "Prior Dist": f"{p_dist:.2f} km",
            "Distance Diff": f"{c_dist - p_dist:+.2f} km",
            "Current Load": f"{c_load:.0f}",
            "Prior Load": f"{p_load:.0f}",
            "Load Diff": f"{c_load - p_load:+.0f}",
        })
    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 10: 🏆 PERSONAL RECORDS
# ============================================================

with tab_records:
    st.markdown("## 🏆 Personal Records & Benchmark Bests")
    st.markdown("Verified best performances across all sports, calculated directly from your Garmin & Strava data.")

    pr_sw = personal_records.get("Swimming", [])
    pr_rn = personal_records.get("Running", [])
    pr_bk = personal_records.get("Cycling", [])
    pr_wk = personal_records.get("Walking", [])

    pr_tab_sw, pr_tab_rn, pr_tab_bk, pr_tab_wk = st.tabs([
        "🏊 Swimming PRs",
        "🏃 Running PRs",
        "🚴 Cycling PRs",
        "🚶 Walking PRs",
    ])

    with pr_tab_sw:
        if pr_sw:
            st.dataframe(pd.DataFrame(pr_sw), use_container_width=True, hide_index=True)
        else:
            st.info("No swimming records calculated yet.")

    with pr_tab_rn:
        if pr_rn:
            st.dataframe(pd.DataFrame(pr_rn), use_container_width=True, hide_index=True)
        else:
            st.info("No running records calculated yet.")

    with pr_tab_bk:
        if pr_bk:
            st.dataframe(pd.DataFrame(pr_bk), use_container_width=True, hide_index=True)
        else:
            st.info("No cycling records calculated yet.")

    with pr_tab_wk:
        if pr_wk:
            st.dataframe(pd.DataFrame(pr_wk), use_container_width=True, hide_index=True)
        else:
            st.info("No walking records calculated yet.")


# ============================================================
# TAB 11: ⚙️ DATA & SETTINGS
# ============================================================

with tab_settings:
    st.markdown("## ⚙️ Data Pipeline & Settings")
    st.markdown("Telemetry sources, caching status, and sync diagnostics.")

    c_st1, c_st2 = st.columns(2)
    with c_st1:
        st.markdown("### 🔌 Connected Data Sources")
        st.markdown(
            f"""
            - **Garmin Forerunner 965:** Synced via Intervals.icu API
            - **Intervals.icu API:** `{api_status.upper()}` ({tot_intervals} activities)
            - **Strava Archive:** `{strava_added} archive sessions loaded` ({tot_strava} total)
            - **Total Master Activities:** `{len(all_activities)} sessions`
            - **Wellness / Sleep Days:** `{len(wellness_records)} days`
            """
        )

    with c_st2:
        st.markdown("### 🔄 Cache & Maintenance")
        if st.button("🧹 Clear All Caches & Resync", use_container_width=True):
            st.cache_data.clear()
            st.success("Caches cleared! Reloading data...")
            st.rerun()

        if st.button("🗑️ Clear Saved Workout Plans", use_container_width=True):
            clear_plans()
            st.warning("All saved workout plans cleared.")
            st.rerun()

    # Saved plans preview
    saved_plans_list = get_plans()
    if saved_plans_list:
        st.markdown("---")
        st.markdown(f"### 🗄️ Saved Workout Plans ({len(saved_plans_list)} Plans)")
        for p_item in saved_plans_list:
            p_id = p_item.get("plan_id") or p_item.get("id") or str(uuid.uuid4())
            p_name = p_item.get("name") or f"{p_item.get('type', 'Custom')} Plan"
            p_dist = p_item.get("distance_m") or p_item.get("target_distance", 0)
            p_date = p_item.get("planned_date") or (p_item.get("created_at") or "")[:10] or "Unscheduled"
            with st.expander(f"🏊 {p_name} ({p_dist}m) — For {p_date}"):
                st.json(p_item)
                if st.button(f"Delete Plan {p_id}", key=f"del_plan_{p_id}"):
                    delete_plan(p_id)
                    st.rerun()
import sys
from pathlib import Path

# Add project root to sys.path so src imports work regardless of working directory
_app_dir = Path(__file__).resolve().parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

import calendar
from datetime import datetime, date, timedelta
import json
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
    format_pace,
)
from src.training.swim_paces import swim_pace_zones
from src.training.plan_store import save_plan, get_plans, delete_plan, clear_plans


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Fitness Dashboard",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HIGH CONTRAST & READABILITY CSS
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
    
    /* Main Container Padding (Desktop) */
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
    
    /* High-Contrast Custom Metric Cards */
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
        font-size: 0.88rem;
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
        font-size: 0.85rem;
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
        padding: 22px 26px;
        margin-bottom: 24px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 4px 0 8px 0;
    }
    .hero-text {
        font-size: 1.05rem;
        color: #E2E8F0 !important;
        line-height: 1.5;
        margin: 0;
    }

    /* Calendar Styling */
    .cal-cell {
        background: #151D2C;
        border: 1px solid #23324A;
        border-radius: 8px;
        padding: 8px 10px;
        min-height: 88px;
    }
    .cal-date-num {
        font-size: 0.95rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 6px;
    }
    .cal-badge {
        display: block;
        padding: 3px 6px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 4px;
        text-align: center;
        text-decoration: none;
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

    /* ============================================================
       MOBILE SCREEN OPTIMIZATIONS (@media max-width: 768px)
       ============================================================ */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 2.2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }

        /* Wrap columns gracefully into 2-column or 1-column grid on mobile */
        [data-testid="column"] {
            min-width: 47% !important;
            flex: 1 1 47% !important;
            margin-bottom: 6px !important;
        }

        /* Typography on small screens */
        h1 { font-size: 1.45rem !important; line-height: 1.25 !important; }
        h2 { font-size: 1.25rem !important; line-height: 1.25 !important; }
        h3 { font-size: 1.1rem !important; line-height: 1.25 !important; }
        h4 { font-size: 0.95rem !important; line-height: 1.25 !important; }

        /* KPI Cards on Mobile */
        .kpi-card {
            padding: 10px 12px !important;
            border-radius: 10px !important;
            margin-bottom: 6px !important;
        }
        .kpi-label {
            font-size: 0.74rem !important;
            margin-bottom: 3px !important;
        }
        .kpi-value {
            font-size: 1.4rem !important;
            line-height: 1.1 !important;
        }
        .kpi-sub {
            font-size: 0.74rem !important;
            margin-top: 2px !important;
        }

        /* Hero Banner on Mobile */
        .hero-banner {
            padding: 14px 16px !important;
            border-radius: 10px !important;
            margin-bottom: 14px !important;
        }
        .hero-title {
            font-size: 1.2rem !important;
            margin: 2px 0 6px 0 !important;
        }
        .hero-text {
            font-size: 0.88rem !important;
            line-height: 1.4 !important;
        }

        /* Calendar on Mobile */
        .cal-cell {
            padding: 4px 4px !important;
            min-height: 60px !important;
            border-radius: 6px !important;
        }
        .cal-date-num {
            font-size: 0.78rem !important;
            margin-bottom: 2px !important;
        }
        .cal-badge {
            font-size: 0.65rem !important;
            padding: 2px 3px !important;
            margin-bottom: 2px !important;
        }

        /* Gallery photos on mobile: 2-column fit */
        .stImage img {
            max-width: 100% !important;
            max-height: 160px !important;
            border-radius: 8px !important;
        }

        /* Tabs font on mobile */
        [data-baseweb="tab"] {
            padding: 6px 10px !important;
            font-size: 0.8rem !important;
            min-height: 36px !important;
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
    """Convert ISO date to readable string (e.g., Aug 23, 2026)."""
    if not date_str:
        return "—"
    try:
        dt = datetime.fromisoformat(str(date_str)[:10])
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(date_str)[:10]


def get_sport_icon(sport):
    icons = {
        "Swim": "🏊",
        "Ride": "🚴",
        "Walk": "🚶",
        "Run": "🏃",
        "Workout": "💪",
    }
    return icons.get(sport, "⚡")


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
    """Apply high-contrast dark theme to Altair charts."""
    return (
        chart.properties(height=height)
        .configure_axis(
            labelColor="#E2E8F0",
            titleColor="#F8FAFC",
            labelFontSize=12,
            titleFontSize=13,
            titleFontWeight="bold",
            gridColor="rgba(255, 255, 255, 0.1)",
            domainColor="#475569",
            tickColor="#475569",
        )
        .configure_legend(
            labelColor="#E2E8F0",
            titleColor="#F8FAFC",
            labelFontSize=12,
            titleFontSize=13,
            titleFontWeight="bold",
        )
        .configure_title(
            color="#FFFFFF",
            fontSize=15,
            fontWeight="bold",
        )
        .configure_view(
            strokeWidth=0
        )
    )


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <span style="font-size: 2.2rem;">🏊</span>
        <div>
            <h2 style="margin: 0; font-weight: 800; color: #FFFFFF; font-size: 1.3rem;">FITNESS AI</h2>
            <span style="font-size: 0.8rem; color: #38BDF8; font-weight: 700; text-transform: uppercase;">Training Engine</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")

# Data Source Filter
source_choice_label = st.sidebar.selectbox(
    "📦 Data Source",
    [
        "🔄 All Sources (Merged & Deduplicated)",
        "🟡 Intervals.icu (Garmin sync)",
        "🟠 Strava Archive",
    ],
    index=0,
    help="Unified views merge Garmin / Intervals.icu data with your full Strava export archive.",
)

source_filter_map = {
    "🔄 All Sources (Merged & Deduplicated)": "all",
    "🟡 Intervals.icu (Garmin sync)": "intervals",
    "🟠 Strava Archive": "strava",
}
source_filter = source_filter_map[source_choice_label]

st.sidebar.markdown("---")

# Time Window Presets
date_preset = st.sidebar.selectbox(
    "⏱️ Select Time Window",
    [
        "Default Period (Jul 1 - Aug 27, 2026)",
        "All Time (Full History · Oct 2025 – Present)",
        "Year to Date (2026)",
        "Last 90 Days",
        "Last 30 Days",
        "Last 14 Days",
        "Last 7 Days",
        "Custom Date Range",
    ],
    index=0,
)

today_date = date(2026, 8, 27)

if date_preset == "Default Period (Jul 1 - Aug 27, 2026)":
    start_val = date(2026, 7, 1)
    end_val = date(2026, 8, 27)
elif date_preset == "All Time (Full History · Oct 2025 – Present)":
    start_val = date(2025, 10, 1)
    end_val = today_date
elif date_preset == "Year to Date (2026)":
    start_val = date(2026, 1, 1)
    end_val = today_date
elif date_preset == "Last 90 Days":
    start_val = today_date - timedelta(days=90)
    end_val = today_date
elif date_preset == "Last 30 Days":
    start_val = today_date - timedelta(days=30)
    end_val = today_date
elif date_preset == "Last 14 Days":
    start_val = today_date - timedelta(days=14)
    end_val = today_date
elif date_preset == "Last 7 Days":
    start_val = today_date - timedelta(days=7)
    end_val = today_date
else:
    c_start, c_end = st.sidebar.columns(2)
    start_val = c_start.date_input("Start Date", date(2025, 10, 1))
    end_val = c_end.date_input("End Date", date(2026, 8, 27))

start_date_str = str(start_val)
end_date_str = str(end_val)

# Determine recommendation timing based on night cutoff (9 PM)
now = datetime.now()
is_night_cutoff = (now.hour >= 21)

if is_night_cutoff:
    target_plan_date = end_val + timedelta(days=1)
    plan_timing_label = "Tomorrow's"
    plan_timing_badge = "Tomorrow"
else:
    target_plan_date = end_val
    plan_timing_label = "Today's"
    plan_timing_badge = "Today"

target_plan_date_str = target_plan_date.strftime("%A, %b %d, %Y")
target_plan_date_short = target_plan_date.strftime("%b %d, %Y")

last_7d_start = end_val - timedelta(days=6)
last_7d_start_str = str(last_7d_start)

prev_7d_start = end_val - timedelta(days=13)
prev_7d_end = end_val - timedelta(days=7)

st.sidebar.markdown("---")


# ============================================================
# DATA CACHING & FETCHING
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def load_cached_dashboard_data(start_str, end_str, src_filter):
    return get_dashboard_data(start_str, end_str, source_filter=src_filter)


if st.sidebar.button("🔄 Refresh / Sync Live Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

with st.spinner("Loading athlete training data from Garmin, Intervals & Strava..."):
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

# Sidebar Status Badges
if source_filter == "all":
    st.sidebar.success(f"🟢 Intervals.icu ({tot_intervals}) + 🟠 Strava ({tot_strava})")
    st.sidebar.caption(f"⚡ Merged: **{strava_matched} synced** · **{strava_added} Strava archive sessions**")
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

st.sidebar.markdown("---")
with st.sidebar.expander("📱 View on iPhone / Mobile"):
    st.markdown(
        """
        **1. Ensure iPhone is on same Wi-Fi**  
        **2. Open Safari & visit:**  
        `http://192.168.0.10:8501`  
        
        *(Replace `192.168.0.10` with your PC's IP if changed)*  
        
        💡 **Tip:** Tap the Share button (📤) in Safari and choose **"Add to Home Screen"** to save it as an app icon!
        """
    )
st.sidebar.markdown("### 📊 Window Totals")
st.sidebar.markdown(f"**Total Distance:** `{total_dist_all:.1f} km`")
st.sidebar.markdown(f"**Total Active Time:** `{total_time_all / 60:.1f} hours`")
st.sidebar.markdown(f"**Total Training Load:** `{total_load_all:.0f}`")

st.sidebar.markdown("---")
st.sidebar.caption("🚀 **Click & Go**: Double-click the desktop shortcut anytime to open this dashboard.")


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🏊 My Fitness Dashboard")

st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: flex-end; flex-wrap: wrap; gap: 8px; margin-bottom: 18px;">
        <span class="sport-chip chip-swim">Garmin 965</span>
        <span class="sport-chip chip-ride">25m Pool</span>
        <span class="sport-chip chip-strava">Strava Connected ({tot_strava} activities)</span>
    </div>
    """,
    unsafe_allow_html=True,
)


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
            <div style="flex: 1; min-width: 320px;">
                <span style="font-size: 0.85rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.06em; text-transform: uppercase;">
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
            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                <div style="text-align: center; background: #1F293D; padding: 10px 16px; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Last Swim</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #38BDF8;">{f"{days_since_swim}d ago" if days_since_swim is not None else "—"}</div>
                </div>
                <div style="text-align: center; background: #1F293D; padding: 10px 16px; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Last Ride</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #4ADE80;">{f"{days_since_ride}d ago" if days_since_ride is not None else "—"}</div>
                </div>
                <div style="text-align: center; background: #1F293D; padding: 10px 16px; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Last Walk</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #FBBF24;">{f"{days_since_walk}d ago" if days_since_walk is not None else "—"}</div>
                </div>
                <div style="text-align: center; background: #1F293D; padding: 10px 16px; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Last Run</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #F472B6;">{f"{days_since_run}d ago" if days_since_run is not None else "—"}</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DASHBOARD TABS
# ============================================================

running_analytics = data.get("running_analytics", {})

tab_overview, tab_plan, tab_calendar, tab_comparison, tab_trends, tab_running, tab_activities, tab_wellness, tab_history = st.tabs([
    "🏠 Overview & KPIs",
    f"🎯 {plan_timing_label} Swim Plan",
    "📅 Training Calendar",
    "📊 Weekly Comparison",
    "📈 Swim Analytics & Baseline",
    "🏃 Running Analytics & Splits",
    "📋 Daily Activity Deep Dive",
    "💓 Wellness & Recovery",
    "🗄️ Saved Plans Library",
])


# ============================================================
# TAB 1: OVERVIEW & KPIS
# ============================================================

with tab_overview:
    # ------------------------------------------------------------
    # TODAY'S GARMIN SLEEP & RECOVERY CARD
    # ------------------------------------------------------------
    today_iso = str(today_date)
    today_wellness = next((w for w in wellness_records if w.get("id") == today_iso or w.get("date") == today_iso), None)
    if not today_wellness and wellness_records:
        today_wellness = wellness_records[-1]

    yesterday_iso = str(today_date - timedelta(days=1))
    yesterday_wellness = next((w for w in wellness_records if w.get("id") == yesterday_iso or w.get("date") == yesterday_iso), None)

    if today_wellness:
        t_sleep_sec = today_wellness.get("sleepSecs")
        t_sleep_score = today_wellness.get("sleepScore")
        t_rhr = today_wellness.get("restingHR")
        t_hrv = today_wellness.get("hrv")
        t_steps = today_wellness.get("steps")
        y_rhr = yesterday_wellness.get("restingHR") if yesterday_wellness else None
        rhr_diff = (t_rhr - y_rhr) if (t_rhr is not None and y_rhr is not None) else None

        if t_sleep_sec or t_rhr or t_hrv:
            t_hours = int(t_sleep_sec // 3600) if t_sleep_sec else 0
            t_mins = int((t_sleep_sec % 3600) // 60) if t_sleep_sec else 0
            dur_display = f"{t_hours}h {t_mins:02d}m" if t_sleep_sec else "—"
            score_badge = f"{t_sleep_score:.0f}/100" if t_sleep_score else "Tracked"

            st.markdown(
                f"""
                <div style="background: #111827; border: 1px solid #23324A; border-left: 6px solid #8B5CF6; border-radius: 12px; padding: 18px 22px; margin-bottom: 22px; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
                        <div>
                            <span style="font-size: 0.82rem; font-weight: 800; color: #A78BFA; text-transform: uppercase; letter-spacing: 0.05em;">
                                🌙 TODAY'S GARMIN SLEEP & RECOVERY · {format_date_clean(today_wellness.get('id', today_iso)).upper()}
                            </span>
                            <h3 style="margin: 3px 0 0 0; color: #FFFFFF; font-size: 1.35rem; font-weight: 800;">
                                Garmin 965 Sleep & Recovery Telemetry
                            </h3>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <span class="sport-chip chip-workout" style="background: #6D28D9;">Score: {score_badge}</span>
                            <span class="sport-chip chip-swim" style="background: #0284C7;">HRV: {f"{t_hrv:.0f} ms" if t_hrv else "—"}</span>
                            <span class="sport-chip chip-ride" style="background: #059669;">RHR: {f"{t_rhr:.0f} bpm" if t_rhr else "—"}</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
                        <div style="background: #151D2C; border: 1px solid #23324A; border-radius: 10px; padding: 12px 16px;">
                            <div style="font-size: 0.8rem; font-weight: 700; color: #A78BFA; text-transform: uppercase;">🛌 Sleep Duration</div>
                            <div style="font-size: 1.65rem; font-weight: 800; color: #FFFFFF;">{dur_display}</div>
                            <div style="font-size: 0.8rem; color: #94A3B8;">{f"{t_sleep_sec:,} sec recorded" if t_sleep_sec else "No duration log"}</div>
                        </div>
                        <div style="background: #151D2C; border: 1px solid #23324A; border-radius: 10px; padding: 12px 16px;">
                            <div style="font-size: 0.8rem; font-weight: 700; color: #F472B6; text-transform: uppercase;">🎯 Sleep Score</div>
                            <div style="font-size: 1.65rem; font-weight: 800; color: #FFFFFF;">{f"{t_sleep_score:.0f}" if t_sleep_score else "—"} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span></div>
                            <div style="font-size: 0.8rem; color: #34D399; font-weight: 600;">Fair Quality · Restful</div>
                        </div>
                        <div style="background: #151D2C; border: 1px solid #23324A; border-radius: 10px; padding: 12px 16px;">
                            <div style="font-size: 0.8rem; font-weight: 700; color: #34D399; text-transform: uppercase;">⚡ Overnight HRV</div>
                            <div style="font-size: 1.65rem; font-weight: 800; color: #FFFFFF;">{f"{t_hrv:.1f}" if t_hrv else "—"} <span style="font-size: 1rem; color: #94A3B8;">ms</span></div>
                            <div style="font-size: 0.8rem; color: #34D399; font-weight: 600;">Balanced Recovery Status</div>
                        </div>
                        <div style="background: #151D2C; border: 1px solid #23324A; border-radius: 10px; padding: 12px 16px;">
                            <div style="font-size: 0.8rem; font-weight: 700; color: #F87171; text-transform: uppercase;">💓 Resting Heart Rate</div>
                            <div style="font-size: 1.65rem; font-weight: 800; color: #FFFFFF;">{f"{t_rhr:.0f}" if t_rhr else "—"} <span style="font-size: 1rem; color: #94A3B8;">bpm</span></div>
                            <div style="font-size: 0.8rem; color: #38BDF8;">{f"↓ {abs(rhr_diff)} bpm vs yesterday" if (rhr_diff is not None and rhr_diff < 0) else "Optimal recovery baseline"}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader(f"Training Overview · Last 7 Days ({format_date_clean(last_7d_start_str)} – {format_date_clean(end_date_str)})")

    swim_curr = current_week.get("Swim", {})
    ride_curr = current_week.get("Ride", {})
    walk_curr = current_week.get("Walk", {})
    run_curr = current_week.get("Run", {})
    workout_curr = current_week.get("Workout", {})

    total_curr_load = sum(s.get("training_load", 0) for s in current_week.values())
    total_curr_dist = sum(s.get("distance_km", 0) for s in current_week.values())
    total_curr_time = sum(s.get("duration_min", 0) for s in current_week.values())

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">🏊 Swim (7d)</div>
                <div class="kpi-value">{swim_curr.get('distance_km', 0):.2f} <span style="font-size: 1.1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">{swim_curr.get('sessions', 0)} sessions · {swim_curr.get('duration_min', 0):.0f} min</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-load">🔥 Swim Load</div>
                <div class="kpi-value">{swim_curr.get('training_load', 0):.0f}</div>
                <div class="kpi-sub">Training Load Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-ride">🚴 Ride (7d)</div>
                <div class="kpi-value">{ride_curr.get('distance_km', 0):.2f} <span style="font-size: 1.1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">{ride_curr.get('sessions', 0)} sessions · {ride_curr.get('duration_min', 0):.0f} min</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-walk">🚶 Walk (7d)</div>
                <div class="kpi-value">{walk_curr.get('distance_km', 0):.2f} <span style="font-size: 1.1rem; color: #94A3B8;">km</span></div>
                <div class="kpi-sub">{walk_curr.get('sessions', 0)} sessions · {walk_curr.get('duration_min', 0):.0f} min</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-total">⚡ Total 7d Load</div>
                <div class="kpi-value">{total_curr_load:.0f}</div>
                <div class="kpi-sub">{total_curr_dist:.1f} km across sports</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label label-swim">🏊 Swim Gap</div>
                <div class="kpi-value">{days_since_swim if days_since_swim is not None else "—"} <span style="font-size: 1.1rem; color: #94A3B8;">days</span></div>
                <div class="kpi-sub">{'Rebuild endurance' if (days_since_swim or 0) >= 4 else 'Regular rhythm'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Overview Visualizations
    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        st.markdown("#### 📊 Daily Training Load (Selected Window)")
        if activities:
            df_act = pd.DataFrame(activities)
            df_act["date_only"] = df_act["date"].str[:10]
            df_act["formatted_date"] = df_act["date"].apply(format_date_clean)
            df_recent = df_act.sort_values("date_only").tail(35)

            chart_load = (
                alt.Chart(df_recent)
                .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                .encode(
                    x=alt.X("date_only:N", title="Activity Date", axis=alt.Axis(labelAngle=-40)),
                    y=alt.Y("training_load:Q", title="Training Load"),
                    color=alt.Color(
                        "sport:N",
                        scale=alt.Scale(
                            domain=["Swim", "Ride", "Walk", "Run", "Workout"],
                            range=["#00D2FF", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"],
                        ),
                        title="Sport",
                    ),
                    tooltip=[
                        alt.Tooltip("formatted_date:N", title="Date"),
                        alt.Tooltip("sport:N", title="Sport"),
                        alt.Tooltip("name:N", title="Name"),
                        alt.Tooltip("distance_km:Q", title="Distance (km)", format=".2f"),
                        alt.Tooltip("training_load:Q", title="Training Load", format=".0f"),
                        alt.Tooltip("duration_min:Q", title="Duration (min)", format=".0f"),
                        alt.Tooltip("source:N", title="Source"),
                    ],
                )
            )
            st.altair_chart(apply_chart_theme(chart_load, height=320), use_container_width=True)
        else:
            st.info("No activity records available in the selected window.")

    with chart_col2:
        st.markdown("#### ⚡ Sport Volume Distribution")
        sport_dist_data = []
        for sport, stats in summary.items():
            sport_dist_data.append({
                "Sport": sport,
                "Distance (km)": stats.get("distance_km", 0),
                "Load": stats.get("training_load", 0),
                "Sessions": stats.get("sessions", 0),
            })
        if sport_dist_data:
            df_pie = pd.DataFrame(sport_dist_data)
            pie_chart = (
                alt.Chart(df_pie)
                .mark_arc(innerRadius=50, stroke="#151D2C", strokeWidth=2)
                .encode(
                    theta=alt.Theta(field="Distance (km)", type="quantitative"),
                    color=alt.Color(
                        field="Sport",
                        type="nominal",
                        scale=alt.Scale(
                            domain=["Swim", "Ride", "Walk", "Run", "Workout"],
                            range=["#00D2FF", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"],
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip("Sport:N"),
                        alt.Tooltip("Distance (km):Q", format=".2f"),
                        alt.Tooltip("Sessions:Q"),
                        alt.Tooltip("Load:Q", format=".0f"),
                    ],
                )
            )
            st.altair_chart(apply_chart_theme(pie_chart, height=320), use_container_width=True)
        else:
            st.info("No volume data available.")


# ============================================================
# TAB 2: SWIM PLAN
# ============================================================

with tab_plan:
    st.header(f"🎯 {plan_timing_label} Swim Workout Plan")
    st.markdown(f"<span style='color: #38BDF8; font-weight: 700; font-size: 1.15rem;'>📅 Scheduled for: {target_plan_date_str} ({plan_timing_badge})</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    plan_type = plan.get("type", "Endurance")
    target_dist = plan.get("target_distance", 1500)
    pool_len = plan.get("pool_length", 25)
    total_laps = plan.get("total_laps", target_dist // 25)
    duration_str = plan.get("duration", "45-60 min")
    goal_str = plan.get("goal", "Build aerobic endurance and maintain technique.")
    coach_rationale = plan.get("coaching_rationale", "Periodized swimming session matched to recent training volume.")
    readiness_score = plan.get("readiness_score", 80)

    # High-Contrast Plan Hero
    st.markdown(
        f"""
        <div style="background: #111827; border: 2px solid #0284C7; border-radius: 14px; padding: 22px 26px; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px;">
                        <span class="sport-chip chip-swim" style="font-size: 0.95rem;">{plan_type} Workout</span>
                        <span style="color: #38BDF8; font-weight: 700; font-size: 0.95rem; background: rgba(56,189,248,0.12); padding: 4px 12px; border-radius: 6px; border: 1px solid rgba(56,189,248,0.3);">
                            📅 {target_plan_date_str} ({plan_timing_badge})
                        </span>
                        <span class="sport-chip chip-workout" style="background: #0284C7;">Readiness: {readiness_score:.0f}/100</span>
                    </div>
                    <h1 style="margin: 6px 0 6px 0; color: #FFFFFF; font-size: 2.1rem; font-weight: 800;">
                        {target_dist} m · {duration_str}
                    </h1>
                    <div style="color: #E2E8F0; font-size: 1.05rem; font-weight: 600;">
                        🏊 <strong>{pool_len}m Pool</strong> · <strong>{total_laps} Total Laps</strong> · Baseline Pace: <strong style="color:#38BDF8;">{format_pace(baseline_pace)}</strong>
                    </div>
                </div>
                <div style="max-width: 460px; background: #1E293B; padding: 14px 18px; border-radius: 10px; border-left: 4px solid #38BDF8;">
                    <div style="font-size: 0.85rem; color: #38BDF8; font-weight: 800; text-transform: uppercase;">🤖 AI Coach Rationale</div>
                    <div style="font-size: 0.95rem; color: #FFFFFF; font-weight: 500; margin: 4px 0 8px 0; line-height: 1.4;">{coach_rationale}</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 700; text-transform: uppercase;">Goal: <span style="color:#E2E8F0; font-weight:600; text-transform:none;">{goal_str}</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("📋 Workout Structure & Sets")

    sets = plan.get("sets", [])
    for index, workout_set in enumerate(sets, start=1):
        if isinstance(workout_set, str):
            st.info(f"**Set {index}:** {workout_set}")
            continue

        reps = workout_set.get("reps", 1)
        dist = workout_set.get("distance", 0)
        tot_dist = workout_set.get("total_distance", dist * reps)
        tot_laps = workout_set.get("total_laps", tot_dist // 25)
        stroke = workout_set.get("stroke", "Freestyle")
        purpose = workout_set.get("purpose", "")
        pace = workout_set.get("pace", "")
        rest = workout_set.get("rest", "None")
        stroke_pattern = workout_set.get("stroke_pattern", stroke)

        set_title = f"{dist}m" if reps == 1 else f"{reps} × {dist}m"
        expanded = (index == 1 or index == 2)

        with st.expander(
            f"🏊 Set {index}: {set_title} · {stroke} · {purpose}",
            expanded=expanded,
        ):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Distance", f"{tot_dist}m", f"{reps} rep(s)" if reps > 1 else None)
            c2.metric("Total Laps", f"{tot_laps} laps", f"Pool: {pool_len}m")
            c3.metric("Target Pace", pace)
            c4.metric("Rest Interval", rest if rest != "None" else "No Rest")

            st.markdown("---")
            if stroke == "Mixed":
                st.markdown(f"**Stroke Breakdown:** `{stroke_pattern}`")
            else:
                st.markdown(f"**Stroke:** `{stroke}`")
            st.markdown(f"**Purpose:** {purpose}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("⚙️ Customize & Save Custom Plan to Library")

    custom_col1, custom_col2, custom_col3, custom_col4 = st.columns([2, 2, 2, 2])

    with custom_col1:
        workout_types_list = ["Endurance", "Tempo", "Intervals", "Pyramid", "Recovery"]
        custom_type = st.selectbox(
            "Workout Type",
            workout_types_list,
            index=workout_types_list.index(plan_type) if plan_type in workout_types_list else 0,
            key="custom_plan_type_select",
        )

    with custom_col2:
        custom_date = st.date_input(
            "Scheduled Date",
            target_plan_date,
            key="custom_plan_date_picker",
        )

    with custom_col3:
        custom_distance = st.slider(
            "Target Distance (m)",
            min_value=1000,
            max_value=3500,
            value=int(target_dist),
            step=100,
            key="custom_plan_dist_slider",
        )

    with custom_col4:
        st.write("")
        st.write("")
        if st.button("💾 Save Plan to Library", use_container_width=True, key="save_custom_plan_btn"):
            if custom_type == "Endurance":
                new_plan = endurance_workout(
                    target_distance=custom_distance,
                    easy_min=pace_zones["easy"]["min"],
                    easy_max=pace_zones["easy"]["max"],
                    endurance_min=pace_zones["endurance"]["min"],
                    endurance_max=pace_zones["endurance"]["max"],
                )
            elif custom_type == "Tempo":
                new_plan = tempo_workout(
                    target_distance=custom_distance,
                    easy_min=pace_zones["easy"]["min"],
                    easy_max=pace_zones["easy"]["max"],
                    tempo_min=pace_zones["tempo"]["min"],
                    tempo_max=pace_zones["tempo"]["max"],
                )
            elif custom_type == "Intervals":
                new_plan = interval_workout(
                    target_distance=custom_distance,
                    easy_min=pace_zones["easy"]["min"],
                    easy_max=pace_zones["easy"]["max"],
                    interval_min=pace_zones["interval"]["min"],
                    interval_max=pace_zones["interval"]["max"],
                )
            elif custom_type == "Pyramid":
                new_plan = pyramid_workout(
                    target_distance=custom_distance,
                    easy_min=pace_zones["easy"]["min"],
                    easy_max=pace_zones["easy"]["max"],
                    tempo_min=pace_zones["tempo"]["min"],
                    tempo_max=pace_zones["tempo"]["max"],
                    interval_min=pace_zones["interval"]["min"],
                    interval_max=pace_zones["interval"]["max"],
                )
            else:
                new_plan = recovery_workout(
                    target_distance=custom_distance,
                    easy_min=pace_zones["easy"]["min"],
                    easy_max=pace_zones["easy"]["max"],
                )

            import uuid
            new_plan["plan_id"] = str(uuid.uuid4())
            new_plan["planned_date"] = str(custom_date)
            new_plan["coaching_rationale"] = f"Custom {custom_type} workout scheduled by athlete."
            save_plan(new_plan)
            st.success(f"✅ {custom_type} workout saved for {custom_date} to `training_plans.json`!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🎯 Personalized Swim Pace Zones")
    st.caption(f"Calculated from your {len(swim_baseline)} long endurance baseline swims ({format_pace(baseline_pace)}/100m)")

    zone_rows = [
        {"Zone": "Easy / Warm-up / Cool-down", "Pace Range (/100m)": f"{format_pace(pace_zones['easy']['min'])} - {format_pace(pace_zones['easy']['max'])}", "Target Purpose": "Aerobic warm-up & active recovery"},
        {"Zone": "Endurance (Baseline)", "Pace Range (/100m)": f"{format_pace(pace_zones['endurance']['min'])} - {format_pace(pace_zones['endurance']['max'])}", "Target Purpose": "Sustainable aerobic volume"},
        {"Zone": "Tempo", "Pace Range (/100m)": f"{format_pace(pace_zones['tempo']['min'])} - {format_pace(pace_zones['tempo']['max'])}", "Target Purpose": "Lactate threshold & rhythm"},
        {"Zone": "Intervals / Speed", "Pace Range (/100m)": f"{format_pace(pace_zones['interval']['min'])} - {format_pace(pace_zones['interval']['max'])}", "Target Purpose": "VO2 max & high cadence speed"},
    ]
    st.dataframe(pd.DataFrame(zone_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 3: TRAINING CALENDAR
# ============================================================

with tab_calendar:
    st.header("📅 Training Calendar Grid")
    st.caption("🏊 Swim   🚴 Ride   🚶 Walk   🏃 Run   💪 Workout")

    # Group activities by date
    activities_by_date = {}
    available_months_set = set()

    for activity in all_activities:
        date_str = activity.get("date", "")[:10]
        if date_str:
            if date_str not in activities_by_date:
                activities_by_date[date_str] = []
            activities_by_date[date_str].append(activity)
            try:
                dt_obj = datetime.fromisoformat(date_str)
                available_months_set.add((dt_obj.year, dt_obj.month))
            except Exception:
                pass

    sorted_months = sorted(list(available_months_set), reverse=True)
    if not sorted_months:
        sorted_months = [(2026, 8), (2026, 7)]

    month_display_names = [f"{calendar.month_name[m]} {y}" for y, m in sorted_months]

    cal_col1, cal_col2 = st.columns([2, 4])
    with cal_col1:
        month_choice = st.selectbox(
            "Select Calendar Month",
            month_display_names,
            index=0,
        )

    chosen_idx = month_display_names.index(month_choice)
    cal_year, cal_month = sorted_months[chosen_idx]

    st.subheader(f"{calendar.month_name[cal_month]} {cal_year}")

    weekday_cols = st.columns(7)
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for idx, day in enumerate(weekdays):
        with weekday_cols[idx]:
            st.markdown(f"<div style='text-align:center; font-weight:800; color:#38BDF8; font-size:1rem; margin-bottom:8px;'>{day}</div>", unsafe_allow_html=True)

    month_weeks = calendar.monthcalendar(cal_year, cal_month)

    for week in month_weeks:
        cols = st.columns(7)
        for idx, day_number in enumerate(week):
            with cols[idx]:
                if day_number == 0:
                    st.write("")
                    continue

                d_str = f"{cal_year:04d}-{cal_month:02d}-{day_number:02d}"
                day_acts = activities_by_date.get(d_str, [])

                with st.container(border=True):
                    st.markdown(f"<div class='cal-date-num'>{day_number}</div>", unsafe_allow_html=True)
                    if not day_acts:
                        st.markdown("<span style='color: #64748B; font-size: 0.8rem;'>Rest</span>", unsafe_allow_html=True)
                    for act in day_acts:
                        sport = act.get("sport", "Activity")
                        dist = act.get("distance_km") or 0
                        load = act.get("training_load") or 0
                        dur = act.get("duration_min") or 0

                        if sport == "Swim":
                            st.markdown(f"<span class='cal-badge chip-swim'>🏊 {dist:.2f}k · L{load:.0f}</span>", unsafe_allow_html=True)
                        elif sport == "Ride":
                            st.markdown(f"<span class='cal-badge chip-ride'>🚴 {dist:.2f}k · L{load:.0f}</span>", unsafe_allow_html=True)
                        elif sport == "Walk":
                            st.markdown(f"<span class='cal-badge chip-walk'>🚶 {dist:.2f}k · L{load:.0f}</span>", unsafe_allow_html=True)
                        elif sport == "Run":
                            st.markdown(f"<span class='cal-badge chip-run'>🏃 {dist:.2f}k · L{load:.0f}</span>", unsafe_allow_html=True)
                        elif sport == "Workout":
                            st.markdown(f"<span class='cal-badge chip-workout'>💪 {dur:.0f}m · L{load:.0f}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='cal-badge chip-rest'>⚡ {dist:.1f}k · L{load:.0f}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔍 Inspect Day Details from Calendar")
    available_dates = sorted(activities_by_date.keys(), reverse=True)
    if available_dates:
        insp_date = st.selectbox(
            "Choose a date to view full workout details",
            available_dates,
            format_func=format_date_clean,
            key="calendar_date_inspector",
        )
        insp_activities = activities_by_date.get(insp_date, [])

        st.markdown(f"#### Activities on `{format_date_clean(insp_date)}` ({len(insp_activities)} session(s))")
        for a_idx, act in enumerate(insp_activities, 1):
            sport = act.get("sport", "")
            icon = get_sport_icon(sport)
            source_tag = act.get("source", "Activity")
            with st.expander(f"{icon} {act.get('name', 'Activity')} · {act.get('distance_km', 0):.2f} km · {act.get('duration_min', 0):.0f} min · Load {act.get('training_load', 0):.0f} ({source_tag})", expanded=True):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Distance", f"{act.get('distance_km', 0):.2f} km")
                m2.metric("Duration", f"{act.get('duration_min', 0):.1f} min")
                m3.metric("Avg HR", f"{act.get('avg_hr', '—')} bpm" if act.get("avg_hr") else "—")
                m4.metric("Load", f"{act.get('training_load', 0):.0f}")

                if act.get("description"):
                    st.markdown(f"**Notes:** {act.get('description')}")

                # Display media if available
                media_items = act.get("media", [])
                if media_items:
                    st.markdown("##### 📸 Attached Photos:")
                    m_cols = st.columns(min(len(media_items), 4) or 1)
                    for m_idx, m_rel in enumerate(media_items):
                        m_path = get_strava_media_path(m_rel)
                        if m_path and m_path.exists():
                            with m_cols[m_idx % len(m_cols)]:
                                st.image(str(m_path), caption=f"Photo #{m_idx+1}", width=220)


# ============================================================
# TAB 4: WEEKLY COMPARISON
# ============================================================

with tab_comparison:
    st.header("📊 Weekly Training Comparison")
    st.markdown(
        f"<span style='color:#94A3B8; font-size:1rem;'>"
        f"Current 7-Day Window (<strong>{format_date_clean(last_7d_start_str)} – {format_date_clean(end_date_str)}</strong>) vs "
        f"Previous 7-Day Window (<strong>{format_date_clean(str(prev_7d_start))} – {format_date_clean(str(prev_7d_end))}</strong>)"
        f"</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    comparison_rows = []
    sports = sorted(set(list(current_week.keys()) + list(previous_week.keys())))

    for sp in sports:
        curr = current_week.get(sp, {})
        prev = previous_week.get(sp, {})

        c_dist = round(curr.get("distance_km", 0), 2)
        p_dist = round(prev.get("distance_km", 0), 2)
        c_load = round(curr.get("training_load", 0), 1)
        p_load = round(prev.get("training_load", 0), 1)
        c_dur = round(curr.get("duration_min", 0), 1)
        p_dur = round(prev.get("duration_min", 0), 1)

        comparison_rows.append({
            "Sport": sp,
            "Current Sessions": curr.get("sessions", 0),
            "Previous Sessions": prev.get("sessions", 0),
            "Current Distance (km)": c_dist,
            "Previous Distance (km)": p_dist,
            "Current Duration (min)": c_dur,
            "Previous Duration (min)": p_dur,
            "Current Load": c_load,
            "Previous Load": p_load,
        })

    if comparison_rows:
        st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        v_col1, v_col2 = st.columns(2)

        with v_col1:
            st.markdown("#### 🏃 Distance Comparison (km)")
            chart_df = []
            for row in comparison_rows:
                chart_df.append({"Sport": row["Sport"], "Period": "Current 7d", "Distance": row["Current Distance (km)"]})
                chart_df.append({"Sport": row["Sport"], "Period": "Previous 7d", "Distance": row["Previous Distance (km)"]})
            df_dist_comp = pd.DataFrame(chart_df)
            dist_bar = (
                alt.Chart(df_dist_comp)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("Period:N", title=None, axis=alt.Axis(labels=True)),
                    y=alt.Y("Distance:Q", title="Distance (km)"),
                    color=alt.Color("Period:N", scale=alt.Scale(domain=["Current 7d", "Previous 7d"], range=["#00D2FF", "#475569"]), title="Window"),
                    column=alt.Column("Sport:N", title="Sport", header=alt.Header(titleColor="#FFFFFF", labelColor="#FFFFFF", labelFontSize=13)),
                    tooltip=["Sport", "Period", alt.Tooltip("Distance:Q", format=".2f")],
                )
            )
            st.altair_chart(apply_chart_theme(dist_bar, height=280))

        with v_col2:
            st.markdown("#### 🔥 Training Load Comparison")
            chart_df_load = []
            for row in comparison_rows:
                chart_df_load.append({"Sport": row["Sport"], "Period": "Current 7d", "Load": row["Current Load"]})
                chart_df_load.append({"Sport": row["Sport"], "Period": "Previous 7d", "Load": row["Previous Load"]})
            df_load_comp = pd.DataFrame(chart_df_load)
            load_bar = (
                alt.Chart(df_load_comp)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("Period:N", title=None, axis=alt.Axis(labels=True)),
                    y=alt.Y("Load:Q", title="Training Load"),
                    color=alt.Color("Period:N", scale=alt.Scale(domain=["Current 7d", "Previous 7d"], range=["#F87171", "#475569"]), title="Window"),
                    column=alt.Column("Sport:N", title="Sport", header=alt.Header(titleColor="#FFFFFF", labelColor="#FFFFFF", labelFontSize=13)),
                    tooltip=["Sport", "Period", alt.Tooltip("Load:Q", format=".0f")],
                )
            )
            st.altair_chart(apply_chart_theme(load_bar, height=280))

    st.markdown("---")
    st.subheader("📋 Entire Query Window Multi-Sport Summary")
    summary_rows = []
    for sp, val in summary.items():
        summary_rows.append({
            "Sport": sp,
            "Total Sessions": val.get("sessions", 0),
            "Total Distance (km)": val.get("distance_km", 0),
            "Total Duration (min)": val.get("duration_min", 0),
            "Moving Time (min)": val.get("moving_time_min", 0),
            "Total Training Load": val.get("training_load", 0),
            "Total Calories (kcal)": val.get("calories", 0),
        })
    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 5: SWIM ANALYTICS & BASELINE
# ============================================================

with tab_trends:
    st.header("📈 Swimming Trends & Long-Swim Baseline")

    t_col1, t_col2 = st.columns(2)

    with t_col1:
        st.subheader("Weekly Swimming Progression")
        if weekly_trends:
            df_trends = pd.DataFrame(weekly_trends)
            trend_chart = (
                alt.Chart(df_trends)
                .mark_bar(color="#00D2FF", cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                .encode(
                    x=alt.X("week:N", title="ISO Week", axis=alt.Axis(labelAngle=-40)),
                    y=alt.Y("distance_km:Q", title="Weekly Volume (km)"),
                    tooltip=[
                        alt.Tooltip("week:N", title="Week"),
                        alt.Tooltip("sessions:Q", title="Sessions"),
                        alt.Tooltip("distance_km:Q", title="Volume (km)", format=".2f"),
                        alt.Tooltip("time_min:Q", title="Total Time (min)", format=".0f"),
                        alt.Tooltip("training_load:Q", title="Load", format=".0f"),
                        alt.Tooltip("avg_hr:Q", title="Avg HR (bpm)", format=".0f"),
                    ],
                )
            )
            st.altair_chart(apply_chart_theme(trend_chart, height=300), use_container_width=True)
            st.dataframe(df_trends, use_container_width=True, hide_index=True)
        else:
            st.info("No swimming trend records available.")

    with t_col2:
        st.subheader(f"Endurance Swims Baseline (≥ 1.5 km · {len(swim_baseline)} sessions)")
        if swim_baseline:
            df_base = pd.DataFrame(swim_baseline)
            df_base["pace_formatted"] = df_base["pace_seconds"].apply(lambda p: format_pace(p) if pd.notnull(p) else "—")
            df_base["date_formatted"] = df_base["date"].apply(format_date_clean)

            pace_chart = (
                alt.Chart(df_base)
                .mark_line(point=alt.OverlayMarkDef(color="#00D2FF", size=70), color="#38BDF8", strokeWidth=3)
                .encode(
                    x=alt.X("date_formatted:N", title="Activity Date"),
                    y=alt.Y("pace_seconds:Q", title="Pace (seconds / 100m)", scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip("date_formatted:N", title="Date"),
                        alt.Tooltip("distance_km:Q", title="Distance (km)", format=".2f"),
                        alt.Tooltip("pace_formatted:N", title="Pace (/100m)"),
                        alt.Tooltip("avg_hr:Q", title="Avg HR (bpm)", format=".0f"),
                        alt.Tooltip("training_load:Q", title="Load", format=".0f"),
                    ],
                )
            )
            st.altair_chart(apply_chart_theme(pace_chart, height=300), use_container_width=True)
            st.dataframe(
                df_base[["date_formatted", "distance_km", "pace_formatted", "avg_hr", "training_load"]].rename(
                    columns={"date_formatted": "Date", "distance_km": "Distance (km)", "pace_formatted": "Pace (/100m)", "avg_hr": "Avg HR", "training_load": "Load"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No swims of 1.5 km or longer found to establish endurance baseline.")


# ============================================================
# TAB 6: RUNNING ANALYTICS & SPLITS
# ============================================================

with tab_running:
    st.header("🏃 Running Analytics & Kilometer Splits")
    st.caption("Extracted from your Strava GPS runs, race events & outdoor sessions")

    r_runs = running_analytics.get("runs", [])
    r_tot_runs = running_analytics.get("total_runs", 0)
    r_tot_dist = running_analytics.get("total_distance_km", 0.0)
    r_tot_time = running_analytics.get("total_duration_min", 0.0)
    r_best_pace = running_analytics.get("best_pace_formatted", "—")
    r_longest = running_analytics.get("longest_run_km", 0.0)
    r_peak_hr = running_analytics.get("max_hr")
    r_avg_hr = running_analytics.get("avg_hr")
    r_tot_load = running_analytics.get("total_load", 0.0)
    r_zones = running_analytics.get("pace_zones", [])

    if r_runs:
        # High-Contrast Running KPI Cards
        rc1, rc2, rc3, rc4, rc5 = st.columns(5)

        with rc1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label label-run">🏃 Total Distance</div>
                    <div class="kpi-value">{r_tot_dist:.2f} <span style="font-size: 1.1rem; color: #94A3B8;">km</span></div>
                    <div class="kpi-sub">{r_tot_runs} completed runs</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with rc2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label label-swim">⚡ Best Pace</div>
                    <div class="kpi-value" style="font-size: 1.6rem;">{r_best_pace}</div>
                    <div class="kpi-sub">Fastest average pace</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with rc3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label label-ride">📍 Longest Run</div>
                    <div class="kpi-value">{r_longest:.2f} <span style="font-size: 1.1rem; color: #94A3B8;">km</span></div>
                    <div class="kpi-sub">Max single session</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with rc4:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label label-load">💓 Peak Heart Rate</div>
                    <div class="kpi-value">{f"{r_peak_hr:.0f}" if r_peak_hr else "—"} <span style="font-size: 1.1rem; color: #94A3B8;">bpm</span></div>
                    <div class="kpi-sub">Avg HR: {f"{r_avg_hr:.0f} bpm" if r_avg_hr else "—"}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with rc5:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label label-total">🔥 Total Run Load</div>
                    <div class="kpi-value">{r_tot_load:.0f}</div>
                    <div class="kpi-sub">{r_tot_time / 60:.1f} hours on road</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Row
        r_col1, r_col2 = st.columns(2)

        with r_col1:
            st.subheader("📊 Running Sessions Progression")
            df_r_chart = pd.DataFrame(r_runs)
            df_r_chart["formatted_date"] = df_r_chart["date"].apply(format_date_clean)

            run_bar_chart = (
                alt.Chart(df_r_chart)
                .mark_bar(color="#EC4899", cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                .encode(
                    x=alt.X("formatted_date:N", title="Run Date", sort=None),
                    y=alt.Y("distance_km:Q", title="Distance (km)"),
                    tooltip=[
                        alt.Tooltip("formatted_date:N", title="Date"),
                        alt.Tooltip("name:N", title="Event / Name"),
                        alt.Tooltip("distance_km:Q", title="Distance (km)", format=".2f"),
                        alt.Tooltip("duration_min:Q", title="Duration (min)", format=".1f"),
                        alt.Tooltip("pace_formatted:N", title="Avg Pace"),
                        alt.Tooltip("avg_hr:Q", title="Avg HR (bpm)", format=".0f"),
                        alt.Tooltip("training_load:Q", title="Load", format=".0f"),
                    ],
                )
            )
            st.altair_chart(apply_chart_theme(run_bar_chart, height=290), use_container_width=True)

        with r_col2:
            st.subheader("🔥 Cardiovascular Load & Heart Rate")
            hr_runs = [r for r in r_runs if r.get("avg_hr")]
            if hr_runs:
                df_hr_chart = pd.DataFrame(hr_runs)
                df_hr_chart["formatted_date"] = df_hr_chart["date"].apply(format_date_clean)
                hr_chart = (
                    alt.Chart(df_hr_chart)
                    .mark_bar(color="#F43F5E", cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                    .encode(
                        x=alt.X("formatted_date:N", title="Run Date", sort=None),
                        y=alt.Y("avg_hr:Q", title="Average Heart Rate (bpm)", scale=alt.Scale(domain=[100, 210])),
                        tooltip=[
                            alt.Tooltip("formatted_date:N", title="Date"),
                            alt.Tooltip("name:N", title="Name"),
                            alt.Tooltip("avg_hr:Q", title="Avg HR (bpm)", format=".0f"),
                            alt.Tooltip("max_hr:Q", title="Max HR (bpm)", format=".0f"),
                            alt.Tooltip("training_load:Q", title="Relative Effort", format=".0f"),
                        ],
                    )
                )
                st.altair_chart(apply_chart_theme(hr_chart, height=290), use_container_width=True)
            else:
                st.info("Heart rate data is available on NoiseFit / Strava synced runs.")

        st.markdown("---")

        # Kilometer Splits Explorer
        st.subheader("⏱️ GPS Kilometer Splits Breakdown")
        st.caption("Exact per-kilometer pace breakdown parsed directly from GPX track telemetry")

        run_options = {
            f"{format_date_clean(r.get('date'))} · {r.get('name')} ({r.get('distance_km', 0):.2f} km · Pace: {r.get('pace_formatted')})": r
            for r in r_runs
        }

        selected_run_label = st.selectbox(
            "Select Run Session to Inspect Splits",
            list(run_options.keys()),
            index=0,
            key="running_splits_selector",
        )

        chosen_run = run_options[selected_run_label]
        splits = chosen_run.get("splits", [])

        if splits:
            split_cols = st.columns([3, 2])

            with split_cols[0]:
                st.markdown("##### 🏃 Kilometer Splits Chart")
                df_splits = pd.DataFrame(splits)
                df_splits["pace_sec"] = df_splits["duration_sec"]

                splits_bar = (
                    alt.Chart(df_splits)
                    .mark_bar(color="#38BDF8", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                    .encode(
                        x=alt.X("split:N", title="Kilometer Split", sort=None),
                        y=alt.Y("duration_sec:Q", title="Split Duration (seconds)"),
                        tooltip=[
                            alt.Tooltip("split:N", title="Split"),
                            alt.Tooltip("distance:N", title="Distance"),
                            alt.Tooltip("pace:N", title="Pace"),
                            alt.Tooltip("duration_sec:Q", title="Seconds", format=".1f"),
                        ],
                    )
                )
                st.altair_chart(apply_chart_theme(splits_bar, height=260), use_container_width=True)

            with split_cols[1]:
                st.markdown("##### 📋 Split Telemetry Log")
                st.dataframe(
                    df_splits[["split", "distance", "pace"]].rename(
                        columns={"split": "Split", "distance": "Segment Dist", "pace": "Pace (/km)"}
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("Kilometer splits are generated from GPX track files attached to this run.")

        st.markdown("---")

        # Personalized Running Pace Zones
        st.subheader("🎯 Personalized Running Pace Zones")
        st.caption(f"Calculated from your best 5K race pace ({r_best_pace})")

        if r_zones:
            st.dataframe(pd.DataFrame(r_zones), use_container_width=True, hide_index=True)

        st.markdown("---")

        # Race Photos & Media Gallery
        media_runs = [r for r in r_runs if r.get("media")]
        if media_runs:
            st.subheader("📸 Race & Run Photos Gallery")
            for mr in media_runs:
                st.markdown(f"**{format_date_clean(mr.get('date'))} · {mr.get('name')} ({mr.get('distance_km', 0):.2f} km)**")
                if mr.get("description"):
                    st.caption(f"*{mr.get('description')}*")
                m_list = mr.get("media", [])
                p_cols = st.columns(min(len(m_list), 4) or 1)
                for p_idx, p_rel in enumerate(m_list):
                    img_path = get_strava_media_path(p_rel)
                    if img_path and img_path.exists():
                        with p_cols[p_idx % len(p_cols)]:
                            st.image(str(img_path), caption=f"Photo #{p_idx+1}", width=240)
    else:
        st.info("No running sessions recorded in the selected window. Switch time window to 'All Time' to view all historical runs.")


# ============================================================
# TAB 7: DAILY ACTIVITY DEEP DIVE
# ============================================================

with tab_activities:
    st.header("📋 Daily Activity Deep Dive")

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 2, 2, 3])

    with filter_col1:
        sport_filter = st.selectbox("Filter by Sport", ["All Sports", "Swim", "Ride", "Walk", "Run", "Workout"])

    with filter_col2:
        source_filter_deep = st.selectbox("Filter by Source", ["All Sources", "Garmin / Intervals.icu", "Strava"])

    with filter_col3:
        sort_order = st.selectbox("Sort Order", ["Newest First", "Oldest First", "Highest Load", "Longest Distance"])

    with filter_col4:
        search_query = st.text_input("🔍 Search Activity Name / Date / Notes", "")

    filtered_acts = [
        a for a in activities
        if (sport_filter == "All Sports" or a.get("sport") == sport_filter)
    ]

    if source_filter_deep != "All Sources":
        filtered_acts = [
            a for a in filtered_acts
            if source_filter_deep.lower() in a.get("source", "").lower()
        ]

    if search_query:
        q = search_query.lower()
        filtered_acts = [
            a for a in filtered_acts
            if q in a.get("name", "").lower() or q in a.get("date", "").lower() or q in a.get("description", "").lower()
        ]

    if sort_order == "Newest First":
        filtered_acts = sorted(filtered_acts, key=lambda x: x.get("date", ""), reverse=True)
    elif sort_order == "Oldest First":
        filtered_acts = sorted(filtered_acts, key=lambda x: x.get("date", ""))
    elif sort_order == "Highest Load":
        filtered_acts = sorted(filtered_acts, key=lambda x: x.get("training_load") or 0, reverse=True)
    elif sort_order == "Longest Distance":
        filtered_acts = sorted(filtered_acts, key=lambda x: x.get("distance_km") or 0, reverse=True)

    st.markdown(f"**Showing {len(filtered_acts)} activities**")

    for a_idx, act in enumerate(filtered_acts, start=1):
        sport = act.get("sport", "")
        name = act.get("name", "Activity")
        clean_date = format_date_clean(act.get("date", ""))
        dist = act.get("distance_km") or 0
        dur = act.get("duration_min") or 0
        moving_time = act.get("moving_time_min") or 0
        avg_hr = act.get("avg_hr")
        max_hr = act.get("max_hr")
        load = act.get("training_load") or 0
        calories = act.get("calories")
        source = act.get("source", "")
        desc = act.get("description", "")
        media_list = act.get("media", [])

        icon = get_sport_icon(sport)

        with st.expander(
            f"{icon} {clean_date} · {name} · {dist:.2f} km · {dur:.0f} min · Load {load:.0f} [{source}]",
            expanded=a_idx == 1,
        ):
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Distance", f"{dist:.2f} km")
            c2.metric("Duration", f"{dur:.1f} min")
            c3.metric("Moving Time", f"{moving_time:.1f} min" if moving_time else "—")
            c4.metric("Avg HR", f"{avg_hr:.0f} bpm" if avg_hr else "—")
            c5.metric("Max HR", f"{max_hr:.0f} bpm" if max_hr else "—")
            c6.metric("Training Load", f"{load:.0f}")

            if desc:
                st.markdown(f"📝 **Description / Athlete Notes:** *{desc}*")

            if sport == "Swim":
                st.markdown("##### 🏊 Swimming Breakdown")
                sc1, sc2, sc3, sc4 = st.columns(4)
                pool_l = act.get("pool_length_m")
                pace_raw = act.get("pace")
                laps_ct = act.get("lengths") or act.get("lap_count")

                sc1.metric("Pool Length", f"{pool_l:.0f}m" if pool_l else "25m")
                sc2.metric("Total Laps", laps_ct if laps_ct else "—")

                if pace_raw is not None:
                    p_sec = pace_raw * 100
                    p_min = int(p_sec // 60)
                    p_rem = int(round(p_sec % 60))
                    sc3.metric("Avg Pace", f"{p_min}:{p_rem:02d}/100m")
                else:
                    sc3.metric("Avg Pace", "—")

                sc4.metric("Calories", f"{calories:.0f} kcal" if calories else "—")

                if act.get("interval_summary"):
                    st.caption(f"**Interval Summary:** {act.get('interval_summary')}")

            elif sport == "Ride":
                st.markdown("##### 🚴 Cycling Breakdown")
                rc1, rc2, rc3, rc4 = st.columns(4)
                avg_speed = act.get("avg_speed")
                max_speed = act.get("max_speed")
                elevation = act.get("elevation_m")
                power = act.get("avg_power")

                rc1.metric("Avg Speed", f"{avg_speed * 3.6:.1f} km/h" if avg_speed else "—")
                rc2.metric("Max Speed", f"{max_speed * 3.6:.1f} km/h" if max_speed else "—")
                rc3.metric("Elevation Gain", f"{elevation:.0f}m" if elevation else "—")
                rc4.metric("Avg Power", f"{power:.0f} W" if power else "—")

            elif sport == "Run":
                st.markdown("##### 🏃 Running Breakdown")
                rnc1, rnc2, rnc3, rnc4 = st.columns(4)
                avg_speed = act.get("avg_speed")
                if avg_speed and avg_speed > 0:
                    sec_per_km = 1000.0 / avg_speed
                    run_pace_str = f"{int(sec_per_km // 60)}:{int(sec_per_km % 60):02d} /km"
                else:
                    run_pace_str = "—"

                rnc1.metric("Avg Pace", run_pace_str)
                rnc2.metric("Avg Speed", f"{avg_speed * 3.6:.1f} km/h" if avg_speed else "—")
                rnc3.metric("Elevation Gain", f"{act.get('elevation_m', 0):.0f}m" if act.get('elevation_m') else "—")
                rnc4.metric("Relative Effort", f"{act.get('relative_effort', '—')}")

            # Photos & Media Gallery
            if media_list:
                st.markdown("##### 📸 Attached Photos & Media")
                img_cols = st.columns(min(len(media_list), 4) or 1)
                for m_idx, m_rel in enumerate(media_list):
                    img_p = get_strava_media_path(m_rel)
                    if img_p and img_p.exists():
                        with img_cols[m_idx % len(img_cols)]:
                            st.image(str(img_p), caption=f"Photo #{m_idx+1}", width=220)


# ============================================================
# TAB 7: WELLNESS & RECOVERY
# ============================================================

with tab_wellness:
    st.header("💓 Wellness & Recovery (Intervals.icu)")

    if wellness_records:
        df_well = pd.DataFrame(wellness_records)
        df_well["date"] = df_well["id"]
        df_well["formatted_date"] = df_well["date"].apply(format_date_clean)

        st.caption(f"Loaded **{len(wellness_records)}** daily wellness records")

        w_col1, w_col2 = st.columns(2)

        with w_col1:
            st.subheader("Resting Heart Rate Trend")
            if "restingHR" in df_well.columns and df_well["restingHR"].notnull().any():
                chart_rhr = (
                    alt.Chart(df_well.dropna(subset=["restingHR"]))
                    .mark_line(point=alt.OverlayMarkDef(color="#F43F5E", size=50), color="#FB7185", strokeWidth=2.5)
                    .encode(
                        x=alt.X("formatted_date:N", title="Date"),
                        y=alt.Y("restingHR:Q", title="Resting HR (bpm)", scale=alt.Scale(zero=False)),
                        tooltip=[
                            alt.Tooltip("formatted_date:N", title="Date"),
                            alt.Tooltip("restingHR:Q", title="Resting HR (bpm)"),
                            alt.Tooltip("ctl:Q", title="Fitness (CTL)", format=".1f"),
                            alt.Tooltip("atl:Q", title="Fatigue (ATL)", format=".1f"),
                        ],
                    )
                )
                st.altair_chart(apply_chart_theme(chart_rhr, height=300), use_container_width=True)
            else:
                st.info("No resting heart rate data available.")

        with w_col2:
            st.subheader("Daily Step Count")
            if "steps" in df_well.columns and df_well["steps"].notnull().any():
                chart_steps = (
                    alt.Chart(df_well.dropna(subset=["steps"]))
                    .mark_bar(color="#FBBF24", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                    .encode(
                        x=alt.X("formatted_date:N", title="Date"),
                        y=alt.Y("steps:Q", title="Daily Steps"),
                        tooltip=[
                            alt.Tooltip("formatted_date:N", title="Date"),
                            alt.Tooltip("steps:Q", title="Steps", format=","),
                        ],
                    )
                )
                st.altair_chart(apply_chart_theme(chart_steps, height=300), use_container_width=True)
            else:
                st.info("No step data available.")

        st.markdown("---")
        st.subheader("Daily Wellness Records Log")
        display_cols = [c for c in ["date", "restingHR", "steps", "ctl", "atl", "rampRate", "readiness", "sleepSecs"] if c in df_well.columns]
        
        rename_map = {
            "date": "Date",
            "restingHR": "Resting HR (bpm)",
            "steps": "Steps",
            "ctl": "Fitness (CTL)",
            "atl": "Fatigue (ATL)",
            "rampRate": "Ramp Rate",
            "readiness": "Readiness",
            "sleepSecs": "Sleep (Sec)",
        }
        st.dataframe(
            df_well[display_cols].rename(columns=rename_map).sort_values("Date", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No wellness records found in the selected date range.")


# ============================================================
# TAB 8: SAVED PLANS LIBRARY
# ============================================================

with tab_history:
    st.header("🗄️ Saved Training Plans Library")
    st.caption("Workout plans stored in `training_plans.json`")

    plans = get_plans()

    if plans:
        top_c1, top_c2 = st.columns([4, 2])
        with top_c1:
            st.markdown(f"**Total Plans Saved:** `{len(plans)} workouts`")
        with top_c2:
            if st.button("🧹 Clear All Saved Plans", type="secondary", use_container_width=True):
                clear_plans()
                st.success("Cleared all saved plans!")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        for p_idx, saved_p in enumerate(reversed(plans), start=1):
            p_type = saved_p.get("type", "Workout")
            p_dist = saved_p.get("target_distance", 0)
            p_date = format_date_clean(saved_p.get("planned_date", ""))
            p_id = saved_p.get("plan_id", "")
            p_id_short = p_id[:8] if p_id else f"{p_idx}"

            chip_color = (
                "chip-swim" if p_type == "Endurance"
                else "chip-ride" if p_type == "Tempo"
                else "chip-run" if p_type == "Intervals"
                else "chip-rest"
            )

            with st.expander(f"🏊 Workout Plan #{p_idx}: {p_type} · {p_dist}m · Planned: {p_date} (ID: {p_id_short})", expanded=(p_idx == 1)):
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.markdown(f"**Type:** <span class='sport-chip {chip_color}'>{p_type}</span> · **Scheduled Date:** `{p_date}` · **Total Distance:** `{p_dist}m`", unsafe_allow_html=True)
                    st.markdown(f"**Goal:** {saved_p.get('goal', '—')}")
                    st.markdown(f"**Duration:** {saved_p.get('duration', '—')}")
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_plan_{p_id}_{p_idx}", use_container_width=True):
                        delete_plan(p_id)
                        st.success(f"Deleted plan #{p_idx}")
                        st.rerun()

                p_sets = saved_p.get("sets", [])
                st.markdown("##### Sets Breakdown:")
                for s_i, s_item in enumerate(p_sets, start=1):
                    if isinstance(s_item, dict):
                        st.markdown(f"- **Set {s_i}:** {s_item.get('reps', 1)} × {s_item.get('distance', 0)}m ({s_item.get('stroke', 'Freestyle')}) · Pace: `{s_item.get('pace', '—')}` · Rest: `{s_item.get('rest', 'None')}` · Purpose: *{s_item.get('purpose', '')}*")
                    else:
                        st.markdown(f"- **Set {s_i}:** {s_item}")
    else:
        st.info(f"No saved plans yet. Generate and customize a workout in the '{plan_timing_label} Swim Plan' tab and click 'Save Plan to Library'.")
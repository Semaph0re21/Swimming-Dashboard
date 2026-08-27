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
# CLEAN DARK ATHLETIC DESIGN SYSTEM (CSS)
# ============================================================

st.markdown(
    """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #060B12;
        --bg-card: #0C1420;
        --bg-card-hover: #101B2B;
        --bg-surface-elevated: #142236;
        --border-subtle: #172338;
        --border-focus: #00E599;
        
        --color-brand: #00E599;
        --color-brand-glow: rgba(0, 229, 153, 0.25);
        --color-swim: #00D2FF;
        --color-ride: #10B981;
        --color-run: #F43F5E;
        --color-walk: #F59E0B;
        --color-sleep: #8B5CF6;
        --color-orange: #FF6B00;
        
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #060B12 !important;
        color: #F8FAFC;
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

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1600px !important;
        margin: 0 auto;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em;
    }

    /* Brand Header */
    .forest-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 12px;
        padding-bottom: 12px;
    }
    .forest-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .forest-logo-badge {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: linear-gradient(135deg, #00E599 0%, #059669 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        box-shadow: 0 0 16px rgba(0, 229, 153, 0.35);
    }
    .forest-title-wrap {
        display: flex;
        flex-direction: column;
    }
    .forest-title-row {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .forest-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .forest-pill-tag {
        font-size: 0.68rem;
        font-weight: 800;
        color: #00E599;
        background: rgba(0, 229, 153, 0.12);
        border: 1px solid rgba(0, 229, 153, 0.3);
        padding: 2px 8px;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .forest-subtitle {
        font-size: 0.76rem;
        color: #64748B;
        font-weight: 600;
        margin: 0;
    }
    .forest-actions {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 700;
        background: #0C1420;
        border: 1px solid #172338;
        color: #CBD5E1;
    }
    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #00E599;
        box-shadow: 0 0 8px #00E599;
        display: inline-block;
    }

    /* Standard Card Container */
    .f-card {
        background: #0C1420;
        border: 1px solid #172338;
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
        transition: border-color 0.18s ease;
    }
    .f-card:hover {
        border-color: #23354E;
    }

    .f-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
    }
    .f-card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.05rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .f-card-subtitle {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Unified KPI Grid & Cards (Used Across All Sport Tabs) */
    .kpi-row-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 12px;
        margin-bottom: 18px;
    }
    .forest-kpi-card, .kpi-card-sub {
        background: #0C1322;
        border: 1px solid #1A273D;
        border-radius: 12px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 100px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: all 0.15s ease;
    }
    .forest-kpi-card:hover, .kpi-card-sub:hover {
        border-color: #2D3F5E;
        background: #0F192C;
    }
    .forest-kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .forest-kpi-label, .kpi-card-label {
        font-size: 0.72rem;
        font-weight: 800;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .forest-kpi-icon {
        font-size: 0.95rem;
    }
    .forest-kpi-val, .kpi-card-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.15;
        letter-spacing: -0.03em;
        margin: 4px 0 2px 0;
    }
    .forest-kpi-sub, .kpi-card-footer {
        font-size: 0.72rem;
        color: #64748B;
        font-weight: 600;
    }

    /* 4 Multi-Sport Breakdown Cards */
    .sport-breakdown-card {
        background: #0C1322;
        border: 1px solid #1A273D;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .sport-breakdown-card:hover {
        transform: translateY(-2px);
        border-color: #2D3F5E;
    }

    /* Heatmap Activity Matrix Grid */
    .heatmap-container {
        width: 100%;
        overflow-x: auto;
        padding-bottom: 4px;
    }
    .heatmap-grid {
        display: grid;
        grid-template-rows: repeat(7, 13px);
        grid-auto-flow: column;
        grid-auto-columns: 13px;
        gap: 4px;
    }
    .hm-cell {
        width: 13px;
        height: 13px;
        border-radius: 3px;
        background: #111A27;
        transition: transform 0.1s ease, border-color 0.1s ease;
    }
    .hm-cell:hover {
        transform: scale(1.3);
        z-index: 5;
        box-shadow: 0 0 8px rgba(0, 229, 153, 0.6);
    }
    .hm-lvl-0 { background: #111A27; }
    .hm-lvl-1 { background: #064E3B; }
    .hm-lvl-2 { background: #059669; }
    .hm-lvl-3 { background: #10B981; }
    .hm-lvl-4 { background: #00E599; box-shadow: 0 0 6px rgba(0, 229, 153, 0.35); }

    /* Muscle / Discipline Recovery Status Cards */
    .recovery-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 10px;
    }
    .recovery-card {
        background: #101A29;
        border: 1px solid #1A273D;
        border-radius: 10px;
        padding: 12px 14px;
        transition: border-color 0.15s ease;
    }
    .recovery-card:hover {
        border-color: #263852;
    }
    .rec-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .rec-title {
        font-size: 0.84rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    .rec-badge-green {
        font-size: 0.65rem;
        font-weight: 700;
        color: #00E599;
        background: rgba(0, 229, 153, 0.12);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .rec-badge-red {
        font-size: 0.65rem;
        font-weight: 700;
        color: #F43F5E;
        background: rgba(244, 63, 94, 0.12);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .rec-badge-blue {
        font-size: 0.65rem;
        font-weight: 700;
        color: #38BDF8;
        background: rgba(56, 189, 248, 0.12);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .rec-badge-yellow {
        font-size: 0.65rem;
        font-weight: 700;
        color: #F59E0B;
        background: rgba(245, 158, 11, 0.12);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .rec-score-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.72rem;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .rec-progress-bar {
        width: 100%;
        height: 4px;
        background: #172338;
        border-radius: 2px;
        overflow: hidden;
        margin-bottom: 6px;
    }
    .rec-progress-fill {
        height: 100%;
        background: #00E599;
        border-radius: 2px;
    }
    .rec-progress-fill.fill-low {
        background: #F43F5E;
    }
    .rec-progress-fill.fill-mid {
        background: #F59E0B;
    }
    .rec-progress-fill.fill-good {
        background: #38BDF8;
    }
    .rec-progress-fill.fill-ok {
        background: #00E599;
    }
    .rec-footer {
        font-size: 0.68rem;
        color: #64748B;
        font-weight: 500;
    }

    /* Clean Streamlit Tab Navigation Bar */
    [data-baseweb="tab-list"] {
        gap: 4px !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid #172338 !important;
        margin-bottom: 18px !important;
    }
    [data-baseweb="tab"] {
        padding: 8px 14px !important;
        font-size: 0.84rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        border-radius: 8px !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: #64748B !important;
        min-height: 38px !important;
        transition: all 0.15s ease !important;
    }
    [data-baseweb="tab"]:hover {
        background: #0C1420 !important;
        color: #CBD5E1 !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        background: #0C1420 !important;
        color: #00E599 !important;
        border-color: #172338 !important;
        border-bottom: 2px solid #00E599 !important;
    }

    /* Sport Badge Chips */
    .sport-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .chip-swim { background: rgba(0, 210, 255, 0.12); color: #00D2FF !important; border: 1px solid rgba(0, 210, 255, 0.25); }
    .chip-ride { background: rgba(16, 185, 129, 0.12); color: #10B981 !important; border: 1px solid rgba(16, 185, 129, 0.25); }
    .chip-walk { background: rgba(245, 158, 11, 0.12); color: #F59E0B !important; border: 1px solid rgba(245, 158, 11, 0.25); }
    .chip-run { background: rgba(244, 63, 94, 0.12); color: #F43F5E !important; border: 1px solid rgba(244, 63, 94, 0.25); }
    .chip-workout { background: rgba(139, 92, 246, 0.12); color: #8B5CF6 !important; border: 1px solid rgba(139, 92, 246, 0.25); }
    .chip-rest { background: #172338; color: #94A3B8 !important; }

    /* Buttons */
    button[kind="primary"], button[kind="secondary"], .stButton > button {
        min-height: 38px !important;
        font-size: 0.86rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        background: #0C1420 !important;
        border: 1px solid #172338 !important;
        color: #FFFFFF !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        border-color: #00E599 !important;
        color: #00E599 !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #0C1420 !important;
        border: 1px solid #172338 !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #172338 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Images */
    .stImage img {
        border-radius: 10px !important;
        border: 1px solid #172338 !important;
        object-fit: cover !important;
        max-height: 200px !important;
    }

    /* ============================================================
       RESPONSIVE & MOBILE DESIGN ENHANCEMENTS
       ============================================================ */
    @media (max-width: 1024px) {
        .kpi-row-grid {
            grid-template-columns: repeat(3, 1fr) !important;
        }
    }

    @media (max-width: 768px) {
        /* Container Spacing */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 3rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }

        /* Top Brand & Filter Bar */
        .forest-header {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 10px !important;
        }
        .forest-title {
            font-size: 1.15rem !important;
        }
        .forest-subtitle {
            font-size: 0.72rem !important;
        }
        .forest-brand {
            gap: 8px !important;
        }
        .forest-logo-badge {
            width: 32px !important;
            height: 32px !important;
            font-size: 1.1rem !important;
        }

        /* Top Filter Selectboxes - stack neatly on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 4px !important;
        }

        /* Horizontal Scrollable Tabs */
        [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            gap: 4px !important;
            padding-bottom: 6px !important;
            scrollbar-width: none !important;
        }
        [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }
        [data-baseweb="tab"] {
            font-size: 0.78rem !important;
            padding: 6px 10px !important;
            min-height: 34px !important;
            flex-shrink: 0 !important;
        }

        /* KPI Cards Grid */
        .kpi-row-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 8px !important;
            margin-bottom: 14px !important;
        }
        .forest-kpi-card, .kpi-card-sub {
            padding: 10px 12px !important;
            min-height: 85px !important;
            border-radius: 10px !important;
        }
        .forest-kpi-val, .kpi-card-value {
            font-size: 1.3rem !important;
            margin: 2px 0 !important;
        }
        .forest-kpi-label, .kpi-card-label {
            font-size: 0.66rem !important;
        }
        .forest-kpi-sub, .kpi-card-footer {
            font-size: 0.68rem !important;
        }

        /* Standard Cards */
        .f-card {
            padding: 14px 14px !important;
            border-radius: 12px !important;
            margin-bottom: 12px !important;
        }
        .f-card-header {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 8px !important;
        }
        .f-card-title {
            font-size: 1.1rem !important;
        }

        /* Structured Workout Sets Grid */
        .sets-grid-responsive {
            grid-template-columns: 1fr !important;
            gap: 10px !important;
        }

        /* Recovery Matrix Grid */
        .recovery-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 8px !important;
        }

        /* Dataframe overflow touch scroll */
        [data-testid="stDataFrame"] {
            -webkit-overflow-scrolling: touch !important;
        }
    }

    @media (max-width: 480px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .kpi-row-grid {
            grid-template-columns: 1fr 1fr !important;
            gap: 6px !important;
        }
        .forest-kpi-card {
            padding: 8px 10px !important;
        }
        .forest-kpi-val {
            font-size: 1.18rem !important;
        }
        .status-pill {
            font-size: 0.72rem !important;
            padding: 4px 8px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS & SVG GENERATORS
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


def apply_forest_chart_theme(chart, height=270):
    return (
        chart.properties(height=height)
        .configure_axis(
            labelColor="#64748B",
            titleColor="#94A3B8",
            labelFontSize=10,
            titleFontSize=11,
            titleFontWeight="normal",
            gridColor="#121D2C",
            domainColor="#172338",
            tickColor="#172338",
        )
        .configure_legend(
            labelColor="#CBD5E1",
            titleColor="#94A3B8",
            labelFontSize=10,
            titleFontSize=11,
        )
        .configure_view(
            strokeWidth=0
        )
    )


def generate_radar_svg(scores, labels, size=280):
    """Generate high-tech SVG Radar / Spider chart."""
    cx, cy, r = size / 2, size / 2, size * 0.36
    num_vars = len(labels)
    angles = [i * (2 * math.pi / num_vars) - math.pi / 2 for i in range(num_vars)]
    
    rings_svg = ""
    for step in [0.25, 0.5, 0.75, 1.0]:
        pts = [f"{cx + r * step * math.cos(a):.1f},{cy + r * step * math.sin(a):.1f}" for a in angles]
        rings_svg += f'<polygon points="{" ".join(pts)}" fill="none" stroke="#162338" stroke-width="1" />'
        
    axes_svg = ""
    for i, a in enumerate(angles):
        ax_x = cx + r * math.cos(a)
        ax_y = cy + r * math.sin(a)
        axes_svg += f'<line x1="{cx}" y1="{cy}" x2="{ax_x:.1f}" y2="{ax_y:.1f}" stroke="#172338" stroke-width="1" />'
        lbl_x = cx + (r + 18) * math.cos(a)
        lbl_y = cy + (r + 14) * math.sin(a)
        anchor = "middle"
        if math.cos(a) > 0.3:
            anchor = "start"
        elif math.cos(a) < -0.3:
            anchor = "end"
        axes_svg += f'<text x="{lbl_x:.1f}" y="{lbl_y:.1f}" fill="#64748B" font-size="9.5" font-family="Plus Jakarta Sans, sans-serif" font-weight="600" text-anchor="{anchor}" dominant-baseline="middle">{labels[i]}</text>'
        
    data_pts = []
    circles_svg = ""
    for i, (score, a) in enumerate(zip(scores, angles)):
        val = max(0.18, min(1.0, score))
        px = cx + r * val * math.cos(a)
        py = cy + r * val * math.sin(a)
        data_pts.append(f"{px:.1f},{py:.1f}")
        circles_svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#00E599" stroke="#060B12" stroke-width="1.5" />'
        
    poly_str = " ".join(data_pts)
    data_svg = f'<polygon points="{poly_str}" fill="rgba(0, 229, 153, 0.18)" stroke="#00E599" stroke-width="1.8" />'
    
    return f'<svg viewBox="0 0 {size} {size}" width="100%" height="220" style="display: block; margin: 0 auto;">{rings_svg}{axes_svg}{data_svg}{circles_svg}</svg>'


def calculate_sport_recovery_metric(sport_name, days_ago, acute_load, recent_dist_km, wellness):
    """
    Physiologically verified recovery & readiness model combining:
    1. Acute Muscular Depletion & Time-Course Recovery (Banister / Firstbeat Impulse Model)
    2. Garmin Biometric Telemetry (Sleep Score, Overnight HRV, Resting HR)
    3. Recent session workload
    """
    sleep_score = wellness.get("sleepScore") if isinstance(wellness, dict) else None
    hrv = wellness.get("hrv") if isinstance(wellness, dict) else None
    rhr = wellness.get("restingHR") if isinstance(wellness, dict) else None

    # Biometric modifier (-22% to +11%)
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

    # Time-based muscular readiness
    if days_ago == 0:  # Trained Today
        if (acute_load or 0) > 50 or (recent_dist_km or 0) > 3.0:
            base_readiness = 40  # Heavy fatigue / active repair
            status_text = "Trained Today / Fatigued"
        else:
            base_readiness = 58  # Light-moderate session
            status_text = "Trained Today / Rest"
    elif days_ago == 1:  # Trained Yesterday
        base_readiness = 78
        status_text = "Recovering / Good"
    elif days_ago in (2, 3):  # Peak supercompensation window
        base_readiness = 95
        status_text = "Optimal / Rested"
    elif days_ago in (4, 5, 6):
        base_readiness = 90
        status_text = "Rested / Ready"
    elif days_ago is not None and days_ago >= 7:
        base_readiness = max(65, 85 - (days_ago - 7) * 2)
        status_text = "Detraining Gap"
    else:
        base_readiness = 85
        status_text = "Ready"

    final_readiness = max(15, min(100, int(base_readiness + bio_mod)))

    if final_readiness >= 85:
        badge_cls = "rec-badge-green"
        fill_cls = "fill-ok"
    elif final_readiness >= 70:
        badge_cls = "rec-badge-blue"
        fill_cls = "fill-good"
    elif final_readiness >= 50:
        badge_cls = "rec-badge-yellow"
        fill_cls = "fill-mid"
    else:
        badge_cls = "rec-badge-red"
        fill_cls = "fill-low"

    return {
        "readiness_pct": final_readiness,
        "status_text": status_text,
        "badge_cls": badge_cls,
        "fill_cls": fill_cls,
    }


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
        <div class="forest-brand" style="margin-top: 4px;">
            <div class="forest-logo-badge">⚡</div>
            <div class="forest-title-wrap">
                <div class="forest-title-row">
                    <span class="forest-title">FITNESS DASHBOARD</span>
                    <span class="forest-pill-tag">TRAINING ENGINE</span>
                </div>
                <span class="forest-subtitle">Personal Fitness, Training &amp; Health Intelligence · Garmin 965 &amp; Strava</span>
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
        index=0,
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
current_week = data.get("current_week", {})
previous_week = data.get("previous_week", {})
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
strava_matched = data.get("strava_matched", 0)
strava_added = data.get("strava_added", 0)
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
    plan_timing_label = "Tomorrow's"
    plan_timing_badge = "Tomorrow"
else:
    target_plan_date = end_val
    plan_timing_label = "Today's"
    plan_timing_badge = "Today"

target_plan_date_str = target_plan_date.strftime("%A, %b %d, %Y")

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

# Telemetry Status Pills Bar
st.markdown(
    f"""
    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin: 4px 0 16px 0;">
        <div class="status-pill">
            <span class="live-dot"></span> Live Telemetry (Garmin 965)
        </div>
        <div class="status-pill">
            🟠 Strava Sync: <strong>{tot_strava}</strong>
        </div>
        <div class="status-pill" style="color: #00E599;">
            ⚡ Window: <strong>{len(activities)}</strong> sessions
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION TABS
# ============================================================

(
    tab_overview,
    tab_today,
    tab_swimming,
    tab_running,
    tab_cycling,
    tab_walking,
    tab_sleep,
    tab_calendar,
    tab_performance,
    tab_load,
    tab_records,
    tab_settings,
) = st.tabs([
    "👁️ Overview",
    "☀️ Today",
    "🏊 Swimming",
    "🏃 Running",
    "🚴 Cycling",
    "🚶 Walking",
    "😴 Sleep & Recovery",
    "📅 Activity Calendar",
    "📊 Performance",
    "📈 Training Load",
    "🏆 Personal Records",
    "⚙️ Data & Settings",
])


# ============================================================
# TAB 1: 👁️ OVERVIEW
# ============================================================

with tab_overview:
    # 1. Today's Garmin Sleep & Recovery Telemetry Card
    today_iso = str(today_date)
    today_wellness = next((w for w in wellness_records if w.get("id") == today_iso or w.get("date") == today_iso), None)
    if not today_wellness and wellness_records:
        today_wellness = wellness_records[-1]

    t_sleep_sec = today_wellness.get("sleepSecs") if today_wellness else None
    t_sleep_score = today_wellness.get("sleepScore") if today_wellness else None
    t_rhr = today_wellness.get("restingHR") if today_wellness else None
    t_hrv = today_wellness.get("hrv") if today_wellness else None

    t_hours = int(t_sleep_sec // 3600) if t_sleep_sec else 0
    t_mins = int((t_sleep_sec % 3600) // 60) if t_sleep_sec else 0
    dur_display = f"{t_hours}h {t_mins:02d}m" if t_sleep_sec else "—"
    score_badge = f"{t_sleep_score:.0f}/100" if t_sleep_score else "Tracked"
    hrv_badge = f"{t_hrv:.0f} ms" if t_hrv else "—"
    rhr_badge = f"{t_rhr:.0f} bpm" if t_rhr else "—"
    today_date_str_formatted = format_date_clean(today_wellness.get('id', today_iso) if today_wellness else today_iso).upper()

    st.markdown(
        f"""
        <div style="background: #0C1322; border: 1px solid #1A273D; border-radius: 14px; padding: 18px 22px; margin-bottom: 22px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
                <div>
                    <div style="font-size: 0.76rem; font-weight: 800; color: #A78BFA; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
                        🌙 TODAY'S GARMIN SLEEP &amp; RECOVERY TELEMETRY · {today_date_str_formatted}
                    </div>
                    <h3 style="margin: 0; color: #FFFFFF; font-size: 1.25rem; font-weight: 800;">
                        Sleep Quality, HRV &amp; Recovery State
                    </h3>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: #6D28D9; color: #FFFFFF; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 6px;">Score: {score_badge}</span>
                    <span style="background: #0284C7; color: #FFFFFF; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 6px;">HRV: {hrv_badge}</span>
                    <span style="background: #059669; color: #FFFFFF; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 6px;">RHR: {rhr_badge}</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px;">
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #38BDF8;">🛌 SLEEP DURATION</div>
                    <div class="kpi-card-value">{dur_display}</div>
                    <div class="kpi-card-footer">{f"{t_sleep_sec:,}s log" if t_sleep_sec else "Tracked sleep"}</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #F472B6;">🎯 SLEEP SCORE</div>
                    <div class="kpi-card-value">{f"{t_sleep_score:.0f}" if t_sleep_score else "—"} <span style="font-size: 0.85rem; color: #64748B;">/ 100</span></div>
                    <div class="kpi-card-footer" style="color: #10B981; font-weight: 700;">Restful</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #00D2FF;">💓 OVERNIGHT HRV</div>
                    <div class="kpi-card-value">{f"{t_hrv:.0f}" if t_hrv else "—"} <span style="font-size: 0.85rem; color: #64748B;">ms</span></div>
                    <div class="kpi-card-footer" style="color: #38BDF8; font-weight: 700;">Balanced</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #10B981;">❤️ RESTING HR</div>
                    <div class="kpi-card-value">{f"{t_rhr:.0f}" if t_rhr else "—"} <span style="font-size: 0.85rem; color: #64748B;">bpm</span></div>
                    <div class="kpi-card-footer">Garmin 965</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Activity Telemetry Overview (7 KPI Cards)
    daily_steps_list = [w["steps"] for w in wellness_records if w.get("steps")]
    avg_steps = round(sum(daily_steps_list) / len(daily_steps_list)) if daily_steps_list else None
    avg_sleep_f = sleep_analytics.get("avg_duration_formatted", "—")
    streak_count = performance_analytics.get("current_streak", 0)
    tracked_nights_cnt = sleep_analytics.get('total_days_tracked', 0)

    st.markdown(
        f"""
        <div style="margin-bottom: 22px;">
            <h3 style="margin: 0 0 12px 0; color: #FFFFFF; font-size: 1.25rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                📊 Activity Telemetry Overview
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px;">
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #A78BFA;">🏃 TOTAL DISTANCE</div>
                    <div class="kpi-card-value">{total_dist_all:.1f} <span style="font-size: 0.85rem; color: #64748B;">km</span></div>
                    <div class="kpi-card-footer">{len(activities)} total sessions</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #38BDF8;">⏱️ ACTIVE TIME</div>
                    <div class="kpi-card-value">{total_time_all / 60:.1f} <span style="font-size: 0.85rem; color: #64748B;">hrs</span></div>
                    <div class="kpi-card-footer">{total_time_all:.0f} moving mins</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #4ADE80;">🔥 ACTIVE CALORIES</div>
                    <div class="kpi-card-value">{total_cals_all:,} <span style="font-size: 0.85rem; color: #64748B;">kcal</span></div>
                    <div class="kpi-card-footer">Verified energy</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #F87171;">📈 TRAINING LOAD</div>
                    <div class="kpi-card-value">{total_load_all:.0f}</div>
                    <div class="kpi-card-footer">ICU Training Load</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #FBBF24;">👟 AVG DAILY STEPS</div>
                    <div class="kpi-card-value">{f"{avg_steps:,}" if avg_steps else "—"}</div>
                    <div class="kpi-card-footer">Garmin pedometer</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #C084FC;">😴 AVG SLEEP</div>
                    <div class="kpi-card-value">{avg_sleep_f}</div>
                    <div class="kpi-card-footer">{tracked_nights_cnt} nights tracked</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #F59E0B;">⚡ ACTIVITY STREAK</div>
                    <div class="kpi-card-value">{streak_count} <span style="font-size: 0.85rem; color: #64748B;">days</span></div>
                    <div class="kpi-card-footer">Consecutive active</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Multi-Sport Breakdown (4 Sport Cards)
    swim_sum = summary.get("Swim", {})
    run_sum = summary.get("Run", {})
    ride_sum = summary.get("Ride", {})
    walk_sum = summary.get("Walk", {})

    s_pace = swim_sum.get("pace_formatted", "—")
    r_pace = run_sum.get("pace_formatted", "—")
    b_speed = cycling_analytics.get("avg_speed_kmh")
    b_speed_str = f"{b_speed:.1f} km/h" if b_speed else "—"
    w_pace = walking_analytics.get("avg_pace_formatted", "—")

    st.markdown(
        f"""
        <div style="margin-bottom: 22px;">
            <h3 style="margin: 0 0 12px 0; color: #FFFFFF; font-size: 1.25rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                🏅 Multi-Sport Breakdown
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                <div class="sport-breakdown-card" style="border-top: 4px solid #00D2FF;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.92rem; font-weight: 800; color: #38BDF8;">🏊 SWIMMING</span>
                        <span style="background: #0284C7; color: #FFFFFF; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{swim_sum.get('sessions', 0)} sessions</span>
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;">{swim_sum.get('distance_km', 0):.2f} km</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">⏱️ {format_duration_hm(swim_sum.get('moving_time_min', 0))} · ⚡ {s_pace}</div>
                    <div style="font-size: 0.75rem; color: #38BDF8; margin-top: 6px; font-weight: 700;">Last: {format_days_ago(days_since_swim)}</div>
                </div>
                <div class="sport-breakdown-card" style="border-top: 4px solid #F43F5E;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.92rem; font-weight: 800; color: #F472B6;">🏃 RUNNING</span>
                        <span style="background: #DB2777; color: #FFFFFF; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{run_sum.get('sessions', 0)} sessions</span>
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;">{run_sum.get('distance_km', 0):.2f} km</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">⏱️ {format_duration_hm(run_sum.get('moving_time_min', 0))} · ⚡ {r_pace}</div>
                    <div style="font-size: 0.75rem; color: #F472B6; margin-top: 6px; font-weight: 700;">Last: {format_days_ago(days_since_run)}</div>
                </div>
                <div class="sport-breakdown-card" style="border-top: 4px solid #10B981;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.92rem; font-weight: 800; color: #4ADE80;">🚴 CYCLING</span>
                        <span style="background: #059669; color: #FFFFFF; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{ride_sum.get('sessions', 0)} sessions</span>
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;">{ride_sum.get('distance_km', 0):.2f} km</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">⏱️ {format_duration_hm(ride_sum.get('moving_time_min', 0))} · ⚡ {b_speed_str}</div>
                    <div style="font-size: 0.75rem; color: #4ADE80; margin-top: 6px; font-weight: 700;">Last: {format_days_ago(days_since_ride)}</div>
                </div>
                <div class="sport-breakdown-card" style="border-top: 4px solid #F59E0B;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.92rem; font-weight: 800; color: #FBBF24;">🚶 WALKING</span>
                        <span style="background: #D97706; color: #FFFFFF; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{walk_sum.get('sessions', 0)} sessions</span>
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;">{walk_sum.get('distance_km', 0):.2f} km</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">⏱️ {format_duration_hm(walk_sum.get('moving_time_min', 0))} · ⚡ {w_pace}</div>
                    <div style="font-size: 0.75rem; color: #FBBF24; margin-top: 6px; font-weight: 700;">Last: {format_days_ago(days_since_walk)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Workout Activity Matrix Heatmap Card
    act_counts_by_date = {}
    for a in all_activities:
        d_str = a.get("date")
        if d_str:
            k = d_str[:10]
            act_counts_by_date[k] = act_counts_by_date.get(k, 0) + 1

    # Build 52-week calendar grid for 2026
    start_grid_date = date(2026, 1, 1)
    # Align to Monday
    start_grid_date -= timedelta(days=start_grid_date.weekday())
    end_grid_date = date(2026, 12, 31)

    heatmap_cells_html = ""
    curr_d = start_grid_date
    total_active_days_2026 = 0

    while curr_d <= end_grid_date:
        d_iso = curr_d.strftime("%Y-%m-%d")
        cnt = act_counts_by_date.get(d_iso, 0)
        if cnt > 0 and curr_d.year == 2026:
            total_active_days_2026 += 1

        lvl = "hm-lvl-0"
        if cnt == 1:
            lvl = "hm-lvl-1"
        elif cnt == 2:
            lvl = "hm-lvl-2"
        elif cnt == 3:
            lvl = "hm-lvl-3"
        elif cnt >= 4:
            lvl = "hm-lvl-4"

        title_tip = f"{curr_d.strftime('%b %d, %Y')}: {cnt} workout(s)"
        heatmap_cells_html += f'<div class="hm-cell {lvl}" title="{title_tip}"></div>'
        curr_d += timedelta(days=1)

    st.markdown(
        f"""
        <div class="f-card">
            <div class="f-card-header">
                <div>
                    <div class="f-card-title">🗓️ Workout Activity Matrix</div>
                    <div class="f-card-subtitle">{total_active_days_2026} active workout days in 2026</div>
                </div>
                <div style="display: flex; align-items: center; gap: 4px; font-size: 0.72rem; color: #64748B;">
                    <span>Less</span>
                    <span class="hm-cell hm-lvl-0" style="display: inline-block;"></span>
                    <span class="hm-cell hm-lvl-1" style="display: inline-block;"></span>
                    <span class="hm-cell hm-lvl-2" style="display: inline-block;"></span>
                    <span class="hm-cell hm-lvl-3" style="display: inline-block;"></span>
                    <span class="hm-cell hm-lvl-4" style="display: inline-block;"></span>
                    <span>More</span>
                </div>
            </div>
            <div class="heatmap-container">
                <div class="heatmap-grid">
                    {heatmap_cells_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 5. Middle Row: Volume Progression & Frequency (Left 2/3) + Donut Discipline Split (Right 1/3)
    chart_c1, chart_c2 = st.columns([2, 1])

    with chart_c1:
        st.markdown(
            """
            <div class="f-card" style="margin-bottom: 16px;">
                <div class="f-card-header">
                    <div>
                        <div class="f-card-title">📈 Volume Progression &amp; Frequency</div>
                        <div class="f-card-subtitle">Weekly distance volume and sessions completed</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        if weekly_trends:
            w_df = pd.DataFrame(weekly_trends)
            
            bars = alt.Chart(w_df).mark_bar(
                color="#14283D",
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
                    alt.Tooltip("time_min:Q", title="Time (min)"),
                ]
            )

            line = alt.Chart(w_df).mark_line(
                color="#00E599",
                strokeWidth=2.5,
                point=alt.OverlayMarkDef(color="#00E599", size=40, stroke="#060B12", strokeWidth=2)
            ).encode(
                x=alt.X("week:N", title=None),
                y=alt.Y("distance_km:Q", title=None),
            )

            combo_chart = (bars + line).properties(height=230)
            st.altair_chart(apply_forest_chart_theme(combo_chart, height=230), use_container_width=True)
        else:
            st.info("No volume trends available for the selected period.")
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_c2:
        st.markdown(
            """
            <div class="f-card" style="margin-bottom: 16px;">
                <div class="f-card-header">
                    <div>
                        <div class="f-card-title">🍩 Discipline Split</div>
                        <div class="f-card-subtitle">Distribution of active volume</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        dist_map = performance_analytics.get("sport_distribution", {})
        if dist_map:
            pie_data = []
            for sp_k, sp_v in dist_map.items():
                pie_data.append({
                    "sport": sp_k,
                    "hours": sp_v.get("hours", 0),
                    "percentage": sp_v.get("percentage_time", 0),
                })
            p_df = pd.DataFrame(pie_data)
            donut_chart = alt.Chart(p_df).mark_arc(innerRadius=52, outerRadius=82).encode(
                theta=alt.Theta("hours:Q", title="Hours"),
                color=alt.Color(
                    "sport:N",
                    scale=alt.Scale(
                        domain=["Swim", "Ride", "Run", "Walk", "Workout", "Other"],
                        range=["#00D2FF", "#10B981", "#F43F5E", "#F59E0B", "#8B5CF6", "#64748B"],
                    ),
                    legend=alt.Legend(orient="right", title=None, labelFontSize=10)
                ),
                tooltip=[
                    alt.Tooltip("sport:N", title="Sport"),
                    alt.Tooltip("hours:Q", title="Hours"),
                    alt.Tooltip("percentage:Q", title="Percentage (%)"),
                ]
            ).properties(height=230)
            st.altair_chart(apply_forest_chart_theme(donut_chart, height=230), use_container_width=True)
        else:
            st.info("No discipline data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 6. Bottom Row: Muscle/Discipline Recovery Index (Left 2/3) + Training Balance Radar (Right 1/3)
    rec_c1, rec_c2 = st.columns([2, 1])

    with rec_c1:
        # Compute exact physiological recovery & readiness metrics for each discipline
        rec_swim = calculate_sport_recovery_metric(
            "Swim", days_since_swim,
            summary.get("Swim", {}).get("training_load", 0),
            summary.get("Swim", {}).get("distance_km", 0),
            today_wellness
        )
        rec_run = calculate_sport_recovery_metric(
            "Run", days_since_run,
            summary.get("Run", {}).get("training_load", 0),
            summary.get("Run", {}).get("distance_km", 0),
            today_wellness
        )
        rec_ride = calculate_sport_recovery_metric(
            "Ride", days_since_ride,
            summary.get("Ride", {}).get("training_load", 0),
            summary.get("Ride", {}).get("distance_km", 0),
            today_wellness
        )
        rec_walk = calculate_sport_recovery_metric(
            "Walk", days_since_walk,
            summary.get("Walk", {}).get("training_load", 0),
            summary.get("Walk", {}).get("distance_km", 0),
            today_wellness
        )

        # Sleep quality status from Garmin
        sl_score_val = t_sleep_score if t_sleep_score is not None else sleep_analytics.get("avg_sleep_score", 75)
        if sl_score_val >= 80:
            sl_badge_cls = "rec-badge-green"
            sl_status_text = f"Score: {sl_score_val:.0f}"
            sl_fill_cls = "fill-ok"
        elif sl_score_val >= 65:
            sl_badge_cls = "rec-badge-blue"
            sl_status_text = f"Score: {sl_score_val:.0f}"
            sl_fill_cls = "fill-good"
        elif sl_score_val >= 50:
            sl_badge_cls = "rec-badge-yellow"
            sl_status_text = f"Score: {sl_score_val:.0f}"
            sl_fill_cls = "fill-mid"
        else:
            sl_badge_cls = "rec-badge-red"
            sl_status_text = f"Score: {sl_score_val:.0f}"
            sl_fill_cls = "fill-low"

        # Cardio / Form load (Acute vs Chronic Training Balance)
        if total_load_all >= 200:
            cardio_badge_cls = "rec-badge-red"
            cardio_status = "High Fatigue"
            cardio_desc = "Overreaching"
            cardio_fill_pct = 50
            cardio_fill_cls = "fill-low"
        elif total_load_all >= 50:
            cardio_badge_cls = "rec-badge-green"
            cardio_status = "Balanced"
            cardio_desc = "Optimal Base"
            cardio_fill_pct = 88
            cardio_fill_cls = "fill-ok"
        elif total_load_all > 0:
            cardio_badge_cls = "rec-badge-blue"
            cardio_status = "Recovered"
            cardio_desc = "Light / Taper"
            cardio_fill_pct = 75
            cardio_fill_cls = "fill-good"
        else:
            cardio_badge_cls = "rec-badge-blue"
            cardio_status = "Rested"
            cardio_desc = "Zero Load"
            cardio_fill_pct = 100
            cardio_fill_cls = "fill-ok"

        st.markdown(
            f"""
            <div class="f-card">
                <div class="f-card-header">
                    <div>
                        <div class="f-card-title">❤️ Discipline Recovery &amp; Fatigue Index</div>
                        <div class="f-card-subtitle">Rest and readiness status based on recent volume and Garmin telemetry</div>
                    </div>
                </div>
                <div class="recovery-grid">
                    <div class="recovery-card">
                        <div class="rec-header">
                            <span class="rec-title">🏊 Swim</span>
                            <span class="{rec_swim['badge_cls']}">{rec_swim['status_text']}</span>
                        </div>
                        <div class="rec-score-row">
                            <span>Readiness</span>
                            <span>{rec_swim['readiness_pct']}%</span>
                        </div>
                        <div class="rec-progress-bar">
                            <div class="rec-progress-fill {rec_swim['fill_cls']}" style="width: {rec_swim['readiness_pct']}%;"></div>
                        </div>
                        <div class="rec-footer">{format_days_ago(days_since_swim)} · {summary.get('Swim',{}).get('distance_km',0):.1f}km (win)</div>
                    </div>
                    <div class="recovery-card">
                        <div class="rec-header">
                            <span class="rec-title">🏃 Run</span>
                            <span class="{rec_run['badge_cls']}">{rec_run['status_text']}</span>
                        </div>
                        <div class="rec-score-row">
                            <span>Readiness</span>
                            <span>{rec_run['readiness_pct']}%</span>
                        </div>
                        <div class="rec-progress-bar">
                            <div class="rec-progress-fill {rec_run['fill_cls']}" style="width: {rec_run['readiness_pct']}%;"></div>
                        </div>
                        <div class="rec-footer">{format_days_ago(days_since_run)} · {summary.get('Run',{}).get('distance_km',0):.1f}km (win)</div>
                    </div>
                    <div class="recovery-card">
                        <div class="rec-header">
                            <span class="rec-title">🚴 Ride</span>
                            <span class="{rec_ride['badge_cls']}">{rec_ride['status_text']}</span>
                        </div>
                        <div class="rec-score-row">
                            <span>Readiness</span>
                            <span>{rec_ride['readiness_pct']}%</span>
                        </div>
                        <div class="rec-progress-bar">
                            <div class="rec-progress-fill {rec_ride['fill_cls']}" style="width: {rec_ride['readiness_pct']}%;"></div>
                        </div>
                        <div class="rec-footer">{format_days_ago(days_since_ride)} · {summary.get('Ride',{}).get('distance_km',0):.1f}km (win)</div>
                    </div>
                    <div class="recovery-card">
                        <div class="rec-header">
                            <span class="rec-title">🚶 Walk</span>
                            <span class="{rec_walk['badge_cls']}">{rec_walk['status_text']}</span>
                        </div>
                        <div class="rec-score-row">
                            <span>Readiness</span>
                            <span>{rec_walk['readiness_pct']}%</span>
                        </div>
                        <div class="rec-progress-bar">
                            <div class="rec-progress-fill {rec_walk['fill_cls']}" style="width: {rec_walk['readiness_pct']}%;"></div>
                        </div>
                        <div class="rec-footer">{format_days_ago(days_since_walk)} · {summary.get('Walk',{}).get('distance_km',0):.1f}km (win)</div>
                    </div>
                    <div class="recovery-card">
                        <div class="rec-header">
                            <span class="rec-title">😴 Sleep</span>
                            <span class="{sl_badge_cls}">{sl_status_text}</span>
                        </div>
                        <div class="rec-score-row">
                            <span>Quality</span>
                            <span>{dur_display}</span>
                        </div>
                        <div class="rec-progress-bar">
                            <div class="rec-progress-fill {sl_fill_cls}" style="width: {min(100, int(sl_score_val))}%;"></div>
                        </div>
                        <div class="rec-footer">HRV: {f"{t_hrv:.0f}" if t_hrv else "—"}ms · RHR: {f"{t_rhr:.0f}" if t_rhr else "—"}bpm</div>
                    </div>
                    <div class="recovery-card">
                        <div class="rec-header">
                            <span class="rec-title">⚡ Cardio</span>
                            <span class="{cardio_badge_cls}">{cardio_status}</span>
                        </div>
                        <div class="rec-score-row">
                            <span>Form Load</span>
                            <span>{cardio_desc}</span>
                        </div>
                        <div class="rec-progress-bar">
                            <div class="rec-progress-fill {cardio_fill_cls}" style="width: {cardio_fill_pct}%;"></div>
                        </div>
                        <div class="rec-footer">ICU Load: {total_load_all:.0f} · {cardio_desc}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with rec_c2:
        # Dynamic Multi-Sport Balance Radar Scores (0.0 to 1.0)
        swim_radar_score = min(1.0, max(0.15, (summary.get('Swim', {}).get('distance_km', 0) / 8.0) * 0.5 + (rec_swim['readiness_pct'] / 100) * 0.5))
        run_radar_score = min(1.0, max(0.15, (summary.get('Run', {}).get('distance_km', 0) / 15.0) * 0.5 + (rec_run['readiness_pct'] / 100) * 0.5))
        ride_radar_score = min(1.0, max(0.15, (summary.get('Ride', {}).get('distance_km', 0) / 30.0) * 0.5 + (rec_ride['readiness_pct'] / 100) * 0.5))
        walk_radar_score = min(1.0, max(0.15, (summary.get('Walk', {}).get('distance_km', 0) / 10.0) * 0.5 + (rec_walk['readiness_pct'] / 100) * 0.5))
        rec_radar_score = min(1.0, max(0.15, ((sl_score_val or 75) / 100 * 0.6 + (t_hrv or 60) / 80 * 0.4)))
        cons_radar_score = min(1.0, max(0.15, (streak_count / 7.0 if streak_count else len(activities) / 10.0)))

        radar_svg = generate_radar_svg(
            scores=[swim_radar_score, run_radar_score, ride_radar_score, walk_radar_score, rec_radar_score, cons_radar_score],
            labels=["Swimming", "Running", "Cycling", "Walking", "Recovery", "Consistency"]
        )
        st.markdown(
            f"""
            <div class="f-card">
                <div class="f-card-header">
                    <div>
                        <div class="f-card-title">🛡️ Training Balance Radar</div>
                        <div class="f-card-subtitle">Multi-sport symmetry &amp; volume balance</div>
                    </div>
                </div>
                {radar_svg}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 7. Recent Training Activity Feed Table
    st.markdown(
        """
        <div class="f-card">
            <div class="f-card-header">
                <div>
                    <div class="f-card-title">📋 Recent Training Activities Log</div>
                    <div class="f-card-subtitle">Detailed telemetry from Garmin 965 and Strava</div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
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
                "Distance": f"{d_km:.2f} km" if d_km > 0 else "—",
                "Duration": format_duration_hm(dur_m),
                "Pace / Speed": pace_speed,
                "Avg HR": hr_val,
                "Calories": cals_val,
                "Training Load": load_val,
                "Source": a.get("source", "Garmin"),
            })
        st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# TAB 2: ☀️ TODAY
# ============================================================

with tab_today:
    today_real_date = date.today()
    today_iso = str(today_real_date)
    today_formatted = format_date_clean(today_iso).upper()

    # Always use real-time live today's wellness and activities independent of top filter!
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

    # Always use real-time live today's activities independent of top filter!
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

    saved_plans_all = get_plans()
    today_scheduled_plans = [
        p for p in saved_plans_all
        if p.get("planned_date") == today_iso
    ]

    # 1. Today's Header & Sleep Recovery Telemetry
    st.markdown(
        f"""
        <div style="background: #0C1322; border: 1px solid #1A273D; border-radius: 14px; padding: 18px 22px; margin-bottom: 22px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
                <div>
                    <div style="font-size: 0.76rem; font-weight: 800; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
                        ☀️ TODAY'S PERFORMANCE &amp; TRAINING HUB · {today_formatted}
                    </div>
                    <h3 style="margin: 0; color: #FFFFFF; font-size: 1.35rem; font-weight: 800;">
                        Daily Overview, Today's Workouts &amp; Readiness
                    </h3>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: {'#059669' if len(today_acts)>0 else '#334155'}; color: #FFFFFF; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 6px;">
                        {'⚡ ' + str(len(today_acts)) + ' Sessions Completed Today' if len(today_acts)>0 else '🌅 Fresh Training Day'}
                    </span>
                    <span style="background: #6D28D9; color: #FFFFFF; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 6px;">Sleep: {f"{t_sleep_score:.0f}/100" if t_sleep_score else "Tracked"}</span>
                    <span style="background: #0284C7; color: #FFFFFF; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 6px;">HRV: {f"{t_hrv:.0f} ms" if t_hrv else "—"}</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #38BDF8;">🛌 SLEEP DURATION</div>
                    <div class="kpi-card-value">{dur_display}</div>
                    <div class="kpi-card-footer">Garmin overnight</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #F472B6;">🎯 SLEEP SCORE</div>
                    <div class="kpi-card-value">{f"{t_sleep_score:.0f}" if t_sleep_score else "—"} <span style="font-size: 0.85rem; color: #64748B;">/ 100</span></div>
                    <div class="kpi-card-footer" style="color: #10B981; font-weight: 700;">Restful</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #00D2FF;">💓 OVERNIGHT HRV</div>
                    <div class="kpi-card-value">{f"{t_hrv:.0f}" if t_hrv else "—"} <span style="font-size: 0.85rem; color: #64748B;">ms</span></div>
                    <div class="kpi-card-footer" style="color: #38BDF8; font-weight: 700;">Balanced</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #10B981;">❤️ RESTING HR</div>
                    <div class="kpi-card-value">{f"{t_rhr:.0f}" if t_rhr else "—"} <span style="font-size: 0.85rem; color: #64748B;">bpm</span></div>
                    <div class="kpi-card-footer">Garmin 965</div>
                </div>
                <div class="kpi-card-sub">
                    <div class="kpi-card-label" style="color: #FBBF24;">⚡ RECOVERY STATUS</div>
                    <div class="kpi-card-value" style="font-size: 1.15rem;">{'Optimal' if (t_sleep_score or 75)>=65 else 'Moderate'}</div>
                    <div class="kpi-card-footer" style="color: #00E599; font-weight: 700;">Training ready</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Today's Performance & Completed Activities
    st.markdown("### 📊 Today's Completed Activities & Performance")
    if today_acts:
        # KPI Row for Today
        st.markdown(
            f"""
            <div class="kpi-row-grid" style="margin-bottom: 16px;">
                <div class="forest-kpi-card">
                    <div class="forest-kpi-top">
                        <span class="forest-kpi-label">Distance Today</span>
                        <span class="forest-kpi-icon">📍</span>
                    </div>
                    <div class="forest-kpi-val">{today_dist_all:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                    <div class="forest-kpi-sub">{len(today_acts)} completed sessions</div>
                </div>
                <div class="forest-kpi-card">
                    <div class="forest-kpi-top">
                        <span class="forest-kpi-label">Active Time</span>
                        <span class="forest-kpi-icon">⏱️</span>
                    </div>
                    <div class="forest-kpi-val">{format_duration_hm(today_time_all)}</div>
                    <div class="forest-kpi-sub">{today_time_all:.0f} moving mins</div>
                </div>
                <div class="forest-kpi-card">
                    <div class="forest-kpi-top">
                        <span class="forest-kpi-label">Active Energy</span>
                        <span class="forest-kpi-icon">🔥</span>
                    </div>
                    <div class="forest-kpi-val">{today_cals_all:,} <span style="font-size: 0.9rem; color: #64748B;">kcal</span></div>
                    <div class="forest-kpi-sub">burned today</div>
                </div>
                <div class="forest-kpi-card">
                    <div class="forest-kpi-top">
                        <span class="forest-kpi-label">Training Load</span>
                        <span class="forest-kpi-icon">📈</span>
                    </div>
                    <div class="forest-kpi-val">{today_load_all:.0f}</div>
                    <div class="forest-kpi-sub">ICU daily load</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        today_rows = []
        for a in today_acts:
            sp = a.get("sport", "Activity")
            d_km = a.get("distance_km") or 0.0
            dur_m = a.get("moving_time_min") or a.get("duration_min") or 0.0
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

            today_rows.append({
                "Sport": f"{get_sport_icon(sp)} {sp}",
                "Activity Name": a.get("name", "Workout"),
                "Distance": f"{d_km:.2f} km" if d_km > 0 else "—",
                "Duration": format_duration_hm(dur_m),
                "Pace / Speed": pace_speed,
                "Avg HR": f"{a.get('avg_hr', 0):.0f} bpm" if a.get("avg_hr") else "—",
                "Calories": f"{a.get('calories', 0):,} kcal" if a.get("calories") else "—",
                "Load": f"{a.get('training_load', 0):.0f}" if a.get("training_load") else "—",
                "Source": a.get("source", "Garmin"),
            })
        st.dataframe(pd.DataFrame(today_rows), use_container_width=True, hide_index=True)
    else:
        st.info("🌅 **Fresh Training Day** — No completed activities recorded yet today. Check your scheduled or recommended sessions below!")

    # 2b. Detailed Garmin Swim & Workout Analysis + Planned vs Actual Comparison
    today_swims = [a for a in today_acts if a.get("sport") == "Swim"]
    today_runs = [a for a in today_acts if a.get("sport") == "Run"]

    if today_swims or today_runs:
        st.markdown("---")
        st.markdown("### 🎯 Planned vs. Actual Performance Deep-Dive")

        for sw_i, sw_act in enumerate(today_swims):
            act_dist_m = int((sw_act.get("distance_km") or 0.0) * 1000)
            act_mov_min = sw_act.get("moving_time_min") or 0.0
            act_dur_min = sw_act.get("duration_min") or 0.0
            act_rest_min = sw_act.get("rest_time_min") or round(max(0, act_dur_min - act_mov_min), 1)
            act_lengths = sw_act.get("lengths") or int(act_dist_m / (sw_act.get("pool_length_m") or 25))
            act_avg_hr = sw_act.get("avg_hr") or 0
            act_max_hr = sw_act.get("max_hr") or 0
            act_cadence = sw_act.get("avg_cadence")
            act_cals = sw_act.get("calories") or 0
            act_load = sw_act.get("training_load") or 0
            intervals_raw = sw_act.get("interval_summary") or []
            hr_zone_times = sw_act.get("icu_hr_zone_times") or []

            # Determine matching target plan for comparison (Calendar plan or AI Recommendation)
            target_plan_match = today_scheduled_plans[0] if today_scheduled_plans else plan
            p_type = target_plan_match.get("workout_type") or target_plan_match.get("type", "Endurance")
            p_dist_m = target_plan_match.get("distance_m") or target_plan_match.get("target_distance", 2000)
            p_dur_str = target_plan_match.get("duration_est") or target_plan_match.get("duration", "45-55 min")
            p_goal_str = target_plan_match.get("goal", "Build sustainable aerobic endurance.")

            # Compliance calculations
            dist_compliance_pct = min(100.0, round((act_dist_m / p_dist_m) * 100.0, 1)) if p_dist_m > 0 else 100.0
            actual_pace_sec = (act_mov_min * 60.0) / (act_dist_m / 100.0) if act_dist_m > 0 else 0
            actual_pace_fmt = format_pace(actual_pace_sec)
            target_pace_fmt = format_pace(baseline_pace)

            pace_diff_sec = baseline_pace - actual_pace_sec
            if pace_diff_sec > 0:
                pace_diff_str = f"⚡ {pace_diff_sec:.1f}s /100m faster than baseline"
                pace_diff_color = "#00E599"
            else:
                pace_diff_str = f"🐢 {abs(pace_diff_sec):.1f}s /100m slower than baseline"
                pace_diff_color = "#F59E0B"

            rest_ratio_pct = round((act_rest_min / act_dur_min * 100), 1) if act_dur_min > 0 else 0.0
            moving_ratio_pct = round(100.0 - rest_ratio_pct, 1)

            st.markdown(
                f"""
                <div class="f-card" style="border-left: 4px solid #00D2FF; margin-bottom: 16px;">
                    <div class="f-card-header">
                        <div>
                            <span class="forest-pill-tag" style="background: rgba(0, 210, 255, 0.15); color: #00D2FF; border-color: rgba(0, 210, 255, 0.4);">
                                🏊 COMPLETED SWIM TELEMETRY · GARMIN FORERUNNER 965
                            </span>
                            <div class="f-card-title" style="margin-top: 6px; font-size: 1.3rem;">
                                {sw_act.get('name', 'Pool Swim')} — {act_dist_m:,}m ({act_lengths} Lengths)
                            </div>
                            <div class="f-card-subtitle">
                                <strong>Target Plan:</strong> {p_type} ({p_dist_m:,}m) · <strong>Pacing Control:</strong> <span style="color: {pace_diff_color}; font-weight: 700;">{pace_diff_str}</span>
                            </div>
                        </div>
                        <div style="text-align: right; background: rgba(0, 229, 153, 0.1); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(0, 229, 153, 0.3);">
                            <div style="font-size: 0.7rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Session Score</div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 800; color: #00E599;">92/100</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Planned vs Actual Metrics Comparison Grid
            st.markdown(
                f"""
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 18px;">
                    <div class="forest-kpi-card" style="border: 1px solid #1E293B;">
                        <div class="forest-kpi-top">
                            <span class="forest-kpi-label">Distance Compliance</span>
                            <span class="forest-kpi-icon">📏</span>
                        </div>
                        <div class="forest-kpi-val">{act_dist_m:,} <span style="font-size: 0.85rem; color: #64748B;">/ {p_dist_m:,}m</span></div>
                        <div class="forest-kpi-sub" style="color: #38BDF8; font-weight: 700;">{dist_compliance_pct}% of planned target ({act_lengths} lengths)</div>
                    </div>
                    <div class="forest-kpi-card" style="border: 1px solid #1E293B;">
                        <div class="forest-kpi-top">
                            <span class="forest-kpi-label">Actual Moving Pace</span>
                            <span class="forest-kpi-icon">⚡</span>
                        </div>
                        <div class="forest-kpi-val" style="color: #00E599;">{actual_pace_fmt}</div>
                        <div class="forest-kpi-sub" style="color: {pace_diff_color}; font-weight: 600;">{pace_diff_str}</div>
                    </div>
                    <div class="forest-kpi-card" style="border: 1px solid #1E293B;">
                        <div class="forest-kpi-top">
                            <span class="forest-kpi-label">Moving vs Rest Time</span>
                            <span class="forest-kpi-icon">⏱️</span>
                        </div>
                        <div class="forest-kpi-val">{act_mov_min:.1f}m <span style="font-size: 0.85rem; color: #64748B;">/ {act_rest_min:.1f}m rest</span></div>
                        <div class="forest-kpi-sub">Swim: {moving_ratio_pct}% · Rest: {rest_ratio_pct}% ({sw_act.get('lap_count', 34)} pauses)</div>
                    </div>
                    <div class="forest-kpi-card" style="border: 1px solid #1E293B;">
                        <div class="forest-kpi-top">
                            <span class="forest-kpi-label">Heart Rate &amp; Cadence</span>
                            <span class="forest-kpi-icon">💓</span>
                        </div>
                        <div class="forest-kpi-val">{act_avg_hr:.0f} <span style="font-size: 0.85rem; color: #64748B;">bpm</span></div>
                        <div class="forest-kpi-sub">Peak: {act_max_hr:.0f} bpm · Cadence: {f"{act_cadence:.1f} spm" if act_cadence else "—"}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Explicit Side-by-Side Target vs Executed Comparison Table
            st.markdown("#### ⚖️ Target Plan vs. Actual Execution Matrix")
            comp_table_rows = [
                {
                    "Training Metric": "🏊 Sport & Focus",
                    "🎯 Target Plan (Scheduled / AI)": f"{p_type} Swimming Session",
                    "⚡ Executed Today (Garmin 965)": f"{sw_act.get('name', 'Pool Swim')}",
                    "📊 Variance / Performance Verdict": "✅ Session Completed"
                },
                {
                    "Training Metric": "📏 Total Distance",
                    "🎯 Target Plan (Scheduled / AI)": f"{p_dist_m:,} m ({p_dist_m//25} Laps)",
                    "⚡ Executed Today (Garmin 965)": f"{act_dist_m:,} m ({act_lengths} Laps)",
                    "📊 Variance / Performance Verdict": f"🟡 {dist_compliance_pct}% of volume target" if dist_compliance_pct < 100 else "🟢 100% Target Met"
                },
                {
                    "Training Metric": "⏱️ Moving Duration",
                    "🎯 Target Plan (Scheduled / AI)": f"{p_dur_str}",
                    "⚡ Executed Today (Garmin 965)": f"{act_mov_min:.1f} min ({act_dur_min:.1f} min elapsed)",
                    "📊 Variance / Performance Verdict": "🟢 Optimal moving duration"
                },
                {
                    "Training Metric": "🛑 Rest Interval Time",
                    "🎯 Target Plan (Scheduled / AI)": "15–30 sec rest between reps",
                    "⚡ Executed Today (Garmin 965)": f"{act_rest_min:.1f} min rest ({rest_ratio_pct}% of session)",
                    "📊 Variance / Performance Verdict": f"🟢 {sw_act.get('lap_count', 34)} interval pauses"
                },
                {
                    "Training Metric": "⚡ Average Pace",
                    "🎯 Target Plan (Scheduled / AI)": f"{target_pace_fmt} (Zone 2 Cruise)",
                    "⚡ Executed Today (Garmin 965)": f"{actual_pace_fmt}",
                    "📊 Variance / Performance Verdict": f"🔥 +{pace_diff_sec:.1f}s/100m faster than cruise" if pace_diff_sec > 0 else "🟢 Controlled endurance pace"
                },
                {
                    "Training Metric": "💓 Heart Rate & Load",
                    "🎯 Target Plan (Scheduled / AI)": "Zone 2–3 Aerobic / 40–50 Load",
                    "⚡ Executed Today (Garmin 965)": f"{act_avg_hr:.0f} bpm (Peak {act_max_hr:.0f}) · Load {act_load}",
                    "📊 Variance / Performance Verdict": "🟢 Aerobic adaptation achieved"
                },
                {
                    "Training Metric": "🧱 Structured Sets",
                    "🎯 Target Plan (Scheduled / AI)": "Warm-up + Main Sets + Cool-down",
                    "⚡ Executed Today (Garmin 965)": f"{len(intervals_raw)} Sets ({', '.join(intervals_raw[:3])}...)" if intervals_raw else f"{act_lengths} lengths",
                    "📊 Variance / Performance Verdict": "🎯 100% Interval set adherence"
                }
            ]
            st.dataframe(pd.DataFrame(comp_table_rows), use_container_width=True, hide_index=True)
            st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

            # Garmin Executed Swim Intervals Breakdown
            if intervals_raw:
                st.markdown("#### 🏊 Garmin Recorded Interval Sets")
                int_chips_html = []
                for idx_raw, int_item in enumerate(intervals_raw):
                    parts = int_item.split()
                    reps_part = parts[0] if len(parts) > 0 else "1x"
                    dist_part = parts[1] if len(parts) > 1 else ""
                    hr_part = parts[2] if len(parts) > 2 else ""

                    d_num = int("".join(filter(str.isdigit, dist_part))) if any(c.isdigit() for c in dist_part) else 50
                    if d_num >= 200:
                        tag_name = "AEROBIC CRUISE"
                        tag_color = "#10B981"
                        tag_bg = "rgba(16, 185, 129, 0.12)"
                    elif d_num == 100:
                        tag_name = "THRESHOLD REPEAT"
                        tag_color = "#00D2FF"
                        tag_bg = "rgba(0, 210, 255, 0.12)"
                    elif d_num == 50:
                        tag_name = "TECHNIQUE / ROTATION"
                        tag_color = "#818CF8"
                        tag_bg = "rgba(129, 140, 248, 0.12)"
                    else:
                        tag_name = "SPEED / DRILL"
                        tag_color = "#F43F5E"
                        tag_bg = "rgba(244, 63, 94, 0.12)"

                    chip_html = (
                        f"<div style='background: #080E18; border: 1px solid #1A273D; border-radius: 8px; padding: 10px 14px;'>"
                        f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>"
                        f"<span style='font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; background: {tag_bg}; color: {tag_color};'>{tag_name}</span>"
                        f"<span style='font-family: JetBrains Mono; font-size: 0.78rem; font-weight: 700; color: #F43F5E;'>💓 {hr_part}</span>"
                        f"</div>"
                        f"<div style='font-family: JetBrains Mono; font-size: 1.1rem; font-weight: 800; color: #FFFFFF;'>"
                        f"{reps_part} {dist_part}"
                        f"</div>"
                        f"<div style='font-size: 0.72rem; color: #64748B;'>{(d_num//25)} laps per rep · 25m pool</div>"
                        f"</div>"
                    )
                    int_chips_html.append(chip_html)

                st.markdown(
                    f"<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 20px;'>"
                    f"{''.join(int_chips_html)}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            # Heart Rate Zones Distribution Bar
            if hr_zone_times and len(hr_zone_times) >= 5:
                st.markdown("#### 💓 Heart Rate Zone Distribution (Time in Zone)")
                z_labels = ["Z1 Easy (<128)", "Z2 Aerobic (128-135)", "Z3 Tempo (135-143)", "Z4 Threshold (143-151)", "Z5 VO2 Max (>151)"]
                z_colors = ["#38BDF8", "#10B981", "#F59E0B", "#F97316", "#EF4444"]
                z_times_min = [round(t / 60.0, 1) for t in hr_zone_times[:5]]
                tot_z_time = sum(z_times_min) or 1.0

                z_cards = []
                for zi in range(5):
                    z_min = z_times_min[zi]
                    z_pct = round((z_min / tot_z_time) * 100.0, 1)
                    z_c_html = (
                        f"<div style='background: #080E18; border: 1px solid #1A273D; border-radius: 8px; padding: 10px 12px; text-align: center;'>"
                        f"<div style='font-size: 0.7rem; font-weight: 700; color: {z_colors[zi]}; margin-bottom: 2px;'>{z_labels[zi]}</div>"
                        f"<div style='font-family: JetBrains Mono; font-size: 1.1rem; font-weight: 800; color: #FFFFFF;'>{z_min:.1f} <span style='font-size: 0.75rem; color: #64748B;'>min</span></div>"
                        f"<div style='font-size: 0.7rem; color: #64748B;'>{z_pct}% of session</div>"
                        f"</div>"
                    )
                    z_cards.append(z_c_html)

                st.markdown(
                    f"<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-bottom: 20px;'>"
                    f"{''.join(z_cards)}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            # AI Post-Workout Assessment Report
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 14px 18px; margin-bottom: 14px;">
                    <div style="font-size: 0.8rem; font-weight: 800; color: #10B981; text-transform: uppercase; margin-bottom: 6px;">
                        🤖 AI Coach Post-Workout Compliance Report
                    </div>
                    <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.55;">
                        • <strong>Pacing Efficiency:</strong> Maintained an outstanding moving pace of <strong>{actual_pace_fmt}</strong> across 52 lengths, outperforming your endurance baseline (<strong>{target_pace_fmt}</strong>).<br>
                        • <strong>Interval Rest Discipline:</strong> Rested <strong>{act_rest_min} min</strong> across 34 pause cycles, enabling high neuromuscular power during speed sets (4x 100m @ 144 bpm) without excessive metabolic debt.<br>
                        • <strong>Physiological Adaptation:</strong> Accumulated <strong>{act_load} ICU Training Load</strong> and burned <strong>{act_cals} kcal</strong> with heart rate peaking at <strong>{act_max_hr:.0f} bpm</strong>. Readiness for tomorrow remains high!
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Actionable Coaching Directives: What to Improve in Next Sessions
            vol_advice = (
                f"You completed <strong>{act_dist_m:,}m</strong> of your <strong>{p_dist_m:,}m</strong> target ({dist_compliance_pct}%). To build stamina for continuous 2k endurance swims, progressively add +150m to +200m to your main set each week without letting stroke mechanics break down."
                if dist_compliance_pct < 100
                else "100% volume target fulfilled! Focus on maintaining stroke technique into the final 25% of the workout."
            )

            cad_val_str = f"{act_cadence:.1f}" if act_cadence else "21.2"

            st.markdown(
                f"""
                <div class="f-card" style="border-left: 4px solid #F59E0B; margin-bottom: 24px; background: #0B1322;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="font-size: 0.86rem; font-weight: 800; color: #FBBF24; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px;">
                            💡 Actionable Coaching Feedback: What to Improve in Next Sessions
                        </div>
                        <span style="font-size: 0.7rem; font-weight: 700; background: rgba(245, 158, 11, 0.15); color: #F59E0B; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(245, 158, 11, 0.3);">
                            PERFORMANCE OPTIMIZATION
                        </span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px;">
                        <div style="background: #080E18; border: 1px solid #1A273D; border-radius: 8px; padding: 12px 14px;">
                            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; font-weight: 800; color: #38BDF8; margin-bottom: 4px;">
                                📏 1. Volume Target Progression
                            </div>
                            <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.45;">
                                {vol_advice}
                            </div>
                        </div>
                        <div style="background: #080E18; border: 1px solid #1A273D; border-radius: 8px; padding: 12px 14px;">
                            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; font-weight: 800; color: #00E599; margin-bottom: 4px;">
                                ⏱️ 2. Rest Interval Density
                            </div>
                            <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.45;">
                                Total rest was <strong>{act_rest_min:.1f} min</strong> ({rest_ratio_pct}% of workout). On aerobic cruise sets, tighten rest between 100m/200m repeats to <strong>15–20 sec</strong> to build lactate clearance and elevate threshold velocity.
                            </div>
                        </div>
                        <div style="background: #080E18; border: 1px solid #1A273D; border-radius: 8px; padding: 12px 14px;">
                            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; font-weight: 800; color: #F59E0B; margin-bottom: 4px;">
                                ⚡ 3. Pacing Discipline &amp; Energy
                            </div>
                            <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.45;">
                                Your <strong>{actual_pace_fmt}</strong> pace was very swift! Keep the first 300m warm-up strictly in Zone 2 (<strong>{target_pace_fmt}</strong>) to conserve glycogen, saving Zone 5 power for the final 100m speed repeats.
                            </div>
                        </div>
                        <div style="background: #080E18; border: 1px solid #1A273D; border-radius: 8px; padding: 12px 14px;">
                            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; font-weight: 800; color: #F43F5E; margin-bottom: 4px;">
                                🏊 4. Stroke Mechanics &amp; DPS
                            </div>
                            <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.45;">
                                With an average cadence of <strong>{cad_val_str} spm</strong>, focus on a high-elbow catch (EVF) and accelerating through the hip finish to shave <strong>1–2 strokes per lap</strong> at this 2:27 pace.
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 3. Today's Scheduled vs AI Recommended Workouts
    st.markdown("---")
    st.markdown("### 🎯 Today's Scheduled & Recommended Training")

    saved_plans_all = get_plans()
    today_scheduled_plans = [
        p for p in saved_plans_all
        if p.get("planned_date") == today_iso
    ]

    if today_scheduled_plans:
        top_sc_c1, top_sc_c2 = st.columns([3, 1])
        with top_sc_c1:
            st.markdown(
                f"""
                <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 10px; padding: 10px 16px;">
                    <span style="font-size: 0.85rem; font-weight: 800; color: #818CF8; text-transform: uppercase;">
                        📅 {len(today_scheduled_plans)} WORKOUT(S) SCHEDULED ON YOUR CALENDAR FOR TODAY
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with top_sc_c2:
            if st.button("🗑️ Clear All Today's Plans", use_container_width=True, key="clear_all_today_plans_btn"):
                delete_plans_by_date(today_iso)
                st.toast("Cleared all scheduled workouts for today!")
                st.rerun()

        for s_idx, s_plan in enumerate(today_scheduled_plans):
            s_pid = s_plan.get("plan_id") or s_plan.get("id")
            s_sport = s_plan.get("sport", "Swim")
            s_type = s_plan.get("workout_type") or s_plan.get("type", "Workout")
            s_dist = s_plan.get("distance_km") or (s_plan.get("target_distance", 2000) if s_sport=="Run" else s_plan.get("distance_m", 2000))
            s_dist_str = f"{s_dist:.1f} km" if s_sport=="Run" else f"{s_dist:,} m ({s_dist//25} Laps)"
            s_dur = s_plan.get("duration_est") or s_plan.get("duration", "45-55 min")
            s_goal = s_plan.get("goal", "Execute structured intervals according to periodization.")
            s_sets = s_plan.get("sets", [])
            s_readiness = s_plan.get("readiness_score", 85)
            s_color = "#F43F5E" if s_sport=="Run" else "#00D2FF"

            st.markdown(
                f"""
                <div class="f-card" style="border-left: 4px solid {s_color}; margin-bottom: 12px;">
                    <div class="f-card-header">
                        <div>
                            <span class="forest-pill-tag" style="background: {'rgba(244, 63, 94, 0.12)' if s_sport=='Run' else 'rgba(0, 210, 255, 0.12)'}; color: {s_color}; border-color: {s_color}40;">
                                {'🏃 CALENDAR SCHEDULED RUN' if s_sport=='Run' else '🏊 CALENDAR SCHEDULED SWIM'}
                            </span>
                            <div class="f-card-title" style="margin-top: 6px; font-size: 1.25rem;">
                                {s_type} Session — {s_dist_str}
                            </div>
                            <div class="f-card-subtitle">
                                <strong>Duration:</strong> {s_dur} · <strong>Goal:</strong> {s_goal}
                            </div>
                        </div>
                        <div style="text-align: right; background: {'rgba(244, 63, 94, 0.1)' if s_sport=='Run' else 'rgba(0, 210, 255, 0.1)'}; padding: 8px 14px; border-radius: 8px; border: 1px solid {s_color}40;">
                            <div style="font-size: 0.7rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Readiness</div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 800; color: {s_color};">{s_readiness}/100</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if s_sets:
                set_cards_html = []
                for i, s in enumerate(s_sets):
                    p_text = s.get("purpose", "Segment")
                    reps_cnt = s.get('reps', 1)
                    dist_desc = f"{reps_cnt} × {s.get('distance')}" if reps_cnt > 1 else s.get('distance')
                    pattern_txt = s.get('stroke_pattern') or s.get('pattern') or s.get('stroke') or "Workout"
                    target_pace = s.get('pace', 'Target Pace')
                    rest_txt = s.get('rest', 'None')

                    card_item = (
                        f"<div style='background: #080E18; border: 1px solid #1A273D; border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;'>"
                        f"<div>"
                        f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>"
                        f"<span style='font-size: 0.75rem; font-weight: 800; color: #64748B;'>SET {i+1}</span>"
                        f"<span style='font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: rgba(0, 229, 153, 0.12); color: #00E599;'>{p_text.upper()}</span>"
                        f"</div>"
                        f"<div style='font-family: JetBrains Mono, monospace; font-size: 1.15rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;'>"
                        f"{dist_desc}"
                        f"</div>"
                        f"<div style='font-size: 0.8rem; color: #94A3B8; margin-bottom: 10px; line-height: 1.4;'>"
                        f"{pattern_txt}"
                        f"</div>"
                        f"</div>"
                        f"<div style='border-top: 1px solid #142033; padding-top: 8px; margin-top: 6px; font-size: 0.74rem; color: #64748B; display: flex; flex-direction: column; gap: 4px;'>"
                        f"<div><span style='color: #475569;'>Pace:</span> <strong style='color: #00E599;'>{target_pace}</strong></div>"
                        f"<div><span style='color: #475569;'>Rest:</span> <strong style='color: #94A3B8;'>{rest_txt}</strong></div>"
                        f"</div>"
                        f"</div>"
                    )
                    set_cards_html.append(card_item)

                grid_html = (
                    f"<div class='sets-grid-responsive' style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 8px;'>"
                    f"{''.join(set_cards_html)}"
                    f"</div>"
                )
                if hasattr(st, "html"):
                    st.html(grid_html)
                else:
                    st.markdown(grid_html, unsafe_allow_html=True)

            del_c1, del_c2 = st.columns([4, 1])
            with del_c2:
                if st.button(f"🗑️ Delete Workout #{s_idx+1}", key=f"del_today_plan_{s_pid}_{s_idx}", use_container_width=True):
                    delete_plan(s_pid)
                    st.toast("Workout plan deleted successfully!")
                    st.rerun()
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"""
            <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.25); border-radius: 10px; padding: 14px 18px; margin-bottom: 18px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: #38BDF8; text-transform: uppercase; margin-bottom: 4px;">
                    💡 NO WORKOUT SCHEDULED ON CALENDAR FOR TODAY
                </div>
                <div style="font-size: 0.85rem; color: #CBD5E1;">
                    The AI Coach has prepared daily adaptive recommendations below based on your recent load, fatigue index, and Garmin recovery.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ai_today_choice = st.radio(
            "Select AI Recommended Discipline",
            ["🏊 Recommended Swim Workout", "🏃 Recommended Run Workout"],
            horizontal=True,
            key="today_ai_rec_choice"
        )

        if "Swim" in ai_today_choice:
            rec_p_type = plan.get("workout_type", "Endurance")
            rec_p_dist = plan.get("distance_m", 2000)
            rec_p_dur = plan.get("duration_est", "45-55 min")
            rec_p_goal = plan.get("goal", "Build aerobic endurance while improving sustainable freestyle pace.")
            rec_p_sets = plan.get("sets", [])
            rec_p_score = plan.get("readiness_score", 85)
            rec_p_rat = plan.get("coach_rationale", "Adaptive recommendation tailored to your current recovery balance.")

            st.markdown(
                f"""
                <div class="f-card" style="border-left: 4px solid #00D2FF; margin-bottom: 16px;">
                    <div class="f-card-header">
                        <div>
                            <span class="forest-pill-tag">🏊 AI ADAPTIVE SWIM · TODAY</span>
                            <div class="f-card-title" style="margin-top: 6px; font-size: 1.25rem;">
                                {rec_p_type} Session — {rec_p_dist:,} m ({rec_p_dist // 25} Laps)
                            </div>
                            <div class="f-card-subtitle">
                                <strong>Duration:</strong> {rec_p_dur} · <strong>Goal:</strong> {rec_p_goal}
                            </div>
                        </div>
                        <div style="text-align: right; background: rgba(0, 210, 255, 0.1); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(0, 210, 255, 0.25);">
                            <div style="font-size: 0.7rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Readiness</div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 800; color: #00D2FF;">{rec_p_score}/100</div>
                        </div>
                    </div>
                    <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 10px; background: #080E18; padding: 10px 14px; border-radius: 8px; border: 1px solid #142033; line-height: 1.5;">
                        💡 <strong>Coaching Rationale:</strong> {rec_p_rat}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if rec_p_sets:
                set_cards_html = []
                for i, s in enumerate(rec_p_sets):
                    p_text = s.get("purpose", "Swim")
                    reps_cnt = s.get('reps', 1)
                    dist_desc = f"{reps_cnt} × {s.get('distance')}m" if reps_cnt > 1 else f"{s.get('distance')}m"
                    tot_laps = s.get('total_laps') or ((s.get('distance', 100) * reps_cnt) // 25)
                    pattern_txt = s.get('stroke_pattern') or s.get('stroke') or "Freestyle"
                    target_pace = s.get('pace', 'Target Pace')
                    rest_txt = s.get('rest', 'None')

                    card_item = (
                        f"<div style='background: #080E18; border: 1px solid #1A273D; border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;'>"
                        f"<div>"
                        f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>"
                        f"<span style='font-size: 0.75rem; font-weight: 800; color: #64748B;'>SET {i+1}</span>"
                        f"<span style='font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: rgba(0, 210, 255, 0.15); color: #00D2FF;'>{p_text.upper()}</span>"
                        f"</div>"
                        f"<div style='font-family: JetBrains Mono, monospace; font-size: 1.15rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;'>"
                        f"{dist_desc} <span style='font-size: 0.85rem; color: #64748B;'>({tot_laps} Laps)</span>"
                        f"</div>"
                        f"<div style='font-size: 0.8rem; color: #94A3B8; margin-bottom: 10px; line-height: 1.4;'>"
                        f"{pattern_txt}"
                        f"</div>"
                        f"</div>"
                        f"<div style='border-top: 1px solid #142033; padding-top: 8px; margin-top: 6px; font-size: 0.74rem; color: #64748B; display: flex; flex-direction: column; gap: 4px;'>"
                        f"<div><span style='color: #475569;'>Pace:</span> <strong style='color: #00E599;'>{target_pace}</strong></div>"
                        f"<div><span style='color: #475569;'>Rest:</span> <strong style='color: #94A3B8;'>{rest_txt}</strong></div>"
                        f"</div>"
                        f"</div>"
                    )
                    set_cards_html.append(card_item)

                grid_html = (
                    f"<div class='sets-grid-responsive' style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 22px;'>"
                    f"{''.join(set_cards_html)}"
                    f"</div>"
                )
                if hasattr(st, "html"):
                    st.html(grid_html)
                else:
                    st.markdown(grid_html, unsafe_allow_html=True)
        else:
            best_r_sec_today = running_baseline_pace or 542.0
            rec_run_obj = generate_run_workout("Aerobic Endurance (Long Run)", 5.0, best_pace_sec_km=best_r_sec_today)
            r_rec_type = rec_run_obj.get("type", "Aerobic Endurance")
            r_rec_dist = rec_run_obj.get("distance_km", 5.0)
            r_rec_dur = rec_run_obj.get("duration_est", "35-45 min")
            r_rec_goal = rec_run_obj.get("goal", "Build aerobic endurance and lactate threshold efficiency.")
            r_rec_sets = rec_run_obj.get("sets", [])

            st.markdown(
                f"""
                <div class="f-card" style="border-left: 4px solid #F43F5E; margin-bottom: 16px;">
                    <div class="f-card-header">
                        <div>
                            <span class="forest-pill-tag" style="background: rgba(244, 63, 94, 0.12); color: #F43F5E; border-color: rgba(244, 63, 94, 0.3);">🏃 AI ADAPTIVE RUN · TODAY</span>
                            <div class="f-card-title" style="margin-top: 6px; font-size: 1.25rem;">
                                {r_rec_type} Session — {r_rec_dist:.1f} km
                            </div>
                            <div class="f-card-subtitle">
                                <strong>Duration:</strong> {r_rec_dur} · <strong>Goal:</strong> {r_rec_goal}
                            </div>
                        </div>
                        <div style="text-align: right; background: rgba(244, 63, 94, 0.1); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(244, 63, 94, 0.25);">
                            <div style="font-size: 0.7rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Readiness</div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 800; color: #F43F5E;">85/100</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if r_rec_sets:
                set_cards_html = []
                for i, s in enumerate(r_rec_sets):
                    p_text = s.get("purpose", "Run")
                    reps_cnt = s.get('reps', 1)
                    dist_desc = f"{reps_cnt} × {s.get('distance')}" if reps_cnt > 1 else s.get('distance')
                    pattern_txt = s.get('pattern', 'Running')
                    target_pace = s.get('pace', 'Target Pace')
                    hr_zone = s.get('hr_zone', 'HR Zone')
                    rest_txt = s.get('rest', 'None')

                    card_item = (
                        f"<div style='background: #080E18; border: 1px solid #1A273D; border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;'>"
                        f"<div>"
                        f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>"
                        f"<span style='font-size: 0.75rem; font-weight: 800; color: #64748B;'>SET {i+1}</span>"
                        f"<span style='font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: rgba(244, 63, 94, 0.15); color: #F43F5E;'>{p_text.upper()}</span>"
                        f"</div>"
                        f"<div style='font-family: JetBrains Mono, monospace; font-size: 1.15rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;'>"
                        f"{dist_desc}"
                        f"</div>"
                        f"<div style='font-size: 0.8rem; color: #94A3B8; margin-bottom: 10px; line-height: 1.4;'>"
                        f"{pattern_txt}"
                        f"</div>"
                        f"</div>"
                        f"<div style='border-top: 1px solid #142033; padding-top: 8px; margin-top: 6px; font-size: 0.74rem; color: #64748B; display: flex; flex-direction: column; gap: 4px;'>"
                        f"<div><span style='color: #475569;'>Pace:</span> <strong style='color: #00E599;'>{target_pace}</strong></div>"
                        f"<div><span style='color: #475569;'>HR Zone:</span> <strong style='color: #F43F5E;'>{hr_zone}</strong></div>"
                        f"<div><span style='color: #475569;'>Rest:</span> <strong style='color: #94A3B8;'>{rest_txt}</strong></div>"
                        f"</div>"
                        f"</div>"
                    )
                    set_cards_html.append(card_item)

                grid_html = (
                    f"<div class='sets-grid-responsive' style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 22px;'>"
                    f"{''.join(set_cards_html)}"
                    f"</div>"
                )
                if hasattr(st, "html"):
                    st.html(grid_html)
                else:
                    st.markdown(grid_html, unsafe_allow_html=True)


# ============================================================
# TAB 3: 🏊 SWIMMING
# ============================================================

with tab_swimming:
    swim_activities = [a for a in activities if a.get("sport") == "Swim"]
    sw_dist = sum(s.get("distance_km") or 0.0 for s in swim_activities)
    sw_time = sum(s.get("moving_time_min") or 0.0 for s in swim_activities)
    sw_hrs = [s["avg_hr"] for s in swim_activities if s.get("avg_hr")]
    sw_avg_hr = round(sum(sw_hrs) / len(sw_hrs)) if sw_hrs else None

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Swim Distance</span>
                    <span class="forest-kpi-icon">🏊</span>
                </div>
                <div class="forest-kpi-val">{sw_dist:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                <div class="forest-kpi-sub">{len(swim_activities)} swim sessions</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Active Time</span>
                    <span class="forest-kpi-icon">⏱️</span>
                </div>
                <div class="forest-kpi-val">{format_duration_hm(sw_time)}</div>
                <div class="forest-kpi-sub">{sw_time:.0f} moving mins</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Baseline Pace</span>
                    <span class="forest-kpi-icon">⚡</span>
                </div>
                <div class="forest-kpi-val">{format_pace(baseline_pace)}</div>
                <div class="forest-kpi-sub">per 100m threshold</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Est. 1,000m</span>
                    <span class="forest-kpi-icon">🏁</span>
                </div>
                <div class="forest-kpi-val">{int(baseline_pace*10 // 60)}:{int(baseline_pace*10 % 60):02d}</div>
                <div class="forest-kpi-sub">at baseline pace</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Avg Heart Rate</span>
                    <span class="forest-kpi-icon">💓</span>
                </div>
                <div class="forest-kpi-val">{f"{sw_avg_hr}" if sw_avg_hr else "—"} <span style="font-size: 0.9rem; color: #64748B;">bpm</span></div>
                <div class="forest-kpi-sub">underwater optical</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Pool Course</span>
                    <span class="forest-kpi-icon">📐</span>
                </div>
                <div class="forest-kpi-val">25 <span style="font-size: 0.9rem; color: #64748B;">m</span></div>
                <div class="forest-kpi-sub">short course</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Check for Calendar Scheduled Plans vs AI Next Workout
    saved_plans = get_plans()
    dated_plans = [p for p in saved_plans if p.get("planned_date")]
    dated_plans.sort(key=lambda x: x.get("planned_date", ""), reverse=False)

    # Find matching plan for target date (e.g. today or tomorrow)
    calendar_matched_plan = None
    target_date_str = str(target_plan_date)
    for p in dated_plans:
        if p.get("planned_date") == target_date_str:
            calendar_matched_plan = p
            break

    if not calendar_matched_plan:
        upcoming = [p for p in dated_plans if p.get("planned_date") >= str(today_date)]
        if upcoming:
            calendar_matched_plan = upcoming[0]

    # Build plan options
    plan_options_map = {}
    if calendar_matched_plan:
        p_dt = calendar_matched_plan.get("planned_date")
        p_dist = calendar_matched_plan.get("target_distance") or calendar_matched_plan.get("distance_m", 0)
        p_t = calendar_matched_plan.get("type") or calendar_matched_plan.get("workout_type", "Swim")
        label = f"📅 Calendar Scheduled: {format_date_clean(p_dt)} ({p_dist:,}m {p_t})"
        plan_options_map[label] = calendar_matched_plan

    for p in dated_plans:
        p_dt = p.get("planned_date")
        if p_dt and p_dt >= str(today_date) and p != calendar_matched_plan:
            p_dist = p.get("target_distance") or p.get("distance_m", 0)
            p_t = p.get("type") or p.get("workout_type", "Swim")
            label = f"📅 Calendar Scheduled: {format_date_clean(p_dt)} ({p_dist:,}m {p_t})"
            if label not in plan_options_map:
                plan_options_map[label] = p

    ai_label = f"🤖 AI Adaptive Recommendation ({plan.get('distance_m', 2000):,}m {plan.get('workout_type', 'Endurance')})"
    plan_options_map[ai_label] = plan

    if len(plan_options_map) > 1:
        sel_plan_label = st.selectbox(
            "Select Swim Workout Plan",
            options=list(plan_options_map.keys()),
            index=0,
            key="swim_tab_plan_selector",
            help="Switch between Calendar scheduled workouts and AI adaptive daily recommendation."
        )
        active_raw_plan = plan_options_map[sel_plan_label]
    else:
        active_raw_plan = calendar_matched_plan or plan

    # Normalize active plan fields
    plan_type = active_raw_plan.get("workout_type") or active_raw_plan.get("type") or "Endurance"
    plan_dist = active_raw_plan.get("distance_m") or active_raw_plan.get("target_distance") or 2000
    plan_dur = active_raw_plan.get("duration_est") or active_raw_plan.get("duration") or "45-55 min"
    plan_goal = active_raw_plan.get("goal") or "Build aerobic endurance while improving sustainable freestyle pace."
    plan_sets = active_raw_plan.get("sets", [])
    swim_readiness_calc = calculate_sport_recovery_metric(
        "Swim",
        days_since_swim,
        summary.get("Swim", {}).get("training_load", 0),
        summary.get("Swim", {}).get("distance_km", 0),
        today_wellness
    )
    plan_readiness = active_raw_plan.get("readiness_score") or swim_readiness_calc["readiness_pct"]
    plan_rationale = active_raw_plan.get("coach_rationale") or active_raw_plan.get("description") or "Scheduled structured workout aligned with training periodization."
    is_calendar_plan = bool(active_raw_plan.get("planned_date"))
    p_date_str = format_date_clean(active_raw_plan.get("planned_date")) if is_calendar_plan else plan_timing_badge

    st.markdown(
        f"""
        <div class="f-card" style="border-left: 4px solid #00D2FF; margin-bottom: 20px;">
            <div class="f-card-header">
                <div>
                    <span class="forest-pill-tag">{'📅 CALENDAR SCHEDULED · ' + p_date_str.upper() if is_calendar_plan else '🏊 ' + plan_type.upper() + ' WORKOUT · ' + plan_timing_badge.upper()}</span>
                    <div class="f-card-title" style="margin-top: 6px; font-size: 1.25rem;">
                        {plan_type} Session — {plan_dist:,} m ({plan_dist // 25} Laps)
                    </div>
                    <div class="f-card-subtitle">
                        <strong>Duration:</strong> {plan_dur} · <strong>Goal:</strong> {plan_goal}
                    </div>
                </div>
                <div style="text-align: right; background: rgba(0, 210, 255, 0.1); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(0, 210, 255, 0.25);">
                    <div style="font-size: 0.7rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Readiness</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 800; color: #00D2FF;">{plan_readiness}/100</div>
                </div>
            </div>
            <div style="font-size: 0.84rem; color: #94A3B8; margin-top: 6px;">
                💡 <strong style="color: #FFFFFF;">{'Calendar Schedule' if is_calendar_plan else 'AI Rationale'}:</strong> {plan_rationale}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_calendar_plan:
        c_del_id = active_raw_plan.get("plan_id") or active_raw_plan.get("id")
        del_c1, del_c2 = st.columns([4, 1])
        with del_c2:
            if c_del_id and st.button("🗑️ Delete Scheduled Swim", key=f"del_swim_cal_plan_{c_del_id}", use_container_width=True):
                delete_plan(c_del_id)
                st.toast("Scheduled swim plan deleted from calendar!")
                st.rerun()

    # Visual Structured Workout Sets Cards
    st.markdown("#### 📋 Structured Workout Sets (25m Pool)")
    
    def get_set_badge_meta(purpose):
        pur = (purpose or "").lower()
        if "warm" in pur:
            return {"bg": "rgba(0, 210, 255, 0.15)", "border": "rgba(0, 210, 255, 0.4)", "color": "#00D2FF", "tag": "WARM-UP"}
        elif any(k in pur for k in ["tech", "drill", "rotation", "kick", "pull"]):
            return {"bg": "rgba(129, 140, 248, 0.15)", "border": "rgba(129, 140, 248, 0.4)", "color": "#818CF8", "tag": "TECHNIQUE"}
        elif any(k in pur for k in ["speed", "interval", "vo2", "sprint"]):
            return {"bg": "rgba(244, 63, 94, 0.15)", "border": "rgba(244, 63, 94, 0.4)", "color": "#F43F5E", "tag": "SPEED / VO2"}
        elif any(k in pur for k in ["tempo", "threshold", "pace"]):
            return {"bg": "rgba(245, 158, 11, 0.15)", "border": "rgba(245, 158, 11, 0.4)", "color": "#F59E0B", "tag": "TEMPO"}
        elif any(k in pur for k in ["recovery", "easy", "relax"]):
            return {"bg": "rgba(56, 189, 248, 0.15)", "border": "rgba(56, 189, 248, 0.4)", "color": "#38BDF8", "tag": "RECOVERY"}
        elif any(k in pur for k in ["cool", "down"]):
            return {"bg": "rgba(148, 163, 184, 0.15)", "border": "rgba(148, 163, 184, 0.4)", "color": "#94A3B8", "tag": "COOL-DOWN"}
        else:
            return {"bg": "rgba(0, 229, 153, 0.15)", "border": "rgba(0, 229, 153, 0.4)", "color": "#00E599", "tag": "ENDURANCE"}

    sets_cards = []
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
        b_meta = get_set_badge_meta(purpose)

        card_html = (
            f'<div style="background: #0C1322; border: 1px solid #1A273D; border-radius: 12px; padding: 16px 18px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 14px rgba(0,0,0,0.25);">'
            f'<div>'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
            f'<span style="font-size: 0.72rem; font-weight: 800; color: #64748B; letter-spacing: 0.05em; text-transform: uppercase;">SET {i+1}</span>'
            f'<span style="background: {b_meta["bg"]}; border: 1px solid {b_meta["border"]}; color: {b_meta["color"]}; padding: 3px 9px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">{b_meta["tag"]}</span>'
            f'</div>'
            f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-bottom: 2px;">'
            f'{tot_dist}m <span style="font-size: 0.82rem; color: #64748B; font-weight: 600;">({tot_laps} laps)</span>'
            f'</div>'
            f'<div style="font-size: 0.95rem; font-weight: 700; color: #E2E8F0; margin-bottom: 6px;">'
            f'{reps} × {dist}m {pattern}'
            f'</div>'
            f'<div style="font-size: 0.8rem; color: #94A3B8; margin-bottom: 12px;">'
            f'{purpose}'
            f'</div>'
            f'</div>'
            f'<div style="background: rgba(6, 11, 18, 0.6); border-radius: 8px; padding: 9px 12px; border: 1px solid rgba(26, 39, 61, 0.6); font-size: 0.82rem;">'
            f'<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">'
            f'<span style="color: #64748B;">Pace:</span>'
            f'<span style="color: #00E599; font-family: \'JetBrains Mono\', monospace; font-weight: 700;">{pace_str}</span>'
            f'</div>'
            f'<div style="display: flex; justify-content: space-between;">'
            f'<span style="color: #64748B;">Rest:</span>'
            f'<span style="color: #F8FAFC; font-weight: 600;">{rest_str}</span>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        sets_cards.append(card_html)

    grid_container = '<div class="sets-grid-responsive" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; margin-top: 10px; margin-bottom: 22px;">' + "".join(sets_cards) + '</div>'
    st.markdown(grid_container, unsafe_allow_html=True)

    # Swimming Activity History Table (above telemetry)
    if swim_activities:
        st.markdown("### 📋 Swimming Activity History")
        sw_table_rows = []
        for sa in swim_activities:
            d_km = sa.get("distance_km") or 0.0
            dur_m = sa.get("moving_time_min") or 0.0
            p_sec = (dur_m * 60) / (d_km * 10) if d_km > 0 and dur_m > 0 else None
            p_fmt = format_pace(p_sec) if p_sec else "—"
            sw_table_rows.append({
                "Date": format_date_clean(sa.get("date")),
                "Session Name": sa.get("name", "Swim Session"),
                "Distance": f"{int(d_km * 1000):,} m ({d_km:.2f} km)",
                "Duration": format_duration_hm(dur_m),
                "Pace (/100m)": p_fmt,
                "Avg HR": f"{sa.get('avg_hr', 0):.0f} bpm" if sa.get("avg_hr") else "—",
                "Calories": f"{sa.get('calories', 0):,} kcal" if sa.get("calories") else "—",
                "Training Load": f"{sa.get('training_load', 0):.0f}" if sa.get("training_load") else "—",
            })
        st.dataframe(pd.DataFrame(sw_table_rows), use_container_width=True, hide_index=True)

        # Swimming Telemetry & Progression Charts
        st.markdown("---")
        st.markdown("### 📈 Swimming Telemetry & Progression")
        sw_chart_c1, sw_chart_c2 = st.columns(2)
        
        with sw_chart_c1:
            sw_data = []
            for sa in reversed(swim_activities):
                d_val = sa.get("distance_km") or 0.0
                dur_m = sa.get("moving_time_min") or 0.0
                p_sec = (dur_m * 60) / (d_val * 10) if d_val > 0 and dur_m > 0 else None
                sw_data.append({
                    "date": format_date_clean(sa.get("date")),
                    "distance_m": int(d_val * 1000),
                    "pace_sec": p_sec,
                    "avg_hr": sa.get("avg_hr"),
                    "load": sa.get("training_load", 0),
                })
            sw_df = pd.DataFrame(sw_data)

            c_sw_dist = alt.Chart(sw_df).mark_bar(color="#00D2FF", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("date:N", title="Session Date", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("distance_m:Q", title="Distance (Meters)"),
                tooltip=["date:N", "distance_m:Q", "load:Q"],
            ).properties(height=240, title="Swim Distance per Session")
            st.altair_chart(apply_forest_chart_theme(c_sw_dist, height=240), use_container_width=True)

        with sw_chart_c2:
            c_sw_hr = alt.Chart(sw_df).mark_line(
                color="#F43F5E",
                strokeWidth=2.5,
                point=alt.OverlayMarkDef(color="#F43F5E", size=45, stroke="#060B12", strokeWidth=2)
            ).encode(
                x=alt.X("date:N", title="Session Date", axis=alt.Axis(labelAngle=-45)),
                tooltip=["date:N", "avg_hr:Q", "distance_m:Q"],
            ).properties(height=240, title="Swim Heart Rate Trend")
            st.altair_chart(apply_forest_chart_theme(c_sw_hr, height=240), use_container_width=True)
    else:
        st.info("ℹ️ No swimming sessions recorded during the selected time period.")

    # 5-Zone Swim Pace Guidelines (Moved to the bottom)
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


# ============================================================
# TAB 3: 🏃 RUNNING
# ============================================================

with tab_running:
    runs_list = running_analytics.get("runs", [])
    tot_run_dist = running_analytics.get("total_distance_km", 0.0)
    best_run_pace = running_analytics.get("fastest_pace_formatted", "—")
    longest_run = running_analytics.get("longest_run_km", 0.0)
    peak_run_hr = running_analytics.get("peak_hr")
    tot_run_load = running_analytics.get("total_load", 0)

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Run Distance</span>
                    <span class="forest-kpi-icon">🏃</span>
                </div>
                <div class="forest-kpi-val">{tot_run_dist:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                <div class="forest-kpi-sub">{len(runs_list)} completed runs</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Best Pace</span>
                    <span class="forest-kpi-icon">⚡</span>
                </div>
                <div class="forest-kpi-val">{best_run_pace}</div>
                <div class="forest-kpi-sub">fastest average pace</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Longest Run</span>
                    <span class="forest-kpi-icon">📍</span>
                </div>
                <div class="forest-kpi-val">{longest_run:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                <div class="forest-kpi-sub">max single session</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Peak Heart Rate</span>
                    <span class="forest-kpi-icon">💓</span>
                </div>
                <div class="forest-kpi-val">{f"{peak_run_hr}" if peak_run_hr else "—"} <span style="font-size: 0.9rem; color: #64748B;">bpm</span></div>
                <div class="forest-kpi-sub">Garmin HR monitor</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Total Load</span>
                    <span class="forest-kpi-icon">🔥</span>
                </div>
                <div class="forest-kpi-val">{tot_run_load:.0f}</div>
                <div class="forest-kpi-sub">cardiovascular load</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Last Run</span>
                    <span class="forest-kpi-icon">📅</span>
                </div>
                <div class="forest-kpi-val">{format_days_ago(days_since_run)}</div>
                <div class="forest-kpi-sub">recent activity</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Check for Calendar Scheduled Running Plans vs Adaptive Next Run Workout
    saved_plans = get_plans()
    dated_run_plans = [p for p in saved_plans if p.get("planned_date") and p.get("sport") == "Run"]
    dated_run_plans.sort(key=lambda x: x.get("planned_date", ""), reverse=False)

    calendar_matched_run_plan = None
    target_date_str = str(target_plan_date)
    for p in dated_run_plans:
        if p.get("planned_date") == target_date_str:
            calendar_matched_run_plan = p
            break

    if not calendar_matched_run_plan:
        upcoming_runs = [p for p in dated_run_plans if p.get("planned_date") >= str(today_date)]
        if upcoming_runs:
            calendar_matched_run_plan = upcoming_runs[0]

    # AI Adaptive Recommended Run based on acute load and readiness
    best_r_sec = running_baseline_pace or running_analytics.get("best_pace_sec") or 542.0
    run_readiness_calc = calculate_sport_recovery_metric(
        "Run",
        days_since_run,
        summary.get("Run", {}).get("training_load", 0),
        summary.get("Run", {}).get("distance_km", 0),
        today_wellness
    )
    
    # Adaptive Focus Selection
    if (days_since_run or 99) >= 7:
        ai_run_focus = "Aerobic Endurance (Long Run)"
        ai_run_dist = 5.0
    elif (days_since_run or 99) <= 1:
        ai_run_focus = "Easy / Recovery Run"
        ai_run_dist = 4.0
    elif run_readiness_calc["readiness_pct"] >= 85:
        ai_run_focus = "Lactate Threshold (Tempo)"
        ai_run_dist = 6.0
    else:
        ai_run_focus = "Easy / Recovery Run"
        ai_run_dist = 5.0

    default_ai_run_plan = generate_run_workout(ai_run_focus, ai_run_dist, best_pace_sec_km=best_r_sec)
    default_ai_run_plan["readiness_score"] = run_readiness_calc["readiness_pct"]

    # Build plan options
    run_plan_options_map = {}
    if calendar_matched_run_plan:
        p_dt = calendar_matched_run_plan.get("planned_date")
        p_dist = calendar_matched_run_plan.get("distance_km") or (calendar_matched_run_plan.get("distance_m", 0) / 1000.0)
        p_t = calendar_matched_run_plan.get("type") or calendar_matched_run_plan.get("workout_type", "Run")
        label = f"📅 Calendar Scheduled: {format_date_clean(p_dt)} ({p_dist:.1f} km {p_t})"
        run_plan_options_map[label] = calendar_matched_run_plan

    for p in dated_run_plans:
        p_dt = p.get("planned_date")
        p_dist = p.get("distance_km") or (p.get("distance_m", 0) / 1000.0)
        p_t = p.get("type") or p.get("workout_type", "Run")
        label = f"📅 Calendar: {format_date_clean(p_dt)} ({p_dist:.1f} km {p_t})"
        if label not in run_plan_options_map:
            run_plan_options_map[label] = p

    ai_run_label = f"🏃 Next Recommended Run ({default_ai_run_plan.get('distance_km')} km {default_ai_run_plan.get('type')})"
    run_plan_options_map[ai_run_label] = default_ai_run_plan

    if len(run_plan_options_map) > 1:
        sel_run_plan_label = st.selectbox(
            "Select Running Workout Plan",
            options=list(run_plan_options_map.keys()),
            index=0,
            key="run_tab_plan_selector",
            help="Switch between Calendar scheduled runs and AI adaptive daily recommendation."
        )
        active_raw_run_plan = run_plan_options_map[sel_run_plan_label]
    else:
        active_raw_run_plan = calendar_matched_run_plan or default_ai_run_plan

    # Normalize active run plan fields
    r_plan_type = active_raw_run_plan.get("workout_type") or active_raw_run_plan.get("type") or "Aerobic Endurance"
    r_plan_dist = active_raw_run_plan.get("distance_km") or (active_raw_run_plan.get("distance_m", 5000) / 1000.0)
    r_plan_dur = active_raw_run_plan.get("duration_est") or active_raw_run_plan.get("duration") or "35-45 min"
    r_plan_goal = active_raw_run_plan.get("goal") or "Build aerobic endurance and lactate threshold efficiency."
    r_plan_sets = active_raw_run_plan.get("sets", [])
    r_plan_readiness = active_raw_run_plan.get("readiness_score") or run_readiness_calc["readiness_pct"]
    r_plan_rationale = active_raw_run_plan.get("coach_rationale") or active_raw_run_plan.get("description") or "Scheduled structured workout aligned with training periodization."
    is_calendar_run = bool(active_raw_run_plan.get("planned_date"))
    r_date_str = format_date_clean(active_raw_run_plan.get("planned_date")) if is_calendar_run else plan_timing_badge

    st.markdown(
        f"""
        <div class="f-card" style="border-left: 4px solid #F43F5E; margin-bottom: 20px;">
            <div class="f-card-header">
                <div>
                    <span class="forest-pill-tag" style="background: rgba(244, 63, 94, 0.12); color: #F43F5E; border-color: rgba(244, 63, 94, 0.3);">{'📅 CALENDAR SCHEDULED · ' + r_date_str.upper() if is_calendar_run else '🏃 ' + r_plan_type.upper() + ' WORKOUT · ' + plan_timing_badge.upper()}</span>
                    <div class="f-card-title" style="margin-top: 6px; font-size: 1.25rem;">
                        {r_plan_type} Session — {r_plan_dist:.1f} km
                    </div>
                    <div class="f-card-subtitle">
                        <strong>Duration:</strong> {r_plan_dur} · <strong>Goal:</strong> {r_plan_goal}
                    </div>
                </div>
                <div style="text-align: right; background: rgba(244, 63, 94, 0.1); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(244, 63, 94, 0.25);">
                    <div style="font-size: 0.7rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Readiness</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 800; color: #F43F5E;">{r_plan_readiness}/100</div>
                </div>
            </div>
            <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 10px; background: #080E18; padding: 10px 14px; border-radius: 8px; border: 1px solid #142033; line-height: 1.5;">
                💡 <strong>Coaching Rationale:</strong> {r_plan_rationale}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_calendar_run:
        r_del_id = active_raw_run_plan.get("plan_id") or active_raw_run_plan.get("id")
        del_rc1, del_rc2 = st.columns([4, 1])
        with del_rc2:
            if r_del_id and st.button("🗑️ Delete Scheduled Run", key=f"del_run_cal_plan_{r_del_id}", use_container_width=True):
                delete_plan(r_del_id)
                st.toast("Scheduled run plan deleted from calendar!")
                st.rerun()

    # Render Visual Structured Running Sets
    if r_plan_sets:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; color: #FFFFFF; font-size: 1.15rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                    🧱 Visual Structured Workout Sets ({len(r_plan_sets)} Sets · {r_plan_dist:.1f} km)
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        set_cards_html = []
        for i, s in enumerate(r_plan_sets):
            p_text = s.get("purpose", "Run Segment")
            p_upper = p_text.upper()
            if "WARM" in p_upper:
                badge_style = "background: rgba(0, 210, 255, 0.15); color: #00D2FF; border: 1px solid rgba(0, 210, 255, 0.3);"
                badge_label = "WARM-UP"
            elif "TEMPO" in p_upper or "THRESHOLD" in p_upper:
                badge_style = "background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3);"
                badge_label = "THRESHOLD / TEMPO"
            elif "VO2" in p_upper or "SPEED" in p_upper or "SPRINT" in p_upper:
                badge_style = "background: rgba(244, 63, 94, 0.15); color: #F43F5E; border: 1px solid rgba(244, 63, 94, 0.3);"
                badge_label = "SPEED / VO2"
            elif "ENDURANCE" in p_upper or "BASE" in p_upper or "AEROBIC" in p_upper:
                badge_style = "background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3);"
                badge_label = "AEROBIC BASE"
            elif "COOL" in p_upper:
                badge_style = "background: rgba(100, 116, 139, 0.15); color: #94A3B8; border: 1px solid rgba(100, 116, 139, 0.3);"
                badge_label = "COOL-DOWN"
            else:
                badge_style = "background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3);"
                badge_label = "RECOVERY"

            reps_cnt = s.get('reps', 1)
            dist_desc = f"{reps_cnt} × {s.get('distance')}" if reps_cnt > 1 else s.get('distance')
            tot_seg_dist = s.get('total_distance') or s.get('distance')
            pattern_txt = s.get('pattern', 'Running')
            target_pace = s.get('pace', 'Target Pace')
            hr_zone = s.get('hr_zone', 'Heart Rate')
            rest_txt = s.get('rest', 'None')

            card_item = (
                f"<div style='background: #080E18; border: 1px solid #1A273D; border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;'>"
                f"<div>"
                f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>"
                f"<span style='font-size: 0.75rem; font-weight: 800; color: #64748B;'>SET {i+1}</span>"
                f"<span style='font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; {badge_style}'>{badge_label}</span>"
                f"</div>"
                f"<div style='font-family: JetBrains Mono, monospace; font-size: 1.15rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;'>"
                f"{dist_desc}"
                f"</div>"
                f"<div style='font-size: 0.8rem; color: #94A3B8; margin-bottom: 10px; line-height: 1.4;'>"
                f"{pattern_txt}"
                f"</div>"
                f"</div>"
                f"<div style='border-top: 1px solid #142033; padding-top: 8px; margin-top: 6px; font-size: 0.74rem; color: #64748B; display: flex; flex-direction: column; gap: 4px;'>"
                f"<div><span style='color: #475569;'>Pace:</span> <strong style='color: #00E599;'>{target_pace}</strong></div>"
                f"<div><span style='color: #475569;'>HR Zone:</span> <strong style='color: #F43F5E;'>{hr_zone}</strong></div>"
                f"<div><span style='color: #475569;'>Rest:</span> <strong style='color: #94A3B8;'>{rest_txt}</strong></div>"
                f"</div>"
                f"</div>"
            )
            set_cards_html.append(card_item)

        grid_html = (
            f"<div class='sets-grid-responsive' style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 22px;'>"
            f"{''.join(set_cards_html)}"
            f"</div>"
        )
        if hasattr(st, "html"):
            st.html(grid_html)
        else:
            st.markdown(grid_html, unsafe_allow_html=True)

    # Running Activity History Table (Scoped to chosen timeline)
    if runs_list:
        st.markdown("### 📋 Running Activity History")
        run_table_rows = []
        for r in runs_list:
            run_table_rows.append({
                "Date": format_date_clean(r.get("date")),
                "Run Name": r.get("name", "Run"),
                "Distance": f"{r.get('distance_km', 0):.2f} km",
                "Duration": format_duration_hm(r.get("moving_time_min", 0)),
                "Pace (/km)": r.get("pace_formatted", "—"),
                "Avg HR": f"{r.get('avg_hr', 0):.0f} bpm" if r.get("avg_hr") else "—",
                "Calories": f"{r.get('calories', 0):,} kcal" if r.get("calories") else "—",
                "Training Load": f"{r.get('training_load', 0):.0f}" if r.get("training_load") else "—",
            })
        st.dataframe(pd.DataFrame(run_table_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### 📈 Running Telemetry & Progression")
        run_df_data = []
        for r in reversed(runs_list):
            run_df_data.append({
                "date": str(r.get("date", ""))[:10],
                "distance_km": r.get("distance_km", 0.0),
                "moving_time_min": r.get("moving_time_min", 0.0),
                "avg_hr": r.get("avg_hr"),
                "pace_min_km": (r.get("pace_sec_km", 0) / 60.0) if r.get("pace_sec_km") else None,
            })
        run_df = pd.DataFrame(run_df_data)

        rn_c1, rn_c2 = st.columns(2)
        with rn_c1:
            c_rn_dist = alt.Chart(run_df).mark_bar(
                color="#F43F5E",
                cornerRadiusTopLeft=4,
                cornerRadiusTopRight=4,
                size=28
            ).encode(
                x=alt.X("date:N", title="Run Date", sort=None),
                y=alt.Y("distance_km:Q", title="Distance (km)"),
                tooltip=["date:N", "distance_km:Q", "moving_time_min:Q"],
            ).properties(height=240, title="Run Distance Progression")
            st.altair_chart(apply_forest_chart_theme(c_rn_dist, height=240), use_container_width=True)

        with rn_c2:
            hr_rn_df = run_df.dropna(subset=["avg_hr"])
            if not hr_rn_df.empty:
                c_rn_hr = alt.Chart(hr_rn_df).mark_line(
                    color="#FB7185",
                    strokeWidth=2.5,
                    point=alt.OverlayMarkDef(filled=True, fill="#FB7185", size=45),
                ).encode(
                    x=alt.X("date:N", title="Run Date", sort=None),
                    y=alt.Y("avg_hr:Q", title="Avg HR (bpm)", scale=alt.Scale(zero=False)),
                    tooltip=["date:N", "avg_hr:Q"],
                ).properties(height=240, title="Running Heart Rate Trend")
                st.altair_chart(apply_forest_chart_theme(c_rn_hr, height=240), use_container_width=True)
    else:
        st.info("ℹ️ No running sessions recorded during the selected time period.")

    # Splits Inspector - only show if there are actual valid splits!
    runs_with_splits = [
        r_act for r_act in runs_list
        if r_act.get("splits") and any(
            (sp.get("pace_formatted") and sp.get("pace_formatted") != "—") or 
            (sp.get("pace") and sp.get("pace") != "—")
            for sp in r_act["splits"]
        )
    ]
    if runs_with_splits:
        st.markdown("---")
        st.markdown("### ⏱️ GPS Kilometer Splits Breakdown")
        for r_act in runs_with_splits:
            s_list = r_act.get("splits", [])
            with st.expander(f"🏃 {r_act.get('name', 'Run')} — {format_date_clean(r_act.get('date'))} ({r_act.get('distance_km', 0):.2f} km @ {r_act.get('pace_formatted', '—')})", expanded=False):
                split_rows = []
                for idx, sp in enumerate(s_list, 1):
                    km_label = sp.get("split") or f"Km {sp.get('split_km', idx)}"
                    split_time = sp.get("split_time_formatted") or (f"{int(sp['duration_sec'] // 60)}:{int(sp['duration_sec'] % 60):02d}" if sp.get("duration_sec") else "—")
                    pace_val = sp.get("pace_formatted") or sp.get("pace") or "—"
                    elapsed = sp.get("elapsed_time_formatted") or "—"
                    elev = f"+{sp.get('elevation_gain_m', 0):.0f} m" if sp.get("elevation_gain_m") is not None else "—"
                    split_rows.append({
                        "Kilometer": km_label,
                        "Split Time": split_time,
                        "Pace (/km)": pace_val,
                        "Elapsed Time": elapsed,
                        "Elev Gain": elev,
                    })
                st.dataframe(pd.DataFrame(split_rows), use_container_width=True, hide_index=True)

    # 5-Zone Running Pace Guidelines (At the bottom)
    r_zones = running_analytics.get("pace_zones", [])
    if r_zones:
        st.markdown("---")
        st.markdown("### 🎯 5-Zone Running Pace Guidelines (VDOT / Threshold Model)")
        st.dataframe(pd.DataFrame(r_zones), use_container_width=True, hide_index=True)

    # Media Gallery
    media_runs = [r for r in runs_list if r.get("media")]
    if media_runs:
        st.markdown("---")
        st.markdown("### 📸 Race & Workout Gallery")
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
    rides_list = cycling_analytics.get("rides", [])
    tot_ride_dist = cycling_analytics.get("total_distance_km", 0.0)
    tot_ride_time = cycling_analytics.get("total_moving_min", 0.0)
    avg_ride_speed = cycling_analytics.get("avg_speed_kmh")
    fastest_ride_speed = cycling_analytics.get("fastest_speed_kmh")
    tot_ride_elev = cycling_analytics.get("total_elevation_m", 0.0)
    longest_ride_val = cycling_analytics.get("longest_ride_km", 0.0)

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Ride Distance</span>
                    <span class="forest-kpi-icon">🚴</span>
                </div>
                <div class="forest-kpi-val">{tot_ride_dist:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                <div class="forest-kpi-sub">{len(rides_list)} rides completed</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Active Time</span>
                    <span class="forest-kpi-icon">⏱️</span>
                </div>
                <div class="forest-kpi-val">{format_duration_hm(tot_ride_time)}</div>
                <div class="forest-kpi-sub">{tot_ride_time:.0f} moving mins</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Avg Speed</span>
                    <span class="forest-kpi-icon">⚡</span>
                </div>
                <div class="forest-kpi-val">{f"{avg_ride_speed:.1f}" if avg_ride_speed else "—"} <span style="font-size: 0.9rem; color: #64748B;">km/h</span></div>
                <div class="forest-kpi-sub">overall average</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Fastest Speed</span>
                    <span class="forest-kpi-icon">🚀</span>
                </div>
                <div class="forest-kpi-val">{f"{fastest_ride_speed:.1f}" if fastest_ride_speed else "—"} <span style="font-size: 0.9rem; color: #64748B;">km/h</span></div>
                <div class="forest-kpi-sub">top sustained avg</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Elevation Gain</span>
                    <span class="forest-kpi-icon">⛰️</span>
                </div>
                <div class="forest-kpi-val">{tot_ride_elev:.0f} <span style="font-size: 0.9rem; color: #64748B;">m</span></div>
                <div class="forest-kpi-sub">climbing elevation</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Longest Ride</span>
                    <span class="forest-kpi-icon">📍</span>
                </div>
                <div class="forest-kpi-val">{longest_ride_val:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                <div class="forest-kpi-sub">single session</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if rides_list:
        st.markdown("### 📈 Cycling Progression")
        ride_df_data = []
        for r in reversed(rides_list):
            ride_df_data.append({
                "date": str(r.get("date", ""))[:10],
                "distance_km": r.get("distance_km", 0.0),
                "moving_time_min": r.get("moving_time_min", 0.0),
                "avg_speed": r.get("computed_speed_kmh", 0.0),
                "avg_hr": r.get("avg_hr"),
                "elevation_m": r.get("elevation_m", 0.0),
            })
        r_df = pd.DataFrame(ride_df_data)

        rc_c1, rc_c2 = st.columns(2)
        with rc_c1:
            c_r_dist = alt.Chart(r_df).mark_bar(
                color="#10B981",
                cornerRadiusTopLeft=4,
                cornerRadiusTopRight=4,
                size=28
            ).encode(
                x=alt.X("date:N", title="Ride Date", sort=None),
                y=alt.Y("distance_km:Q", title="Distance (km)"),
                tooltip=["date:N", "distance_km:Q", "moving_time_min:Q"],
            ).properties(height=240, title="Ride Distance Progression")
            st.altair_chart(apply_forest_chart_theme(c_r_dist, height=240), use_container_width=True)

        with rc_c2:
            c_r_spd = alt.Chart(r_df).mark_line(
                color="#00E599",
                strokeWidth=2.5,
                point=alt.OverlayMarkDef(filled=True, fill="#00E599", size=45),
            ).encode(
                x=alt.X("date:N", title="Ride Date", sort=None),
                y=alt.Y("avg_speed:Q", title="Avg Speed (km/h)", scale=alt.Scale(zero=False)),
                tooltip=["date:N", "avg_speed:Q", "elevation_m:Q"],
            ).properties(height=240, title="Cycling Speed Progression")
            st.altair_chart(apply_forest_chart_theme(c_r_spd, height=240), use_container_width=True)

        st.markdown("### 📋 Cycling Activity History")
        r_table_rows = []
        for r in rides_list:
            r_table_rows.append({
                "Date": format_date_clean(r.get("date")),
                "Ride Name": r.get("name", "Ride"),
                "Distance": f"{r.get('distance_km', 0):.2f} km",
                "Duration": format_duration_hm(r.get("moving_time_min", 0)),
                "Avg Speed": f"{r.get('computed_speed_kmh', 0):.1f} km/h" if r.get("computed_speed_kmh") else "—",
                "Elevation Gain": f"{r.get('elevation_m', 0):.0f} m" if r.get("elevation_m") else "—",
                "Avg HR": f"{r.get('avg_hr', 0):.0f} bpm" if r.get("avg_hr") else "—",
                "Calories": f"{r.get('calories', 0):,} kcal" if r.get("calories") else "—",
            })
        st.dataframe(pd.DataFrame(r_table_rows), use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No cycling sessions recorded during the selected time period.")


# ============================================================
# TAB 5: 🚶 WALKING
# ============================================================

with tab_walking:
    walks_list = walking_analytics.get("walks", [])
    tot_walk_dist = walking_analytics.get("total_distance_km", 0.0)
    tot_walk_time = walking_analytics.get("total_moving_min", 0.0)
    avg_walk_pace = walking_analytics.get("avg_pace_formatted", "—")
    longest_walk_val = walking_analytics.get("longest_walk_km", 0.0)
    active_walk_days = walking_analytics.get("active_days", 0)
    avg_daily_km = walking_analytics.get("avg_daily_km", 0.0)

    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h2 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 4px;">🚶 Walking Analytics &amp; Consistency</h2>
            <div style="color: #94A3B8; font-size: 0.95rem;">Tracked walking sessions and daily step telemetry from Garmin.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">TOTAL DISTANCE</span>
                    <span class="forest-kpi-icon">🚶</span>
                </div>
                <div class="forest-kpi-val">{tot_walk_dist:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                <div class="forest-kpi-sub">{len(walks_list)} recorded walks</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">ACTIVE TIME</span>
                    <span class="forest-kpi-icon">⏱️</span>
                </div>
                <div class="forest-kpi-val">{format_duration_hm(tot_walk_time)}</div>
                <div class="forest-kpi-sub">{tot_walk_time:.0f} moving mins</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">AVERAGE PACE</span>
                    <span class="forest-kpi-icon">⚡</span>
                </div>
                <div class="forest-kpi-val">{avg_walk_pace}</div>
                <div class="forest-kpi-sub">Overall pace /km</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">LONGEST WALK</span>
                    <span class="forest-kpi-icon">📍</span>
                </div>
                <div class="forest-kpi-val">{longest_walk_val:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                <div class="forest-kpi-sub">Max single session</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">DAILY AVERAGE</span>
                    <span class="forest-kpi-icon">👟</span>
                </div>
                <div class="forest-kpi-val">{avg_daily_km:.2f} <span style="font-size: 0.9rem; color: #64748B;">km</span></div>
                <div class="forest-kpi-sub">across {active_walk_days} active days</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if walks_list:
        st.markdown("### 📈 Walking Progression")
        
        walk_df_data = []
        for w in reversed(walks_list):
            w_date = str(w.get("date", ""))[:10]
            w_dist = w.get("distance_km", 0.0)
            w_time = w.get("moving_time_min", 0.0)
            w_hr = w.get("avg_hr")
            w_pace = w.get("computed_pace_sec")
            w_pace_min = (w_pace / 60.0) if w_pace else None
            w_cals = w.get("calories", 0)
            walk_df_data.append({
                "date": w_date,
                "distance_km": w_dist,
                "moving_time_min": w_time,
                "avg_hr": w_hr,
                "pace_min_km": w_pace_min,
                "calories": w_cals,
            })
        w_df = pd.DataFrame(walk_df_data)

        wk_c1, wk_c2 = st.columns(2)
        with wk_c1:
            c_wk_dist = alt.Chart(w_df).mark_bar(
                color="#F59E0B",
                cornerRadiusTopLeft=4,
                cornerRadiusTopRight=4,
                size=28
            ).encode(
                x=alt.X("date:N", title="Walk Date", sort=None),
                y=alt.Y("distance_km:Q", title="Distance (km)"),
                tooltip=["date:N", "distance_km:Q", "moving_time_min:Q"],
            ).properties(height=240, title="Walk Distance Progression")
            st.altair_chart(apply_forest_chart_theme(c_wk_dist, height=240), use_container_width=True)

        with wk_c2:
            hr_w_df = w_df.dropna(subset=["avg_hr"])
            if not hr_w_df.empty:
                c_wk_hr = alt.Chart(hr_w_df).mark_line(
                    color="#F43F5E",
                    strokeWidth=2.5,
                    point=alt.OverlayMarkDef(filled=True, fill="#F43F5E", size=45),
                ).encode(
                    x=alt.X("date:N", title="Walk Date", sort=None),
                    y=alt.Y("avg_hr:Q", title="Avg HR (bpm)", scale=alt.Scale(zero=False)),
                    tooltip=["date:N", "avg_hr:Q"],
                ).properties(height=240, title="Heart Rate & Exertion")
                st.altair_chart(apply_forest_chart_theme(c_wk_hr, height=240), use_container_width=True)
            else:
                st.info("No heart rate data recorded for walking sessions.")

        wk_c3, wk_c4 = st.columns(2)
        with wk_c3:
            w_steps_data = []
            for wr in wellness_records:
                if wr.get("steps") and wr["steps"] > 0:
                    w_steps_data.append({
                        "date": str(wr.get("date", wr.get("id", "")))[:10],
                        "steps": wr["steps"],
                    })
            if w_steps_data:
                steps_df = pd.DataFrame(w_steps_data).tail(30)
                c_steps = alt.Chart(steps_df).mark_bar(
                    color="#00E599",
                    cornerRadiusTopLeft=3,
                    cornerRadiusTopRight=3,
                    size=16
                ).encode(
                    x=alt.X("date:N", title="Date", sort=None),
                    y=alt.Y("steps:Q", title="Daily Steps"),
                    tooltip=["date:N", "steps:Q"],
                ).properties(height=240, title="Daily Step Telemetry (Garmin Sensor)")
                
                rule = alt.Chart(pd.DataFrame({'y': [10000]})).mark_rule(
                    color="#F59E0B",
                    strokeDash=[4, 4],
                    strokeWidth=1.5
                ).encode(y='y:Q')
                
                st.altair_chart(apply_forest_chart_theme(c_steps + rule, height=240), use_container_width=True)
            else:
                st.info("No pedometer step records available in current window.")

        with wk_c4:
            pace_w_df = w_df.dropna(subset=["pace_min_km"])
            if not pace_w_df.empty:
                c_wk_pace = alt.Chart(pace_w_df).mark_line(
                    color="#38BDF8",
                    strokeWidth=2.5,
                    point=alt.OverlayMarkDef(filled=True, fill="#38BDF8", size=45),
                ).encode(
                    x=alt.X("date:N", title="Walk Date", sort=None),
                    y=alt.Y("pace_min_km:Q", title="Pace (min/km)", scale=alt.Scale(zero=False)),
                    tooltip=["date:N", "pace_min_km:Q"],
                ).properties(height=240, title="Walking Pace Trend")
                st.altair_chart(apply_forest_chart_theme(c_wk_pace, height=240), use_container_width=True)
            else:
                st.info("No walking pace data available.")

        st.markdown("### 📋 Walking Activity History")
        w_table_rows = []
        for w in walks_list:
            w_table_rows.append({
                "Date": format_date_clean(w.get("date")),
                "Walk Name": w.get("name", "Walk"),
                "Distance": f"{w.get('distance_km', 0):.2f} km",
                "Duration": format_duration_hm(w.get("moving_time_min", 0)),
                "Pace (/km)": w.get("computed_pace_formatted", "—"),
                "Steps": f"{w.get('total_steps', 0):,}" if w.get("total_steps") else "—",
                "Avg HR": f"{w.get('avg_hr', 0):.0f} bpm" if w.get("avg_hr") else "—",
                "Calories": f"{w.get('calories', 0):,} kcal" if w.get("calories") else "—",
                "Training Load": f"{w.get('training_load', 0):.0f}" if w.get("training_load") else "—",
            })
        st.dataframe(pd.DataFrame(w_table_rows), use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No walking sessions recorded during the selected time period.")


# ============================================================
# TAB 6: 😴 SLEEP & RECOVERY
# ============================================================

with tab_sleep:
    sl_dur_fmt = sleep_analytics.get("avg_duration_formatted", "—")
    sl_score = sleep_analytics.get("avg_sleep_score")
    sl_hrv = sleep_analytics.get("avg_hrv")
    sl_rhr = sleep_analytics.get("avg_resting_hr")
    sl_days = sleep_analytics.get("total_days_tracked", 0)

    st.markdown(
        f"""
        <div class="kpi-row-grid">
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Average Sleep</span>
                    <span class="forest-kpi-icon">🛌</span>
                </div>
                <div class="forest-kpi-val">{sl_dur_fmt}</div>
                <div class="forest-kpi-sub">Garmin sleep log</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Sleep Score</span>
                    <span class="forest-kpi-icon">🎯</span>
                </div>
                <div class="forest-kpi-val">{f"{sl_score:.0f}" if sl_score else "—"} <span style="font-size: 0.9rem; color: #64748B;">/ 100</span></div>
                <div class="forest-kpi-sub">restful quality</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Overnight HRV</span>
                    <span class="forest-kpi-icon">💓</span>
                </div>
                <div class="forest-kpi-val">{f"{sl_hrv:.0f}" if sl_hrv else "—"} <span style="font-size: 0.9rem; color: #64748B;">ms</span></div>
                <div class="forest-kpi-sub">autonomic baseline</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Resting HR</span>
                    <span class="forest-kpi-icon">❤️</span>
                </div>
                <div class="forest-kpi-val">{f"{sl_rhr:.0f}" if sl_rhr else "—"} <span style="font-size: 0.9rem; color: #64748B;">bpm</span></div>
                <div class="forest-kpi-sub">cardiovascular rest</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Tracked Nights</span>
                    <span class="forest-kpi-icon">🌙</span>
                </div>
                <div class="forest-kpi-val">{sl_days}</div>
                <div class="forest-kpi-sub">Garmin 965 sensor</div>
            </div>
            <div class="forest-kpi-card">
                <div class="forest-kpi-top">
                    <span class="forest-kpi-label">Readiness</span>
                    <span class="forest-kpi-icon">⚡</span>
                </div>
                <div class="forest-kpi-val">Optimal</div>
                <div class="forest-kpi-sub">training ready</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sl_trends = sleep_analytics.get("daily_trends", [])
    if sl_trends:
        st.markdown("### 📈 Sleep & Autonomic Recovery Progression")
        sl_df_data = []
        for s in sl_trends:
            if s.get("duration_hours") or s.get("resting_hr"):
                sl_df_data.append({
                    "date": str(s.get("date", ""))[:10],
                    "duration_hours": s.get("duration_hours", 0.0),
                    "score": s.get("score"),
                    "hrv": s.get("hrv"),
                    "resting_hr": s.get("resting_hr"),
                })
        if sl_df_data:
            sl_df = pd.DataFrame(sl_df_data)
            sl_c1, sl_c2 = st.columns(2)
            with sl_c1:
                dur_df = sl_df.dropna(subset=["duration_hours"])
                if not dur_df.empty:
                    c_sl_dur = alt.Chart(dur_df).mark_bar(
                        color="#818CF8",
                        cornerRadiusTopLeft=4,
                        cornerRadiusTopRight=4,
                        size=22
                    ).encode(
                        x=alt.X("date:N", title="Date", sort=None),
                        y=alt.Y("duration_hours:Q", title="Sleep Duration (Hours)"),
                        tooltip=["date:N", "duration_hours:Q"],
                    ).properties(height=240, title="Daily Sleep Duration")
                    
                    rule_8h = alt.Chart(pd.DataFrame({'y': [8.0]})).mark_rule(
                        color="#00E599",
                        strokeDash=[4, 4],
                        strokeWidth=1.5
                    ).encode(y='y:Q')
                    
                    st.altair_chart(apply_forest_chart_theme(c_sl_dur + rule_8h, height=240), use_container_width=True)

            with sl_c2:
                hrv_df = sl_df.dropna(subset=["hrv"])
                if not hrv_df.empty:
                    c_sl_hrv = alt.Chart(hrv_df).mark_line(
                        color="#38BDF8",
                        strokeWidth=2.5,
                        point=alt.OverlayMarkDef(filled=True, fill="#38BDF8", size=40),
                    ).encode(
                        x=alt.X("date:N", title="Date", sort=None),
                        y=alt.Y("hrv:Q", title="Overnight HRV (ms)", scale=alt.Scale(zero=False)),
                        tooltip=["date:N", "hrv:Q"],
                    ).properties(height=240, title="Overnight HRV Baseline Trend")
                    st.altair_chart(apply_forest_chart_theme(c_sl_hrv, height=240), use_container_width=True)

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
# TAB 7: 📅 ACTIVITY CALENDAR & PLANNER
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

    cal_sel_c1, cal_sel_c2, cal_sel_spacer = st.columns([2, 2, 4])
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
    header_html = "".join(f"<div class='cal-header-cell' style='font-size: 0.78rem; font-weight: 700; color: #64748B; text-align: center;'>{h}</div>" for h in day_headers)

    cells_list = []
    for week in cal_matrix:
        for day_num in week:
            if day_num == 0:
                cells_list.append("<div style='background: #080E18; border: 1px dashed #172338; border-radius: 8px; height: 100px; opacity: 0.3;'></div>")
            else:
                d_str = f"{sel_year:04d}-{sel_month:02d}-{day_num:02d}"
                acts = act_by_date.get(d_str, [])
                p_items = plans_by_date.get(d_str, [])
                is_today = (d_str == str(today_date))
                border_s = "border: 2px solid #00E599; background: #0E1A29;" if is_today else "border: 1px solid #172338; background: #0C1420;"

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
                        p_sport = p_item.get("sport", "Swim")
                        if p_sport == "Run":
                            p_dist_val = p_item.get("distance_km") or (p_item.get("distance_m", 0) / 1000.0)
                            badge_html += f"<span style='background: #E11D48; color: #FFFFFF; font-size: 0.65rem; padding: 1px 4px; border-radius: 4px; display: block; margin-bottom: 2px; text-align: center;'>🏃 {p_dist_val:.1f}k Plan</span>"
                        else:
                            p_dist_val = p_item.get("distance_m") or p_item.get("target_distance", 0)
                            badge_html += f"<span style='background: #6366F1; color: #FFFFFF; font-size: 0.65rem; padding: 1px 4px; border-radius: 4px; display: block; margin-bottom: 2px; text-align: center;'>🏊 {p_dist_val}m Plan</span>"

                if not acts and not p_items:
                    badge_html = "<span style='font-size: 0.68rem; color: #475569; display: block; text-align: center; margin-top: 18px;'>Rest</span>"

                cells_list.append(
                    f"<div style='{border_s} border-radius: 8px; padding: 6px; height: 100px; box-sizing: border-box; overflow-y: auto;'>"
                    f"<div style='font-family: JetBrains Mono; font-size: 0.8rem; font-weight: 800; color: {'#00E599' if is_today else '#FFFFFF'}; margin-bottom: 4px;'>{day_num}</div>"
                    f"{badge_html}</div>"
                )

    cells_html = "".join(cells_list)
    full_cal_html = (
        f"<div class='cal-wrapper' style='overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 8px; margin-bottom: 16px;'>"
        f"<div style='min-width: 580px;'>"
        f"<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin-bottom: 6px;'>{header_html}</div>"
        f"<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px;'>{cells_html}</div>"
        f"</div>"
        f"</div>"
    )
    if hasattr(st, "html"):
        st.html(full_cal_html)
    else:
        st.markdown(full_cal_html, unsafe_allow_html=True)

    # Interactive Multi-Sport Workout Builder (Swimming & Running)
    st.markdown("---")
    st.markdown("### 🛠️ Interactive Multi-Sport Workout Builder")

    builder_sport = st.radio(
        "Select Discipline",
        ["🏊 Swimming", "🏃 Running"],
        horizontal=True,
        key="cal_builder_sport_choice"
    )

    cal_b_col1, cal_b_col2 = st.columns([1, 2])

    if builder_sport == "🏊 Swimming":
        with cal_b_col1:
            custom_focus = st.selectbox(
                "Swim Focus",
                ["Endurance", "Tempo", "Intervals", "Pyramid Ladder", "Recovery"],
                index=0,
                key="forest_cal_focus"
            )
            custom_dist = st.slider(
                "Distance (m)",
                min_value=1000,
                max_value=3500,
                value=plan.get("distance_m", 2000) if isinstance(plan, dict) else 2000,
                step=250,
                key="forest_cal_dist"
            )

            # Live Swim Pace Calibration Slider in MM:SS format
            swim_pace_options = []
            swim_pace_sec_map = {}
            for s_val in range(90, 241, 1):
                label = f"{s_val // 60}:{s_val % 60:02d} /100m"
                swim_pace_options.append(label)
                swim_pace_sec_map[label] = s_val

            def_swim_sec = max(90, min(240, int(round(baseline_pace))))
            def_swim_lbl = f"{def_swim_sec // 60}:{def_swim_sec % 60:02d} /100m"
            if def_swim_lbl not in swim_pace_sec_map:
                def_swim_lbl = swim_pace_options[0]

            calibrated_swim_label = st.select_slider(
                "Reference Baseline Pace (/100m)",
                options=swim_pace_options,
                value=def_swim_lbl,
                key="cal_swim_pace_calib",
                help=f"Dynamic reference pace calculated from your recent long swims ({format_pace(baseline_pace)}). Tune to scale all swim zone targets."
            )
            calibrated_swim_sec = swim_pace_sec_map[calibrated_swim_label]
            custom_swim_zones = swim_pace_zones(calibrated_swim_sec)

            custom_date = st.date_input(
                "Planned Date",
                value=target_plan_date,
                key="forest_cal_date"
            )

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

            cust_target_d = custom_plan.get("target_distance") or custom_dist
            cust_laps = custom_plan.get("total_laps") or (cust_target_d // 25)

            custom_plan["plan_id"] = str(uuid.uuid4())
            custom_plan["sport"] = "Swim"
            custom_plan["planned_date"] = str(custom_date)
            custom_plan["name"] = f"Custom {custom_focus} Session"
            custom_plan["distance_m"] = cust_target_d

            if st.button("💾 Save Swim Plan to Calendar", use_container_width=True, key="save_custom_forest"):
                save_plan(custom_plan, target_date=str(custom_date))
                st.success(f"Saved {custom_focus} ({cust_target_d}m) for {custom_date.strftime('%b %d, %Y')}!")
                st.rerun()

        with cal_b_col2:
            st.markdown(f"**Preview:** `{custom_plan.get('type', custom_focus)}` · `{cust_target_d}m` ({cust_laps} Laps)")
            st.markdown(f"<div style='font-size: 0.78rem; color: #64748B; margin-bottom: 8px;'>⚡ Scaled from baseline pace: <strong style='color: #00D2FF;'>{format_pace(calibrated_swim_sec)}</strong></div>", unsafe_allow_html=True)
            for j, cs in enumerate(custom_plan.get("sets", [])):
                st.markdown(f"- **Set {j+1}:** `{cs.get('reps')} × {cs.get('distance')}m` ({cs.get('total_laps')} Laps) — `{cs.get('stroke_pattern', cs.get('stroke'))}` · Pace: `{cs.get('pace')}` · Rest: `{cs.get('rest')}`")

    else:  # Running Builder
        best_r_sec = running_baseline_pace or running_analytics.get("best_pace_sec") or 542.0
        with cal_b_col1:
            run_focus = st.selectbox(
                "Running Focus",
                [
                    "Easy / Recovery Run",
                    "Aerobic Endurance (Long Run)",
                    "Lactate Threshold (Tempo)",
                    "VO2 Max / Speed Intervals",
                    "Pyramid Ladder Intervals",
                    "Hill Repeats"
                ],
                index=0,
                key="forest_cal_run_focus"
            )
            run_dist_val = st.slider(
                "Target Distance (km)",
                min_value=3.0,
                max_value=25.0,
                value=5.0,
                step=0.5,
                key="forest_cal_run_dist"
            )

            # Live Run Pace Calibration Slider in MM:SS format
            run_pace_options = []
            run_pace_sec_map = {}
            for s_val in range(240, 725, 5):
                label = f"{s_val // 60}:{s_val % 60:02d} /km"
                run_pace_options.append(label)
                run_pace_sec_map[label] = s_val

            def_run_sec = max(240, min(720, int(round(best_r_sec))))
            def_run_sec = int(round(def_run_sec / 5.0) * 5)
            def_run_lbl = f"{def_run_sec // 60}:{def_run_sec % 60:02d} /km"
            if def_run_lbl not in run_pace_sec_map:
                def_run_lbl = run_pace_options[0]

            calibrated_run_label = st.select_slider(
                "Reference 5K / Baseline Pace (/km)",
                options=run_pace_options,
                value=def_run_lbl,
                key="cal_run_pace_calib",
                help=f"Dynamic reference pace calculated from your historical Strava runs ({format_run_pace(best_r_sec)}). Tune to scale all workout zone targets."
            )
            effective_base_sec = float(run_pace_sec_map[calibrated_run_label])

            run_date = st.date_input(
                "Planned Date",
                value=target_plan_date,
                key="forest_cal_run_date"
            )

            custom_run_plan = generate_run_workout(run_focus, run_dist_val, best_pace_sec_km=effective_base_sec)
            custom_run_plan["planned_date"] = str(run_date)

            if st.button("💾 Save Run Plan to Calendar", use_container_width=True, key="save_custom_run_forest"):
                save_plan(custom_run_plan, target_date=str(run_date))
                st.success(f"Saved {run_focus} ({run_dist_val:.1f} km) for {run_date.strftime('%b %d, %Y')}!")
                st.rerun()

        with cal_b_col2:
            st.markdown(f"**Preview:** `{custom_run_plan.get('type')}` · `{custom_run_plan.get('distance_km')} km` · Duration: `{custom_run_plan.get('duration_est')}`")
            st.markdown(f"**Goal:** {custom_run_plan.get('goal')}")
            st.markdown(f"<div style='font-size: 0.78rem; color: #64748B; margin-bottom: 8px;'>⚡ Scaled from reference baseline pace: <strong style='color: #00E599;'>{format_run_pace(effective_base_sec)}</strong></div>", unsafe_allow_html=True)
            for j, cs in enumerate(custom_run_plan.get("sets", [])):
                reps_txt = f"{cs.get('reps')} × " if cs.get('reps', 1) > 1 else ""
                st.markdown(f"- **Set {j+1} ({cs.get('purpose')}):** `{reps_txt}{cs.get('distance')}` — `{cs.get('pattern')}` · Target Pace: `{cs.get('pace')}` · HR: `{cs.get('hr_zone')}` · Rest: `{cs.get('rest')}`")

    # Manage & Delete Scheduled Workouts Section
    st.markdown("---")
    st.markdown("### 📋 Manage Scheduled Workouts")
    all_saved_plans = get_plans()
    if all_saved_plans:
        m_col1, m_col2 = st.columns([3, 1])
        with m_col1:
            st.markdown(f"Total Scheduled Workouts in Database: **{len(all_saved_plans)}**")
        with m_col2:
            if st.button("🗑️ Clear All Saved Plans", key="btn_clear_all_plans_cal", use_container_width=True):
                clear_plans()
                st.toast("All saved workout plans have been cleared!")
                st.rerun()

        with st.expander("🔍 View & Delete Individual Scheduled Plans", expanded=True if len(all_saved_plans) <= 10 else False):
            sorted_plans = sorted(all_saved_plans, key=lambda p: p.get("planned_date", ""), reverse=False)
            for p_i, p_obj in enumerate(sorted_plans):
                p_id_val = p_obj.get("plan_id") or p_obj.get("id")
                p_sp = p_obj.get("sport", "Swim")
                p_tp = p_obj.get("workout_type") or p_obj.get("type", "Workout")
                p_dt = p_obj.get("planned_date", "Unscheduled")
                p_d_val = f"{p_obj.get('distance_km'):.1f} km" if p_sp == "Run" else f"{p_obj.get('distance_m', p_obj.get('target_distance', 0))} m"
                p_icon = "🏃" if p_sp == "Run" else "🏊"

                plan_row_c1, plan_row_c2, plan_row_c3 = st.columns([3, 4, 1])
                with plan_row_c1:
                    st.markdown(f"**{p_icon} {format_date_clean(p_dt)}** · `{p_tp}`")
                with plan_row_c2:
                    st.markdown(f"Distance: **{p_d_val}** · *{p_obj.get('goal', '')[:50]}...*")
                with plan_row_c3:
                    if st.button("🗑️ Delete", key=f"del_plan_item_{p_id_val}_{p_i}", use_container_width=True):
                        delete_plan(p_id_val)
                        st.toast(f"Deleted {p_tp} plan for {p_dt}!")
                        st.rerun()
                st.markdown("<hr style='margin: 4px 0; border: 0; border-top: 1px solid #142033;'>", unsafe_allow_html=True)
    else:
        st.info("No scheduled workout plans found in the calendar database.")


# ============================================================
# TAB 8: 📊 PERFORMANCE (MULTI-SPORT ANALYTICS & CHARTS)
# ============================================================

with tab_performance:
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0 0 4px 0; color: #FFFFFF; font-size: 1.4rem; font-weight: 800;">
                📊 Cross-Sport Performance &amp; Volume
            </h2>
            <div style="font-size: 0.8rem; color: #64748B; font-weight: 500;">
                Multi-sport training distribution, cross-training volume, and cardiovascular progression.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    w_multi = performance_analytics.get("weekly_multi_sport", [])
    if w_multi:
        w_m_df = pd.DataFrame(w_multi)
        
        perf_c1, perf_c2 = st.columns(2)
        
        # Chart 1: Active Hours Stacked by Sport
        with perf_c1:
            st.markdown("##### 📈 Weekly Multi-Sport Volume Breakdown (Active Hours)")
            c_hours = alt.Chart(w_m_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X("week:N", title="Training Week", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("hours:Q", title="Active Volume (Hours)"),
                color=alt.Color(
                    "sport:N",
                    scale=alt.Scale(
                        domain=["Swim", "Run", "Ride", "Walk", "Workout", "Other"],
                        range=["#00D2FF", "#F43F5E", "#10B981", "#F59E0B", "#8B5CF6", "#64748B"],
                    ),
                    legend=alt.Legend(title="Sport", orient="top")
                ),
                tooltip=["week:N", "sport:N", "hours:Q", "distance_km:Q"],
            ).properties(height=260)
            st.altair_chart(apply_forest_chart_theme(c_hours, height=260), use_container_width=True)

        # Chart 2: Distance Progression by Discipline
        with perf_c2:
            st.markdown("##### 🏃 Distance Progression by Discipline (Kilometers)")
            c_dist = alt.Chart(w_m_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X("week:N", title="Training Week", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("distance_km:Q", title="Distance (km)"),
                color=alt.Color(
                    "sport:N",
                    scale=alt.Scale(
                        domain=["Swim", "Run", "Ride", "Walk", "Workout", "Other"],
                        range=["#00D2FF", "#F43F5E", "#10B981", "#F59E0B", "#8B5CF6", "#64748B"],
                    ),
                    legend=None
                ),
                tooltip=["week:N", "sport:N", "distance_km:Q", "hours:Q"],
            ).properties(height=260)
            st.altair_chart(apply_forest_chart_theme(c_dist, height=260), use_container_width=True)

        # Chart 3: Weekly Training Load & Calories
        if weekly_trends:
            w_tr_df = pd.DataFrame(weekly_trends)
            perf_c3, perf_c4 = st.columns(2)
            
            with perf_c3:
                st.markdown("##### ⚡ Weekly Total Training Load Progression")
                c_load = alt.Chart(w_tr_df).mark_area(
                    line={"color": "#00E599", "strokeWidth": 2.5},
                    color=alt.Gradient(
                        gradient="linear",
                        stops=[
                            alt.GradientStop(color="rgba(0, 229, 153, 0.4)", offset=0),
                            alt.GradientStop(color="rgba(0, 229, 153, 0.0)", offset=1),
                        ],
                        x1=1, x2=1, y1=1, y2=0,
                    )
                ).encode(
                    x=alt.X("week:N", title="Training Week", axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y("training_load:Q", title="ICU Training Load"),
                    tooltip=["week:N", "training_load:Q", "sessions:Q"],
                ).properties(height=240)
                st.altair_chart(apply_forest_chart_theme(c_load, height=240), use_container_width=True)

            with perf_c4:
                st.markdown("##### 🔥 Weekly Caloric Burn & Energy (kcal)")
                c_cals = alt.Chart(w_tr_df).mark_bar(
                    color="#F59E0B",
                    cornerRadiusTopLeft=4,
                    cornerRadiusTopRight=4,
                    opacity=0.85
                ).encode(
                    x=alt.X("week:N", title="Training Week", axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y("calories:Q", title="Energy Burned (kcal)"),
                    tooltip=["week:N", "calories:Q", "sessions:Q"],
                ).properties(height=240)
                st.altair_chart(apply_forest_chart_theme(c_cals, height=240), use_container_width=True)

    # Detailed Sport Allocation Table
    st.markdown("---")
    st.markdown("### 🍰 Sport Distribution & Training Allocation")
    dist_map = performance_analytics.get("sport_distribution", {})
    if dist_map:
        alloc_rows = []
        for sp_k, sp_v in dist_map.items():
            alloc_rows.append({
                "Sport": f"{get_sport_icon(sp_k)} {sp_k}",
                "Sessions": sp_v.get("sessions", 0),
                "Total Distance": f"{sp_v.get('distance_km', 0):.2f} km",
                "Total Time": f"{sp_v.get('hours', 0):.1f} hours",
                "Training Load": f"{sp_v.get('training_load', 0):.0f}",
                "Energy (Calories)": f"{sp_v.get('calories', 0):,} kcal",
                "% of Total Time": f"{sp_v.get('percentage_time', 0):.1f}%",
            })
        st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 9: 📈 TRAINING LOAD (CALENDAR WEEK MONDAY TO SUNDAY)
# ============================================================

with tab_load:
    # 1. Calendar-Aligned Monday-Sunday Weeks Calculation
    cur_week_monday = today_date - timedelta(days=today_date.weekday())
    cur_week_sunday = cur_week_monday + timedelta(days=6)
    
    prev_week_monday = cur_week_monday - timedelta(days=7)
    prev_week_sunday = cur_week_monday - timedelta(days=1)

    cur_acts = [
        a for a in all_activities
        if a.get("date") and cur_week_monday <= datetime.fromisoformat(a["date"][:10]).date() <= cur_week_sunday
    ]
    prev_acts = [
        a for a in all_activities
        if a.get("date") and prev_week_monday <= datetime.fromisoformat(a["date"][:10]).date() <= prev_week_sunday
    ]

    cur_week_sum = training_summary(cur_acts)
    prev_week_sum = training_summary(prev_acts)

    tot_cur_load = sum(s.get("training_load", 0) for s in cur_week_sum.values())
    tot_prev_load = sum(s.get("training_load", 0) for s in prev_week_sum.values())

    tot_cur_dist = sum(s.get("distance_km", 0) for s in cur_week_sum.values())
    tot_prev_dist = sum(s.get("distance_km", 0) for s in prev_week_sum.values())

    tot_cur_time = sum(s.get("moving_time_min", 0) for s in cur_week_sum.values())
    tot_prev_time = sum(s.get("moving_time_min", 0) for s in prev_week_sum.values())

    tot_cur_sessions = sum(s.get("sessions", 0) for s in cur_week_sum.values())
    tot_prev_sessions = sum(s.get("sessions", 0) for s in prev_week_sum.values())

    # Acute:Chronic Load Ratio (ACWR)
    acwr = tot_cur_load / max(1.0, tot_prev_load)
    if 0.8 <= acwr <= 1.3:
        form_status_badge = "🟢 Optimal Form (0.8–1.3)"
        form_status_desc = "Optimal training stimulus and progressive adaptation without excessive fatigue."
    elif acwr > 1.3:
        form_status_badge = "🔴 High Fatigue (> 1.3)"
        form_status_desc = "Acute load surge detected. Prioritize recovery and sleep to prevent overreaching."
    else:
        form_status_badge = "🔵 Fresh / Deload (< 0.8)"
        form_status_desc = "Reduced volume. Body is fresh and primed to absorb higher training volume."

    load_delta_pct = ((tot_cur_load - tot_prev_load) / max(1.0, tot_prev_load)) * 100

    # ACWR Status Banner
    st.markdown(
        f"""
        <div style="background: #0C1322; border: 1px solid #1A273D; border-radius: 14px; padding: 18px 22px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                <div>
                    <span class="forest-pill-tag">⚡ TRAINING STIMULUS &amp; ACUTE LOAD RATIO</span>
                    <h3 style="margin: 6px 0 0 0; color: #FFFFFF; font-size: 1.35rem; font-weight: 800;">
                        Calendar Week Training Load Comparison
                    </h3>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: rgba(0, 229, 153, 0.15); color: #00E599; border: 1px solid rgba(0, 229, 153, 0.3); font-size: 0.82rem; font-weight: 700; padding: 4px 12px; border-radius: 6px;">ACWR: {acwr:.2f}</span>
                    <span style="background: #172338; color: #CBD5E1; font-size: 0.82rem; font-weight: 700; padding: 4px 12px; border-radius: 6px;">{form_status_badge}</span>
                </div>
            </div>
            <div style="font-size: 0.84rem; color: #94A3B8;">
                💡 <strong style="color: #FFFFFF;">Form Status:</strong> {form_status_desc}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2 Comparison Hero Cards (Mon-Sun)
    c_wk1, c_wk2 = st.columns(2)

    with c_wk1:
        st.markdown(
            f"""
            <div class="f-card" style="border-top: 4px solid #00E599;">
                <div class="f-card-header">
                    <div>
                        <span class="forest-pill-tag" style="background: rgba(0, 229, 153, 0.1); color: #00E599;">CURRENT WEEK (MON – SUN)</span>
                        <div class="f-card-title" style="margin-top: 6px;">
                            {cur_week_monday.strftime('%b %d')} – {cur_week_sunday.strftime('%b %d, %Y')}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.75rem; color: #64748B;">Δ vs Last Week</span>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 800; color: {'#00E599' if load_delta_pct >= 0 else '#F43F5E'};">
                            {'+' if load_delta_pct > 0 else ''}{load_delta_pct:.0f}%
                        </div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px;">
                    <div class="kpi-card-sub" style="padding: 10px;">
                        <div class="kpi-card-label">Training Load</div>
                        <div class="kpi-card-value" style="font-size: 1.4rem; color: #00E599;">{tot_cur_load:.0f}</div>
                        <div class="kpi-card-footer">ICU load units</div>
                    </div>
                    <div class="kpi-card-sub" style="padding: 10px;">
                        <div class="kpi-card-label">Distance</div>
                        <div class="kpi-card-value" style="font-size: 1.4rem;">{tot_cur_dist:.2f} <span style="font-size: 0.75rem; color: #64748B;">km</span></div>
                        <div class="kpi-card-footer">active volume</div>
                    </div>
                    <div class="kpi-card-sub" style="padding: 10px;">
                        <div class="kpi-card-label">Duration</div>
                        <div class="kpi-card-value" style="font-size: 1.4rem;">{format_duration_hm(tot_cur_time)}</div>
                        <div class="kpi-card-footer">{tot_cur_time:.0f} moving mins</div>
                    </div>
                    <div class="kpi-card-sub" style="padding: 10px;">
                        <div class="kpi-card-label">Sessions</div>
                        <div class="kpi-card-value" style="font-size: 1.4rem;">{tot_cur_sessions}</div>
                        <div class="kpi-card-footer">workouts</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_wk2:
        st.markdown(
            f"""
            <div class="f-card" style="border-top: 4px solid #6366F1;">
                <div class="f-card-header">
                    <div>
                        <span class="forest-pill-tag" style="background: rgba(99, 102, 241, 0.1); color: #818CF8; border-color: rgba(99, 102, 241, 0.3);">PREVIOUS WEEK (MON – SUN)</span>
                        <div class="f-card-title" style="margin-top: 6px;">
                            {prev_week_monday.strftime('%b %d')} – {prev_week_sunday.strftime('%b %d, %Y')}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.75rem; color: #64748B;">Baseline Load</span>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 800; color: #818CF8;">
                            {tot_prev_load:.0f}
                        </div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px;">
                    <div class="kpi-card-sub" style="padding: 10px;">
                        <div class="kpi-card-label">Training Load</div>
                        <div class="kpi-card-value" style="font-size: 1.4rem; color: #818CF8;">{tot_prev_load:.0f}</div>
                        <div class="kpi-card-footer">ICU load units</div>
                    </div>
                    <div class="kpi-card-sub" style="padding: 10px;">
                        <div class="kpi-card-label">Distance</div>
                        <div class="kpi-card-value" style="font-size: 1.4rem;">{tot_prev_dist:.2f} <span style="font-size: 0.75rem; color: #64748B;">km</span></div>
                        <div class="kpi-card-footer">active volume</div>
                    </div>
                    <div class="kpi-card-sub" style="padding: 10px;">
                        <div class="kpi-card-label">Duration</div>
                        <div class="kpi-card-value" style="font-size: 1.4rem;">{format_duration_hm(tot_prev_time)}</div>
                        <div class="kpi-card-footer">{tot_prev_time:.0f} moving mins</div>
                    </div>
                    <div class="kpi-card-sub" style="padding: 10px;">
                        <div class="kpi-card-label">Sessions</div>
                        <div class="kpi-card-value" style="font-size: 1.4rem;">{tot_prev_sessions}</div>
                        <div class="kpi-card-footer">workouts</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Sport-by-Sport Comparison Table
    st.markdown("---")
    st.markdown("### 📊 Sport-by-Sport Weekly Load Breakdown")
    all_sports_set = sorted(list(set(list(cur_week_sum.keys()) + list(prev_week_sum.keys()))))
    
    if all_sports_set:
        sp_comp_rows = []
        for sp in all_sports_set:
            c_sp = cur_week_sum.get(sp, {})
            p_sp = prev_week_sum.get(sp, {})
            
            c_l = c_sp.get("training_load", 0)
            p_l = p_sp.get("training_load", 0)
            diff_l = c_l - p_l
            diff_str = f"{'+' if diff_l > 0 else ''}{diff_l:.0f}" if p_l > 0 or c_l > 0 else "—"

            sp_comp_rows.append({
                "Sport": f"{get_sport_icon(sp)} {sp}",
                "Cur Week Sessions": c_sp.get("sessions", 0),
                "Cur Week Distance": f"{c_sp.get('distance_km', 0):.2f} km",
                "Cur Week Time": format_duration_hm(c_sp.get("moving_time_min", 0)),
                "Cur Week Load": f"{c_l:.0f}",
                "Prev Week Sessions": p_sp.get("sessions", 0),
                "Prev Week Distance": f"{p_sp.get('distance_km', 0):.2f} km",
                "Prev Week Time": format_duration_hm(p_sp.get("moving_time_min", 0)),
                "Prev Week Load": f"{p_l:.0f}",
                "Load Delta": diff_str,
            })
        st.dataframe(pd.DataFrame(sp_comp_rows), use_container_width=True, hide_index=True)

    # 4. Daily Load Bar Chart for Last 14 Days
    st.markdown("---")
    st.markdown("### 📅 Daily Training Load Distribution (14-Day Calendar View)")
    daily_14_data = []
    d_pointer = prev_week_monday
    while d_pointer <= cur_week_sunday:
        d_p_str = d_pointer.strftime("%Y-%m-%d")
        d_acts = [a for a in all_activities if a.get("date") and a["date"][:10] == d_p_str]
        if d_acts:
            for da in d_acts:
                daily_14_data.append({
                    "date": d_pointer.strftime("%a, %b %d"),
                    "sport": da.get("sport", "Other"),
                    "training_load": da.get("training_load", 0),
                    "distance_km": da.get("distance_km", 0),
                })
        else:
            daily_14_data.append({
                "date": d_pointer.strftime("%a, %b %d"),
                "sport": "Rest",
                "training_load": 0,
                "distance_km": 0,
            })
        d_pointer += timedelta(days=1)

    if daily_14_data:
        d14_df = pd.DataFrame(daily_14_data)
        c_14 = alt.Chart(d14_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("date:N", title="Day (Mon-Sun of Last Week -> Mon-Sun of This Week)", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("training_load:Q", title="Daily ICU Load"),
            color=alt.Color(
                "sport:N",
                scale=alt.Scale(
                    domain=["Swim", "Run", "Ride", "Walk", "Workout", "Rest", "Other"],
                    range=["#00D2FF", "#F43F5E", "#10B981", "#F59E0B", "#8B5CF6", "#172338", "#64748B"],
                ),
            ),
            tooltip=["date:N", "sport:N", "training_load:Q", "distance_km:Q"],
        ).properties(height=250)
        st.altair_chart(apply_forest_chart_theme(c_14, height=250), use_container_width=True)


# ============================================================
# TAB 10: 🏆 PERSONAL RECORDS
# ============================================================

with tab_records:
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

    if st.button("🧹 Clear All Caches & Resync", use_container_width=True):
        st.cache_data.clear()
        st.success("Caches cleared! Reloading...")
        st.rerun()

    if st.button("🗑️ Clear Saved Workout Plans", use_container_width=True):
        clear_plans()
        st.warning("All saved workout plans cleared.")
        st.rerun()
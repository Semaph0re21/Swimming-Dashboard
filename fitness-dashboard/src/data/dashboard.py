import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from src.api.intervals import get_activities, get_wellness
from src.data.activities import normalize_activities
from src.data.strava import load_strava_activities, find_strava_export_path
from src.analytics.weekly import weekly_summary
from src.analytics.swim_pace import swim_pace_baseline
from src.analytics.swim_trend import swimming_weekly_trend
from src.analytics.summary import training_summary
from src.analytics.running import get_running_analytics
from src.analytics.cycling import get_cycling_analytics
from src.analytics.walking import get_walking_analytics
from src.analytics.sleep import get_sleep_analytics
from src.analytics.performance import get_performance_analytics
from src.analytics.personal_records import calculate_all_personal_records
from src.training.swim_plan import generate_swim_plan, calculate_baseline
from src.training.swim_paces import swim_pace_zones
from src.training.decision import training_recommendation, days_since_last

CACHE_FILE = Path("activities_raw.json")
logger = logging.getLogger(__name__)


def parse_activity_datetime(date_str):
    """Parse activity date string into datetime object."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str[:19])
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str[:19], fmt)
            except Exception:
                pass
    return None


def merge_and_deduplicate_activities(intervals_activities, strava_activities):
    """
    Merge activities from Intervals.icu and Strava, deduplicating overlapping sessions.
    Intervals provides rich power/intensity/ICU load data, while Strava adds descriptions,
    Relative Effort, photos/media, and historical archive data.
    """
    merged = {}
    
    # First index intervals activities by minute timestamp and sport
    for act in intervals_activities:
        act_dt = parse_activity_datetime(act.get("date"))
        if not act_dt:
            continue
        key = (act_dt.strftime("%Y-%m-%d %H:%M"), act.get("sport"))
        act_entry = dict(act)
        act_entry["source"] = "Garmin / Intervals.icu"
        merged[key] = act_entry

    # Match or add Strava activities
    strava_matched = 0
    strava_added = 0

    for s_act in strava_activities:
        s_dt = parse_activity_datetime(s_act.get("date"))
        if not s_dt:
            continue
        
        s_sport = s_act.get("sport")
        s_dist = s_act.get("distance_km") or 0.0

        # Try exact minute match first
        exact_key = (s_dt.strftime("%Y-%m-%d %H:%M"), s_sport)
        matched_key = None

        if exact_key in merged:
            matched_key = exact_key
        else:
            # Check within +/- 5 minutes window for identical sport and distance
            for offset_m in (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5):
                cand_dt = s_dt + timedelta(minutes=offset_m)
                cand_key = (cand_dt.strftime("%Y-%m-%d %H:%M"), s_sport)
                if cand_key in merged:
                    cand_act = merged[cand_key]
                    cand_dist = cand_act.get("distance_km") or 0.0
                    # Check if distance is similar (within 0.3km or 15%)
                    if abs(cand_dist - s_dist) <= max(0.3, cand_dist * 0.15):
                        matched_key = cand_key
                        break

        if matched_key:
            strava_matched += 1
            target = merged[matched_key]
            target["source"] = "Garmin / Intervals.icu + Strava"
            target["strava_id"] = s_act.get("strava_id")
            if s_act.get("description"):
                target["description"] = s_act.get("description")
            if s_act.get("media"):
                target["media"] = s_act.get("media")
            if s_act.get("relative_effort") is not None:
                target["relative_effort"] = s_act.get("relative_effort")
            if s_act.get("filename"):
                target["filename"] = s_act.get("filename")
            if not target.get("calories") and s_act.get("calories"):
                target["calories"] = s_act.get("calories")
            if not target.get("pool_length_m") and s_act.get("pool_length_m"):
                target["pool_length_m"] = s_act.get("pool_length_m")
        else:
            strava_added += 1
            merged[exact_key] = dict(s_act)

    all_activities = list(merged.values())
    all_activities.sort(key=lambda a: a.get("date", ""), reverse=True)
    return all_activities, strava_matched, strava_added


def get_dashboard_data(start_date, end_date, source_filter="all", strava_path=None):
    """
    Fetch, normalize, and compile full dashboard analytics for the given date window.
    Supports Intervals.icu API, local cache, and Strava export integration.
    
    source_filter: 'all' (merged), 'intervals' (Intervals.icu only), 'strava' (Strava only)
    """
    api_status = "offline"
    raw_intervals = []

    # 1. Fetch or load Intervals.icu data
    try:
        # Fetch wide window from API to enable full historical merge if needed
        raw_intervals = get_activities("2025-01-01", end_date)
        api_status = "connected"
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(raw_intervals, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save Intervals cache: {e}")
    except Exception as e:
        logger.warning(f"API fetch failed: {e}. Falling back to cached activities.")
        api_status = "cache"
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    raw_intervals = json.load(f)
            except Exception as read_err:
                logger.error(f"Failed to read cache: {read_err}")
                raw_intervals = []

    intervals_clean = normalize_activities(raw_intervals)

    # 2. Load Strava activities
    strava_clean = load_strava_activities(strava_path)
    strava_found = bool(strava_clean)

    # 3. Select and merge datasets according to source_filter
    if source_filter == "intervals":
        clean_activities = intervals_clean
        strava_matched, strava_added = 0, 0
    elif source_filter == "strava":
        clean_activities = strava_clean
        strava_matched, strava_added = 0, len(strava_clean)
    else:  # 'all' - Merged
        clean_activities, strava_matched, strava_added = merge_and_deduplicate_activities(
            intervals_clean,
            strava_clean
        )

    # 4. Filter activities within the requested date window [start_date, end_date]
    start_dt = datetime.fromisoformat(start_date).date()
    end_dt = datetime.fromisoformat(end_date).date()

    window_activities = []
    for act in clean_activities:
        act_date_str = act.get("date")
        if not act_date_str:
            continue
        try:
            act_date = datetime.fromisoformat(act_date_str[:10]).date()
            if start_dt <= act_date <= end_dt:
                window_activities.append(act)
        except Exception:
            pass

    # 5. Weekly summaries (current 7 days and prior 7 days ending at end_date)
    current_week = weekly_summary(clean_activities, end_date)

    end = datetime.fromisoformat(end_date).date()
    previous_end = end - timedelta(days=7)
    previous_week = weekly_summary(clean_activities, str(previous_end))

    # 6. Swimming baseline (using all available swims up to end_date for strong baseline)
    all_swims_up_to_date = [
        a for a in clean_activities
        if a.get("sport") == "Swim" and a.get("date") and datetime.fromisoformat(a["date"][:10]).date() <= end_dt
    ]
    long_swims = swim_pace_baseline(all_swims_up_to_date)
    baseline_pace = calculate_baseline(long_swims)
    pace_zones = swim_pace_zones(baseline_pace)

    # 7. Days since last activity for each sport
    days_since_swim = days_since_last(clean_activities, "Swim", end_date)
    days_since_ride = days_since_last(clean_activities, "Ride", end_date)
    days_since_walk = days_since_last(clean_activities, "Walk", end_date)
    days_since_run = days_since_last(clean_activities, "Run", end_date)
    days_since_workout = days_since_last(clean_activities, "Workout", end_date)

    # 8. Wellness data (optional)
    wellness_data = []
    try:
        wellness_data = get_wellness(start_date, end_date)
    except Exception as e:
        logger.warning(f"Could not load wellness data: {e}")

    latest_wellness = wellness_data[-1] if wellness_data else None

    # 9. Generate next swim plan (incorporating latest Garmin sleep & recovery)
    swim_plan = generate_swim_plan(
        current_week,
        previous_week,
        days_since_swim,
        long_swims,
        wellness=latest_wellness,
    )

    # 10. Next workout recommendation across sports
    recommendation = training_recommendation(
        clean_activities,
        current_week,
        previous_week,
        end_date
    )

    # 11. Multi-sport summary for the selected window
    summary = training_summary(window_activities)

    # 12. Swimming weekly trends (within selected window or full history)
    weekly_trends = swimming_weekly_trend(window_activities if len(window_activities) > 5 else clean_activities)

    # 13. Running analytics
    running_analytics = get_running_analytics(clean_activities, strava_path)

    # 14. Cycling analytics
    cycling_analytics = get_cycling_analytics(clean_activities)

    # 15. Walking analytics
    walking_analytics = get_walking_analytics(clean_activities)

    # 16. Sleep & Recovery analytics
    sleep_analytics = get_sleep_analytics(wellness_data, start_date, end_date)

    # 17. Cross-sport Performance analytics
    performance_analytics = get_performance_analytics(window_activities if window_activities else clean_activities, wellness_data)

    # 18. Unified Personal Records (PBs)
    personal_records = calculate_all_personal_records(clean_activities)

    return {
        "activities": window_activities,
        "all_activities": clean_activities,
        "current_week": current_week,
        "previous_week": previous_week,
        "swim_baseline": long_swims,
        "baseline_pace": baseline_pace,
        "pace_zones": pace_zones,
        "days_since_swim": days_since_swim,
        "days_since_ride": days_since_ride,
        "days_since_walk": days_since_walk,
        "days_since_run": days_since_run,
        "days_since_workout": days_since_workout,
        "next_swim_plan": swim_plan,
        "recommendation": recommendation,
        "summary": summary,
        "weekly_trends": weekly_trends,
        "running_analytics": running_analytics,
        "cycling_analytics": cycling_analytics,
        "walking_analytics": walking_analytics,
        "sleep_analytics": sleep_analytics,
        "performance_analytics": performance_analytics,
        "personal_records": personal_records,
        "wellness": wellness_data,
        "api_status": api_status,
        "strava_found": strava_found,
        "total_intervals_count": len(intervals_clean),
        "total_strava_count": len(strava_clean),
        "strava_matched": strava_matched,
        "strava_added": strava_added,
        "source_filter": source_filter,
    }
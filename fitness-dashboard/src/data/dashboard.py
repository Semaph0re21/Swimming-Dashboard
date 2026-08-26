import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from src.api.intervals import get_activities, get_wellness
from src.data.activities import normalize_activities
from src.analytics.weekly import weekly_summary
from src.analytics.swim_pace import swim_pace_baseline
from src.analytics.swim_trend import swimming_weekly_trend
from src.analytics.summary import training_summary
from src.training.swim_plan import generate_swim_plan, calculate_baseline
from src.training.swim_paces import swim_pace_zones
from src.training.decision import training_recommendation, days_since_last

CACHE_FILE = Path("activities_raw.json")
logger = logging.getLogger(__name__)


def get_dashboard_data(start_date, end_date):
    """
    Fetch, normalize, and compile full dashboard analytics for the given date window.
    Supports graceful fallback to cached raw data if API is offline.
    """
    data_source = "api"
    activities = []

    try:
        activities = get_activities(start_date, end_date)
        # Cache raw data locally for offline resiliency
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(activities, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    except Exception as e:
        logger.warning(f"API fetch failed: {e}. Falling back to cached activities.")
        data_source = "cache"
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    all_raw = json.load(f)
                start_dt = datetime.fromisoformat(start_date).date()
                end_dt = datetime.fromisoformat(end_date).date()
                activities = [
                    a for a in all_raw
                    if "start_date_local" in a and (
                        start_dt <= datetime.fromisoformat(a["start_date_local"][:10]).date() <= end_dt
                    )
                ]
            except Exception as read_err:
                logger.error(f"Failed to read cache: {read_err}")
                activities = []

    clean_activities = normalize_activities(activities)

    # Weekly summaries (current 7 days and prior 7 days)
    current_week = weekly_summary(clean_activities, end_date)

    end = datetime.fromisoformat(end_date).date()
    previous_end = end - timedelta(days=7)
    previous_week = weekly_summary(clean_activities, str(previous_end))

    # Swimming baseline
    long_swims = swim_pace_baseline(clean_activities)
    baseline_pace = calculate_baseline(long_swims)
    pace_zones = swim_pace_zones(baseline_pace)

    # Days since last activity for each sport
    days_since_swim = days_since_last(clean_activities, "Swim", end_date)
    days_since_ride = days_since_last(clean_activities, "Ride", end_date)
    days_since_walk = days_since_last(clean_activities, "Walk", end_date)

    # Generate next swim plan
    swim_plan = generate_swim_plan(
        current_week,
        previous_week,
        days_since_swim,
        long_swims
    )

    # Next workout recommendation across sports
    recommendation = training_recommendation(
        clean_activities,
        current_week,
        previous_week,
        end_date
    )

    # Multi-sport overall summary
    summary = training_summary(clean_activities)

    # Swimming weekly trends
    weekly_trends = swimming_weekly_trend(clean_activities)

    # Wellness data (optional)
    wellness_data = []
    try:
        wellness_data = get_wellness(start_date, end_date)
    except Exception as e:
        logger.warning(f"Could not load wellness data: {e}")

    return {
        "activities": clean_activities,
        "current_week": current_week,
        "previous_week": previous_week,
        "swim_baseline": long_swims,
        "baseline_pace": baseline_pace,
        "pace_zones": pace_zones,
        "days_since_swim": days_since_swim,
        "days_since_ride": days_since_ride,
        "days_since_walk": days_since_walk,
        "next_swim_plan": swim_plan,
        "recommendation": recommendation,
        "summary": summary,
        "weekly_trends": weekly_trends,
        "wellness": wellness_data,
        "data_source": data_source,
    }
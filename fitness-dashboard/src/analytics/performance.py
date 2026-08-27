"""
Cross-sport performance analytics and multi-sport training volume trends.
"""
from datetime import datetime, timedelta
from collections import defaultdict


def calculate_activity_streak(activities, today_date_str=None):
    """
    Calculate current consecutive days activity streak.
    """
    if not activities:
        return 0

    dates = set()
    for a in activities:
        d = a.get("date")
        if d:
            dates.add(d[:10])

    if not dates:
        return 0

    sorted_dates = sorted(dates, reverse=True)
    today = datetime.fromisoformat(today_date_str[:10]).date() if today_date_str else datetime.now().date()
    latest_act_date = datetime.fromisoformat(sorted_dates[0]).date()

    # If latest activity was not today or yesterday, streak is 0
    if (today - latest_act_date).days > 1:
        return 0

    streak = 0
    curr_check = latest_act_date
    while curr_check.strftime("%Y-%m-%d") in dates:
        streak += 1
        curr_check -= timedelta(days=1)

    return streak


def get_performance_analytics(activities, wellness_records=None):
    """
    Compile cross-sport performance, multi-sport volume trends, and HR progression.
    """
    if not activities:
        return {
            "sport_distribution": {},
            "weekly_multi_sport": [],
            "monthly_multi_sport": [],
            "hr_trends": [],
            "current_streak": 0,
            "total_active_days": 0,
        }

    # 1. Sport Totals
    sports_data = defaultdict(lambda: {"distance_km": 0.0, "time_min": 0.0, "calories": 0, "load": 0, "count": 0})
    for a in activities:
        sp = a.get("sport") or "Other"
        sports_data[sp]["distance_km"] += a.get("distance_km") or 0.0
        sports_data[sp]["time_min"] += a.get("moving_time_min") or a.get("duration_min") or 0.0
        sports_data[sp]["calories"] += a.get("calories") or 0
        sports_data[sp]["load"] += a.get("training_load") or 0
        sports_data[sp]["count"] += 1

    total_time = sum(d["time_min"] for d in sports_data.values())
    sport_dist = {}
    for sp, data in sports_data.items():
        pct = round((data["time_min"] / total_time * 100), 1) if total_time > 0 else 0
        sport_dist[sp] = {
            "distance_km": round(data["distance_km"], 2),
            "time_min": round(data["time_min"], 1),
            "hours": round(data["time_min"] / 60, 1),
            "calories": data["calories"],
            "load": data["load"],
            "count": data["count"],
            "percentage_time": pct,
        }

    # 2. Multi-Sport Weekly Volume
    weekly_map = defaultdict(lambda: defaultdict(lambda: {"distance_km": 0.0, "time_min": 0.0, "load": 0, "sessions": 0}))
    for a in activities:
        d_str = a.get("date")
        if not d_str:
            continue
        try:
            dt = datetime.fromisoformat(d_str[:10])
            year, week_num, _ = dt.isocalendar()
            w_key = f"{year}-W{week_num:02d}"
            sp = a.get("sport") or "Other"
            weekly_map[w_key][sp]["distance_km"] += a.get("distance_km") or 0.0
            weekly_map[w_key][sp]["time_min"] += a.get("moving_time_min") or a.get("duration_min") or 0.0
            weekly_map[w_key][sp]["load"] += a.get("training_load") or 0
            weekly_map[w_key][sp]["sessions"] += 1
        except Exception:
            pass

    weekly_multi_sport = []
    for w_key in sorted(weekly_map.keys()):
        for sp, v in weekly_map[w_key].items():
            weekly_multi_sport.append({
                "week": w_key,
                "sport": sp,
                "distance_km": round(v["distance_km"], 2),
                "time_min": round(v["time_min"], 1),
                "hours": round(v["time_min"] / 60, 2),
                "load": v["load"],
                "sessions": v["sessions"],
            })

    # 3. Multi-Sport Monthly Volume
    monthly_map = defaultdict(lambda: defaultdict(lambda: {"distance_km": 0.0, "time_min": 0.0, "load": 0, "sessions": 0}))
    for a in activities:
        d_str = a.get("date")
        if not d_str:
            continue
        try:
            m_key = d_str[:7]
            sp = a.get("sport") or "Other"
            monthly_map[m_key][sp]["distance_km"] += a.get("distance_km") or 0.0
            monthly_map[m_key][sp]["time_min"] += a.get("moving_time_min") or a.get("duration_min") or 0.0
            monthly_map[m_key][sp]["load"] += a.get("training_load") or 0
            monthly_map[m_key][sp]["sessions"] += 1
        except Exception:
            pass

    monthly_multi_sport = []
    for m_key in sorted(monthly_map.keys()):
        for sp, v in monthly_map[m_key].items():
            monthly_multi_sport.append({
                "month": m_key,
                "sport": sp,
                "distance_km": round(v["distance_km"], 2),
                "time_min": round(v["time_min"], 1),
                "hours": round(v["time_min"] / 60, 2),
                "load": v["load"],
                "sessions": v["sessions"],
            })

    # 4. Heart Rate progression across activities
    hr_trends = []
    for a in sorted(activities, key=lambda x: x.get("date", "")):
        if a.get("avg_hr") and a.get("date"):
            hr_trends.append({
                "date": a["date"][:10],
                "sport": a.get("sport", "Other"),
                "name": a.get("name", "Activity"),
                "avg_hr": a["avg_hr"],
                "max_hr": a.get("max_hr"),
                "load": a.get("training_load", 0),
            })

    # 5. Streak & Active Days
    unique_dates = set(a["date"][:10] for a in activities if a.get("date"))
    latest_d = max(unique_dates) if unique_dates else None
    streak = calculate_activity_streak(activities, latest_d)

    return {
        "sport_distribution": sport_dist,
        "weekly_multi_sport": weekly_multi_sport,
        "monthly_multi_sport": monthly_multi_sport,
        "hr_trends": hr_trends,
        "current_streak": streak,
        "total_active_days": len(unique_dates),
    }

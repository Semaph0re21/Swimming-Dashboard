"""
Walking analytics and consistency calculations.
"""
from datetime import datetime
from collections import defaultdict


def format_walking_pace(pace_seconds_per_km):
    """Format pace in seconds per km to MM:SS /km."""
    if not pace_seconds_per_km or pace_seconds_per_km <= 0 or pace_seconds_per_km > 3600:
        return "N/A"
    minutes = int(pace_seconds_per_km // 60)
    seconds = int(pace_seconds_per_km % 60)
    return f"{minutes}:{seconds:02d} /km"


def get_walking_analytics(activities):
    """
    Extract and compute comprehensive walking analytics from activities list.
    """
    walks = [
        a for a in activities
        if a.get("sport") == "Walk"
    ]
    walks.sort(key=lambda a: a.get("date", ""), reverse=True)

    if not walks:
        return {
            "walks": [],
            "total_walks": 0,
            "total_distance_km": 0.0,
            "total_time_min": 0.0,
            "total_moving_min": 0.0,
            "total_calories": 0,
            "total_elevation_m": 0.0,
            "total_steps": 0,
            "avg_pace_formatted": "N/A",
            "avg_pace_seconds": None,
            "avg_hr": None,
            "max_hr": None,
            "longest_walk_km": 0.0,
            "avg_daily_km": 0.0,
            "active_days": 0,
            "weekly_volume": [],
            "personal_bests": [],
        }

    total_walks = len(walks)
    total_dist = sum(w.get("distance_km") or 0.0 for w in walks)
    total_time = sum(w.get("duration_min") or 0.0 for w in walks)
    total_moving = sum(w.get("moving_time_min") or 0.0 for w in walks)
    total_cals = sum(w.get("calories") or 0 for w in walks if w.get("calories"))
    total_elev = sum(w.get("elevation_m") or 0.0 for w in walks if w.get("elevation_m"))
    total_steps = sum(w.get("total_steps") or 0 for w in walks if w.get("total_steps"))

    # Paces
    paces_sec = []
    for w in walks:
        p_sec = None
        if w.get("distance_km") and w.get("moving_time_min") and w["distance_km"] > 0:
            p_sec = (w["moving_time_min"] * 60) / w["distance_km"]
        elif w.get("avg_speed") and w["avg_speed"] > 0:
            p_sec = 1000 / w["avg_speed"]
        if p_sec and 180 <= p_sec <= 2400:
            paces_sec.append(p_sec)
            w["computed_pace_sec"] = p_sec
            w["computed_pace_formatted"] = format_walking_pace(p_sec)

    avg_pace_sec = sum(paces_sec) / len(paces_sec) if paces_sec else None
    avg_pace_fmt = format_walking_pace(avg_pace_sec)

    # Heart rate
    hrs = [w["avg_hr"] for w in walks if w.get("avg_hr")]
    avg_hr = round(sum(hrs) / len(hrs)) if hrs else None
    max_hrs = [w["max_hr"] for w in walks if w.get("max_hr")]
    peak_hr = max(max_hrs) if max_hrs else None

    # Longest walk
    distances = [w.get("distance_km") or 0.0 for w in walks]
    longest_walk = max(distances) if distances else 0.0

    # Active days and daily average over unique active days
    unique_dates = set(w.get("date", "")[:10] for w in walks if w.get("date"))
    active_days_count = len(unique_dates)
    avg_daily_km = round(total_dist / active_days_count, 2) if active_days_count > 0 else 0.0

    # Weekly volume
    weeks_map = defaultdict(lambda: {"distance_km": 0.0, "time_min": 0.0, "sessions": 0, "elevation_m": 0.0})
    for w in walks:
        date_str = w.get("date", "")
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str[:10])
                year, week_num, _ = dt.isocalendar()
                w_key = f"{year}-W{week_num:02d}"
                weeks_map[w_key]["distance_km"] += w.get("distance_km") or 0.0
                weeks_map[w_key]["time_min"] += w.get("moving_time_min") or 0.0
                weeks_map[w_key]["elevation_m"] += w.get("elevation_m") or 0.0
                weeks_map[w_key]["sessions"] += 1
            except Exception:
                pass

    weekly_volume = [
        {"week": k, "distance_km": round(v["distance_km"], 2), "time_min": round(v["time_min"], 1), "sessions": v["sessions"], "elevation_m": round(v["elevation_m"], 1)}
        for k, v in sorted(weeks_map.items())
    ]

    # Walking Personal Bests
    pbs = []
    # 1. Longest Walk
    longest_act = max(walks, key=lambda w: w.get("distance_km") or 0.0, default=None)
    if longest_act and (longest_act.get("distance_km") or 0) > 0:
        pbs.append({
            "category": "Longest Walk",
            "metric": f"{longest_act['distance_km']:.2f} km",
            "date": longest_act.get("date", "")[:10],
            "activity_name": longest_act.get("name", "Walk"),
            "duration": f"{longest_act.get('moving_time_min', 0):.0f} min",
        })

    # 2. Fastest Pace (walks >= 1 km)
    qual_pace_walks = [w for w in walks if (w.get("distance_km") or 0) >= 1.0 and w.get("computed_pace_sec")]
    if qual_pace_walks:
        fastest_act = min(qual_pace_walks, key=lambda w: w["computed_pace_sec"])
        pbs.append({
            "category": "Fastest Pace (>=1km)",
            "metric": format_walking_pace(fastest_act["computed_pace_sec"]),
            "date": fastest_act.get("date", "")[:10],
            "activity_name": fastest_act.get("name", "Walk"),
            "distance": f"{fastest_act.get('distance_km', 0):.2f} km",
        })

    # 3. Highest Elevation Gain
    elev_walks = [w for w in walks if w.get("elevation_m") and w["elevation_m"] > 0]
    if elev_walks:
        highest_elev_act = max(elev_walks, key=lambda w: w["elevation_m"])
        pbs.append({
            "category": "Highest Elevation Gain",
            "metric": f"{highest_elev_act['elevation_m']:.0f} m",
            "date": highest_elev_act.get("date", "")[:10],
            "activity_name": highest_elev_act.get("name", "Walk"),
            "distance": f"{highest_elev_act.get('distance_km', 0):.2f} km",
        })

    return {
        "walks": walks,
        "total_walks": total_walks,
        "total_distance_km": round(total_dist, 2),
        "total_time_min": round(total_time, 1),
        "total_moving_min": round(total_moving, 1),
        "total_calories": total_cals,
        "total_elevation_m": round(total_elev, 1),
        "total_steps": total_steps,
        "avg_pace_formatted": avg_pace_fmt,
        "avg_pace_seconds": avg_pace_sec,
        "avg_hr": avg_hr,
        "max_hr": peak_hr,
        "longest_walk_km": round(longest_walk, 2),
        "avg_daily_km": avg_daily_km,
        "active_days": active_days_count,
        "weekly_volume": weekly_volume,
        "personal_bests": pbs,
    }

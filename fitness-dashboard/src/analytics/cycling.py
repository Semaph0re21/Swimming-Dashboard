"""
Cycling analytics and metric calculations.
"""
from datetime import datetime
from collections import defaultdict


def get_cycling_analytics(activities):
    """
    Extract and compute comprehensive cycling analytics from activities list.
    """
    rides = [
        a for a in activities
        if a.get("sport") == "Ride"
    ]
    rides.sort(key=lambda a: a.get("date", ""), reverse=True)

    if not rides:
        return {
            "rides": [],
            "total_rides": 0,
            "total_distance_km": 0.0,
            "total_time_min": 0.0,
            "total_moving_min": 0.0,
            "total_calories": 0,
            "total_elevation_m": 0.0,
            "total_load": 0,
            "avg_speed_kmh": None,
            "avg_hr": None,
            "max_hr": None,
            "longest_ride_km": 0.0,
            "fastest_speed_kmh": None,
            "weekly_volume": [],
            "personal_bests": [],
        }

    total_rides = len(rides)
    total_dist = sum(r.get("distance_km") or 0.0 for r in rides)
    total_time = sum(r.get("duration_min") or 0.0 for r in rides)
    total_moving = sum(r.get("moving_time_min") or 0.0 for r in rides)
    total_cals = sum(r.get("calories") or 0 for r in rides if r.get("calories"))
    total_elev = sum(r.get("elevation_m") or 0.0 for r in rides if r.get("elevation_m"))
    total_load = sum(r.get("training_load") or 0 for r in rides if r.get("training_load"))

    # Speeds: convert m/s to km/h if present, or compute distance / moving_time
    speeds_kmh = []
    for r in rides:
        s_kmh = None
        if r.get("avg_speed"):
            s_kmh = round(r["avg_speed"] * 3.6, 1)
        elif r.get("distance_km") and r.get("moving_time_min") and r["moving_time_min"] > 0:
            s_kmh = round(r["distance_km"] / (r["moving_time_min"] / 60), 1)
        if s_kmh and 1.0 <= s_kmh <= 80.0:
            speeds_kmh.append(s_kmh)
            r["computed_speed_kmh"] = s_kmh

    avg_speed = round(sum(speeds_kmh) / len(speeds_kmh), 1) if speeds_kmh else None
    fastest_speed = max(speeds_kmh) if speeds_kmh else None

    # Heart rates
    hrs = [r["avg_hr"] for r in rides if r.get("avg_hr")]
    avg_hr = round(sum(hrs) / len(hrs)) if hrs else None
    max_hrs = [r["max_hr"] for r in rides if r.get("max_hr")]
    peak_hr = max(max_hrs) if max_hrs else None

    # Longest ride
    distances = [r.get("distance_km") or 0.0 for r in rides]
    longest_ride = max(distances) if distances else 0.0

    # Weekly volume
    weeks_map = defaultdict(lambda: {"distance_km": 0.0, "time_min": 0.0, "sessions": 0, "elevation_m": 0.0})
    for r in rides:
        date_str = r.get("date", "")
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str[:10])
                year, week_num, _ = dt.isocalendar()
                w_key = f"{year}-W{week_num:02d}"
                weeks_map[w_key]["distance_km"] += r.get("distance_km") or 0.0
                weeks_map[w_key]["time_min"] += r.get("moving_time_min") or 0.0
                weeks_map[w_key]["elevation_m"] += r.get("elevation_m") or 0.0
                weeks_map[w_key]["sessions"] += 1
            except Exception:
                pass

    weekly_volume = [
        {"week": k, "distance_km": round(v["distance_km"], 2), "time_min": round(v["time_min"], 1), "sessions": v["sessions"], "elevation_m": round(v["elevation_m"], 1)}
        for k, v in sorted(weeks_map.items())
    ]

    # Cycling Personal Bests (strictly from data)
    pbs = []
    # 1. Longest Ride
    longest_act = max(rides, key=lambda r: r.get("distance_km") or 0.0, default=None)
    if longest_act and (longest_act.get("distance_km") or 0) > 0:
        pbs.append({
            "category": "Longest Ride",
            "metric": f"{longest_act['distance_km']:.2f} km",
            "date": longest_act.get("date", "")[:10],
            "activity_name": longest_act.get("name", "Ride"),
            "duration": f"{longest_act.get('moving_time_min', 0):.0f} min",
        })

    # 2. Fastest Average Speed (rides >= 3 km for reliability)
    qual_speed_rides = [r for r in rides if (r.get("distance_km") or 0) >= 3.0 and r.get("computed_speed_kmh")]
    if qual_speed_rides:
        fastest_act = max(qual_speed_rides, key=lambda r: r["computed_speed_kmh"])
        pbs.append({
            "category": "Fastest Avg Speed (>=3km)",
            "metric": f"{fastest_act['computed_speed_kmh']:.1f} km/h",
            "date": fastest_act.get("date", "")[:10],
            "activity_name": fastest_act.get("name", "Ride"),
            "distance": f"{fastest_act.get('distance_km', 0):.2f} km",
        })

    # 3. Highest Elevation Gain
    elev_rides = [r for r in rides if r.get("elevation_m") and r["elevation_m"] > 0]
    if elev_rides:
        highest_elev_act = max(elev_rides, key=lambda r: r["elevation_m"])
        pbs.append({
            "category": "Highest Elevation Gain",
            "metric": f"{highest_elev_act['elevation_m']:.0f} m",
            "date": highest_elev_act.get("date", "")[:10],
            "activity_name": highest_elev_act.get("name", "Ride"),
            "distance": f"{highest_elev_act.get('distance_km', 0):.2f} km",
        })

    # 4. Longest Duration
    dur_act = max(rides, key=lambda r: r.get("moving_time_min") or 0.0, default=None)
    if dur_act and (dur_act.get("moving_time_min") or 0) > 0:
        pbs.append({
            "category": "Longest Duration",
            "metric": f"{dur_act['moving_time_min']:.0f} min",
            "date": dur_act.get("date", "")[:10],
            "activity_name": dur_act.get("name", "Ride"),
            "distance": f"{dur_act.get('distance_km', 0):.2f} km",
        })

    return {
        "rides": rides,
        "total_rides": total_rides,
        "total_distance_km": round(total_dist, 2),
        "total_time_min": round(total_time, 1),
        "total_moving_min": round(total_moving, 1),
        "total_calories": total_cals,
        "total_elevation_m": round(total_elev, 1),
        "total_load": total_load,
        "avg_speed_kmh": avg_speed,
        "fastest_speed_kmh": fastest_speed,
        "avg_hr": avg_hr,
        "max_hr": peak_hr,
        "longest_ride_km": round(longest_ride, 2),
        "weekly_volume": weekly_volume,
        "personal_bests": pbs,
    }

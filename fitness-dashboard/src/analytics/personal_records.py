"""
Unified multi-sport Personal Records (PBs) calculation engine.
Strictly calculates metrics from verified athlete activity data without fabrication.
"""
from datetime import datetime


def format_time_sec(seconds):
    """Format seconds into HH:MM:SS or MM:SS."""
    if not seconds or seconds <= 0:
        return "N/A"
    seconds = int(round(seconds))
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def format_pace_100m(pace_sec):
    """Format pace in sec/100m into M:SS /100m."""
    if not pace_sec or pace_sec <= 0 or pace_sec > 600:
        return "N/A"
    mins = int(pace_sec // 60)
    secs = int(round(pace_sec % 60))
    return f"{mins}:{secs:02d} /100m"


def format_pace_km(pace_sec_km):
    """Format pace in sec/km into MM:SS /km."""
    if not pace_sec_km or pace_sec_km <= 0 or pace_sec_km > 3600:
        return "N/A"
    mins = int(pace_sec_km // 60)
    secs = int(round(pace_sec_km % 60))
    return f"{mins}:{secs:02d} /km"


def calculate_all_personal_records(activities):
    """
    Calculate verified personal bests for Swimming, Running, Cycling, and Walking.
    """
    swims = [a for a in activities if a.get("sport") == "Swim"]
    runs = [a for a in activities if a.get("sport") == "Run"]
    rides = [a for a in activities if a.get("sport") == "Ride"]
    walks = [a for a in activities if a.get("sport") == "Walk"]

    records = {
        "Swimming": [],
        "Running": [],
        "Cycling": [],
        "Walking": [],
    }

    # ==================== SWIMMING RECORDS ====================
    if swims:
        # Longest Swim
        longest_swim = max(swims, key=lambda s: s.get("distance_km") or 0.0, default=None)
        if longest_swim and (longest_swim.get("distance_km") or 0) > 0:
            records["Swimming"].append({
                "event": "Longest Swim Distance",
                "record": f"{longest_swim['distance_km'] * 1000:.0f} m ({longest_swim['distance_km']:.2f} km)",
                "date": longest_swim.get("date", "")[:10],
                "activity_name": longest_swim.get("name", "Swim"),
                "duration": f"{longest_swim.get('moving_time_min', 0):.1f} min",
            })

        # Distance benchmarks: 1000m, 1500m, 2000m, 2500m, 3000m
        for target_m in (1000, 1500, 2000, 2500, 3000):
            target_km = target_m / 1000.0
            # Qualifying swims within +/- 150m of target
            qual = [
                s for s in swims
                if s.get("distance_km") and abs(s["distance_km"] - target_km) <= 0.18
                and s.get("moving_time_min") and s["moving_time_min"] > 0
            ]
            if qual:
                best = min(qual, key=lambda s: (s["moving_time_min"] * 60) / (s["distance_km"] * 10))
                pace_100m = (best["moving_time_min"] * 60) / (best["distance_km"] * 10)
                records["Swimming"].append({
                    "event": f"Fastest {target_m:,}m Swim",
                    "record": format_pace_100m(pace_100m),
                    "date": best.get("date", "")[:10],
                    "activity_name": best.get("name", "Swim"),
                    "duration": f"{best.get('moving_time_min', 0):.1f} min ({best.get('distance_km', 0)*1000:.0f}m)",
                })

        # Fastest overall pace on any swim >= 800m
        long_qual = [
            s for s in swims
            if (s.get("distance_km") or 0) >= 0.8
            and s.get("moving_time_min") and s["moving_time_min"] > 0
        ]
        if long_qual:
            best_pace_act = min(long_qual, key=lambda s: (s["moving_time_min"] * 60) / (s["distance_km"] * 10))
            pace_100m = (best_pace_act["moving_time_min"] * 60) / (best_pace_act["distance_km"] * 10)
            records["Swimming"].append({
                "event": "Fastest Overall Pace (>=800m)",
                "record": format_pace_100m(pace_100m),
                "date": best_pace_act.get("date", "")[:10],
                "activity_name": best_pace_act.get("name", "Swim"),
                "duration": f"{best_pace_act.get('distance_km', 0):.2f} km in {best_pace_act.get('moving_time_min', 0):.1f} min",
            })

    # ==================== RUNNING RECORDS ====================
    if runs:
        # Longest Run
        longest_run = max(runs, key=lambda r: r.get("distance_km") or 0.0, default=None)
        if longest_run and (longest_run.get("distance_km") or 0) > 0:
            records["Running"].append({
                "event": "Longest Run Distance",
                "record": f"{longest_run['distance_km']:.2f} km",
                "date": longest_run.get("date", "")[:10],
                "activity_name": longest_run.get("name", "Run"),
                "duration": f"{longest_run.get('moving_time_min', 0):.1f} min",
            })

        # Benchmarks: 1 km, 5 km, 10 km
        for target_km, label in [(1.0, "1 km"), (5.0, "5 km"), (10.0, "10 km"), (21.1, "Half Marathon")]:
            qual_runs = [
                r for r in runs
                if (r.get("distance_km") or 0) >= (target_km * 0.95)
                and r.get("moving_time_min") and r["moving_time_min"] > 0
            ]
            if qual_runs:
                # Calculate estimated pace/time for target
                best_run = min(qual_runs, key=lambda r: (r["moving_time_min"] * 60) / r["distance_km"])
                pace_sec_km = (best_run["moving_time_min"] * 60) / best_run["distance_km"]
                time_at_pace = pace_sec_km * target_km
                records["Running"].append({
                    "event": f"Best {label}",
                    "record": f"{format_time_sec(time_at_pace)} ({format_pace_km(pace_sec_km)})",
                    "date": best_run.get("date", "")[:10],
                    "activity_name": best_run.get("name", "Run"),
                    "duration": f"{best_run.get('distance_km', 0):.2f} km in {best_run.get('moving_time_min', 0):.1f} min",
                })

        # Fastest Average Pace
        fast_runs = [r for r in runs if (r.get("distance_km") or 0) >= 1.0 and r.get("moving_time_min")]
        if fast_runs:
            fastest_run = min(fast_runs, key=lambda r: (r["moving_time_min"] * 60) / r["distance_km"])
            pace_sec_km = (fastest_run["moving_time_min"] * 60) / fastest_run["distance_km"]
            records["Running"].append({
                "event": "Fastest Overall Pace (>=1km)",
                "record": format_pace_km(pace_sec_km),
                "date": fastest_run.get("date", "")[:10],
                "activity_name": fastest_run.get("name", "Run"),
                "duration": f"{fastest_run.get('distance_km', 0):.2f} km in {fastest_run.get('moving_time_min', 0):.1f} min",
            })

    # ==================== CYCLING RECORDS ====================
    if rides:
        # Longest Ride
        longest_ride = max(rides, key=lambda r: r.get("distance_km") or 0.0, default=None)
        if longest_ride and (longest_ride.get("distance_km") or 0) > 0:
            records["Cycling"].append({
                "event": "Longest Ride Distance",
                "record": f"{longest_ride['distance_km']:.2f} km",
                "date": longest_ride.get("date", "")[:10],
                "activity_name": longest_ride.get("name", "Ride"),
                "duration": f"{longest_ride.get('moving_time_min', 0):.0f} min",
            })

        # Fastest Speed (rides >= 2km)
        qual_speed = []
        for r in rides:
            s_kmh = None
            if r.get("avg_speed"):
                s_kmh = r["avg_speed"] * 3.6
            elif r.get("distance_km") and r.get("moving_time_min") and r["moving_time_min"] > 0:
                s_kmh = r["distance_km"] / (r["moving_time_min"] / 60)
            if s_kmh and 3.0 <= s_kmh <= 80.0 and (r.get("distance_km") or 0) >= 2.0:
                qual_speed.append((r, s_kmh))
        if qual_speed:
            best_ride, best_speed = max(qual_speed, key=lambda item: item[1])
            records["Cycling"].append({
                "event": "Fastest Avg Speed (>=2km)",
                "record": f"{best_speed:.1f} km/h",
                "date": best_ride.get("date", "")[:10],
                "activity_name": best_ride.get("name", "Ride"),
                "duration": f"{best_ride.get('distance_km', 0):.2f} km in {best_ride.get('moving_time_min', 0):.0f} min",
            })

        # Highest Elevation Gain
        elev_rides = [r for r in rides if r.get("elevation_m") and r["elevation_m"] > 0]
        if elev_rides:
            best_elev_ride = max(elev_rides, key=lambda r: r["elevation_m"])
            records["Cycling"].append({
                "event": "Highest Elevation Gain",
                "record": f"{best_elev_ride['elevation_m']:.0f} m",
                "date": best_elev_ride.get("date", "")[:10],
                "activity_name": best_elev_ride.get("name", "Ride"),
                "duration": f"{best_elev_ride.get('distance_km', 0):.2f} km",
            })

    # ==================== WALKING RECORDS ====================
    if walks:
        # Longest Walk
        longest_walk = max(walks, key=lambda w: w.get("distance_km") or 0.0, default=None)
        if longest_walk and (longest_walk.get("distance_km") or 0) > 0:
            records["Walking"].append({
                "event": "Longest Walk Distance",
                "record": f"{longest_walk['distance_km']:.2f} km",
                "date": longest_walk.get("date", "")[:10],
                "activity_name": longest_walk.get("name", "Walk"),
                "duration": f"{longest_walk.get('moving_time_min', 0):.0f} min",
            })

        # Fastest Walk Pace (>= 1km)
        qual_walks = [
            w for w in walks
            if (w.get("distance_km") or 0) >= 1.0
            and w.get("moving_time_min") and w["moving_time_min"] > 0
        ]
        if qual_walks:
            best_walk = min(qual_walks, key=lambda w: (w["moving_time_min"] * 60) / w["distance_km"])
            pace_sec_km = (best_walk["moving_time_min"] * 60) / best_walk["distance_km"]
            records["Walking"].append({
                "event": "Fastest Avg Pace (>=1km)",
                "record": format_pace_km(pace_sec_km),
                "date": best_walk.get("date", "")[:10],
                "activity_name": best_walk.get("name", "Walk"),
                "duration": f"{best_walk.get('distance_km', 0):.2f} km in {best_walk.get('moving_time_min', 0):.0f} min",
            })

    return records

import gzip
import math
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from src.data.strava import find_strava_export_path


def format_run_pace(seconds_per_km):
    """Format seconds per km into MM:SS /km string."""
    if not seconds_per_km or seconds_per_km <= 0:
        return "—"
    try:
        minutes = int(seconds_per_km // 60)
        seconds = int(round(seconds_per_km % 60))
        return f"{minutes}:{seconds:02d} /km"
    except Exception:
        return "—"


def haversine_distance(lat1, lon1, lat2, lon2):
    """Compute Great Circle distance between two coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def parse_gpx_splits(filename, custom_path=None):
    """
    Parse a GPX (or GPX.GZ) file from Strava export to compute 1-km splits.
    """
    if not filename:
        return []

    export_path = find_strava_export_path(custom_path)
    gpx_file = None

    if export_path and export_path.is_dir():
        cand = export_path / filename
        if cand.exists():
            gpx_file = cand

    if not gpx_file:
        cand_local = Path("data/strava") / filename
        if cand_local.exists():
            gpx_file = cand_local

    if not gpx_file or not gpx_file.exists():
        return []

    try:
        if str(gpx_file).endswith(".gz"):
            with gzip.open(gpx_file, "rt", encoding="utf-8", errors="replace") as f:
                tree = ET.parse(f)
        else:
            with open(gpx_file, "r", encoding="utf-8", errors="replace") as f:
                tree = ET.parse(f)

        root = tree.getroot()
        ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
        pts = root.findall(".//gpx:trkpt", ns)
        if not pts:
            pts = root.findall(".//trkpt")

        splits = []
        current_km = 1
        km_start_time = None
        pts_start_time = None
        cum_dist = 0.0
        last_pt = None
        last_time = None

        for p in pts:
            lat = float(p.attrib["lat"])
            lon = float(p.attrib["lon"])
            t_elem = p.find("gpx:time", ns) if ns else p.find("time")
            if t_elem is None or not t_elem.text:
                continue

            t_str = t_elem.text.replace("Z", "+00:00")
            try:
                t_dt = datetime.fromisoformat(t_str)
            except Exception:
                continue

            if pts_start_time is None:
                pts_start_time = t_dt

            if last_pt is None:
                last_pt = (lat, lon)
                last_time = t_dt
                km_start_time = t_dt
                continue

            d = haversine_distance(last_pt[0], last_pt[1], lat, lon)
            cum_dist += d
            last_pt = (lat, lon)
            last_time = t_dt

            if cum_dist >= current_km * 1000.0:
                split_duration = (t_dt - km_start_time).total_seconds()
                elapsed_dur = (t_dt - pts_start_time).total_seconds()
                splits.append({
                    "split": f"Kilometer {current_km}",
                    "split_km": current_km,
                    "distance": "1.00 km",
                    "duration_sec": split_duration,
                    "split_time_formatted": f"{int(split_duration // 60)}:{int(split_duration % 60):02d}",
                    "pace": format_run_pace(split_duration),
                    "pace_formatted": format_run_pace(split_duration),
                    "elapsed_time_formatted": f"{int(elapsed_dur // 60)}:{int(elapsed_dur % 60):02d}",
                    "elevation_gain_m": 0,
                })
                current_km += 1
                km_start_time = t_dt

        # Remainder segment
        if cum_dist > (current_km - 1) * 1000.0 and km_start_time and last_time and pts_start_time:
            rem_dist = cum_dist - (current_km - 1) * 1000.0
            if rem_dist >= 50.0:  # Only if more than 50 meters
                rem_sec = (last_time - km_start_time).total_seconds()
                elapsed_dur = (last_time - pts_start_time).total_seconds()
                pace_sec = rem_sec / (rem_dist / 1000.0)
                splits.append({
                    "split": f"Final ({rem_dist:.0f}m)",
                    "split_km": current_km,
                    "distance": f"{rem_dist / 1000.0:.2f} km",
                    "duration_sec": rem_sec,
                    "split_time_formatted": f"{int(rem_sec // 60)}:{int(rem_sec % 60):02d}",
                    "pace": format_run_pace(pace_sec),
                    "pace_formatted": format_run_pace(pace_sec),
                    "elapsed_time_formatted": f"{int(elapsed_dur // 60)}:{int(elapsed_dur % 60):02d}",
                    "elevation_gain_m": 0,
                })

        return splits
    except Exception:
        return []


def calculate_running_zones(best_pace_sec_km=550):
    """
    Calculate 5 standard running training pace zones based on athlete's 5K / best pace.
    """
    if not best_pace_sec_km or best_pace_sec_km <= 0:
        best_pace_sec_km = 550  # ~9:10/km default

    # Standard percentage offsets from threshold / 5K pace
    easy_min = best_pace_sec_km * 1.25
    easy_max = best_pace_sec_km * 1.45

    marathon_min = best_pace_sec_km * 1.12
    marathon_max = best_pace_sec_km * 1.25

    tempo_min = best_pace_sec_km * 1.05
    tempo_max = best_pace_sec_km * 1.12

    threshold_min = best_pace_sec_km * 0.98
    threshold_max = best_pace_sec_km * 1.05

    interval_min = best_pace_sec_km * 0.90
    interval_max = best_pace_sec_km * 0.98

    return [
        {
            "Zone": "Zone 1 · Easy / Recovery Run",
            "Pace Range": f"{format_run_pace(easy_min)} – {format_run_pace(easy_max)}",
            "Intensity": "Low Aerobic (65-75% HRmax)",
            "Target Purpose": "Active recovery, fat adaptation, base volume",
        },
        {
            "Zone": "Zone 2 · Aerobic Endurance",
            "Pace Range": f"{format_run_pace(marathon_min)} – {format_run_pace(marathon_max)}",
            "Intensity": "Moderate Aerobic (75-80% HRmax)",
            "Target Purpose": "Long runs, mitochondrial development, aerobic efficiency",
        },
        {
            "Zone": "Zone 3 · Tempo / Marathon Pace",
            "Pace Range": f"{format_run_pace(tempo_min)} – {format_run_pace(tempo_max)}",
            "Intensity": "Lactate Steady State (80-87% HRmax)",
            "Target Purpose": "Sustained rhythm, muscular endurance",
        },
        {
            "Zone": "Zone 4 · Threshold (5K Race Pace)",
            "Pace Range": f"{format_run_pace(threshold_min)} – {format_run_pace(threshold_max)}",
            "Intensity": "Lactate Threshold (88-92% HRmax)",
            "Target Purpose": "Lactate clearance, 5K pace tolerance",
        },
        {
            "Zone": "Zone 5 · VO2 Max / Speed Intervals",
            "Pace Range": f"{format_run_pace(interval_min)} – {format_run_pace(interval_max)}",
            "Intensity": "High Intensity (>93% HRmax)",
            "Target Purpose": "400m-800m repeats, anaerobic power, cadence",
        },
    ]


def get_running_analytics(activities, custom_strava_path=None):
    """
    Extract and compile comprehensive running analytics.
    """
    runs = [a for a in activities if a.get("sport") == "Run"]
    if not runs:
        return {
            "runs": [],
            "total_runs": 0,
            "total_distance_km": 0.0,
            "total_duration_min": 0.0,
            "total_calories": 0.0,
            "total_load": 0.0,
            "best_pace_sec": None,
            "best_pace_formatted": "—",
            "longest_run_km": 0.0,
            "max_hr": None,
            "avg_hr": None,
            "pace_zones": calculate_running_zones(550),
        }

    # Sort descending by date
    runs = sorted(runs, key=lambda r: r.get("date", ""), reverse=True)

    enriched_runs = []
    total_dist = 0.0
    total_dur = 0.0
    total_cal = 0.0
    total_load = 0.0
    hr_list = []
    max_hr_list = []
    paces_sec = []

    for r in runs:
        dist_km = r.get("distance_km") or 0.0
        dur_min = r.get("duration_min") or 0.0
        moving_min = r.get("moving_time_min") or dur_min
        avg_speed = r.get("avg_speed")
        avg_hr = r.get("avg_hr")
        max_hr = r.get("max_hr")
        cal = r.get("calories") or 0.0
        load = r.get("training_load") or 0.0

        total_dist += dist_km
        total_dur += dur_min
        total_cal += cal
        total_load += load

        if avg_hr:
            hr_list.append(avg_hr)
        if max_hr:
            max_hr_list.append(max_hr)

        # Pace calculation (seconds per km)
        if avg_speed and avg_speed > 0:
            sec_km = 1000.0 / avg_speed
        elif dist_km > 0 and moving_min > 0:
            sec_km = (moving_min * 60.0) / dist_km
        else:
            sec_km = None

        if sec_km:
            paces_sec.append(sec_km)

        # Parse GPX splits if available
        filename = r.get("filename")
        splits = parse_gpx_splits(filename, custom_strava_path) if filename else []

        speed_kmh = (avg_speed * 3.6) if avg_speed else ((dist_km / (moving_min / 60.0)) if moving_min > 0 else 0.0)

        run_entry = dict(r)
        run_entry["pace_sec_km"] = sec_km
        run_entry["pace_formatted"] = format_run_pace(sec_km)
        run_entry["speed_kmh"] = round(speed_kmh, 2)
        run_entry["splits"] = splits
        enriched_runs.append(run_entry)

    best_pace_sec = min(paces_sec) if paces_sec else 550
    longest_run = max(r.get("distance_km") or 0.0 for r in runs)
    avg_hr_all = round(sum(hr_list) / len(hr_list), 1) if hr_list else None
    peak_hr_all = max(max_hr_list) if max_hr_list else None

    pace_zones = calculate_running_zones(best_pace_sec)

    return {
        "runs": enriched_runs,
        "total_runs": len(runs),
        "total_distance_km": round(total_dist, 2),
        "total_duration_min": round(total_dur, 1),
        "total_calories": round(total_cal, 0),
        "total_load": round(total_load, 1),
        "best_pace_sec": best_pace_sec,
        "best_pace_formatted": format_run_pace(best_pace_sec),
        "longest_run_km": round(longest_run, 2),
        "max_hr": peak_hr_all,
        "avg_hr": avg_hr_all,
        "pace_zones": pace_zones,
    }

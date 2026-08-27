import csv
import io
import logging
from datetime import datetime, timedelta
from pathlib import Path
import zipfile

logger = logging.getLogger(__name__)

DEFAULT_LOCATIONS = [
    Path(r"C:\Users\ranit\Downloads\export_122045206"),
    Path(r"C:\Users\ranit\Downloads\export_122045206.zip"),
    Path("data/strava"),
    Path("data/strava/activities.csv"),
    Path("data/strava.zip"),
]

DATE_FORMATS = (
    "%b %d, %Y, %I:%M:%S %p",
    "%b %d, %Y, %H:%M:%S",
    "%d %b %Y, %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
)


def find_strava_export_path(custom_path=None):
    """
    Find the Strava export directory or zip file.
    Works seamlessly on Local Windows, Cloud Linux, and nested repositories.
    """
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p

    module_dir = Path(__file__).resolve().parent
    project_dir = module_dir.parent.parent

    candidates = [
        project_dir / "data" / "strava",
        project_dir / "data" / "strava" / "activities.csv",
        project_dir.parent / "data" / "strava",
        project_dir.parent / "fitness-dashboard" / "data" / "strava",
        Path("fitness-dashboard/data/strava"),
        Path("data/strava"),
        Path("data/strava/activities.csv"),
        Path(r"C:\Users\ranit\Downloads\export_122045206"),
        Path(r"C:\Users\ranit\Downloads\export_122045206.zip"),
        Path("data/strava.zip"),
    ]

    for cand in candidates:
        if cand.exists():
            if cand.is_file() and cand.name == "activities.csv":
                return cand.parent
            return cand

    # Try searching in user Downloads for any export_*.zip or export_* folder
    try:
        downloads_dir = Path.home() / "Downloads"
        if downloads_dir.exists():
            for item in downloads_dir.glob("export_*"):
                if item.is_dir() or item.suffix.lower() == ".zip":
                    return item
    except Exception:
        pass

    return None


def parse_strava_date(date_str, timezone_offset_hours=5.5):
    """
    Parse Strava UTC date string and convert to athlete local timezone ISO string.
    Default offset is +5:30 (Asia/Kolkata / IST).
    """
    if not date_str:
        return None
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            local_dt = dt + timedelta(hours=timezone_offset_hours)
            return local_dt.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            pass
    return None


def estimate_training_load(sport, moving_seconds, distance_meters, avg_hr):
    """
    Estimate training load for Strava activities when Relative Effort / ICU load is absent.
    """
    moving_min = (moving_seconds or 0) / 60
    if moving_min <= 0:
        return 0.0

    if avg_hr and avg_hr > 60:
        # HR-based TRIMP approximation
        hr_factor = max(0.4, min(2.0, (avg_hr - 60) / 75.0))
        return round(moving_min * hr_factor, 1)

    if sport == "Swim":
        return round(moving_min * 0.9, 1)
    elif sport == "Run":
        dist_km = (distance_meters or 0) / 1000
        return round(max(moving_min * 1.4, dist_km * 9.5), 1)
    elif sport == "Ride":
        return round(moving_min * 0.6, 1)
    elif sport == "Walk":
        return round(moving_min * 0.35, 1)
    elif sport == "Workout":
        return round(moving_min * 0.7, 1)
    else:
        return round(moving_min * 0.5, 1)


def parse_strava_row(row):
    """
    Parse and normalize a single row from Strava activities.csv.
    """
    raw_date = row.get("Activity Date", "")
    iso_date = parse_strava_date(raw_date)
    if not iso_date:
        return None

    act_id = row.get("Activity ID", "")
    sport = row.get("Activity Type", "Workout")
    name = row.get("Activity Name") or sport
    description = row.get("Activity Description", "")

    # Distance & times
    try:
        distance_m = float(row.get("Distance") or 0)
    except (ValueError, TypeError):
        distance_m = 0.0

    try:
        elapsed_s = float(row.get("Elapsed Time") or 0)
    except (ValueError, TypeError):
        elapsed_s = 0.0

    try:
        moving_s = float(row.get("Moving Time") or 0)
    except (ValueError, TypeError):
        moving_s = elapsed_s

    if moving_s <= 0:
        moving_s = elapsed_s

    # Heart Rate & Relative Effort
    try:
        avg_hr = float(row.get("Average Heart Rate")) if row.get("Average Heart Rate") else None
    except (ValueError, TypeError):
        avg_hr = None

    try:
        max_hr = float(row.get("Max Heart Rate")) if row.get("Max Heart Rate") else None
    except (ValueError, TypeError):
        max_hr = None

    try:
        rel_effort = float(row.get("Relative Effort")) if row.get("Relative Effort") else None
    except (ValueError, TypeError):
        rel_effort = None

    try:
        calories = float(row.get("Calories")) if row.get("Calories") else None
    except (ValueError, TypeError):
        calories = None

    try:
        elev_gain = float(row.get("Elevation Gain")) if row.get("Elevation Gain") else None
    except (ValueError, TypeError):
        elev_gain = None

    try:
        elev_loss = float(row.get("Elevation Loss")) if row.get("Elevation Loss") else None
    except (ValueError, TypeError):
        elev_loss = None

    try:
        avg_speed = float(row.get("Average Speed")) if row.get("Average Speed") else None
    except (ValueError, TypeError):
        avg_speed = None

    try:
        max_speed = float(row.get("Max Speed")) if row.get("Max Speed") else None
    except (ValueError, TypeError):
        max_speed = None

    try:
        avg_cadence = float(row.get("Average Cadence")) if row.get("Average Cadence") else None
    except (ValueError, TypeError):
        avg_cadence = None

    try:
        avg_watts = float(row.get("Average Watts")) if row.get("Average Watts") else None
    except (ValueError, TypeError):
        avg_watts = None

    # Training Load: prioritize Relative Effort, or calculate estimate
    if rel_effort is not None and rel_effort > 0:
        training_load = round(rel_effort, 1)
    else:
        training_load = estimate_training_load(sport, moving_s, distance_m, avg_hr)

    # Swimming specifics
    pool_length_m = None
    lengths = None
    pace = None

    if sport == "Swim":
        try:
            pool_length_m = float(row.get("Pool Length") or 25.0)
        except (ValueError, TypeError):
            pool_length_m = 25.0

        if distance_m > 0 and pool_length_m > 0:
            lengths = int(round(distance_m / pool_length_m))

        if distance_m > 0 and moving_s > 0:
            pace_sec = moving_s / (distance_m / 100.0)
            pace = pace_sec / 100.0  # seconds per meter (normalized format)

    # Media attachments
    media_raw = row.get("Media", "")
    media_list = [m.strip() for m in media_raw.split("|") if m.strip()] if media_raw else []

    # Total Steps
    try:
        total_steps = int(float(row.get("Total Steps"))) if row.get("Total Steps") else None
    except (ValueError, TypeError):
        total_steps = None

    return {
        "id": f"strava_{act_id}",
        "strava_id": act_id,
        "source": "Strava",
        "date": iso_date,
        "sport": sport,
        "name": name,
        "description": description,
        "distance_km": round(distance_m / 1000.0, 2) if distance_m else 0.0,
        "duration_min": round(elapsed_s / 60.0, 1) if elapsed_s else 0.0,
        "moving_time_min": round(moving_s / 60.0, 1) if moving_s else 0.0,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "calories": calories,
        "elevation_m": elev_gain,
        "elevation_loss_m": elev_loss,
        "training_load": training_load,
        "relative_effort": rel_effort,
        "avg_speed": avg_speed,
        "max_speed": max_speed,
        "avg_cadence": avg_cadence,
        "avg_power": avg_watts,
        "pool_length_m": pool_length_m,
        "lengths": lengths,
        "lap_count": lengths,
        "pace": pace,
        "media": media_list,
        "total_steps": total_steps,
        "filename": row.get("Filename", ""),
    }


def load_strava_activities(custom_path=None):
    """
    Load and normalize all activities from the Strava export.
    Supports directory paths and zip files.
    """
    export_path = find_strava_export_path(custom_path)
    if not export_path:
        logger.warning("No Strava export directory or zip found.")
        return []

    activities = []

    try:
        if export_path.is_dir():
            csv_path = export_path / "activities.csv"
            if not csv_path.exists():
                matches = list(export_path.glob("**/activities.csv"))
                if matches:
                    csv_path = matches[0]
                else:
                    logger.warning(f"activities.csv not found inside {export_path}")
                    return []

            with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parsed = parse_strava_row(row)
                    if parsed:
                        activities.append(parsed)

        elif export_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(export_path, "r") as z:
                csv_entry = None
                for name in z.namelist():
                    if name.endswith("activities.csv"):
                        csv_entry = name
                        break

                if not csv_entry:
                    logger.warning(f"activities.csv not found inside zip {export_path}")
                    return []

                with z.open(csv_entry) as zf:
                    text_wrapper = io.TextIOWrapper(zf, encoding="utf-8-sig", errors="replace")
                    reader = csv.DictReader(text_wrapper)
                    for row in reader:
                        parsed = parse_strava_row(row)
                        if parsed:
                            activities.append(parsed)

        logger.info(f"Loaded {len(activities)} activities from Strava export at {export_path}")
    except Exception as e:
        logger.error(f"Error loading Strava activities from {export_path}: {e}")

    activities.sort(key=lambda a: a.get("date", ""), reverse=True)
    return activities


def get_strava_media_path(media_rel_path, custom_path=None):
    """
    Resolve absolute path for a Strava media image.
    """
    if not media_rel_path:
        return None

    export_path = find_strava_export_path(custom_path)
    if export_path and export_path.is_dir():
        cand = export_path / media_rel_path
        if cand.exists():
            return cand

    module_dir = Path(__file__).resolve().parent
    project_dir = module_dir.parent.parent

    for base in [
        project_dir / "data" / "strava",
        project_dir.parent / "fitness-dashboard" / "data" / "strava",
        project_dir.parent / "data" / "strava",
        Path("fitness-dashboard/data/strava"),
        Path("data/strava"),
        Path(r"C:\Users\ranit\Downloads\export_122045206"),
    ]:
        cand = base / media_rel_path
        if cand.exists():
            return cand

    return None

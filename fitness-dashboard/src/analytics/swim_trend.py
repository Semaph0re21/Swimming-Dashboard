from collections import defaultdict
from datetime import datetime


def pace_seconds_per_100m(distance_km, moving_time_min):
    if not distance_km or not moving_time_min:
        return None

    distance_m = distance_km * 1000

    return (
        moving_time_min * 60
    ) / (distance_m / 100)


def week_key(date_string):
    date = datetime.fromisoformat(
        date_string
    ).date()

    year, week, _ = date.isocalendar()

    return f"{year}-W{week:02d}"


def swimming_weekly_trend(activities):

    weekly = defaultdict(
        lambda: {
            "sessions": 0,
            "distance_km": 0,
            "total_time_min": 0,
            "training_load": 0,
            "hr_values": [],
            "pace_values": [],
        }
    )

    for activity in activities:

        if activity["sport"] != "Swim":
            continue

        week = week_key(
            activity["date"]
        )

        data = weekly[week]

        data["sessions"] += 1

        data["distance_km"] += (
            activity["distance_km"] or 0
        )

        data["total_time_min"] += (
            activity["moving_time_min"] or 0
        )

        data["training_load"] += (
            activity["training_load"] or 0
        )

        if activity["avg_hr"]:
            data["hr_values"].append(
                activity["avg_hr"]
            )

        pace = pace_seconds_per_100m(
            activity["distance_km"],
            activity["moving_time_min"]
        )

        if pace:
            data["pace_values"].append(pace)

    results = []

    for week, data in sorted(weekly.items()):

        avg_pace = None

        if data["pace_values"]:
            avg_pace = (
                sum(data["pace_values"])
                / len(data["pace_values"])
            )

        avg_hr = None

        if data["hr_values"]:
            avg_hr = (
                sum(data["hr_values"])
                / len(data["hr_values"])
            )

        results.append({
            "week": week,
            "sessions": data["sessions"],
            "distance_km": round(
                data["distance_km"], 2
            ),
            "time_min": round(
                data["total_time_min"], 1
            ),
            "training_load": round(
                data["training_load"], 1
            ),
            "avg_hr": round(avg_hr, 1)
                if avg_hr else None,
            "avg_pace_seconds": round(
                avg_pace, 1
            ) if avg_pace else None,
        })

    return results
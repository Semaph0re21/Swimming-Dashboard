from datetime import datetime, timedelta
from collections import defaultdict


def parse_date(activity):
    return datetime.fromisoformat(
        activity["date"]
    ).date()


def weekly_summary(activities, end_date):
    end_date = datetime.fromisoformat(
        end_date
    ).date()

    start_date = end_date - timedelta(days=6)

    selected = [
        activity
        for activity in activities
        if start_date
        <= parse_date(activity)
        <= end_date
    ]

    summary = defaultdict(
        lambda: {
            "sessions": 0,
            "distance_km": 0.0,
            "duration_min": 0.0,
            "training_load": 0.0,
        }
    )

    for activity in selected:
        sport = activity["sport"]

        summary[sport]["sessions"] += 1

        summary[sport]["distance_km"] += (
            activity["distance_km"] or 0
        )

        summary[sport]["duration_min"] += (
            activity["duration_min"] or 0
        )

        summary[sport]["training_load"] += (
            activity["training_load"] or 0
        )

    for sport in summary:
        summary[sport]["distance_km"] = round(
            summary[sport]["distance_km"], 2
        )

        summary[sport]["duration_min"] = round(
            summary[sport]["duration_min"], 1
        )

        summary[sport]["training_load"] = round(
            summary[sport]["training_load"], 1
        )

    return dict(summary)
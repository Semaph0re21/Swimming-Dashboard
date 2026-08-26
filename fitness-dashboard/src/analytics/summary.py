from collections import defaultdict


def training_summary(activities):
    summary = defaultdict(lambda: {
        "sessions": 0,
        "distance_km": 0.0,
        "duration_min": 0.0,
        "moving_time_min": 0.0,
        "training_load": 0.0,
        "calories": 0.0,
    })

    for activity in activities:
        sport = activity["sport"]

        summary[sport]["sessions"] += 1

        summary[sport]["distance_km"] += (
            activity["distance_km"] or 0
        )

        summary[sport]["duration_min"] += (
            activity["duration_min"] or 0
        )

        summary[sport]["moving_time_min"] += (
            activity["moving_time_min"] or 0
        )

        summary[sport]["training_load"] += (
            activity["training_load"] or 0
        )

        summary[sport]["calories"] += (
            activity["calories"] or 0
        )

    # Round values
    for sport in summary:
        summary[sport]["distance_km"] = round(
            summary[sport]["distance_km"], 2
        )

        summary[sport]["duration_min"] = round(
            summary[sport]["duration_min"], 1
        )

        summary[sport]["moving_time_min"] = round(
            summary[sport]["moving_time_min"], 1
        )

        summary[sport]["training_load"] = round(
            summary[sport]["training_load"], 1
        )

        summary[sport]["calories"] = round(
            summary[sport]["calories"], 0
        )

    return dict(summary)
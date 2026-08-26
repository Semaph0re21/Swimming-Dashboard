def pace_seconds_per_100m(
    distance_km,
    moving_time_min
):
    if not distance_km or not moving_time_min:
        return None

    distance_m = distance_km * 1000

    return (
        moving_time_min * 60
    ) / (distance_m / 100)


def swim_pace_baseline(activities):
    swims = [
        a for a in activities
        if a["sport"] == "Swim"
    ]

    # Only consider swims of at least 1.5 km
    # for the endurance baseline.
    long_swims = [
        swim
        for swim in swims
        if (swim["distance_km"] or 0) >= 1.5
    ]

    results = []

    for swim in long_swims:

        pace = pace_seconds_per_100m(
            swim["distance_km"],
            swim["moving_time_min"]
        )

        results.append({
            "date": swim["date"],
            "distance_km": swim["distance_km"],
            "pace_seconds": pace,
            "avg_hr": swim["avg_hr"],
            "training_load": swim["training_load"],
        })

    return results
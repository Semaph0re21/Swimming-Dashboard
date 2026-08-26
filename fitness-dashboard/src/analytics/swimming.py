def pace_per_100m(distance_km, moving_time_min):
    if not distance_km or not moving_time_min:
        return None

    distance_m = distance_km * 1000

    # Total seconds required to swim 100m
    seconds_per_100m = (
        moving_time_min * 60
    ) / (distance_m / 100)

    minutes = int(seconds_per_100m // 60)
    seconds = int(round(seconds_per_100m % 60))

    if seconds >= 60:
        minutes += 1
        seconds -= 60

    return f"{minutes}:{seconds:02d} /100m"


def swimming_baseline(activities):
    swims = [
        a for a in activities
        if a["sport"] == "Swim"
    ]

    results = []

    for swim in swims:
        results.append({
            "date": swim["date"],
            "distance_km": swim["distance_km"],
            "moving_time_min": swim["moving_time_min"],
            "avg_hr": swim["avg_hr"],
            "max_hr": swim["max_hr"],
            "training_load": swim["training_load"],
            "pace": pace_per_100m(
                swim["distance_km"],
                swim["moving_time_min"]
            ),
        })

    return results
from datetime import datetime


def days_since_last(activities, sport, today):
    today = datetime.fromisoformat(today).date()

    dates = []

    for activity in activities:
        if activity["sport"] != sport:
            continue

        date = datetime.fromisoformat(
            activity["date"]
        ).date()

        if date <= today:
            dates.append(date)

    if not dates:
        return None

    last_date = max(dates)

    return (today - last_date).days


def training_recommendation(
    activities,
    current_week,
    previous_week,
    today
):
    swim_days = days_since_last(
        activities,
        "Swim",
        today
    )

    ride_days = days_since_last(
        activities,
        "Ride",
        today
    )

    swim_load = current_week.get(
        "Swim",
        {}
    ).get("training_load", 0)

    ride_load = current_week.get(
        "Ride",
        {}
    ).get("training_load", 0)

    previous_swim_load = previous_week.get(
        "Swim",
        {}
    ).get("training_load", 0)

    previous_ride_load = previous_week.get(
        "Ride",
        {}
    ).get("training_load", 0)

    # Basic recovery rule
    total_load = swim_load + ride_load

    if total_load > 250:
        return {
            "sport": "Rest",
            "reason": "Recent training load is high.",
            "intensity": "Easy",
        }

    # Cycling has been absent recently
    if ride_days is None or ride_days >= 4:
        return {
            "sport": "Ride",
            "reason": "Cycling has been absent recently.",
            "intensity": "Easy",
        }

    # Swimming has been absent recently
    if swim_days is None or swim_days >= 4:
        return {
            "sport": "Swim",
            "reason": "Swimming has been absent recently.",
            "intensity": "Easy",
        }

    # Default
    return {
        "sport": "Recovery",
        "reason": "Maintain consistency without adding excessive load.",
        "intensity": "Easy",
    }
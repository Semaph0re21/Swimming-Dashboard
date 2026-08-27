from datetime import datetime


def meters_to_km(distance):
    if distance is None:
        return None
    return round(distance / 1000, 2)


def seconds_to_minutes(seconds):
    if seconds is None:
        return None
    return round(seconds / 60, 1)


def normalize_activity(activity):
    activity_type = activity.get("type")

    result = {
        "id": activity.get("id"),
        "source": activity.get("source"),
        "date": activity.get("start_date_local"),
        "sport": activity_type,
        "name": activity.get("name"),

        "distance_km": meters_to_km(
            activity.get("distance")
        ),

        "duration_min": seconds_to_minutes(
            activity.get("elapsed_time")
        ),

        "moving_time_min": seconds_to_minutes(
            activity.get("moving_time")
        ),

        "avg_hr": activity.get("average_heartrate"),
        "max_hr": activity.get("max_heartrate"),

        "calories": activity.get("calories"),

        "elevation_m": activity.get(
            "total_elevation_gain"
        ),

        "training_load": activity.get(
            "icu_training_load"
        ),

        "hr_load": activity.get("hr_load"),

        "trimp": activity.get("trimp"),

        "intensity": activity.get(
            "icu_intensity"
        ),

        "avg_speed": activity.get(
            "average_speed"
        ),

        "avg_cadence": activity.get(
            "average_cadence"
        ),

        "avg_power": activity.get(
            "icu_average_watts"
        ),
    }

    # Retain optional enriched fields
    if activity.get("description"):
        result["description"] = activity.get("description")
    if activity.get("media"):
        result["media"] = activity.get("media")
    if activity.get("strava_id"):
        result["strava_id"] = activity.get("strava_id")
    if activity.get("relative_effort"):
        result["relative_effort"] = activity.get("relative_effort")
    if activity.get("total_steps"):
        result["total_steps"] = activity.get("total_steps")

    # Swimming-specific data
    if activity_type == "Swim":
        result.update({
            "pool_length_m": activity.get(
                "pool_length"
            ) or activity.get("pool_length_m"),

            "lengths": activity.get(
                "lengths"
            ),

            "lap_count": activity.get(
                "icu_lap_count"
            ) or activity.get("lengths"),

            "pace": activity.get(
                "pace"
            ),

            "interval_summary": activity.get(
                "interval_summary"
            ),
        })

    return result


def normalize_activities(activities):
    return [
        normalize_activity(activity)
        for activity in activities
    ]
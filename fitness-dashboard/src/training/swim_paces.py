def swim_pace_zones(baseline_pace_seconds):
    """
    Create initial personalized swim pace zones.

    baseline_pace_seconds represents sustainable
    endurance pace in seconds per 100m.
    """

    return {
        "easy": {
            "min": baseline_pace_seconds + 15,
            "max": baseline_pace_seconds + 30,
        },

        "endurance": {
            "min": baseline_pace_seconds,
            "max": baseline_pace_seconds + 10,
        },

        "tempo": {
            "min": baseline_pace_seconds - 10,
            "max": baseline_pace_seconds,
        },

        "interval": {
            "min": baseline_pace_seconds - 20,
            "max": baseline_pace_seconds - 10,
        },
    }


def format_pace(seconds):
    minutes = int(seconds // 60)
    secs = int(round(seconds % 60))

    if secs >= 60:
        minutes += 1
        secs -= 60

    return f"{minutes}:{secs:02d}/100m"
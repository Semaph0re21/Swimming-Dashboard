def format_pace(seconds):
    """
    Format seconds per 100m into MM:SS/100m string.
    """
    if not seconds or seconds <= 0:
        return "—"
    try:
        minutes = int(seconds // 60)
        secs = int(round(seconds % 60))

        if secs >= 60:
            minutes += 1
            secs -= 60

        return f"{minutes}:{secs:02d}/100m"
    except Exception:
        return "—"


def swim_pace_zones(baseline_pace_seconds):
    """
    Create comprehensive personalized swim pace zones based on athlete baseline pace.
    baseline_pace_seconds represents sustainable endurance pace in seconds per 100m.
    """
    if not baseline_pace_seconds or baseline_pace_seconds <= 0:
        baseline_pace_seconds = 154  # ~2:34/100m default

    return {
        "easy": {
            "min": baseline_pace_seconds + 15,
            "max": baseline_pace_seconds + 30,
            "formatted": f"{format_pace(baseline_pace_seconds + 15)} – {format_pace(baseline_pace_seconds + 30)}",
            "name": "Zone 1 · Easy / Recovery",
            "purpose": "Warm-up, cool-down, active recovery & drills",
        },
        "endurance": {
            "min": baseline_pace_seconds,
            "max": baseline_pace_seconds + 10,
            "formatted": f"{format_pace(baseline_pace_seconds)} – {format_pace(baseline_pace_seconds + 10)}",
            "name": "Zone 2 · Aerobic Base (Cruise)",
            "purpose": "Aerobic conditioning, long mixed sets (200m-400m)",
        },
        "tempo": {
            "min": baseline_pace_seconds - 10,
            "max": baseline_pace_seconds,
            "formatted": f"{format_pace(baseline_pace_seconds - 10)} – {format_pace(baseline_pace_seconds)}",
            "name": "Zone 3 · Tempo (Lactate Threshold)",
            "purpose": "Sustainable hard pace, stroke efficiency under fatigue",
        },
        "interval": {
            "min": baseline_pace_seconds - 20,
            "max": baseline_pace_seconds - 10,
            "formatted": f"{format_pace(baseline_pace_seconds - 20)} – {format_pace(baseline_pace_seconds - 10)}",
            "name": "Zone 4 · VO2 Max & Speed Intervals",
            "purpose": "100m freestyle speed repeats with rest",
        },
        "sprint": {
            "min": baseline_pace_seconds - 30,
            "max": baseline_pace_seconds - 20,
            "formatted": f"{format_pace(baseline_pace_seconds - 30)} – {format_pace(baseline_pace_seconds - 20)}",
            "name": "Zone 5 · Anaerobic Power / Sprint",
            "purpose": "25m-50m max cadence & explosive push-offs",
        },
    }
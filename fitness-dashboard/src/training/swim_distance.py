def recommended_endurance_distance(
    current_distance_km,
    previous_distance_km
):
    """
    Calculate target endurance distance based on volume ratio.
    """
    current_m = (current_distance_km or 0.0) * 1000
    previous_m = (previous_distance_km or 0.0) * 1000

    if previous_m <= 0:
        return 1500

    volume_ratio = current_m / previous_m

    # Major reduction in swimming volume (< 30%)
    if volume_ratio < 0.30:
        target = 1500

    # Moderate reduction (< 60%)
    elif volume_ratio < 0.60:
        target = 1800

    # Similar or higher volume
    else:
        target = current_m / 3
        # Minimum useful endurance session
        target = max(target, 1500)
        # Ceiling
        target = min(target, 2500)

    # Round to nearest 100m
    target = round(target / 100) * 100
    return int(target)


def recommended_swim_distance(
    workout_type,
    current_distance_km,
    previous_distance_km,
    wellness=None
):
    """
    Intelligently calculate recommended swim distance for any workout type,
    incorporating weekly capacity and Garmin recovery/sleep score.
    """
    base_endurance = recommended_endurance_distance(current_distance_km, previous_distance_km)

    # Scale factor based on Garmin Sleep / Recovery if available
    sleep_score = (wellness or {}).get("sleepScore") if isinstance(wellness, dict) else None
    modifier = 1.0
    if sleep_score is not None:
        if sleep_score < 55:
            modifier = 0.85  # Reduce volume slightly if sleep/recovery is poor
        elif sleep_score >= 80:
            modifier = 1.10  # Optimal recovery green light

    if workout_type == "Endurance":
        dist = base_endurance * modifier
        dist = max(1400, min(3000, dist))
    elif workout_type == "Tempo":
        dist = max(1500, min(2400, (base_endurance * 0.95) * modifier))
    elif workout_type == "Intervals":
        dist = max(1400, min(2000, (base_endurance * 0.85) * modifier))
    elif workout_type == "Recovery":
        dist = max(1000, min(1400, base_endurance * 0.65))
    elif workout_type == "Pyramid":
        dist = max(1600, min(2200, (base_endurance * 0.90) * modifier))
    else:
        dist = base_endurance

    return int(round(dist / 100) * 100)
def recommended_endurance_distance(
    current_distance_km,
    previous_distance_km
):
    current_m = current_distance_km * 1000
    previous_m = previous_distance_km * 1000

    if previous_m <= 0:
        return 1500

    volume_ratio = current_m / previous_m

    # Major reduction in swimming volume.
    if volume_ratio < 0.30:
        target = 1500

    # Moderate reduction.
    elif volume_ratio < 0.60:
        target = 1800

    # Similar or higher volume.
    else:
        target = current_m / 3

        # Minimum useful endurance session.
        target = max(target, 1500)

        # Don't exceed a reasonable first-version ceiling.
        target = min(target, 2500)

    # Round to nearest 100m.
    target = round(target / 100) * 100

    return int(target)
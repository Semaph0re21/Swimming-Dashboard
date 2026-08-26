def choose_swim_workout(
    current_week,
    previous_week,
    days_since_swim,
):
    current_swim = current_week.get(
        "Swim",
        {}
    )

    previous_swim = previous_week.get(
        "Swim",
        {}
    )

    current_load = current_swim.get(
        "training_load", 0
    )

    current_distance = current_swim.get(
        "distance_km", 0
    )

    previous_distance = previous_swim.get(
        "distance_km", 0
    )

    # High recent load → recovery
    if current_load >= 150:
        return "Recovery"

    # Long gap → rebuild endurance
    if days_since_swim is None or days_since_swim >= 4:
        return "Endurance"

    # Significant reduction in volume
    if previous_distance > 0:
        volume_ratio = (
            current_distance /
            previous_distance
        )

        if volume_ratio < 0.5:
            return "Endurance"

    # Moderate load + regular swimming
    if current_load < 100:
        return "Tempo"

    return "Endurance"
from datetime import date
import uuid

from src.training.swim_decision import (
    choose_swim_workout,
    evaluate_swim_coach,
)
from src.training.swim_distance import (
    recommended_swim_distance,
    recommended_endurance_distance,
)
from src.training.swim_workouts import (
    endurance_workout,
    tempo_workout,
    interval_workout,
    recovery_workout,
    pyramid_workout,
)
from src.training.swim_paces import (
    swim_pace_zones,
)


def calculate_baseline(long_swims):
    """
    Calculate average pace in seconds per 100m from long endurance swims.
    """
    if not long_swims:
        return 154.0

    pace_values = [
        swim["pace_seconds"]
        for swim in long_swims
        if swim.get("pace_seconds") is not None and swim.get("pace_seconds") > 0
    ]

    if not pace_values:
        return 154.0

    return sum(pace_values) / len(pace_values)


def generate_swim_plan(
    current_week,
    previous_week,
    days_since_swim,
    long_swims,
    target_date=None,
    target_distance=None,
    target_type=None,
    wellness=None,
):
    """
    Generate an intelligent, personalized, and periodized swim plan.
    """
    coach_eval = evaluate_swim_coach(
        current_week,
        previous_week,
        days_since_swim,
        wellness=wellness,
    )

    workout_type = target_type or coach_eval["workout_type"]
    rationale = coach_eval["coaching_rationale"]
    readiness_score = coach_eval["readiness_score"]

    current_swim = current_week.get("Swim", {}) if isinstance(current_week, dict) else {}
    previous_swim = previous_week.get("Swim", {}) if isinstance(previous_week, dict) else {}

    current_distance = current_swim.get("distance_km", 0) or 0
    previous_distance = previous_swim.get("distance_km", 0) or 0

    baseline = calculate_baseline(long_swims)
    zones = swim_pace_zones(baseline)

    if target_distance is None:
        target_distance = recommended_swim_distance(
            workout_type,
            current_distance,
            previous_distance,
            wellness=wellness,
        )

    # Build dynamically scaled workout with athlete's exact pace zones
    if workout_type == "Endurance":
        workout = endurance_workout(
            target_distance=target_distance,
            easy_min=zones["easy"]["min"],
            easy_max=zones["easy"]["max"],
            endurance_min=zones["endurance"]["min"],
            endurance_max=zones["endurance"]["max"],
        )
    elif workout_type == "Tempo":
        workout = tempo_workout(
            target_distance=target_distance,
            easy_min=zones["easy"]["min"],
            easy_max=zones["easy"]["max"],
            tempo_min=zones["tempo"]["min"],
            tempo_max=zones["tempo"]["max"],
        )
    elif workout_type == "Intervals":
        workout = interval_workout(
            target_distance=target_distance,
            easy_min=zones["easy"]["min"],
            easy_max=zones["easy"]["max"],
            interval_min=zones["interval"]["min"],
            interval_max=zones["interval"]["max"],
        )
    elif workout_type == "Pyramid":
        workout = pyramid_workout(
            target_distance=target_distance,
            easy_min=zones["easy"]["min"],
            easy_max=zones["easy"]["max"],
            tempo_min=zones["tempo"]["min"],
            tempo_max=zones["tempo"]["max"],
            interval_min=zones["interval"]["min"],
            interval_max=zones["interval"]["max"],
        )
    else:  # Recovery / default
        workout = recovery_workout(
            target_distance=target_distance,
            easy_min=zones["easy"]["min"],
            easy_max=zones["easy"]["max"],
        )

    workout["plan_id"] = str(uuid.uuid4())
    workout["planned_date"] = str(target_date or date.today())
    workout["coaching_rationale"] = rationale
    workout["readiness_score"] = readiness_score
    workout["baseline_pace"] = round(baseline, 1)

    return workout
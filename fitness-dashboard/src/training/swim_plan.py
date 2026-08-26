from datetime import date
import uuid

from src.training.swim_decision import choose_swim_workout
from src.training.swim_distance import (
    recommended_endurance_distance
)
from src.training.swim_workouts import (
    endurance_workout,
    tempo_workout,
    interval_workout,
    recovery_workout,
)
from src.training.swim_paces import (
    swim_pace_zones,
)


def calculate_baseline(long_swims):
    pace_values = [
        swim["pace_seconds"]
        for swim in long_swims
        if swim["pace_seconds"] is not None
    ]

    if not pace_values:
        return 154

    return sum(pace_values) / len(pace_values)


def generate_swim_plan(
    current_week,
    previous_week,
    days_since_swim,
    long_swims,
):
    workout_type = choose_swim_workout(
        current_week,
        previous_week,
        days_since_swim,
    )

    current_swim = current_week.get(
        "Swim",
        {}
    )

    previous_swim = previous_week.get(
        "Swim",
        {}
    )

    current_distance = current_swim.get(
        "distance_km",
        0
    )

    previous_distance = previous_swim.get(
        "distance_km",
        0
    )

    baseline = calculate_baseline(
        long_swims
    )

    zones = swim_pace_zones(
        baseline
    )

    if workout_type == "Endurance":

        target_distance = (
            recommended_endurance_distance(
                current_distance,
                previous_distance,
            )
        )

        workout = endurance_workout(
            target_distance=target_distance,
            easy_min=zones["easy"]["min"],
            easy_max=zones["easy"]["max"],
            endurance_min=zones["endurance"]["min"],
            endurance_max=zones["endurance"]["max"],
        )

    elif workout_type == "Tempo":

        workout = tempo_workout()

    elif workout_type == "Intervals":

        workout = interval_workout()

    else:

        workout = recovery_workout()

    workout["plan_id"] = str(uuid.uuid4())

    workout["planned_date"] = str(
        date.today()
    )

    return workout
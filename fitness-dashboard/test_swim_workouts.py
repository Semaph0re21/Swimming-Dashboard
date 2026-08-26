from src.training.swim_workouts import (
    endurance_workout,
    tempo_workout,
    interval_workout,
    recovery_workout,
)


workouts = [
    endurance_workout(2000),
    tempo_workout(),
    interval_workout(),
    recovery_workout(),
]


for workout in workouts:

    print("\n==============================")
    print(workout["type"])
    print("==============================")

    print(
        "Distance:",
        workout["target_distance"],
        "m"
    )

    print(
        "Duration:",
        workout["duration"]
    )

    print("\nSets:")

    for item in workout["sets"]:
        print(" -", item)

    print(
        "\nGoal:",
        workout["goal"]
    )

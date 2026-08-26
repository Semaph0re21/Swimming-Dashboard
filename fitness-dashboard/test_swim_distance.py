from src.training.swim_distance import (
    recommended_endurance_distance
)


tests = [
    (1.92, 10.34),
    (5.0, 6.0),
    (7.0, 7.5),
    (0, 5.0),
]


for current, previous in tests:

    target = recommended_endurance_distance(
        current,
        previous
    )

    print(
        f"Current: {current} km | "
        f"Previous: {previous} km | "
        f"Target: {target}m"
    )
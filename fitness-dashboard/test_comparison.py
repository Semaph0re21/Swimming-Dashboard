from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.weekly import weekly_summary

activities = get_activities(
    "2026-08-14",
    "2026-08-27"
)

clean_activities = normalize_activities(
    activities
)

current = weekly_summary(
    clean_activities,
    "2026-08-27"
)

previous = weekly_summary(
    clean_activities,
    "2026-08-20"
)

sports = set(current) | set(previous)

print("\n===== 7-DAY COMPARISON =====\n")

for sport in sorted(sports):

    current_data = current.get(
        sport,
        {
            "sessions": 0,
            "distance_km": 0,
            "duration_min": 0,
            "training_load": 0,
        }
    )

    previous_data = previous.get(
        sport,
        {
            "sessions": 0,
            "distance_km": 0,
            "duration_min": 0,
            "training_load": 0,
        }
    )

    print(sport)

    print(
        f"  Current:  "
        f"{current_data['sessions']} sessions | "
        f"{current_data['distance_km']} km | "
        f"load {current_data['training_load']}"
    )

    print(
        f"  Previous: "
        f"{previous_data['sessions']} sessions | "
        f"{previous_data['distance_km']} km | "
        f"load {previous_data['training_load']}"
    )

    print()
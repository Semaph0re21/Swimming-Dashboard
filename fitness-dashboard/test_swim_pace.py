from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.swim_pace import swim_pace_baseline


activities = get_activities(
    "2026-07-01",
    "2026-08-27"
)

clean_activities = normalize_activities(
    activities
)

results = swim_pace_baseline(
    clean_activities
)

print("\n===== LONG-SWIM PACE BASELINE =====\n")

for swim in results:

    pace = swim["pace_seconds"]

    minutes = int(pace // 60)
    seconds = int(round(pace % 60))

    print(
        swim["date"],
        "|",
        swim["distance_km"],
        "km",
        "|",
        f"{minutes}:{seconds:02d} /100m",
        "| HR:",
        swim["avg_hr"],
        "| Load:",
        swim["training_load"],
    )
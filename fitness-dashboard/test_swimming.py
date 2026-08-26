from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.swimming import swimming_baseline

activities = get_activities(
    "2026-01-01",
    "2026-08-27"
)

clean_activities = normalize_activities(
    activities
)

swims = swimming_baseline(
    clean_activities
)

print("\n===== SWIMMING BASELINE =====\n")

for swim in swims:
    print(
        swim["date"],
        "|",
        swim["distance_km"], "km",
        "|",
        swim["moving_time_min"], "min",
        "| HR:", swim["avg_hr"],
        "| Load:", swim["training_load"],
        "| Pace:", swim["pace"]
    )
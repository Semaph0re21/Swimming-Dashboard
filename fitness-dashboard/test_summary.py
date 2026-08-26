from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.summary import training_summary

activities = get_activities(
    "2026-01-01",
    "2026-08-27"
)

clean_activities = normalize_activities(
    activities
)

summary = training_summary(
    clean_activities
)

print("\n===== TRAINING SUMMARY =====\n")

for sport, data in summary.items():

    print(sport)

    for metric, value in data.items():
        print(f"  {metric}: {value}")

    print()
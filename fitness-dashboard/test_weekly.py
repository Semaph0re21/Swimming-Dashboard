from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.weekly import weekly_summary

activities = get_activities(
    "2026-08-01",
    "2026-08-27"
)

clean_activities = normalize_activities(
    activities
)

print("\n===== LAST 7 DAYS =====\n")

summary = weekly_summary(
    clean_activities,
    "2026-08-27"
)

for sport, data in summary.items():
    print(sport)

    for metric, value in data.items():
        print(f"  {metric}: {value}")

    print()
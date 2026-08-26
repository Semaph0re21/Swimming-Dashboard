from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.swim_trend import swimming_weekly_trend


activities = get_activities(
    "2026-07-01",
    "2026-08-27"
)

clean_activities = normalize_activities(
    activities
)

trend = swimming_weekly_trend(
    clean_activities
)

print("\n===== SWIMMING TREND =====\n")

for week in trend:
    print(week)
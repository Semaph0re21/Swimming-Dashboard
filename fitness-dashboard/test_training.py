from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.weekly import weekly_summary
from src.training.decision import training_recommendation


activities = get_activities(
    "2026-08-14",
    "2026-08-27"
)

clean_activities = normalize_activities(
    activities
)


current_week = weekly_summary(
    clean_activities,
    "2026-08-27"
)

previous_week = weekly_summary(
    clean_activities,
    "2026-08-20"
)


recommendation = training_recommendation(
    clean_activities,
    current_week,
    previous_week,
    "2026-08-27"
)


print("\n===== TOMORROW'S RECOMMENDATION =====\n")

print("Sport:", recommendation["sport"])
print("Intensity:", recommendation["intensity"])
print("Reason:", recommendation["reason"])

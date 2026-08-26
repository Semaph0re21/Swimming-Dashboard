from datetime import datetime

from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.weekly import weekly_summary
from src.training.swim_decision import choose_swim_workout


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


today = datetime.fromisoformat(
    "2026-08-27"
).date()


swim_dates = [
    datetime.fromisoformat(
        a["date"]
    ).date()

    for a in clean_activities

    if a["sport"] == "Swim"
]


last_swim = max(
    d for d in swim_dates
    if d <= today
)


days_since_swim = (
    today - last_swim
).days


recommendation = choose_swim_workout(
    current_week,
    previous_week,
    days_since_swim
)


current_swim = current_week.get(
    "Swim",
    {}
)

previous_swim = previous_week.get(
    "Swim",
    {}
)


print("\n===== SWIM TRAINING ANALYSIS =====\n")

print("CURRENT 7 DAYS")
print("----------------")
print(
    "Sessions:",
    current_swim.get("sessions", 0)
)

print(
    "Distance:",
    current_swim.get("distance_km", 0),
    "km"
)

print(
    "Duration:",
    current_swim.get("duration_min", 0),
    "min"
)

print(
    "Training load:",
    current_swim.get("training_load", 0)
)


print("\nPREVIOUS 7 DAYS")
print("----------------")
print(
    "Sessions:",
    previous_swim.get("sessions", 0)
)

print(
    "Distance:",
    previous_swim.get("distance_km", 0),
    "km"
)

print(
    "Duration:",
    previous_swim.get("duration_min", 0),
    "min"
)

print(
    "Training load:",
    previous_swim.get("training_load", 0)
)


print("\nRECOVERY / CONSISTENCY")
print("----------------")
print(
    "Days since last swim:",
    days_since_swim
)


print("\nRECOMMENDATION")
print("----------------")
print(
    "Workout:",
    recommendation
)
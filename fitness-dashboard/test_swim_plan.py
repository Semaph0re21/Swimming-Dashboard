from datetime import datetime

from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.weekly import weekly_summary
from src.training.swim_plan import generate_swim_plan
from src.analytics.swim_pace import swim_pace_baseline
from src.training.plan_store import save_plan


# Get recent activity data
activities = get_activities(
    "2026-08-14",
    "2026-08-27"
)

# Normalize the data
clean_activities = normalize_activities(
    activities
)
long_swims = swim_pace_baseline(
    clean_activities
)


# Current and previous 7-day periods
current_week = weekly_summary(
    clean_activities,
    "2026-08-27"
)

previous_week = weekly_summary(
    clean_activities,
    "2026-08-20"
)


# Find the last swim
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


# Generate complete workout
workout = generate_swim_plan(
    current_week,
    previous_week,
    days_since_swim,
    long_swims
)
save_plan(workout)

print("\n================================")
print("      TOMORROW'S SWIM PLAN")
print("================================\n")

print("Workout:", workout["type"])
print(
    "Distance:",
    workout["target_distance"],
    "m"
)
print("Duration:", workout["duration"])

print("\nSets:")

for item in workout["sets"]:
    print(" -", item)

print("\nGoal:")
print(workout["goal"])

print("\n================================")
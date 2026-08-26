from src.api.intervals import get_activities, get_wellness

activities = get_activities("2026-01-01", "2026-08-27")
wellness = get_wellness("2026-08-01", "2026-08-27")

print("Activities:", len(activities))
print("Wellness records:", len(wellness))

print("\nRecent activities:")

for activity in activities[:5]:
    print(
        activity.get("start_date_local"),
        "|",
        activity.get("type"),
        "|",
        activity.get("name"),
        "|",
        activity.get("distance"),
    )
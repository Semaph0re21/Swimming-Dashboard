from src.api.intervals import get_activities
from src.data.activities import normalize_activities

activities = get_activities("2026-01-01", "2026-08-27")

clean_activities = normalize_activities(activities)

print("Total activities:", len(clean_activities))

print("\nFirst 5 normalized activities:")

for activity in clean_activities[:5]:
    print(activity)

print("\nSport totals:")

sports = {}

for activity in clean_activities:
    sport = activity["sport"]
    sports[sport] = sports.get(sport, 0) + 1

for sport, count in sports.items():
    print(f"{sport}: {count}")
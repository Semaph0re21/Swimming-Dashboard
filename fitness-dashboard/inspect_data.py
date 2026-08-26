import json

with open("activities_raw.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

print("Total activities:", len(activities))

if activities:
    print("\nAvailable fields in first activity:")
    for key in sorted(activities[0].keys()):
        print("-", key)

    print("\nActivity types:")
    types = sorted(set(a.get("type", "Unknown") for a in activities))
    for activity_type in types:
        print("-", activity_type)
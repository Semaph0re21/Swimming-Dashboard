from src.data.dashboard import get_dashboard_data


data = get_dashboard_data(
    "2026-07-01",
    "2026-08-27"
)


print("\n===== DASHBOARD DATA TEST =====\n")

print(
    "Activities:",
    len(data["activities"])
)

print(
    "Days since swim:",
    data["days_since_swim"]
)


print("\nCURRENT WEEK")

for sport, values in data["current_week"].items():
    print(
        sport,
        values
    )


print("\nPREVIOUS WEEK")

for sport, values in data["previous_week"].items():
    print(
        sport,
        values
    )


print("\nNEXT SWIM PLAN")

plan = data["next_swim_plan"]

print(
    "Type:",
    plan["type"]
)

print(
    "Distance:",
    plan["target_distance"],
    "m"
)

print(
    "Duration:",
    plan["duration"]
)

print("Sets:")

for item in plan["sets"]:
    print(" -", item)
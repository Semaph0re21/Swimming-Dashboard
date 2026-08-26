import json

with open("activities_raw.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

swims = [a for a in activities if a.get("type") == "Swim"]

print("Total swims:", len(swims))

if swims:
    swim = swims[0]

    print("\nLatest/first swim:")
    print("Name:", swim.get("name"))
    print("Date:", swim.get("start_date_local"))
    print("Distance:", swim.get("distance"))
    print("Moving time:", swim.get("moving_time"))
    print("Elapsed time:", swim.get("elapsed_time"))
    print("Pool length:", swim.get("pool_length"))
    print("Average HR:", swim.get("average_heartrate"))
    print("Max HR:", swim.get("max_heartrate"))
    print("Calories:", swim.get("calories"))
    print("Training load:", swim.get("icu_training_load"))
    print("HR load:", swim.get("hr_load"))
    print("Pace:", swim.get("pace"))
    print("Lap count:", swim.get("icu_lap_count"))
    print("Lengths:", swim.get("lengths"))

    print("\nStream types:")
    print(swim.get("stream_types"))

    print("\nInterval summary:")
    print(swim.get("interval_summary"))
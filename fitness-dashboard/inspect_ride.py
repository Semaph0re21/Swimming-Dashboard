import json

with open("activities_raw.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

rides = [a for a in activities if a.get("type") == "Ride"]

print("Total rides:", len(rides))

if rides:
    ride = rides[0]

    print("\nLatest/first ride:")
    print("Name:", ride.get("name"))
    print("Date:", ride.get("start_date_local"))
    print("Distance:", ride.get("distance"))
    print("Moving time:", ride.get("moving_time"))
    print("Elapsed time:", ride.get("elapsed_time"))
    print("Average HR:", ride.get("average_heartrate"))
    print("Max HR:", ride.get("max_heartrate"))
    print("Average speed:", ride.get("average_speed"))
    print("Max speed:", ride.get("max_speed"))
    print("Average cadence:", ride.get("average_cadence"))
    print("Average power:", ride.get("icu_average_watts"))
    print("Weighted power:", ride.get("icu_weighted_avg_watts"))
    print("Elevation:", ride.get("total_elevation_gain"))
    print("Calories:", ride.get("calories"))
    print("Training load:", ride.get("icu_training_load"))
    print("HR load:", ride.get("hr_load"))
    print("Power load:", ride.get("power_load"))
    print("TRIMP:", ride.get("trimp"))
    print("Intensity:", ride.get("icu_intensity"))
    print("Variability index:", ride.get("icu_variability_index"))

    print("\nStream types:")
    print(ride.get("stream_types"))
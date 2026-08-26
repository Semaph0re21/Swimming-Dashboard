from src.api.intervals import get_activities
from src.data.activities import normalize_activities
from src.analytics.swim_pace import swim_pace_baseline
from src.training.swim_paces import (
    swim_pace_zones,
    format_pace,
)


activities = get_activities(
    "2026-07-01",
    "2026-08-27"
)

clean_activities = normalize_activities(
    activities
)

long_swims = swim_pace_baseline(
    clean_activities
)


pace_values = [
    swim["pace_seconds"]
    for swim in long_swims
    if swim["pace_seconds"] is not None
]


baseline = sum(pace_values) / len(pace_values)

zones = swim_pace_zones(
    baseline
)


print("\n===== PERSONAL SWIM PACE ZONES =====\n")

print(
    "Baseline:",
    format_pace(baseline)
)

for zone, values in zones.items():

    print(
        f"{zone.capitalize():10}",
        format_pace(values["min"]),
        "-",
        format_pace(values["max"])
    )
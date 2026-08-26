import json
from pathlib import Path


PLAN_FILE = Path("training_plans.json")


def save_plan(plan):
    plans = []

    if PLAN_FILE.exists():
        with open(
            PLAN_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            plans = json.load(f)

    plans.append(plan)

    with open(
        PLAN_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            plans,
            f,
            indent=2
        )


def get_plans():
    if not PLAN_FILE.exists():
        return []

    with open(
        PLAN_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)
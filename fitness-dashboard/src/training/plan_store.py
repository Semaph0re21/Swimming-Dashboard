import json
from pathlib import Path

PLAN_FILE = Path("training_plans.json")


def save_plan(plan):
    plans = get_plans()
    plans.append(plan)
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plans, f, indent=2)


def get_plans():
    if not PLAN_FILE.exists():
        return []
    try:
        with open(PLAN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def delete_plan(plan_id):
    """Delete a plan by plan_id."""
    plans = get_plans()
    new_plans = [p for p in plans if p.get("plan_id") != plan_id]
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(new_plans, f, indent=2)
    return len(new_plans) < len(plans)


def clear_plans():
    """Clear all saved plans."""
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)
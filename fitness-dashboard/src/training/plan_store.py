import json
import uuid
from pathlib import Path

_base_dir = Path(__file__).resolve().parent.parent.parent
PLAN_FILE = _base_dir / "training_plans.json"


def save_plan(plan, target_date=None):
    plans = get_plans()
    if target_date and "planned_date" not in plan:
        plan["planned_date"] = str(target_date)
    if "plan_id" not in plan and "id" not in plan:
        plan["plan_id"] = str(uuid.uuid4())
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
    """Delete a plan by plan_id or id."""
    plans = get_plans()
    new_plans = [p for p in plans if p.get("plan_id") != plan_id and p.get("id") != plan_id]
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(new_plans, f, indent=2)
    return len(new_plans) < len(plans)


def clear_plans():
    """Clear all saved plans."""
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)
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
            data = json.load(f)
            changed = False
            for p in data:
                if not p.get("plan_id") and not p.get("id"):
                    p["plan_id"] = str(uuid.uuid4())
                    changed = True
            if changed:
                with open(PLAN_FILE, "w", encoding="utf-8") as fw:
                    json.dump(data, fw, indent=2)
            return data
    except Exception:
        return []


def delete_plan(plan_id):
    """Delete a single plan by plan_id or id."""
    if not plan_id:
        return False
    plans = get_plans()
    new_plans = [p for p in plans if str(p.get("plan_id")) != str(plan_id) and str(p.get("id")) != str(plan_id)]
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(new_plans, f, indent=2)
    return len(new_plans) < len(plans)


def delete_plans_by_date(date_str):
    """Delete all plans planned for a specific date."""
    if not date_str:
        return False
    plans = get_plans()
    new_plans = [
        p for p in plans
        if (p.get("planned_date") != date_str and (p.get("created_at") or "")[:10] != date_str)
    ]
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(new_plans, f, indent=2)
    return len(new_plans) < len(plans)


def clear_plans():
    """Clear all saved plans."""
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)
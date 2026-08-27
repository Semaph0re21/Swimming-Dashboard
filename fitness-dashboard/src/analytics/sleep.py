"""
Sleep and recovery analytics from Garmin wellness records.
"""
from datetime import datetime, timedelta


def format_sleep_duration(seconds):
    """Format sleep seconds into 'Xh Ym'."""
    if not seconds or seconds <= 0:
        return "N/A"
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    return f"{hrs}h {mins:02d}m"


def get_sleep_analytics(wellness_records, start_date=None, end_date=None):
    """
    Compute comprehensive sleep, HRV, and recovery analytics from wellness data.
    """
    if not wellness_records:
        return {
            "records": [],
            "total_days_tracked": 0,
            "avg_duration_formatted": "N/A",
            "avg_duration_hours": None,
            "avg_sleep_score": None,
            "avg_hrv": None,
            "avg_resting_hr": None,
            "latest_record": None,
            "duration_vs_prev_min": None,
            "score_vs_prev": None,
            "daily_trends": [],
        }

    # Filter by date window if specified
    filtered = []
    for w in wellness_records:
        w_date_str = w.get("id") or w.get("date")
        if not w_date_str:
            continue
        try:
            w_date = datetime.fromisoformat(str(w_date_str)[:10]).date()
            if start_date and w_date < datetime.fromisoformat(str(start_date)[:10]).date():
                continue
            if end_date and w_date > datetime.fromisoformat(str(end_date)[:10]).date():
                continue
            filtered.append(w)
        except Exception:
            pass

    if not filtered:
        filtered = list(wellness_records)

    filtered.sort(key=lambda w: str(w.get("id") or w.get("date") or ""))

    # Process daily metrics
    daily_trends = []
    valid_durations = []
    valid_scores = []
    valid_hrvs = []
    valid_rhrs = []

    for w in filtered:
        d_str = str(w.get("id") or w.get("date") or "")[:10]
        s_secs = w.get("sleepSecs")
        s_score = w.get("sleepScore")
        s_hrv = w.get("hrv")
        s_rhr = w.get("restingHR")
        s_qual = w.get("sleepQuality")
        s_readiness = w.get("readiness")
        steps = w.get("steps")

        dur_hrs = round(s_secs / 3600, 2) if s_secs and s_secs > 0 else None
        if dur_hrs:
            valid_durations.append(s_secs)
        if s_score is not None and s_score > 0:
            valid_scores.append(s_score)
        if s_hrv is not None and s_hrv > 0:
            valid_hrvs.append(s_hrv)
        if s_rhr is not None and s_rhr > 0:
            valid_rhrs.append(s_rhr)

        daily_trends.append({
            "date": d_str,
            "sleep_secs": s_secs,
            "duration_hours": dur_hrs,
            "duration_formatted": format_sleep_duration(s_secs),
            "score": s_score,
            "hrv": s_hrv,
            "resting_hr": s_rhr,
            "quality": s_qual,
            "readiness": s_readiness,
            "steps": steps,
        })

    total_days = len([d for d in daily_trends if d["duration_hours"]])
    avg_secs = sum(valid_durations) / len(valid_durations) if valid_durations else None
    avg_hrs = round(avg_secs / 3600, 2) if avg_secs else None
    avg_fmt = format_sleep_duration(avg_secs) if avg_secs else "N/A"
    avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else None
    avg_hrv = round(sum(valid_hrvs) / len(valid_hrvs), 1) if valid_hrvs else None
    avg_rhr = round(sum(valid_rhrs) / len(valid_rhrs), 1) if valid_rhrs else None

    # Comparison: Split into two halves if sufficient data
    dur_diff_min = None
    score_diff = None
    if len(valid_durations) >= 4:
        half = len(valid_durations) // 2
        prev_dur = sum(valid_durations[:half]) / half
        curr_dur = sum(valid_durations[half:]) / (len(valid_durations) - half)
        dur_diff_min = round((curr_dur - prev_dur) / 60)

    if len(valid_scores) >= 4:
        half_s = len(valid_scores) // 2
        prev_s = sum(valid_scores[:half_s]) / half_s
        curr_s = sum(valid_scores[half_s:]) / (len(valid_scores) - half_s)
        score_diff = round(curr_s - prev_s, 1)

    latest = daily_trends[-1] if daily_trends else None

    return {
        "records": daily_trends,
        "total_days_tracked": total_days,
        "avg_duration_formatted": avg_fmt,
        "avg_duration_hours": avg_hrs,
        "avg_sleep_score": avg_score,
        "avg_hrv": avg_hrv,
        "avg_resting_hr": avg_rhr,
        "latest_record": latest,
        "duration_vs_prev_min": dur_diff_min,
        "score_vs_prev": score_diff,
        "daily_trends": daily_trends,
    }

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
    Compute comprehensive sleep, HRV, and recovery analytics from wellness data,
    including Garmin sleep stage architecture (Deep, Light, REM).
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
            "avg_deep_hours": None,
            "avg_light_hours": None,
            "avg_rem_hours": None,
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
    valid_deep_secs = []
    valid_light_secs = []
    valid_rem_secs = []

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
        
        deep_secs = None
        light_secs = None
        rem_secs = None
        deep_hrs = None
        light_hrs = None
        rem_hrs = None
        deep_pct = None
        light_pct = None
        rem_pct = None

        if s_secs and s_secs > 0:
            valid_durations.append(s_secs)

            # Garmin sleep stage architecture calculation
            if w.get("deepSleepSecs") is not None:
                deep_secs = w.get("deepSleepSecs")
            else:
                score_factor = (s_score - 50) / 50 if s_score is not None else 0.0
                deep_ratio = max(0.15, min(0.24, 0.19 + 0.05 * score_factor))
                deep_secs = round(s_secs * deep_ratio)

            if w.get("remSleepSecs") is not None:
                rem_secs = w.get("remSleepSecs")
            else:
                score_factor = (s_score - 50) / 50 if s_score is not None else 0.0
                rem_ratio = max(0.18, min(0.26, 0.22 + 0.04 * score_factor))
                rem_secs = round(s_secs * rem_ratio)

            if w.get("lightSleepSecs") is not None:
                light_secs = w.get("lightSleepSecs")
            else:
                light_secs = max(0, s_secs - deep_secs - rem_secs)

            deep_hrs = round(deep_secs / 3600, 2)
            light_hrs = round(light_secs / 3600, 2)
            rem_hrs = round(rem_secs / 3600, 2)

            deep_pct = round((deep_secs / s_secs) * 100, 1)
            rem_pct = round((rem_secs / s_secs) * 100, 1)
            light_pct = round((light_secs / s_secs) * 100, 1)

            valid_deep_secs.append(deep_secs)
            valid_light_secs.append(light_secs)
            valid_rem_secs.append(rem_secs)

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
            "deep_secs": deep_secs,
            "deep_hours": deep_hrs,
            "deep_formatted": format_sleep_duration(deep_secs),
            "deep_pct": deep_pct,
            "light_secs": light_secs,
            "light_hours": light_hrs,
            "light_formatted": format_sleep_duration(light_secs),
            "light_pct": light_pct,
            "rem_secs": rem_secs,
            "rem_hours": rem_hrs,
            "rem_formatted": format_sleep_duration(rem_secs),
            "rem_pct": rem_pct,
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

    avg_deep_hrs = round(sum(valid_deep_secs) / len(valid_deep_secs) / 3600, 2) if valid_deep_secs else None
    avg_light_hrs = round(sum(valid_light_secs) / len(valid_light_secs) / 3600, 2) if valid_light_secs else None
    avg_rem_hrs = round(sum(valid_rem_secs) / len(valid_rem_secs) / 3600, 2) if valid_rem_secs else None

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
        "avg_deep_hours": avg_deep_hrs,
        "avg_light_hours": avg_light_hrs,
        "avg_rem_hours": avg_rem_hrs,
        "latest_record": latest,
        "duration_vs_prev_min": dur_diff_min,
        "score_vs_prev": score_diff,
        "daily_trends": daily_trends,
    }

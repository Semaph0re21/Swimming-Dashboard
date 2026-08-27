"""
Structured running workout generator based on Jack Daniels VDOT and lactate threshold training models.
Generates periodized, structured interval sets with exact target paces, distances, heart rate zones, and rest periods.
"""
import uuid
from src.analytics.running import format_run_pace


def get_run_pace_targets(best_pace_sec_km=550):
    """
    Calculate target pace seconds per km for each physiological training zone.
    best_pace_sec_km: athlete's best pace or 5K threshold pace in seconds per km (default ~550s = 9:10/km).
    """
    if not best_pace_sec_km or best_pace_sec_km <= 0:
        best_pace_sec_km = 550

    return {
        "recovery": (best_pace_sec_km * 1.30, best_pace_sec_km * 1.50),
        "easy": (best_pace_sec_km * 1.20, best_pace_sec_km * 1.35),
        "marathon": (best_pace_sec_km * 1.10, best_pace_sec_km * 1.20),
        "tempo": (best_pace_sec_km * 1.02, best_pace_sec_km * 1.10),
        "threshold": (best_pace_sec_km * 0.96, best_pace_sec_km * 1.02),
        "interval": (best_pace_sec_km * 0.88, best_pace_sec_km * 0.95),
        "repetition": (best_pace_sec_km * 0.80, best_pace_sec_km * 0.88),
    }


def format_zone_pace(min_sec, max_sec):
    return f"{format_run_pace(min_sec)} – {format_run_pace(max_sec)}"


def generate_run_workout(focus, distance_km, best_pace_sec_km=550):
    """
    Generate a structured running workout with detailed sets, intervals, target paces, and rest intervals.
    focus: 'Easy / Recovery Run', 'Aerobic Endurance (Long Run)', 'Lactate Threshold (Tempo)',
           'VO2 Max / Speed Intervals', 'Pyramid Ladder Intervals', 'Hill Repeats'
    distance_km: total target distance in km (e.g. 5.0, 8.0, 10.0, 15.0)
    best_pace_sec_km: athlete's reference baseline pace in seconds/km.
    """
    paces = get_run_pace_targets(best_pace_sec_km)
    dist = max(3.0, round(float(distance_km), 1))
    
    if "Recovery" in focus or "Easy" in focus:
        # Easy Recovery Run
        warm_dist = round(min(1.0, dist * 0.2), 1)
        cool_dist = round(min(1.0, dist * 0.2), 1)
        main_dist = round(dist - warm_dist - cool_dist, 1)
        avg_pace_sec = (paces["easy"][0] + paces["easy"][1]) / 2.0
        dur_mins = int(round((dist * avg_pace_sec) / 60.0))

        sets = [
            {
                "set_num": 1,
                "reps": 1,
                "distance": f"{warm_dist} km",
                "distance_km": warm_dist,
                "purpose": "Warm-up Jog",
                "pattern": "Easy Aerobic Jog",
                "pace": format_zone_pace(paces["recovery"][0], paces["recovery"][1]),
                "hr_zone": "Zone 1 (< 70% HRmax)",
                "rest": "Continuous",
            },
            {
                "set_num": 2,
                "reps": 1,
                "distance": f"{main_dist} km",
                "distance_km": main_dist,
                "purpose": "Aerobic Base Cruise",
                "pattern": "Steady Conversational Run",
                "pace": format_zone_pace(paces["easy"][0], paces["easy"][1]),
                "hr_zone": "Zone 2 (70–78% HRmax)",
                "rest": "None",
            },
            {
                "set_num": 3,
                "reps": 1,
                "distance": f"{cool_dist} km",
                "distance_km": cool_dist,
                "purpose": "Cool-down & Strides",
                "pattern": "Easy Flush Jog + 4 × 50m light strides",
                "pace": format_zone_pace(paces["recovery"][0], paces["recovery"][1]),
                "hr_zone": "Zone 1 (< 68% HRmax)",
                "rest": "None",
            },
        ]
        goal = "Promote active recovery, enhance capillary density, and build aerobic volume without joint stress."

    elif "Endurance" in focus or "Long" in focus:
        # Long Aerobic Endurance Run
        warm_dist = round(min(2.0, dist * 0.2), 1)
        cool_dist = round(min(1.5, dist * 0.15), 1)
        main_dist = round(dist - warm_dist - cool_dist, 1)
        avg_pace_sec = (paces["marathon"][0] + paces["marathon"][1]) / 2.0
        dur_mins = int(round((dist * avg_pace_sec) / 60.0))

        sets = [
            {
                "set_num": 1,
                "reps": 1,
                "distance": f"{warm_dist} km",
                "distance_km": warm_dist,
                "purpose": "Progressive Warm-up",
                "pattern": "Gradual ramp from Easy to Marathon Pace",
                "pace": format_zone_pace(paces["easy"][0], paces["easy"][1]),
                "hr_zone": "Zone 1–2 (68–75% HRmax)",
                "rest": "None",
            },
            {
                "set_num": 2,
                "reps": 1,
                "distance": f"{main_dist} km",
                "distance_km": main_dist,
                "purpose": "Steady Aerobic Stamina",
                "pattern": "Sustained Marathon Base Pace",
                "pace": format_zone_pace(paces["marathon"][0], paces["marathon"][1]),
                "hr_zone": "Zone 2–3 (75–82% HRmax)",
                "rest": "None",
            },
            {
                "set_num": 3,
                "reps": 1,
                "distance": f"{cool_dist} km",
                "distance_km": cool_dist,
                "purpose": "Cool-down Jog",
                "pattern": "Relaxed recovery jog",
                "pace": format_zone_pace(paces["recovery"][0], paces["recovery"][1]),
                "hr_zone": "Zone 1 (< 70% HRmax)",
                "rest": "None",
            },
        ]
        goal = "Develop glycogen sparing efficiency, fat oxidation, and mental resilience for distance racing."

    elif "Threshold" in focus or "Tempo" in focus:
        # Lactate Threshold Tempo Run
        warm_dist = round(min(2.0, dist * 0.25), 1)
        cool_dist = round(min(1.5, dist * 0.2), 1)
        tempo_dist = round(dist - warm_dist - cool_dist, 1)
        avg_pace_sec = (paces["tempo"][0] + paces["tempo"][1]) / 2.0
        dur_mins = int(round((dist * avg_pace_sec) / 60.0))

        sets = [
            {
                "set_num": 1,
                "reps": 1,
                "distance": f"{warm_dist} km",
                "distance_km": warm_dist,
                "purpose": "Warm-up & Activation",
                "pattern": "Easy Jog + Dynamic Running Drills",
                "pace": format_zone_pace(paces["easy"][0], paces["easy"][1]),
                "hr_zone": "Zone 1–2 (70–75% HRmax)",
                "rest": "None",
            },
            {
                "set_num": 2,
                "reps": 1,
                "distance": f"{tempo_dist} km",
                "distance_km": tempo_dist,
                "purpose": "Lactate Threshold Tempo",
                "pattern": "Continuous 'Comfortably Hard' Threshold Effort",
                "pace": format_zone_pace(paces["threshold"][0], paces["threshold"][1]),
                "hr_zone": "Zone 4 (86–92% HRmax)",
                "rest": "Continuous",
            },
            {
                "set_num": 3,
                "reps": 1,
                "distance": f"{cool_dist} km",
                "distance_km": cool_dist,
                "purpose": "Cool-down Jog",
                "pattern": "Easy flush jog",
                "pace": format_zone_pace(paces["recovery"][0], paces["recovery"][1]),
                "hr_zone": "Zone 1 (< 70% HRmax)",
                "rest": "None",
            },
        ]
        goal = "Increase lactate threshold speed, delaying fatigue onset during high sustained velocities."

    elif "Intervals" in focus or "VO2" in focus or "Speed" in focus:
        # VO2 Max Track / Road Speed Intervals
        warm_dist = 1.5
        cool_dist = 1.5
        rem_dist = max(1.6, dist - warm_dist - cool_dist)
        
        # Interval repeats of 800m (0.8km) or 1km
        rep_dist_km = 0.8 if rem_dist < 5.0 else 1.0
        reps = max(3, int(round(rem_dist / rep_dist_km)))
        interval_total_dist = round(reps * rep_dist_km, 1)
        actual_total_dist = round(warm_dist + interval_total_dist + cool_dist, 1)
        avg_pace_sec = (paces["interval"][0] + paces["interval"][1]) / 2.0
        dur_mins = int(round((actual_total_dist * avg_pace_sec) / 60.0)) + (reps * 2)

        sets = [
            {
                "set_num": 1,
                "reps": 1,
                "distance": f"{warm_dist} km",
                "distance_km": warm_dist,
                "purpose": "Warm-up & Activation",
                "pattern": "Easy Jog + 4 × 100m High Cadence Strides",
                "pace": format_zone_pace(paces["easy"][0], paces["easy"][1]),
                "hr_zone": "Zone 1–2 (70–75% HRmax)",
                "rest": "2 min",
            },
            {
                "set_num": 2,
                "reps": reps,
                "distance": f"{int(rep_dist_km * 1000)}m",
                "total_distance": f"{interval_total_dist} km",
                "distance_km": interval_total_dist,
                "purpose": "VO2 Max Speed Repeats",
                "pattern": f"{reps} × {int(rep_dist_km * 1000)}m @ VO2 Max Pace",
                "pace": format_zone_pace(paces["interval"][0], paces["interval"][1]),
                "hr_zone": "Zone 5 (92–98% HRmax)",
                "rest": "90–120 sec jog recovery",
            },
            {
                "set_num": 3,
                "reps": 1,
                "distance": f"{cool_dist} km",
                "distance_km": cool_dist,
                "purpose": "Cool-down Jog",
                "pattern": "Slow recovery flush jog",
                "pace": format_zone_pace(paces["recovery"][0], paces["recovery"][1]),
                "hr_zone": "Zone 1 (< 68% HRmax)",
                "rest": "None",
            },
        ]
        goal = "Expand maximum aerobic capacity (VO2 max), running economy, and neuromuscular turnover."
        dist = actual_total_dist

    elif "Pyramid" in focus or "Ladder" in focus:
        # Pyramid Ladder (400m - 800m - 1200m - 800m - 400m = 3.6km work)
        warm_dist = 1.5
        cool_dist = 1.5
        ladder_work = 3.6
        total_d = round(warm_dist + ladder_work + cool_dist, 1)
        dur_mins = 45

        sets = [
            {
                "set_num": 1,
                "reps": 1,
                "distance": f"{warm_dist} km",
                "distance_km": warm_dist,
                "purpose": "Warm-up Jog",
                "pattern": "Easy Jog + Dynamic Movement",
                "pace": format_zone_pace(paces["easy"][0], paces["easy"][1]),
                "hr_zone": "Zone 1–2",
                "rest": "2 min",
            },
            {
                "set_num": 2,
                "reps": 1,
                "distance": "3.6 km (5 steps)",
                "total_distance": "3.6 km",
                "distance_km": 3.6,
                "purpose": "Pyramid Pace Ladder",
                "pattern": "400m (Fast) · 800m (Threshold) · 1,200m (Tempo) · 800m (Threshold) · 400m (Fast)",
                "pace": format_zone_pace(paces["interval"][0], paces["threshold"][1]),
                "hr_zone": "Zone 4–5 (88–96% HRmax)",
                "rest": "60–90 sec between steps",
            },
            {
                "set_num": 3,
                "reps": 1,
                "distance": f"{cool_dist} km",
                "distance_km": cool_dist,
                "purpose": "Cool-down Jog",
                "pattern": "Flush recovery jog",
                "pace": format_zone_pace(paces["recovery"][0], paces["recovery"][1]),
                "hr_zone": "Zone 1",
                "rest": "None",
            },
        ]
        goal = "Improve race pace shifting, psychological endurance, and lactate clearance during fluctuating speeds."
        dist = total_d

    else:  # Hill Repeats
        warm_dist = 2.0
        cool_dist = 1.5
        reps = 6
        hill_work = round(reps * 0.2, 1)  # 6 x 200m
        total_d = round(warm_dist + hill_work + cool_dist, 1)
        dur_mins = 40

        sets = [
            {
                "set_num": 1,
                "reps": 1,
                "distance": f"{warm_dist} km",
                "distance_km": warm_dist,
                "purpose": "Warm-up Jog",
                "pattern": "Easy Aerobic Jogging",
                "pace": format_zone_pace(paces["easy"][0], paces["easy"][1]),
                "hr_zone": "Zone 1–2",
                "rest": "None",
            },
            {
                "set_num": 2,
                "reps": reps,
                "distance": "200m",
                "total_distance": f"{hill_work} km",
                "distance_km": hill_work,
                "purpose": "Hill Sprints & Power",
                "pattern": f"{reps} × 200m Explosive Uphill Sprints (4–6% gradient)",
                "pace": "Hard Effort / Maximum Cadence",
                "hr_zone": "Zone 5 (Power / Anaerobic)",
                "rest": "Jog-down recovery to base",
            },
            {
                "set_num": 3,
                "reps": 1,
                "distance": f"{cool_dist} km",
                "distance_km": cool_dist,
                "purpose": "Cool-down Jog",
                "pattern": "Flat easy recovery jog",
                "pace": format_zone_pace(paces["recovery"][0], paces["recovery"][1]),
                "hr_zone": "Zone 1",
                "rest": "None",
            },
        ]
        goal = "Build running-specific muscular power, stride efficiency, and ankle elasticity with low impact."
        dist = total_d

    dur_str = f"{dur_mins - 5}–{dur_mins + 5} min" if dur_mins > 10 else f"{dur_mins} min"

    return {
        "plan_id": str(uuid.uuid4()),
        "sport": "Run",
        "type": focus,
        "workout_type": focus,
        "name": f"{focus} ({dist} km)",
        "distance_km": dist,
        "target_distance": dist,
        "distance_m": int(dist * 1000),
        "duration": dur_str,
        "duration_est": dur_str,
        "sets": sets,
        "goal": goal,
        "readiness_score": 85,
        "coach_rationale": "Structured running session engineered from your 5-Zone pace guidelines and acute load.",
    }

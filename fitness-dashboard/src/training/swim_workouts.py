# ============================================================
# DYNAMIC SWIM WORKOUT GENERATOR
# Pool: 25m (1 lap = 25m)
#
# User's primary mixed stroke pattern:
#   100m = 3 laps Freestyle + 1 lap Breaststroke (75% Free / 25% Breast)
#   200m = 6 laps Freestyle + 2 laps Breaststroke
#   300m = 9 laps Freestyle + 3 laps Breaststroke
# ============================================================

POOL_LENGTH_M = 25

MIXED_100_PATTERN = [
    "25m Freestyle",
    "25m Freestyle",
    "25m Freestyle",
    "25m Breaststroke",
]


def mixed_pattern(distance):
    """
    Return the stroke pattern list for a mixed-distance set.
    """
    if distance % 100 != 0:
        return None
    repetitions = distance // 100
    pattern = []
    for _ in range(repetitions):
        pattern.extend(MIXED_100_PATTERN)
    return pattern


def format_pace(seconds):
    """
    Format seconds per 100m into MM:SS/100m string.
    """
    if not seconds or seconds <= 0:
        return "—"
    minutes = int(seconds // 60)
    secs = int(round(seconds % 60))
    if secs >= 60:
        minutes += 1
        secs -= 60
    return f"{minutes}:{secs:02d}/100m"


def laps_for_distance(distance):
    """
    Convert distance to laps in a 25m pool.
    """
    if distance % POOL_LENGTH_M != 0:
        raise ValueError(
            f"{distance}m cannot be completed exactly in a {POOL_LENGTH_M}m pool."
        )
    return distance // POOL_LENGTH_M


def stroke_summary(stroke, distance):
    """
    Return a human-readable stroke description.
    """
    if stroke == "Mixed":
        pattern = mixed_pattern(distance)
        if pattern:
            freestyle_laps = (distance // 100) * 3
            breaststroke_laps = distance // 100
            return (
                f"{freestyle_laps} laps Freestyle + {breaststroke_laps} laps Breaststroke"
            )
        return "Mixed strokes"
    return stroke


def create_set(distance, reps, stroke, purpose, pace, rest):
    """
    Create a structured workout set.
    """
    total_distance = distance * reps
    return {
        "distance": distance,
        "reps": reps,
        "total_distance": total_distance,
        "laps": laps_for_distance(distance),
        "total_laps": laps_for_distance(total_distance),
        "stroke": stroke,
        "stroke_pattern": stroke_summary(stroke, distance),
        "purpose": purpose,
        "pace": pace,
        "rest": rest,
    }


# ============================================================
# 1. ENDURANCE WORKOUT
# ============================================================

def endurance_workout(
    target_distance=2000,
    easy_min=169,
    easy_max=184,
    endurance_min=154,
    endurance_max=164,
):
    """
    Aerobic base endurance workout with 200m mixed intervals and active recovery.
    """
    target_distance = max(1000, round(target_distance / 100) * 100)

    if target_distance % 200 == 0:
        warmup = 300
        cooldown = 300
    else:
        warmup = 300
        cooldown = 200

    main_distance = target_distance - warmup - cooldown

    if main_distance <= 0:
        warmup = 200
        cooldown = 200
        main_distance = target_distance - warmup - cooldown

    repetitions = max(1, main_distance // 200)
    adjusted_target = warmup + (repetitions * 200) + cooldown

    sets = [
        # Warm-up
        create_set(
            distance=warmup,
            reps=1,
            stroke="Freestyle",
            purpose="Easy warm-up",
            pace=f"{format_pace(easy_min)}-{format_pace(easy_max)}",
            rest="None",
        ),
        # Main Endurance Set
        create_set(
            distance=200,
            reps=repetitions,
            stroke="Mixed",
            purpose="Endurance",
            pace=f"{format_pace(endurance_min)}-{format_pace(endurance_max)}",
            rest="20-30 sec",
        ),
        # Cool-down
        create_set(
            distance=cooldown,
            reps=1,
            stroke="Freestyle",
            purpose="Cool-down",
            pace=f"{format_pace(easy_min)}-{format_pace(easy_max)}",
            rest="None",
        ),
    ]

    duration_est = f"{max(35, int(adjusted_target / 45))}-{max(45, int(adjusted_target / 35))} min"

    return {
        "type": "Endurance",
        "target_distance": adjusted_target,
        "pool_length": POOL_LENGTH_M,
        "total_laps": laps_for_distance(adjusted_target),
        "duration": duration_est,
        "sets": sets,
        "goal": "Build aerobic endurance while improving sustainable freestyle pace.",
    }


# ============================================================
# 2. TEMPO (THRESHOLD) WORKOUT
# ============================================================

def tempo_workout(
    target_distance=2100,
    easy_min=169,
    easy_max=184,
    tempo_min=144,
    tempo_max=154,
):
    """
    Lactate threshold tempo workout designed to increase sustainable swimming speed.
    """
    target_distance = max(1200, round(target_distance / 100) * 100)
    warmup = 300
    drill_dist = 200  # 4 x 50m Backstroke technique
    recovery_dist = 200  # 4 x 50m Breaststroke recovery
    cooldown = 200

    fixed_dist = warmup + drill_dist + recovery_dist + cooldown
    main_distance = target_distance - fixed_dist

    if main_distance < 200:
        main_reps = 3
    else:
        main_reps = max(2, main_distance // 200)

    tempo_pace_str = f"{format_pace(tempo_min)}-{format_pace(tempo_max)}" if tempo_min and tempo_max else "2:24-2:34/100m"

    sets = [
        # Warm-up
        create_set(
            distance=warmup,
            reps=1,
            stroke="Freestyle",
            purpose="Warm-up",
            pace=f"{format_pace(easy_min)}-{format_pace(easy_max)}",
            rest="None",
        ),
        # Backstroke Technique
        create_set(
            distance=50,
            reps=4,
            stroke="Backstroke",
            purpose="Technique",
            pace="Controlled",
            rest="15-20 sec",
        ),
        # Tempo Main Set
        create_set(
            distance=200,
            reps=main_reps,
            stroke="Mixed",
            purpose="Tempo",
            pace=tempo_pace_str,
            rest="20-30 sec",
        ),
        # Breaststroke Recovery
        create_set(
            distance=50,
            reps=4,
            stroke="Breaststroke",
            purpose="Recovery",
            pace="Easy",
            rest="15 sec",
        ),
        # Cool-down
        create_set(
            distance=cooldown,
            reps=1,
            stroke="Freestyle",
            purpose="Cool-down",
            pace=f"{format_pace(easy_min)}-{format_pace(easy_max)}",
            rest="None",
        ),
    ]

    total_dist = sum(s["total_distance"] for s in sets)
    duration_est = f"{max(35, int(total_dist / 45))}-{max(50, int(total_dist / 35))} min"

    return {
        "type": "Tempo",
        "target_distance": total_dist,
        "pool_length": POOL_LENGTH_M,
        "total_laps": laps_for_distance(total_dist),
        "duration": duration_est,
        "sets": sets,
        "goal": "Improve sustainable swimming pace while maintaining efficient technique.",
    }


# ============================================================
# 3. SPEED INTERVALS WORKOUT
# ============================================================

def interval_workout(
    target_distance=1900,
    easy_min=169,
    easy_max=184,
    interval_min=134,
    interval_max=144,
):
    """
    High-intensity speed repeats focused on VO2 Max and 100m freestyle pacing.
    """
    target_distance = max(1200, round(target_distance / 100) * 100)
    warmup = 300
    drill_dist = 200  # 4 x 50m Backstroke technique
    cooldown = 200

    fixed_dist = warmup + drill_dist + cooldown
    rem_dist = target_distance - fixed_dist

    # Each interval block consists of 100m Speed Free + 50m Easy Breaststroke = 150m
    if rem_dist <= 300:
        blocks = 4
    else:
        blocks = max(4, round(rem_dist / 150))

    interval_pace_str = f"{format_pace(interval_min)}-{format_pace(interval_max)}" if interval_min and interval_max else "2:14-2:24/100m"

    sets = [
        # Warm-up
        create_set(
            distance=warmup,
            reps=1,
            stroke="Freestyle",
            purpose="Warm-up",
            pace=f"{format_pace(easy_min)}-{format_pace(easy_max)}",
            rest="None",
        ),
        # Backstroke Technique
        create_set(
            distance=50,
            reps=4,
            stroke="Backstroke",
            purpose="Technique",
            pace="Controlled",
            rest="15-20 sec",
        ),
        # Freestyle Speed Repeats
        create_set(
            distance=100,
            reps=blocks,
            stroke="Freestyle",
            purpose="Speed",
            pace=interval_pace_str,
            rest="20-30 sec",
        ),
        # Active Recovery
        create_set(
            distance=50,
            reps=blocks,
            stroke="Breaststroke",
            purpose="Recovery",
            pace="Easy",
            rest="15-20 sec",
        ),
        # Cool-down
        create_set(
            distance=cooldown,
            reps=1,
            stroke="Freestyle",
            purpose="Cool-down",
            pace=f"{format_pace(easy_min)}-{format_pace(easy_max)}",
            rest="None",
        ),
    ]

    total_dist = sum(s["total_distance"] for s in sets)
    duration_est = f"{max(35, int(total_dist / 45))}-{max(45, int(total_dist / 35))} min"

    return {
        "type": "Intervals",
        "target_distance": total_dist,
        "pool_length": POOL_LENGTH_M,
        "total_laps": laps_for_distance(total_dist),
        "duration": duration_est,
        "sets": sets,
        "goal": "Improve freestyle speed and pace control.",
    }


# ============================================================
# 4. RECOVERY & TECHNIQUE WORKOUT
# ============================================================

def recovery_workout(
    target_distance=1200,
    easy_min=169,
    easy_max=184,
):
    """
    Low-intensity recovery workout emphasizing catch efficiency and technique.
    """
    target_distance = max(1000, round(target_distance / 100) * 100)
    warmup = 300
    drill_back = 200  # 4 x 50m Backstroke
    cooldown = 300

    fixed = warmup + drill_back + cooldown
    rem = max(200, target_distance - fixed)
    mixed_reps = max(2, rem // 100)

    recovery_pace_str = f"{format_pace(easy_min)}-{format_pace(easy_max)}" if easy_min and easy_max else "2:49-3:04/100m"

    sets = [
        # Easy Freestyle
        create_set(
            distance=warmup,
            reps=1,
            stroke="Freestyle",
            purpose="Easy swim",
            pace=recovery_pace_str,
            rest="None",
        ),
        # Mixed Easy Swimming
        create_set(
            distance=100,
            reps=mixed_reps,
            stroke="Mixed",
            purpose="Relaxed swimming",
            pace="Easy",
            rest="15 sec",
        ),
        # Backstroke Technique
        create_set(
            distance=50,
            reps=4,
            stroke="Backstroke",
            purpose="Technique",
            pace="Controlled",
            rest="15 sec",
        ),
        # Cool-down
        create_set(
            distance=cooldown,
            reps=1,
            stroke="Freestyle",
            purpose="Cool-down",
            pace="Easy",
            rest="None",
        ),
    ]

    total_dist = sum(s["total_distance"] for s in sets)
    duration_est = f"{max(25, int(total_dist / 45))}-{max(35, int(total_dist / 35))} min"

    return {
        "type": "Recovery",
        "target_distance": total_dist,
        "pool_length": POOL_LENGTH_M,
        "total_laps": laps_for_distance(total_dist),
        "duration": duration_est,
        "sets": sets,
        "goal": "Promote recovery while maintaining swimming consistency and technique.",
    }


# ============================================================
# 5. PYRAMID / LADDER WORKOUT
# ============================================================

def pyramid_workout(
    target_distance=2000,
    easy_min=169,
    easy_max=184,
    tempo_min=144,
    tempo_max=154,
    interval_min=134,
    interval_max=144,
):
    """
    Ascending & Descending Ladder Pyramid workout for pace discipline and stamina.
    """
    warmup = 300
    cooldown = 300
    easy_pace = f"{format_pace(easy_min)}-{format_pace(easy_max)}"
    tempo_pace = f"{format_pace(tempo_min)}-{format_pace(tempo_max)}"
    speed_pace = f"{format_pace(interval_min)}-{format_pace(interval_max)}"

    sets = [
        # Warmup
        create_set(300, 1, "Freestyle", "Warm-up", easy_pace, "None"),
        # Pyramid Step 1: 50m Speed
        create_set(50, 2, "Freestyle", "Sprint Build", speed_pace, "15 sec"),
        # Pyramid Step 2: 100m Mixed
        create_set(100, 2, "Mixed", "Speed Interval", speed_pace, "20 sec"),
        # Pyramid Step 3: 200m Mixed (Peak of Pyramid)
        create_set(200, 2, "Mixed", "Threshold Peak", tempo_pace, "30 sec"),
        # Pyramid Step 4: 100m Mixed
        create_set(100, 2, "Mixed", "Descending Speed", speed_pace, "20 sec"),
        # Pyramid Step 5: 50m Backstroke / Free Sprint
        create_set(50, 4, "Backstroke", "Technique & Finish", "Controlled", "15 sec"),
        # Cooldown
        create_set(cooldown, 1, "Freestyle", "Cool-down", easy_pace, "None"),
    ]

    total_dist = sum(s["total_distance"] for s in sets)
    duration_est = f"{max(35, int(total_dist / 45))}-{max(50, int(total_dist / 35))} min"

    return {
        "type": "Pyramid",
        "target_distance": total_dist,
        "pool_length": POOL_LENGTH_M,
        "total_laps": laps_for_distance(total_dist),
        "duration": duration_est,
        "sets": sets,
        "goal": "Build aerobic capacity, stroke pacing discipline, and finishing speed.",
    }
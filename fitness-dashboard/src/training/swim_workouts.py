# ============================================================
# SWIM WORKOUT GENERATOR
# Pool: 25m
# 1 lap = 25m
#
# User's normal mixed pattern:
# 100m = 3 laps Freestyle + 1 lap Breaststroke
# 200m = 6 laps Freestyle + 2 laps Breaststroke
# ============================================================


POOL_LENGTH_M = 25


# ============================================================
# MIXED SWIM PATTERN
# ============================================================

MIXED_100_PATTERN = [
    "25m Freestyle",
    "25m Freestyle",
    "25m Freestyle",
    "25m Breaststroke",
]


def mixed_pattern(distance):
    """
    Return the stroke pattern for a mixed-distance set.

    100m:
        3 laps Freestyle
        1 lap Breaststroke

    200m:
        6 laps Freestyle
        2 laps Breaststroke

    300m:
        9 laps Freestyle
        3 laps Breaststroke
    """

    if distance % 100 != 0:
        return None

    repetitions = distance // 100

    pattern = []

    for _ in range(repetitions):
        pattern.extend(MIXED_100_PATTERN)

    return pattern


# ============================================================
# BASIC HELPERS
# ============================================================

def format_pace(seconds):
    minutes = int(seconds // 60)
    secs = int(round(seconds % 60))

    if secs >= 60:
        minutes += 1
        secs -= 60

    return f"{minutes}:{secs:02d}/100m"


def laps_for_distance(distance):
    """
    Convert distance to laps.

    Example:
        25m  = 1 lap
        50m  = 2 laps
        100m = 4 laps
        200m = 8 laps
    """

    if distance % POOL_LENGTH_M != 0:
        raise ValueError(
            f"{distance}m cannot be completed exactly "
            f"in a {POOL_LENGTH_M}m pool."
        )

    return distance // POOL_LENGTH_M


def stroke_summary(stroke, distance):
    """
    Return a human-readable stroke description.
    """

    if stroke == "Mixed":

        pattern = mixed_pattern(distance)

        if pattern:
            freestyle_laps = (
                distance // 100
            ) * 3

            breaststroke_laps = (
                distance // 100
            )

            return (
                f"{freestyle_laps} laps Freestyle + "
                f"{breaststroke_laps} laps Breaststroke"
            )

        return "Mixed strokes"

    return stroke


def create_set(
    distance,
    reps,
    stroke,
    purpose,
    pace,
    rest,
):
    """
    Create a structured workout set.
    """

    total_distance = distance * reps

    return {
        "distance": distance,
        "reps": reps,
        "total_distance": total_distance,

        "laps": laps_for_distance(
            distance
        ),

        "total_laps": laps_for_distance(
            total_distance
        ),

        "stroke": stroke,

        "stroke_pattern": stroke_summary(
            stroke,
            distance
        ),

        "purpose": purpose,
        "pace": pace,
        "rest": rest,
    }


# ============================================================
# ENDURANCE WORKOUT
# ============================================================

def endurance_workout(
    target_distance=2000,
    easy_min=169,
    easy_max=184,
    endurance_min=154,
    endurance_max=164,
):
    """
    Endurance workout.

    Example for 1500m:

        300m warm-up
        5 x 200m mixed
        200m cool-down

    Total = 1500m
    Total laps = 60
    """

    if target_distance % 200 == 0:
        warmup = 300
        cooldown = 300
    else:
        warmup = 300
        cooldown = 200

    main_distance = (
        target_distance
        - warmup
        - cooldown
    )

    if main_distance <= 0:
        warmup = 100
        cooldown = 100
        main_distance = target_distance - warmup - cooldown

    if main_distance <= 0:
        raise ValueError(
            "Target distance is too small."
        )

    repetitions = max(1, main_distance // 200)

    sets = [

        # ----------------------------------------------------
        # WARM-UP
        # ----------------------------------------------------

        create_set(
            distance=warmup,
            reps=1,
            stroke="Freestyle",
            purpose="Easy warm-up",
            pace=(
                f"{format_pace(easy_min)}-"
                f"{format_pace(easy_max)}"
            ),
            rest="None",
        ),

        # ----------------------------------------------------
        # MAIN ENDURANCE SET
        # ----------------------------------------------------

        create_set(
            distance=200,
            reps=repetitions,
            stroke="Mixed",
            purpose="Endurance",
            pace=(
                f"{format_pace(endurance_min)}-"
                f"{format_pace(endurance_max)}"
            ),
            rest="20-30 sec",
        ),

        # ----------------------------------------------------
        # COOL-DOWN
        # ----------------------------------------------------

        create_set(
            distance=cooldown,
            reps=1,
            stroke="Freestyle",
            purpose="Cool-down",
            pace=(
                f"{format_pace(easy_min)}-"
                f"{format_pace(easy_max)}"
            ),
            rest="None",
        ),
    ]

    return {
        "type": "Endurance",
        "target_distance": target_distance,
        "pool_length": POOL_LENGTH_M,

        "total_laps": laps_for_distance(
            target_distance
        ),

        "duration": "45-60 min",
        "sets": sets,

        "goal": (
            "Build aerobic endurance while "
            "improving sustainable freestyle pace."
        ),
    }


# ============================================================
# TEMPO WORKOUT
# ============================================================

def tempo_workout():
    """
    Tempo workout focused on sustainable pace.
    """

    sets = [

        # WARM-UP
        create_set(
            distance=300,
            reps=1,
            stroke="Freestyle",
            purpose="Warm-up",
            pace="Easy",
            rest="None",
        ),

        # BACKSTROKE TECHNIQUE
        create_set(
            distance=50,
            reps=4,
            stroke="Backstroke",
            purpose="Technique",
            pace="Controlled",
            rest="15-20 sec",
        ),

        # TEMPO MAIN SET
        create_set(
            distance=200,
            reps=6,
            stroke="Mixed",
            purpose="Tempo",
            pace="2:24-2:34/100m",
            rest="20-30 sec",
        ),

        # BREASTSTROKE RECOVERY
        create_set(
            distance=50,
            reps=4,
            stroke="Breaststroke",
            purpose="Recovery",
            pace="Easy",
            rest="15 sec",
        ),

        # COOL-DOWN
        create_set(
            distance=200,
            reps=1,
            stroke="Freestyle",
            purpose="Cool-down",
            pace="Easy",
            rest="None",
        ),
    ]

    total_distance = sum(
        item["total_distance"]
        for item in sets
    )

    return {
        "type": "Tempo",
        "target_distance": total_distance,
        "pool_length": POOL_LENGTH_M,

        "total_laps": laps_for_distance(
            total_distance
        ),

        "duration": "50-60 min",
        "sets": sets,

        "goal": (
            "Improve sustainable swimming pace "
            "while maintaining efficient technique."
        ),
    }


# ============================================================
# INTERVAL WORKOUT
# ============================================================

def interval_workout():
    """
    Speed-focused freestyle workout.
    """

    sets = [

        # WARM-UP
        create_set(
            distance=300,
            reps=1,
            stroke="Freestyle",
            purpose="Warm-up",
            pace="Easy",
            rest="None",
        ),

        # BACKSTROKE TECHNIQUE
        create_set(
            distance=50,
            reps=4,
            stroke="Backstroke",
            purpose="Technique",
            pace="Controlled",
            rest="15-20 sec",
        ),

        # FREESTYLE SPEED
        create_set(
            distance=100,
            reps=8,
            stroke="Freestyle",
            purpose="Speed",
            pace="2:14-2:24/100m",
            rest="20-30 sec",
        ),

        # BREASTSTROKE RECOVERY
        create_set(
            distance=50,
            reps=8,
            stroke="Breaststroke",
            purpose="Recovery",
            pace="Easy",
            rest="15-20 sec",
        ),

        # COOL-DOWN
        create_set(
            distance=200,
            reps=1,
            stroke="Freestyle",
            purpose="Cool-down",
            pace="Easy",
            rest="None",
        ),
    ]

    total_distance = sum(
        item["total_distance"]
        for item in sets
    )

    return {
        "type": "Intervals",
        "target_distance": total_distance,
        "pool_length": POOL_LENGTH_M,

        "total_laps": laps_for_distance(
            total_distance
        ),

        "duration": "45-55 min",
        "sets": sets,

        "goal": (
            "Improve freestyle speed and "
            "pace control."
        ),
    }


# ============================================================
# RECOVERY WORKOUT
# ============================================================

def recovery_workout():
    """
    Low-intensity recovery workout.
    """

    sets = [

        # EASY FREESTYLE
        create_set(
            distance=300,
            reps=1,
            stroke="Freestyle",
            purpose="Easy swim",
            pace="2:49-3:04/100m",
            rest="None",
        ),

        # MIXED EASY SWIMMING
        create_set(
            distance=100,
            reps=4,
            stroke="Mixed",
            purpose="Relaxed swimming",
            pace="Easy",
            rest="15 sec",
        ),

        # BACKSTROKE TECHNIQUE
        create_set(
            distance=50,
            reps=4,
            stroke="Backstroke",
            purpose="Technique",
            pace="Controlled",
            rest="15 sec",
        ),

        # COOL-DOWN
        create_set(
            distance=300,
            reps=1,
            stroke="Freestyle",
            purpose="Cool-down",
            pace="Easy",
            rest="None",
        ),
    ]

    total_distance = sum(
        item["total_distance"]
        for item in sets
    )

    return {
        "type": "Recovery",
        "target_distance": total_distance,
        "pool_length": POOL_LENGTH_M,

        "total_laps": laps_for_distance(
            total_distance
        ),

        "duration": "30-40 min",
        "sets": sets,

        "goal": (
            "Promote recovery while maintaining "
            "swimming consistency and technique."
        ),
    }
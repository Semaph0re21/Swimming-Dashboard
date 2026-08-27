def evaluate_swim_coach(
    current_week,
    previous_week,
    days_since_swim,
    wellness=None,
    last_workout_type=None,
):
    """
    Multi-dimensional AI Swim Coach evaluation engine.
    Analyzes:
      1. Garmin Sleep Score, Overnight HRV, and Resting Heart Rate
      2. Acute Training Load (ATL) and 7-day fatigue
      3. Training gap & detraining prevention
      4. Session sequence & periodization balance
    """
    current_swim = current_week.get("Swim", {}) if isinstance(current_week, dict) else {}
    previous_swim = previous_week.get("Swim", {}) if isinstance(previous_week, dict) else {}

    current_load = current_swim.get("training_load", 0) or 0
    current_distance = current_swim.get("distance_km", 0) or 0
    current_sessions = current_swim.get("sessions", 0) or 0
    previous_distance = previous_swim.get("distance_km", 0) or 0

    # Wellness & biometric signals
    sleep_score = None
    rhr = None
    hrv = None

    if isinstance(wellness, dict):
        sleep_score = wellness.get("sleepScore")
        rhr = wellness.get("restingHR")
        hrv = wellness.get("hrv")

    # ------------------------------------------------------------
    # 1. BIOMETRIC OVERLOAD / POOR RECOVERY CHECK
    # ------------------------------------------------------------
    if sleep_score is not None and sleep_score < 50:
        return {
            "workout_type": "Recovery",
            "intensity": "Easy",
            "primary_driver": "Biometric Recovery",
            "readiness_score": 45,
            "coaching_rationale": f"Garmin sleep score is low ({sleep_score:.0f}/100). Prescribing an easy recovery and technique swim to prevent overreaching.",
        }

    # ------------------------------------------------------------
    # 2. HIGH ACUTE TRAINING LOAD (LOAD >= 150)
    # ------------------------------------------------------------
    if current_load >= 150:
        return {
            "workout_type": "Recovery",
            "intensity": "Easy",
            "primary_driver": "High Load Taper",
            "readiness_score": 55,
            "coaching_rationale": f"High 7-day swim load ({current_load:.0f}). Active recovery and technique focus will accelerate muscular restoration.",
        }

    # ------------------------------------------------------------
    # 3. TRAINING GAP (GAP >= 4 DAYS) OR VOLUME DROP (> 50%)
    # ------------------------------------------------------------
    if days_since_swim is None or days_since_swim >= 4:
        gap_str = f"{days_since_swim} days" if days_since_swim is not None else "extended break"
        return {
            "workout_type": "Endurance",
            "intensity": "Moderate",
            "primary_driver": "Aerobic Base Rebuild",
            "readiness_score": 70,
            "coaching_rationale": f"After a {gap_str} gap without swimming, an aerobic base endurance session is recommended to regain feel for the water.",
        }

    if previous_distance > 0:
        volume_ratio = current_distance / previous_distance
        if volume_ratio < 0.5:
            return {
                "workout_type": "Endurance",
                "intensity": "Moderate",
                "primary_driver": "Volume Rebuild",
                "readiness_score": 75,
                "coaching_rationale": f"Weekly volume is lower ({current_distance:.1f}km vs {previous_distance:.1f}km). An aerobic endurance session builds total capacity.",
            }

    # ------------------------------------------------------------
    # 4. EXCELLENT RECOVERY + SOLID RHYTHM -> INTERVALS / SPEED
    # ------------------------------------------------------------
    is_prime_recovery = (hrv is not None and hrv >= 60) or (sleep_score is not None and sleep_score >= 65)
    
    if days_since_swim <= 2 and current_sessions >= 2 and current_load < 120:
        if last_workout_type == "Intervals":
            # Avoid back-to-back interval burnouts
            return {
                "workout_type": "Tempo",
                "intensity": "Moderate-Hard",
                "primary_driver": "Threshold Conditioning",
                "readiness_score": 85,
                "coaching_rationale": "High consistency detected. Following yesterday's speed work with a steady lactate threshold tempo session.",
            }
        
        return {
            "workout_type": "Intervals",
            "intensity": "Hard",
            "primary_driver": "Speed & VO2 Max",
            "readiness_score": 90 if is_prime_recovery else 80,
            "coaching_rationale": "Consistent swimming rhythm and controlled fatigue indicate readiness for 100m freestyle speed repeats and VO2 max training.",
        }

    # ------------------------------------------------------------
    # 5. MODERATE LOAD + REGULAR SWIMMING -> TEMPO OR PYRAMID
    # ------------------------------------------------------------
    if current_load < 100:
        if current_sessions >= 3:
            return {
                "workout_type": "Pyramid",
                "intensity": "Moderate-Hard",
                "primary_driver": "Ladder Endurance",
                "readiness_score": 85,
                "coaching_rationale": "Great session consistency this week! A progressive ladder pyramid workout challenges both threshold pacing and sprint endurance.",
            }

        return {
            "workout_type": "Tempo",
            "intensity": "Moderate",
            "primary_driver": "Lactate Threshold",
            "readiness_score": 80,
            "coaching_rationale": "Moderate training load allows for a sustained lactate threshold tempo session to raise sustainable cruise speed.",
        }

    # ------------------------------------------------------------
    # 6. DEFAULT AEROBIC ENDURANCE
    # ------------------------------------------------------------
    return {
        "workout_type": "Endurance",
        "intensity": "Moderate",
        "primary_driver": "Aerobic Base",
        "readiness_score": 75,
        "coaching_rationale": "Standard aerobic base building session to maintain steady weekly volume and stroke efficiency.",
    }


def choose_swim_workout(
    current_week,
    previous_week,
    days_since_swim,
    wellness=None,
    last_workout_type=None,
):
    """
    Main recommendation function returning the prescribed workout type string.
    100% backward-compatible with original API.
    """
    decision = evaluate_swim_coach(
        current_week,
        previous_week,
        days_since_swim,
        wellness,
        last_workout_type,
    )
    return decision["workout_type"]
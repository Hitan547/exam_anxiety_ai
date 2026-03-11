"""
This module focuses on anxiety-safe, explainable decision-making.
All outputs prioritize psychological safety over score maximization.
"""

import pandas as pd
import random

from data import STUDENT_PROFILE, SYLLABUS, PERFORMANCE_HISTORY
# Convert performance history to DataFrame
performance_df = pd.DataFrame(PERFORMANCE_HISTORY)
def calculate_consistency_ratio():
    """
    Calculates consistency as a ratio over the last 7 days.
    Missing a single day does not heavily penalize the student.
    """

    # Ensure date column is datetime
    df = performance_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Define rolling window (last 7 days from latest date)
    latest_date = df["date"].max()
    start_date = latest_date - pd.Timedelta(days=6)

    # Filter last 7 days
    last_7_days = df[df["date"] >= start_date]

    # Count unique study days
    days_studied = last_7_days["date"].dt.date.nunique()
    total_days = 7

    consistency_ratio = days_studied / total_days

    explanation = (
        f"You studied on {days_studied} out of the last {total_days} days. "
        "Consistency is more important than studying every single day."
    )

    return {
        "consistency_ratio": round(consistency_ratio, 2),
        "days_studied": days_studied,
        "explanation": explanation
    }




def detect_stress_level():
    """
    Detects stress level based on recent performance trends.
    Stress is inferred, not judged.
    """

    df = performance_df.copy()

    # Calculate accuracy
    df["accuracy"] = df["correct_answers"] / df["questions_attempted"]

    # Focus on last 3 study sessions
    recent_df = df.tail(3)

    avg_accuracy = recent_df["accuracy"].mean()
    avg_time = recent_df["time_spent"].mean()
    mistake_count = recent_df["mistake"].sum()

    # Rule-based stress detection
    if avg_accuracy < 0.5 and avg_time > 35:
        stress_level = "High"
        reason = (
            "Recent sessions show high effort with low accuracy, "
            "which may indicate stress or fatigue."
        )
    elif mistake_count >= 2:
        stress_level = "Medium"
        reason = (
            "Repeated mistakes were detected recently. "
            "This can be frustrating and increase stress."
        )
    else:
        stress_level = "Low"
        reason = (
            "Performance has been stable with manageable effort levels."
        )

    return {
        "stress_level": stress_level,
        "reason": reason
    }




def generate_micro_goals():
    """
    Generates 2–4 anxiety-safe daily micro-goals
    based on topic difficulty, mistakes, and stress level.
    """

    stress_info = detect_stress_level()
    stress_level = stress_info["stress_level"]

    # Determine number of goals
    if stress_level == "High":
        num_goals = 2
    elif stress_level == "Medium":
        num_goals = 3
    else:
        num_goals = 3

    goals = []

    # Identify weak topics (mistakes made earlier)
    weak_topics = performance_df[performance_df["mistake"] == True]["topic"].unique().tolist()

    # Prioritize weak topics, then others
    prioritized_topics = weak_topics.copy()
    for topic in [s["topic"] for s in SYLLABUS]:
        if topic not in prioritized_topics:
            prioritized_topics.append(topic)

    for topic in prioritized_topics[:num_goals]:
        # Get difficulty
        difficulty = next(
            (s["difficulty"] for s in SYLLABUS if s["topic"] == topic),
            "medium"
        )

        # Assign time based on difficulty
        if difficulty == "easy":
            time_required = "15 mins"
        elif difficulty == "hard":
            time_required = "30 mins"
        else:
            time_required = "20 mins"

        if stress_level == "High":
            goal_text = f"Revise core concepts of {topic}"
            reason = (
                "High stress was detected, so revision helps maintain confidence "
                "without adding pressure."
            )
        elif topic in weak_topics:
            goal_text = f"Revise core concepts of {topic}"
            reason = (
                "This topic showed mistakes earlier, and revision helps "
                "regain confidence before practice."
            )
        else:
            goal_text = f"Attempt 5 medium questions from {topic} (no time pressure)"
            reason = (
                "Your recent performance on this topic has been stable, "
                "so light practice can strengthen understanding without stress."
            )


        goals.append({
            "goal": goal_text,
            "time": time_required,
            "reason": reason
        })

    return goals




def calculate_confidence_score():
    """
    Calculates confidence score (0–100) based on
    consistency, accuracy trend, effort stability, and stress.
    """

    # --- Consistency (Primary) ---
    consistency_info = calculate_consistency_ratio()
    consistency_score = consistency_info["consistency_ratio"] * 100  # 0–100

    # --- Accuracy Trend ---
    df = performance_df.copy()
    df["accuracy"] = df["correct_answers"] / df["questions_attempted"]
    accuracy_trend = df["accuracy"].mean() * 100  # average accuracy %

    # --- Effort Stability ---
    effort_variation = df["time_spent"].std()
    if effort_variation < 5:
        effort_score = 80
    elif effort_variation < 10:
        effort_score = 60
    else:
        effort_score = 40

    # --- Stress Penalty ---
    stress_info = detect_stress_level()
    if stress_info["stress_level"] == "High":
        stress_penalty = 10
    elif stress_info["stress_level"] == "Medium":
        stress_penalty = 5
    else:
        stress_penalty = 0

    # --- Final Confidence Score ---
    confidence_score = (
        0.4 * consistency_score +
        0.3 * accuracy_trend +
        0.2 * effort_score -
        stress_penalty
    )

    confidence_score = max(0, min(100, round(confidence_score, 1)))

    breakdown = {
        "consistency_contribution": round(0.4 * consistency_score, 1),
        "accuracy_contribution": round(0.3 * accuracy_trend, 1),
        "effort_contribution": round(0.2 * effort_score, 1),
        "stress_penalty": stress_penalty,
        "explanation": (
            "Confidence is driven mainly by consistency, supported by accuracy "
            "and stable effort. Stress slightly reduces the score to avoid pressure."
        )
    }

    return {
        "confidence_score": confidence_score,
        "breakdown": breakdown
    }



def generate_encouragement():
    """
    Generates empathetic, explainable encouragement messages
    with light variation to avoid repetition, while keeping
    logic and explainability intact.
    """

    consistency_info = calculate_consistency_ratio()
    stress_info = detect_stress_level()
    confidence_info = calculate_confidence_score()

    consistency = consistency_info["consistency_ratio"]
    stress_level = stress_info["stress_level"]
    confidence = confidence_info["confidence_score"]
    days_studied = consistency_info["days_studied"]

    # -------- Message templates --------

    high_stress_messages = [
        "It's okay to slow down today. Small steps help reduce pressure.",
        "Today is about staying calm, not pushing harder.",
        "Taking things lightly today helps regain control."
    ]

    consistent_messages = [
        "You’ve been showing up regularly. That habit matters more than speed.",
        "Your consistency this week is solid. Small daily effort adds up.",
        "Studying most days is a strong signal of readiness. Keep this rhythm."
    ]

    growing_confidence_messages = [
        "Your confidence is building steadily. Keep focusing on manageable goals.",
        "You’re moving in the right direction. Calm consistency is working.",
        "Progress looks stable. Stay patient with the process."
    ]

    neutral_messages = [
        "One missed goal doesn’t break progress. Just continue without pressure.",
        "Progress isn’t about perfection. Showing up again is what matters.",
        "Learning works best when pressure stays low."
    ]

    # -------- Message selection logic --------

    if stress_level == "High":
        message = random.choice(high_stress_messages)
        why = (
            "High stress was detected based on recent effort and accuracy patterns."
        )

    elif consistency >= 0.6:
        message = random.choice(consistent_messages)
        why = (
            f"Study activity was detected on {days_studied} out of the last 7 days, "
            "indicating good consistency."
        )

    elif confidence >= 70:
        message = random.choice(growing_confidence_messages)
        why = (
            f"Your confidence score is {confidence}, which reflects steady readiness."
        )

    else:
        message = random.choice(neutral_messages)
        why = (
            "Progress patterns suggest steady effort despite normal fluctuations."
        )

    return {
        "message": message,
        "why": why
    }



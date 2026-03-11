import pandas as pd
from data import SYLLABUS


def build_df(history):
    df = pd.DataFrame(history)
    df["accuracy"] = df["correct_answers"] / df["questions_attempted"]
    return df


def detect_stress(history):
    df = build_df(history)
    recent = df.tail(3)

    if recent["accuracy"].mean() < 0.5 and recent["time_spent"].mean() > 35:
        return "High"
    elif recent["mistake"].sum() >= 2:
        return "Medium"
    else:
        return "Low"


def calculate_consistency(history):
    df = build_df(history)
    df["date"] = pd.to_datetime(df["date"])

    latest = df["date"].max()
    start = latest - pd.Timedelta(days=6)

    days = df[df["date"] >= start]["date"].dt.date.nunique()

    return days / 7


def generate_micro_goals(history):
    df = build_df(history)
    stress = detect_stress(history)

    weak = df[df["mistake"] == True]["topic"].unique().tolist()

    topics = weak + [s["topic"] for s in SYLLABUS if s["topic"] not in weak]

    num = 2 if stress == "High" else 3

    goals = []

    for topic in topics[:num]:
        difficulty = next(
            (s["difficulty"] for s in SYLLABUS if s["topic"] == topic),
            "medium"
        )

        time_map = {"easy": "15 mins", "medium": "20 mins", "hard": "30 mins"}

        if stress == "High":
            text = f"Revise core concepts of {topic}"
        elif topic in weak:
            text = f"Revise core concepts of {topic}"
        else:
            text = f"Attempt 5 medium questions from {topic}"

        goals.append({
            "goal": text,
            "time": time_map[difficulty]
        })

    return goals


def confidence_score(history):
    df = build_df(history)

    consistency = calculate_consistency(history) * 100
    accuracy = df["accuracy"].mean() * 100
    effort = df["time_spent"].std()

    effort_score = 80 if effort < 5 else 60 if effort < 10 else 40

    stress = detect_stress(history)
    penalty = 10 if stress == "High" else 5 if stress == "Medium" else 0

    score = 0.4 * consistency + 0.3 * accuracy + 0.2 * effort_score - penalty

    return round(max(0, min(100, score)), 1)


def encouragement(history):
    stress = detect_stress(history)
    consistency = calculate_consistency(history)
    score = confidence_score(history)

    if stress == "High":
        return "Take it slow today. Calm revision helps."
    elif consistency >= 0.6:
        return "Great consistency this week!"
    elif score >= 70:
        return "Confidence improving steadily."
    else:
        return "Keep going calmly."

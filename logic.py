import pandas as pd
from data import SYLLABUS


# -------------------------
# Helper: Flatten syllabus topics
# -------------------------

def get_all_topics():
    topics = []
    for subj in SYLLABUS:
        for ch in subj["chapters"]:
            for t in ch["topics"]:
                topics.append({
                    "subject": subj["subject"],
                    "chapter": ch["chapter"],
                    "topic": t["topic"],
                    "difficulty": t["difficulty"],
                    "weightage": t["weightage"],
                    "recommended_questions": t["recommended_questions"]
                })
    return topics


# -------------------------
# Build dataframe safely
# -------------------------

def build_df(history):
    df = pd.DataFrame(history)

    if len(df) == 0:
        return df

    df["accuracy"] = df.apply(
        lambda x: x["correct_answers"] / x["questions_attempted"]
        if x["questions_attempted"] > 0 else 0,
        axis=1
    )

    df["date"] = pd.to_datetime(df["date"])

    return df


# -------------------------
# Stress Detection
# -------------------------

def detect_stress(history):
    df = build_df(history)

    if len(df) < 2:
        return "Low"

    recent = df.tail(3)

    if recent["accuracy"].mean() < 0.5 and recent["time_spent"].mean() > 35:
        return "High"

    if recent["accuracy"].mean() < 0.65:
        return "Medium"

    return "Low"


# -------------------------
# Consistency Score
# -------------------------

def calculate_consistency(history):
    df = build_df(history)

    if len(df) == 0:
        return 0

    latest = df["date"].max()
    start = latest - pd.Timedelta(days=6)

    days = df[df["date"] >= start]["date"].dt.date.nunique()

    return days / 7


# -------------------------
# Weak Topic Detection
# -------------------------

def weak_topics(history):
    df = build_df(history)

    if len(df) == 0:
        return []

    weak = df[df["accuracy"] < 0.6]["topic"].unique().tolist()

    return weak


# -------------------------
# Topic Coverage %
# -------------------------

def topic_coverage(history):
    all_topics = [t["topic"] for t in get_all_topics()]
    studied = list(set([h["topic"] for h in history]))

    if len(all_topics) == 0:
        return 0

    return len(studied) / len(all_topics) * 100


# -------------------------
# Generate Micro Goals
# -------------------------

def generate_micro_goals(history):

    stress = detect_stress(history)
    weak = weak_topics(history)
    all_topics = get_all_topics()

    goals = []

    if stress == "High":
        num_goals = 2
    elif stress == "Medium":
        num_goals = 3
    else:
        num_goals = 4

    # Prioritize weak topics
    ordered_topics = weak + [
        t["topic"] for t in all_topics if t["topic"] not in weak
    ]

    for topic in ordered_topics[:num_goals]:

        meta = next(t for t in all_topics if t["topic"] == topic)

        difficulty = meta["difficulty"]

        time_map = {
            "easy": "15 mins",
            "medium": "20 mins",
            "hard": "30 mins"
        }

        if topic in weak:
            text = f"Revise concepts and solve basic problems from {topic}"
        else:
            text = f"Practice {meta['recommended_questions']//5} questions from {topic}"

        goals.append({
            "goal": text,
            "time": time_map[difficulty],
            "difficulty": difficulty
        })

    return goals


# -------------------------
# Confidence Score
# -------------------------

def confidence_score(history):

    df = build_df(history)

    if len(df) == 0:
        return 0

    consistency = calculate_consistency(history) * 100
    accuracy = df["accuracy"].mean() * 100

    coverage = topic_coverage(history)

    stress = detect_stress(history)

    penalty = 15 if stress == "High" else 8 if stress == "Medium" else 0

    score = (
        0.35 * consistency +
        0.35 * accuracy +
        0.3 * coverage -
        penalty
    )

    return round(max(0, min(100, score)), 1)


# -------------------------
# Encouragement Generator
# -------------------------

def encouragement(history):

    stress = detect_stress(history)
    coverage = topic_coverage(history)
    consistency = calculate_consistency(history)

    if stress == "High":
        return "Take a short break and revise slowly. You are improving."

    if coverage > 70:
        return "Great syllabus coverage! Keep revising smartly."

    if consistency > 0.6:
        return "Excellent study consistency this week."

    return "Stay calm and keep progressing step by step."

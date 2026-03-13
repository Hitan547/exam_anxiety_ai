import streamlit as st
import pandas as pd

from data import PERFORMANCE_HISTORY, SYLLABUS
from logic import (
    generate_micro_goals,
    confidence_score,
    encouragement,
    calculate_consistency,
    detect_stress,
    topic_coverage
)

st.set_page_config(page_title="AI Exam Anxiety Assistant", layout="centered")

# -----------------------
# Session History
# -----------------------

if "history" not in st.session_state:
    st.session_state.history = PERFORMANCE_HISTORY.copy()

history = st.session_state.history

st.title("🧠 AI Exam Anxiety Reduction Assistant")

st.markdown("Track your study sessions and get intelligent preparation insights.")

st.divider()

# -----------------------
# Study Session Input
# -----------------------

st.subheader("📘 Log Today's Study Session")

subjects = [s["subject"] for s in SYLLABUS]
subject = st.selectbox("Select Subject", subjects)

chapters = []
for s in SYLLABUS:
    if s["subject"] == subject:
        chapters = [c["chapter"] for c in s["chapters"]]

chapter = st.selectbox("Select Chapter", chapters)

topics = []
for s in SYLLABUS:
    if s["subject"] == subject:
        for c in s["chapters"]:
            if c["chapter"] == chapter:
                topics = [t["topic"] for t in c["topics"]]

topic = st.selectbox("Select Topic", topics)

questions = st.slider("Questions Attempted", 0, 50, 10)
correct = st.slider("Correct Answers", 0, questions, 5)
time_spent = st.slider("Study Time (minutes)", 5, 120, 30)

if questions > 0:
    accuracy_live = correct / questions * 100
    st.info(f"📊 Current Accuracy: {accuracy_live:.1f}%")

# -----------------------
# Submit Button
# -----------------------

if st.button("Submit Study Session"):

    new_entry = {
        "date": pd.Timestamp.today(),
        "subject": subject,
        "chapter": chapter,
        "topic": topic,
        "questions_attempted": questions,
        "correct_answers": correct,
        "time_spent": time_spent
    }

    st.session_state.history.append(new_entry)

    history = st.session_state.history

    st.success("Study session recorded successfully!")

    st.divider()

    # -----------------------
    # AI Insights
    # -----------------------

    st.subheader("🧠 AI Study Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Confidence Score", confidence_score(history))

    with col2:
        st.metric("Consistency (7 days)", round(calculate_consistency(history)*100,1))

    with col3:
        st.metric("Anxiety Risk", detect_stress(history))

    st.progress(int(topic_coverage(history)))

    st.caption(f"Syllabus Coverage: {topic_coverage(history):.1f}%")

    st.divider()

    # -----------------------
    # Micro Goals
    # -----------------------

    st.subheader("🎯 Smart Micro Goals")

    goals = generate_micro_goals(history)

    for g in goals:
        st.write(f"📌 {g['goal']}")
        st.caption(f"⏱ Suggested Time: {g['time']} | Difficulty: {g['difficulty']}")

    st.divider()

    # -----------------------
    # Encouragement
    # -----------------------

    st.subheader("💬 AI Encouragement")
    st.success(encouragement(history))

    st.divider()

# -----------------------
# Study History Table
# -----------------------

st.subheader("📅 Recent Study Sessions")
st.dataframe(pd.DataFrame(history).sort_values("date", ascending=False).head(7))

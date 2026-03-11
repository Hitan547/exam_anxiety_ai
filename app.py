import streamlit as st
import pandas as pd

from data import PERFORMANCE_HISTORY
from logic import (
    generate_micro_goals,
    confidence_score,
    encouragement,
    calculate_consistency
)

st.set_page_config(page_title="Exam Anxiety AI", layout="centered")

if "history" not in st.session_state:
    st.session_state.history = PERFORMANCE_HISTORY.copy()

st.title("🧠 AI Exam Anxiety Reduction")

topic = st.text_input("Topic Studied")
questions = st.number_input("Questions Attempted", min_value=0)
correct = st.number_input("Correct Answers", min_value=0)
time_spent = st.number_input("Time Spent (minutes)", min_value=0)

if st.button("Submit Study Session"):

    new_entry = {
        "date": pd.Timestamp.today(),
        "topic": topic,
        "questions_attempted": questions,
        "correct_answers": correct,
        "time_spent": time_spent,
        "mistake": correct / questions < 0.6 if questions > 0 else False
    }

    st.session_state.history.append(new_entry)

    history = st.session_state.history

    st.subheader("🎯 Micro Goals")
    goals = generate_micro_goals(history)
    for g in goals:
        st.write(g)

    st.subheader("📈 Confidence Score")
    st.metric("Score", confidence_score(history))

    st.subheader("📅 Consistency")
    st.write(round(calculate_consistency(history), 2))

    st.subheader("💬 Encouragement")
    st.success(encouragement(history))

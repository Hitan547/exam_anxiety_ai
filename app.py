import streamlit as st
import pandas as pd

from logic import (
    generate_micro_goals,
    calculate_confidence_score,
    calculate_consistency_ratio,
    generate_encouragement
)
st.set_page_config(page_title="Exam Anxiety Reduction", layout="centered")

st.title("🧠 Exam Anxiety Reduction Dashboard")
st.caption("Designed to reduce anxiety through consistency, not comparison.")


st.write(
    "This system helps students feel prepared, not pressured, "
    "by breaking study into small daily goals and focusing on consistency."
)
st.subheader("🎯 Today's Micro-Goals")

goals = generate_micro_goals()

for idx, goal in enumerate(goals, start=1):
    st.markdown(f"**Goal {idx}:** {goal['goal']}")
    st.markdown(f"- ⏱ Time: {goal['time']}")
    st.markdown(f"- 💡 Why: {goal['reason']}")
    st.markdown("---")
st.subheader("📈 Confidence Score")

confidence_info = calculate_confidence_score()
confidence_score = confidence_info["confidence_score"]

st.metric(label="Current Confidence Score", value=confidence_score)

st.caption(confidence_info["breakdown"]["explanation"])
st.subheader("📅 Consistency Summary")

consistency_info = calculate_consistency_ratio()

st.write(
    f"You studied on **{consistency_info['days_studied']} out of the last 7 days**."
)
st.caption(consistency_info["explanation"])
st.subheader("💬 Encouragement")

encouragement = generate_encouragement()

st.success(encouragement["message"])

with st.expander("Why am I seeing this message?"):
    st.write(encouragement["why"])
